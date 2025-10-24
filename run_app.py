"""Entrypoint wrapper for Streamlit that sets page config early.

This wrapper ensures st.set_page_config is executed before the main app imports,
preventing Streamlit from generating a default top-level label like "streamlit app".
"""

import streamlit as st

# Set a consistent page title early
try:
    st.set_page_config(page_title='Clickbait Verifier')
except Exception:
    # If Streamlit has already been configured elsewhere, ignore
    pass
# Inject minimal CSS/JS early to attempt to hide default root nav entry quickly
try:
    from clickbait_verifier.ui.styling import get_custom_css
    st.markdown(get_custom_css(), unsafe_allow_html=True)
except Exception:
    pass

try:
    import streamlit.components.v1 as components
    js = """
<style>
  /* hide any streamlit app label if present */
  ul[data-testid="stSidebarNavItems"] li a span[label="streamlit app"],
  ul[data-testid="stSidebarNav"] li a span[label="streamlit app"],
  ul[data-testid="stSidebarNavItems"] li a[href$="/"],
  ul[data-testid="stSidebarNav"] li a[href$="/"] { display:none !important; }
</style>
<script>
(function(){
  try{
    // remove root nav item if it appears
    const nav = document.querySelector('div[data-testid="stSidebarNav"]') || document.querySelector('ul[data-testid="stSidebarNavItems"]');
    if(nav){
      const li = nav.querySelector('li');
      if(li){ try{ li.remove(); }catch(e){} }
    }
  }catch(e){}
})();
</script>
"""
    components.html(js, height=1)
except Exception:
    pass

# Import and run the main app
from clickbait_verifier.streamlit_app import main

if __name__ == '__main__':
    main()
