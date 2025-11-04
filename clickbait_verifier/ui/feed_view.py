"""Feed view for end-user display."""

import streamlit as st
import os
import sys
import html
from datetime import datetime
from typing import List, Tuple, Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.file_loader import load_json_if_exists
from utils.helpers import fetch_image_from_page
from ui.components import (
    render_simple_header_card_with_suggestion,
    render_image_block_compact,
    render_score_card_with_rationale,
    render_badges_card,
    get_score_color,
    format_score_display,
    _get_badge_image_data_uri,
    get_label_display_name,
)


def _get_label_badge_html(label: Optional[str], size: int = 48) -> str:
    """Get HTML for label badge image.
    
    Args:
        label: Label string (not_clickbait, mild, strong, extreme).
        size: Size of the badge in pixels.
        
    Returns:
        HTML string with badge image or fallback emoji.
    """
    badge_map = {
        'not_clickbait': 'badges/not_clickbait.png',
        'mild': 'badges/mild.png',
        'strong': 'badges/strong.png',
        'extreme': 'badges/extreme.png'
    }
    
    badge_path = badge_map.get(label.lower() if label else '', None)
    
    if badge_path:
        badge_uri = _get_badge_image_data_uri(badge_path)
        if badge_uri:
            return f'<img src="{badge_uri}" alt="{label}" style="width:{size}px;height:{size}px;" />'
    
    # Fallback to emoji
    emoji_map = {
        'not_clickbait': '✅',
        'mild': '⚠️',
        'strong': '🔴',
        'extreme': '🚨'
    }
    emoji = emoji_map.get(label.lower() if label else '', '📊')
    return f'<div style="font-size:{int(size*0.75)}px;">{emoji}</div>'


