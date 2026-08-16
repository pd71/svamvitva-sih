import sys
import os

# Ensure backend root directory is in Python path for Vercel Serverless execution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app as fastapi_app

async def app(scope, receive, send):
    """
    ASGI entrypoint for Vercel Serverless Functions.
    Strips Vercel function routing prefixes (/api/index.py, /api/index)
    from scope['path'] and scope['raw_path'] so FastAPI matches exact route definitions.
    """
    if scope["type"] == "http":
        path = scope.get("path", "/")
        for prefix in ["/api/index.py", "/api/index"]:
            if path == prefix or path == prefix + "/":
                path = "/"
                break
            elif path.startswith(prefix + "/"):
                path = path[len(prefix):]
                break
        path = path if path else "/"
        scope["path"] = path
        scope["raw_path"] = path.encode("utf-8")
    await fastapi_app(scope, receive, send)
