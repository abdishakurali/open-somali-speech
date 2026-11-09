# Data card (TEMPLATE)

Fill one section per release. Fields marked REQUIRED must have evidence or the words CANNOT VERIFY; a release with any CANNOT VERIFY in a REQUIRED rights field must not be published.

## 1. Dataset summary
- Name / version / date:
- Language and variety: Somali (som), standard Latin script. Dialects included (list):
- Contents: [ ] text sentences [ ] audio recordings [ ] both (aligned)
- Size: sentences ___, hours ___, speakers ___
- Intended uses: speech recognition, text-to-speech research and products, evaluation
- Out-of-scope uses (stated, not enforceable by licence alone): impersonating a speaker, fraud, harassment
- Current status of this project: no release exists yet.

## 2. Provenance (per text item)
| Field | REQUIRED | Notes |
|---|---|---|
| item_id | yes | |
| text | yes | |
| origin | yes | `own-writing` / `licensed-third-party` / `public-domain` |
| author_or_rightsholder | yes | name or contributor ID |
| source_url_or_citation | if third-party | |
| licence_as_found | yes | exact name and URL read at the source |
| licence_evidence | yes | where it was checked, date, who |
| contributor_grant | yes | confirms the contributor may license it |
| dialect_label | no | |
| reviewer_ids / review_date | yes | two reviewers |
| known_issues | no | spelling variants, uncertain words |

## 3. Provenance and consent (per audio item)
| Field | REQUIRED | Notes |
|---|---|---|
| clip_id | yes | |
| transcript_id (links to text item) | yes | transcript must match speech exactly |
| speaker_id | yes | anonymous code, not a name |
| consent_form_id + version + date | yes | form stored privately; adult or guardian signed |
| release_licence | yes | the licence the speaker agreed to |
| identification_choice | yes | numeric ID / name / other |
| recording_device, room, sample_rate, bit_depth | yes | |
| processing_applied | yes | `none` or exact steps (denoise, trim, normalise) |
| synthetic | yes | `no` for human recordings. Synthetic audio must be labelled `yes` with the model and its licence, and is kept out of human sets |
| optional demographics (age band, gender, region) | no | only if the speaker opted in |
| audio_reviewer_id / review_date | yes | |
| withdrawal_status | yes | `active` / `withdrawn-from-future-releases` |

## 4. Collection process
How prompts were chosen, how speakers were recruited, whether paid (amount stated), how consent was explained in Somali.

## 5. Quality and evaluation
Hard-word list (`hard-words.txt`), independent ASR check (state the model and its licence), listener panel results, known failure modes.

## 6. Risks and limitations
Link to `RISKS.md`. State speaker/dialect/gender imbalance honestly.

## 7. Licence and citation
Data licence, code licence, citation text, contact and takedown address.
