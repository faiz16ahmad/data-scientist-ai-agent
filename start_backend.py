#!/usr/bin/env python3
"""
Startup script for the FastAPI backend server.
Run this script to start the Data Scientist AI Agent API server.
"""

import uvicorn
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("🚀 Starting Data Scientist AI Agent API Server...")
    print("📍 Server will be available at: http://127.0.0.1:8000")
    print("📚 API documentation at: http://127.0.0.1:8000/docs")
    print("🔄 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    uvicorn.run(
        "api:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
