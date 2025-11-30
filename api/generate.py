import json
from http.server import BaseHTTPRequestHandler
from generator import slugify, build_design, build_repo_manifest

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length) if length > 0 else b"{}"
        payload = json.loads(body.decode("utf-8") or "{}")
        title = payload.get("title") or "Product"
        slug = slugify(title)
        design = build_design(title)
        manifest = build_repo_manifest(slug)
        result = {"design": design, "repo_manifest": manifest}
        data = json.dumps(result).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
