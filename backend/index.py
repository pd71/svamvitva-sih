import sys
import os

# Ensure backend root directory is in Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.main import app
from mangum import Mangum

# Vercel Serverless ASGI Handler with lifespan off for instant execution
handler = Mangum(app, lifespan="off")
app = app
