import sys
import os

# Add backend root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app

# Export app for Vercel Serverless Function
app = app
