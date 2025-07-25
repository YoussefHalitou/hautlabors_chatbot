#!/usr/bin/env python3
"""
Launch script for the Haut Labor Oldenburg Streamlit AI Consultant
This script starts the Streamlit app for the clinic AI assistant.
"""

import subprocess
import sys
import os

def run_streamlit():
    """Run the Streamlit app"""
    # Change to the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Run streamlit with the UI file
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_ui.py",
            "--server.headless", "false",
            "--server.port", "8501"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nStreamlit app stopped by user")
        sys.exit(0)

if __name__ == "__main__":
    print("🏥 Starting Haut Labor Oldenburg AI Consultant...")
    print("🌐 The app will open in your browser at http://localhost:8501")
    print("Press Ctrl+C to stop the app")
    print("-" * 50)
    run_streamlit()
