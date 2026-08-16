import sys
import os
from urllib.parse import parse_qs

# Ensure backend root directory is in Python path for Vercel Serverless execution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app as fastapi_app

async def app(scope, receive, send):
    """
    ASGI entrypoint for Vercel Serverless Functions.
    Parses the original requested path from __url query param or strips Vercel function prefixes.
    """
    if scope["type"] == "http":
        qs = scope.get("query_string", b"").decode("utf-8")
        parsed = parse_qs(qs)
        
        if "__url" in parsed and parsed["__url"]:
            target = parsed["__url"][0]
            if not target.startswith("/"):
                target = "/" + target
            path = target.split("?")[0]
        else:
            path = scope.get("path", "/")
            for prefix in ["/api/index.py", "/api/index", "/api"]:
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
