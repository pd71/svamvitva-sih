import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app as fastapi_app

class VercelPathResolver:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            
            # Print diagnostic info to Vercel runtime logs
            matched_path = headers.get(b"x-matched-path", b"").decode("utf-8")
            raw_path = scope.get("path", "/")
            
            # Determine true target path
            if matched_path and not matched_path.startswith("/api/index"):
                target_path = matched_path
            else:
                target_path = raw_path
                for prefix in ["/api/index.py", "/api/index"]:
                    if target_path.startswith(prefix):
                        target_path = target_path[len(prefix):]
                        break
            
            target_path = target_path if target_path else "/"
            scope["root_path"] = ""
            scope["path"] = target_path
            scope["raw_path"] = target_path.encode("utf-8")
            
        await self.app(scope, receive, send)

app = VercelPathResolver(fastapi_app)
