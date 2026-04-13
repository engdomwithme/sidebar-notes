#!/usr/bin/env python3
"""
sidebar-notes weekly actor news fetcher
Reads people/names.md, queries Google News RSS,
commits weekly/YYYY-MM-DD.md to this repo.
"""

import os
import re
import base64
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime


GH_TOKEN = os.environ["GITHUB_TOKEN"]
REPO = os.environ.get("GITHUB_REPOSITORY", "engdomwithme/sidebar-notes")
HEADERS = {
    "Authorization": f"Bearer {GH_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "sidebar-notes-bot",
}


def gh_get(path):
    url = f"https://api.github.com/repos/{REPO}/contents/{path}"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def gh_put(path, content_str, message, sha=None):
    url = f"https://api.github.com/repos/{REPO}/contents/{path}"
    body = {
        "message": message,
        "content": base64.b64encode(content_str.encode()).decode(),
    }
    if sha:
        body["sha"] = sha
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        url, data=data,
        headers={**HEADERS, "Content-Type": "application/json"},
        method="PUT"
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def parse_actors(md_text):
    names = set()
    for line in md_text.splitlines():
        m = re.match(r'^- (.+?) \(', line.strip())
        if m:
            names.add(m.group(1))
    return sorted(names)


def fetch_news(actor, days=7):
    query = urllib.parse.quote(f'"{actor}"')
    url = f"https://news.google.com/rss/search?q={query}&hl=en&gl=US&ceid=US:en"
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    articles = []
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            root = ET.fromstring(r.read())
        for item in root.findall(".//item"):
            title = item.findtext("title", "").strip()
            link  = item.findtext("link", "").strip()
            pub   = item.findtext("pubDate", "")
            try:
                pub_dt = parsedate_to_datetime(pub)
            except Exception:
                continue
            if pub_dt >= cutoff:
                articles.append({
                    "title": title,
                    "link": link,
                    "date": pub_dt.strftime("%Y-%m-%d"),
                })
    except Exception:
        pass
    return articles


def build_report(actor_news, week_str):
    lines = [f"# Haftalık Oyuncu Haberleri — {week_str}", ""]
    found_any = False
    for actor, articles in sorted(actor_news.items()):
        if not articles:
            continue
        found_any = True
        lines.append(f"## {actor}")
        for a in articles[:5]:
            lines.append(f"- [{a['title']}]({a['link']}) _{a['date']}_")
        lines.append("")
    if not found_any:
        lines.append("_Bu hafta haber bulunamadı._")
    return "\n".join(lines)


def main():
    file_data = gh_get("people/names.md")
    md_text = base64.b64decode(file_data["content"]).decode()
    actors = parse_actors(md_text)
    print(f"{len(actors)} benzersiz oyuncu bulundu.")

    actor_news = {}
    for i, actor in enumerate(actors, 1):
        print(f"[{i}/{len(actors)}] {actor}")
        actor_news[actor] = fetch_news(actor)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    report = build_report(actor_news, today)

    weekly_path = f"weekly/{today}.md"
    try:
        existing = gh_get(weekly_path)
        sha = existing["sha"]
    except Exception:
        sha = None

    gh_put(weekly_path, report, f"weekly: {today} haber özeti", sha)
    print(f"Commit edildi: {weekly_path}")


if __name__ == "__main__":
    main()
