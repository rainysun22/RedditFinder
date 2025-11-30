import os
import json
import urllib.request

def query_notion_started(token, db_id):
    url = "https://api.notion.com/v1/databases/" + db_id + "/query"
    payload = {"filter": {"property": "Status", "status": {"equals": "开始开发"}}}
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={
        "Authorization": "Bearer " + token,
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8")).get("results", [])
    except Exception:
        return []
