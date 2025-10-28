import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
from urllib.parse import urlparse
import json
import os
import yaml

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except Exception:
    PLAYWRIGHT_AVAILABLE = False

from .content_extractor import load_extractor_for_source
import re


def parse_polish_published(s: str):
    """Parse Polish relative/human date strings into datetime when possible.

    Returns datetime on success, otherwise returns original string.
    """
    if not s or not isinstance(s, str):
        return s
    # normalize
    txt = s.replace('\u200b', '').replace('\xa0', ' ').replace('\u00a0', ' ')
    txt = ' '.join(txt.split())
    low = txt.lower()
    now = datetime.now()

    # relative minutes e.g. '5 minut temu', '5 min', '5 min.'
    m = re.search(r"(\d{1,3})\s*(?:min(?:ut(?:y|ę)?)?|min\.?|m)\b", low, flags=re.I)
    if m:
        try:
            return now - timedelta(minutes=int(m.group(1)))
        except Exception:
            pass

    # combined hours + minutes e.g. '1 godz. 16 minut temu'
    m = re.search(r"(\d{1,3})\s*(?:godz(?:in(?:y|ę)?)?|godz\.?)[^\d]*(\d{1,3})\s*(?:min(?:ut(?:y|ę)?)?|min\.?|m)\b", low, flags=re.I)
    if m:
        try:
            hrs = int(m.group(1))
            mins = int(m.group(2))
            return now - timedelta(hours=hrs, minutes=mins)
        except Exception:
            pass

    # relative hours e.g. '2 godziny temu', '2 godz.'
    m = re.search(r"(\d{1,3})\s*(?:godz(?:in(?:y|ę)?)?|godz\.?)\b", low, flags=re.I)
    if m:
        try:
            return now - timedelta(hours=int(m.group(1)))
        except Exception:
            pass

    # relative seconds e.g. '30 sekund temu', '30 sek.'
    m = re.search(r"(\d{1,3})\s*(?:sek(?:und(?:y)?)?|sek\.?|s)\b", low, flags=re.I)
    if m:
        try:
            return now - timedelta(seconds=int(m.group(1)))
        except Exception:
            pass

    # Dzisiaj / dziś
    if 'dzis' in low or 'dziś' in low:
        tm = re.search(r"(\d{1,2}):(\d{2})", txt)
        if tm:
            return datetime(now.year, now.month, now.day, int(tm.group(1)), int(tm.group(2)))
        return datetime(now.year, now.month, now.day)

    # Wczoraj
    if 'wczoraj' in low:
        tm = re.search(r"(\d{1,2}):(\d{2})", txt)
        d = now - timedelta(days=1)
        if tm:
            return datetime(d.year, d.month, d.day, int(tm.group(1)), int(tm.group(2)))
        return datetime(d.year, d.month, d.day)

    # explicit day + month + optional year + time e.g. '21 października (10:57)'
    months = {
        'stycznia':1, 'styczen':1, 'styczeń':1,
        'lutego':2, 'luty':2,
        'marca':3, 'marzec':3,
        'kwietnia':4, 'kwiecien':4, 'kwiecień':4,
        'maja':5, 'maj':5,
        'czerwca':6, 'czerwiec':6,
        'lipca':7, 'lipiec':7,
        'sierpnia':8, 'sierpien':8, 'sierpień':8,
        'wrzesnia':9, 'wrzesień':9, 'września':9, 'wrzesien':9,
        'października':10, 'pazdziernika':10, 'pazdziernik':10, 'październik':10,
        'listopada':11, 'listopad':11,
        'grudnia':12, 'grudzien':12, 'grudzień':12
    }
    m = re.search(r"(\d{1,2})\s+([\wąćęłńóśżźĄĆĘŁŃÓŚŻŹ]+)\s*(\d{4})?.*?(\d{1,2}):(\d{2})", txt, flags=re.I|re.U)
    if m:
        try:
            day = int(m.group(1))
            mon_name = m.group(2).lower()
            year = int(m.group(3)) if m.group(3) else now.year
            hour = int(m.group(4)); minute = int(m.group(5))
            mon = months.get(mon_name)
            if mon:
                return datetime(year, mon, day, hour, minute)
        except Exception:
            pass

    # fallback
    return s


