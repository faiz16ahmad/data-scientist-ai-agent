# 🔧 Setup Guide for AI Agent Testing Suite

## Prerequisites

Before running the testing suite, you need to set up your Google Generative AI API key.

## 🔑 Google API Key Setup

### Step 1: Get Your API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy your API key

### Step 2: Set Environment Variable

#### Option A: Using .env file (Recommended)

1. Create a `.env` file in your project root:
```bash
touch .env
```

2. Add your API key to the `.env` file:
```
GOOGLE_API_KEY=your_api_key_here
```

#### Option B: Set Environment Variable Directly

**Windows PowerShell:**
```powershell
$env:GOOGLE_API_KEY="your_api_key_here"
```

**Windows Command Prompt:**
```cmd
set GOOGLE_API_KEY=your_api_key_here
```

**Linux/Mac:**
```bash
export GOOGLE_API_KEY="your_api_key_here"
```

### Step 3: Verify Setup

Run this Python code to verify your setup:

```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if api_key:
    print("✅ API key found!")
    print(f"Key starts with: {api_key[:10]}...")
else:
    print("❌ API key not found. Please set GOOGLE_API_KEY environment variable.")
```

## 🚀 Running Tests

Once your API key is set up:

### Quick Test (10 questions)
```bash
python run_tests.py
```
Then select option 1.

### Full Test Suite (50 questions)
```bash
python run_tests.py
```
Then select option 2.

### Streamlit Interface
```bash
streamlit run src/testing/test_app.py
```

## 🔧 Troubleshooting

### Common Issues

1. **"DefaultCredentialsError"**
   - Cause: API key not set or not found
   - Solution: Follow the API key setup steps above

2. **"ModuleNotFoundError"**
   - Cause: Missing dependencies
   - Solution: `pip install -r requirements.txt`

3. **"FileNotFoundError: sample_sales.csv"**
   - Cause: Dataset file missing
   - Solution: Ensure your CSV file exists or update the path in `run_tests.py`

4. **Rate limiting errors**
   - Cause: Too many API requests
   - Solution: Reduce concurrent tests or add delays

### Verification Commands

Check if everything is working:

```bash
# Check if virtual environment is activated
where python

# Check if packages are installed
pip list | findstr streamlit
pip list | findstr langchain

# Check if API key is accessible
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API Key found!' if os.getenv('GOOGLE_API_KEY') else 'API Key missing!')"
```

## 📞 Need Help?

If you're still having issues:

1. Check that your `.env` file is in the project root
2. Restart your terminal/command prompt after setting environment variables
3. Verify your API key is valid at [Google AI Studio](https://makersuite.google.com/)
4. Ensure you're in the correct virtual environment

## 🎯 Quick Start Checklist

- [ ] Get Google API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- [ ] Create `.env` file with `GOOGLE_API_KEY=your_key`
- [ ] Activate virtual environment: `venv\Scripts\activate`
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Run quick test: `python run_tests.py`
- [ ] Success! 🎉

---

**Ready to test your AI agent!** 🧪🤖
