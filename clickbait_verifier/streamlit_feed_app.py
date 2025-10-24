"""Dedicated Streamlit entry point that renders the Feed view only."""

import os
import sys
import streamlit as st

# Ensure package imports work when running via `streamlit run` directly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from streamlit_app import initialize_app, get_file_config  # Reuse shared setup helpers
from ui.feed_view import render_feed
from utils.file_loader import get_analysis_files, get_scraped_files, get_candidates_for_feed


def main():
    """Render the standalone Feed view application."""
    initialize_app(
        "Clickbait Verifier — przegląd feedu",
        page_title="Clickbait Verifier — Feed View",
    )

    config = get_file_config()
    analysis_files = get_analysis_files(config.analysis_dir)
    scraped_files = get_scraped_files(config.scraped_dir)
    candidates = get_candidates_for_feed(analysis_files, scraped_files)

    if not candidates:
        st.info("Brak danych do wyświetlenia w widoku feedu.")
        return

    render_feed(candidates)


if __name__ == "__main__":
    main()
