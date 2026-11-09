# Open Somali TTS: research and plan (2026-11-03)

Goal from the maintainer: build our own better Somali voice, reliable and efficient, open-sourced, with a natural, fuller tone (the Block "Dessa" demo as a naturalness reference).

## 1. Hard facts that shape everything
1. **Block Dessa is not usable.** It is a closed speech-to-speech conversation model on a waitlist, no languages listed, no licence. It is only a *target for how natural speech should feel*. Its stated secret: trained directly on raw human conversation audio, so it keeps pauses, emotion and breath that text-only pipelines throw away. (Source: block.xyz/dessa, company claims, no independent benchmark.)
2. **We cannot open-source MMS-derived weights under a free licence.** `facebook/mms-tts-som` is CC-BY-NC 4.0. Anything fine-tuned from it stays CC-BY-NC: shareable for research, not usable in a paid product, and not "open source" in the OSI sense. Meta's code is MIT, but that is not the weights. **A truly open model must start from a permissive base or from scratch, on data we are allowed to use.**
3. **Data is the real bottleneck, not the model.** What I found:
   | Source | Somali? | Licence | Fit for TTS |
   |---|---|---|---|
   | Google WAXAL (TTS, 180+ h) | **No** (17 TTS languages, no Somali) | CC-BY / CC-BY-SA | not for Somali |
   | `SomaliDatasets/somali-tts` (HF) | stated goal of 1M clips | CC-BY-4.0 | **empty** at time of check (3 kB) |
   | Mozilla Data Collective, Digital Divide Data Somali, 68 h | yes | listed CC-BY-4.0 but terms say research only, no redistribution | **no for a public model** until permission is in writing |
   | Google FLEURS Somali (so_so) | yes (checked 2026-11-09 on the dataset card) | cc-by-4.0 on the card | small read-sentence benchmark, not a TTS corpus |
   | Mozilla Common Voice Somali | **no released dataset found**; an inactive Somali placeholder locale exists (read through a summarising tool; re-check in a browser) | n/a | cannot verify any Somali audio exists |
   | OpenBibleTTS (37 languages) | **unknown** | paper CC-BY-SA, audio/model licence not stated | check; Bible recordings are exactly what MMS used |
   | LDC MATERIAL Somali, 50 h | yes | paid LDC licence | no |
   So: **there is no ready open, clean, single-speaker Somali TTS corpus.** We have to make one.
4. **Open-weights bases that could be fine-tuned** (verify each licence on the repo before use): Chatterbox Multilingual (reported MIT, 23 languages, no Somali, needs tokenizer extension), StyleTTS2 (MIT; a 1 h 15 min single-speaker Somali fine-tune exists on HF as `Zyroxx66/StyleTTS2-Somali`, licence not checked), VITS/Piper family (MIT code). A 2026 benchmark (OpenBibleTTS) found open from-scratch systems degrade sharply on out-of-domain text, and monolingual models trained on clean Bible-style data had the best intelligibility for African languages.

## 2. What is actually wrong with MMS Somali (found by inspection and test)
- **Its tokenizer has no punctuation at all.** Vocabulary is `a-z`, space, `'`, `-`, `_`. Commas, full stops and parentheses are deleted before synthesis. The model cannot be told where to pause; the duration predictor guesses. This is the main cause of odd pauses. Our verses are full of `( ... )` glosses and commas.
- **Training audio is Bible readings, one reading style.** That explains the sermon-like tone and why anything outside that register (names, glosses, Arabic loanwords like Alle, qiyaamo) is shaky.
- **Sampling is stochastic.** Default `noise_scale=0.667`, `noise_scale_duration=0.8`: the same text gives different pauses and pronunciations per run. In my test of "mahad alle ayaa iska leh" with the default settings, a Somali ASR heard "mahad" correctly 3 of 4 times and "maxad" once. So "Malad" is a *seed-dependent failure*, not a fixed bug. That is good news: it can be filtered out.
- Output is 16 kHz, so it sounds thin; "fuller" tone needs mastering or a higher-rate model.

