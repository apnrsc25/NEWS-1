# सारांश · Saransh - 25 categories x 15 cards, refreshed daily ~6 AM IST

## Repo layout (upload to repo root)
- `fetch_news.py`   pulls RSS feeds, dedupes, ranks, summarises, writes `docs/news.json`
- `context.json`    background/history cards (add `"cat": "<category>"` to tie one to a category)
- `docs/index.html` the app (GitHub Pages) + `manifest.webmanifest`, `sw.js`, `icon*.png/svg` (install + offline)
- `.github/workflows/news.yml` the daily job (00:30 UTC = 6:00 AM IST)

## Setup
1. Settings > Pages > Deploy from branch > `main` / `/docs`.
2. Optional: Settings > Secrets and variables > Actions > `ANTHROPIC_API_KEY` (needs Console credits). Without it, cards show raw RSS snippets.
3. Actions > "Update news" > Run workflow.

## App features
Top brief (12 stories, ~6 min) · 25 categories x 15 cards · For you (follow topics) · Learn (background cards) · search · save · share · listen · unread tracking · daily streak · text size · blue light/dark theme · installable + works offline.

## Tuning (`fetch_news.py`)
`CATS` (feeds per category; the run log prints every `EMPTY/FAILED` feed), `PER_CAT` (cards per category), `TOP_N`, `MAX_AGE_H`.
Cost: 375 cards = 15 summarising calls/day. Lower `PER_CAT` to cut it.
The bot commits `docs/news.json` daily - run `git pull` before pushing your own edits.
