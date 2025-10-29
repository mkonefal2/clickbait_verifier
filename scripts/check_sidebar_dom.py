"""Headless check for Streamlit sidebar DOM.

This script:
- launches Streamlit in a background process (uses subprocess)
- waits until the local server responds (http://localhost:8501)
- fetches the homepage HTML
- parses `ul[data-testid="stSidebarNav"]` using BeautifulSoup
- prints the list of sidebar item texts and a verdict whether only Analytics View and Feed View are visible

Run from repository root.
"""
import subprocess
import time
import requests
import sys
import os
from bs4 import BeautifulSoup

STREAMLIT_CMD = [sys.executable, '-m', 'streamlit', 'run', 'clickbait_verifier/streamlit_feed_app.py']
LOCAL_URL = 'http://localhost:8501'

# Start Streamlit as a background process
proc = subprocess.Popen(STREAMLIT_CMD, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=os.getcwd())
print('Started Streamlit (PID=%s), waiting for server to start...' % proc.pid)

# Wait for server to be available
timeout = 60
start = time.time()
up = False
while time.time() - start < timeout:
    try:
        r = requests.get(LOCAL_URL, timeout=2)
        up = True
        break
    except Exception:
        time.sleep(0.5)

if not up:
    print('Streamlit did not start within %s seconds. Printing recent stdout/stderr:' % timeout)
    try:
        out = proc.stdout.read().decode(errors='ignore')
        print(out)
    except Exception as e:
        print('Could not read process output:', e)
    proc.terminate()
    sys.exit(2)

print('Server is up, fetching page...')
try:
    r = requests.get(LOCAL_URL)
    html = r.text
except Exception as e:
    print('Failed to fetch page:', e)
    proc.terminate()
    sys.exit(3)

soup = BeautifulSoup(html, 'html.parser')
nav = soup.select_one('ul[data-testid="stSidebarNav"]')
if not nav:
    print('No sidebar nav found in HTML snapshot. The sidebar may be rendered client-side after initial load.')
    proc.terminate()
    sys.exit(4)

items = []
for li in nav.select('li'):
    # text inside anchor or span
    a = li.select_one('a') or li.select_one('span') or li
    text = a.get_text(strip=True)
    items.append(text)

print('Sidebar items (snapshot):')
for i, t in enumerate(items, 1):
    print(f'{i}. {t}')

# Verdict: keep only Analytics View and Feed View
keep = ['analytics view', 'feed view']
visible = [t.strip().lower() for t in items if t.strip()]
others = [t for t in visible if not any(k in t for k in keep)]
if len(visible) == 0:
    print('No visible items captured.')
else:
    if not others:
        print('\nVERDICT: OK — only Analytics View and Feed View are visible (or equivalents).')
    else:
        print('\nVERDICT: NOT OK — additional items present:')
        for o in others:
            print(' -', o)

# Clean up
proc.terminate()
print('Streamlit process terminated.')
