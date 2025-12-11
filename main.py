#!/usr/bin/env python3
"""
Main entry point for MultiDoc-IntelliAgent
"""

import sys
import subprocess
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

if __name__ == "__main__":
    # Check for critical environment variables
    if not os.getenv("PERPLEXITY_API_KEY"):
        print("⚠️  WARNING: PERPLEXITY_API_KEY is not set. The LLM features will not work.")
        print("   Please create a .env file with your API key.")

    if len(sys.argv) > 1 and sys.argv[1] == "ui":
        print("Launching Streamlit UI...")
        # Use sys.executable to ensure we're using the interpreter from the correct environment
        # Running as a module helps Python resolve the paths correctly.
        subprocess.run([sys.executable, "-m", "streamlit", "run", "src/ui/app.py"])
    else:
        script_name = "main.py" if "main.py" in sys.argv[0] else "app.py"

        print("Invalid command. To run the UI, use:")
        print(f"python {script_name} ui")
        print("Or directly:")
        print("streamlit run src/ui/app.py")