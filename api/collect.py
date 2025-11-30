import sys
import os

# Add parent directory to sys.path to allow importing collector
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from http.server import BaseHTTPRequestHandler
from collector import collect_posts
from analyzer import analyze_posts
from notion_sync import sync_to_notion
import json
import traceback

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests (for browser testing)"""
        try:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # Trigger collection with defaults
            print("Starting collection via GET...")
            posts = collect_posts(["SaaS", "SideProject", "MicroSaaS"], 5)
            
            if not posts:
                print("No posts collected.")
                self.wfile.write(json.dumps({
                    "posts": [],
                    "analysis": [],
                    "count": 0,
                    "debug": "No posts found. Check collector logs."
                }).encode('utf-8'))
                return

            print(f"Collected {len(posts)} posts. Starting analysis...")
            analysis = analyze_posts(posts)
            
            print("Syncing to Notion...")
            synced = sync_to_notion(analysis)
            
            response = {
                "posts": posts,
                "analysis": analysis,
                "count": len(posts),
                "notion_synced": synced
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            print(f"Error in do_GET: {e}")
            traceback.print_exc()
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))

    def do_POST(self):
        try:
            content_len = int(self.headers.get('Content-Length', 0))
            post_body = self.rfile.read(content_len)
            data = json.loads(post_body) if content_len > 0 else {}

            subreddits = data.get("subreddits", ["SaaS", "SideProject", "MicroSaaS"])
            limit = data.get("limit", 10)

            print(f"Starting collection for {subreddits} with limit {limit}...")
            posts = collect_posts(subreddits, limit)
            
            if not posts:
                print("No posts collected.")
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "posts": [],
                    "analysis": [],
                    "count": 0,
                    "debug": "No posts found. Check collector logs."
                }).encode('utf-8'))
                return

            print(f"Collected {len(posts)} posts. Starting analysis...")
            analysis = analyze_posts(posts)
            
            print("Syncing to Notion...")
            synced = sync_to_notion(analysis)
            
            response = {
                "posts": posts,
                "analysis": analysis,
                "count": len(posts),
                "notion_synced": synced
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            print(f"Error in do_POST: {e}")
            traceback.print_exc()
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))

# For local testing
if __name__ == "__main__":
    from http.server import HTTPServer
    server = HTTPServer(('localhost', 8000), handler)
    print("Starting server at http://localhost:8000")
    server.serve_forever()
