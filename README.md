# Brief - setup (about 10 minutes)
1. Create a GitHub repo and upload everything in this folder (keep the structure, including `.github/`).
2. Repo > Settings > Secrets and variables > Actions > New secret: `ANTHROPIC_API_KEY` (optional; without it cards use raw RSS snippets).
3. Repo > Settings > Pages > Deploy from branch > `main` / `/docs`.
4. Actions tab > "Update news" > Run workflow. It then refreshes hourly.
5. Open your Pages URL. The app loads `docs/news.json`, falling back to sample stories if it is missing.

Customise: feeds, TOTAL (cards per day) and PER_CAT in `fetch_news.py`; explainer cards in `context.json`.
Respect each outlet's terms: only headlines/snippets are used, summaries are rewritten, and every card links to the original.
