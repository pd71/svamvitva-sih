import sys
import os

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.main import app

# Export app for Vercel ASGI serverless handler
app = app
