# Data Scientist AI Agent

A conversational AI agent for data analysis built with Streamlit, FastAPI, and LangChain. This application allows users to upload CSV/Excel files and interact with an AI agent that can analyze data, generate insights, and create visualizations.

## 🚀 Quick Start

### Method 1: Automated Setup (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd windsurf-project
   ```

2. **Run the setup script**
   ```bash
   python start_backend.py
   ```
   This will automatically:
   - Install all dependencies
   - Start the FastAPI backend
   - Launch the Streamlit frontend

3. **Access the application**
   - Streamlit UI: http://localhost:8501
   - FastAPI Backend: http://localhost:8000

### Method 2: Manual Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Google API key**
   - Follow instructions in `SETUP_GUIDE.md`
   - Add your Google API key to the environment

3. **Start the backend**
   ```bash
   uvicorn api:app --reload --host 127.0.0.1 --port 8000
   ```

4. **Start the frontend**
   ```bash
   streamlit run src/app.py
   ```

## 📊 Key Features

- **Interactive Data Analysis**: Upload CSV/Excel files and ask questions about your data
- **AI-Powered Insights**: Uses Google Gemini for intelligent data analysis
- **Automated Visualizations**: Generates charts and graphs based on your queries
- **Session Management**: Maintains conversation context across queries
- **Comprehensive Testing**: 50-question automated test suite for reliability

## 🏗️ Project Structure

```
windsurf-project/
├── src/                    # Python Backend
│   ├── app.py             # Streamlit frontend
│   ├── agent.py           # LangChain AI agent
│   ├── utils.py           # Utility functions
│   └── query_analyzer/    # Query analysis logic
├── api.py                 # FastAPI backend server
├── requirements.txt       # Python dependencies
├── start_backend.py       # Automated setup script
├── run_tests.py           # Test runner
├── sample_sales.csv      # Sample dataset
└── README.md             # This file
```

## 🧪 Testing

Run the comprehensive test suite:
```bash
python run_tests.py
```

This will test 50 different scenarios including:
- Data upload and processing
- Statistical analysis
- Visualization generation
- Error handling

## 📈 Sample Data

The project includes sample datasets:
- `sample_sales.csv`: E-commerce sales data
- `advanced_customer_behavior.csv`: Customer behavior analytics

## 🔧 Configuration

### Environment Variables
- `GOOGLE_API_KEY`: Your Google Gemini API key (required)

### API Endpoints
- `POST /upload/`: Upload CSV/Excel files
- `POST /process_query/`: Process data analysis queries
- `GET /health`: Health check endpoint

## 🚀 Deployment

### Local Development
```bash
# Terminal 1: Backend
uvicorn api:app --reload --host 127.0.0.1 --port 8000

# Terminal 2: Frontend
streamlit run src/app.py
```

### Production
```bash
# Start backend
uvicorn api:app --host 0.0.0.0 --port 8000

# Start frontend
streamlit run src/app.py --server.port 8501
```

## 📚 Documentation

- `SETUP_GUIDE.md`: Detailed setup instructions
- `TESTING_README.md`: Testing documentation
- `requirements.txt`: Python dependencies

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run the test suite
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

If you encounter any issues:
1. Check the `SETUP_GUIDE.md` for setup instructions
2. Run the test suite to verify functionality
3. Check the console logs for error messages
4. Ensure your Google API key is properly configured

---

**Ready to analyze your data?** Upload a CSV file and start asking questions! 🚀📊