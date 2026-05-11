"""Minimal static file server for the frontend container."""

import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)


if __name__ == "__main__":
    with ThreadingHTTPServer(("", PORT), Handler) as httpd:
        print(f"Frontend serving on port {PORT}", flush=True)
        httpd.serve_forever()
