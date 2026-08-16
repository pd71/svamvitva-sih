import sys
import os
from urllib.parse import parse_qs

# Ensure backend root directory is in Python path for Vercel Serverless execution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app as fastapi_app

class VercelFix:
    """
    Parses original URL path passed in ?path=/$1 query parameter by Vercel rewrites,
    resets scope['root_path'] to empty string, and sets scope['path'] & scope['raw_path']
    so FastAPI matches exact route definitions natively on Vercel Serverless.
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            qs = scope.get("query_string", b"").decode("utf-8")
            parsed = parse_qs(qs)
            if "path" in parsed and parsed["path"]:
                real_path = parsed["path"][0]
                if not real_path.startswith("/"):
                    real_path = "/" + real_path
                scope["path"] = real_path.split("?")[0]
            else:
                path = scope.get("path", "/")
                for prefix in ["/api/index.py", "/api/index"]:
                    if path.startswith(prefix):
                        path = path[len(prefix):]
                        break
                scope["path"] = path if path else "/"
            
            scope["root_path"] = ""
            scope["raw_path"] = scope["path"].encode("utf-8")
        await self.app(scope, receive, send)

app = VercelFix(fastapi_app)
