"""Dashboard view: ranking of most clickbait-y articles and simple portal counts.

This view provides three sections:
- Ranking: top-N articles sorted by score (descending) showing title, source, score and label.
- Portal counts: simple bar chart of number of 'strong' clickbait articles per source/portal.
- Review list: plain one-line-per-article list of candidates "warto się przyjrzeć" obok wykresu.
"""

from typing import List, Dict, Any

import streamlit as st

from utils.file_loader import load_json_if_exists


def _load_all_analyses(analysis_files: List[str]) -> List[Dict[str, Any]]:
    results = []
    for p in analysis_files:
        a = load_json_if_exists(p)
        if not a:
            continue
        # ensure stable fields
        results.append(a)
    return results


def _top_ranking(analyses: List[Dict[str, Any]], top_n: int = 15) -> List[Dict[str, Any]]:
    # Sort by score (None treated as -inf)
    def key_fn(a):
        s = a.get('score')
        return s if isinstance(s, (int, float)) else -999999

    sorted_list = sorted(analyses, key=key_fn, reverse=True)
    return sorted_list[:top_n]


def _portal_counts_strong(analyses: List[Dict[str, Any]]) -> Dict[str, int]:
    counts = {}
    for a in analyses:
        label = a.get('label')
        if label == 'strong':
            src = a.get('source') or 'unknown'
            counts[src] = counts.get(src, 0) + 1
    return counts


def _review_candidates(analyses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    candidates = []
    for a in analyses:
        label = a.get('label')
        score = a.get('score')
        # Heuristic: include mild-labelled OR borderline scores (30-49)
        if label == 'mild' or (isinstance(score, (int, float)) and 30 <= score <= 49):
            candidates.append(a)
    # keep stable order (by score desc)
    candidates.sort(key=lambda x: x.get('score') or 0, reverse=True)
    return candidates


def render_dashboard(analysis_files: List[str]):
    """Render the Dashboard view.

    Args:
        analysis_files: list of analysis file paths (from FileConfig)
    """
    st.header('Dashboard — ranking clickbait')

    analyses = _load_all_analyses(analysis_files)

    if not analyses:
        st.info('Brak analiz w katalogu reports/analysis — najpierw zescrapuj i przeanalizuj artykuły.')
        return

    # Controls
    col1, col2 = st.columns([2, 1])
    with col1:
        top_n = st.number_input('Pokaż top N artykułów', min_value=5, max_value=100, value=15, step=5)
    with col2:
        show_portal_chart = st.checkbox('Pokaż wykres portali (strong)', value=True)

    # Ranking
    st.subheader(f'Top {top_n} najbardziej clickbaitowych artykułów (wg score)')
    top = _top_ranking(analyses, top_n)

    for idx, a in enumerate(top, start=1):
        score = a.get('score')
        label = a.get('label') or '-'
        src = a.get('source') or 'unknown'
        title = a.get('title') or a.get('url') or f"(id {a.get('id')})"
        # one-line presentation with basic meta and link if available
        url = a.get('url')
        if url:
            st.markdown(f"{idx}. **{title}** — {src} — score: **{score}** — label: *{label}*  \n{url}")
        else:
            st.markdown(f"{idx}. **{title}** — {src} — score: **{score}** — label: *{label}*")

    st.markdown('---')

    # Portal counts
    counts = _portal_counts_strong(analyses)
    candidates = _review_candidates(analyses)

    st.markdown('---')
    st.subheader('Portale vs lista artykułów do weryfikacji (obok wykresu)')
    chart_col, list_col = st.columns([3, 2])

    with chart_col:
        st.caption('Mocno clickbaitowe artykuły (label == strong) per portal')
        if show_portal_chart:
            try:
                import pandas as pd
                if counts:
                    df = (
                        pd.DataFrame(list(counts.items()), columns=['portal', 'strong_count'])
                        .sort_values('strong_count', ascending=False)
                    )
                    st.bar_chart(df.set_index('portal'))
                else:
                    st.info('Brak artykułów z etykietą "strong" w analizach.')
            except Exception:
                for portal, cnt in sorted(counts.items(), key=lambda x: x[1], reverse=True):
                    st.write(f"{portal}: {cnt}")
        else:
            for portal, cnt in sorted(counts.items(), key=lambda x: x[1], reverse=True):
                st.write(f"{portal}: {cnt}")

    with list_col:
        st.caption('Lista artykułów, którym warto się przyjrzeć (linijka po linijce)')
        st.markdown(
            """
            <style>
            .review-card {border:1px solid #e5e7eb;border-radius:8px;padding:10px 12px;margin-bottom:10px;background:#f9fafb;}
            .review-card .review-title {font-weight:600;color:#111827;margin-bottom:4px;}
            .review-card .review-meta {color:#6b7280;font-size:0.9rem;}
            </style>
            """,
            unsafe_allow_html=True,
        )
        if not candidates:
            st.write('Brak kandydatów do ręcznej weryfikacji.')
        else:
            for a in candidates:
                src = a.get('source') or 'unknown'
                title = a.get('title') or a.get('url') or f"(id {a.get('id')})"
                label = a.get('label') or '-'
                url = a.get('url')
                if url:
                    st.markdown(
                        f"<div class='review-card'><div class='review-title'><a href='{url}' target='_blank'>{title}</a></div>"
                        f"<div class='review-meta'>{src} — {label}</div></div>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f"<div class='review-card'><div class='review-title'>{title}</div>"
                        f"<div class='review-meta'>{src} — {label}</div></div>",
                        unsafe_allow_html=True,
                    )
