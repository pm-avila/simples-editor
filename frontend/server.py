"""Minimal static file server for the frontend container."""

import os
import pathlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

PORT = 8080
DIST = pathlib.Path(__file__).resolve().parent / "dist"

_DEFAULT_URL = "https://example.supabase.co"
_DEFAULT_KEY = "dev-anon-key"


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
        if self.path.split("?")[0] == "/config.js":
            body = _build_config_js()
            self.send_response(200)
            self.send_header("Content-Type", "application/javascript; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def send_error(self, code, message=None, explain=None):
        # SPA fallback: serve index.html for any 404 so client-side routing works
        if code == 404:
            index = DIST / "index.html"
            if index.exists():
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(index.read_bytes())
                return
        super().send_error(code, message, explain)


if __name__ == "__main__":
    with ThreadingHTTPServer(("", PORT), Handler) as httpd:
        print(f"Frontend serving on port {PORT}", flush=True)
        httpd.serve_forever()
