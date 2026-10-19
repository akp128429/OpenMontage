"""Static Studio companion service (no provider API or login credentials)."""
import json
import os
from pathlib import Path
from wsgiref.simple_server import make_server

INDEX = Path(__file__).resolve().parent / "static" / "index.html"


def app(environ, start_response):
    path, method = environ.get("PATH_INFO", "/"), environ.get("REQUEST_METHOD", "GET")
    if method == "GET" and path == "/health":
        body = json.dumps({"ok": True, "service": "openmontage-studio"}).encode()
        start_response("200 OK", [("Content-Type", "application/json; charset=utf-8"),
                                   ("Content-Length", str(len(body))), ("Cache-Control", "no-store")])
        return [body]
    if method == "GET" and path == "/":
        body = INDEX.read_bytes()
        start_response("200 OK", [("Content-Type", "text/html; charset=utf-8"),
                                   ("Content-Length", str(len(body))),
                                   ("X-Content-Type-Options", "nosniff")])
        return [body]
    body = b'{"error":"Not found"}'
    start_response("404 Not Found", [("Content-Type", "application/json; charset=utf-8"),
                                     ("Content-Length", str(len(body)))])
    return [body]


if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))
    with make_server("0.0.0.0", port, app) as server:
        server.serve_forever()
