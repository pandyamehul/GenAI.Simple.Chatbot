#!/usr/bin/env python3
"""
GenAI Enterprise Document Intelligence Platform - Application Runner

This script properly sets up the Python path and runs the Streamlit application
with the correct module structure, avoiding relative import issues.

Usage:
    python run_app.py

Alternative usage:
    streamlit run run_app.py
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

# Import and run the main application
if __name__ == "__main__":
    from Modular_App.main import main
    main()