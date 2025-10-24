"""Streamlit Clickbait Verifier - Analytics View logic."""

import streamlit as st

# (Chooser click handler removed per user request)
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.styling import get_custom_css
from ui.sidebar import render_sidebar
from ui.analysis_view import render_analysis_view
from ui.feed_view import render_feed
from ui.dashboard_view import render_dashboard
from ui.scraper_view import render_scraper_view
from utils.file_loader import (
    FileConfig,
    get_analysis_files,
    get_scraped_files,
    build_display_map,
    load_analysis_data,
    get_candidates_for_feed,
)


def initialize_app(main_heading: str, page_title: str = "Clickbait Verifier — Analytics View"):
    """Initialize Streamlit app configuration and styling."""
    try:
        st.set_page_config(page_title=page_title, layout="wide")
    except Exception:
        # Streamlit raises when page config was already set (e.g., rerun)
        pass
    st.title(main_heading)
    st.markdown(get_custom_css(), unsafe_allow_html=True)


def get_file_config() -> FileConfig:
    """Get file configuration for reports directories.
    
    Returns:
        FileConfig object with directory paths.
    """
    reports_dir = os.path.join(os.path.dirname(__file__), '..', 'reports')
    return FileConfig(reports_dir)


def get_selection_index(choices: list, display_map: dict) -> int:
    """Determine default selection index based on last scraped path.
    
    Args:
        choices: List of display choices.
        display_map: Map of display names to file info.
        
    Returns:
        Index of the selection to use as default.
    """
    default_index = 0
    last_path = st.session_state.get('last_scraped_path')
    
    if last_path:
        for idx, key in enumerate(choices):
            info = display_map.get(key)
            if info and info.get('path'):
                if os.path.normpath(info.get('path')) == os.path.normpath(last_path):
                    default_index = idx
                    break
    
    return default_index



def render_analytics_view_full(analysis, scraped_path, analysis_name, config, analysis_files, scraped_files):
    """Render the full analytics view with all controls and prompt generator."""
    # --- MAIN ANALYSIS VIEW ---
    # (Scraper controls were moved to a dedicated 'Scraper' view.)
    render_analysis_view(analysis, scraped_path, analysis_name)

def main():
    """Render the Analytics View."""
    # Initialize app
    initialize_app("Clickbait Verifier — przegląd analiz")

    # Get file configuration
    config = get_file_config()

    # Load files
    analysis_files = get_analysis_files(config.analysis_dir)
    scraped_files = get_scraped_files(config.scraped_dir)

    # Build display map
    display_map = build_display_map(analysis_files, scraped_files)

    # Handle empty state
    if not display_map:
        st.warning(
            'Brak plików analizy ani zeskrapowanych artykułów w katalogu reports/. '
            'Możesz użyć panelu poniżej, aby zescrapować URL.'
        )
        display_map['(brak plików) Użyj panelu scrapowania poniżej'] = {
            'type': 'none', 
            'path': None
        }

    # Move view selection to sidebar (render a header above the radio)
    view_options = ['Article View', 'Dashboard', 'Feed View', 'Scraper']
    default_view = st.session_state.get('selected_view', view_options[0])
    try:
        selected_index = view_options.index(default_view)
    except ValueError:
        selected_index = 0

    with st.sidebar:
        st.markdown('### Wybierz widok')
        # Use a non-empty (whitespace) label to avoid Streamlit label warnings
        # while keeping the visible header above the control.
        # Also clamp the index to a valid range in case session state contained
        # an out-of-range value from a previous run.
        safe_index = max(0, min(selected_index, len(view_options) - 1))
        view = st.radio(label=' ', options=view_options, index=safe_index, key='selected_view_radio')
    st.session_state['selected_view'] = view

    if view == 'Article View':
        choices = list(display_map.keys())

        # Analysis view: allow selecting analysis/scraped file
        default_index = get_selection_index(choices, display_map)
        sel = st.selectbox(
            'Wybierz analizę / zescrapowany artykuł',
            choices,
            index=default_index,
            key='main_analysis_select'
        )
        sel_info = display_map[sel]

        analysis, scraped_path, analysis_name = load_analysis_data(sel_info, config.scraped_dir)

        # Render sidebar but disable the prompt generator here because the
        # prompt generator is rendered at the bottom of the main analysis view
        # (to match previous UX where prompt lived in the analytics page).
        try:
            render_sidebar()
        except Exception:
            pass

        render_analytics_view_full(analysis, scraped_path, analysis_name, config, analysis_files, scraped_files)
    elif view == 'Dashboard':
        # Render sidebar for dashboard (no per-article prompts)
        try:
            render_sidebar()
        except Exception:
            pass

        # Render dashboard using available analysis files
        render_dashboard(analysis_files)
    elif view == 'Scraper':
        # Dedicated Scraper view: render scrapers in the main area (not sidebar)
        try:
            render_sidebar()
        except Exception:
            pass

        render_scraper_view(config.scraped_dir)

    else:
        # Build feed candidates and render feed (no analysis selector in Feed view)
        candidates = get_candidates_for_feed(analysis_files, scraped_files)
        # For the Feed view we show scrapers in the sidebar but hide the prompt
        # generator (it only applies to per-article Analysis view).
        try:
            render_sidebar()
        except Exception:
            pass

        render_feed(candidates)


if __name__ == "__main__":
    main()
