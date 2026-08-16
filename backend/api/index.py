import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app as fastapi_app

class VercelDebugMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            # Return debug info if requesting /debug
            path = scope.get("path", "")
            if "debug" in path or "debug" in str(headers):
                response_body = f"path: {path}\nheaders: {headers}\nscope_keys: {list(scope.keys())}".encode('utf-8')
                await send({
                    'type': 'http.response.start',
                    'status': 200,
                    'headers': [(b'content-type', b'text/plain')]
                })
                await send({
                    'type': 'http.response.body',
                    'body': response_body
                })
                return

        await self.app(scope, receive, send)

app = fastapi_app
