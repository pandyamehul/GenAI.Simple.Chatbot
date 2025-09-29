"""
GenAI PDF Chatbot - Application Launcher

This is the main entry point for the GenAI PDF Chatbot application.
The application has been refactored into a modular, maintainable structure.

To run the application:
    streamlit run app.py

Features:
- Modular architecture for easy maintenance
- Support for both FAISS and ChromaDB vector databases
- Persistent storage capabilities
- Enhanced chat interface with conversation history
- Professional authentication system
- Comprehensive error handling
"""

import sys
import os

# Add the parent directory to the Python path to allow absolute imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Use absolute import instead of relative import
from Modular_App.main import main

if __name__ == "__main__":
    main()