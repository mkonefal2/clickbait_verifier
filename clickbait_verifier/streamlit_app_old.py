import streamlit as st
import glob
import json
import os
import yaml
import textwrap
import html
from datetime import datetime
from collections import defaultdict
from glob import glob as glob_files
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


@st.cache_data(show_spinner=False)
def fetch_image_from_page(url: str) -> str | None:
    """Try to retrieve a representative image URL from a web page without saving any files.
    Returns absolute image URL or None.
    Caching avoids repeated network requests for the same URL.
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible)"}
        resp = requests.get(url, headers=headers, timeout=6)
        if resp.status_code != 200:
            return None
        soup = BeautifulSoup(resp.text, "lxml")
        # try common meta tags
        meta_props = ["og:image", "twitter:image", "image", "og:image:url"]
        for prop in meta_props:
            m = soup.find("meta", property=prop) or soup.find("meta", attrs={"name": prop})
            if m:
                val = m.get("content") or m.get("value")
                if val:
                    return urljoin(resp.url, val)
        # link rel image_src
        link = soup.find("link", rel=lambda x: x and "image_src" in x)
        if link and link.get("href"):
            return urljoin(resp.url, link["href"])
        # pick a large image from <img> elements (heuristic)
        imgs = soup.find_all("img", src=True)
        if imgs:
            best = None
            best_area = 0
            for img in imgs:
                src = img.get("src")
                if not src or src.startswith("data:"):
                    continue
                full = urljoin(resp.url, src)
                w = img.get("width")
                h = img.get("height")
                try:
                    def render_feed(max_items: int = 10):
                        """Renderuje prosty feed artykułów (bez sekcji dolnych i bez selectbox).
                        Grupuje artykuły według dat (jedna data nagłówkowa na dzień), pokazuje maksymalnie max_items.
                        """
                        candidates = []
                        for p in analysis_files + scraped_files:
                            try:
                                m = os.path.getmtime(p)
                            except Exception:
                                m = 0
                            candidates.append((m, p))
                        candidates.sort(reverse=True)

                        items = []
                        for _, p in candidates:
                            if len(items) >= max_items:
                                break
                            data = _load_json_if_exists(p)
                            if not data:
                                continue
                            is_analysis = os.path.basename(p).startswith('analysis_')
                            article = {
                                'title': None,
                                'source': None,
                                'url': None,
                                'score': None,
                                'label': None,
                                'image': None,
                                'mtime': datetime.fromtimestamp(os.path.getmtime(p)) if os.path.exists(p) else None,
                            }
                            if is_analysis:
                                a = data
                                article['title'] = a.get('title') or '-'
                                article['source'] = a.get('source')
                                article['url'] = a.get('url')
                                article['score'] = a.get('score')
                                article['label'] = a.get('label')
                                # try to find scraped file for image
                                try:
                                    if a.get('id') is not None:
                                        spattern = os.path.join(SCRAPED_DIR, f"scraped_{a.get('id')}*.json")
                                        s_matches = sorted(glob_files(spattern))
                                        if s_matches:
                                            sdata = _load_json_if_exists(s_matches[-1]) or {}
                                            meta = sdata.get('meta') if isinstance(sdata.get('meta'), dict) else {}
                                            article['image'] = sdata.get('lead_image_url') or sdata.get('image') or meta.get('og:image') or meta.get('twitter:image')
                                except Exception:
                                    pass
                            else:
                                s = data
                                article['title'] = s.get('title') or os.path.basename(p)
                                article['source'] = s.get('source')
                                article['url'] = s.get('url')
                                meta = s.get('meta') if isinstance(s.get('meta'), dict) else {}
                                article['image'] = s.get('lead_image_url') or s.get('image') or meta.get('og:image') or meta.get('twitter:image')

                            # if no image yet, try fetching a thumbnail from page (cached)
                            if not article['image'] and article['url']:
                                try:
                                    candidate = fetch_image_from_page(article['url'])
                                    if candidate:
                                        article['image'] = candidate
                                except Exception:
                                    pass

                            items.append(article)

                        # group by date (YYYY-MM-DD) preserving order
                        grouped = defaultdict(list)
                        order = []
                        for it in items:
                            dt = it['mtime'].date().isoformat() if it['mtime'] else 'unknown'
                            if dt not in grouped:
                                order.append(dt)
                            grouped[dt].append(it)

                        # render groups
                        for dt in order:
                            # render single date header
                            try:
                                pretty = datetime.fromisoformat(dt).strftime('%Y-%m-%d')
                            except Exception:
                                pretty = dt
                            st.markdown('---')
                            st.markdown(f"<h3 style='margin-bottom:8px'>{pretty}</h3>", unsafe_allow_html=True)
                            for it in grouped[dt]:
                                title = it['title']
                                src = it['source']
                                url = it['url']
                                score = it['score']
                                label = it['label']
                                image_url_local = it['image']

                                image_block = ''
                                if image_url_local:
                                    if url:
                                        image_block = textwrap.dedent(f"""
                                        <div style="margin-top:12px;margin-bottom:0px">
                                            <div style="width:100%;border-radius:8px;overflow:hidden;box-shadow:0 6px 18px rgba(0,0,0,0.08);">
                                                <a href="{url}" target="_blank" rel="noopener noreferrer" style="display:block;text-decoration:none;">
                                                    <img src="{image_url_local}" alt="miniatura artykułu" style="display:block;width:100%;height:auto;object-fit:cover;" />
                                                </a>
                                            </div>
                                        </div>
                                        """).strip()
                                    else:
                                        image_block = textwrap.dedent(f"""
                                        <div style="margin-top:12px;margin-bottom:0px">
                                            <div style="width:100%;border-radius:8px;overflow:hidden;box-shadow:0 6px 18px rgba(0,0,0,0.08);">
                                                <img src="{image_url_local}" alt="miniatura artykułu" style="display:block;width:100%;height:auto;object-fit:cover;" />
                                            </div>
                                        </div>
                                        """).strip()

                                header_card = f"""
                    <div style='border:2px solid #ddd;border-radius:8px;padding:12px;background:#fff;margin-bottom:10px;'>
                      <div class="article-title">{html.escape(str(title))}</div>
                      <div class="helper-text">{html.escape(str(src or ''))}</div>
                      {image_block}
                    </div>
                    """
                                st.markdown(textwrap.dedent(header_card), unsafe_allow_html=True)
                                st.markdown(f"<div style='margin-bottom:12px;color:#374151'><strong>Wynik:</strong> {html.escape(str(score or '-'))} — <em>{html.escape(str(label or '-'))}</em></div>", unsafe_allow_html=True)
        margin-bottom: 0.9rem !important;
    }

    /* Utility small text (selectors, helper labels) */
    .helper-text {
        font-size: 15px !important;
        color: #6b7280 !important;
    }

    /* Image caption */
    .img-caption {
        font-size: 14px !important;
        font-style: italic !important;
        color: #6b7280 !important;
        margin-top: 0.5rem !important;
        margin-bottom: 1rem !important;
    }

    /* Ensure margins between sections */
    .section-space { margin-bottom: 1rem !important; }

    /* Prevent shadows or decorative effects from being added */
    .no-decor { box-shadow: none !important; }

</style>
""", unsafe_allow_html=True)

REPORTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'reports')
REPORTS_DIR = os.path.normpath(REPORTS_DIR)
ANALYSIS_DIR = os.path.join(REPORTS_DIR, 'analysis')
SCRAPED_DIR = os.path.join(REPORTS_DIR, 'scraped')

# try to import scraper helper
SCRAPER_AVAILABLE = False
fetch_and_save_url = None
try:
    # Prefer import as package module
    import importlib
    mod = importlib.import_module('clickbait_verifier.scraper')
    fetch_and_save_url = getattr(mod, 'fetch_and_save_url', None)
    if fetch_and_save_url:
        SCRAPER_AVAILABLE = True
except Exception:
    try:
        # Fallback: add repo root to sys.path and import scraper by name
        import sys
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        if repo_root not in sys.path:
            sys.path.insert(0, repo_root)
        from scraper import fetch_and_save_url as _fetch_fn
        fetch_and_save_url = _fetch_fn
        SCRAPER_AVAILABLE = True
    except Exception:
        SCRAPER_AVAILABLE = False
        fetch_and_save_url = None

analysis_files = sorted(glob.glob(os.path.join(ANALYSIS_DIR, 'analysis_*.json')))
scraped_files = sorted(glob.glob(os.path.join(SCRAPED_DIR, 'scraped_*.json')))

