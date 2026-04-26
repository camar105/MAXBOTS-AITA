# StatAI-TA — Report
**Team:** Max's Bots | MAE 301 Applied Experimental Statistics

**Team Members:**
- Lily Urbanczyk | lurbancz@asu.edu
- Kolter Nelson | knels104@asu.edu
- Edward Bernstein | egbernst@asu.edu
- Carlos Martinez | camar105@asu.edu
- Oscar Barrera | oabarre2@asu.edu
- Carter Baldwin | cdbaldw4@asu.edu

---

## 1. Executive Summary

Introductory statistics students already have access to powerful general purpose AI tools like ChatGPT and Claude, but those tools do not know the student, do not know their course, and do not stay within what has actually been taught. StatAI-TA is a personalized AI teaching assistant that is grounded in a student's own uploaded course materials. A student uploads their PDFs — lecture slides, notes, textbook excerpts — and the system returns structured, plain-English explanations, course-accurate summaries, and adaptive quizzes that prioritize topics the student keeps missing.

The MVP is a working Streamlit web application. A student uploads their course PDFs and uses three commands — Daily Quiz, Summary, and Explain Topic — to study using only their own course content as the source.

---

## 2. User and Use Case

**Primary User:** An undergraduate student enrolled in an introductory statistics course, typically a student with no experience in statistics taking the course as a requirement with no prior background in probability or statistical reasoning. No excessive statistical jargon!



---

## 3. MVP Definition

A user uploads their statistics course PDFs and the system returns:
- A structured daily quiz of 5 multiple-choice questions generated from the uploaded materials, weighted toward previously missed topics
- A plain-English summary of everything covered in the uploaded materials
- A targeted explanation of any topic using only the uploaded course content

---

## 4. System Architecture

### Pipeline Overview

```
Student uploads PDFs
        |
        v
PDF text extraction (pdfplumber) — page by page
        |
        v
Keyword-based retrieval — finds most relevant pages for each query
        |
        v
Groq API (llama-3.3-70b-versatile) + strict system prompt
        |
        v
Plain-English output displayed in Streamlit interface
        |
        v
Wrong quiz answers saved to quiz_history.json
Next quiz weighted toward missed topics
```

### Key Technical Components

**PDF Extraction:** pdfplumber extracts text page by page. Each page becomes one chunk tagged with the filename and page number.

**Retrieval:** When a student asks a question, the system scores every chunk by counting how many query words appear in it. The top 6 most relevant chunks are passed to the model as context. This is a lightweight keyword matching approach that requires no embeddings or vector database.

**Generation:** Groq API running llama-3.3-70b-versatile receives the retrieved context plus a strict system prompt that instructs the model to only use the provided material, use plain language, and never invent facts.

**Weak Topic Tracking:** Incorrect quiz answers are logged to a local quiz_history.json file. The next quiz generation prompt includes the top 3 most-missed topics, instructing the model to weight questions toward those areas.

### System Prompt

The model receives these rules on every request:
1. Only use the course material provided in the context. Do not add outside knowledge.
2. Use plain everyday English. Avoid statistical jargon.
3. Keep explanations short and beginner-friendly.
4. If the answer is not in the provided context, say so — do not invent it.
5. Never make up formulas, definitions, or facts.

---

## 5. Evaluation

### Baseline vs. StatAI-TA Comparison

**Test prompt:** "Explain hypothesis testing"

| Dimension | Baseline GPT (no system prompt, no context) | StatAI-TA |
|---|---|---|
| Language level | Uses terms like "asymptotic normality," "null distribution," "Type I error rate" without defining them | Plain English only — technical terms immediately explained in everyday language |
| Grounded in course material | No — draws from general statistical knowledge | Yes — references only uploaded slide content |
| Consistent structure | No — format changes every run | Yes — same structure every time |
| Stays within course scope | No — may introduce topics not yet covered | Yes — constrained to uploaded materials |

### Before vs. After Example

**Baseline response (GPT, no system prompt):**
Hypothesis testing is a statistical method used to make inferences about population parameters based on sample data. Under the null hypothesis H0, we assume no effect exists. The test statistic is compared against a reference distribution to compute a p-value, which represents the probability of observing data at least as extreme as the sample under H0 assuming the null is true.

**StatAI-TA response (same question, with uploaded Week 8 slides):**
Hypothesis testing is a way to use your data to answer a yes-or-no question about a population. You start by assuming nothing unusual is happening. That is your null hypothesis. Then you look at what you actually observed in your data and ask: how surprising would this be if nothing unusual were happening? If the answer is very surprising, you reject your starting assumption. Your week 8 slides describe this using the p-value, it is the probability of getting a result this extreme just by chance.

### Weak Topic Tracking Result

After a simulated 3-session quiz sequence where a student consistently missed p-value questions, the next generated quiz contained 3 of 5 questions directly addressing p-values, compared to 1 of 5 in the first session. The weighting behavior worked as designed.

---

## 6. Limitations

**PDF extraction quality:** Slides that are primarily images or scanned documents will not extract text correctly, limiting the system's ability to answer questions about visual content.

**No persistent session memory:** The knowledge base resets when the app restarts. Students must re-upload PDFs each session. Only quiz history persists via the local JSON file.

**Keyword retrieval is simple:** The current retrieval method scores chunks by word frequency rather than semantic meaning. This means a question phrased differently from how the slide is written may not retrieve the best chunks.

**No instructor portal:** Each student must upload their own files. There is no shared class-wide knowledge base.

**Output quality depends on PDF quality:** If uploaded materials are sparse, poorly formatted, or very short, output quality degrades.

---

## 7. Next Steps

- Add vision-capable PDF processing to handle image-heavy lecture slides
- Replace keyword retrieval with semantic search using embeddings for better accuracy
- Build a professor-facing upload portal so one knowledge base serves an entire class
- Add a readability metric (Flesch-Kincaid) to automatically verify plain-language compliance
- Conduct user testing with real introductory statistics students and measure comprehension improvement
- Explore a course timeline feature so the system knows which week's material to draw from
