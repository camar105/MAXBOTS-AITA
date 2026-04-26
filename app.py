import streamlit as st
import pdfplumber
import json
import os
import re
from groq import Groq

st.set_page_config(page_title="StatAI-TA", page_icon="📊", layout="centered")

for key, default in {
    "messages": [],
    "quiz_active": False,
    "quiz_questions": [],
    "quiz_index": 0,
    "quiz_score": 0,
    "weak_topics": {},
    "docs_loaded": False,
    "collection": [],
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

HISTORY_FILE = "quiz_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE) as f:
            return json.load(f)
    return {}

def save_history(data):
    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=2)

def extract_text_from_pdfs(uploaded_files):
    all_chunks = []
    for pdf in uploaded_files:
        with pdfplumber.open(pdf) as doc:
            for i, page in enumerate(doc.pages):
                text = page.extract_text()
                if text and text.strip():
                    all_chunks.append({
                        "text": text.strip(),
                        "source": f"{pdf.name} - page {i+1}"
                    })
    return all_chunks

def retrieve_context(query, chunks, n=6):
    query_words = set(query.lower().split())
    scored = []
    for chunk in chunks:
        text_lower = chunk["text"].lower()
        score = sum(1 for word in query_words if word in text_lower)
        scored.append((score, chunk))
    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:n]
    context = "\n\n".join(f"[{c['source']}]\n{c['text']}" for _, c in top)
    return context

SYSTEM_PROMPT = """You are StatAI-TA, a friendly and patient AI teaching assistant
for an introductory undergraduate statistics course.

Rules you must always follow:
1. ONLY use the course material provided in the context below. Do not add outside knowledge.
2. Use plain, everyday English. Avoid statistical jargon. If you must use a technical term,
   immediately explain it in simple words.
3. Keep explanations short and beginner-friendly.
4. If the answer is not in the provided context, say:
   I couldn't find that in your course materials. Check your notes or ask your professor.
5. Never make up formulas, definitions, or facts."""

def ask_groq(user_prompt, context):
    client = Groq(api_key=st.session_state.api_key)
    full_prompt = f"{SYSTEM_PROMPT}\n\nCourse material context:\n{context}\n\n---\n\n{user_prompt}"
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": full_prompt}],
        temperature=0.3,
        max_tokens=1024
    )
    return response.choices[0].message.content

def generate_quiz(chunks, weak_topics):
    weak_str = ""
    if weak_topics:
        sorted_weak = sorted(weak_topics.items(), key=lambda x: x[1], reverse=True)
        top_weak = [t for t, _ in sorted_weak[:3]]
        weak_str = f"Focus especially on these topics the student has struggled with: {', '.join(top_weak)}."
    prompt = f"""Generate exactly 5 multiple-choice quiz questions from the course material below.
{weak_str}
Each question must follow this exact format (no deviations):

Q: [question text]
A) [option]
B) [option]
C) [option]
D) [option]
Answer: [A/B/C/D]
Explanation: [one plain-English sentence explaining why]

Only use content from the provided course materials."""
    context = retrieve_context("statistics concepts quiz questions", chunks, n=8)
    raw = ask_groq(prompt, context)
    return parse_quiz(raw)

def parse_quiz(raw_text):
    questions = []
    blocks = re.split(r'\n(?=Q:)', raw_text.strip())
    for block in blocks:
        lines = [l.strip() for l in block.strip().splitlines() if l.strip()]
        q_dict = {}
        options = {}
        for line in lines:
            if line.startswith("Q:"):
                q_dict["question"] = line[2:].strip()
            elif line.startswith("A)"):
                options["A"] = line[2:].strip()
            elif line.startswith("B)"):
                options["B"] = line[2:].strip()
            elif line.startswith("C)"):
                options["C"] = line[2:].strip()
            elif line.startswith("D)"):
                options["D"] = line[2:].strip()
            elif line.startswith("Answer:"):
                q_dict["answer"] = line.split(":", 1)[1].strip().upper()[0]
            elif line.startswith("Explanation:"):
                q_dict["explanation"] = line.split(":", 1)[1].strip()
        if "question" in q_dict and options and "answer" in q_dict:
            q_dict["options"] = options
            questions.append(q_dict)
    return questions

st.title("📊 StatAI-TA")
st.caption("Your personalized statistics study assistant")

