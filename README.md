# Whitespace category tracker

One link, updated every Monday, showing Reddit mention volume + Google
search-trend index for every category you're tracking.

## The only thing you ever do
Open `watchlist.txt` in this repo, click the pencil icon (Edit), add your
category on its own line (e.g. `waterless shampoo`), click "Commit changes."
That's it — the tool picks it up automatically (it runs immediately when you
edit this file, and every Monday after that).

## Where your report lives
Once this repo's GitHub Pages is turned on (one-time, see below), your
dashboard link will be:
`https://<your-github-username>.github.io/<repo-name>/`

That page shows, per category: latest Reddit mention count, latest Google
search-interest index, week-over-week growth %, an 8-week history table, and
a "READY TO ANALYZE" flag when a category crosses the threshold (default:
30+ Reddit mentions in a week, or 25%+ search growth week-over-week — both
adjustable in `build_dashboard.py`).

## One-time setup (needs to be done once by whoever has repo admin access)
1. Push this folder to a GitHub repo.
2. Repo Settings → Pages → Source → "GitHub Actions."
3. Repo Settings → Actions → General → Workflow permissions → "Read and
   write permissions" (so the bot can save data back to the repo).
4. Run the workflow once manually from the Actions tab to confirm it works.

No API keys, no Google Cloud account, no Reddit developer account needed —
everything here uses public, no-login data sources.

## About Looker Studio
You mentioned wanting Looker Studio specifically. That's still possible, but
it needs its own Google login regardless of how automated the rest of this
is — Looker Studio only connects to Google-owned data sources (Sheets,
BigQuery, etc.), so there's no way around a one-time Google sign-in for that
piece specifically. If you want it: connect Looker Studio to a Google Sheet,
and I can adapt `collect_reddit.py`/`collect_trends.py` to also write to
that Sheet instead of (or alongside) the CSV files here — just say the word
once you've got a Sheet ready.
