# User Testing Notes


I reviewed the repository from a non-technical user perspective. I  focused on understanding the app, testing the setup instructions, checking whether the project is easy to navigate, and identifying areas that may need revision.

## What I Reviewed

- Main repository structure
- MVP folder
- README instructions
- Study engine code
- Supported file types
- Summary, explain, and daily quiz features

## What the Project Does

This project is a study assistant for statistics students. It allows a user to upload class materials and then generate a summary, explanation, or quiz based on the uploaded content.

## Things That Look Good

- The project has a clear educational purpose.
- The MVP is separated into its own folder.
- The code is organized into sections for document parsing, chunking, retrieval, and quiz generation.
- The app can run without needing a paid AI API.
- The quiz feature includes an answer key.

## Things That May Need Revision

- The repository has both old root-level files and the newer MVP folder, which may confuse new users.
- There are two README files, so it is not immediately clear which one is current.
- The app may not work well with scanned PDFs because it does not appear to use OCR.
- The quiz questions are basic fill-in-the-blank questions and may need improvement.
- More screenshots or a demo video would make the project easier to understand.

## Suggested Improvements

1. Add a clear “Start Here” section to the main README.
2. Label old files as archived or remove them if they are no longer used.
3. Add screenshots of the app.
4. Add a simple demo walkthrough.
5. Improve quiz question generation in a future version.
6. Add support for scanned PDFs if possible.

## Testing Notes

I reviewed the intended app path:

`mvp → src → maxbots_mvp → engine.py`

This file appears to contain the main study-assistant logic for parsing uploads, finding relevant text, and generating summaries, explanations, and quizzes.