def fetch_rss(url):
    d = feedparser.parse(url)
    for entry in d.entries:
        yield {
            "title": entry.get("title"),
            "url": entry.get("link"),
            "published": entry.get("published_parsed")
        }


def fetch_html_playwright(url, timeout_ms=30000):
    if not PLAYWRIGHT_AVAILABLE:
        raise RuntimeError('Playwright not installed')
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=timeout_ms)
        content = page.content()
        browser.close()
        return content


def fetch_html_with_method(url, method='auto'):
    """Fetch HTML using a specified method.
    method: 'requests', 'playwright', or 'auto' (try requests, fallback to playwright)
    """
    method = (method or 'auto').lower()
    if method == 'playwright':
        return fetch_html_playwright(url)
    if method == 'requests':
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9,pl;q=0.8'
            }
            r = requests.get(url, timeout=10, headers=headers)
            r.raise_for_status()
            # Some sites may send bytes that requests decodes with the wrong
            # encoding. Decode explicitly using apparent_encoding when available
            # (fallback to detected r.encoding or utf-8) to avoid mojibake
            # (e.g. Polish characters turning into \u00c4\u0099 sequences).
            enc = getattr(r, 'apparent_encoding', None) or r.encoding or 'utf-8'
            try:
                return r.content.decode(enc, errors='replace')
            except Exception:
                # worst-case fallback to requests' .text
                return r.text
        except Exception:
            # allow fallback to playwright if available
            if PLAYWRIGHT_AVAILABLE:
                return fetch_html_playwright(url)
            raise
    # auto
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9,pl;q=0.8'
        }
        r = requests.get(url, timeout=10, headers=headers)
        r.raise_for_status()
        # See note above: prefer decoding from bytes using apparent_encoding
        enc = getattr(r, 'apparent_encoding', None) or r.encoding or 'utf-8'
        try:
            text = r.content.decode(enc, errors='replace')
        except Exception:
            text = r.text
        if len(text) < 1000 and PLAYWRIGHT_AVAILABLE:
            return fetch_html_playwright(url)
        return text
    except Exception:
        if PLAYWRIGHT_AVAILABLE:
            return fetch_html_playwright(url)
        raise


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

    # image extraction: og:image, twitter:image
    image_url = None
    og_img = soup.find('meta', property='og:image')
    if og_img and og_img.get('content'):
        image_url = og_img.get('content')
    if not image_url:
        tw_img = soup.find('meta', attrs={'name': 'twitter:image'})
        if tw_img and tw_img.get('content'):
            image_url = tw_img.get('content')

    content = None
    # support extractor-provided selector(s) (str or list)
    selectors = []
    if extractor_config and extractor_config.get("content_css"):
        cfg_sel = extractor_config.get("content_css")
        if isinstance(cfg_sel, str):
            selectors = [cfg_sel]
        elif isinstance(cfg_sel, (list, tuple)):
            selectors = list(cfg_sel)

    # common fallback selectors for article body
    fallback_selectors = [
        'article',
        'div[itemprop="articleBody"]',
        'div.article__body',
        'div.article-body',
        'div#articleBody',
        'div.content',
        'main article'
    ]

    tried = selectors + fallback_selectors

    def _clean_element(el):
        # remove unwanted nodes inside article element
        for bad in el.select('script, style, .cookie, .consent, .acceptance, .promo, .newsletter, .newsletter-box, .breadcrumbs, .related, .related-articles, .read-more, .comments, .advertisement, aside, footer'):
            try:
                bad.decompose()
            except Exception:
                pass

    def _looks_like_boilerplate(text):
        if not text:
            return True
        low = text.lower()
        boiler_phrases = ['korzystanie z portalu', 'polityka cookies', 'copyright', 'wszystkie prawa zastrzeżone', 'skorzystaj z naszego bota', 'regulamin']
        for p in boiler_phrases:
            if p in low:
                return True
        return False

    for sel in tried:
        try:
            el = soup.select_one(sel)
        except Exception:
            el = None
        if not el:
            continue
        _clean_element(el)
        text = el.get_text(separator='\n', strip=True)
        # skip very short or boilerplate-only elements
        if len(text) < 200 and _looks_like_boilerplate(text):
            continue
        # accept this as content
        content = text
        break

    if not content:
        # fallback: aggregate meaningful <p> paragraphs while filtering boilerplate/short ones
        ps = soup.find_all('p')
        parts = []
        for p in ps:
            t = p.get_text(strip=True)
            if not t:
                continue
            if len(t) < 50:
                # skip tiny paragraphs that often are nav/credits
                continue
            if _looks_like_boilerplate(t):
                continue
            parts.append(t)
        content = "\n\n".join(parts)

    # published extraction: try common meta tags or <time datetime=>
    published = None
    
    def _clean_date_text(s: str) -> str:
        if not s:
            return s
        # remove invisible chars and normalize spaces
        s = s.replace('\u200b', '').replace('\xa0', ' ')
        s = s.replace('\u00a0', ' ')
        return ' '.join(s.split())

    def _parse_polish_published(s: str):
        """Try to parse Polish relative and human-friendly date strings into datetime.

        Handles examples like:
        - '5 minut temu', '2 godziny temu'
        - 'Dzisiaj, 10:57' / 'dzisiaj 10:57'
        - 'Wczoraj, 10:57' -> yesterday at time
        - '21 października (10:57)' -> parse day/month and time
        Returns datetime or original string on failure.
        """
        if not s or not isinstance(s, str):
            return s
        s0 = _clean_date_text(s)
        low = s0.lower()
        now = datetime.now()
        import re

        # relative minutes e.g. '5 minut temu', '5 min', '5 min.'
        m = re.search(r"(\d{1,3})\s*(?:min(?:ut(?:y|ę)?)?|min\.?|m)\b", low)
        if m:
            try:
                return now - timedelta(minutes=int(m.group(1)))
            except Exception:
                pass

        # relative hours e.g. '2 godziny temu', '2 godz.', '2 godz'
        m = re.search(r"(\d{1,3})\s*(?:godz(?:in(?:y|ę)?)?|godz\.?)\b", low)
        if m:
            try:
                return now - timedelta(hours=int(m.group(1)))
            except Exception:
                pass

        # relative seconds e.g. '30 sekund temu', '30 sek.', '30 sec'
        m = re.search(r"(\d{1,3})\s*(?:sek(?:und(?:y)?)?|sek\.?|s)\b", low)
        if m:
            try:
                return now - timedelta(seconds=int(m.group(1)))
            except Exception:
                pass

        # Dzisiaj / dziś
        if 'dzis' in low or 'dziś' in low:
            tm = re.search(r"(\d{1,2}):(\d{2})", s0)
            if tm:
                return datetime(now.year, now.month, now.day, int(tm.group(1)), int(tm.group(2)))
            return datetime(now.year, now.month, now.day)

        # Wczoraj
        if 'wczoraj' in low:
            tm = re.search(r"(\d{1,2}):(\d{2})", s0)
            d = now - timedelta(days=1)
            if tm:
                return datetime(d.year, d.month, d.day, int(tm.group(1)), int(tm.group(2)))
            return datetime(d.year, d.month, d.day)

        # explicit day + month + optional year + time e.g. '21 października (10:57)'
        # map Polish month names (genitive and nominative)
        months = {
            'stycznia':1, 'styczeń':1, 'styczen':1,
            'lutego':2, 'luty':2,
            'marca':3, 'marzec':3,
            'kwietnia':4, 'kwiecien':4, 'kwietnia':4,
            'maja':5, 'maj':5,
            'czerwca':6, 'czerwiec':6,
            'lipca':7, 'lipiec':7,
            'sierpnia':8, 'sierpien':8,
            'września':9, 'wrzesien':9, 'września':9,
            'października':10, 'pazdziernika':10, 'październik':10, 'pazdziernik':10,
            'listopada':11, 'listopad':11,
            'grudnia':12, 'grudzien':12
        }
        m = re.search(r"(\d{1,2})\s+([\wąćęłńóśżźĄĆĘŁŃÓŚŻŹ]+)\s*(\d{4})?.*?(\d{1,2}):(\d{2})", s0, flags=re.I|re.U)
        if m:
            try:
                day = int(m.group(1))
                mon_name = m.group(2).lower()
                year = int(m.group(3)) if m.group(3) else now.year
                hour = int(m.group(4)); minute = int(m.group(5))
                mon = months.get(mon_name)
                if mon:
                    return datetime(year, mon, day, hour, minute)
            except Exception:
                pass

        # fallback: return original string
        return s
    # Try several common meta attributes used by different portals. Prefer
    # itemprop=datePublished (used by RMF) because it contains ISO string.
    meta = None
    # itemprop (e.g. <meta itemprop="datePublished" content="2025-10-21T10:57:00"/>)
    meta = soup.find('meta', attrs={'itemprop': 'datePublished'}) or soup.find('meta', attrs={'itemprop': 'dateModified'})
    # OpenGraph / article properties
    if not meta:
        meta = soup.find('meta', property='article:published_time') or soup.find('meta', property='og:article:published_time') or soup.find('meta', attrs={'name': 'article:published_time'})
    if not meta:
        meta = soup.find('meta', attrs={'name': 'og:published_time'}) or soup.find('meta', attrs={'name': 'published_time'})
    # generic date meta names
    if not meta:
        meta = soup.find('meta', attrs={'name': 'date'}) or soup.find('meta', attrs={'name': 'pubdate'})

    if meta and meta.get('content'):
        val = meta.get('content').strip()
        try:
            # Accept ISO-like strings; handle trailing Z as UTC
            if val.endswith('Z'):
                published = datetime.fromisoformat(val.replace('Z', '+00:00'))
            else:
                published = datetime.fromisoformat(val)
        except Exception:
            # leave raw value for fallback
            # try to parse polish/human-readable date strings
            parsed = _parse_polish_published(val)
            published = parsed
    else:
        # fallback to <time datetime=> or visible date elements
        time_tag = soup.find('time')
        if time_tag and time_tag.get('datetime'):
            try:
                published = datetime.fromisoformat(time_tag.get('datetime'))
            except Exception:
                published = time_tag.get('datetime')
        else:
            # try to find elements commonly used by RMF: div.article-date or div.date
            possible = soup.select_one('.article-date') or soup.select_one('.date') or soup.select_one('.czas')
            if possible:
                txt = possible.get_text(' ', strip=True)
                published = _parse_polish_published(txt)

    return content, title, published, image_url


