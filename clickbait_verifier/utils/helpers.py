"""Helper utility functions for the Streamlit application."""

import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


@st.cache_data(show_spinner=False)
def fetch_image_from_page(url: str) -> str | None:
    """Try to retrieve a representative image URL from a web page without saving any files.
    
    Returns absolute image URL or None.
    Caching avoids repeated network requests for the same URL.
    
    Args:
        url: The URL of the web page to fetch the image from.
        
    Returns:
        Absolute image URL or None if no image is found.
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
                    area = int(w) * int(h) if w and h else 0
                except Exception:
                    area = 0
                if area > best_area:
                    best_area = area
                    best = full
            if best:
                return best
            return urljoin(resp.url, imgs[0]["src"])
    except Exception:
        return None


def safe_rerun():
    """Safe wrapper for rerunning the Streamlit app across different Streamlit versions.
    
    Tries to call st.experimental_rerun(); if unavailable, toggles a session_state key 
    and stops execution.
    """
    try:
        rerun = getattr(st, "experimental_rerun", None)
        if callable(rerun):
            rerun()
            return
    except Exception:
        pass
    try:
        # Fallback: toggle a session-state flag so UI reflects change on next interaction
        st.session_state['_cb_rerun_toggle'] = not st.session_state.get('_cb_rerun_toggle', False)
    except Exception:
        pass
    try:
        st.stop()
    except Exception:
        return
