# MAE301 Criteria Audit

This document maps the rebuilt repository to the MAE301 project guideline requirements.

## Phase 1: Proposal

| Requirement | Evidence | Status |
| --- | --- | --- |
| Idea pitch in markdown | `proposal/idea.md` | Met |
| Team members listed | `proposal/idea.md` | Met |
| Problem statement and user | `proposal/idea.md` sections "Problem Statement" and "Why Now?" | Met |
| Proposed AI-powered solution | `proposal/idea.md` section "Proposed AI-Powered Solution" | Met |
| Initial technical concept | `proposal/idea.md` section "Initial Technical Concept" | Met |
| Scope for MVP | `proposal/idea.md` section "Scope For MVP" | Met |
| Risks and planned data sources | `proposal/idea.md` final sections | Met |
| Original phase assets preserved | `docs/assets/phase1/` | Met |

## Phase 2: nanoGPT Build

| Requirement | Evidence | Status |
| --- | --- | --- |
| GPT-style implementation | `nanogpt/model.py` | Met |
| Training script | `nanogpt/train.py` | Met |
| Sampling/generation script | `nanogpt/sample.py` | Met |
| Requirements and setup instructions | `nanogpt/requirements.txt`, `nanogpt/README.md` | Met |
| At least 3 experiment configs | `nanogpt/configs/experiments.json` | Met |
| Training and validation loss reporting | `nanogpt/outputs/*_metrics.json`, `nanogpt/outputs/*_curve.png` | Met |
| Generated sample text | `nanogpt/outputs/*_sample.txt` | Met |
| Results summary/report | `nanogpt/report.md` | Met |
| Local tests for model code | `nanogpt/tests/test_model.py` | Met |
| GitHub release/tag milestone | No remote auth available in this session | Ready locally, external step remains |

### Completed experiment results

| Config | Params | Best Val Loss | Runtime (s) |
| --- | ---: | ---: | ---: |
| `baseline` | 112,193 | 2.2770 | 7.13 |
| `wider` | 241,985 | 2.2269 | 12.11 |
| `deeper_context` | 356,609 | 2.3273 | 22.17 |

## Phase 3: MVP Build

| Requirement | Evidence | Status |
| --- | --- | --- |
| MVP code in dedicated folder | `mvp/` | Met |
| Web UI / runnable demo | `mvp/app.py`, `mvp/templates/`, `mvp/static/` | Met |
| Demo instructions / README | `mvp/README.md` | Met |
| Clear code layout (`src`, data, tests) | `mvp/src/`, `mvp/data/`, `mvp/tests/` | Met |
| User-facing functionality | `summary`, `explain`, `daily quiz` in `mvp/src/maxbots_mvp/engine.py` | Met |
| Grounded use of uploaded material | PDF/text extraction + chunk retrieval in `mvp/src/maxbots_mvp/engine.py` | Met |
| Local progress tracking | `mvp/src/maxbots_mvp/storage.py` | Met |
| MVP report | `mvp/report.md` | Met |
| Evaluation and reproducibility | `mvp/tests/`, smoke tests, `mvp/README.md` | Met |

### Phase 3 completion summary

Phase 3 is complete for a local, rubric-safe MVP. The final build supports grounded upload-based study sessions, local progress tracking, reproducible setup, and automated verification without requiring external API credentials.

## Repository Organization

| Guideline | Evidence | Status |
| --- | --- | --- |
| Proposal content separated | `proposal/` | Met |
| nanoGPT work separated | `nanogpt/` | Met |
| MVP work separated | `mvp/` | Met |
| Extra documentation | `docs/` | Met |

## Final Notes

- The original public prototype has been preserved under `docs/archive/original-prototype/`.
- The rebuilt repository is submission-ready locally.
- The only guideline item that still depends on remote access is publishing a GitHub release/tag milestone online.
