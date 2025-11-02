"""Analysis view for displaying article analysis."""

import streamlit as st
import os
import sys
import json
import html
from typing import Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.file_loader import load_json_if_exists
from utils.helpers import fetch_image_from_page
from ui.components import (
    render_header_card, 
    render_score_card, 
    render_rationale_card,
    render_image_block,
    render_badges_card
)


def render_prompt_generator(scraped_path: str):
        """Render prompt generator (inlined here to avoid external module import).

        This mirrors the previous `ui.sidebar_prompt.render_prompt_generator` behavior
        but lives inside the analysis view so the prompt appears at the bottom of
        the article analysis page.
        """
        if not scraped_path:
                st.info('Brak powiązanego pliku scraped_*.json')
                return

        spec_rel = os.path.relpath(
                os.path.join(os.path.dirname(__file__), '../..', 'clickbait_agent_spec_v1.1.yaml'),
                start=os.getcwd(),
        )
        rel_scraped = os.path.relpath(scraped_path, start=os.getcwd())

        prompt_text = (
                f"Przeanalizuj plik JSON zeskrapowanego artykułu: {rel_scraped}\n"
                f"Użyj instrukcji i kryteriów zawartych w pliku '{spec_rel}'.\n"
                "DODATKOWO: Zapisz wygenerowany JSON do pliku o nazwie 'analysis_{id}.json' w katalogu "
                "'reports/analysis' (gdzie {id} to id artykułu z pliku scraped). Jeżeli plik o tej nazwie "
                "już istnieje, dopisz numerowany sufiks (np. analysis_{id}_1.json), aby nie nadpisać "
                "istniejącego pliku.\n"
        )

        try:
                import streamlit.components.v1 as components
                js_prompt = json.dumps(prompt_text)
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


def prepare_scraped_metadata(analysis: dict, scraped_path: Optional[str]) -> tuple:
    """Prepare metadata from scraped file.
    
    Args:
        analysis: Analysis dictionary.
        scraped_path: Path to scraped file.
        
    Returns:
        Tuple of (scraped dict, orig_url, image_url, scraped_name).
    """
    scraped = {}
    orig_url = analysis.get('url')
    image_url = None
    scraped_name = None
    
    if scraped_path:
        scraped_name = os.path.basename(scraped_path)
        scraped = load_json_if_exists(scraped_path) or {}
        
        # Use analysis.url if present, otherwise fallback to scraped url
        orig_url = orig_url or scraped.get('url')
        
        # Common keys where image might be stored
        candidates = [
            'lead_image_url', 'top_image', 'image', 'thumbnail', 
            'og_image', 'thumbnail_url'
        ]
        meta = scraped.get('meta') if isinstance(scraped.get('meta'), dict) else {}
        
        for k in candidates:
            val = scraped.get(k)
            if val:
                image_url = val
                break
        
        if not image_url:
            image_url = meta.get('og:image') or meta.get('image') or meta.get('twitter:image')
    
    # If no image was found but we have the original URL, try to fetch a thumbnail
    if not image_url and orig_url:
        try:
            with st.spinner('Pobieram miniaturę z artykułu...'):
                candidate = fetch_image_from_page(orig_url)
                if candidate:
                    image_url = candidate
        except Exception:
            pass
    
    return scraped, orig_url, image_url, scraped_name


def render_analysis_view(analysis: dict, scraped_path: Optional[str], analysis_name: Optional[str]):
    """Render the main analysis view.
    
    Args:
        analysis: Analysis dictionary.
        scraped_path: Path to scraped file.
        analysis_name: Name of the analysis file.
    """
    scraped, orig_url, image_url, scraped_name = prepare_scraped_metadata(analysis, scraped_path)
    
    # Precompute image HTML block
    image_block_html = render_image_block(image_url, orig_url)
    
    # Precompute summary block
    summary_text = analysis.get('summary', '')
    if summary_text and summary_text.strip():
        summary_block_html = f"""
  <div style='margin-top:20px;padding:16px;background:#f9fafb;border-left:3px solid #3b82f6;border-radius:6px;'>
    <div class="helper-text" style='font-size:11px;margin-bottom:8px;color:#9ca3af;text-transform:uppercase;letter-spacing:0.5px;font-weight:600;'>Podsumowanie</div>
    <div style='font-size:16px;line-height:1.6;color:#374151;font-weight:400;'>{html.escape(summary_text)}</div>
  </div>
"""
    else:
        summary_block_html = ""
    
    # Create two-column layout: left for content, right for rationale
    col_left, col_right = st.columns([3, 2])
    
    with col_left:
        # Render header card
        try:
            original_title = analysis.get('title') or '-'
            suggested = analysis.get('suggestions', {}).get('rewrite_title_neutral')
            
            header_card = render_header_card(original_title, suggested, image_block_html, summary_block_html)
            st.markdown(header_card, unsafe_allow_html=True)
        except Exception:
            # Fallback to simple text display
            st.header(analysis.get('title') or '-')
            suggested = analysis.get('suggestions', {}).get('rewrite_title_neutral')
            if suggested:
                st.markdown(f"**Sugerowany tytuł (neutralny):** {suggested}")
            else:
                st.markdown("**Sugerowany tytuł (neutralny):** - brak sugestii -")
    
    with col_right:
        # Score card
        try:
            score_val = analysis.get('score')
            label_val = analysis.get('label')
            
            score_card = render_score_card(score_val, label_val)
            st.markdown(score_card, unsafe_allow_html=True)
        except Exception:
            # Fallback numeric metric
            st.metric(label='Wynik (score)', value=analysis.get('score'))
        
        # Rationale card
        rationale = analysis.get('rationale_user_friendly', []) or []
        try:
            rationale_card = render_rationale_card(rationale)
            st.markdown(rationale_card, unsafe_allow_html=True)
        except Exception:
            # Fallback to simple list rendering
            st.subheader('Uzasadnienie')
            if rationale:
                for i, r in enumerate(rationale, 1):
                    st.markdown(f"{i}. {r}")
            else:
                st.info('- brak uzasadnienia -')

        # Badges display removed per user request
    
    
    # Signals at the bottom
    with st.expander('Główne sygnały'):
        st.json(analysis.get('signals', {}))
    
    # Show scraped/analysis source filenames as footer
    if scraped_name or analysis_name:
        try:
            if scraped_name:
                st.markdown(f"**Źródło scraped:** `{scraped_name}`")
            if analysis_name:
                st.markdown(f"**Plik analizy:** `{analysis_name}`")
        except Exception:
            pass

    # Prompt generator at the bottom of the analysis view (user requested)
    try:
        st.markdown('---')
        render_prompt_generator(scraped_path)
    except Exception:
        # Don't break the view if prompt rendering fails
        pass
