import sys
import os

# Add parent directory to sys.path to allow importing collector
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from http.server import BaseHTTPRequestHandler
from collector import collect_posts
from analyzer import analyze_posts
from notion_sync import sync_to_notion
from translator import translate_text_real
import json
import traceback

def translate_analysis(analysis_results):
    """Translate analysis results to Chinese before syncing"""
    print("Translating results to Chinese...")
    translated_results = []
    for item in analysis_results:
        # Clone item to avoid modifying original if needed elsewhere (though here it's fine)
        new_item = item.copy()
        
        # Translate Title
        if new_item.get("title"):
            new_item["title"] = translate_text_real(new_item["title"], "zh-CN")
            
        # Translate Summary
        if new_item.get("summary"):
            new_item["summary"] = translate_text_real(new_item["summary"], "zh-CN")
            
        # Translate Category (optional, but good for consistency)
        if new_item.get("category"):
            # Simple mapping or translate
            new_item["category"] = translate_text_real(new_item["category"], "zh-CN")
            
        translated_results.append(new_item)
    return translated_results

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
            
            # Translate before syncing
            translated_analysis = translate_analysis(analysis)
            
            print("Syncing to Notion...")
            synced = sync_to_notion(translated_analysis)
            
            response = {
                "posts": posts,
                "analysis": translated_analysis, # Return translated
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
            
            # Translate before syncing
            translated_analysis = translate_analysis(analysis)
            
            print("Syncing to Notion...")
            synced = sync_to_notion(translated_analysis)
            
            response = {
                "posts": posts,
                "analysis": translated_analysis,
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