def _render_pagination_controls(filtered_total: int):
    """Render pagination controls at bottom of feed.
    
    Args:
        filtered_total: Total number of filtered articles.
    """
    page_size_options = ['10', '25', '50', 'All']
    
    # Calculate pagination values
    page_size = None if st.session_state['feed_page_size'] == 'All' else int(st.session_state['feed_page_size'])
    total_pages = 1 if (page_size is None or filtered_total == 0) else ((filtered_total - 1) // page_size) + 1
    
    if st.session_state['feed_page'] < 1:
        st.session_state['feed_page'] = 1
    if st.session_state['feed_page'] > total_pages:
        st.session_state['feed_page'] = total_pages
    
    current_page = st.session_state['feed_page']
    
    # Render controls in a clean layout
    with st.container():
        # Main navigation row
        col1, col2, col3 = st.columns([1.5, 3, 1.5])
        
        with col1:
            sel = st.selectbox('Ilość na stronę', page_size_options, 
                             index=page_size_options.index(st.session_state['feed_page_size']),
                             key='page_size_select',
                             label_visibility='visible')
            if sel != st.session_state['feed_page_size']:
                st.session_state['feed_page_size'] = sel
                st.session_state['feed_page'] = 1  # Reset to first page on page size change
                st.rerun()
        
        with col2:
            # Navigation buttons and page indicator in sub-columns
            nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
            
            with nav_col1:
                # Add spacing div to push button down
                st.markdown("<div style='height:31px;'></div>", unsafe_allow_html=True)
                # Use link_button for navigation with query params
                if current_page > 1:
                    prev_page = current_page - 1
                    if st.button('◀ Poprzednia', use_container_width=True, key='prev_btn'):
                        st.session_state['feed_page'] = prev_page
                        st.query_params['page'] = str(prev_page)
                        st.rerun()
                else:
                    st.button('◀ Poprzednia', use_container_width=True, key='prev_btn', disabled=True)
            
            with nav_col2:
                # Add spacing div to push indicator down
                st.markdown("<div style='height:31px;'></div>", unsafe_allow_html=True)
                st.markdown(
                    f"""<div style='text-align:center;font-weight:700;font-size:16px;padding:10px;
                    background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color:white;border-radius:8px;box-shadow:0 2px 8px rgba(102,126,234,0.3);'>
                    Strona {current_page} / {total_pages}
                    </div>""",
                    unsafe_allow_html=True,
                )
            
            with nav_col3:
                # Add spacing div to push button down
                st.markdown("<div style='height:31px;'></div>", unsafe_allow_html=True)
                # Use link_button for navigation with query params
                if current_page < total_pages:
                    next_page = current_page + 1
                    if st.button('Następna ▶', use_container_width=True, key='next_btn'):
                        st.session_state['feed_page'] = next_page
                        st.query_params['page'] = str(next_page)
                        st.rerun()
                else:
                    st.button('Następna ▶', use_container_width=True, key='next_btn', disabled=True)
        
        with col3:
            # Jump to page input
            if page_size is not None and total_pages > 1:
                p = st.number_input('Przejdź do strony', min_value=1, max_value=total_pages, 
                                  value=current_page, step=1,
                                  key='page_jump',
                                  label_visibility='visible')
                if p != current_page:
                    st.session_state['feed_page'] = int(p)
                    st.rerun()
            else:
                # Empty placeholder to maintain layout
                st.markdown("<div style='height:74px;'></div>", unsafe_allow_html=True)


def render_feed(candidates: List[Tuple[float, str]], max_items: int = 10):
    """Render a simple feed of articles with pagination controls.

    Args:
        candidates: List of (mtime, path) tuples sorted by mtime descending.
        max_items: (deprecated) kept for compatibility but feed now uses pagination controls.
    """
    # --- Initialize session state FIRST (before any callbacks can be triggered) ---
    if 'feed_page' not in st.session_state:
        st.session_state['feed_page'] = 1
    if 'feed_page_size' not in st.session_state:
        st.session_state['feed_page_size'] = '10'
    
    # Check for query params to update page
    query_params = st.query_params
    if 'page' in query_params:
        try:
            page_from_url = int(query_params['page'])
            if page_from_url > 0:
                st.session_state['feed_page'] = page_from_url
        except (ValueError, TypeError):
            pass
    
    # --- Load all data first for filtering and stats ---
    all_articles = []
    for _, p in candidates:
        data = load_json_if_exists(p)
        if data is None:
            continue
            
        is_analysis = os.path.basename(p).startswith('analysis_')
        
        if is_analysis:
            a = data
            src = a.get('source')
            title = a.get('title') or '-'
            url = a.get('url')
            score = a.get('score')
            label = a.get('label')
            
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
        
        # Get article date
        current_date = ''
        try:
            date_source = None
            if scraped_data and isinstance(scraped_data, dict):
                for key in ('fetched_at', 'fetched', 'added', 'created_at', 'published'):
                    if scraped_data.get(key):
                        date_source = scraped_data.get(key)
                        break

            if not date_source and isinstance(a, dict):
                for key in ('fetched_at', 'fetched', 'added', 'created_at', 'published', 'analyzed_at'):
                    if a.get(key):
                        date_source = a.get(key)
                        break

            if date_source:
                if isinstance(date_source, (int, float)):
                    current_date = datetime.fromtimestamp(float(date_source)).strftime('%Y-%m-%d')
                else:
                    try:
                        current_date = datetime.fromisoformat(str(date_source)).strftime('%Y-%m-%d')
                    except Exception:
                        try:
                            current_date = datetime.strptime(str(date_source)[:10], '%Y-%m-%d').strftime('%Y-%m-%d')
                        except Exception:
                            current_date = ''

            if not current_date:
                current_date = datetime.fromtimestamp(os.path.getmtime(p)).strftime('%Y-%m-%d')
        except Exception:
            current_date = ''
        
        all_articles.append({
            'path': p,
            'data': a,
            'scraped_data': scraped_data,
            'source': src,
            'title': title,
            'url': url,
            'score': score,
            'label': label,
            'date': current_date,
            'mtime': os.path.getmtime(p) if os.path.exists(p) else 0
        })
    
    # --- Filters and Sorting in Expander ---
    with st.expander("🔍 Filtry i sortowanie", expanded=True):
        # View mode selector
        if 'feed_layout' not in st.session_state:
            st.session_state['feed_layout'] = 'Dwie kolumny'
        
        # Mobile detection hint in UI
        st.markdown("""
        <style>
        @media (max-width: 900px) {
            /* Force single column layout on mobile regardless of user selection */
            div[data-testid="column"] {
                width: 100% !important;
                flex: 0 0 100% !important;
                max-width: 100% !important;
            }
            
            /* Make filter controls stack vertically */
            div[data-testid="stHorizontalBlock"] {
                flex-direction: column !important;
            }
            
            /* Adjust grid layouts to single column */
            [style*="grid-template-columns"] {
                grid-template-columns: 1fr !important;
            }
            
            /* Compact statistics on mobile */
            [style*="display:grid"] > div {
                margin-bottom: 1rem !important;
            }
        }
        
        @media (max-width: 600px) {
            /* Even more compact on small phones */
            .stSelectbox label, .stMultiSelect label {
                font-size: 0.85rem !important;
            }
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Initialize date filter in session state
        if 'feed_date_filter' not in st.session_state:
            st.session_state['feed_date_filter'] = 'Dzisiaj'
        
        layout_col, date_col, filter_col1, filter_col2, filter_col3, filter_col4 = st.columns([1, 1, 1, 1, 1, 1])
        
        with layout_col:
            layout_options = ['Jedna kolumna', 'Dwie kolumny', 'Kompaktowy']
            st.session_state['feed_layout'] = st.selectbox('📱 Widok', layout_options, index=layout_options.index(st.session_state['feed_layout']))
        
        with date_col:
            from datetime import datetime as dt
            today_str = dt.now().strftime('%Y-%m-%d')
            date_filter_options = ['Wszystkie', 'Dzisiaj', 'Ostatnie 7 dni', 'Ostatnie 30 dni']
            selected_date_filter = st.selectbox('📅 Data', date_filter_options, 
                                               index=date_filter_options.index(st.session_state['feed_date_filter']))
            st.session_state['feed_date_filter'] = selected_date_filter
            
            if selected_date_filter == 'Dzisiaj':
                all_articles = [art for art in all_articles if art['date'] == today_str]
            elif selected_date_filter == 'Ostatnie 7 dni':
                from datetime import timedelta
                cutoff_date = (dt.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                all_articles = [art for art in all_articles if art['date'] >= cutoff_date]
            elif selected_date_filter == 'Ostatnie 30 dni':
                from datetime import timedelta
                cutoff_date = (dt.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                all_articles = [art for art in all_articles if art['date'] >= cutoff_date]
        
        with filter_col1:
            sources = sorted(list(set([art['source'] for art in all_articles if art['source']])))
            selected_sources = st.multiselect('📰 Źródło', ['Wszystkie'] + sources, default=['Wszystkie'])
            if 'Wszystkie' not in selected_sources and selected_sources:
                all_articles = [art for art in all_articles if art['source'] in selected_sources]
        
        with filter_col2:
            labels = ['not_clickbait', 'mild', 'strong', 'extreme']
            label_display = {
                'not_clickbait': 'Godny Naśladowania', 
                'mild': 'Łagodny Clickbait', 
                'strong': 'Silny Clickbait', 
                'extreme': 'Ekstremalny Clickbait'
            }
            selected_labels = st.multiselect('🏷️ Etykieta', ['Wszystkie'] + [label_display.get(l, l) for l in labels], default=['Wszystkie'])
            if 'Wszystkie' not in selected_labels and selected_labels:
                reverse_map = {v: k for k, v in label_display.items()}
                selected_label_keys = [reverse_map.get(l, l) for l in selected_labels]
                all_articles = [art for art in all_articles if art['label'] in selected_label_keys]
        
        with filter_col3:
            min_score = st.number_input('📊 Min. wynik', min_value=0, max_value=100, value=0, step=5)
            max_score = st.number_input('📊 Max. wynik', min_value=0, max_value=100, value=100, step=5)
            all_articles = [art for art in all_articles if art['score'] is not None and min_score <= art['score'] <= max_score or art['score'] is None]
        
        with filter_col4:
            sort_options = {
                'Data (najnowsze)': lambda x: -x['mtime'],
                'Data (najstarsze)': lambda x: x['mtime'],
                'Wynik (malejąco)': lambda x: -(x['score'] if x['score'] is not None else -1),
                'Wynik (rosnąco)': lambda x: (x['score'] if x['score'] is not None else 999),
                'Źródło (A-Z)': lambda x: x['source'] or 'zzz',
            }
            selected_sort = st.selectbox('🔃 Sortowanie', list(sort_options.keys()))
            all_articles = sorted(all_articles, key=sort_options[selected_sort])
    
    filtered_total = len(all_articles)
    original_total = len(candidates)
    if filtered_total == 0:
        st.info("Brak artykułów spełniających kryteria filtrowania.")
        return
    
    # --- Visual separator with extra spacing ---
    st.markdown("<div style='margin:32px 0 16px 0;'></div>", unsafe_allow_html=True)
    
    # --- Results Section ---
    st.markdown("### Wyniki")
    
    # --- Pagination controls removed from top, only at bottom now ---

    # Determine slice of candidates to show based on pagination
    if st.session_state['feed_page_size'] == 'All':
        page_articles = all_articles
    else:
        page_size = int(st.session_state['feed_page_size'])
        page = max(1, int(st.session_state.get('feed_page', 1)))
        start = (page - 1) * page_size
        end = start + page_size
        page_articles = all_articles[start:end]

    shown = 0
    last_date = None
    
    for art in page_articles:
        a = art['data']
        scraped_data = art['scraped_data']
        current_date = art['date']
        
        if current_date and current_date != last_date:
            if last_date is not None:
                st.markdown("<div style='margin-top:40px;'></div>", unsafe_allow_html=True)
            
            st.markdown(
                f"""
                <div style='margin-top:32px;margin-bottom:32px;'>
                    <div style='font-size:32px;font-weight:700;color:#111827;margin-bottom:10px;text-shadow:0 2px 4px rgba(0,0,0,0.1);'>📅 {current_date}</div>
                    <div style='border-bottom:3px solid #667eea;width:120px;'></div>
                </div>
                """, 
                unsafe_allow_html=True
            )
            last_date = current_date

        # Header card
        suggested = a.get('suggestions', {}).get('rewrite_title_neutral') if isinstance(a.get('suggestions'), dict) else None
        rationale = a.get('rationale_user_friendly', [])
        image_url_local = None
        
        if scraped_data:
            meta = scraped_data.get('meta') if isinstance(scraped_data.get('meta'), dict) else {}
            image_url_local = (
                scraped_data.get('lead_image_url') or 
                scraped_data.get('image') or 
                meta.get('og:image') or 
                meta.get('twitter:image')
            )
        
        if not image_url_local and art['url']:
            try:
                candidate = fetch_image_from_page(art['url'])
                if candidate:
                    image_url_local = candidate
            except Exception:
                pass

        image_block = render_image_block_compact(image_url_local, art['url'])
        
        # Build summary block if available
        summary_text = a.get('summary', '')
        if summary_text and summary_text.strip():
            summary_block = f"""
  <div style='margin-top:20px;padding:16px;background:#f9fafb;border-left:3px solid #3b82f6;border-radius:6px;'>
    <div class="helper-text" style='font-size:11px;margin-bottom:8px;color:#9ca3af;text-transform:uppercase;letter-spacing:0.5px;font-weight:600;'>Podsumowanie</div>
    <div style='font-size:14px;line-height:1.6;color:#374151;'>{html.escape(summary_text)}</div>
  </div>
"""
        else:
            summary_block = ""
        
        header_card = render_simple_header_card_with_suggestion(art['title'], art['source'], suggested, image_block, art['url'], summary_block)
        score_card = render_score_card_with_rationale(art['score'], art['label'], rationale)

        # Adjust layout based on selected view mode
        layout_mode = st.session_state.get('feed_layout', 'Dwie kolumny')
        
        if layout_mode == 'Kompaktowy':
            # Get badge HTML for compact view
            badge_html = _get_label_badge_html(art['label'], size=36)
            label_display = get_label_display_name(art['label'])
            
            # Compact: horizontal layout with image on left, info in middle, score on right
            article_card = f"""
<div style='padding:8px;'>
  <div style='display:grid;grid-template-columns:200px 2fr 1fr;gap:16px;border:1px solid #e5e7eb;border-radius:12px;padding:16px;background:#fff;box-shadow:0 1px 3px rgba(0,0,0,0.08);transition:all 0.3s ease;' onmouseover='this.style.boxShadow="0 8px 24px rgba(0,0,0,0.12)";this.style.transform="translateY(-2px)"' onmouseout='this.style.boxShadow="0 1px 3px rgba(0,0,0,0.08)";this.style.transform="translateY(0)"'>
    <div>{image_block if image_url_local else '<div style="width:200px;height:150px;background:#f3f4f6;border-radius:8px;"></div>'}</div>
    <div>
      <div style='font-size:18px;font-weight:700;margin-bottom:8px;'>{html.escape(art['title'])}</div>
      <div style='font-size:14px;color:#6b7280;margin-bottom:8px;'>📰 {html.escape(art['source'] or '')}</div>
      {f"<div style='font-size:14px;color:#111827;font-weight:500;'>✨ {html.escape(suggested)}</div>" if suggested else ''}
    </div>
    <div style='text-align:center;display:flex;flex-direction:column;justify-content:center;align-items:center;'>
      <div style='margin-bottom:8px;'>{badge_html}</div>
      <div style='font-size:42px;font-weight:800;color:{get_score_color(art['score'], art['label'])};'>{format_score_display(art['score'])}</div>
      <div style='font-size:14px;font-weight:700;color:{get_score_color(art['score'], art['label'])};margin-top:8px;'>{html.escape(label_display)}</div>
    </div>
  </div>
</div>
"""
            columns_per_row = 1  # Compact mode: one per row
        elif layout_mode == 'Jedna kolumna':
            # Single column: full width
            article_card = f"""
<div style='padding:10px;'>
  <div style='display:grid;grid-template-columns:3fr minmax(280px,1fr);gap:20px;'>
    {header_card}
    {score_card}
  </div>
</div>
"""
            columns_per_row = 1
        else:
            # Two columns (default)
            article_card = f"""
<div style='padding:10px;'>
  <div style='display:grid;grid-template-columns:3fr minmax(220px,1fr);gap:16px;'>
    {header_card}
    {score_card}
  </div>
</div>
"""
            columns_per_row = 2

        if '__feed_row_buffer' not in st.session_state:
            st.session_state['__feed_row_buffer'] = []

        if st.session_state['__feed_row_buffer'] and current_date != last_date:
            buf = st.session_state['__feed_row_buffer']
            cols_per_row = st.session_state.get('__cols_per_row', 2)
            for i in range(0, len(buf), cols_per_row):
                row = buf[i:i+cols_per_row]
                cols = st.columns(len(row))
                for j, card_html in enumerate(row):
                    with cols[j]:
                        st.markdown(card_html, unsafe_allow_html=True)
                st.markdown("<div style='margin-bottom:24px;'></div>", unsafe_allow_html=True)
            st.session_state['__feed_row_buffer'] = []

        st.session_state['__feed_row_buffer'].append(article_card)
        st.session_state['__cols_per_row'] = columns_per_row

        if len(st.session_state['__feed_row_buffer']) >= columns_per_row:
            buf = st.session_state['__feed_row_buffer']
            row = buf[:columns_per_row]
            cols = st.columns(columns_per_row)
            for j, card_html in enumerate(row):
                with cols[j]:
                    st.markdown(card_html, unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom:24px;'></div>", unsafe_allow_html=True)
            st.session_state['__feed_row_buffer'] = buf[columns_per_row:]

        shown += 1

    if '__feed_row_buffer' in st.session_state and st.session_state['__feed_row_buffer']:
        buf = st.session_state['__feed_row_buffer']
        cols_per_row = st.session_state.get('__cols_per_row', 2)
        for i in range(0, len(buf), cols_per_row):
            row = buf[i:i+cols_per_row]
            cols = st.columns(len(row))
            for j, card_html in enumerate(row):
                with cols[j]:
                    st.markdown(card_html, unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom:24px;'></div>", unsafe_allow_html=True)
        st.session_state['__feed_row_buffer'] = []
    
    # --- Pagination controls (bottom) ---
    st.markdown("<hr style='margin:32px 0;border:none;border-top:2px solid #e5e7eb;'>", unsafe_allow_html=True)
    _render_pagination_controls(filtered_total)
