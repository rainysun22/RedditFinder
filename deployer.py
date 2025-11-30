import os
import json
import urllib.request

def deploy_manifest(manifest):
    token = os.getenv("VERCEL_TOKEN")
    project = os.getenv("VERCEL_PROJECT_ID")
    if not token or not project:
        return {"platform": "vercel", "url": None, "deployment_id": None}
    url = "https://api.vercel.com/v13/deployments"
    payload = {"name": project, "files": [], "project": project}
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json"
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return {"platform": "vercel", "url": data.get("url"), "deployment_id": data.get("id")}
    except Exception:
        return {"platform": "vercel", "url": None, "deployment_id": None}
