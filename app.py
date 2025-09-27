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

from main import main

if __name__ == "__main__":
    main()