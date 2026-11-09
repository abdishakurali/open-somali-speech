"""Experiment 1: why does MMS say 'Malad' for 'Mahad'? Sweep prosody settings x respellings x seeds,
transcribe back with MMS-1b-all (Somali) and count how often the target word survives."""
import itertools, json, os, re, time
import torch, librosa
from transformers import VitsModel, AutoTokenizer, Wav2Vec2ForCTC, AutoProcessor

here = os.path.dirname(os.path.abspath(__file__))
tok = AutoTokenizer.from_pretrained("facebook/mms-tts-som")
tts = VitsModel.from_pretrained("facebook/mms-tts-som").eval()
proc = AutoProcessor.from_pretrained("facebook/mms-1b-all", target_lang="som")
asr = Wav2Vec2ForCTC.from_pretrained("facebook/mms-1b-all", target_lang="som", ignore_mismatched_sizes=True).eval()

settings = {"base(.667,.8)": (0.667, 0.8), "ns.5/nsd0": (0.5, 0.0), "ns.35/nsd0": (0.35, 0.0), "ns.667/nsd0": (0.667, 0.0)}
spellings = {"mahad": "mahad alle ayaa iska leh", "mahhad": "mahhad alle ayaa iska leh", "mahaad": "mahaad alle ayaa iska leh"}
seeds = [0, 1, 2, 3]

def say(text, ns, nsd, seed, rate=1.0):
    tts.noise_scale, tts.noise_scale_duration, tts.speaking_rate = ns, nsd, rate
    torch.manual_seed(seed)
    with torch.no_grad():
        return tts(**tok(text, return_tensors="pt")).waveform[0].numpy()

def hear(wav):
    w = librosa.resample(wav, orig_sr=16000, target_sr=16000)
    with torch.no_grad():
        ids = asr(**proc(w, sampling_rate=16000, return_tensors="pt")).logits.argmax(-1)[0]
    return re.sub(r"[^a-z' ]+", "", proc.decode(ids).lower())

res = {}
for (sn, (ns, nsd)), (sp, text) in itertools.product(settings.items(), spellings.items()):
    hits, hyps = 0, []
    for s in seeds:
        h = hear(say(text, ns, nsd, s))
        first = h.split()[0] if h.split() else ""
        ok = first.startswith("mahad") or first.startswith("mahaad") or first.startswith("mahhad")
        hits += ok
        hyps.append(h)
    res[f"{sn} | {sp}"] = {"hits": f"{hits}/{len(seeds)}", "hyps": hyps}
    print(f"{sn:14s} {sp:7s} {hits}/{len(seeds)}  {hyps}", flush=True)
json.dump(res, open(os.path.join(here, "exp1_mahad.json"), "w"), indent=1)
