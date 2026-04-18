#!/usr/bin/env python3
import os
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

_TOKEN = os.environ["EUROLEAGUE_PROXY_TOKEN"]
_PORT = int(os.environ.get("EUROLEAGUE_PROXY_PORT", "8787"))
_TARGET_HOST = "https://www.euroleaguebasketball.net"
_STRIP_HEADERS = {"authorization", "host"}


class _ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.headers.get("Authorization") != f"Bearer {_TOKEN}":
            self.send_response(401)
            self.end_headers()
            return

        if not self.path.startswith("/proxy/"):
            self.send_response(404)
            self.end_headers()
            return

        target_url = _TARGET_HOST + self.path[len("/proxy"):]
        forward_headers = {
            k: v for k, v in self.headers.items()
            if k.lower() not in _STRIP_HEADERS
        }
        req = urllib.request.Request(target_url, headers=forward_headers)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read()
                self.send_response(resp.status)
                self.send_header("Content-Type", resp.headers.get("Content-Type", "text/html"))
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
        except urllib.error.HTTPError as exc:
            self.send_response(exc.code)
            self.end_headers()

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"{self.address_string()} {fmt % args}", flush=True)


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", _PORT), _ProxyHandler)
    print(f"Listening on port {_PORT}", flush=True)
    server.serve_forever()
