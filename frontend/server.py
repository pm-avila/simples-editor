"""Minimal static file server for the frontend container."""

import os
import pathlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

PORT = 8080
DIST = pathlib.Path(__file__).resolve().parent / "dist"


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIST), **kwargs)

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
