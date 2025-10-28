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

/* === Responsive / Mobile / narrow-tablet tweaks === */
/* Raise breakpoint to 900px so responsive rules apply in device emulators
    and narrow/tablet viewports (e.g., 818px preview). */
@media (max-width: 900px) {
    /* Tighten page padding for small screens */
    .block-container {
        padding: 0.5rem !important;
        max-width: 100% !important;
        margin: 0 auto !important;
    }

    /* Scale down large headings and body copy for readability on mobile */
    h1 {
        font-size: 1.5rem !important;
        line-height: 1.3 !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.8rem !important;
    }
    
    h2, h3 {
        font-size: 1.2rem !important;
        line-height: 1.3rem !important;
        margin-top: 0.4rem !important;
        margin-bottom: 0.6rem !important;
    }
    
    p, span, div, label {
        font-size: 0.95rem !important;
    }

    /* Columns should stack vertically on small screens. Force a single
       column layout for article cards by making each column/container
       full-width and block-level. We target several Streamlit-generated
       wrappers to be defensive across Streamlit versions. */
    div[data-testid="column"],
    div[data-testid="stColumns"],
    div[data-testid="stColumns"] > div,
    div[data-testid="column"] > div,
    div[data-testid="stVerticalBlock"] > div,
    .css-1l02zno > div,
    .css-1v3fvcr > div {
        display: block !important;
        flex-direction: column !important;
        width: 100% !important;
        max-width: 100% !important;
        min-width: 0 !important;
        box-sizing: border-box !important;
        margin-left: 0 !important;
        margin-right: 0 !important;
        margin-bottom: 1rem !important;
    }

    /* Score/metric value: larger and centered */
    div[data-testid="stMetricValue"], .stMetricValue {
        font-size: 1.5rem !important;
        text-align: center !important;
    }

    /* Make controls full-width for easier tapping */
    button, select, input, .stButton button, .stSelectbox select, .stTextInput input {
        width: 100% !important;
        font-size: 1rem !important;
        min-height: 44px !important; /* iOS recommended tap target */
        padding: 10px !important;
    }

    /* Pagination and horizontal groups should wrap */
    div[data-testid="stHorizontalBlock"], div[data-testid="stColumns"] {
        flex-wrap: wrap !important;
        justify-content: center !important;
        gap: 0.5rem !important;
    }

    /* Hide streamlit sidebar on mobile to maximize content area */
    [data-testid="stSidebar"], div[data-testid="stSidebarNav"] {
        display: none !important;
    }

    /* Ensure images scale down inside cards */
    img, figure img {
        max-width: 100% !important;
        height: auto !important;
        object-fit: cover !important;
    }

    /* Slightly reduce margins on lists/rationale to fit mobile */
    .rationale-item {
        font-size: 0.95rem !important;
        margin-bottom: 0.6rem !important;
    }
    
    /* Article title in cards - smaller on mobile */
    .article-title {
        font-size: 1.1rem !important;
        line-height: 1.4 !important;
    }
    
    /* Suggested title - smaller on mobile */
    .suggested-title {
        font-size: 0.95rem !important;
        line-height: 1.5 !important;
    }
    
    /* Score display - adjust for mobile */
    .score-value {
        font-size: 2.5rem !important;
    }
    
    .score-label {
        font-size: 1rem !important;
    }
    
    .score-label-text {
        font-size: 0.9rem !important;
    }

    /* Fallback safe adjustments for Streamlit's generated wrappers */
    main, .main, .block-container, .css-1d391kg, .css-18e3th9 {
        max-width: 100% !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    
    /* Statistics cards - stack vertically on mobile */
    [data-testid="stHorizontalBlock"] > div {
        margin-bottom: 0.5rem !important;
    }
}

/* Extra small devices (phones in portrait, less than 600px) */
@media (max-width: 600px) {
    /* Even tighter spacing */
    .block-container {
        padding: 0.25rem !important;
    }
    
    h1 {
        font-size: 1.25rem !important;
    }
    
    h2, h3 {
        font-size: 1rem !important;
    }
    
    /* Score display - smaller for very small screens */
    .score-value {
        font-size: 2rem !important;
    }
    
    /* Hide date separators decorative elements on very small screens */
    .article-title {
        font-size: 1rem !important;
    }
    
    /* Images - reduce height on very small screens */
    img {
        max-height: 200px !important;
    }
    
    /* Compact layout for filter controls */
    .stSelectbox, .stMultiSelect, .stNumberInput {
        margin-bottom: 0.5rem !important;
    }
}

</style>
"""
