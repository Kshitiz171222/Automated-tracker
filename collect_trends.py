"""
Google Trends search-interest collector for every category in watchlist.txt.
Uses pytrends (no login needed). Appends one row per category per run to
data/trends_<category>.csv
"""
import csv
import datetime
import os
import re
import time
from pytrends.request import TrendReq

DATA_DIR = "data"
GEO = "IN"  # change to "" for worldwide


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def read_watchlist():
    with open("watchlist.txt") as f:
        return [l.strip() for l in f if l.strip() and not l.startswith("#")]


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    today = datetime.date.today().isoformat()
    pytrends = TrendReq(hl="en-US", tz=330)

    for kw in read_watchlist():
        try:
            pytrends.build_payload([kw], timeframe="today 3-m", geo=GEO)
            df = pytrends.interest_over_time()
            if df.empty:
                print(f"No trend data for '{kw}'")
                continue
            avg_index = round(df[kw].tail(7).mean(), 1)
            prev_index = round(df[kw].iloc[-14:-7].mean(), 1) if len(df) >= 14 else None
            growth_pct = (
                round(((avg_index - prev_index) / prev_index) * 100, 1)
                if prev_index and prev_index > 0 else ""
            )
        except Exception as e:
            print(f"Skipping '{kw}': {e}")
            continue

        path = os.path.join(DATA_DIR, f"trends_{slug(kw)}.csv")
        is_new = not os.path.exists(path)
        with open(path, "a", newline="") as f:
            w = csv.writer(f)
            if is_new:
                w.writerow(["date", "category", "search_index", "wow_growth_pct"])
            w.writerow([today, kw, avg_index, growth_pct])

        print(f"{kw}: index={avg_index}, growth={growth_pct}%")
        time.sleep(3)  # Google Trends rate-limits aggressively


if __name__ == "__main__":
    main()
