import feedparser
import requests
from bs4 import BeautifulSoup
import duckdb
import yaml
from datetime import datetime
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

from .core.storage import init_db, save_article
from .content_extractor import load_extractor_for_source


def fetch_rss(url):
    d = feedparser.parse(url)
    for entry in d.entries:
        yield {
            "title": entry.get("title"),
            "url": entry.get("link"),
            "published": entry.get("published_parsed")
        }


def fetch_html_playwright(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=30000)
        content = page.content()
        browser.close()
        return content


def fetch_html(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        text = r.text
        if len(text) < 1000:  # fallback heuristic
            return fetch_html_playwright(url)
        return text
    except Exception:
        # fallback to playwright
        return fetch_html_playwright(url)


def extract_content_and_title(html, extractor_config=None):
    soup = BeautifulSoup(html, "lxml")
    # title extraction: og:title, twitter:title, <title>
    title = None
    og = soup.find('meta', property='og:title')
    if og and og.get('content'):
        title = og.get('content')
    if not title:
        tw = soup.find('meta', attrs={'name': 'twitter:title'})
        if tw and tw.get('content'):
            title = tw.get('content')
    if not title and soup.title:
        title = soup.title.string.strip()

    content = None
    if extractor_config and extractor_config.get("content_css"):
        el = soup.select_one(extractor_config["content_css"])
        content = el.get_text(strip=True) if el else None
    if not content:
        p = soup.find_all("p")
        content = "\n".join([x.get_text(strip=True) for x in p])
    return content, title


def run_scraper():
    cfg = yaml.safe_load(open("config.yaml"))
    sources = cfg.get("sources", [])
    init_db()
    for s in sources:
        if not s.get("enabled", True):
            continue
        extractor = load_extractor_for_source(s["name"])
        if s.get("rss"):
            for item in fetch_rss(s["rss"]):
                url = item["url"]
                html = fetch_html(url)
                content, title = extract_content_and_title(html, extractor)
                save_article({
                    "source": s["name"],
                    "title": item.get("title") or title,
                    "url": url,
                    "content": content,
                    "published": datetime.now()
                })
        else:
            # single URL
            url = s.get("url")
            html = fetch_html(url)
            content, title = extract_content_and_title(html, extractor)
            save_article({
                "source": s["name"],
                "title": title,
                "url": url,
                "content": content,
                "published": datetime.now()
            })
