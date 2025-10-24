"""CSS styling for the Streamlit application."""


def get_custom_css() -> str:
    """Return custom CSS styles for the application.
    
    Typography overrides (fonts, weights, colors) — only visual styles, no layout changes.
    """
    return """
<style>
    /* Global font family */
    :root { font-family: 'Inter', Roboto, 'Helvetica Neue', Arial, sans-serif; }

    /* Page title */
    h1 {
        font-size: 36px !important; /* requested 36px */
        font-weight: 700 !important; /* bold */
        color: #1f2937 !important;
        margin-bottom: 1rem !important;
    }

    /* Section headers (e.g. Uzasadnienie, Wynik) */
    h2, h3, .section-header {
        font-size: 24px !important; /* requested 24px */
        font-weight: 600 !important; /* semibold */
        color: #1f2937 !important;
        margin-bottom: 0.9rem !important;
    }

    /* Original article title inside cards */
    .article-title {
        font-size: 24px !important; /* match score label size */
        font-weight: 700 !important; /* bold */
        color: #1f2937 !important;
        margin-bottom: 0.5rem !important;
    }

    /* Suggested title */
    .suggested-title {
        font-size: 17px !important; /* requested 17px */
        font-weight: 500 !important; /* medium */
        color: #374151 !important;
        margin-bottom: 0.6rem !important;
    }

    /* Score card */
    .score-label {
        font-size: 24px !important; /* section header scale */
        font-weight: 600 !important;
        color: #374151 !important;
        margin-bottom: 0.5rem !important;
    }
    .score-value {
        font-size: 48px !important; /* requested 48px */
        font-weight: 700 !important; /* bold */
        color: inherit !important; /* color will be set inline based on label */
        line-height: 1 !important;
    }
    .score-label-text {
        font-size: 18px !important; /* label (mild/strong/neutral) */
        font-weight: 600 !important; /* semibold */
        color: inherit !important;
        margin-top: 0.5rem !important;
    }

    /* Rationale list items */
    .rationale-item {
        font-size: 17px !important; /* requested 17px */
        font-weight: 400 !important; /* regular */
        line-height: 1.6 !important;
        color: #374151 !important;
        margin-bottom: 0.9rem !important;
    }

    /* Utility small text (selectors, helper labels) */
    .helper-text {
        font-size: 15px !important;
        color: #6b7280 !important;
    }

    /* Image caption */
    .img-caption {
        font-size: 14px !important;
        font-style: italic !important;
        color: #6b7280 !important;
        margin-top: 0.5rem !important;
        margin-bottom: 1rem !important;
    }

    /* Ensure margins between sections */
    .section-space { margin-bottom: 1rem !important; }

    /* Prevent shadows or decorative effects from being added */
    .no-decor { box-shadow: none !important; }

    /* Hide Streamlit multipage navigation completely (single-page UX) */
    div[data-testid="stSidebarNav"],
    ul[data-testid="stSidebarNav"],
    ul[data-testid="stSidebarNavItems"] {
        display: none !important;
    }

    /* Style the view selector radio in the sidebar to look like button pills */
    /* Target radios inside the sidebar specifically */
    div[data-testid="stSidebar"] [data-testid="stRadio"] .stRadio > label {
        display: inline-flex !important;
        gap: 0.25rem !important;
        align-items: center !important;
        margin: 0.25rem 0 !important;
    }

    div[data-testid="stSidebar"] [data-testid="stRadio"] .stRadio > label > div {
        /* hide native radio circle visually (we'll style the button) */
        display: none !important;
    }

    div[data-testid="stSidebar"] [data-testid="stRadio"] .stRadio > label > span {
        display: inline-block !important;
        padding: 8px 14px !important;
        border-radius: 999px !important; /* pill */
        background: #f3f4f6 !important; /* light gray */
        color: #111827 !important;
        border: 1px solid transparent !important;
        font-weight: 600 !important;
        cursor: pointer !important;
    }

    /* Selected state */
    div[data-testid="stSidebar"] [data-testid="stRadio"] .stRadio > label[aria-checked="true"] > span {
        background: #ef4444 !important; /* red */
        color: white !important;
        border-color: #ef4444 !important;
    }

    /* Hover/focus */
    div[data-testid="stSidebar"] [data-testid="stRadio"] .stRadio > label:hover > span,
    div[data-testid="stSidebar"] [data-testid="stRadio"] .stRadio > label:focus > span {
        box-shadow: 0 1px 4px rgba(0,0,0,0.08) !important;
        transform: translateY(-1px) !important;
    }

    /* Make sure long labels wrap nicely and buttons align vertically */
    div[data-testid="stSidebar"] [data-testid="stRadio"] .stRadio > label > span {
        white-space: nowrap !important;
    }

</style>
"""
