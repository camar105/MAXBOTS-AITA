# Work Report - 2026-04-19

## Scope Of Work

This report summarizes the work completed today to turn the public MAXBOTS-AITA prototype into a more complete, course-ready repository for MAE301.

## Repository And Structure Work

- cloned the public GitHub repository into a local working copy
- confirmed the public repo state matched the earlier local snapshot
- reorganized the repository into the course-oriented structure:
  - `proposal/`
  - `nanogpt/`
  - `mvp/`
  - `docs/`
- archived the original prototype under `docs/archive/original-prototype/`
- moved the original Phase 1 report and video into `docs/assets/phase1/`

## Phase 1 Work

- converted the Phase 1 concept into markdown at `proposal/idea.md`
- preserved the original submission assets for reference

## Phase 2 Work: nanoGPT

- implemented a small GPT-style character-level model in `nanogpt/model.py`
- implemented training/evaluation pipeline in `nanogpt/train.py`
- implemented checkpoint sampling in `nanogpt/sample.py`
- created three experiment configs in `nanogpt/configs/experiments.json`
- added setup instructions and requirements for the Phase 2 folder
- added model smoke tests in `nanogpt/tests/test_model.py`
- executed all three training runs on CPU
- produced:
  - checkpoints
  - loss curves
  - metrics JSON files
  - generated text samples
  - aggregate experiment summary
- wrote a real results report in `nanogpt/report.md`

### Phase 2 experiment outcomes

| Config | Params | Best Val Loss | Runtime (s) |
| --- | ---: | ---: | ---: |
| `baseline` | 112,193 | 2.2770 | 7.13 |
| `wider` | 241,985 | 2.2269 | 12.11 |
| `deeper_context` | 356,609 | 2.3273 | 22.17 |

Best run: `wider`

## Phase 3 Work: MVP

- replaced the earlier one-off summarizer with a dedicated `mvp/` application
- built a Flask app that supports:
  - file upload
  - grounded retrieval from uploaded content
  - `summary`
  - `explain`
  - `daily quiz`
- added PDF extraction with `pypdf`
- added document chunking and local relevance scoring
- added local JSON-based progress/session storage
- added a browser UI in `mvp/templates/` and `mvp/static/`
- added unit and request-flow tests in `mvp/tests/`
- wrote `mvp/README.md` and `mvp/report.md`

## Documentation And Audit Work

- created a new root `README.md`
- added `docs/architecture.md`
- created `docs/course-rubric-audit.md` to map course requirements to evidence
- polished the Phase 2 and Phase 3 reports to align more closely with the MAE301 rubric

## Verification Performed Today

### MVP

- `pytest` in `mvp/` -> passed
- Python compile checks for MVP source -> passed
- Flask upload + command smoke test -> passed

### nanoGPT

- Python compile checks for nanoGPT source -> passed
- `pytest` in `nanogpt/` -> passed
- checkpoint loading and sampling -> passed
- all three experiment runs completed successfully on CPU

## Constraints Encountered

- no GitHub authentication was available, so no push or GitHub release was performed
- local `venv` creation failed in this environment because `ensurepip` did not complete successfully
- the build was completed using the available system Python environment instead

## Final Status At End Of Session

- Phase 1 documentation is present in markdown and archived assets are preserved
- Phase 2 now exists as a full local deliverable with experiments and results
- Phase 3 is complete as a runnable, locally testable MVP
- the repository is organized to match the MAE301 project structure more closely
- the remaining external step is publishing the updated work back to GitHub once auth is available