def _format_datetime_for_json(val):
    """Normalize various date representations to an ISO 8601 string or return None/string as-is.

    Handles:
    - datetime -> isoformat()
    - time.struct_time -> convert to datetime then isoformat()
    - other strings -> return as-is (optionally try iso parsing)
    - None -> None
    """
    if val is None:
        return None
    try:
        # datetime instance
        if isinstance(val, datetime):
            return val.isoformat()
    except Exception:
        pass
    try:
        # struct_time from feedparser (time.struct_time)
        import time as _time
        if hasattr(val, 'tm_year') and hasattr(val, 'tm_hour'):
            # best-effort convert
            try:
                ts = _time.mktime(val)
                return datetime.fromtimestamp(ts).isoformat()
            except Exception:
                return str(val)
    except Exception:
        pass
    # fallback: if it's already a string, try to keep it
    try:
        if isinstance(val, str):
            # try to normalize if it's ISO-like
            try:
                return datetime.fromisoformat(val).isoformat()
            except Exception:
                return val
    except Exception:
        pass
    # other types: stringify
    try:
        return str(val)
    except Exception:
        return None


def find_existing_scraped_by_url(url):
    """Search reports/scraped for a file with matching URL. Return (id, path) or (None, None)."""
    scraped_dir = os.path.join(os.path.dirname(__file__), '..', 'reports', 'scraped')
    scraped_dir = os.path.normpath(scraped_dir)
    if not os.path.isdir(scraped_dir):
        return None, None
    for fname in os.listdir(scraped_dir):
        if not fname.endswith('.json'):
            continue
        path = os.path.join(scraped_dir, fname)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if data.get('url') == url:
                return data.get('id'), path
        except Exception:
            continue
    return None, None


