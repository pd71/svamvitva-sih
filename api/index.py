import sys
import os

# Add backend directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.main import app

# Vercel serverless handler entrypoint
handler = app
