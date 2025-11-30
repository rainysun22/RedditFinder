import json
import os
import urllib.request
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length) if length > 0 else b"{}"
        payload = json.loads(body.decode("utf-8") or "{}")
        token = os.getenv("NOTION_API_TOKEN")
        page_id = payload.get("page_id")
        if token and page_id:
            url = "https://api.notion.com/v1/pages/" + page_id
            props = {"properties": {}}
            if payload.get("status"):
                props["properties"]["Status"] = {"status": {"name": payload["status"]}}
            if payload.get("online_url"):
                props["properties"]["OnlineURL"] = {"url": payload["online_url"]}
            if payload.get("repo_url"):
                props["properties"]["RepoURL"] = {"url": payload["repo_url"]}
            if payload.get("changelog"):
                props["properties"]["Changelog"] = {"rich_text": [{"text": {"content": "; ".join(payload["changelog"])}}]}
            req = urllib.request.Request(url, data=json.dumps(props).encode("utf-8"), headers={"Authorization": "Bearer " + token, "Notion-Version": "2022-06-28", "Content-Type": "application/json"}, method="PATCH")
            try:
                with urllib.request.urlopen(req, timeout=15) as resp:
                    resp.read()
            except Exception:
                pass
        out = {"update": {"status": payload.get("status"), "online_url": payload.get("online_url"), "repo_url": payload.get("repo_url"), "changelog": payload.get("changelog")}}
        data = json.dumps(out).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
