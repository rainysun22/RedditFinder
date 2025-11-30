import feedparser
import time
from datetime import datetime
import re

def collect_posts(subreddits, total_limit):
    collected = []
    # Distribute limit roughly
    per_sub_limit = max(1, int(total_limit / len(subreddits)))
    
    # Reddit RSS usually returns 25 items. 
    # If we need more, we might need to handle 'after' parameter if RSS supports it,
    # but standard RSS is usually just the latest.
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    for sub_name in subreddits:
        rss_url = f"https://www.reddit.com/r/{sub_name}/new/.rss"
        print(f"Fetching RSS: {rss_url}")
        
        try:
            # feedparser can handle URLs directly but adding headers is safer with requests + string parsing
            # However, feedparser's internal fetcher is usually okay for simple use.
            # Let's try feedparser directly first.
            feed = feedparser.parse(rss_url, agent=headers['User-Agent'])
            
            if feed.bozo:
                print(f"Feed error for {sub_name}: {feed.bozo_exception}")
                # Sometimes it's just a warning, continue if entries exist
            
            if not feed.entries:
                print(f"No entries found for r/{sub_name}")
                continue
                
            count = 0
            for entry in feed.entries:
                if count >= per_sub_limit:
                    break
                
                # Extract data
                # RSS fields: title, link, updated, author, content/summary
                
                # ID: usually in 'id' or 'link'
                post_id = entry.id if 'id' in entry else entry.link
                
                # Body: 'content' (list) or 'summary'
                body = ""
                if 'content' in entry:
                    body = entry.content[0].value
                elif 'summary' in entry:
                    body = entry.summary
                
                # Clean HTML from body if needed, or keep it. 
                # The system likely expects text. Let's do a simple strip.
                clean_body = re.sub('<[^<]+?>', '', body)
                
                # Timestamp
                # feedparser parses dates into time.struct_time
                created_utc = time.mktime(entry.updated_parsed) if 'updated_parsed' in entry and entry.updated_parsed else time.time()
                
                collected.append({
                    "id": post_id,
                    "subreddit": sub_name, # RSS entry might not have subreddit name explicitly in a clean field
                    "title": entry.title,
                    "body": clean_body[:5000], # Truncate if too long
                    "score": 0, # RSS doesn't provide score
                    "num_comments": 0, # RSS doesn't provide comment count
                    "created_utc": created_utc,
                    "url": entry.link,
                    "permalink": entry.link, # RSS link is usually the permalink
                    "author": entry.author if 'author' in entry else "[unknown]",
                    "_ext": {"source": "rss_feed"}
                })
                count += 1
                
        except Exception as e:
            print(f"Error collecting from r/{sub_name}: {e}")
            continue

    # Deduplicate
    unique = {p["id"]: p for p in collected}
    posts = list(unique.values())
    
    # Sort by time (desc) since score is 0
    posts.sort(key=lambda x: -x["created_utc"])
    
    return posts[:total_limit]
