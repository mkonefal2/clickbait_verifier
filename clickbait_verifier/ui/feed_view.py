"""Feed view for end-user display."""

import streamlit as st
import os
import sys
import html
from datetime import datetime
from typing import List, Tuple

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.file_loader import load_json_if_exists
from utils.helpers import fetch_image_from_page
from ui.components import (
    render_simple_header_card_with_suggestion,
    render_image_block_compact,
    render_score_card_with_rationale,
    render_badges_card,
)


def render_feed(candidates: List[Tuple[float, str]], max_items: int = 10):
    """Render a simple feed of articles with pagination controls.

    Args:
        candidates: List of (mtime, path) tuples sorted by mtime descending.
        max_items: (deprecated) kept for compatibility but feed now uses pagination controls.
    """
    # --- Pagination controls ---
    total = len(candidates)
    # Page size options (string form to include 'All')
    page_size_options = ['10', '25', '50', 'All']
    # initialize session state keys
    if 'feed_page' not in st.session_state:
        st.session_state['feed_page'] = 1
    if 'feed_page_size' not in st.session_state:
        st.session_state['feed_page_size'] = page_size_options[0]

    # Controls row
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            # page size selector
            sel = st.selectbox('Ilość na stronę', page_size_options, index=page_size_options.index(st.session_state['feed_page_size']))
            st.session_state['feed_page_size'] = sel
        with col2:
            # display current range / total and page navigation
            # determine numeric page size
            page_size = None if st.session_state['feed_page_size'] == 'All' else int(st.session_state['feed_page_size'])
            total_pages = 1 if (page_size is None or total == 0) else ((total - 1) // page_size) + 1
            # normalize page within bounds
            if st.session_state['feed_page'] < 1:
                st.session_state['feed_page'] = 1
            if st.session_state['feed_page'] > total_pages:
                st.session_state['feed_page'] = total_pages

            # navigation buttons
            nav_cols = st.columns([1, 2, 1])
            if nav_cols[0].button('◀ Poprzednia'):
                st.session_state['feed_page'] = max(1, st.session_state['feed_page'] - 1)
            nav_cols[1].markdown(f"**Strona {st.session_state['feed_page']} / {total_pages} — {total} artykułów**")
            if nav_cols[2].button('Następna ▶'):
                st.session_state['feed_page'] = min(total_pages, st.session_state['feed_page'] + 1)
        with col3:
            # quick jump to page
            if page_size is not None and total_pages > 1:
                p = st.number_input('Przejdź do strony', min_value=1, max_value=total_pages, value=st.session_state['feed_page'], step=1)
                if p != st.session_state['feed_page']:
                    st.session_state['feed_page'] = int(p)

    # Determine slice of candidates to show based on pagination
    if st.session_state['feed_page_size'] == 'All':
        page_candidates = candidates
    else:
        page_size = int(st.session_state['feed_page_size'])
        page = max(1, int(st.session_state.get('feed_page', 1)))
        start = (page - 1) * page_size
        end = start + page_size
        page_candidates = candidates[start:end]

    shown = 0
    last_date = None
    
    for _, p in page_candidates:
        # no max_items limiting — pagination controls govern the number shown
        
            
        data = load_json_if_exists(p)
        if data is None:
            continue
            
        # Decide whether this is analysis or scraped by filename prefix
        is_analysis = os.path.basename(p).startswith('analysis_')
        
        if is_analysis:
            a = data
            src = a.get('source')
            title = a.get('title') or '-'
            url = a.get('url')
            score = a.get('score')
            label = a.get('label')
            
            # Try to find corresponding scraped file for image
            scraped_id = a.get('id')
            scraped_dir = os.path.join(os.path.dirname(p), '..', 'scraped')
            scraped_path = os.path.join(scraped_dir, f'scraped_{scraped_id}.json')
            scraped_data = load_json_if_exists(scraped_path)
        else:
            s = data
            scraped_data = data
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

        # Render date separator - prefer article's stored date (fetched_at/published/added)
        # fallback to file mtime if no date found
        current_date = ''
        try:
            date_source = None
            # scraped_data (if present) likely contains fetched_at or published
            if scraped_data and isinstance(scraped_data, dict):
                for key in ('fetched_at', 'fetched', 'added', 'created_at', 'published'):
                    if scraped_data.get(key):
                        date_source = scraped_data.get(key)
                        break

            # analysis files might include a date in the analysis dict (rare), check there too
            if not date_source and isinstance(a, dict):
                for key in ('fetched_at', 'fetched', 'added', 'created_at', 'published', 'analyzed_at'):
                    if a.get(key):
                        date_source = a.get(key)
                        break

            if date_source:
                # numeric timestamps (seconds since epoch)
                if isinstance(date_source, (int, float)):
                    current_date = datetime.fromtimestamp(float(date_source)).strftime('%Y-%m-%d')
                else:
                    # try ISO format first, then fall back to taking the date prefix
                    try:
                        current_date = datetime.fromisoformat(str(date_source)).strftime('%Y-%m-%d')
                    except Exception:
                        try:
                            current_date = datetime.strptime(str(date_source)[:10], '%Y-%m-%d').strftime('%Y-%m-%d')
                        except Exception:
                            current_date = ''

            if not current_date:
                # final fallback: use file modification time
                current_date = datetime.fromtimestamp(os.path.getmtime(p)).strftime('%Y-%m-%d')
        except Exception:
            current_date = ''
        
        if current_date and current_date != last_date:
            if last_date is not None:
                st.markdown("<div style='margin-top:32px;'></div>", unsafe_allow_html=True)
            
            st.markdown(
                f"""
                <div style='margin-top:24px;margin-bottom:24px;'>
                    <div style='font-size:28px;font-weight:600;color:#111827;margin-bottom:8px;'>{current_date}</div>
                    <div style='border-bottom:2px solid #e5e7eb;'></div>
                </div>
                """, 
                unsafe_allow_html=True
            )
            last_date = current_date

        # Header card
        suggested = a.get('suggestions', {}).get('rewrite_title_neutral') if isinstance(a.get('suggestions'), dict) else None
        rationale = a.get('rationale_user_friendly', [])
        image_url_local = None
        
        # Try to pull image from scraped data if available
        if scraped_data:
            meta = scraped_data.get('meta') if isinstance(scraped_data.get('meta'), dict) else {}
            image_url_local = (
                scraped_data.get('lead_image_url') or 
                scraped_data.get('image') or 
                meta.get('og:image') or 
                meta.get('twitter:image')
            )
        
        # If no image was found but we have the URL, try to fetch a thumbnail
        if not image_url_local and url:
            try:
                candidate = fetch_image_from_page(url)
                if candidate:
                    image_url_local = candidate
            except Exception:
                pass

        # Build image block (compact version for feed)
        image_block = render_image_block_compact(image_url_local, url)

        # Render in CSS Grid layout: 3fr (left) + minmax(280px, 1fr) (right)
        st.markdown("""
        <style>
        .feed-grid {
            display: grid;
            grid-template-columns: 3fr minmax(280px, 1fr);
            gap: 24px;
        }
        @media (max-width: 768px) {
            .feed-grid {
                grid-template-columns: 1fr;
            }
            .feed-grid > :nth-child(2) {
                order: -1;
            }
        }
        </style>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Render header card with suggested title
            header_card = render_simple_header_card_with_suggestion(title, src, suggested, image_block, url)
            st.markdown(header_card, unsafe_allow_html=True)
        
        with col2:
            # Render score card with rationale
            score_card = render_score_card_with_rationale(score, label, rationale)
            st.markdown(score_card, unsafe_allow_html=True)

            # Badges display removed per user request
        
        # Add spacing between articles
        st.markdown("<div style='margin-bottom:24px;'></div>", unsafe_allow_html=True)

        shown += 1