# build a combined selection list: analyses first, then scraped-only entries
display_map = {}
analysis_ids = set()

for p in analysis_files:
    try:
        with open(p, 'r', encoding='utf-8') as f:
            a = json.load(f)
        src = a.get('source', 'unknown')
        title = a.get('title', '')
        display = f"{src} — {title if len(title) <= 120 else title[:117] + '...'}"
        # record id to avoid adding duplicate scraped entry for same article
        if a.get('id') is not None:
            analysis_ids.add(a.get('id'))
    except Exception:
        display = os.path.basename(p)
    key = display
    i = 1
    while key in display_map:
        key = f"{display} ({i})"
        i += 1
    display_map[key] = {'type': 'analysis', 'path': p}

# include scraped files (they may not have an analysis yet) - skip if analysis exists for same id
for p in scraped_files:
    try:
        with open(p, 'r', encoding='utf-8') as f:
            s = json.load(f)
        # skip scraped entries when we already have an analysis for the same id
        if s.get('id') in analysis_ids:
            continue
        src = s.get('source', 'unknown')
        title = s.get('title', os.path.basename(p))
        display = f"SCRAPED — {src} — {title if len(title) <= 120 else title[:117] + '...'}"
    except Exception:
        display = os.path.basename(p)
    key = display
    i = 1
    while key in display_map:
        key = f"{display} ({i})"
        i += 1
    display_map[key] = {'type': 'scraped', 'path': p}

if not display_map:
    st.warning('Brak plików analizy ani zeskrapowanych artykułów w katalogu reports/. Możesz użyć panelu po prawej, aby zescrapować URL.')
    # provide a placeholder so UI stays active and user can use scraping sidebar
    display_map['(brak plików) Użyj panelu scrapowania po prawej'] = {'type': 'none', 'path': None}

choices = list(display_map.keys())
# if we have a recently scraped path in session_state, try to select it by default
default_index = 0
last_path = st.session_state.get('last_scraped_path') if 'last_scraped_path' in st.session_state else None
if last_path:
    for idx, key in enumerate(choices):
        info = display_map.get(key)
        if info and info.get('path') and os.path.normpath(info.get('path')) == os.path.normpath(last_path):
            default_index = idx
            break
if st.session_state.get('feed_mode'):
    # in feed mode we don't show the selectbox - pick first item as placeholder
    sel = choices[0] if choices else None
    sel_info = display_map[sel] if sel else {'type': 'none', 'path': None}
else:
    sel = st.selectbox('Wybierz analizę / zescrapowany artykuł', choices, index=default_index)
    sel_info = display_map[sel]

# Feed mode toggle: allow switching to a simplified end-user feed (10 articles one after another)
if 'feed_mode' not in st.session_state:
    st.session_state['feed_mode'] = False

with st.sidebar:
    if st.button('Przełącz widok (Feed / Analiza)'):
        st.session_state['feed_mode'] = not st.session_state['feed_mode']
    st.markdown(f"**Aktualny tryb:** {'FEED (end-user)' if st.session_state['feed_mode'] else 'ANALIZA (developer)'}")

