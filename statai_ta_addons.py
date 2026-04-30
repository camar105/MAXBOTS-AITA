# =============================================================================
# StatAI-TA — OPTIONAL ADD-ONS
# =============================================================================
# Each section below is a self-contained feature upgrade.
# Follow the instructions in each section's header comment to add it to the
# original statai_ta.py file. You do not need to use all of them — pick the
# ones you want.
# =============================================================================


# -----------------------------------------------------------------------------
# ADDON 1: PDF CACHING (faster reloads)
# -----------------------------------------------------------------------------
# WHY: Without caching, every time the user clicks "Load Materials" it re-reads
# all PDFs from scratch. This saves parsed pages to disk so repeat loads are
# instant.
#
# HOW TO ADD:
# 1. Add this import at the top of the file with the other imports:
#       import hashlib
# 2. Add this constant near the top of the file (after the imports):
#       MATERIAL_CACHE_FILE = "materials_cache.json"
# 3. Replace the existing extract_text_from_pdfs() function with the one below.
# -----------------------------------------------------------------------------

import hashlib
import json

MATERIAL_CACHE_FILE = "materials_cache.json"

def extract_text_from_pdfs(uploaded_files):
    """Drop-in replacement for the original. Caches parsed pages to disk."""
    # Load existing cache from disk if it exists.
    if os.path.exists(MATERIAL_CACHE_FILE):
        with open(MATERIAL_CACHE_FILE, "r", encoding="utf-8") as f:
            cache = json.load(f)
    else:
        cache = {}

    all_chunks = []

    for pdf in uploaded_files:
        data = pdf.getvalue()
        # Create a unique key for this file based on its name and contents.
        digest = hashlib.sha256()
        digest.update(pdf.name.encode("utf-8"))
        digest.update(data)
        file_key = digest.hexdigest()

        if file_key in cache:
            # Already parsed before — load from cache.
            all_chunks.extend(cache[file_key])
            continue

        # Not cached — parse the PDF and store the result.
        import io
        import pdfplumber
        file_chunks = []
        with pdfplumber.open(io.BytesIO(data)) as doc:
            for i, page in enumerate(doc.pages):
                text = page.extract_text()
                if text and text.strip():
                    clean = re.sub(r"\s+", " ", text).strip()
                    file_chunks.append({
                        "text": clean,
                        "source": f"{pdf.name} - page {i + 1}"
                    })
        cache[file_key] = file_chunks
        all_chunks.extend(file_chunks)

    # Save updated cache back to disk.
    with open(MATERIAL_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)

    return all_chunks


# -----------------------------------------------------------------------------
# ADDON 2: TF-IDF SMARTER SEARCH (better retrieval)
# -----------------------------------------------------------------------------
# WHY: The original retrieve_context() just counts how many query words appear
# in each chunk. TF-IDF also weights rare words more heavily, so a page that
# mentions "heteroscedasticity" once ranks higher than one that mentions "the"
# a hundred times.
#
# HOW TO ADD:
# 1. Add this import at the top of the file with the other imports:
#       import math
#       from collections import Counter
# 2. Add this constant near the top of the file (after the imports):
#       STOPWORDS = {
#           "a","an","and","are","as","at","be","by","for","from","how","i",
#           "in","is","it","of","on","or","that","the","this","to","was",
#           "what","when","where","which","with","you","your",
#       }
# 3. Add the build_retrieval_index() function below anywhere before it is used.
# 4. Replace the existing retrieve_context() function with the one below.
# 5. After loading PDFs (inside the "Load Materials" button block), add this
#    line right after st.session_state.collection = chunks:
#       st.session_state.retrieval_index = build_retrieval_index(chunks)
#    And add "retrieval_index": {} to the session state defaults at the top.
# 6. Every call to retrieve_context() in the file currently passes
#    st.session_state.collection as the second argument. Change those calls to
#    pass st.session_state.retrieval_index instead.
# -----------------------------------------------------------------------------

import math
from collections import Counter

STOPWORDS = {
    "a","an","and","are","as","at","be","by","for","from","how","i",
    "in","is","it","of","on","or","that","the","this","to","was",
    "what","when","where","which","with","you","your",
}

def _tokenize(text: str) -> list:
    return [w for w in re.findall(r"[a-zA-Z0-9']+", text.lower()) if w not in STOPWORDS]

