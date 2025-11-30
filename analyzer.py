import math

def _score_pain(text, num_comments, score):
    t = text.lower()
    kw = ["pain", "manual", "time-consuming", "expensive", "困扰", "痛点", "麻烦", "复杂"]
    k = sum(1 for w in kw if w in t)
    s = min(10, 3 * k + min(10, (num_comments or 0) / 5) + min(10, (score or 0) / 50))
    return max(1, round(s, 1))

def _score_feasible(text):
    t = text.lower()
    hard_kw = ["realtime", "hardware", "ios", "android", "blockchain", "vr", "deep learning", "gpu", "低延迟", "硬件", "原生"]
    easy_kw = ["automation", "script", "web", "api", "chrome", "notion", "zapier", "n8n", "自动化", "网页", "API"]
    e = sum(1 for w in easy_kw if w in t)
    h = sum(1 for w in hard_kw if w in t)
    base = 6 + e - h
    return min(10, max(1, round(base, 1)))

def _score_market(subreddit, engagement):
    base = {"Entrepreneur": 8, "SaaS": 8, "Smallbusiness": 7, "InternetIsBeautiful": 6, "Startups": 8, "NoCode": 7}.get(subreddit, 6)
    boost = min(2, (engagement or 0) / 100)
    return min(10, round(base + boost, 1))

def _score_competition(text):
    t = text.lower()
    kw = ["already", "existing", "tool", "github", "producthunt", "替代", "已有", "竞争"]
    k = sum(1 for w in kw if w in t)
    score = 10 - min(9, k * 2)
    return max(1, round(score, 1))

def analyze_posts(posts):
    out = []
    for p in posts:
        pain = _score_pain((p.get("title") or "") + " " + (p.get("body") or ""), p.get("num_comments") or 0, p.get("score") or 0)
        feasible = _score_feasible((p.get("title") or "") + " " + (p.get("body") or ""))
        market = _score_market(p.get("subreddit") or "", (p.get("score") or 0) + (p.get("num_comments") or 0))
        competition = _score_competition((p.get("title") or "") + " " + (p.get("body") or ""))
        overall = round((pain + feasible + market + competition) / 4, 1)
        category = "AI工具"
        recommendation = "HIGH" if overall >= 7.5 else ("MEDIUM" if overall >= 5.5 else "LOW")
        out.append({
            "id": p.get("id"),
            "title": p.get("title"),
            "summary": (p.get("body") or "")[:280],
            "scores": {
                "PainScore": pain,
                "FeasibleScore": feasible,
                "MarketSizeScore": market,
                "CompetitionScore": competition,
                "OverallScore": overall
            },
            "category": category,
            "recommendation": recommendation,
            "reddit_url": "https://reddit.com" + str(p.get("permalink") or "")
        })
    return out
