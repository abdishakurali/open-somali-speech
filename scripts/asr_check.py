"""Round-trip check: transcribe each sample with Meta MMS-1b-all (Somali adapter) and report CER vs the input text."""
import json, os, re, sys, glob
import torch, librosa
from transformers import Wav2Vec2ForCTC, AutoProcessor

here = os.path.dirname(os.path.abspath(__file__))
texts = json.load(open(os.path.join(here, "texts.json")))
proc = AutoProcessor.from_pretrained("facebook/mms-1b-all", target_lang="som")
model = Wav2Vec2ForCTC.from_pretrained("facebook/mms-1b-all", target_lang="som", ignore_mismatched_sizes=True).eval()

def norm(s):
    return re.sub(r"[^a-z' ]+", "", s.lower().replace("(", " ").replace(")", " ")).split()

def edit(a, b):
    d = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        p, d[0] = d[0], i
        for j, y in enumerate(b, 1):
            p, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, p + (x != y))
    return d[-1]

for path in sorted(glob.glob(os.path.join(here, "samples", "*", "*.wav"))):
    key = os.path.basename(path)[:-4].replace("_", ":")
    wav, _ = librosa.load(path, sr=16000)
    with torch.no_grad():
        ids = model(**proc(wav, sampling_rate=16000, return_tensors="pt")).logits.argmax(-1)[0]
    hyp = proc.decode(ids)
    ref = " ".join(norm(texts[key]))
    h = " ".join(norm(hyp))
    cer = edit(ref.replace(" ", ""), h.replace(" ", "")) / max(1, len(ref.replace(" ", "")))
    print(f"{os.path.basename(os.path.dirname(path))}/{key}  CER={cer:.2f}\n  ref: {ref}\n  hyp: {h}")
