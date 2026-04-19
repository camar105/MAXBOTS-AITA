from pathlib import Path

from src.maxbots_mvp.engine import build_chunks
from src.maxbots_mvp.storage import load_progress, load_session, record_quiz_attempt, save_session, summarize_progress


def test_save_session_and_progress_round_trip(tmp_path: Path):
    runtime_dir = tmp_path / "runtime"
    chunks = build_chunks([("stats.md", "The sample mean stays near the population mean.")])
    save_session(runtime_dir, "session1", [{"name": "stats.md", "characters": 48, "bytes": 48}], chunks)

    session = load_session(runtime_dir, "session1")
    assert session["sessionId"] == "session1"
    assert len(session["chunks"]) == 1

    progress = record_quiz_attempt(runtime_dir, "session1", "sample mean", 7, 10)
    assert progress["attempts"][0]["score"] == 7

    summary = summarize_progress(load_progress(runtime_dir, "session1"))
    assert summary["attemptCount"] == 1
    assert summary["overallPercentage"] == 70.0
    assert summary["weakTopics"] == ["sample mean"]
