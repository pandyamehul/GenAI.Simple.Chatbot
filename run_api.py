#!/usr/bin/env python3
"""
GenAI Enterprise Document Intelligence Platform - API Server Runner

This script properly sets up the Python path and runs the FastAPI server
with the correct module structure, avoiding relative import issues.

Usage:
    python run_api.py

Alternative usage with uvicorn:
    uvicorn Modular_App.api:app --reload --host 0.0.0.0 --port 8000
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

if __name__ == "__main__":
    # Import the FastAPI app
    from Modular_App.api import app
    
    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )