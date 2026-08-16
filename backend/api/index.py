import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app as fastapi_app

class VercelPathResolver:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            
            forwarded_uri = headers.get(b"x-forwarded-uri", b"").decode("utf-8")
            matched_path = headers.get(b"x-matched-path", b"").decode("utf-8")
            raw_path = scope.get("path", "/")
            
            # Determine true target path from Vercel headers
            if forwarded_uri:
                target_path = forwarded_uri.split("?")[0]
            elif matched_path and not matched_path.startswith("/api/index"):
                target_path = matched_path.split("?")[0]
            else:
                target_path = raw_path
                for prefix in ["/api/index.py", "/api/index"]:
                    if target_path.startswith(prefix):
                        target_path = target_path[len(prefix):]
                        break

            if not target_path or target_path == "":
                target_path = "/"

            scope["root_path"] = ""
            scope["path"] = target_path
            scope["raw_path"] = target_path.encode("utf-8")
            
        await self.app(scope, receive, send)

app = VercelPathResolver(fastapi_app)
