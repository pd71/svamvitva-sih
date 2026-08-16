import sys
import os

# Ensure backend root directory is in Python path for Vercel Serverless execution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app as fastapi_app

class VercelPrefixFixMiddleware:
    """
    Strips Vercel function route prefixes (/api/index.py, /api/index) from both scope['path'] and scope['raw_path']
    so all incoming request paths match their exact FastAPI handlers.
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            path = scope.get("path", "/")
            prefixes = ["/api/index.py", "/api/index", "/api"]
            for prefix in prefixes:
                if path == prefix or path == prefix + "/":
                    path = "/"
                    break
                elif path.startswith(prefix + "/"):
                    path = path[len(prefix):]
                    break
            path = path if path else "/"
            scope["path"] = path
            scope["raw_path"] = path.encode("utf-8")
        await self.app(scope, receive, send)

app = VercelPrefixFixMiddleware(fastapi_app)