with st.sidebar:
    st.header("Setup")
    api_key_input = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
    if api_key_input:
        st.session_state.api_key = api_key_input
    st.markdown("---")
    st.header("Upload Course Materials")
    uploaded_files = st.file_uploader("Upload your PDFs (syllabus, slides, notes)", type="pdf", accept_multiple_files=True)
    if uploaded_files and st.button("📥 Load Materials"):
        if not st.session_state.get("api_key"):
            st.error("Please enter your Groq API key first.")
        else:
            with st.spinner("Reading PDFs and building knowledge base…"):
                chunks = extract_text_from_pdfs(uploaded_files)
                if not chunks:
                    st.error("No readable text found in your PDFs.")
                else:
                    st.session_state.collection = chunks
                    st.session_state.docs_loaded = True
                    st.session_state.weak_topics = load_history()
                    st.success(f"Loaded {len(chunks)} pages from {len(uploaded_files)} file(s).")
    if st.session_state.docs_loaded:
        st.markdown("---")
        st.success("✅ Materials loaded")
        if st.session_state.weak_topics:
            st.markdown("**Your weak topics:**")
            for topic, count in sorted(st.session_state.weak_topics.items(), key=lambda x: x[1], reverse=True)[:5]:
                st.markdown(f"- {topic} *(missed {count}x)*")

if st.session_state.docs_loaded and not st.session_state.quiz_active:
    st.markdown("### What would you like to do?")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📝 Daily Quiz", use_container_width=True):
            with st.spinner("Generating quiz questions from your materials…"):
                questions = generate_quiz(st.session_state.collection, st.session_state.weak_topics)
            if questions:
                st.session_state.quiz_questions = questions
                st.session_state.quiz_active = True
                st.session_state.quiz_index = 0
                st.session_state.quiz_score = 0
                st.rerun()
            else:
                st.error("Couldn't generate questions. Try uploading more material.")
    with col2:
        if st.button("📖 Summary", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "summary"})
    with col3:
        if st.button("💡 Explain Topic", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "explain_prompt"})

if st.session_state.quiz_active:
    questions = st.session_state.quiz_questions
    idx = st.session_state.quiz_index
    if idx < len(questions):
        q = questions[idx]
        st.markdown(f"### Question {idx+1} of {len(questions)}")
        st.markdown(f"**{q['question']}**")
        choice = st.radio("Choose your answer:", options=list(q["options"].keys()), format_func=lambda k: f"{k}) {q['options'][k]}", key=f"quiz_q_{idx}")
        if st.button("Submit Answer"):
            correct = q["answer"]
            if choice == correct:
                st.success(f"✅ Correct! {q.get('explanation', '')}")
                st.session_state.quiz_score += 1
            else:
                st.error(f"❌ Incorrect. The answer is **{correct}**: {q['options'].get(correct, '')}. {q.get('explanation', '')}")
                topic_key = q["question"][:60]
                st.session_state.weak_topics[topic_key] = st.session_state.weak_topics.get(topic_key, 0) + 1
                save_history(st.session_state.weak_topics)
            st.session_state.quiz_index += 1
            st.rerun()
    else:
        total = len(questions)
        score = st.session_state.quiz_score
        st.markdown("## Quiz Complete! 🎉")
        st.markdown(f"### Score: {score} / {total}")
        if score == total:
            st.balloons()
            st.success("Perfect score! Great work.")
        elif score >= total * 0.7:
            st.info("Good job! Review the topics you missed.")
        else:
            st.warning("Keep studying — your weak topics will be prioritized next quiz.")
        if st.button("Back to Main Menu"):
            st.session_state.quiz_active = False
            st.rerun()

if st.session_state.docs_loaded and not st.session_state.quiz_active:
    st.markdown("---")
    st.markdown("### Or type a command below:")
    st.caption("Try: **summary** · **explain hypothesis testing** · **explain standard deviation**")
    for msg in st.session_state.messages:
        if msg["role"] == "user" and msg["content"] not in ("summary", "explain_prompt"):
            with st.chat_message("user"):
                st.markdown(msg["content"])
        elif msg["role"] == "assistant":
            with st.chat_message("assistant"):
                st.markdown(msg["content"])
    if st.session_state.messages:
        last = st.session_state.messages[-1]
        if last["role"] == "user":
            content = last["content"]
            response = None
            if content == "summary":
                with st.spinner("Summarizing your course materials…"):
                    context = retrieve_context("statistics course summary overview topics", st.session_state.collection, n=8)
                    response = ask_groq("Give me a plain-English summary of the main topics covered in my course materials. Use simple language. Use bullet points.", context)
            elif content == "explain_prompt":
                st.session_state.messages.pop()
                st.info("Type your question below, e.g. **explain standard deviation**")
            elif content.lower().startswith("explain"):
                topic = content[7:].strip() or "the main statistics concepts"
                with st.spinner(f"Explaining '{topic}'…"):
                    context = retrieve_context(topic, st.session_state.collection, n=5)
                    response = ask_groq(f"Explain '{topic}' in plain English using only the course materials. No jargon. Beginner-friendly.", context)
            else:
                with st.spinner("Thinking…"):
                    context = retrieve_context(content, st.session_state.collection, n=5)
                    response = ask_groq(content, context)
            if response:
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
    user_input = st.chat_input("Type a command or question…")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input.strip()})
        st.rerun()

elif not st.session_state.docs_loaded:
    st.info("👈 Upload your course PDFs in the sidebar to get started.")