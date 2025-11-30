import os
import json
from redditsfinder import RedditsFinder

def collect_posts(subreddits, total_limit):
    # RedditsFinder usually prints to stdout or returns JSON.
    # Based on typical usage:
    # f = RedditsFinder(subreddits=["subreddit_name"], limit=N)
    # posts = f.get_posts()
    
    collected = []
    # Distribute limit among subreddits
    per_sub_limit = max(1, int(total_limit / len(subreddits)))
    
    for sub_name in subreddits:
        try:
            # RedditsFinder 2.x usage
            # Note: RedditsFinder might write to a file or return a dict.
            # We will use it to fetch and then parse the result.
            finder = RedditsFinder()
            # The library's API might vary, but assuming standard usage:
            # It often returns a JSON-compatible list of dicts
            # We capture the result. 
            # Since RedditsFinder 2.1.3 is a scraper wrapper, it might not need API keys.
            
            # Using the library's simplified interface if available, 
            # otherwise we instantiate and call specific methods.
            # Assuming scrape_subreddit or similar method exists.
            # If the library is strictly CLI, we might need to subprocess it, 
            # but let's try to import and use the class.
            
            # Standard scraping
            posts = finder.get_posts(subreddit_name=sub_name, limit=per_sub_limit)
            
            if posts:
                for p in posts:
                    # Normalize fields
                    collected.append({
                        "id": p.get("id", ""),
                        "subreddit": sub_name,
                        "title": p.get("title", ""),
                        "body": p.get("self_text", "") or p.get("body", "") or "",
                        "score": int(p.get("score", 0) or 0),
                        "num_comments": int(p.get("num_comments", 0) or 0),
                        "created_utc": float(p.get("created_utc", 0) or 0),
                        "url": p.get("url", ""),
                        "permalink": p.get("permalink", ""),
                        "author": p.get("author", ""),
                        "_ext": {"source": "redditsfinder"}
                    })
        except Exception as e:
            print(f"Error collecting from r/{sub_name}: {e}")
            continue

    # Deduplicate by ID
    unique = {}
    for p in collected:
        if p["id"]:
            unique[p["id"]] = p
    
    posts = list(unique.values())
    # Sort by score (desc) then time (desc)
    posts.sort(key=lambda x: (-x["score"], -x["created_utc"]))
    
    return posts[:total_limit]
