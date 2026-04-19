# MVP Report

## 1. Executive Summary

StatAI-TA is a local, single-user study assistant built for introductory statistics students. The MVP lets a user upload course material, choose a study command, and receive a grounded response from the uploaded content instead of a generic internet-facing answer.

The implemented MVP supports three commands:

- `summary`
- `explain`
- `daily quiz`

The system also stores quiz history locally so that repeated weak topics can be identified.

## 2. User And Use Case

### Primary user

An undergraduate student taking an introductory statistics course who wants faster, clearer, course-aligned AI help.

### Example use case

The student uploads lecture notes or a statistics problem set, enters `central limit theorem` or `z-test`, and asks the system to:

- summarize the topic in a review-friendly format
- explain it in plain language
- build a 10-question quiz tied to the uploaded material

After the quiz, the student records their score so the app can highlight weaker areas later.

## 3. System Design

### High-level flow

1. User uploads PDF or text material.
2. The backend extracts text from those files.
3. The text is split into overlapping chunks.
4. A command and optional topic are used to retrieve the most relevant chunks.
5. A local mock study engine generates a grounded response from the retrieved chunks.
6. Quiz performance is stored locally in JSON.

### Architecture diagram

```text
User Browser
    |
    v
Flask UI + API (app.py)
    |
    +--> File ingestion (.pdf/.txt/.md/.csv/.log)
    |       |
    |       v
    |   Text extraction + normalization
    |       |
    |       v
    |   Chunk builder (overlapping text passages)
    |
    +--> Command router (summary / explain / daily quiz)
            |
            v
      Local retrieval scorer
            |
            v
      Mock study engine
            |
            +--> grounded response markdown
            +--> 10-question quiz
            +--> answer key
            |
            v
      Local progress storage (JSON)
```

### Main components

- `app.py`: Flask routes and API layer
- `src/maxbots_mvp/engine.py`: parsing, chunking, retrieval, and grounded response generation
- `src/maxbots_mvp/storage.py`: session/progress persistence
- `templates/index.html`, `static/app.js`, `static/styles.css`: browser UI

## 4. Data

### Data sources used by the MVP

- student-uploaded PDFs
- student-uploaded text/markdown files
- sample statistics materials included in the repository for demo use

### Processing

- PDFs are parsed with `pypdf`
- text files are decoded directly
- extracted text is normalized and chunked into 140-word passages with 25-word overlap for retrieval

### Data size and splits

- The MVP is not trained on a fixed dataset, so there is no train/validation split in Phase 3.
- Instead, the system operates on user-uploaded course material at runtime.
- Included repository demo material consists of:
  - a sample statistics textbook PDF in `data/samples/`
  - two sample markdown study/example files in `data/examples/`
- During verification, `Stats_Problem.md` was successfully parsed into 5 retrieval chunks for a working smoke test.

No external dataset is required for the MVP itself; the system is grounded in user-provided material.

## 5. Models And AI Strategy

The original concept planned to use hosted language models plus retrieval. For this submission-ready MVP, the system is mock-first and deterministic by design.

### Why this choice was made

- the project must be runnable locally without API credentials
- the main product workflow can still be demonstrated credibly
- grounded retrieval and command routing can still be evaluated

### Current AI-related behavior

- local retrieval selects grounded chunks relevant to the user's topic
- the study engine produces structured summaries and explanations from those chunks
- the quiz builder creates a 10-question grounded quiz from retrieved content

This keeps the system aligned with the product goal even without a live hosted model.

## 6. Evaluation

### Automated tests

The MVP includes tests covering:

- summary generation sections
- quiz generation count and content
- storage round-trip for sessions and progress
- app-level request flow via Flask test client

### Verification completed

- Python files compile successfully
- unit tests pass with `pytest`
- end-to-end upload plus command flow succeeds against a sample file
- the Flask app responds correctly for upload, command execution, and progress persistence in local testing

### Reproducibility

The MVP can be reproduced locally with the checked-in code and `requirements.txt`. No external API key is required for the default demo path.

## 7. Limitations And Risks

- The current system uses a deterministic mock provider instead of a hosted language model.
- PDF extraction quality still depends on the source PDF.
- Retrieval is lightweight and local, not embedding-based.
- Image-heavy lecture slides are not a first-class path in this build.
- Quiz scoring is user-recorded rather than automatically graded from typed answers.

## 8. Next Steps

With more time, the next improvements would be:

1. add an optional hosted-model provider behind configuration
2. upgrade retrieval from local scoring to embedding-based search
3. add automatic answer grading for quiz responses
4. support diagram/image-heavy lecture slides more directly
5. persist user progress in a stronger local database such as SQLite
