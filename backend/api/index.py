import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app as fastapi_app

class VercelDebugMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers_dict = {k.decode('latin1'): v.decode('latin1') for k, v in scope.get("headers", [])}
            info = {
                "path": scope.get("path"),
                "raw_path": scope.get("raw_path", b"").decode('latin1'),
                "query_string": scope.get("query_string", b"").decode('latin1'),
                "headers": headers_dict
            }
            # If path ends with /scope_info
            if scope.get("path", "").endswith("/scope_info"):
                await send({
                    'type': 'http.response.start',
                    'status': 200,
                    'headers': [(b'content-type', b'application/json')]
                })
                await send({
                    'type': 'http.response.body',
                    'body': json.dumps(info, indent=2).encode('utf-8')
                })
                return

        await self.app(scope, receive, send)

app = VercelDebugMiddleware(fastapi_app)
