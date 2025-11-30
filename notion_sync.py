import os
import json
import urllib.request

def write_page(record):
    token = os.getenv("NOTION_API_TOKEN")
    db = os.getenv("NOTION_DB_ID")
    if not token or not db:
        return None
    url = "https://api.notion.com/v1/pages"
    payload = {
        "parent": {"database_id": db},
        "properties": {
            "Title": {"title": [{"text": {"content": record.get("title") or ""}}]},
            "RedditURL": {"url": record.get("reddit_url")},
            "Summary": {"rich_text": [{"text": {"content": record.get("summary") or ""}}]},
            "Category": {"select": {"name": record.get("category") or ""}},
            "Status": {"status": {"name": "待评估"}},
            "Priority": {"select": {"name": record.get("recommendation") or "MEDIUM"}},
            "Scores": {"rich_text": [{"text": {"content": json.dumps(record.get("scores") or {})}}]}
        }
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={
        "Authorization": "Bearer " + token,
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None

def write_pages_bulk(records):
    res = []
    for r in records:
        res.append(write_page(r))
    return res

# Alias for compatibility
sync_to_notion = write_pages_bulk
