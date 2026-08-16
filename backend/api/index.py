import sys
import os

# Ensure backend root directory is in Python path for Vercel Serverless execution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

# Set root_path for native FastAPI Vercel serverless prefix stripping
app.root_path = "/api/index.py"
