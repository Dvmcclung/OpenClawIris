#!/usr/bin/env python3
"""
Iris Knowledge Refresh Script
Runs at 6am and 6pm ET to search for 3 communication improvement insights.
"""
import json
import os
import requests
from datetime import datetime

BRAVE_API_KEY = None
# Load from openclaw.json
try:
    with open(os.path.expanduser("~/.openclaw/openclaw.json")) as f:
        cfg = json.load(f)
    BRAVE_API_KEY = cfg.get("plugins", {}).get("brave-search", {}).get("apiKey") or \
                    cfg.get("brave", {}).get("apiKey") or \
                    os.environ.get("BRAVE_API_KEY")
except Exception:
    BRAVE_API_KEY = os.environ.get("BRAVE_API_KEY")

SEARCH_QUERIES = [
    "executive communication best practices writing clarity",
    "supply chain leadership communication strategies",
    "business writing improve impact audience engagement"
]

OUTPUT_FILE = os.path.expanduser("~/.openclaw/iris-workspace/memory/knowledge-updates.md")


def search(query):
    if not BRAVE_API_KEY:
        return []
    try:
        resp = requests.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers={"Accept": "application/json", "X-Subscription-Token": BRAVE_API_KEY},
            params={"q": query, "count": 3},
            timeout=10
        )
        results = resp.json().get("web", {}).get("results", [])
        return [{"title": r.get("title"), "url": r.get("url"), "desc": r.get("description", "")} for r in results[:2]]
    except Exception as e:
        return [{"title": f"Search error: {e}", "url": "", "desc": ""}]


def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M ET")
    entries = [f"\n## {now} — Knowledge Refresh\n"]

    for i, query in enumerate(SEARCH_QUERIES, 1):
        results = search(query)
        entries.append(f"\n### Search {i}: {query}")
        for r in results:
            entries.append(f"- **{r['title']}** — {r['url']}")
            if r['desc']:
                entries.append(f"  {r['desc'][:200]}")

    with open(OUTPUT_FILE, "a") as f:
        f.write("\n".join(entries) + "\n")

    print(f"Knowledge refresh complete: {now}")


if __name__ == "__main__":
    main()