## 3. Techniques that make it more accurate (what I built and tested)
All in `pipeline.py` (MMS-only, for the quality benchmark; same ideas port to any model):
1. **Chunk at punctuation and add explicit pauses** (0.24 s after commas/parentheses, 0.55 s after sentence ends, long chunks split near a word boundary). We control pauses instead of the model guessing.
2. **Lower sampling noise and fixed durations** (`noise_scale` 0.5, `noise_scale_duration` 0): steadier, less random.
3. **ASR-in-the-loop best-of-N**: synthesize each chunk with N seeds, transcribe with a Somali ASR, keep the lowest character-error candidate. This is rejection sampling and it is cheap because verses are pre-generated once, offline. It directly targets the "Malad" class of error.
4. **Trim silence and soften chunk edges** before stitching.
5. **Mastering for a fuller sound**: upsample to 24 kHz, +3.5 dB low shelf at 160 Hz, small presence boost, gentle compression, loudness to -18 LUFS, very short room reflection. This can add warmth but cannot create real high-frequency detail from a 16 kHz model.
Caveat: the ASR I use is from the same Meta family as the TTS, so it favours MMS-style pronunciation. For the real project, use an independent Somali ASR and a Somali listener panel as the final judge.

## 4. Lessons borrowed from ElevenLabs and Dessa (public information only; I did not find their internals)
- Quality comes first from **many hours of clean, professionally recorded, expressive speech with accurate transcripts**, not from model tricks. Voices are built from studio recordings of one speaker.
- They are **context-aware**: the model reads the whole sentence/paragraph to choose pacing and emphasis. Our small VITS only sees one chunk; a larger context window (paragraph-level, or a model conditioned on neighbouring verses) is the upgrade path.
- Controls exposed to users (stability vs expressiveness) map to our noise scale and best-of-N.
- Dessa's lesson: **train on raw, natural audio, not just text.** For us: record a human reading in a warm, natural voice with real pauses, not a flat studio read, and keep the pauses in the transcript (punctuation or pause tokens).
- Not verified: anything about their architectures. I would not claim we can match them; a single-voice Somali reciter model is a much narrower and achievable target.

## 5. Recommended plan to own it (open, reliable, efficient)
**Phase 0 (now, free): improve the benchmark** using the pipeline above; maintainer judges by ear. Output: a "gold" set of 16 verses everyone agrees sounds right.
**Phase 1: build the dataset (the real work).**
- Record **5-10 hours of one Somali speaker** (ideally one the maintainer likes, with a signed release that allows open-source release of the voice) reading the Quran translation and varied everyday text, in a quiet room, 44.1/48 kHz. Transcribe with exact punctuation and mark parenthetical glosses. This is the asset that makes everything else possible and keeps the licence clean (CC-BY or CC0).
- Verify the Somali translation text's own rights (the corpus came from an archive.org scan) before releasing text+audio together.
- Optionally add speaker consent and community contributions via a simple recorder app, with a review step by Somali speakers.
**Phase 2: train.** Permissive base only. Candidates: fine-tune StyleTTS2 or a Piper/VITS model, or extend Chatterbox's tokenizer to Somali. Start with the existing 1 h 15 StyleTTS2 Somali voice as a cheap data-efficiency check. A single GPU (rented, days not months) is enough for a single-speaker model.
**Phase 3: reliability layer** (what we already prototyped): punctuation chunking, pause control, best-of-N with independent ASR, a Somali text normaliser (Alle/Allaah spelling, glosses, numbers), and a regression set of hard words (mahad, Alle, dhalin, qiyaamo, long vowels aa/ee/ii).
**Phase 4: efficiency and release.** Export to ONNX/Core ML for on-device, int8 quantise, publish weights + dataset + the evaluation set on Hugging Face under a clear open licence, with a model card. Ship pre-generated MP3 in the app meanwhile.
**Cost shape (estimates, not quotes):** recording and editing a speaker for 5-10 h, a few hundred to a few thousand dollars depending on the speaker; GPU training tens to low hundreds of dollars; the largest hidden cost is QA by Somali speakers.

## 6. Open questions for the maintainer
1. Who is the voice: a specific reciter, or the maintainer? (Rights and consent decide the licence.)
2. Is the goal only Qur'an translation reading, or a general Somali voice for everyone? The second needs far more varied text and speakers.
3. Release licence: CC-BY / Apache-2.0 (anyone, even commercial) or share-alike? This decides what data and bases we can use.