def _load_json_if_exists(path: str) -> dict | None:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None

def render_feed(max_items: int = 10):
    """Renderuje prosty feed artykułów (bez sekcji dolnych i bez selectbox)."""
    # choose files (analyses first, then scraped) sorted by mtime desc
    candidates = []
    for p in analysis_files + scraped_files:
        try:
            m = os.path.getmtime(p)
        except Exception:
            m = 0
        candidates.append((m, p))
    candidates.sort(reverse=True)
    shown = 0
    for _, p in candidates:
        if shown >= max_items:
            break
        data = _load_json_if_exists(p)
        if data is None:
            continue
        # decide whether this is analysis or scraped by filename prefix
        is_analysis = os.path.basename(p).startswith('analysis_')
        if is_analysis:
            a = data
            src = a.get('source')
            title = a.get('title') or '-'
            url = a.get('url')
            score = a.get('score')
            label = a.get('label')
        else:
            s = data
            a = {
                'id': s.get('id'),
                'source': s.get('source'),
                'title': s.get('title') or os.path.basename(p),
                'url': s.get('url'),
                'score': None,
                'label': None,
                'suggestions': {},
                'rationale': [],
                'signals': {}
            }
            src = a.get('source')
            title = a.get('title')
            url = a.get('url')
            score = a.get('score')
            label = a.get('label')

        # render date separator (file mtime)
        try:
            dt = datetime.fromtimestamp(os.path.getmtime(p)).strftime('%Y-%m-%d %H:%M')
        except Exception:
            dt = ''
        st.markdown('---')
        st.markdown(f"<div style='font-size:13px;color:#6b7280;margin-bottom:6px'>{dt}</div>", unsafe_allow_html=True)

        # header card (reuse same HTML format)
        suggested = a.get('suggestions', {}).get('rewrite_title_neutral') if isinstance(a.get('suggestions'), dict) else None
        image_url_local = None
        # try to pull image from scraped meta if available
        if not is_analysis:
            meta = data.get('meta') if isinstance(data.get('meta'), dict) else {}
            image_url_local = data.get('lead_image_url') or data.get('image') or meta.get('og:image') or meta.get('twitter:image')

        # build small image block if available
        image_block = ''
        if image_url_local:
            if url:
                image_block = textwrap.dedent(f"""
                <div style="margin-top:12px;margin-bottom:0px">
                    <div style="width:100%;border-radius:8px;overflow:hidden;box-shadow:0 6px 18px rgba(0,0,0,0.08);">
                        <a href="{url}" target="_blank" rel="noopener noreferrer" style="display:block;text-decoration:none;">
                            <img src="{image_url_local}" alt="miniatura artykułu" style="display:block;width:100%;height:auto;object-fit:cover;" />
                        </a>
                    </div>
                </div>
                """
                ).strip()
            else:
                image_block = textwrap.dedent(f"""
                <div style="margin-top:12px;margin-bottom:0px">
                    <div style="width:100%;border-radius:8px;overflow:hidden;box-shadow:0 6px 18px rgba(0,0,0,0.08);">
                        <img src="{image_url_local}" alt="miniatura artykułu" style="display:block;width:100%;height:auto;object-fit:cover;" />
                    </div>
                </div>
                """
                ).strip()

        header_card = f"""
<div style='border:2px solid #ddd;border-radius:8px;padding:12px;background:#fff;margin-bottom:10px;'>
  <div class="article-title">{html.escape(str(title))}</div>
  <div class="helper-text">{html.escape(str(src or ''))}</div>
  <div class="suggested-title">{html.escape(str(suggested or ''))}</div>
  {image_block}
</div>
"""
        st.markdown(textwrap.dedent(header_card), unsafe_allow_html=True)

        # small score line
        score_display = '-' if score is None else score
        st.markdown(f"<div style='margin-bottom:18px;color:#374151'><strong>Wynik:</strong> {html.escape(str(score_display))} — <em>{html.escape(str(label or '-'))}</em></div>", unsafe_allow_html=True)

        shown += 1

    st.markdown('---')

