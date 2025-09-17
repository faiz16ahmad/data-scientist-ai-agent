@echo off
echo 🚀 Starting Data Scientist AI Agent in virtual environment...

REM Check if virtual environment exists
if not exist "venv" (
    echo ❌ Virtual environment not found. Please run setup.py first.
    echo Run: python setup.py
    pause
    exit /b 1
)

REM Activate virtual environment and run the app
call venv\Scripts\activate
echo ✅ Virtual environment activated
echo 🌐 Starting Streamlit application...
python -m streamlit run src/app.py

pause
