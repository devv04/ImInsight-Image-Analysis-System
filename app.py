import os
import sys

# Add backend directory to Python path so it can import its modules correctly
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from backend.app import app

if __name__ == "__main__":
    # Hugging Face Spaces (Gradio SDK) routes traffic to port 7860
    app.run(host="0.0.0.0", port=7860)
