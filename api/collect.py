import json
from http.server import BaseHTTPRequestHandler
from collector import collect_posts
from analyzer import analyze_posts
from notion_sync import write_pages_bulk

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length) if length > 0 else b"{}"
        payload = json.loads(body.decode("utf-8") or "{}")
        subs = payload.get("subreddits") or ["Entrepreneur", "SaaS", "Smallbusiness", "InternetIsBeautiful", "Startups", "NoCode"]
        limit = int(payload.get("limit") or 200)
        posts = collect_posts(subs, limit)
        analysis = analyze_posts(posts)
        notion_res = write_pages_bulk(analysis)
        result = {"posts": posts, "analysis": analysis, "count": len(posts), "_notion_debug": notion_res}
        data = json.dumps(result).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