# if feed_mode active, render feed and stop
if st.session_state.get('feed_mode'):
    render_feed(max_items=10)
    st.stop()

analysis = None
scraped_path = None
analysis_name = None
if sel_info['type'] == 'analysis':
    sel_path = sel_info['path']
    analysis_name = os.path.basename(sel_path)
    with open(sel_path, 'r', encoding='utf-8') as f:
        analysis = json.load(f)
    # try to locate scraped file for this analysis id (optional)
    try:
        scraped_pattern = os.path.join(SCRAPED_DIR, f"scraped_{analysis.get('id')}*.json")
        s_matches = sorted(glob_files(scraped_pattern))
        if s_matches:
            scraped_path = s_matches[-1]
    except Exception:
        scraped_path = None
elif sel_info['type'] == 'scraped':
    # selection is a scraped-only entry; load scraped JSON and synthesize minimal analysis object
    scraped_path = sel_info['path']
    with open(scraped_path, 'r', encoding='utf-8') as f:
        scraped = json.load(f)
    analysis = {
        'id': scraped.get('id'),
        'source': scraped.get('source'),
        'title': scraped.get('title'),
        'url': scraped.get('url'),
        'score': None,
        'label': None,
        'suggestions': {},
        'rationale': [],
        'signals': {}
    }
else:
    # placeholder selection when there are no files; provide empty analysis object so UI renders
    analysis = {
        'id': None,
        'source': None,
        'title': 'Brak plików - użyj panelu scrapowania po prawej',
        'url': None,
        'score': None,
        'label': None,
        'suggestions': {},
        'rationale': [],
        'signals': {}
    }

# after building `analysis` and `scraped_path` variables, prepare scraped metadata for top section
scraped = {}
orig_url = analysis.get('url')
image_url = None
scraped_name = None
if scraped_path:
    scraped_name = os.path.basename(scraped_path)
    try:
        with open(scraped_path, 'r', encoding='utf-8') as f:
            scraped = json.load(f)
    except Exception:
        scraped = {}
    # use analysis.url if present, otherwise fallback to scraped url
    orig_url = orig_url or scraped.get('url')
    # common keys where image might be stored
    candidates = [
        'lead_image_url', 'top_image', 'image', 'thumbnail', 'og_image', 'thumbnail_url'
    ]
    meta = scraped.get('meta') if isinstance(scraped.get('meta'), dict) else {}
    for k in candidates:
        val = scraped.get(k)
        if val:
            image_url = val
            break
    if not image_url:
        image_url = meta.get('og:image') or meta.get('image') or meta.get('twitter:image')
# If no image was found in scraped JSON but we have the original URL, try to fetch a thumbnail directly
if not image_url and orig_url:
    try:
        with st.spinner('Pobieram miniaturę z artykułu...'):
            candidate = fetch_image_from_page(orig_url)
            if candidate:
                image_url = candidate
    except Exception:
        # ignore network errors and proceed without thumbnail
        pass

# Precompute image HTML block so it can be inserted into header regardless of later exceptions
image_block_html = ''
if image_url:
        try:
                # build the HTML with consistent indentation, then dedent+strip
                if orig_url:
                        raw = f'''
    <div style="margin-top:12px;margin-bottom:0px">
        <div style="width:100%;border-radius:8px;overflow:hidden;box-shadow:0 6px 18px rgba(0,0,0,0.08);">
            <a href="{orig_url}" target="_blank" rel="noopener noreferrer" style="display:block;text-decoration:none;">
                <img src="{image_url}" alt="miniatura artykułu" style="display:block;width:100%;height:auto;object-fit:cover;" />
            </a>
        </div>
    </div>
'''
                else:
                        raw = f'''
    <div style="margin-top:12px;margin-bottom:0px">
        <div style="width:100%;border-radius:8px;overflow:hidden;box-shadow:0 6px 18px rgba(0,0,0,0.08);">
            <img src="{image_url}" alt="miniatura artykułu" style="display:block;width:100%;height:auto;object-fit:cover;" />
        </div>
    </div>
'''
                # remove common indentation so Markdown doesn't treat HTML lines starting with 4 spaces as code
                image_block_html = textwrap.dedent(raw).strip()
        except Exception:
                image_block_html = ''

