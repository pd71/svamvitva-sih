import sys
import os

# Ensure backend root directory is at the front of sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.main import app

# Official Vercel Python Serverless handler
handler = app