def save_article_file(rec):
    """Save article summary JSON to reports/scraped and return generated id and path.
    Does not touch DB.
    """
    ensure_reports_dir()
    now = datetime.now()
    new_id = int(now.timestamp() * 1000)
    article_dict = {
        'id': new_id,
        'source': rec.get('source'),
        'title': rec.get('title'),
        'url': rec.get('url'),
        'published': _format_datetime_for_json(rec.get('published')),
        'fetched_at': _format_datetime_for_json(now),
        'content': rec.get('content') or '',
        'content_preview': (rec.get('content') or '')[:300],
        'image_url': rec.get('image_url')
    }
    path = write_summary_json(article_dict)
    return new_id, path


def ensure_reports_dir():
    os.makedirs("reports/scraped", exist_ok=True)
    os.makedirs("reports/analysis", exist_ok=True)


def article_row_to_dict(row):
    if not row:
        return None
    keys = ['id','source','title','url','published','fetched_at','content','score','label','reasons','similarity','analyzed_at']
    return dict(zip(keys, row))


def write_summary_json(article_dict):
    ensure_reports_dir()
    id_ = article_dict.get('id')
    # Zapisujemy pełną treść w pliku JSON oraz krótkie preview do szybkiego podglądu w terminalu
    summary = {
         'id': id_,
         'source': article_dict.get('source'),
         'title': article_dict.get('title'),
         'url': article_dict.get('url'),
         'published': article_dict.get('published'),
         'fetched_at': article_dict.get('fetched_at'),
         'content': article_dict.get('content') or '',
         'content_preview': (article_dict.get('content') or '')[:300],
         'image_url': article_dict.get('image_url')
     }
    # Use only the id in the filename (avoid timestamp). If file exists, add numeric suffix to avoid overwriting.
    filename = f"scraped_{id_}.json"
    path = os.path.join("reports", "scraped", filename)
    if os.path.exists(path):
        i = 1
        while True:
            alt = f"scraped_{id_}_{i}.json"
            alt_path = os.path.join("reports", "scraped", alt)
            if not os.path.exists(alt_path):
                filename = alt
                path = alt_path
                break
            i += 1
    with open(path, 'w', encoding='utf-8') as f:
         json.dump(summary, f, ensure_ascii=False, indent=2)
    return path


