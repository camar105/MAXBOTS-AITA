import io
from pathlib import Path

from app import app


def test_upload_then_run_command(tmp_path: Path):
    app.config["TESTING"] = True
    client = app.test_client()

    sample = b"The central limit theorem says the distribution of sample means approaches a normal shape as sample size grows."
    upload = client.post(
        "/api/upload",
        data={"sources": (io.BytesIO(sample), "lecture.md")},
        content_type="multipart/form-data",
    )

    assert upload.status_code == 200
    session_id = upload.get_json()["sessionId"]

    command = client.post(
        "/api/command",
        json={
            "sessionId": session_id,
            "command": "summary",
            "topic": "central limit theorem",
        },
    )

    assert command.status_code == 200
    payload = command.get_json()
    assert payload["title"] == "Summary: central limit theorem"
    assert payload["sources"]
