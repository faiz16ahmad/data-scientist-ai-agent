#!/bin/bash
echo "🚀 Starting Data Scientist AI Agent in virtual environment..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.py first."
    echo "Run: python setup.py"
    exit 1
fi

# Activate virtual environment and run the app
source venv/bin/activate
echo "✅ Virtual environment activated"
echo "🌐 Starting Streamlit application..."
python -m streamlit run src/app.py
