"""Small browser-first Studio service for OpenMontage (Python stdlib only)."""
import hmac
import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from wsgiref.simple_server import make_server

ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "static" / "index.html"


def response(start_response, status, payload, content_type="application/json; charset=utf-8"):
    data = payload if isinstance(payload, bytes) else payload.encode("utf-8")
    start_response(status, [("Content-Type", content_type), ("Content-Length", str(len(data))),
                            ("X-Content-Type-Options", "nosniff"), ("Cache-Control", "no-store")])
    return [data]


def app(environ, start_response):
    path, method = environ.get("PATH_INFO", "/"), environ.get("REQUEST_METHOD", "GET")
    if path == "/health" and method == "GET":
        return response(start_response, "200 OK", json.dumps({"ok": True, "service": "openmontage-studio"}))
    if path == "/" and method == "GET":
        return response(start_response, "200 OK", INDEX.read_bytes(), "text/html; charset=utf-8")
    if path != "/api/storyboard" or method != "POST":
        return response(start_response, "404 Not Found", json.dumps({"error": "Not found"}))
    try:
        length = int(environ.get("CONTENT_LENGTH") or 0)
        if length > 12000:
            return response(start_response, "413 Payload Too Large", json.dumps({"error": "Brief is too large."}))
        body = json.loads(environ["wsgi.input"].read(length) or b"{}")
    except (ValueError, json.JSONDecodeError):
        return response(start_response, "400 Bad Request", json.dumps({"error": "Invalid JSON request."}))

    title = str(body.get("title", "Untitled project")).strip()[:100]
    prompt = str(body.get("prompt", "")).strip()[:6000]
    if len(prompt) < 12:
        return response(start_response, "400 Bad Request", json.dumps({"error": "Describe the video in at least 12 characters."}))

    access_code = os.getenv("STUDIO_ACCESS_CODE")
    supplied = environ.get("HTTP_X_STUDIO_CODE", "")
    if not access_code:
        return response(start_response, "503 Service Unavailable", json.dumps({"error": "Studio is not configured yet. Set STUDIO_ACCESS_CODE in the service environment."}))
    if not hmac.compare_digest(supplied, access_code):
        return response(start_response, "401 Unauthorized", json.dumps({"error": "Enter the correct Studio access code."}))
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return response(start_response, "503 Service Unavailable", json.dumps({"error": "Set OPENAI_API_KEY in the Studio service environment."}))

    system = ("You are a concise video pre-production assistant. Turn the brief into a practical storyboard. "
              "Return only valid JSON with keys: logline (string), duration_seconds (integer), style (string), "
              "scenes (array). Each scene must contain title, duration_seconds, visual, narration, audio, transition. "
              "Use 4 to 8 scenes and keep the total close to 30 seconds.")
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    payload = {"model": model, "response_format": {"type": "json_object"},
               "messages": [{"role": "system", "content": system},
                            {"role": "user", "content": f"Project: {title}\nBrief: {prompt}"}]}
    req = Request("https://api.openai.com/v1/chat/completions", data=json.dumps(payload).encode(),
                  headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(req, timeout=90) as upstream:
            result = json.loads(upstream.read())
        storyboard = json.loads(result["choices"][0]["message"]["content"])
        if not isinstance(storyboard.get("scenes"), list) or not storyboard["scenes"]:
            raise ValueError("No scenes returned")
        return response(start_response, "200 OK", json.dumps({"title": title, **storyboard}))
    except (HTTPError, URLError, TimeoutError):
        return response(start_response, "502 Bad Gateway", json.dumps({"error": "The AI service could not be reached. Check the server logs and API key."}))
    except (KeyError, ValueError, json.JSONDecodeError):
        return response(start_response, "502 Bad Gateway", json.dumps({"error": "The AI returned an invalid storyboard. Try generating again."}))


if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))
    with make_server("0.0.0.0", port, app) as server:
        server.serve_forever()
