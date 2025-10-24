"""Headless check for Streamlit sidebar DOM using Playwright.

This script:
- launches Streamlit in a background process
- uses Playwright (Chromium) to open http://localhost:8501 in headless mode
- waits until `ul[data-testid="stSidebarNav"]` is visible
- collects the visible sidebar item texts
- prints them and a verdict whether only Analytics View and Feed View remain
"""
import subprocess
import time
import sys
import os
from playwright.sync_api import sync_playwright

STREAMLIT_CMD = [sys.executable, '-m', 'streamlit', 'run', 'run_app.py']
LOCAL_URL = 'http://localhost:8501'

proc = subprocess.Popen(STREAMLIT_CMD, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=os.getcwd())
print('Started Streamlit (PID=%s), waiting for server to start...' % proc.pid)

# Wait for server to be reachable
start = time.time()
while time.time() - start < 60:
    try:
        import requests
        r = requests.get(LOCAL_URL, timeout=2)
        if r.status_code == 200:
            break
    except Exception:
        time.sleep(0.5)
else:
    print('Streamlit did not start in time.')
    proc.terminate()
    sys.exit(1)

print('Server reachable — launching headless browser...')

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(LOCAL_URL, wait_until='networkidle')

    # dump page content for debugging (always)
    content = page.content()
    dump_path = os.path.join('scripts', 'playwright_page_snapshot.html')
    with open(dump_path, 'w', encoding='utf-8') as f:
        f.write(content)

    try:
        # wait for the sidebar navigation (give more time for client-side render)
        # Streamlit renders a div[data-testid="stSidebarNav"] containing
        # ul[data-testid="stSidebarNavItems"], so wait for either to appear.
        page.wait_for_selector('div[data-testid="stSidebarNav"]', timeout=60000)
    except Exception as e:
        # dump page content for debugging
        content = page.content()
        dump_path = os.path.join('scripts', 'playwright_page_snapshot.html')
        with open(dump_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print('Sidebar nav did not appear within timeout:', e)
        print(f'Wrote page snapshot to {dump_path}')
        browser.close()
        proc.terminate()
        sys.exit(2)

    # collect visible li texts — Streamlit may use different data-testids
    ul_selector = None
    for sel in ['ul[data-testid="stSidebarNavItems"]', 'ul[data-testid="stSidebarNav"]']:
        if page.query_selector(sel):
            ul_selector = sel
            break

    if not ul_selector:
        # fallback: any ul under the nav container
        ul_selector = 'div[data-testid="stSidebarNav"] ul'

    items = page.query_selector_all(f'{ul_selector} li')
    visible_texts = []
    for it in items:
        try:
            # prefer span[label] (Streamlit renders <span label="...">)
            span = it.query_selector('span[label]')
            if span:
                txt = (span.get_attribute('label') or span.inner_text() or '').strip()
            else:
                a = it.query_selector('a')
                txt = (a.inner_text().strip() if a else (it.inner_text().strip()))

            # check computed style visibility
            visible = it.evaluate("(el) => window.getComputedStyle(el).display !== 'none'")

            # additionally, skip elements that are visually hidden by style attributes
            if visible and txt:
                visible_texts.append(txt)
        except Exception:
            continue

    print('Sidebar visible items:')
    for i, t in enumerate(visible_texts, 1):
        print(f'{i}. {t}')

    keep = ['analytics view', 'feed view']
    others = [t for t in [s.lower() for s in visible_texts] if not any(k in t for k in keep)]
    if not others:
        print('\nVERDICT: OK — only Analytics View and Feed View visible (or equivalents).')
    else:
        print('\nVERDICT: NOT OK — additional visible items:')
        for o in others:
            print(' -', o)

    browser.close()

proc.terminate()
print('Streamlit process terminated.')