# Create two-column layout: left for content, right for rationale
col_left, col_right = st.columns([3, 2])

with col_left:
    # Top row: render header card and score card
    try:
        original_title = analysis.get('title') or '-'
        suggested = analysis.get('suggestions', {}).get('rewrite_title_neutral')
        score_val = analysis.get('score')
        label_val = (analysis.get('label') or '') if analysis.get('label') else None
        score_display = '-' if score_val is None else score_val
        score_color = '#888'

        label_colors = {
            'not_clickbait': '#1a7f37',
            'mild': '#b2700f',
            'strong': '#c4301f',
            'extreme': '#800000',
            'insufficient_content': '#666'
        }

        try:
            if isinstance(score_val, (int, float)):
                s = float(score_val)
            else:
                s = float(score_val) if score_val is not None else None
        except Exception:
            s = None

        if label_val and label_val.lower() in label_colors:
            score_color = label_colors[label_val.lower()]
        elif s is not None:
            if s >= 75:
                score_color = label_colors['extreme']
            elif s >= 50:
                score_color = label_colors['strong']
            elif s >= 25:
                score_color = label_colors['mild']
            else:
                score_color = label_colors['not_clickbait']

        # format score for display
        try:
            score_display = f"{int(s) if s is not None and s == int(s) else round(s,1)}"
        except Exception:
            score_display = '-' if s is None else str(s)

        # use precomputed image_block_html inside header card
        header_card = f"""
<div style='border:2px solid #ddd;border-radius:8px;padding:16px;background:#fff;margin-bottom:14px;'>
  <div class="article-title">{original_title}</div>
  <div class="helper-text">Sugerowany tytuł (neutralny)</div>
  <div class="suggested-title">{(suggested or "- brak sugestii -")}</div>
{image_block_html}
</div>
"""

        score_card = f"""
<div style='border:2px solid #ddd;border-radius:8px;padding:14px;background:#fff;margin-bottom:12px;text-align:center;'>
  <div class="score-label">Wynik (score)</div>
  <div class="score-value" style='color:{score_color};'>{score_display}</div>
  <div class="score-label-text" style='color:{score_color};'>Etykieta: <strong style='color:{score_color}'>{analysis.get('label') or "-"}</strong></div>
</div>
"""

        # render header on the left; score will be shown in the right column above rationale
        st.markdown(textwrap.dedent(header_card), unsafe_allow_html=True)
    except Exception:
        # fallback to simple text display
        st.header(analysis.get('title') or '-')
        suggested = analysis.get('suggestions', {}).get('rewrite_title_neutral')
        if suggested:
            st.markdown(f"**Sugerowany tytuł (neutralny):** {suggested}")
        else:
            st.markdown("**Sugerowany tytuł (neutralny):** - brak sugestii -")

        # NOTE: thumbnail (if any) is embedded into the header card above so no separate rendering here

