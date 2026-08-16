import sys
import os
from urllib.parse import parse_qs

# Ensure backend root directory is in Python path for Vercel Serverless execution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app as fastapi_app

class VercelPathFixMiddleware:
    """
    Middleware to fix Vercel rewrite pathing for FastAPI.
    When vercel.json rewrites /(.*) to /api/index?__path=/$1,
    this middleware extracts __path and sets scope['path'] to the exact original requested route.
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            query_string = scope.get("query_string", b"").decode("utf-8")
            parsed_qs = parse_qs(query_string)

            if "__path" in parsed_qs and parsed_qs["__path"]:
                target_path = parsed_qs["__path"][0]
                if not target_path.startswith("/"):
                    target_path = "/" + target_path
                scope["path"] = target_path
            else:
                headers = dict(scope.get("headers", []))
                for header_name in [b"x-forwarded-uri", b"x-original-url", b"x-rewrite-url"]:
                    val = headers.get(header_name, b"").decode("utf-8")
                    if val:
                        scope["path"] = val.split("?")[0]
                        break
                else:
                    path = scope.get("path", "/")
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
