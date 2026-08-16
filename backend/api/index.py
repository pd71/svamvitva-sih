import sys
import os

# Since Root Directory = "backend" on Vercel, the CWD is already "backend/"
# We insert it so "app.*" imports resolve correctly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