def write_analysis_json(analysis_dict):
    ensure_reports_dir()
    id_ = analysis_dict.get('id')
    # Use only the id in the filename (avoid timestamp). If file exists, add numeric suffix to avoid overwriting.
    filename = f"analysis_{id_}.json"
    path = os.path.join("reports", "analysis", filename)
    if os.path.exists(path):
        i = 1
        while True:
            alt = f"analysis_{id_}_{i}.json"
            alt_path = os.path.join("reports", "analysis", alt)
            if not os.path.exists(alt_path):
                filename = alt
                path = alt_path
                break
            i += 1
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(analysis_dict, f, ensure_ascii=False, indent=2)
    return path


def run_scraper():
    cfg = yaml.safe_load(open("config.yaml"))
    sources = cfg.get("sources", [])
    for s in sources:
        if not s.get("enabled", True):
            continue
        extractor = load_extractor_for_source(s["name"])
        fetch_method = s.get("fetch_method", "auto")

        # If source is configured to ask user for URL(s), prompt now
        if s.get("ask_for_url", False):
            prompt = f"Podaj link(i) do artykułu dla '{s['name']}' (oddziel przecinkami jeśli więcej niż jeden), lub wpisz 'skip': "
            user_input = input(prompt).strip()
            if not user_input or user_input.lower() == 'skip':
                continue
            urls = [u.strip() for u in user_input.split(",") if u.strip()]
            for url in urls:
                try:
                    # skip if URL already exists as a scraped file
                    eid, existing_path = find_existing_scraped_by_url(url)
                    if eid:
                        print(f'Pomijam — URL już zapisany w plikach: {url} (id={eid}, file={existing_path})')
                        continue
                    html = fetch_html_with_method(url, fetch_method)
                    content, title, published, image_url = extract_content_and_title(html, extractor)
                    new_id, path = save_article_file({
                        "source": s["name"],
                        "title": title,
                        "url": url,
                        "content": content,
                        "published": published or datetime.now(),
                        "image_url": image_url
                    })
                    print(f"Zescrapowano: {url} -> zapisano plik {path}")
                except Exception as e:
                    print(f"Błąd pobierania {url} dla {s['name']}: {e}")
            continue

        # Listing page scraping (collect article links from a listing page)
        if s.get("scrape_listing", False) and s.get("url"):
            list_url = s.get("url")
            try:
                html = fetch_html_with_method(list_url, fetch_method)
                soup = BeautifulSoup(html, "lxml")
                base_host = urlparse(list_url).netloc
                links = set()
                # Support per-source URL pattern to identify article links (regex string in config.yaml)
                pattern = s.get('article_url_pattern')

                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if href.startswith('//'):
                        href = 'https:' + href
                    elif href.startswith('/'):
                        href = f"{urlparse(list_url).scheme}://{base_host}{href}"
                    if not href.startswith('http'):
                        continue
                    # only same-host links
                    if urlparse(href).netloc != base_host:
                        continue
                    if href == list_url:
                        continue
                    low = href.lower()
                    # basic blacklist to skip common non-article sections
                    if any(x in low for x in ['/tylko-w-rmf24', '/galeria', '/wideo', '/video', '/tag/', '/tag-']):
                        continue
                    # skip pagination/listing links (nPack)
                    if ',npack,' in low:
                        continue
                    # if a per-source regex is provided, require it to match; if it doesn't,
                    # accept articles containing ',nId,' as a safe fallback (RMF article IDs)
                    if pattern:
                        try:
                            import re
                            if not re.search(pattern, href):
                                # fallback: accept URLs containing ',nId,' even if regex failed
                                if ',nid,' in low:
                                    pass
                                else:
                                    continue
                        except Exception:
                            pass
                    links.add(href.split('#')[0])

                print(f"Znaleziono {len(links)} linków na stronie listingu {list_url}")
                for url in sorted(links):
                    try:
                        eid, existing_path = find_existing_scraped_by_url(url)
                        if eid:
                            print(f'Pomijam — URL już zapisany: {url}')
                            continue
                        article_html = fetch_html_with_method(url, fetch_method)
                        content, title, published, image_url = extract_content_and_title(article_html, extractor)
                        # if configured, only keep articles published today
                        if s.get("only_today", False) and isinstance(published, datetime):
                            if published.date() != datetime.now().date():
                                print(f"Pominięto (nie z dzisiaj): {url} (published={published})")
                                continue
                        new_id, path = save_article_file({
                            "source": s["name"],
                            "title": title,
                            "url": url,
                            "content": content,
                            "published": published or datetime.now(),
                            "image_url": image_url
                        })
                        print(f"Zescrapowano: {url} -> zapisano plik {path}")
                    except Exception as e:
                        print(f"Błąd pobierania z listingu {url} dla {s['name']}: {e}")
            except Exception as e:
                print(f"Błąd pobierania listingu {list_url} dla {s['name']}: {e}")
            continue

        # RSS handling stays the same but respects fetch_method when fetching html
        if s.get("rss") and s.get("enabled", True):
            for item in fetch_rss(s["rss"]):
                url = item["url"]
                try:
                    # skip if URL already exists as a scraped file
                    eid, existing_path = find_existing_scraped_by_url(url)
                    if eid:
                        print(f'Pomijam — URL już zapisany w plikach: {url} (id={eid}, file={existing_path})')
                        continue
                    html = fetch_html_with_method(url, fetch_method)
                    content, title, published, image_url = extract_content_and_title(html, extractor)
                    new_id, path = save_article_file({
                        "source": s["name"],
                        "title": item.get("title") or title,
                        "url": url,
                        "content": content,
                        "published": published or item.get("published"),
                        "image_url": image_url
                    })
                    print(f"Zescrapowano: {url} -> zapisano plik {path}")
                except Exception as e:
                    print(f"Błąd pobierania RSS item {url} dla {s['name']}: {e}")
        else:
            # single URL from config (if present)
            url = s.get("url")
            if not url:
                continue
            try:
                # skip if URL already exists as a scraped file
                eid, existing_path = find_existing_scraped_by_url(url)
                if eid:
                    print(f'Pomijam — URL już zapisany w plikach: {url} (id={eid}, file={existing_path})')
                    continue
                html = fetch_html_with_method(url, fetch_method)
                content, title, published, image_url = extract_content_and_title(html, extractor)
                new_id, path = save_article_file({
                    "source": s["name"],
                    "title": title,
                    "url": url,
                    "content": content,
                    "published": published or datetime.now(),
                    "image_url": image_url
                })
                print(f"Zescrapowano: {url} -> zapisano plik {path}")
            except Exception as e:
                print(f"Błąd pobierania {url} dla {s['name']}: {e}")


