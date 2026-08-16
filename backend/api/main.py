import sys
import os
from urllib.parse import parse_qs

# Ensure backend root directory is in Python path for Vercel Serverless execution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app as fastapi_app

class VercelRouteMiddleware:
    """
    Strips Vercel serverless function entrypoint prefixes from scope['path']
    and extracts original requested route from __url parameter.
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            qs = scope.get("query_string", b"").decode("utf-8")
            parsed = parse_qs(qs)
            if "__url" in parsed and parsed["__url"]:
                real_path = parsed["__url"][0]
                if not real_path.startswith("/"):
                    real_path = "/" + real_path
                scope["path"] = real_path.split("?")[0]
            else:
                path = scope.get("path", "/")
                for prefix in ["/api/main.py", "/api/main", "/api/index.py", "/api/index"]:
                    if path.startswith(prefix):
                        path = path[len(prefix):]
                        break
                scope["path"] = path if path else "/"
        await self.app(scope, receive, send)

app = VercelRouteMiddleware(fastapi_app)
