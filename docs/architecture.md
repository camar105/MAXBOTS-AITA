# Architecture Notes

## Repository Layout

- `proposal/` contains the Phase 1 concept write-up.
- `nanogpt/` contains the Phase 2 model implementation, experiments, and report.
- `mvp/` contains the Phase 3 product implementation and report.
- `docs/assets/phase1/` stores the original report and video artifacts.
- `docs/archive/original-prototype/` preserves the original rapid prototype that was in the public repo.

## MVP Design

The rebuilt MVP is intentionally mock-first so it can run locally without paid API access.

Core flow:

1. Upload one or more course files.
2. Parse PDF and text inputs into plain text.
3. Chunk the extracted text into small grounded passages.
4. Route a user command (`summary`, `explain`, or `daily quiz`).
5. Retrieve the most relevant chunks with local scoring.
6. Produce a grounded response using a local mock provider by default.
7. Store quiz history and topic-level progress locally.

## Why This Design

- It matches the course MVP scope.
- It avoids blocking on API keys.
- It remains easy to test locally.
- It still leaves room for an optional hosted-model provider later.
