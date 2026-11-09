# Open Somali Speech

An open project to build a clean, openly licensed **Somali voice dataset** (recordings with exact transcripts, with each speaker's consent) so anyone can build speech recognition and text-to-speech for Somali.

**Status: day one.** This repository holds our starting point: a plan, evaluation scripts, a draft list of hard Somali words, and the rules for contributing safely. **It holds no dataset yet, and no recordings.** We would rather say that plainly than look bigger than we are.

## Why
Somali has no open, clean, single-speaker speech corpus that we could find. Checked on 2026-11-09:
- Google FLEURS includes Somali (`so_so`, cc-by-4.0 on its dataset card), but it is a small read-sentence benchmark, not a corpus for building a voice.
- Mozilla Common Voice shows an inactive Somali placeholder and no released Somali dataset that we could find.
- The one Somali text-to-speech dataset we found on Hugging Face (`SomaliDatasets/somali-tts`) was empty when we looked.
- The Somali text-to-speech model we tested (Meta MMS-TTS) is licensed non-commercial (CC-BY-NC), so nothing made from it can be a truly open model.

The bottleneck is data with clear rights, not model code.

## What is in this repository
- `docs/OPEN_SOMALI_TTS_PLAN.md`: research notes and a phased plan (dataset first, then training, then a reliability layer, then release). Costs in it are estimates.
- `scripts/`: a small evaluation toolkit. It chunks text at punctuation, controls pauses, and picks the best of several synthesis attempts by checking them with a speech recognizer. It **downloads third-party models at run time** (some are CC-BY-NC); it ships none of them and none of their output. Copy `scripts/texts.example.json` to `scripts/texts.json` and put in text you have the right to use.
- `hard-words.txt`: a **draft** list of Somali words that speech systems get wrong. Words only. It has not been reviewed by a Somali speaker yet; see CONTRIBUTING.
- `docs/DATA-CARD-TEMPLATE.md`: the provenance and consent fields every future release must fill.
- `docs/RISKS.md`: the risks we know about and how we plan to handle them.
- `docs/CONSENT-FORM-DRAFT.md`: draft wording for speaker consent. **Not in use, and not legal advice.** It needs a legal review and a Somali version before anyone records anything for this project.

## What is deliberately not included
- **The Somali Quran translation text we used in early experiments.** Its rights holder, licence and copyright status could not be verified (no licence field on the archive.org item; the printed book names the King Fahd Complex as publisher and carries no copyright notice we could find in the part we read). It stays out until there is a written permission or a fresh, licensed translation.
- **Any audio from MMS-TTS or OmniVoice** (both CC-BY-NC) or from our own early experiments, because the spoken text was not cleared.
- Anything copied from other people's datasets. We link to them; we do not redistribute them.

## Licences
- **Code** (`scripts/`): Apache-2.0 (see `LICENSE`).
- **`hard-words.txt`**: CC0 1.0, released to the public domain.
- **Documentation** (`docs/`, this file): CC BY 4.0.
- **Future data:** not decided. We are leaning toward CC BY-SA 4.0 so it is compatible with related open Somali text work, but we will not accept data until the consent process is ready and reviewed. Nothing here grants rights to data that is not in this repository.

## Related open work
- Unkad Labs runs [Qor Af-Soomaali](https://qor.unkad.com), a community-verified Somali sentence corpus; their organisation card says they release under CC BY-SA 4.0 (https://huggingface.co/unkadlabs). We are not affiliated with them. If you want to contribute Somali text today, that is a good place.

## How to help right now
- **Somali speakers:** review `hard-words.txt` (spelling, dialect, pronunciation notes) and tell us what is missing, in an issue.
- **Developers:** improve the evaluation scripts, add an independent Somali speech recognizer to the checks, or design a safe recording and review tool.
- **Researchers and lawyers:** check our rights reading, or review the consent wording.
- **Rights holders:** if you hold rights to a Somali translation or recordings and want to license them openly, open an issue.

Read `CONTRIBUTING.md` before you contribute anything. Questions and takedown requests: open an issue on this repository.

Maintainer: [@abdishakurali](https://github.com/abdishakurali). This project is independent of any company product.
