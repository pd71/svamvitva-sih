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
            path = scope.get("path", "/")
            headers = dict(scope.get("headers", []))

            for header_name in [b"x-forwarded-uri", b"x-original-url", b"x-rewrite-url", b"x-matched-path"]:
                val = headers.get(header_name, b"").decode("utf-8")
                if val:
                    path = val.split("?")[0]
                    break

            for prefix in ["/api/index.py", "/api/index", "/index.py", "/index"]:
                if path == prefix or path == prefix + "/":
                    path = "/"
                    break
                elif path.startswith(prefix + "/"):
                    path = path[len(prefix):]
                    break

            scope["path"] = path if path else "/"

        await self.app(scope, receive, send)

app = VercelPathFixMiddleware(fastapi_app)
