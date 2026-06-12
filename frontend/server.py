"""Minimal static file server for the frontend container."""

import os
import pathlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

PORT = 8080
DIST = pathlib.Path(__file__).resolve().parent / "dist"

_DEFAULT_URL = "https://example.supabase.co"
_DEFAULT_KEY = "dev-anon-key"


def _send_no_cache_headers(handler) -> None:
    handler.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
    handler.send_header("Pragma", "no-cache")


def _serve_bytes(handler, content_type: str, body: bytes) -> None:
    handler.send_response(200)
    handler.send_header("Content-Type", content_type)
    _send_no_cache_headers(handler)
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    if handler.command != "HEAD":
        handler.wfile.write(body)


def _build_config_js() -> bytes:
    """Return config.js content populated from runtime environment variables."""
    def _js_str(s: str) -> str:
        return s.replace("\\", "\\\\").replace('"', '\\"')

    url = _js_str(os.getenv("SUPABASE_URL", _DEFAULT_URL))
    key = _js_str(os.getenv("SUPABASE_ANON_KEY", _DEFAULT_KEY))
    return (
        f'window.__SUPABASE_URL__ = "{url}";\n'
        f'window.__SUPABASE_ANON_KEY__ = "{key}";\n'
    ).encode()


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIST), **kwargs)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path in {"/", "/index.html"}:
            index = DIST / "index.html"
            if index.exists():
                _serve_bytes(self, "text/html; charset=utf-8", index.read_bytes())
                return
        if path == "/config.js":
            _serve_bytes(self, "application/javascript; charset=utf-8", _build_config_js())
            return
        super().do_GET()

    def do_HEAD(self):
        path = self.path.split("?")[0]
        if path in {"/", "/index.html"}:
            index = DIST / "index.html"
            if index.exists():
                _serve_bytes(self, "text/html; charset=utf-8", index.read_bytes())
                return
        if path == "/config.js":
            _serve_bytes(self, "application/javascript; charset=utf-8", _build_config_js())
            return
        super().do_HEAD()

    def send_error(self, code, message=None, explain=None):
        # SPA fallback: serve index.html for any 404 so client-side routing works
        if code == 404:
            index = DIST / "index.html"
            if index.exists():
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                _send_no_cache_headers(self)
                self.end_headers()
                self.wfile.write(index.read_bytes())
                return
        super().send_error(code, message, explain)


if __name__ == "__main__":
    with ThreadingHTTPServer(("", PORT), Handler) as httpd:
        print(f"Frontend serving on port {PORT}", flush=True)
        httpd.serve_forever()
