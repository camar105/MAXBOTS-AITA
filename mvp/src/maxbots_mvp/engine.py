from __future__ import annotations

import io
import re
import textwrap
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from pypdf import PdfReader


TEXT_EXTENSIONS = {".txt", ".md", ".csv", ".log"}
SUPPORTED_EXTENSIONS = TEXT_EXTENSIONS | {".pdf"}
STOPWORDS = {
    "a",
    "about",
    "after",
    "all",
    "also",
    "an",
    "and",
    "any",
    "are",
    "as",
    "at",
    "be",
    "because",
    "been",
    "before",
    "being",
    "between",
    "both",
    "but",
    "by",
    "can",
    "do",
    "does",
    "each",
    "for",
    "from",
    "had",
    "has",
    "have",
    "how",
    "if",
    "in",
    "into",
    "is",
    "it",
    "its",
    "may",
    "more",
    "most",
    "must",
    "no",
    "not",
    "of",
    "on",
    "or",
    "our",
    "out",
    "over",
    "same",
    "should",
    "so",
    "some",
    "such",
    "than",
    "that",
    "the",
    "their",
    "them",
    "then",
    "there",
    "these",
    "they",
    "this",
    "those",
    "through",
    "to",
    "under",
    "up",
    "use",
    "uses",
    "using",
    "very",
    "was",
    "we",
    "were",
    "what",
    "when",
    "where",
    "which",
    "while",
    "who",
    "why",
    "will",
    "with",
    "you",
    "your",
}


@dataclass(slots=True)
class DocumentChunk:
    chunk_id: str
    source_name: str
    text: str
    word_count: int

    def to_dict(self) -> dict[str, str | int]:
        return {
            "chunk_id": self.chunk_id,
            "source_name": self.source_name,
            "text": self.text,
            "word_count": self.word_count,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, str | int]) -> "DocumentChunk":
        return cls(
            chunk_id=str(payload["chunk_id"]),
            source_name=str(payload["source_name"]),
            text=str(payload["text"]),
            word_count=int(payload["word_count"]),
        )


@dataclass(slots=True)
class QuizQuestion:
    number: int
    prompt: str
    answer: str


@dataclass(slots=True)
class StudyResponse:
    command: str
    title: str
    markdown: str
    sources: list[dict[str, str]] = field(default_factory=list)
    questions: list[QuizQuestion] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "command": self.command,
            "title": self.title,
            "markdown": self.markdown,
            "sources": self.sources,
        }
        if self.questions:
            payload["quiz"] = [{"number": item.number, "prompt": item.prompt} for item in self.questions]
            payload["answerKey"] = [{"number": item.number, "answer": item.answer} for item in self.questions]
        return payload


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def extract_text_from_bytes(filename: str, raw_bytes: bytes) -> str:
    extension = Path(filename).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise ValueError(f"Unsupported file type: {extension or 'unknown'}. Supported types: {supported}")

    if extension == ".pdf":
        reader = PdfReader(io.BytesIO(raw_bytes))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    else:
        text = raw_bytes.decode("utf-8", errors="ignore")

    cleaned = normalize_text(text)
    if not cleaned:
        raise ValueError(f"Could not extract readable text from {filename}.")
    return cleaned


def build_chunks(documents: Iterable[tuple[str, str]], chunk_size: int = 140, overlap: int = 25) -> list[DocumentChunk]:
    chunks: list[DocumentChunk] = []
    for source_name, text in documents:
        words = text.split()
        if not words:
            continue

        if len(words) <= chunk_size:
            chunk_text = " ".join(words)
            chunks.append(
                DocumentChunk(
                    chunk_id=f"{Path(source_name).stem}-1",
                    source_name=source_name,
                    text=chunk_text,
                    word_count=len(words),
                )
            )
            continue

        start = 0
        chunk_number = 1
        while start < len(words):
            end = min(len(words), start + chunk_size)
            chunk_text = " ".join(words[start:end]).strip()
            if chunk_text:
                chunks.append(
                    DocumentChunk(
                        chunk_id=f"{Path(source_name).stem}-{chunk_number}",
                        source_name=source_name,
                        text=chunk_text,
                        word_count=end - start,
                    )
                )
                chunk_number += 1
            if end == len(words):
                break
            start = max(end - overlap, start + 1)
    return chunks


def tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[a-zA-Z0-9']+", text.lower())
    return [token for token in tokens if len(token) > 2 and token not in STOPWORDS]


def split_sentences(text: str) -> list[str]:
    pieces = re.split(r"(?<=[.!?])\s+", text)
    results: list[str] = []
    for piece in pieces:
        cleaned = normalize_text(piece)
        if 35 <= len(cleaned) <= 320:
            results.append(cleaned)
    return results


def dedupe_keep_order(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        key = re.sub(r"\W+", "", item).lower()
        if key and key not in seen:
            ordered.append(item)
            seen.add(key)
    return ordered


def build_source_payload(chunks: Iterable[DocumentChunk]) -> list[dict[str, str]]:
    payload: list[dict[str, str]] = []
    for chunk in chunks:
        payload.append(
            {
                "source": chunk.source_name,
                "chunk": chunk.chunk_id,
                "excerpt": textwrap.shorten(chunk.text, width=180, placeholder="..."),
            }
        )
    return payload


def retrieve_relevant_chunks(chunks: list[DocumentChunk], command: str, topic: str, limit: int = 4) -> list[DocumentChunk]:
    query_terms = tokenize(f"{command} {topic}")
    if not query_terms:
        return chunks[:limit]

    ranked: list[tuple[float, DocumentChunk]] = []
    for chunk in chunks:
        chunk_terms = Counter(tokenize(chunk.text))
        overlap = sum(chunk_terms.get(term, 0) for term in query_terms)
        phrase_bonus = 3.0 if topic and topic.lower() in chunk.text.lower() else 0.0
        density = overlap / max(chunk.word_count, 1)
        score = overlap + phrase_bonus + density * 50
        if score > 0:
            ranked.append((score, chunk))

    if not ranked:
        return chunks[:limit]

    ranked.sort(key=lambda item: item[0], reverse=True)
    return [item[1] for item in ranked[:limit]]


def select_ranked_sentences(chunks: list[DocumentChunk], topic: str) -> list[str]:
    query_terms = tokenize(topic)
    scored: list[tuple[float, str]] = []
    for chunk in chunks:
        for sentence in split_sentences(chunk.text):
            sentence_terms = Counter(tokenize(sentence))
            overlap = sum(sentence_terms.get(term, 0) for term in query_terms)
            score = overlap * 2 + min(len(sentence) / 120, 1.5)
            scored.append((score, sentence))

    scored.sort(key=lambda item: item[0], reverse=True)
    return dedupe_keep_order(sentence for _, sentence in scored)


def collect_formula_notes(chunks: list[DocumentChunk]) -> list[str]:
    formula_notes: list[str] = []
    hints = ("=", "variance", "standard deviation", "probability", "z", "mean", "p(")
    for chunk in chunks:
        for sentence in split_sentences(chunk.text):
            lowered = sentence.lower()
            if any(hint in lowered for hint in hints) or any(symbol in sentence for symbol in ("=", "/", "^")):
                formula_notes.append(sentence)
    deduped = dedupe_keep_order(formula_notes)
    if not deduped:
        return ["No explicit formula provided in the uploaded material."]
    return [textwrap.shorten(note, width=160, placeholder="...") for note in deduped[:3]]


def infer_topic_label(topic: str, chunks: list[DocumentChunk]) -> str:
    cleaned = topic.strip()
    if cleaned:
        return cleaned
    if chunks:
        return Path(chunks[0].source_name).stem.replace("_", " ")
    return "Uploaded Material"


def select_key_terms(chunks: list[DocumentChunk], limit: int = 8) -> list[str]:
    counter: Counter[str] = Counter()
    for chunk in chunks:
        counter.update(tokenize(chunk.text))
    return [term for term, _ in counter.most_common(limit)]


def choose_focus_term(sentence: str, used_terms: set[str]) -> str:
    for token in tokenize(sentence):
        if token not in used_terms and len(token) >= 5:
            used_terms.add(token)
            return token
    return ""


def blank_out_term(sentence: str, term: str) -> str:
    if not term:
        return sentence
    pattern = re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE)
    replaced = pattern.sub("_____", sentence, count=1)
    return replaced if replaced != sentence else sentence


class MockStudyProvider:
    def build_summary(self, topic: str, relevant_chunks: list[DocumentChunk], progress: dict[str, object]) -> StudyResponse:
        topic_label = infer_topic_label(topic, relevant_chunks)
        ranked_sentences = select_ranked_sentences(relevant_chunks, topic_label)
        overview = ranked_sentences[0] if ranked_sentences else "The uploaded material did not provide enough detail to summarize this topic cleanly."
        key_points = ranked_sentences[:4] or [overview]
        formula_notes = collect_formula_notes(relevant_chunks)
        weak_topics = progress.get("weakTopics", []) if isinstance(progress, dict) else []

        applications = [
            f"Use {topic_label} when a homework problem asks you to explain or justify a statistics result from the uploaded notes.",
            f"Use the grounded material from {relevant_chunks[0].source_name if relevant_chunks else 'your uploads'} to match class wording and examples.",
            "Use the retrieved notes as a first check before jumping straight to a formula.",
        ]

        mistakes = [
            f"Mixing up the main idea of {topic_label} with the steps used to solve a problem.",
            "Plugging values into a formula before defining what each variable means.",
            "Answering a different question than the one the notes or homework actually ask.",
        ]
        if weak_topics:
            mistakes.append(f"Ignoring past quiz trouble spots such as {weak_topics[0]} when reviewing this topic.")

        tips = [
            "Start by stating what the question gives you and what it wants you to find.",
            "Match the wording in your answer to the grounded material before doing calculations.",
            "After solving, check whether your result agrees with the pattern described in the notes.",
        ]

        markdown = "\n".join(
            [
                f"# Summary: {topic_label}",
                "",
                "## Topic Overview",
                overview,
                "",
                "## Key Points",
                *[f"- {point}" for point in key_points],
                "",
                "## Important Formulas",
                *[f"- {note}" for note in formula_notes],
                "",
                "## What These Ideas Apply To",
                *[f"- {item}" for item in applications],
                "",
                "## Common Mistakes",
                *[f"- {item}" for item in mistakes],
                "",
                "## Problem-Solving Tips",
                *[f"- {item}" for item in tips],
                "",
                "## Quick Recap",
                f"Focus on the grounded definition, the matching setup, and the result the problem is asking for when you review {topic_label}.",
            ]
        )
        return StudyResponse(
            command="summary",
            title=f"Summary: {topic_label}",
            markdown=markdown,
            sources=build_source_payload(relevant_chunks),
        )

    def build_explanation(self, topic: str, relevant_chunks: list[DocumentChunk], progress: dict[str, object]) -> StudyResponse:
        topic_label = infer_topic_label(topic, relevant_chunks)
        ranked_sentences = select_ranked_sentences(relevant_chunks, topic_label)
        main_line = ranked_sentences[0] if ranked_sentences else "The uploaded material did not provide enough detail to explain this topic yet."
        support_lines = ranked_sentences[1:4]
        weak_topics = progress.get("weakTopics", []) if isinstance(progress, dict) else []

        review_notes = [
            "Explain the idea in words before reaching for a formula.",
            "Connect each step back to the phrase the class materials use.",
            "If a result feels surprising, go back to the definition and assumptions first.",
        ]
        if weak_topics:
            review_notes.append(f"Your weakest recorded topic right now is {weak_topics[0]}, so compare it directly against {topic_label} while reviewing.")

        markdown = "\n".join(
            [
                f"# Explain: {topic_label}",
                "",
                "## Plain-Language Explanation",
                f"In plain language, the uploaded material says this about {topic_label}: {main_line}",
                "",
                "## Grounded Notes",
                *[f"- {line}" for line in (support_lines or [main_line])],
                "",
                "## Why It Matters",
                f"This topic matters because it shows up in course problems where you need to justify a result, interpret a statistic, or decide what conclusion the data supports.",
                "",
                "## What To Review Next",
                *[f"- {note}" for note in review_notes],
            ]
        )
        return StudyResponse(
            command="explain",
            title=f"Explain: {topic_label}",
            markdown=markdown,
            sources=build_source_payload(relevant_chunks),
        )

    def build_quiz(self, topic: str, relevant_chunks: list[DocumentChunk], progress: dict[str, object]) -> StudyResponse:
        topic_label = infer_topic_label(topic, relevant_chunks)
        candidate_sentences = select_ranked_sentences(relevant_chunks, topic_label)
        if not candidate_sentences:
            candidate_sentences = [chunk.text for chunk in relevant_chunks[:3]]

        if not candidate_sentences:
            candidate_sentences = [f"Describe one important idea from {topic_label}."]

        used_terms: set[str] = set()
        questions: list[QuizQuestion] = []
        index = 0
        while len(questions) < 10:
            sentence = candidate_sentences[index % len(candidate_sentences)]
            focus_term = choose_focus_term(sentence, used_terms)
            if focus_term:
                prompt_text = blank_out_term(sentence, focus_term)
                prompt = f"Fill in the blank from the uploaded material: {prompt_text}"
                answer = focus_term
            else:
                prompt = f"In one or two sentences, explain this grounded idea: {textwrap.shorten(sentence, width=150, placeholder='...')}"
                answer = textwrap.shorten(sentence, width=150, placeholder="...")

            questions.append(QuizQuestion(number=len(questions) + 1, prompt=prompt, answer=answer))
            index += 1

        key_terms = select_key_terms(relevant_chunks, limit=5)
        quiz_markdown = "\n".join(
            [
                f"# Daily Quiz: {topic_label}",
                "",
                "## Focus Areas",
                *[f"- {term}" for term in key_terms],
                "",
                "## Questions",
                *[f"{question.number}. {question.prompt}" for question in questions],
                "",
                "Record your score after you finish so the app can track weak topics.",
            ]
        )
        return StudyResponse(
            command="daily quiz",
            title=f"Daily Quiz: {topic_label}",
            markdown=quiz_markdown,
            sources=build_source_payload(relevant_chunks),
            questions=questions,
        )


class StudyEngine:
    def __init__(self) -> None:
        self.provider = MockStudyProvider()

    def run_command(
        self,
        command: str,
        topic: str,
        chunks: list[DocumentChunk],
        progress: dict[str, object] | None = None,
    ) -> StudyResponse:
        normalized_command = command.strip().lower()
        if normalized_command not in {"summary", "explain", "daily quiz"}:
            raise ValueError("Unsupported command. Use summary, explain, or daily quiz.")

        progress_snapshot = progress or {}
        relevant_chunks = retrieve_relevant_chunks(chunks, normalized_command, topic)

        if normalized_command == "summary":
            return self.provider.build_summary(topic, relevant_chunks, progress_snapshot)
        if normalized_command == "explain":
            return self.provider.build_explanation(topic, relevant_chunks, progress_snapshot)
        return self.provider.build_quiz(topic, relevant_chunks, progress_snapshot)
