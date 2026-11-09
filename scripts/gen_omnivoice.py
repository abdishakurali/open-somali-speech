"""Generate Somali samples with OmniVoice (auto voice, no reference clip, no cloning)."""
import json, os, sys, time
import torch, soundfile as sf
from omnivoice import OmniVoice

here = os.path.dirname(os.path.abspath(__file__))
texts = json.load(open(os.path.join(here, "texts.json")))
keys = sys.argv[1:] or ["1:1", "1:2", "112:1", "112:2", "112:3", "112:4"]
out = os.path.join(here, "samples", "omnivoice")
os.makedirs(out, exist_ok=True)

dev = "mps" if torch.backends.mps.is_available() else "cpu"
t0 = time.time()
model = OmniVoice.from_pretrained("k2-fsa/OmniVoice", device_map=dev, dtype=torch.float16 if dev == "mps" else torch.float32)
print("load", round(time.time() - t0, 1), "s on", dev)
for k in keys:
    t0 = time.time()
    audio = model.generate(text=texts[k], language="so")
    wav = audio[0]
    path = os.path.join(out, f"{k.replace(':', '_')}.wav")
    sf.write(path, wav.squeeze().cpu().float().numpy() if hasattr(wav, "cpu") else wav, 24000)
    dur = (wav.shape[-1] if hasattr(wav, "shape") else len(wav)) / 24000
    print(k, "gen", round(time.time() - t0, 1), "s, audio", round(dur, 1), "s ->", path)