def build_retrieval_index(chunks: list) -> dict:
    """Call this once after loading PDFs. Pass the result to retrieve_context()."""
    documents = []
    doc_freq = Counter()
    for chunk in chunks:
        tokens = _tokenize(chunk["text"])
        counts = Counter(tokens)
        documents.append({**chunk, "tokens": tokens, "token_counts": counts})
        for token in set(tokens):
            doc_freq[token] += 1
    total = max(len(documents), 1)
    idf = {
        t: math.log((1 + total) / (1 + f)) + 1
        for t, f in doc_freq.items()
    }
    return {"documents": documents, "idf": idf, "total_docs": total}

def retrieve_context(query: str, index: dict, n: int = 6) -> str:
    """
    Drop-in replacement for the original retrieve_context().
    NOTE: the second argument is now the index dict from build_retrieval_index(),
    not the raw chunks list.
    """
    query_tokens = _tokenize(query)
    if not query_tokens or not index.get("documents"):
        return ""
    query_counts = Counter(query_tokens)
    scored = []
    for chunk in index["documents"]:
        score = 0.0
        for token, qcount in query_counts.items():
            if token in chunk["token_counts"]:
                score += (
                    (1 + math.log(chunk["token_counts"][token]))
                    * index["idf"].get(token, 1.0)
                    * qcount
                )
        if score > 0:
            scored.append((score, chunk))
    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:n]
    return "\n\n".join(f"[{c['source']}]\n{c['text']}" for _, c in top)


# -----------------------------------------------------------------------------
# ADDON 3: CONTEXT OVERFLOW PROTECTION (24k char cap)
# -----------------------------------------------------------------------------
# WHY: If many large PDF pages are retrieved, the combined context can exceed
# the model's context window and cause an API error. This caps the context
# before it is sent to the model.
#
# HOW TO ADD:
# 1. Add this constant near the top of the file (after the imports):
#       MAX_CONTEXT_CHARS = 24_000
# 2. Replace the existing retrieve_context() function with the version below
#    (or, if you already added Addon 2, add the truncation block at the end of
#    that version's build step — see the comment inside the function).
# NOTE: If you are using BOTH Addon 2 and Addon 3, just add the truncation
# block shown in the comment below into the Addon 2 retrieve_context() instead
# of using this standalone version.
# -----------------------------------------------------------------------------

MAX_CONTEXT_CHARS = 24_000

def retrieve_context_with_cap(query: str, chunks: list, n: int = 6) -> str:
    """
    Standalone drop-in for the original retrieve_context() that adds a
    character cap. Use this only if you are NOT using Addon 2.
    If using Addon 2, instead add the following lines at the end of that
    retrieve_context(), just before the final return statement:

        # Truncate to avoid exceeding the model context window.
        parts, total = [], 0
        for _, c in top:
            entry = f"[{c['source']}]\\n{c['text']}"
            if total + len(entry) > MAX_CONTEXT_CHARS:
                break
            parts.append(entry)
            total += len(entry)
        return "\\n\\n".join(parts)
    """
    query_words = set(query.lower().split())
    scored = []
    for chunk in chunks:
        text_lower = chunk["text"].lower()
        score = sum(1 for word in query_words if word in text_lower)
        scored.append((score, chunk))
    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:n]

    # Truncate to avoid exceeding the model context window.
    parts, total = [], 0
    for _, c in top:
        entry = f"[{c['source']}]\n{c['text']}"
        if total + len(entry) > MAX_CONTEXT_CHARS:
            break
        parts.append(entry)
        total += len(entry)
    return "\n\n".join(parts)


# -----------------------------------------------------------------------------
# ADDON 4: API ERROR HANDLING (friendly messages)
# -----------------------------------------------------------------------------
# WHY: If the API key is wrong or missing mid-session, the original code crashes
# with a raw exception. This wraps the call and shows a friendly message instead.
#
# HOW TO ADD:
# 1. Replace the existing ask_groq() function with the one below.
# -----------------------------------------------------------------------------

def ask_groq(user_prompt: str, context: str) -> str:
    """Drop-in replacement for the original ask_groq() with error handling."""
    from groq import Groq
    import streamlit as st

    api_key = st.session_state.get("api_key", "").strip()
    if not api_key:
        return "⚠️ No API key found. Please enter your Groq API key in the sidebar."
    try:
        client = Groq(api_key=api_key)
        full_prompt = f"{SYSTEM_PROMPT}\n\nCourse material context:\n{context}\n\n---\n\n{user_prompt}"
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": full_prompt}],
            temperature=0.3,
            max_tokens=1024,
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        return f"⚠️ API error: {exc}. Please check your Groq API key and try again."