with col_right:
    # Score in right column (moved above rationale)
    try:
        # score_card was created in the left column's try block; if available, render it here
        st.markdown(textwrap.dedent(score_card), unsafe_allow_html=True)
    except Exception:
        # fallback numeric metric
        st.metric(label='Wynik (score)', value=analysis.get('score'))

    # Rationale in right column - render inside a bordered card similar to the score card
    rationale = analysis.get('rationale', []) or []
    try:
        # build HTML block for rationale (same visual card style as score_card)
        if rationale:
            items_html = "\n".join(
                f"<div class='rationale-item'>{i}. {html.escape(str(r))}</div>" for i, r in enumerate(rationale, 1)
            )
        else:
            items_html = "<div class='rationale-item'>- brak uzasadnienia -</div>"

        rationale_card = f"""
<div style='border:2px solid #ddd;border-radius:8px;padding:14px;background:#fff;margin-bottom:12px;'>
  <div class="score-label">Uzasadnienie</div>
  <div style='margin-top:6px'>
    {items_html}
  </div>
</div>
"""

        st.markdown(textwrap.dedent(rationale_card), unsafe_allow_html=True)
    except Exception:
        # fallback to simple list rendering
        st.subheader('Uzasadnienie')
        if rationale:
            for i, r in enumerate(rationale, 1):
                st.markdown(f"{i}. {r}")
        else:
            st.info('- brak uzasadnienia -')

st.markdown('---')

# Sidebar: scrapowanie z GUI
st.sidebar.header('Scrapuj URL')
input_url = st.sidebar.text_input('URL do zescrapowania')

# minimal scraping UI: only URL and button
if st.sidebar.button('Scrapuj'):
    if not input_url:
        st.sidebar.error('Podaj URL przed rozpoczęciem scrapowania')
    elif not SCRAPER_AVAILABLE:
        st.sidebar.error('Funkcja scrapowania nie jest dostępna (problem z importem scraper.py)')
    else:
        with st.spinner('Pobieram...'):
            # use default source_name and fetch_method to keep UI minimal
            result = fetch_and_save_url(input_url, source_name='CLI', fetch_method='auto')
        if not result:
            st.sidebar.error('Scrapowanie nie powiodło się. Sprawdź komunikaty w terminalu serwera.')
        else:
            # support new structured return {id, existed} or legacy int
            if isinstance(result, dict):
                sid = result.get('id')
                existed = result.get('existed', False)
            else:
                sid = int(result)
                existed = False
            if existed:
                st.sidebar.info(f'URL już istnieje w DB (id={sid}) — pomijam ponowne zapisanie.')
            else:
                st.sidebar.success(f'Zapisano artykuł w DB (id={sid})')
            # find latest scraped file for this id (may exist from previous save)
            pattern = os.path.join(SCRAPED_DIR, f'scraped_{sid}*.json')
            matches = sorted(glob_files(pattern))
            if matches:
                latest = matches[-1]
                rel = os.path.relpath(latest, start=os.getcwd())
                st.sidebar.markdown(f'Plik scraped: `{rel}`')
                try:
                    st.session_state['last_scraped_path'] = os.path.normpath(latest)
                except Exception:
                    pass
                # refresh the app so selection appears in the main panel
                _safe_rerun()
            else:
                if existed:
                    st.sidebar.warning('URL jest w bazie danych, ale nie znaleziono odpowiadającego pliku scraped_*.json — możliwe, że plik został usunięty ręcznie.')
                else:
                    st.sidebar.info('Nie znaleziono pliku scraped_* dla zapisanego id — sprawdź logi serwera.')

# Sidebar: quick scrape of today's articles from configured sources
st.sidebar.markdown('---')
st.sidebar.header('Scrapuj dzisiaj z serwisu')
# load sources from config
try:
    cfg = yaml.safe_load(open('config.yaml'))
    cfg_sources = [s for s in cfg.get('sources', []) if s.get('enabled', True) and s.get('scrape_listing')]
    source_names = [s.get('name') for s in cfg_sources]
except Exception:
    cfg_sources = []
    source_names = []

