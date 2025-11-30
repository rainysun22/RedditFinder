import json
from http.server import BaseHTTPRequestHandler
from deployer import deploy_manifest

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length) if length > 0 else b"{}"
        payload = json.loads(body.decode("utf-8") or "{}")
        res = deploy_manifest(payload)
        out = {"deploy": {"platform": "vercel", "url": res.get("url"), "deployment_id": res.get("deployment_id")}}
        data = json.dumps(out).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
