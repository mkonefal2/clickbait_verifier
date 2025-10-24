"""Main-page scraper view.

This module renders the scraper UI inside the main application area (not the
sidebar). It reuses the existing functions in `ui.sidebar_scrapers` but keeps
the layout and presentation separate so `streamlit_app.py` stays concise.
"""

import streamlit as st
from typing import Optional, List

from ui.sidebar_scrapers import initialize_scraper, render_url_scraper, render_service_scraper
from utils.file_loader import get_scraped_files, get_analysis_files, load_json_if_exists
import os
import pandas as pd


def render_scraper_view(scraped_dir: str):
    """Render scraper UI in the main page area using a two-column layout.

    Args:
        scraped_dir: path to the directory where scraped files are stored.
    """
    st.title('Scraper')
    st.markdown('Użyj poniższych narzędzi, aby dodać/zescrapować artykuły.')

    # Two-column layout for scrapers and service
    col_scraper, col_service = st.columns(2)
    scraper_available, fetch_and_save_url, scrape_listing_for_source = initialize_scraper()

    with col_scraper:
        try:
            render_url_scraper(scraped_dir, scraper_available, fetch_and_save_url)
        except Exception as e:
            st.error(f'Błąd renderowania URL scraper: {e}')

    with col_service:
        try:
            if scrape_listing_for_source:
                render_service_scraper(scraped_dir, scraper_available, scrape_listing_for_source)
            else:
                st.info('Funkcja scrapowania list serwisów nie jest dostępna.')
        except Exception as e:
            st.error(f'Błąd renderowania service scraper: {e}')

    # Show table of scraped files and whether they have been analyzed
    try:
        st.header('Lista zeskrapowanych plików')

        scraped_files = get_scraped_files(scraped_dir)
        analysis_files = get_analysis_files(os.path.join(os.path.dirname(scraped_dir), 'analysis'))

        # Build a set of analyzed ids from analysis files
        analyzed_ids = set()
        for af in analysis_files:
            a = load_json_if_exists(af) or {}
            if a.get('id') is not None:
                analyzed_ids.add(a.get('id'))

        rows = []
        for sf in scraped_files:
            s = load_json_if_exists(sf) or {}
            sid = s.get('id')
            source = s.get('source') or ''
            title = s.get('title') or os.path.basename(sf)
            analyzed = 'Tak' if (sid is not None and sid in analyzed_ids) else 'Nie'
            rows.append({'plik': os.path.relpath(sf, start=os.getcwd()), 'źródło': source, 'tytuł': title, 'analiza': analyzed})

        if rows:
            df = pd.DataFrame(rows)

            # Filter controls: show all or only not-analyzed
            filter_opt = st.selectbox('Pokaż', ['Wszystkie', 'Tylko nieprzeanalizowane'], index=0, key='scraper_table_filter')
            if filter_opt == 'Tylko nieprzeanalizowane':
                df = df[df['analiza'] == 'Nie']

            # Allow sorting/viewing in Streamlit
            st.dataframe(df)
            # Provide an action to remove/move all not-analyzed files
            st.markdown('---')
            st.subheader('Zarządzaj nieprzeanalizowanymi')
            remove_confirm = st.checkbox('Potwierdzam, chcę usunąć (przenieść) wszystkie nieprzeanalizowane pliki', key='scraper_remove_confirm')
            remove_button = st.button('Usuń wszystkie nieprzeanalizowane')

            if remove_button:
                if not remove_confirm:
                    st.warning('Aby usunąć pliki, zaznacz pole potwierdzenia.')
                else:
                    # Move files to removed subdirectory inside scraped_dir
                    removed_dir = os.path.join(scraped_dir, 'removed')
                    os.makedirs(removed_dir, exist_ok=True)
                    moved = []
                    failed = []
                    for r in rows:
                        try:
                            if r.get('analiza') == 'Nie':
                                src_path = os.path.normpath(os.path.join(os.getcwd(), r.get('plik')))
                                # Ensure path is under scraped_dir for safety
                                if os.path.commonpath([os.path.normpath(scraped_dir)]) != os.path.commonpath([os.path.normpath(scraped_dir), src_path]):
                                    failed.append((r.get('plik'), 'Poza katalogiem scraped'))
                                    continue
                                dst = os.path.join(removed_dir, os.path.basename(src_path))
                                os.replace(src_path, dst)
                                moved.append(os.path.relpath(dst, start=os.getcwd()))
                        except Exception as e:
                            failed.append((r.get('plik'), str(e)))

                    st.success(f'Przeniesiono {len(moved)} plików do `{os.path.relpath(removed_dir, start=os.getcwd())}`')
                    if failed:
                        st.error(f'Błędy podczas przenoszenia {len(failed)} plików. Pierwszy błąd: {failed[0]}')
        else:
            st.info('Brak plików scraped_*.json w katalogu raportów.')
    except Exception as e:
        st.error(f'Błąd podczas budowania tabeli zeskrapowanych plików: {e}')
