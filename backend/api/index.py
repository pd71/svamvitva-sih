import sys
import os

# Ensure backend root directory is in Python path for Vercel Serverless execution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app as fastapi_app

class VercelPathFixMiddleware:
    """
    Middleware to fix Vercel rewrite pathing for FastAPI.
    When Vercel rewrites requests to /api/index, it passes /api/index as scope['path'].
    This middleware restores the original requested path from Vercel headers or strips /api/index prefix.
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            orig_path = (
                headers.get(b"x-matched-path", b"") or
                headers.get(b"x-forwarded-uri", b"") or
                headers.get(b"x-original-url", b"") or
                headers.get(b"x-rewrite-url", b"")
            ).decode("utf-8")

            if orig_path:
                orig_path = orig_path.split("?")[0]
                scope["path"] = orig_path
            elif scope["path"].startswith("/api/index"):
                sub = scope["path"][len("/api/index"):]
                scope["path"] = sub if sub else "/"

        await self.app(scope, receive, send)

app = VercelPathFixMiddleware(fastapi_app)
