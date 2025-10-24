"""Scraper related sidebar components (moved from sidebar.py)."""

import os
import sys
import yaml
from glob import glob as glob_files
import streamlit as st

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import safe_rerun


def initialize_scraper():
    """Try to import scraper functions.
    Returns:
        Tuple of (scraper_available, fetch_and_save_url, scrape_listing_for_source).
    """
    scraper_available = False
    fetch_and_save_url = None
    scrape_listing_for_source = None

    try:
        # Prefer import as package module
        import importlib
        mod = importlib.import_module('clickbait_verifier.scraper')
        fetch_and_save_url = getattr(mod, 'fetch_and_save_url', None)
        scrape_listing_for_source = getattr(mod, 'scrape_listing_for_source', None)
        if fetch_and_save_url:
            scraper_available = True
    except Exception:
        try:
            # Fallback: add repo root to sys.path and import scraper by name
            repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            if repo_root not in sys.path:
                sys.path.insert(0, repo_root)
            from scraper import fetch_and_save_url as _fetch_fn
            from scraper import scrape_listing_for_source as _scrape_listing
            fetch_and_save_url = _fetch_fn
            scrape_listing_for_source = _scrape_listing
            scraper_available = True
        except Exception:
            scraper_available = False

    return scraper_available, fetch_and_save_url, scrape_listing_for_source


def render_url_scraper(scraped_dir: str, scraper_available: bool, fetch_and_save_url):
    """Render URL scraping section."""
    st.header('Scrapuj URL')
    input_url = st.text_input('URL do zescrapowania')

    if st.button('Scrapuj'):
        if not input_url:
            st.error('Podaj URL przed rozpoczęciem scrapowania')
        elif not scraper_available:
            st.error('Funkcja scrapowania nie jest dostępna (problem z importem scraper.py)')
        else:
            with st.spinner('Pobieram...'):
                result = fetch_and_save_url(input_url, source_name='CLI', fetch_method='auto')

            if not result:
                st.error('Scrapowanie nie powiodło się. Sprawdź komunikaty w terminalu serwera.')
            else:
                # Support new structured return {id, existed} or legacy int
                if isinstance(result, dict):
                    sid = result.get('id')
                    existed = result.get('existed', False)
                else:
                    sid = int(result)
                    existed = False

                if existed:
                    st.info(f'URL już istnieje w DB (id={sid}) — pomijam ponowne zapisanie.')
                else:
                    st.success(f'Zapisano artykuł w DB (id={sid})')

                # Find latest scraped file for this id
                pattern = os.path.join(scraped_dir, f'scraped_{sid}*.json')
                matches = sorted(glob_files(pattern))
                if matches:
                    latest = matches[-1]
                    rel = os.path.relpath(latest, start=os.getcwd())
                    st.markdown(f'Plik scraped: `{rel}`')
                    try:
                        st.session_state['last_scraped_path'] = os.path.normpath(latest)
                    except Exception:
                        pass
                    safe_rerun()
                else:
                    if existed:
                        st.warning('URL jest w bazie danych, ale nie znaleziono odpowiadającego pliku scraped_*.json')
                    else:
                        st.info('Nie znaleziono pliku scraped_* dla zapisanego id — sprawdź logi serwera.')


def render_service_scraper(scraped_dir: str, scraper_available: bool, scrape_listing_for_source):
    """Render service scraping section."""
    st.header('Scrapuj dzisiaj z serwisu')

    # Load sources from config
    try:
        cfg = yaml.safe_load(open('config.yaml'))
        cfg_sources = [s for s in cfg.get('sources', []) if s.get('enabled', True) and s.get('scrape_listing')]
        source_names = [s.get('name') for s in cfg_sources]
    except Exception:
        cfg_sources = []
        source_names = []

    if source_names:
        selected_service = st.selectbox(
            'Wybierz serwis',
            ['-- wybierz --'] + source_names,
            index=0,
            key='sidebar_service_select'
        )

        if selected_service and selected_service != '-- wybierz --':
            if st.button('Zescrapuj dzisiaj'):
                if not scraper_available:
                    st.error('Funkcja scrapowania nie jest dostępna (problem z importem scraper.py)')
                else:
                    with st.spinner(f'Scrapuję artykuły z {selected_service}...'):
                        try:
                            results = scrape_listing_for_source(selected_service)
                            added = [r for r in results if r.get('id') and not r.get('skipped')]
                            skipped = [r for r in results if r.get('skipped')]

                            st.success(f'Dodano {len(added)} nowych artykułów z {selected_service}')
                            if skipped:
                                st.info(f'Pominięto {len(skipped)} pozycji (już istniały lub nie były z dzisiaj)')

                            # Show list of added files
                            for r in added[:10]:
                                st.markdown(f"- `{os.path.relpath(r.get('path'), start=os.getcwd())}`")

                            # Set last_scraped_path to most recent added if any
                            if added:
                                latest = added[-1]['path']
                                try:
                                    st.session_state['last_scraped_path'] = os.path.normpath(latest)
                                except Exception:
                                    pass
                                safe_rerun()
                        except Exception as e:
                            st.error(f'Błąd podczas scrapowania: {e}')
    else:
        st.info('Brak skonfigurowanych serwisów z opcją scrape_listing w config.yaml')
