import sys
import os
from mangum import Mangum

# Ensure backend root directory is in Python path for Vercel Serverless execution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app as fastapi_app

handler = Mangum(fastapi_app, lifespan="off")
app = fastapi_app
