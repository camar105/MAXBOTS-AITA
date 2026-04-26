# StatAI-TA — MVP
*Max's Bots: MAE 301 Spring 2026*

A personalized AI teaching assistant for introductory statistics students. Upload your course PDFs and get explanations, summaries, and adaptive quizzes in concise and simple words, grounded entirely in your own course materials.

---

# What This Does

StatAI-TA takes your uploaded statistics course materials (lecture slides, notes, textbook excerpts as PDFs) and lets you perform,

- **Daily Quiz** — 5 multiple-choice questions generated from your materials, weighted toward topics you've previously missed
- **Summary** — plain-English bullet point recap of everything in your uploaded materials
- **Explain Topic** — type "explain [any topic]" and get a beginner-friendly explanation using only your course slides

---

## Requirements

- Python 3.10 or higher
- A free Groq API key (get one at console.groq.com — no credit card needed)
- Your statistics course PDFs

---

## Setup

### Step 1 — Clone the repository
```
git clone https://github.com/camar105/MAXBOTS-AITA.git
cd MAXBOTS-AITA/mvp
```

### Step 2 — Install dependencies
```
pip install streamlit groq pdfplumber
```

### Step 3 — Run the app
```
streamlit run app.py
```

The app will open automatically in your browser at http://localhost:8501

---

## How to Use

1. Go to console.groq.com, sign up for free, and create an API key
2. Open the app in your browser
3. Paste your Groq API key into the left sidebar
4. Upload one or more statistics course PDFs using the file uploader
5. Click Load Materials and wait for the green confirmation
6. Use the three buttons or type in the chat:
   - Daily Quiz — generates 5 questions from your materials
   - Summary — plain-English overview of your uploaded content
   - Type "explain [topic]" — e.g. "explain p-value" or "explain hypothesis testing"

---

## Example Commands

```
explain hypothesis testing
explain what a p-value means
explain confidence intervals
summary
explain standard deviation
explain central limit theorem
```

---

## How It Works

1. PDFs are parsed page by page using pdfplumber
2. Each page becomes a searchable chunk tagged with its source and page number
3. When you ask a question, the system finds the most relevant pages using keyword matching
4. Those pages are passed to the Groq API (llama-3.3-70b-versatile model) along with a strict system prompt that enforces plain language and prohibits going outside the uploaded content
5. Quiz answers marked wrong are saved to quiz_history.json and prioritized in future quizzes

---

## File Structure

```
mvp/
├── app.py              — Main Streamlit application
├── README.md           — This file
├── report.md           — Full MVP report
└── quiz_history.json   — Auto-created; stores your missed quiz topics
```

---

## Team

Max's Bots | MAE 301 Applied Experimental Statistics 

Lily Urbanczyk | Kolter Nelson | Edward Bernstein | Carlos Martinez | Oscar Barrera | Carter Baldwin
