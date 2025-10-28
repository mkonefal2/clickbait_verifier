"""
Standalone Streamlit Scraper Application

Aplikacja do scrapowania artykułów z różnych źródeł.
"""

import streamlit as st
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.scraper_view import render_scraper_view

# Page configuration
st.set_page_config(
    page_title="Scraper - Clickbait Verifier",
    page_icon="🕷️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
/* Main container styling */
.main {
    padding: 2rem;
}

/* Header styling */
h1 {
    color: #667eea;
    font-weight: 700;
    margin-bottom: 1rem;
}

h2 {
    color: #764ba2;
    font-weight: 600;
    margin-top: 2rem;
    margin-bottom: 1rem;
}

/* Card-like sections */
.stExpander {
    background-color: #f9fafb;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
    margin-bottom: 1rem;
}

/* Button styling */
.stButton button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    font-weight: 600;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1.5rem;
    transition: all 0.3s ease;
}

.stButton button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

/* Input fields */
.stTextInput input, .stSelectbox select {
    border-radius: 8px;
    border: 1px solid #e5e7eb;
}

/* DataFrame styling */
.dataframe {
    border-radius: 8px;
    overflow: hidden;
}

/* Success/Error/Info messages */
.stSuccess, .stError, .stWarning, .stInfo {
    border-radius: 8px;
    padding: 1rem;
}

/* Responsive design */
@media (max-width: 768px) {
    .main {
        padding: 1rem;
    }
}
</style>
""", unsafe_allow_html=True)

def main():
    """Main application entry point."""
    
    # Header with icon
    st.markdown("""
    <div style='background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding:20px;
                border-radius:12px;
                margin-bottom:2rem;
                box-shadow:0 4px 12px rgba(102,126,234,0.3);'>
        <h1 style='color:white;margin:0;font-size:2rem;text-align:center;'>
            🕷️ Scraper Artykułów
        </h1>
        <p style='color:white;margin:0.5rem 0 0 0;text-align:center;opacity:0.9;'>
            Narzędzie do pobierania i zarządzania artykułami z różnych źródeł
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Determine scraped directory
    scraped_dir = os.path.join(os.path.dirname(__file__), '..', 'reports', 'scraped')
    scraped_dir = os.path.normpath(scraped_dir)
    
    # Ensure directory exists
    os.makedirs(scraped_dir, exist_ok=True)
    
    # Info about current directory
    with st.expander("ℹ️ Informacje o konfiguracji", expanded=False):
        st.info(f"**Katalog scraped:** `{os.path.relpath(scraped_dir, start=os.getcwd())}`")
        st.info(f"**Katalog roboczy:** `{os.getcwd()}`")
    
    # Render main scraper view
    try:
        render_scraper_view(scraped_dir)
    except Exception as e:
        st.error(f"❌ Błąd podczas renderowania widoku scrapera: {e}")
        st.exception(e)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align:center;color:#6b7280;padding:2rem 0;'>
        <p>Clickbait Verifier - Scraper © 2025</p>
        <p style='font-size:0.9rem;margin-top:0.5rem;'>
            Scrapuj odpowiedzialnie • Respektuj robots.txt • Nie nadużywaj serwisów
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