# -----------------------------------------------------------------------------
# ADDON 5: QUIZ FEEDBACK FIX (no flashing)
# -----------------------------------------------------------------------------
# WHY: The original code calls st.success()/st.error() then immediately calls
# st.rerun(), so the feedback disappears before the user can read it.
# This stores feedback in session state so it renders properly on the next page.
#
# HOW TO ADD:
# 1. Add "quiz_feedback": None to the session state defaults block at the top
#    of the file, so it looks like:
#       for key, default in {
#           ...
#           "quiz_feedback": None,
#       }.items():
# 2. Find the quiz block (the `if st.session_state.quiz_active:` section) and
#    replace the inner `if idx < len(questions):` block with the one below.
# -----------------------------------------------------------------------------

# Paste this block to replace the existing `if idx < len(questions):` block
# inside the `if st.session_state.quiz_active:` section:

# ---- START PASTE ----
#
#   if idx < len(questions):
#       q = questions[idx]
#
#       # Show feedback from the previous answer before rendering the next question.
#       if st.session_state.quiz_feedback:
#           fb = st.session_state.quiz_feedback
#           if fb["correct"]:
#               st.success(fb["message"])
#           else:
#               st.error(fb["message"])
#           st.session_state.quiz_feedback = None
#
#       st.markdown(f"### Question {idx+1} of {len(questions)}")
#       st.markdown(f"**{q['question']}**")
#       choice = st.radio(
#           "Choose your answer:",
#           options=list(q["options"].keys()),
#           format_func=lambda k: f"{k}) {q['options'][k]}",
#           key=f"quiz_q_{idx}"
#       )
#       if st.button("Submit Answer"):
#           correct = q["answer"]
#           if choice == correct:
#               st.session_state.quiz_score += 1
#               st.session_state.quiz_feedback = {
#                   "correct": True,
#                   "message": f"✅ Correct! {q.get('explanation', '')}"
#               }
#           else:
#               topic_key = q["question"][:60]
#               st.session_state.weak_topics[topic_key] = st.session_state.weak_topics.get(topic_key, 0) + 1
#               save_history(st.session_state.weak_topics)
#               st.session_state.quiz_feedback = {
#                   "correct": False,
#                   "message": (
#                       f"❌ Incorrect. The answer is **{correct}**: "
#                       f"{q['options'].get(correct, '')}. {q.get('explanation', '')}"
#                   )
#               }
#           st.session_state.quiz_index += 1
#           st.rerun()
#
# ---- END PASTE ----


# -----------------------------------------------------------------------------
# ADDON 6: PROGRESS DASHBOARD TAB (weak topic tracking)
# -----------------------------------------------------------------------------
# WHY: The original only shows weak topics as a small sidebar list. This adds a
# dedicated Progress tab with metrics and a full breakdown.
#
# HOW TO ADD:
# 1. Find this line near the top of the file:
#       tab_study, tab_quiz, tab_progress = st.tabs(["Study", "Quiz", "Progress"])
#    If the original does not use tabs, first wrap the existing UI sections in
#    tabs by adding:
#       tab_main, tab_progress = st.tabs(["Study & Quiz", "Progress"])
#    Then indent the existing page content under `with tab_main:` and add
#    `with tab_progress:` below it.
# 2. Inside the `with tab_progress:` block, paste the render_progress() call
#    and add the function definition below anywhere before it is called.
# -----------------------------------------------------------------------------

def render_progress():
    """Paste this function into the file, then call render_progress() inside
    your `with tab_progress:` block."""
    import streamlit as st

    weak_topics = st.session_state.get("weak_topics", {})
    collection = st.session_state.get("collection", [])
    total_misses = sum(weak_topics.values())

    st.subheader("📈 Progress Dashboard")

    col1, col2, col3 = st.columns(3)
    col1.metric("Pages Loaded", len(collection))
    col2.metric("Total Misses", total_misses)
    col3.metric("Weak Topics", len(weak_topics))

    st.markdown("---")

    if weak_topics:
        st.markdown("**Your weakest topics (most missed first):**")
        sorted_topics = sorted(weak_topics.items(), key=lambda x: x[1], reverse=True)
        for topic, count in sorted_topics[:10]:
            bar = "🟥" * min(count, 10)
            st.markdown(f"- {bar} **{topic[:80]}** — missed {count} time(s)")

        st.markdown("---")
        if st.button("🗑️ Reset Progress History", use_container_width=True):
            st.session_state.weak_topics = {}
            save_history({})
            st.success("Progress history cleared.")
            st.rerun()
    else:
        st.info("No missed topics yet. Complete a quiz to start tracking your progress here.")
