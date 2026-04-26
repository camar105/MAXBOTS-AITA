@echo off
TITLE StatAI-TA Launcher
SET VENV_DIR=venv

:: 1. Verify/Create Virtual Environment
IF NOT EXIST %VENV_DIR% (
    echo [INFO] Initializing virtual environment...
    python -m venv %VENV_DIR%
)

:: 2. Activate and Install Dependencies
echo [INFO] Syncing libraries...
call %VENV_DIR%\Scripts\activate
pip install -r requirements.txt --quiet

:: 3. Launch the Application
echo [INFO] Running Streamlit...
streamlit run app.py

:: Keep window open if the app crashes
if %errorlevel% neq 0 (
    echo [ERROR] Application failed. Check your requirements.txt or API keys.
    pause
)