if source_names:
    selected_service = st.sidebar.selectbox('Wybierz serwis', ['-- wybierz --'] + source_names, index=0)
    if selected_service and selected_service != '-- wybierz --':
        if st.sidebar.button('Zescrapuj dzisiaj'):
            if not SCRAPER_AVAILABLE:
                st.sidebar.error('Funkcja scrapowania nie jest dostępna (problem z importem scraper.py)')
            else:
                with st.spinner(f'Scrapuję artykuły z {selected_service}...'):
                    try:
                        from clickbait_verifier.scraper import scrape_listing_for_source
                        results = scrape_listing_for_source(selected_service)
                        added = [r for r in results if r.get('id') and not r.get('skipped')]
                        skipped = [r for r in results if r.get('skipped')]
                        st.sidebar.success(f'Dodano {len(added)} nowych artykułów z {selected_service}')
                        if skipped:
                            st.sidebar.info(f'Pominięto {len(skipped)} pozycji (już istniały lub nie były z dzisiaj)')
                        # show list of added files
                        for r in added[:10]:
                            st.sidebar.markdown(f"- `{os.path.relpath(r.get('path'), start=os.getcwd())}`")
                        # set last_scraped_path to most recent added if any
                        if added:
                            latest = added[-1]['path']
                            try:
                                st.session_state['last_scraped_path'] = os.path.normpath(latest)
                            except Exception:
                                pass
                            _safe_rerun()
                    except Exception as e:
                        st.sidebar.error(f'Błąd podczas scrapowania: {e}')
else:
    st.sidebar.info('Brak skonfigurowanych serwisów z opcją scrape_listing w config.yaml')

# fix scraped lookup for main panel: prepare prompt in the sidebar (we already loaded scraped earlier, avoid re-reading/displaying link/image)
if scraped_path:
    spec_rel = os.path.relpath(os.path.join(os.path.dirname(__file__), '..', 'clickbait_agent_spec_v1.1.yaml'), start=os.getcwd())
    rel_scraped = os.path.relpath(scraped_path, start=os.getcwd())
    prompt_text = (
        f"Przeanalizuj plik JSON zeskrapowanego artykułu: {rel_scraped}\n"
        f"Użyj instrukcji i kryteriów zawartych w pliku '{spec_rel}'.\n"
        "DODATKOWO: Zapisz wygenerowany JSON do pliku o nazwie 'analysis_{id}.json' w katalogu 'reports/analysis' (gdzie {id} to id artykułu z pliku scraped). Jeśli plik o tej nazwie już istnieje, dopisz numerowany sufiks (np. analysis_{id}_1.json), aby nie nadpisać istniejącego pliku.\n"
    )

    with st.sidebar.expander('Gotowy prompt do skopiowania (wklej do interfejsu LLM/Agenta)', expanded=True):
        try:
            import streamlit.components.v1 as components
            import json as _json
            js_prompt = _json.dumps(prompt_text)
            html = f'''<div>
  <textarea id="prompt_textarea" style="width:100%;height:260px;"></textarea>
  <div style="margin-top:8px">
    <button id="copybtn">Skopiuj prompt</button>
  </div>
</div>
<script>
  const ta = document.getElementById("prompt_textarea");
  ta.value = {js_prompt};
  document.getElementById("copybtn").addEventListener("click", async function() {{
    try {{
      await navigator.clipboard.writeText(ta.value);
      this.innerText = "Skopiowano";
    }} catch(e) {{
      alert("Kopiowanie nie powiodło się: " + e);
    }}
  }});
</script>'''
            components.html(html, height=340)
        except Exception:
            st.write('Brak możliwości wygenerowania promptu do kopiowania.')
else:
    st.info('Brak powiązanego pliku scraped_*.json')

# place 'Główne sygnały' at the very bottom of the main content
st.markdown('---')
with st.expander('Główne sygnały'):
    st.json(analysis.get('signals', {}))

# Show scraped/analysis source filenames as a footer at the very bottom (if available)
if scraped_name or analysis_name:
    try:
        if scraped_name:
            st.markdown(f"**Źródło scraped:** `{scraped_name}`")
        if analysis_name:
            st.markdown(f"**Plik analizy:** `{analysis_name}`")
    except Exception:
        pass
