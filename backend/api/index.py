import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app as fastapi_app

class VercelPathFixMiddleware:
    """
    Middleware to fix Vercel rewrite pathing for FastAPI.
    When Vercel rewrites requests to /api/index, it sets scope['path'] = '/api/index'.
    This middleware restores the original requested path from Vercel headers (x-forwarded-uri or x-matched-path).
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            
            # Check headers for original requested path
            forwarded_uri = headers.get(b"x-forwarded-uri", b"").decode("utf-8")
            matched_path  = headers.get(b"x-matched-path", b"").decode("utf-8")
            original_url  = headers.get(b"x-original-url", b"").decode("utf-8")

            orig = forwarded_uri or original_url or matched_path
            if orig and orig != "/api/index" and orig != "/api/index.py":
                scope["path"] = orig.split("?")[0]
            elif scope.get("path") in ["/api/index", "/api/index.py", "/api"]:
                scope["path"] = "/"

        await self.app(scope, receive, send)

app = VercelPathFixMiddleware(fastapi_app)