def fetch_and_save_url(url, source_name='CLI', fetch_method='auto'):
    """Pobierz pojedynczy URL i zapisz artykuł do pliku JSON. Zwraca dict {id:int, existed:bool, path: str} lub None przy błędzie.

    When called from interactive UI (source_name default 'CLI'), try to infer the real
    portal/source name by matching the URL against entries in config.yaml (by host). If
    that fails, attempt to read site name from HTML meta tags (e.g. og:site_name). As a
    last resort, fall back to the hostname.
    """
    # do not fetch if URL already exists as a scraped file
    eid, existing_path = find_existing_scraped_by_url(url)
    if eid:
        print(f'URL już istnieje w plikach: {url} (id={eid}, file={existing_path}) — pomijam pobieranie')
        return {"id": int(eid), "existed": True, "path": existing_path}

    # Try to infer source name from config by matching host
    inferred_source = None
    try:
        cfg = yaml.safe_load(open('config.yaml'))
        sources = cfg.get('sources', []) if isinstance(cfg, dict) else []
        url_host = urlparse(url).netloc.lower()
        if url_host.startswith('www.'):
            url_host = url_host[4:]
        for s in sources:
            su = s.get('url')
            if not su:
                continue
            try:
                shost = urlparse(su).netloc.lower()
                if shost.startswith('www.'):
                    shost = shost[4:]
            except Exception:
                shost = ''
            if shost and shost == url_host:
                inferred_source = s.get('name')
                break
    except Exception:
        inferred_source = None

    # Prefer inferred_source when available for extractor selection
    extractor = None
    try:
        extractor = load_extractor_for_source(inferred_source or source_name)
    except Exception:
        extractor = None

    try:
        html = fetch_html_with_method(url, fetch_method)

        # If we haven't inferred source yet, try to get site name from HTML meta
        save_source = inferred_source
        if not save_source:
            try:
                soup = BeautifulSoup(html, 'lxml')
                og_site = soup.find('meta', property='og:site_name') or soup.find('meta', attrs={'name': 'application-name'})
                if og_site and og_site.get('content'):
                    save_source = og_site.get('content').strip()
                else:
                    # fallback to hostname
                    save_source = urlparse(url).netloc
                    if save_source.startswith('www.'):
                        save_source = save_source[4:]
            except Exception:
                save_source = urlparse(url).netloc
                if save_source.startswith('www.'):
                    save_source = save_source[4:]

        content, title, published, image_url = extract_content_and_title(html, extractor)
        # Use save_source if we have it, else fall back to provided source_name
        final_source = save_source or source_name

        new_id, path = save_article_file({
            "source": final_source,
            "title": title,
            "url": url,
            "content": content,
            "published": published or datetime.now(),
            "image_url": image_url
        })
        print(f"Zescrapowano: {url} -> zapisano plik {path}")
        return {"id": int(new_id), "existed": False, "path": path}
    except Exception as e:
        print(f"Błąd pobierania {url} dla {source_name}: {e}")
        return None


