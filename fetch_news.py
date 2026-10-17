"""RSS -> dedupe -> rank -> (optional) LLM summaries -> docs/news.json"""
import feedparser, json, os, re, html, time, datetime as dt
from calendar import timegm

FEEDS = [  # (category, source, url) - verify URLs occasionally; edit freely
 ("World","BBC News","https://feeds.bbci.co.uk/news/world/rss.xml"),
 ("World","Al Jazeera","https://www.aljazeera.com/xml/rss/all.xml"),
 ("World","The Guardian","https://www.theguardian.com/world/rss"),
 ("India","The Hindu","https://www.thehindu.com/news/national/feeder/default.rss"),
 ("India","Indian Express","https://indianexpress.com/section/india/feed/"),
 ("Business","BBC News","https://feeds.bbci.co.uk/news/business/rss.xml"),
 ("Tech","BBC News","https://feeds.bbci.co.uk/news/technology/rss.xml"),
 ("Science","BBC News","https://feeds.bbci.co.uk/news/science_and_environment/rss.xml"),
 ("Health","BBC News","https://feeds.bbci.co.uk/news/health/rss.xml"),
 ("Sports","BBC Sport","https://feeds.bbci.co.uk/sport/rss.xml"),
]
TOTAL, PER_CAT, MAX_AGE_H = 12, 3, 36      # cards per briefing, cap per category, freshness window
MODEL = os.getenv("MODEL", "claude-haiku-5-5")
PROMPT = ("You are a neutral news editor. For each story write: headline (max 90 chars), "
 "summary (2-3 sentences, max 55 words, ONLY facts present in the input - add nothing), "
 "why_it_matters (one plain sentence, max 20 words). "
 "Return ONLY a JSON array of {id, headline, summary, why_it_matters}.\nStories:\n")

clean = lambda t: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html.unescape(t or ""))).strip()
words = lambda t: {w for w in re.findall(r"[a-z0-9]+", t.lower()) if len(w) > 3}

def collect():
    out, now = [], time.time()
    for cat, src, url in FEEDS:
        try:
            for e in feedparser.parse(url).entries[:15]:
                t = e.get("published_parsed") or e.get("updated_parsed")
                ts = timegm(t) if t else now
                if now - ts > MAX_AGE_H * 3600: continue
                out.append(dict(category=cat, source=src, title=clean(e.get("title")),
                                snippet=clean(e.get("summary"))[:400], url=e.get("link", ""), ts=ts))
        except Exception as ex:
            print("feed failed:", src, ex)
    return out

def cluster(items):  # same story from several outlets -> one group
    groups = []
    for it in sorted(items, key=lambda i: -i["ts"]):
        w = words(it["title"])
        for g in groups:
            if len(w & g["w"]) / max(1, len(w | g["w"])) >= 0.5:
                g["srcs"].add(it["source"]); break
        else:
            groups.append(dict(w=w, item=it, srcs={it["source"]}))
    return groups

def pick(groups):
    now, chosen, count = time.time(), [], {}
    for g in groups:
        g["score"] = len(g["srcs"]) * 2 + max(0, 1 - (now - g["item"]["ts"]) / (MAX_AGE_H * 3600))
    for g in sorted(groups, key=lambda g: -g["score"]):
        c = g["item"]["category"]
        if count.get(c, 0) >= PER_CAT: continue
        count[c] = count.get(c, 0) + 1; chosen.append(g)
        if len(chosen) == TOTAL: break
    return chosen

def summarise(chosen):
    base = []
    for i, g in enumerate(chosen):
        it = g["item"]
        base.append(dict(id=i, category=it["category"], headline=it["title"], summary=it["snippet"][:220],
                         why_it_matters="", source=it["source"] + (f" +{len(g['srcs'])-1}" if len(g["srcs"]) > 1 else ""),
                         url=it["url"], published=dt.datetime.fromtimestamp(it["ts"], dt.timezone.utc).isoformat()))
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("No ANTHROPIC_API_KEY - using raw snippets"); return base
    try:
        import anthropic
        src = [dict(id=b["id"], title=b["headline"], snippet=b["summary"]) for b in base]
        msg = anthropic.Anthropic().messages.create(model=MODEL, max_tokens=3000,
              messages=[{"role": "user", "content": PROMPT + json.dumps(src)}])
        for d in json.loads(re.search(r"\[.*\]", msg.content[0].text, re.S).group(0)):
            if isinstance(d.get("id"), int) and 0 <= d["id"] < len(base):
                b = base[d["id"]]
                for k in ("headline", "summary", "why_it_matters"):
                    if d.get(k): b[k] = d[k]
    except Exception as ex:
        print("LLM step failed, using raw snippets:", ex)
    return base

if __name__ == "__main__":
    items = collect()
    if not items:
        raise SystemExit("No items fetched - keeping previous news.json")
    cards = summarise(pick(cluster(items)))
    ctx = json.load(open("context.json")) if os.path.exists("context.json") else []
    os.makedirs("docs", exist_ok=True)
    json.dump(dict(updated=dt.datetime.now(dt.timezone.utc).isoformat(), items=cards, context=ctx),
              open("docs/news.json", "w"), indent=1, ensure_ascii=False)
    print("Wrote", len(cards), "cards")
