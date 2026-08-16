import sys
import os

# Ensure backend root directory is in Python path for Vercel Serverless execution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app as fastapi_app

class VercelRouteMiddleware:
    """
    Strips Vercel serverless function entrypoint prefixes from scope['path']
    so all incoming routes (/, /docs, /api/...) match their exact FastAPI handlers.
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            path = scope.get("path", "/")
            for prefix in ["/api/main.py", "/api/main", "/api/index.py", "/api/index"]:
                if path.startswith(prefix):
                    path = path[len(prefix):]
                    break
            scope["path"] = path if path else "/"
        await self.app(scope, receive, send)

app = VercelRouteMiddleware(fastapi_app)
