import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app as fastapi_app

class VercelHeaderLoggerMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            hdrs = {k.decode('utf-8', 'ignore'): v.decode('utf-8', 'ignore') for k, v in headers.items()}
            if "x-inspect" in hdrs or scope.get("path") == "/inspect" or "inspect" in scope.get("path", ""):
                body = json.dumps({"scope_path": scope.get("path"), "headers": hdrs}, indent=2).encode('utf-8')
                await send({'type': 'http.response.start', 'status': 200, 'headers': [(b'content-type', b'application/json')]})
                await send({'type': 'http.response.body', 'body': body})
                return
        await self.app(scope, receive, send)

app = VercelHeaderLoggerMiddleware(fastapi_app)
