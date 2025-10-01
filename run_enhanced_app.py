"""
Enhanced Application Runner
Runs the GenAI Enhanced Chatbot with source attribution and collaborative features.
"""

import sys
import os

# Add the current directory to Python path for proper imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import and run the enhanced application
from enhanced_main import main

if __name__ == "__main__":
    print("🚀 Starting GenAI Enhanced Chatbot v3.0...")
    print("📍 Features: Source Attribution + Real-time Collaboration")
    print("🌐 Access at: http://localhost:8501")
    print("-" * 50)
    
    main()
