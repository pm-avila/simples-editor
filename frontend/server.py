import http.server
from http.server import ThreadingHTTPServer

PORT = 8080

Handler = http.server.SimpleHTTPRequestHandler

with ThreadingHTTPServer(("", PORT), Handler) as httpd:
    print(f"Serving on port {PORT}")
    httpd.serve_forever()
