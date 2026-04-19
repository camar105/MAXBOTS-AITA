# MAXBOTS-AITA

Course-ready repository for the MAE301 Max's Bots project.

## Repository Structure

- `proposal/` - Phase 1 idea pitch in markdown
- `nanogpt/` - Phase 2 nanoGPT implementation, experiments, and report
- `mvp/` - Phase 3 MVP code, demo instructions, tests, and report
- `docs/` - architecture notes, archived prototype, and original submission assets

## Current Status

- The original public-repo prototype is preserved under `docs/archive/original-prototype/`.
- The active product build now lives under `mvp/`.
- The `mvp/` app is designed to run locally in mock mode first so it does not depend on paid API access.

## MVP Commands

The rebuilt MVP focuses on three study commands grounded in uploaded course material:

- `summary`
- `explain`
- `daily quiz`

## Running The MVP

From the `mvp/` directory:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Then open `http://localhost:3000`.

## Notes

- The `nanogpt/` folder contains the completed Phase 2 implementation, experiment outputs, and report.
