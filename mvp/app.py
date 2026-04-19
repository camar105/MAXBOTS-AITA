from __future__ import annotations

import os
import uuid
from pathlib import Path

from flask import Flask, jsonify, render_template, request
from werkzeug.utils import secure_filename

from src.maxbots_mvp.engine import StudyEngine, build_chunks, extract_text_from_bytes
from src.maxbots_mvp.storage import load_progress, load_session, record_quiz_attempt, save_session, summarize_progress


BASE_DIR = Path(__file__).resolve().parent
RUNTIME_DIR = BASE_DIR / "data" / "runtime"
ENGINE = StudyEngine()


app = Flask(__name__)


@app.get("/")
def index() -> str:
    return render_template("index.html")


@app.get("/api/health")
def health() -> object:
    return jsonify({"status": "ok", "provider": "mock"})


@app.post("/api/upload")
def upload_materials() -> object:
    uploaded_files = request.files.getlist("sources")
    valid_files = [item for item in uploaded_files if item and item.filename]
    if not valid_files:
        return jsonify({"error": "Upload at least one PDF or text file to start a study session."}), 400

    documents: list[tuple[str, str]] = []
    file_records: list[dict[str, object]] = []

    try:
        for uploaded_file in valid_files:
            safe_name = secure_filename(uploaded_file.filename) or Path(uploaded_file.filename).name
            raw_bytes = uploaded_file.read()
            extracted_text = extract_text_from_bytes(safe_name, raw_bytes)
            documents.append((safe_name, extracted_text))
            file_records.append(
                {
                    "name": safe_name,
                    "characters": len(extracted_text),
                    "bytes": len(raw_bytes),
                }
            )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": f"Could not process the uploaded files. Server error: {exc}"}), 500

    chunks = build_chunks(documents)
    if not chunks:
        return jsonify({"error": "The uploaded files did not contain enough readable text to build a study session."}), 400

    session_id = uuid.uuid4().hex[:12]
    save_session(RUNTIME_DIR, session_id, file_records, chunks)

    return jsonify(
        {
            "sessionId": session_id,
            "fileCount": len(file_records),
            "chunkCount": len(chunks),
            "files": file_records,
            "progress": summarize_progress(load_progress(RUNTIME_DIR, session_id)),
        }
    )


@app.post("/api/command")
def run_command() -> object:
    payload = request.get_json(silent=True) or {}
    session_id = str(payload.get("sessionId", "")).strip()
    command = str(payload.get("command", "")).strip().lower()
    topic = str(payload.get("topic", "")).strip()

    if not session_id:
        return jsonify({"error": "Start by uploading course material first."}), 400
    if command not in {"summary", "explain", "daily quiz"}:
        return jsonify({"error": "Choose summary, explain, or daily quiz."}), 400

    try:
        session = load_session(RUNTIME_DIR, session_id)
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 404

    progress = load_progress(RUNTIME_DIR, session_id)
    progress_summary = summarize_progress(progress)

    try:
        response = ENGINE.run_command(command, topic, session["chunks"], progress_summary)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": f"The command could not be completed. Server error: {exc}"}), 500

    payload = response.to_dict()
    payload["progress"] = progress_summary
    return jsonify(payload)


@app.post("/api/progress")
def save_progress() -> object:
    payload = request.get_json(silent=True) or {}
    session_id = str(payload.get("sessionId", "")).strip()
    topic = str(payload.get("topic", "")).strip() or "Uploaded Material"
    score = payload.get("score")
    total = payload.get("total", 10)

    if not session_id:
        return jsonify({"error": "Missing session id."}), 400
    if score is None:
        return jsonify({"error": "Provide a quiz score before saving progress."}), 400

    try:
        numeric_score = int(score)
        numeric_total = int(total)
    except (TypeError, ValueError):
        return jsonify({"error": "Score and total must be numbers."}), 400

    if numeric_total <= 0 or numeric_score < 0 or numeric_score > numeric_total:
        return jsonify({"error": "Score must be between 0 and the quiz total."}), 400

    try:
        updated_progress = record_quiz_attempt(RUNTIME_DIR, session_id, topic, numeric_score, numeric_total)
    except Exception as exc:
        return jsonify({"error": f"Could not save progress. Server error: {exc}"}), 500

    return jsonify({"progress": summarize_progress(updated_progress)})


@app.get("/api/progress/<session_id>")
def get_progress(session_id: str) -> object:
    try:
        progress = load_progress(RUNTIME_DIR, session_id)
    except Exception as exc:
        return jsonify({"error": f"Could not load progress. Server error: {exc}"}), 500
    return jsonify({"progress": summarize_progress(progress)})


if __name__ == "__main__":
    port = int(os.getenv("PORT", "3000"))
    app.run(host="0.0.0.0", port=port, debug=True)
