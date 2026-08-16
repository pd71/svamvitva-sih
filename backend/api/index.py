import sys
import os
from urllib.parse import parse_qs

# Ensure backend root directory is in Python path for Vercel Serverless execution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app as fastapi_app

async def app(scope, receive, send):
    """
    ASGI entrypoint for Vercel Serverless Functions.
    Parses original client URL path from __url query parameter,
    resets scope['root_path'] to empty, and passes exact path to FastAPI.
    """
    if scope["type"] == "http":
        qs = scope.get("query_string", b"").decode("utf-8")
        parsed = parse_qs(qs)
        if "__url" in parsed and parsed["__url"]:
            path = parsed["__url"][0]
        else:
            path = scope.get("path", "/")

        if not path.startswith("/"):
            path = "/" + path

        path = path.split("?")[0]
        path = path if path else "/"

        scope["root_path"] = ""
        scope["path"] = path
        scope["raw_path"] = path.encode("utf-8")

    await fastapi_app(scope, receive, send)
