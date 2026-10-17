# Brief - 25 categories x 5 cards, refreshed daily at ~6 AM IST

## Layout (repo root)
- `fetch_news.py`  - pulls RSS feeds, dedupes, ranks, summarises, writes `docs/news.json`
- `context.json`   - background/history cards (add `"cat": "<category>"` to tie one to a category)
- `docs/index.html`- the app (served by GitHub Pages)
- `.github/workflows/news.yml` - the daily job

## Setup
1. Upload everything to the repo root (keep the folder structure, including `.github/`).
2. Settings > Pages > Deploy from branch > `main` / `/docs`.
3. Optional: Settings > Secrets and variables > Actions > secret `ANTHROPIC_API_KEY` (needs API credits in the Claude Console). Without it, cards show raw RSS snippets.
4. Actions > "Update news" > Run workflow. Then it runs daily at 00:30 UTC (6:00 AM IST).

## Tuning
- Categories and feeds: the `CATS` dict in `fetch_news.py`. The run log lists every `EMPTY/FAILED` feed - replace those URLs.
- `PER_CAT` (cards per category), `TOP_N` (size of the Top brief), `MAX_AGE_H` (freshness window).
- Change the schedule in `news.yml` (cron is in UTC).
- The bot commits `docs/news.json` daily, so run `git pull` before pushing your own edits.

Only headlines/snippets are used, summaries are rewritten, and every card links to the original article.
