import urllib.request
import json

def fetch_subreddit_page(subreddit, limit, after):
    base = "https://www.reddit.com/r/" + subreddit + "/new.json?limit=" + str(min(limit, 100))
    url = base + ("&after=" + after if after else "")
    req = urllib.request.Request(url, headers={"User-Agent": "ProductAutoBuilder/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    items = []
    for child in data.get("data", {}).get("children", []):
        d = child.get("data", {})
        items.append({
            "id": d.get("name"),
            "subreddit": d.get("subreddit"),
            "title": d.get("title"),
            "body": d.get("selftext") or "",
            "score": int(d.get("score") or 0),
            "num_comments": int(d.get("num_comments") or 0),
            "created_utc": int(d.get("created_utc") or 0),
            "url": d.get("url"),
            "permalink": d.get("permalink"),
            "author": d.get("author"),
            "_ext": {"source": "reddit_public"}
        })
    return items, data.get("data", {}).get("after")

def collect_posts(subreddits, total_limit):
    collected = []
    per = int(max(1, total_limit // len(subreddits)))
    for s in subreddits:
        after = None
        fetched = 0
        while fetched < per:
            try:
                items, after = fetch_subreddit_page(s, per - fetched, after)
                collected.extend(items)
                fetched += len(items)
                if not after or len(items) == 0:
                    break
            except Exception as e:
                print(f"Error fetching {s}: {e}")
                break
    unique = {}
    for p in collected:
        unique[p["id"]] = p
    posts = list(unique.values())
    posts.sort(key=lambda x: (-x["score"], -x["created_utc"]))
    return posts[:total_limit]
