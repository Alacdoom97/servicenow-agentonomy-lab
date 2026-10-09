"""Loopback-only training server. No authentication; do not expose to a network."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
from .engine import ROOT
from .store import Conflict

def make_server(store, port=8765):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass
        def send(self, status, data, content_type="application/json"):
            body = data.encode("utf-8") if isinstance(data, str) else json.dumps(data).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", content_type + "; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
        def do_GET(self):
            path = urlparse(self.path).path
            if path == "/": self.send(200, (ROOT / "visual/index.html").read_text(encoding="utf-8"), "text/html")
            elif path == "/api/incidents": self.send(200, store.incidents())
            elif path == "/api/audit": self.send(200, store.audit())
            elif path == "/api/health": self.send(200, {"mode":"offline", "adapter":"sqlite_mock", "ai_agent_studio":"unknown"})
            else: self.send(404, {"error":"Not found"})
        def do_POST(self):
            # JSON and same-origin checks prevent casual cross-origin writes to localhost.
            if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                return self.send(415, {"error":"Use application/json"})
            origin = self.headers.get("Origin")
            expected = f"http://127.0.0.1:{self.server.server_port}"
            if origin and origin != expected:
                return self.send(403, {"error":"Origin not allowed"})
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if not 0 < size <= 16384: raise ValueError("Body must be 1–16384 bytes")
                body = json.loads(self.rfile.read(size))
                if not isinstance(body, dict): raise ValueError("Body must be an object")
                path = urlparse(self.path).path
                if path == "/api/triage": result = store.run(body["number"])
                elif path == "/api/preview":
                    from .engine import triage
                    result = triage(body)
                elif path == "/api/decision": result = store.decide(body["run_id"], body["decision"], body["reviewer"])
                else: return self.send(404, {"error":"Not found"})
                self.send(200, result)
            except Conflict as error: self.send(409, {"error":str(error)})
            except KeyError as error: self.send(404, {"error":str(error)})
            except (ValueError, TypeError) as error: self.send(400, {"error":str(error)})
    return ThreadingHTTPServer(("127.0.0.1", port), Handler)
