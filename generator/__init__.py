import re
import time

def slugify(title):
    s = title.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    if not s:
        s = str(int(time.time()))
    return s

def build_design(title):
    return {
        "feature_desc": ["采集与分析", "Notion 同步", "自动部署"],
        "tech_stack": {
            "frontend": "Next.js",
            "backend": "Python (Vercel Serverless)",
            "infra": ["Vercel", "Cloudflare Worker(CRON)"]
        },
        "api": [
            {"method": "GET", "path": "/api/items", "desc": "列表"},
            {"method": "POST", "path": "/api/items", "desc": "创建"}
        ],
        "data_structures": {
            "Item": {"id": "string", "name": "string", "created_at": "number"}
        }
    }

def build_repo_manifest(slug):
    files = [
        "README.md",
        "vercel.json",
        "frontend/next.config.js",
        "frontend/app/page.tsx",
        "backend/api/items.py",
        "backend/api/deploy.py"
    ]
    return {"name": "product-" + slug, "files": files}
