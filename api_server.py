"""
FastAPI Server Launcher - GenAI Enterprise Document Intelligence Platform
Run this file to start the REST API server independently.
"""
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import the FastAPI app from the Modular_App package
from Modular_App.api import app

if __name__ == "__main__":
    import uvicorn
    
    # Start the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[project_root]
    )