def scrape_listing_for_source(source_name):
    """Scrape listing page for a single source defined in config.yaml.
    Returns a list of result dicts: {source, url, id, path, skipped:bool, reason:str}
    """
    try:
        cfg = yaml.safe_load(open("config.yaml"))
    except Exception as e:
        raise RuntimeError(f'Nie można wczytać config.yaml: {e}')
    sources = cfg.get('sources', [])
    # find source (case-insensitive by name)
    target = None
    for s in sources:
        if s.get('name', '').lower() == source_name.lower():
            target = s
            break
    if not target:
        raise ValueError(f'Źródło nie znalezione w config.yaml: {source_name}')
    if not target.get('scrape_listing') or not target.get('url'):
        raise ValueError(f'Źródło {source_name} nie ma ustawionej opcji scrape_listing lub url')

    fetch_method = target.get('fetch_method', 'auto')
    list_url = target.get('url')
    try:
        html = fetch_html_with_method(list_url, fetch_method)
    except Exception as e:
        raise RuntimeError(f'Błąd pobierania listingu {list_url}: {e}')

    soup = BeautifulSoup(html, 'lxml')
    base_host = urlparse(list_url).netloc
    links = set()
    # Support per-source URL pattern to identify article links (regex string in config.yaml)
    pattern = None
    try:
        pattern = target.get('article_url_pattern')
    except Exception:
        pattern = None

    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.startswith('//'):
            href = 'https:' + href
        elif href.startswith('/'):
            href = f"{urlparse(list_url).scheme}://{base_host}{href}"
        if not href.startswith('http'):
            continue
        # only same-host links
        if urlparse(href).netloc != base_host:
            continue
        if href == list_url:
            continue
        low = href.lower()
        # basic blacklist to skip common non-article sections
        if any(x in low for x in ['/tylko-w-rmf24', '/galeria', '/wideo', '/video', '/tag/', '/tag-']):
            continue
        # if a per-source regex is provided, require it to match
        if pattern:
            try:
                import re
                if not re.search(pattern, href):
                    continue
            except Exception:
                pass
        links.add(href.split('#')[0])

    results = []
    for url in sorted(links):
        rec = {'source': source_name, 'url': url, 'id': None, 'path': None, 'skipped': False, 'reason': None}
        try:
            eid, existing_path = find_existing_scraped_by_url(url)
            if eid:
                rec['skipped'] = True
                rec['reason'] = f'URL already exists (id={eid})'
                rec['id'] = int(eid)
                rec['path'] = existing_path
                results.append(rec)
                continue
            article_html = fetch_html_with_method(url, fetch_method)
            content, title, published, image_url = extract_content_and_title(article_html, load_extractor_for_source(source_name))
            # if configured, only keep articles published today
            if target.get('only_today', False) and isinstance(published, datetime):
                if published.date() != datetime.now().date():
                    rec['skipped'] = True
                    rec['reason'] = f'Not today (published={published})'
                    results.append(rec)
                    continue
            new_id, path = save_article_file({
                'source': source_name,
                'title': title,
                'url': url,
                'content': content,
                'published': published or datetime.now(),
                'image_url': image_url
            })
            rec['id'] = int(new_id)
            rec['path'] = path
            results.append(rec)
        except Exception as e:
            rec['skipped'] = True
            rec['reason'] = f'Error: {e}'
            results.append(rec)
    return results
