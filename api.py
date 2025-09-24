from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import asyncio
import os
from typing import Dict, Any
import uuid
import io
import pickle
import tempfile
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import your existing agent and query analyzer logic
from src.agent import get_agent
from src.query_analyzer import analyze_query

app = FastAPI(title="Data Scientist AI Agent API", version="1.0.0")

# Add CORS middleware to allow requests from Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Streamlit app's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Persistent session storage
SESSION_STORAGE_DIR = Path("session_storage")
SESSION_STORAGE_DIR.mkdir(exist_ok=True)

@app.on_event("startup")
async def startup_event():
    """Verify API key is loaded on startup and load existing sessions."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        print("✅ Google API key loaded successfully")
    else:
        print("❌ Warning: GOOGLE_API_KEY not found in environment variables")
    
    # Load existing sessions from disk
    session_files = list(SESSION_STORAGE_DIR.glob("*.pkl"))
    if session_files:
        print(f"🔄 Found {len(session_files)} existing sessions on disk")
        for session_file in session_files:
            session_id = session_file.stem
            df = load_session_from_disk(session_id)
            if df is not None:
                DF_STORAGE[session_id] = df
                print(f"📂 Loaded session {session_id} with shape {df.shape}")
    else:
        print("📂 No existing sessions found on disk")

# In-memory cache for active sessions (for performance)
DF_STORAGE: Dict[str, pd.DataFrame] = {}

def save_session_to_disk(session_id: str, df: pd.DataFrame):
    """Save session data to disk for persistence."""
    try:
        session_file = SESSION_STORAGE_DIR / f"{session_id}.pkl"
        with open(session_file, 'wb') as f:
            pickle.dump(df, f)
        print(f"💾 Session {session_id} saved to disk")
    except Exception as e:
        print(f"❌ Failed to save session {session_id} to disk: {e}")

def load_session_from_disk(session_id: str) -> pd.DataFrame:
    """Load session data from disk."""
    try:
        session_file = SESSION_STORAGE_DIR / f"{session_id}.pkl"
        if session_file.exists():
            with open(session_file, 'rb') as f:
                df = pickle.load(f)
            print(f"📂 Session {session_id} loaded from disk")
            return df
    except Exception as e:
        print(f"❌ Failed to load session {session_id} from disk: {e}")
    return None

def delete_session_from_disk(session_id: str):
    """Delete session data from disk."""
    try:
        session_file = SESSION_STORAGE_DIR / f"{session_id}.pkl"
        if session_file.exists():
            session_file.unlink()
            print(f"🗑️ Session {session_id} deleted from disk")
    except Exception as e:
        print(f"❌ Failed to delete session {session_id} from disk: {e}")

def get_or_load_session(session_id: str) -> pd.DataFrame:
    """Get session from memory cache or load from disk."""
    if session_id in DF_STORAGE:
        return DF_STORAGE[session_id]
    
    # Try to load from disk
    df = load_session_from_disk(session_id)
    if df is not None:
        DF_STORAGE[session_id] = df
        return df
    
    return None

class QueryRequest(BaseModel):
    query: str
    session_id: str

class QueryAnalysisRequest(BaseModel):
    query: str

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Data Scientist AI Agent API is running!", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "active_sessions": len(DF_STORAGE)}

@app.get("/debug/sessions")
async def debug_sessions():
    """Debug endpoint to see active sessions."""
    return {"active_sessions": list(DF_STORAGE.keys()), "count": len(DF_STORAGE)}

@app.post("/upload/")
async def upload_data(session_id: str, file: UploadFile = File(...)):
    """Handles uploading a data file and loading it into a DataFrame."""
    print(f"📁 Upload request for session: {session_id}")
    
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV or Excel file.")

    try:
        # Read the file content
        file_content = await file.read()
        
        # Read the file into a pandas DataFrame
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(file_content))
        else:
            df = pd.read_excel(io.BytesIO(file_content))

        # Store the DataFrame in our in-memory storage
        DF_STORAGE[session_id] = df
        
        # Save to disk for persistence
        save_session_to_disk(session_id, df)
        
        print(f"✅ File uploaded successfully for session: {session_id}, shape: {df.shape}")
        print(f"📊 Active sessions: {list(DF_STORAGE.keys())}")

        # Categorize columns for better UX
        numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        categorical_columns = df.select_dtypes(include=['object']).columns.tolist()
        datetime_columns = df.select_dtypes(include=['datetime64[ns]']).columns.tolist()
        
        return {
            "status": "success", 
            "filename": file.filename, 
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "numeric_columns": numeric_columns,
            "categorical_columns": categorical_columns,
            "datetime_columns": datetime_columns
        }
    except Exception as e:
        print(f"❌ Upload failed for session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")

@app.post("/analyze_query/")
async def analyze_user_query(request: QueryAnalysisRequest):
    """Analyzes a user query to determine its intent."""
    try:
        analysis = await analyze_query(request.query)
        return {
            "intent": analysis.intent,
            "confidence": analysis.confidence
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze query: {str(e)}")

@app.post("/process_query/")
async def process_agent_query(request: QueryRequest):
    """Processes a query using the main data scientist agent."""
    print(f"🔍 Process query request for session: {request.session_id}")
    print(f"📊 Available sessions in memory: {list(DF_STORAGE.keys())}")
    
    # Try to get session from memory or disk
    df = get_or_load_session(request.session_id)
    
    if df is None:
        print(f"❌ Session {request.session_id} not found in storage or disk")
        raise HTTPException(status_code=404, detail="No data found for this session. Please upload a file first.")

    try:
        print(f"✅ Processing query for session {request.session_id} with data shape: {df.shape}")
        agent = get_agent(df)
        result = await agent.process_query(request.query)

        # Convert Plotly figures to JSON for client display
        if result.get("chart_figure"):
            chart_figure = result.pop("chart_figure")
            # Convert Plotly figure to JSON (much smaller than HTML)
            chart_json = chart_figure.to_json()
            result["visualization_json"] = chart_json
            result["visualization_generated"] = True
        else:
            result["visualization_generated"] = False
            result["visualization_json"] = None

        return result
    except Exception as e:
        print(f"❌ Query processing failed for session {request.session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process query: {str(e)}")

@app.get("/session/{session_id}/data_info")
async def get_data_info(session_id: str):
    """Get information about the uploaded data for a session."""
    df = get_or_load_session(session_id)
    if df is None:
        raise HTTPException(status_code=404, detail="No data found for this session.")
    
    return {
        "shape": df.shape,
        "columns": df.columns.tolist(),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "numeric_columns": df.select_dtypes(include=['number']).columns.tolist(),
        "categorical_columns": df.select_dtypes(include=['object', 'category']).columns.tolist(),
        "datetime_columns": df.select_dtypes(include=['datetime64']).columns.tolist()
    }

@app.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Clear data for a specific session."""
    # Remove from memory cache
    if session_id in DF_STORAGE:
        del DF_STORAGE[session_id]
    
    # Remove from disk
    delete_session_from_disk(session_id)
    
    return {"status": "success", "message": f"Session {session_id} cleared"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
