import json

async def app(scope, receive, send):
    if scope["type"] == "http":
        headers = [[k.decode("latin1"), v.decode("latin1")] for k, v in scope.get("headers", [])]
        body = json.dumps({
            "path": scope.get("path"),
            "raw_path": scope.get("raw_path", b"").decode("latin1"),
            "query_string": scope.get("query_string", b"").decode("latin1"),
            "headers": headers,
            "root_path": scope.get("root_path", "")
        }).encode("utf-8")

        await send({
            "type": "http.response.start",
            "status": 200,
            "headers": [
                [b"content-type", b"application/json"],
                [b"content-length", str(len(body)).encode("utf-8")]
            ]
        })
        await send({
            "type": "http.response.body",
            "body": body
        })
