"""
Reddit mention counter for every category in watchlist.txt.
Uses Reddit's public search JSON endpoint - no API key, no login needed.
Appends one row per category per run to data/reddit_<category>.csv
"""
import csv
import datetime
import os
import re
import time
import urllib.request
import json

DATA_DIR = "data"
HEADERS = {"User-Agent": "whitespace-tracker/0.1"}


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def read_watchlist():
    with open("watchlist.txt") as f:
        return [l.strip() for l in f if l.strip() and not l.startswith("#")]


def search_reddit(keyword, days=7):
    url = f"https://www.reddit.com/search.json?q={urllib.parse.quote(keyword)}&sort=new&limit=100&t=month"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as resp:
        payload = json.loads(resp.read())

    cutoff = time.time() - days * 86400
    posts, comments, score = 0, 0, 0
    for child in payload.get("data", {}).get("children", []):
        d = child["data"]
        if d["created_utc"] < cutoff:
            continue
        posts += 1
        comments += d.get("num_comments", 0)
        score += d.get("score", 0)
    return posts, comments, score


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    today = datetime.date.today().isoformat()

    for kw in read_watchlist():
        try:
            posts, comments, score = search_reddit(kw)
        except Exception as e:
            print(f"Skipping '{kw}': {e}")
            continue

        path = os.path.join(DATA_DIR, f"reddit_{slug(kw)}.csv")
        is_new = not os.path.exists(path)
        with open(path, "a", newline="") as f:
            w = csv.writer(f)
            if is_new:
                w.writerow(["date", "category", "posts", "comments", "total_upvotes", "total_mentions"])
            w.writerow([today, kw, posts, comments, score, posts + comments])

        print(f"{kw}: {posts} posts, {comments} comments, {score} upvotes")
        time.sleep(2)  # be polite to Reddit's servers


if __name__ == "__main__":
    import urllib.parse
    main()
