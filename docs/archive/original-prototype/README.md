Report: https://docs.google.com/document/d/1N05pGLe9K3O4Grm0YjHb96laR-BohjM3JuOpYaG0Mvc/edit?tab=t.0#heading=h.gjdgxs

# Study Tool Summarizer

This is a Python sample project you can include in your GitHub report. It lets a user upload:

- a text file such as `.txt` or `.md`
- a textbook image such as `.png`, `.jpg`, or `.jpeg`

The app then generates a study guide with:

- key points
- important formulas
- real uses of the concept
- common mistakes
- problem-solving tips
- a quick recap

## How it works

The Flask server uses the OpenAI Responses API:

- text files are read directly and sent as text input
- images are uploaded with the Files API and analyzed as vision input
- the user chooses `short`, `medium`, or `long` summary length

## Files

- `app.py` - Flask server and OpenAI API calls
- `templates/index.html` - upload form
- `static/app.js` - browser logic
- `static/styles.css` - simple UI styling
- `requirements.txt` - Python dependencies

## Setup

1. Install Python 3.
2. Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file based on `.env.example`.
5. Add your OpenAI API key:

```env
OPENAI_API_KEY=your_api_key_here
PORT=3000
```

6. Start the app:

```bash
python app.py
```

7. Open `http://localhost:3000`

## Example project description

You can describe this in your report like this:

> I created a Python study assistant web app that accepts either typed study material or textbook images. The system uses an AI model to summarize the material based on a user-selected output length and automatically organizes the response into key points, formulas, applications, common mistakes, and problem-solving advice. This makes the tool useful for quick review before quizzes or exams.

## Notes

- I could not run it fully in this workspace because Python is not installed here.
- For scanned images, clearer photos usually produce better notes.
- Very large text files may need chunking in a future version.
