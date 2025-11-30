import json
import os
from http.server import BaseHTTPRequestHandler
from webhooks import query_notion_started

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        token = os.getenv("NOTION_API_TOKEN")
        db = os.getenv("NOTION_DB_ID")
        items = query_notion_started(token, db) if token and db else []
        data = json.dumps({"started": items}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
