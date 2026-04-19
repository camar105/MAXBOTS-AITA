# MVP

StatAI-TA is a practical single-user study assistant for statistics courses.

## What It Does

- uploads PDF and text-based course material
- builds a grounded local study session from those uploads
- supports three commands: `summary`, `explain`, and `daily quiz`
- tracks local quiz history so weak topics can be surfaced over time

## Why It Is Mock-First

This MVP is designed to be fully demoable without paid API access. Instead of blocking on external model credentials, it uses a local deterministic study engine that:

- parses uploaded course material
- retrieves relevant text chunks
- generates grounded study outputs from those chunks
- stores progress locally in JSON files

This keeps the demo reproducible while preserving the course-facing product flow.

## Project Layout

- `app.py` - Flask entrypoint
- `src/maxbots_mvp/engine.py` - document parsing, chunking, retrieval, and grounded response generation
- `src/maxbots_mvp/storage.py` - local session and progress persistence
- `templates/index.html` - browser UI
- `static/` - browser logic and styling
- `tests/` - unit and integration tests
- `data/examples/` - sample markdown examples from the original prototype
- `data/templates/` - legacy study templates kept as reference material
- `data/samples/` - sample demo assets, including a statistics textbook PDF

## Setup

From this `mvp/` directory:

```powershell
python -m pip install -r requirements.txt
python app.py
```

Then open `http://localhost:3000`.

If you prefer a virtual environment and your local Python build supports it:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

## How To Demo

1. Upload one or more course files.
2. Enter a topic such as `central limit theorem`, `z-test`, or `hypothesis testing`.
3. Run one of the three commands.
4. If you run `daily quiz`, enter your score after finishing the quiz to update progress tracking.

## Running Tests

```powershell
pytest
```

## Verification Completed

- API upload flow tested with sample markdown material
- grounded command flow tested for `summary`
- unit tests cover engine logic, storage, and Flask request flow
- runtime study sessions persist to `data/runtime/`

## Notes

- Supported input types: `.pdf`, `.txt`, `.md`, `.csv`, `.log`
- Runtime session data is written under `data/runtime/` and ignored by git.
- The original public-repo prototype is preserved under `../docs/archive/original-prototype/`.
