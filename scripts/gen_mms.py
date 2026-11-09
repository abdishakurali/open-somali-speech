"""Generate Somali samples with Meta MMS-TTS (facebook/mms-tts-som, VITS, CC-BY-NC 4.0)."""
import json, os, sys, time
import torch, soundfile as sf
from transformers import VitsModel, AutoTokenizer

here = os.path.dirname(os.path.abspath(__file__))
texts = json.load(open(os.path.join(here, "texts.json")))
keys = sys.argv[1:] or ["1:1", "1:2", "112:1", "112:2", "112:3", "112:4"]
out = os.path.join(here, "samples", "mms")
os.makedirs(out, exist_ok=True)

t0 = time.time()
tok = AutoTokenizer.from_pretrained("facebook/mms-tts-som")
model = VitsModel.from_pretrained("facebook/mms-tts-som").eval()
print("load", round(time.time() - t0, 1), "s, params", sum(p.numel() for p in model.parameters()))
for k in keys:
    t0 = time.time()
    inp = tok(texts[k].lower(), return_tensors="pt")
    with torch.no_grad():
        wav = model(**inp).waveform[0].numpy()
    path = os.path.join(out, f"{k.replace(':', '_')}.wav")
    sf.write(path, wav, model.config.sampling_rate)
    print(k, "gen", round(time.time() - t0, 2), "s, audio", round(len(wav) / model.config.sampling_rate, 1), "s ->", path)
