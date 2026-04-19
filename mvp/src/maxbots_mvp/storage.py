from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .engine import DocumentChunk


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def session_directory(runtime_dir: Path, session_id: str) -> Path:
    return runtime_dir / "sessions" / session_id


def save_session(
    runtime_dir: Path,
    session_id: str,
    file_records: list[dict[str, Any]],
    chunks: list[DocumentChunk],
) -> None:
    target_dir = session_directory(runtime_dir, session_id)
    target_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "sessionId": session_id,
        "createdAt": utc_now_iso(),
        "files": file_records,
        "chunks": [chunk.to_dict() for chunk in chunks],
    }
    (target_dir / "session.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    progress_file = target_dir / "progress.json"
    if not progress_file.exists():
        progress_file.write_text(json.dumps({"attempts": []}, indent=2), encoding="utf-8")


def load_session(runtime_dir: Path, session_id: str) -> dict[str, Any]:
    session_file = session_directory(runtime_dir, session_id) / "session.json"
    if not session_file.exists():
        raise FileNotFoundError(f"Unknown session: {session_id}")

    raw_payload = json.loads(session_file.read_text(encoding="utf-8"))
    raw_payload["chunks"] = [DocumentChunk.from_dict(item) for item in raw_payload.get("chunks", [])]
    return raw_payload


def load_progress(runtime_dir: Path, session_id: str) -> dict[str, Any]:
    progress_file = session_directory(runtime_dir, session_id) / "progress.json"
    if not progress_file.exists():
        return {"attempts": []}
    return json.loads(progress_file.read_text(encoding="utf-8"))


def record_quiz_attempt(runtime_dir: Path, session_id: str, topic: str, score: int, total: int) -> dict[str, Any]:
    progress = load_progress(runtime_dir, session_id)
    attempts = progress.setdefault("attempts", [])
    attempts.append(
        {
            "recordedAt": utc_now_iso(),
            "topic": topic.strip() or "Uploaded Material",
            "score": int(score),
            "total": int(total),
        }
    )

    progress_file = session_directory(runtime_dir, session_id) / "progress.json"
    progress_file.parent.mkdir(parents=True, exist_ok=True)
    progress_file.write_text(json.dumps(progress, indent=2), encoding="utf-8")
    return progress


def summarize_progress(progress: dict[str, Any]) -> dict[str, Any]:
    attempts = progress.get("attempts", [])
    if not attempts:
        return {
            "attemptCount": 0,
            "overallPercentage": None,
            "topicStats": [],
            "weakTopics": [],
            "lastAttemptAt": None,
        }

    topic_totals: dict[str, dict[str, float]] = {}
    scored_points = 0
    total_points = 0
    for attempt in attempts:
        topic = str(attempt.get("topic", "Uploaded Material")).strip() or "Uploaded Material"
        score = int(attempt.get("score", 0))
        total = max(int(attempt.get("total", 0)), 1)
        scored_points += score
        total_points += total
        bucket = topic_totals.setdefault(topic, {"score": 0.0, "total": 0.0, "attempts": 0.0})
        bucket["score"] += score
        bucket["total"] += total
        bucket["attempts"] += 1

    topic_stats = []
    for topic, values in topic_totals.items():
        percentage = round((values["score"] / values["total"]) * 100, 1) if values["total"] else 0.0
        topic_stats.append(
            {
                "topic": topic,
                "averagePercentage": percentage,
                "attempts": int(values["attempts"]),
            }
        )

    topic_stats.sort(key=lambda item: (item["averagePercentage"], item["topic"]))
    return {
        "attemptCount": len(attempts),
        "overallPercentage": round((scored_points / total_points) * 100, 1) if total_points else None,
        "topicStats": topic_stats,
        "weakTopics": [item["topic"] for item in topic_stats[:3]],
        "lastAttemptAt": attempts[-1].get("recordedAt"),
    }
