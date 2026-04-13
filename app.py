import os
import tempfile
from pathlib import Path

from flask import Flask, jsonify, render_template, request
from openai import OpenAI


app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

TEXT_EXTENSIONS = {".txt", ".md", ".csv", ".log"}


def get_length_instruction(length: str) -> str:
    instructions = {
        "short": "Keep the response concise and easy to review in about 5 to 8 bullet points total where appropriate.",
        "medium": "Give a balanced response with enough detail to study from without becoming a full chapter rewrite.",
        "long": "Give a detailed study guide with richer explanations, but keep it practical and organized.",
    }
    return instructions.get(length, instructions["medium"])


def build_study_prompt(summary_length: str) -> str:
    return f"""
You are an academic study assistant.
{get_length_instruction(summary_length)}

Analyze the provided material and return a Markdown study guide with exactly these sections:
1. Topic Overview
2. Key Points
3. Important Formulas
4. What These Ideas Apply To
5. Common Mistakes
6. Problem-Solving Tips
7. Quick Recap

Rules:
- If formulas are present or strongly implied, write them clearly and define variables.
- If no formulas are visible, say "No explicit formula provided" and infer only when reasonable.
- Focus on helping a student review and solve problems.
- For image inputs, read the text in the image first, then interpret the concepts.
- Do not invent textbook page numbers or citations.
- Keep the language student-friendly and direct.
""".strip()


def is_text_file(filename: str, content_type: str) -> bool:
    extension = Path(filename).suffix.lower()
    return content_type.startswith("text/") or extension in TEXT_EXTENSIONS


def is_image_file(content_type: str) -> bool:
    return content_type.startswith("image/")


def summarize_text_file(uploaded_file, summary_length: str) -> str:
    text = uploaded_file.read().decode("utf-8", errors="ignore")

    response = client.responses.create(
        model=MODEL_NAME,
        input=[
            {
                "role": "system",
                "content": [{"type": "input_text", "text": build_study_prompt(summary_length)}],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": f'Study material from uploaded file "{uploaded_file.filename}":\n\n{text}',
                    }
                ],
            },
        ],
    )

    return response.output_text


def summarize_image_file(uploaded_file, summary_length: str) -> str:
    suffix = Path(uploaded_file.filename).suffix or ".png"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        uploaded_file.save(temp_file.name)
        temp_path = temp_file.name

    try:
        with open(temp_path, "rb") as image_file:
            uploaded = client.files.create(file=image_file, purpose="vision")

        response = client.responses.create(
            model=MODEL_NAME,
            input=[
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": build_study_prompt(summary_length)}],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "Read this textbook image and turn it into a study guide.",
                        },
                        {
                            "type": "input_image",
                            "file_id": uploaded.id,
                            "detail": "high",
                        },
                    ],
                },
            ],
        )

        return response.output_text
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/study-notes")
def study_notes():
    try:
        if not os.getenv("OPENAI_API_KEY"):
            return jsonify(
                {"error": "Missing OPENAI_API_KEY. Add it to your environment before running the app."}
            ), 500

        uploaded_file = request.files.get("source")
        summary_length = request.form.get("summaryLength", "medium")

        if not uploaded_file or not uploaded_file.filename:
            return jsonify({"error": "Please upload a text file or image."}), 400

        if is_text_file(uploaded_file.filename, uploaded_file.mimetype):
            result = summarize_text_file(uploaded_file, summary_length)
        elif is_image_file(uploaded_file.mimetype):
            result = summarize_image_file(uploaded_file, summary_length)
        else:
            return jsonify(
                {
                    "error": "Unsupported file type. Use a text file like .txt/.md or an image such as .png/.jpg."
                }
            ), 400

        return jsonify({"result": (result or "No summary was generated.").strip()})
    except Exception as exc:
        print(exc)
        return jsonify(
            {
                "error": f"The study guide could not be generated. Server error: {exc}"
            }
        ), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", "3000"))
    app.run(host="0.0.0.0", port=port, debug=True)
