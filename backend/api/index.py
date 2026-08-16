import sys
import os

# Ensure backend root directory is in Python path for Vercel Serverless execution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app as fastapi_app

async def app(scope, receive, send):
    """
    ASGI entrypoint for Vercel Serverless Functions.
    Extracts true original request path from x-matched-path or scope['path']
    and strips Vercel function routing prefixes so FastAPI matches exact route definitions.
    """
    if scope["type"] == "http":
        path = scope.get("path", "/")
        headers = dict(scope.get("headers", []))
        matched_path = headers.get(b"x-matched-path", b"").decode("utf-8")
        if matched_path:
            path = matched_path

        for prefix in ["/api/index.py", "/api/index"]:
            if path.startswith(prefix):
                path = path[len(prefix):]
                break

        path = path if path else "/"
        scope["root_path"] = ""
        scope["path"] = path
        scope["raw_path"] = path.encode("utf-8")

    await fastapi_app(scope, receive, send)
