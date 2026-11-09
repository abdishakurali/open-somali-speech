"""Experiment 2: a reliability layer around MMS-TTS Somali.
 1. split text at punctuation (MMS's tokenizer deletes punctuation, so it cannot place pauses itself)
 2. synthesize each chunk deterministically-ish (low noise_scale, noise_scale_duration=0)
 3. best-of-N seeds per chunk, picked by ASR round-trip CER (rejection sampling)
 4. trim silence, stitch with explicit pauses
 5. optional 'fuller' mastering with ffmpeg (EQ, gentle compression, loudness, tiny room)
Usage: pipeline.py <noise_scale> <n_seeds> <tag> verse [verse ...]"""
import json, os, re, subprocess, sys
import numpy as np, torch, librosa, soundfile as sf
from transformers import VitsModel, AutoTokenizer, Wav2Vec2ForCTC, AutoProcessor

here = os.path.dirname(os.path.abspath(__file__))
texts = json.load(open(os.path.join(here, "texts.json")))
ns, nseeds, tag, verses = float(sys.argv[1]), int(sys.argv[2]), sys.argv[3], sys.argv[4:]
SR = 16000
tok = AutoTokenizer.from_pretrained("facebook/mms-tts-som")
tts = VitsModel.from_pretrained("facebook/mms-tts-som").eval()
proc = AutoProcessor.from_pretrained("facebook/mms-1b-all", target_lang="som")
asr = Wav2Vec2ForCTC.from_pretrained("facebook/mms-1b-all", target_lang="som", ignore_mismatched_sizes=True).eval()
tts.noise_scale, tts.noise_scale_duration, tts.speaking_rate = ns, 0.0, 1.0

def words(s):
    return re.sub(r"[^a-z' ]+", "", s.lower()).split()

def edit(a, b):
    d = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        p, d[0] = d[0], i
        for j, y in enumerate(b, 1):
            p, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, p + (x != y))
    return d[-1]

def cer(ref, hyp):
    r, h = "".join(words(ref)), "".join(words(hyp))
    return edit(r, h) / max(1, len(r))

def chunks(text):
    """-> [(chunk, pause_after_seconds)]"""
    out = []
    for part in re.split(r"([,;:.!?()]+)", text.lower().replace("…", ".")):
        if re.fullmatch(r"[,;:.!?()]+", part or "x"):
            if out:
                strong = any(c in part for c in ".!?")
                out[-1] = (out[-1][0], 0.55 if strong else 0.24)
        elif part.strip():
            out.append((part.strip(), 0.12))
    final = []
    for c, p in out:  # split very long chunks near the middle at a space
        while len(c) > 90:
            cut = c.rfind(" ", 0, 60) if c.rfind(" ", 0, 60) > 30 else 60
            final.append((c[:cut].strip(), 0.08)); c = c[cut:].strip()
        final.append((c, p))
    return final

def say(text, seed):
    torch.manual_seed(seed)
    with torch.no_grad():
        w = tts(**tok(text, return_tensors="pt")).waveform[0].numpy()
    w, _ = librosa.effects.trim(w, top_db=35)
    return w

def hear(w):
    with torch.no_grad():
        ids = asr(**proc(w, sampling_rate=SR, return_tensors="pt")).logits.argmax(-1)[0]
    return proc.decode(ids)

def synth(text, log):
    parts = []
    for c, pause in chunks(text):
        best = None
        for s in range(nseeds):
            w = say(c, s)
            e = cer(c, hear(w)) if nseeds > 1 else 0.0
            if best is None or e < best[0]:
                best = (e, w, s)
        log.append(f"  [{c[:40]}] best seed {best[2]} cer {best[0]:.2f} pause {pause}")
        w = best[1] * np.hanning(len(best[1]) + 2)[1:-1] ** 0.1  # soft edges
        parts += [w, np.zeros(int(pause * SR), dtype=np.float32)]
    return np.concatenate(parts[:-1])

for v in verses:
    log = []
    base = os.path.join(here, "samples", tag); os.makedirs(base, exist_ok=True)
    raw = os.path.join(base, v.replace(":", "_") + ".wav")
    if os.path.exists(raw):
        wav = sf.read(raw)[0]
    else:
        wav = synth(texts[v], log)
        sf.write(raw, wav, SR)
    # 'fuller' master: upsample, low-shelf warmth, presence, gentle compression, loudness, tiny room
    full = raw.replace(".wav", "_full.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af",
                    "aresample=24000,bass=g=3.5:f=160:w=0.8,equalizer=f=2800:t=q:w=1.2:g=2,"
                    "acompressor=threshold=-22dB:ratio=3:attack=8:release=160:makeup=3,"
                    "aecho=0.85:0.4:28|55:0.10|0.05,loudnorm=I=-18:TP=-2",
                    full], check=True)
    print(v, "\n".join(log), flush=True)
