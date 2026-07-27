"""
Reads every CSV in data/ and builds docs/index.html - one dashboard page,
published automatically via GitHub Pages. This is the link you'll open
every week.
"""
import csv
import glob
import os
import re

# ---- threshold: edit this if you want the "ready to look closer" flag
#      to trigger earlier/later ----
THRESHOLD_GROWTH_PCT = 25

os.makedirs("docs", exist_ok=True)


def load_csv(path):
    with open(path) as f:
        return list(csv.DictReader(f))


def category_from_filename(path):
    name = os.path.basename(path)
    name = re.sub(r"^trends_", "", name)
    return re.sub(r"\.csv$", "", name)


def main():
    categories = {}
    for path in glob.glob("data/trends_*.csv"):
        cat = category_from_filename(path)
        categories[cat] = load_csv(path)

    cards = []
    for cat, rows in sorted(categories.items()):
        latest = rows[-1] if rows else None
        label = latest.get("category", cat) if latest else cat

        growth = latest.get("wow_growth_pct") if latest else ""
        growth_val = float(growth) if growth not in ("", None) else 0

        flagged = growth_val >= THRESHOLD_GROWTH_PCT
        flag_html = '<span class="flag">READY TO ANALYZE</span>' if flagged else ""

        history_rows = ""
        for r in rows[-8:]:
            history_rows += (
                f"<tr><td>{r['date']}</td><td>{r.get('search_index','-')}</td>"
                f"<td>{r.get('wow_growth_pct','-')}</td></tr>"
            )

        cards.append(f"""
        <div class="card">
          <h2>{label} {flag_html}</h2>
          <p class="stats">Latest search index: <b>{latest.get('search_index','-') if latest else '-'}</b> &nbsp;|&nbsp;
             WoW search growth: <b>{growth if growth != '' else '-'}%</b></p>
          <table>
            <tr><th>Date</th><th>Search index</th><th>Growth %</th></tr>
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
.btn {{ background: #16a34a; color: #fff; padding: 6px 14px; border-radius: 6px; text-decoration: none; font-size: 14px; }}
.empty {{ color: #888; }}
</style></head>
<body>
<h1>Whitespace category tracker</h1>
<p>Updates automatically every week. Add a new category by editing <code>watchlist.txt</code> in the repo.
&nbsp; <a href="dashboard.xlsx" class="btn">Download Excel</a></p>
{''.join(cards) if cards else '<p class="empty">No data yet - runs weekly, or trigger manually from the Actions tab.</p>'}
</body></html>"""

    with open("docs/index.html", "w") as f:
        f.write(html)
    print("Dashboard written to docs/index.html")


if __name__ == "__main__":
    main()
