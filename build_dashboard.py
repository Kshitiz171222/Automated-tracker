"""
Reads every CSV in data/ and builds docs/index.html - one dashboard page,
published automatically via GitHub Pages. This is the link you'll open
every week.
"""
import csv
import glob
import os
import re

# ---- thresholds: edit these two numbers if you want the "ready to look
#      closer" flag to trigger earlier/later ----
THRESHOLD_MENTIONS = 30
THRESHOLD_GROWTH_PCT = 25

os.makedirs("docs", exist_ok=True)


def load_csv(path):
    with open(path) as f:
        return list(csv.DictReader(f))


def category_from_filename(path):
    name = os.path.basename(path)
    name = re.sub(r"^(reddit_|trends_)", "", name)
    return re.sub(r"\.csv$", "", name)


def main():
    categories = {}
    for path in glob.glob("data/reddit_*.csv"):
        cat = category_from_filename(path)
        rows = load_csv(path)
        categories.setdefault(cat, {})["reddit"] = rows
    for path in glob.glob("data/trends_*.csv"):
        cat = category_from_filename(path)
        rows = load_csv(path)
        categories.setdefault(cat, {})["trends"] = rows

    cards = []
    for cat, data in sorted(categories.items()):
        reddit_rows = data.get("reddit", [])
        trends_rows = data.get("trends", [])
        latest_r = reddit_rows[-1] if reddit_rows else None
        latest_t = trends_rows[-1] if trends_rows else None
        label = (latest_r or latest_t or {}).get("category", cat)

        mentions = int(latest_r["total_mentions"]) if latest_r else 0
        growth = latest_t.get("wow_growth_pct") if latest_t else ""
        growth_val = float(growth) if growth not in ("", None) else 0

        flagged = mentions >= THRESHOLD_MENTIONS or growth_val >= THRESHOLD_GROWTH_PCT
        flag_html = '<span class="flag">READY TO ANALYZE</span>' if flagged else ""

        history_rows = ""
        all_dates = sorted(set([r["date"] for r in reddit_rows] + [r["date"] for r in trends_rows]))
        r_by_date = {r["date"]: r for r in reddit_rows}
        t_by_date = {r["date"]: r for r in trends_rows}
        for d in all_dates[-8:]:
            r = r_by_date.get(d, {})
            t = t_by_date.get(d, {})
            history_rows += (
                f"<tr><td>{d}</td><td>{r.get('total_mentions','-')}</td>"
                f"<td>{t.get('search_index','-')}</td><td>{t.get('wow_growth_pct','-')}</td></tr>"
            )

        cards.append(f"""
        <div class="card">
          <h2>{label} {flag_html}</h2>
          <p class="stats">Latest Reddit mentions: <b>{mentions}</b> &nbsp;|&nbsp;
             Latest search index: <b>{latest_t.get('search_index','-') if latest_t else '-'}</b> &nbsp;|&nbsp;
             WoW search growth: <b>{growth if growth != '' else '-'}%</b></p>
          <table>
            <tr><th>Date</th><th>Reddit mentions</th><th>Search index</th><th>Growth %</th></tr>
            {history_rows}
          </table>
        </div>""")

    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>Whitespace category tracker</title>
<style>
body {{ font-family: -apple-system, Arial, sans-serif; max-width: 900px; margin: 40px auto; padding: 0 16px; color: #222; }}
h1 {{ font-size: 22px; }}
.card {{ border: 1px solid #ddd; border-radius: 8px; padding: 16px 20px; margin-bottom: 20px; }}
.stats {{ color: #444; }}
table {{ border-collapse: collapse; width: 100%; margin-top: 10px; font-size: 14px; }}
th, td {{ border-bottom: 1px solid #eee; padding: 6px 8px; text-align: left; }}
.flag {{ background: #ffedd5; color: #9a3412; font-size: 12px; padding: 3px 8px; border-radius: 4px; margin-left: 8px; }}
.empty {{ color: #888; }}
</style></head>
<body>
<h1>Whitespace category tracker</h1>
<p>Updates automatically every week. Add a new category by editing <code>watchlist.txt</code> in the repo.</p>
{''.join(cards) if cards else '<p class="empty">No data yet - runs weekly, or trigger manually from the Actions tab.</p>'}
</body></html>"""

    with open("docs/index.html", "w") as f:
        f.write(html)
    print("Dashboard written to docs/index.html")


if __name__ == "__main__":
    main()
