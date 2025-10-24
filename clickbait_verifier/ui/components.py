"""UI components for rendering cards and elements."""

import base64
import streamlit as st
import textwrap
import html
from pathlib import Path
from typing import Optional, Sequence


# Color mappings for different label types
LABEL_COLORS = {
    'not_clickbait': '#1a7f37',
    'mild': '#b2700f',
    'strong': '#c4301f',
    'extreme': '#800000',
    'insufficient_content': '#666'
}


def get_score_color(score_val: Optional[float], label_val: Optional[str]) -> str:
    """Determine color for score display based on value and label.
    
    Args:
        score_val: Score value (0-100).
        label_val: Label string (e.g., 'mild', 'strong').
        
    Returns:
        Hex color code.
    """
    if label_val and label_val.lower() in LABEL_COLORS:
        return LABEL_COLORS[label_val.lower()]
    
    if score_val is not None:
        try:
            s = float(score_val)
            if s >= 75:
                return LABEL_COLORS['extreme']
            elif s >= 50:
                return LABEL_COLORS['strong']
            elif s >= 25:
                return LABEL_COLORS['mild']
            else:
                return LABEL_COLORS['not_clickbait']
        except Exception:
            pass
    
    return '#888'


def format_score_display(score_val: Optional[float]) -> str:
    """Format score value for display.
    
    Args:
        score_val: Score value to format.
        
    Returns:
        Formatted score string.
    """
    if score_val is None:
        return '-'
    
    try:
        s = float(score_val)
        if s == int(s):
            return str(int(s))
        else:
            return str(round(s, 1))
    except Exception:
        return str(score_val)


def render_image_block(image_url: Optional[str], orig_url: Optional[str]) -> str:
    """Generate HTML for image block.
    
    Args:
        image_url: URL of the image to display.
        orig_url: Original article URL (for linking).
        
    Returns:
        HTML string for image block.
    """
    if not image_url:
        return ''
    
    try:
        if orig_url:
            raw = f'''
    <div style="margin-top:12px;margin-bottom:0px">
        <div style="width:100%;border-radius:8px;overflow:hidden;box-shadow:0 6px 18px rgba(0,0,0,0.08);">
            <a href="{orig_url}" target="_blank" rel="noopener noreferrer" style="display:block;text-decoration:none;">
                <img src="{image_url}" alt="miniatura artykułu" style="display:block;width:100%;height:auto;object-fit:cover;" />
            </a>
        </div>
    </div>
'''
        else:
            raw = f'''
    <div style="margin-top:12px;margin-bottom:0px">
        <div style="width:100%;border-radius:8px;overflow:hidden;box-shadow:0 6px 18px rgba(0,0,0,0.08);">
            <img src="{image_url}" alt="miniatura artykułu" style="display:block;width:100%;height:auto;object-fit:cover;" />
        </div>
    </div>
'''
        return textwrap.dedent(raw).strip()
    except Exception:
        return ''


def render_image_block_compact(image_url: Optional[str], orig_url: Optional[str]) -> str:
    """Generate HTML for compact image block (for feed view).
    
    Args:
        image_url: URL of the image to display.
        orig_url: Original article URL (for linking).
        
    Returns:
        HTML string for compact image block.
    """
    if not image_url:
        return ''
    
    try:
        if orig_url:
            raw = f'''
    <div style="margin-top:8px;margin-bottom:0px">
        <div style="width:100%;max-height:350px;border-radius:8px;overflow:hidden;box-shadow:0 4px 12px rgba(0,0,0,0.08);">
            <a href="{orig_url}" target="_blank" rel="noopener noreferrer" style="display:block;text-decoration:none;">
                <img src="{image_url}" alt="miniatura artykułu" style="display:block;width:100%;height:350px;object-fit:cover;transition:transform 0.2s;" onmouseover="this.style.transform='scale(1.02)'" onmouseout="this.style.transform='scale(1)'" />
            </a>
        </div>
    </div>
'''
        else:
            raw = f'''
    <div style="margin-top:8px;margin-bottom:0px">
        <div style="width:100%;max-height:350px;border-radius:8px;overflow:hidden;box-shadow:0 4px 12px rgba(0,0,0,0.08);">
            <img src="{image_url}" alt="miniatura artykułu" style="display:block;width:100%;height:350px;object-fit:cover;" />
        </div>
    </div>
'''
        return textwrap.dedent(raw).strip()
    except Exception:
        return ''


def render_header_card(title: str, suggested_title: Optional[str], image_block_html: str) -> str:
    """Generate HTML for header card.
    
    Args:
        title: Original article title.
        suggested_title: Suggested neutral title.
        image_block_html: HTML for image block.
        
    Returns:
        HTML string for header card.
    """
    suggested_text = suggested_title or "- brak sugestii -"
    
    header_card = f"""
<div style='border:2px solid #ddd;border-radius:8px;padding:16px;background:#fff;margin-bottom:14px;'>
  <div class="article-title">{html.escape(title)}</div>
  <div class="helper-text">Sugerowany tytuł (neutralny)</div>
  <div class="suggested-title">{html.escape(suggested_text)}</div>
{image_block_html}
</div>
"""
    return textwrap.dedent(header_card)


def render_score_card(score_val: Optional[float], label_val: Optional[str]) -> str:
    """Generate HTML for score card.
    
    Args:
        score_val: Score value.
        label_val: Label string.
        
    Returns:
        HTML string for score card.
    """
    score_display = format_score_display(score_val)
    score_color = get_score_color(score_val, label_val)
    label_text = label_val or "-"
    
    score_card = f"""
<div style='border:2px solid #ddd;border-radius:8px;padding:14px;background:#fff;margin-bottom:12px;text-align:center;'>
  <div class="score-label">Wynik (score)</div>
  <div class="score-value" style='color:{score_color};'>{score_display}</div>
  <div class="score-label-text" style='color:{score_color};'>Etykieta: <strong style='color:{score_color}'>{html.escape(label_text)}</strong></div>
</div>
"""
    return textwrap.dedent(score_card)


_BADGE_IMAGE_CACHE: dict[str, Optional[str]] = {}


def _sanitize_badge_text(value: Optional[str]) -> str:
    """Escape badge text while preserving emoji."""
    if value is None:
        return ''
    try:
        # html.escape leaves emoji untouched but escapes HTML-sensitive chars
        return html.escape(str(value))
    except Exception:
        return str(value)


def _get_badge_image_data_uri(image_path: Optional[str]) -> Optional[str]:
    """Return a data URI for the badge image, caching results."""
    if not image_path:
        return None

    if image_path in _BADGE_IMAGE_CACHE:
        return _BADGE_IMAGE_CACHE[image_path]

    try:
        path = Path(image_path)
        if not path.is_absolute():
            repo_root = Path(__file__).resolve().parents[2]
            path = (repo_root / path).resolve()

        if not path.exists():
            _BADGE_IMAGE_CACHE[image_path] = None
            return None

        data = path.read_bytes()
        encoded = base64.b64encode(data).decode('ascii')
        uri = f"data:image/png;base64,{encoded}"
        _BADGE_IMAGE_CACHE[image_path] = uri
        return uri
    except Exception:
        _BADGE_IMAGE_CACHE[image_path] = None
        return None


def render_badges_card(badges: Sequence[dict], max_items: int = 3) -> str:
    """Generate HTML card showcasing up to `max_items` badges.

    Args:
        badges: Iterable of badge dicts containing id, color, icon, name, description.
        max_items: Maximum number of badges to display.

    Returns:
        HTML string for badges card.
    """
    if not badges:
        body_html = "<div class='rationale-item'>- brak odznak -</div>"
    else:
        rendered = []
        for badge in list(badges)[:max_items]:
            image_uri = _get_badge_image_data_uri(badge.get('image'))
            icon = _sanitize_badge_text(badge.get('icon') or '•')
            name = _sanitize_badge_text(badge.get('name') or badge.get('id') or '')
            description = _sanitize_badge_text(badge.get('description') or '')

            tooltip = name
            if description:
                tooltip = f"{tooltip} — {description}"

            if image_uri:
                badge_media = (
                    f"<div style='width:112px;height:112px;border-radius:16px;overflow:hidden;background:#f9fafb;display:flex;"
                    f"align-items:center;justify-content:center;' title='{tooltip}'><img src='{image_uri}' alt='{name}' style='max-width:96px;max-height:96px;object-fit:contain;' /></div>"
                )
            else:
                badge_media = (
                    f"<div style='width:112px;height:112px;border-radius:16px;background:#f3f4f6;display:flex;align-items:center;"
                    f"justify-content:center;font-size:52px;' title='{tooltip}'>{icon}</div>"
                )

            rendered.append(
                f"""
<div style='display:inline-block;margin-right:18px;margin-bottom:18px;'>{badge_media}</div>
""".strip()
            )

        body_html = "\n".join(rendered)

    card_html = f"""
<div style='border:2px solid #ddd;border-radius:8px;padding:14px;background:#fff;margin-bottom:12px;'>
  <div class="score-label">Odznaki</div>
  <div style='margin-top:8px;display:flex;flex-wrap:wrap;'>
    {body_html}
  </div>
</div>
"""
    return textwrap.dedent(card_html)


def render_score_card_with_suggestion(score_val: Optional[float], label_val: Optional[str], 
                                       suggested_title: Optional[str]) -> str:
    """Generate HTML for score card with suggested title (for feed view).
    
    Args:
        score_val: Score value.
        label_val: Label string.
        suggested_title: Suggested neutral title.
        
    Returns:
        HTML string for score card.
    """
    # This function is kept for compatibility but not used
    pass


def render_score_card_with_rationale(score_val: Optional[float], label_val: Optional[str], 
                                      rationale: list) -> str:
    """Generate HTML for score card with rationale (for feed view).
    
    Args:
        score_val: Score value.
        label_val: Label string.
        rationale: List of rationale strings.
        
    Returns:
        HTML string for score card.
    """
    score_display = format_score_display(score_val)
    score_color = get_score_color(score_val, label_val)
    label_text = label_val or "-"
    
    if rationale:
        items_html = "\n".join(
            f"<div style='margin-bottom:10px;font-size:18px;line-height:1.7;border-left:3px solid #e5e7eb;padding-left:14px;padding-top:6px;padding-bottom:6px;font-weight:500;'>{i}. {html.escape(str(r))}</div>" 
            for i, r in enumerate(rationale, 1)
        )
    else:
        items_html = "<div style='font-size:18px;color:#9ca3af;'>- brak uzasadnienia -</div>"
    
    score_card = f"""
<div style='border:1px solid #ddd;border-radius:8px;padding:16px;background:#fff;margin-bottom:12px;height:100%;display:flex;flex-direction:column;'>
  <div style='text-align:center;margin-bottom:24px;'>
    <div class="score-label" style='font-size:24px;font-weight:600;color:#111827;'>Wynik (score)</div>
    <div class="score-value" style='font-size:48px;font-weight:700;color:{score_color};line-height:1;'>{score_display}</div>
    <div class="score-label-text" style='font-size:18px;font-weight:600;color:{score_color};margin-top:8px;'>Etykieta: <strong style='color:{score_color}'>{html.escape(label_text)}</strong></div>
  </div>
  <div style='flex-grow:1;border-top:1px solid #e5e7eb;padding-top:12px;'>
    <div class="helper-text" style='font-size:11px;margin-bottom:8px;color:#9ca3af;'>Uzasadnienie</div>
    {items_html}
  </div>
</div>
"""
    return textwrap.dedent(score_card)


def render_rationale_card(rationale: list) -> str:
    """Generate HTML for rationale card.
    
    Args:
        rationale: List of rationale strings.
        
    Returns:
        HTML string for rationale card.
    """
    if rationale:
        items_html = "\n".join(
            f"<div class='rationale-item'>{i}. {html.escape(str(r))}</div>" 
            for i, r in enumerate(rationale, 1)
        )
    else:
        items_html = "<div class='rationale-item'>- brak uzasadnienia -</div>"

    rationale_card = f"""
<div style='border:2px solid #ddd;border-radius:8px;padding:14px;background:#fff;margin-bottom:12px;'>
  <div class="score-label">Uzasadnienie</div>
  <div style='margin-top:6px'>
    {items_html}
  </div>
</div>
"""
    return textwrap.dedent(rationale_card)


def render_simple_header_card(title: str, source: str, suggested_title: Optional[str], 
                               image_block_html: str) -> str:
    """Generate HTML for simple header card (used in feed view).
    
    Args:
        title: Article title.
        source: Source name.
        suggested_title: Suggested neutral title (not used, kept for compatibility).
        image_block_html: HTML for image block.
        
    Returns:
        HTML string for header card.
    """    
    header_card = f"""
<div style='border:2px solid #ddd;border-radius:8px;padding:12px;background:#fff;margin-bottom:10px;height:100%;'>
  <div class="article-title">{html.escape(str(title))}</div>
  <div class="helper-text">{html.escape(str(source or ''))}</div>
  {image_block_html}
</div>
"""
    return textwrap.dedent(header_card)


def render_simple_header_card_with_rationale(title: str, source: str, rationale: list,
                                              image_block_html: str) -> str:
    """Generate HTML for simple header card with rationale (used in feed view).
    
    Args:
        title: Article title.
        source: Source name.
        rationale: List of rationale strings.
        image_block_html: HTML for image block.
        
    Returns:
        HTML string for header card.
    """
    # This function is kept for compatibility but not used
    pass


def render_simple_header_card_with_suggestion(title: str, source: str, suggested_title: Optional[str],
                                               image_block_html: str, url: Optional[str] = None) -> str:
    """Generate HTML for simple header card with suggested title (used in feed view).
    
    Args:
        title: Article title.
        source: Source name.
        suggested_title: Suggested neutral title.
        image_block_html: HTML for image block.
        url: URL to the original article.
        
    Returns:
        HTML string for header card.
    """
    suggested_text = suggested_title or "- brak sugestii -"
    
    # Create clickable title if URL is provided with hover effect
    if url:
        title_html = f'<a href="{html.escape(url)}" target="_blank" rel="noopener noreferrer" style="text-decoration:none;color:#111827;transition:all 0.2s;" onmouseover="this.style.color=\'#2563eb\';this.style.textDecoration=\'underline\'" onmouseout="this.style.color=\'#111827\';this.style.textDecoration=\'none\'"><div style="cursor:pointer;font-size:18px;line-height:1.4;font-weight:500;">{html.escape(str(title))}</div></a>'
    else:
        title_html = f'<div style="font-size:18px;line-height:1.4;color:#111827;font-weight:500;">{html.escape(str(title))}</div>'
    
    header_card = f"""
<div style='border:1px solid #ddd;border-radius:8px;padding:16px;background:#fff;margin-bottom:10px;display:flex;flex-direction:column;height:100%;'>
  <div style='margin-bottom:24px;'>
    <div class="helper-text" style='font-size:11px;margin-bottom:8px;color:#9ca3af;'>Sugerowany tytuł</div>
    <div style='font-size:36px;line-height:1.4;color:#111827;font-weight:600;'>{html.escape(suggested_text)}</div>
  </div>
  <div class="helper-text" style='font-size:15px;color:#9ca3af;margin-bottom:24px;'>{html.escape(str(source or ''))}</div>
  <div style='margin-bottom:24px;padding-top:16px;padding-bottom:16px;border-top:1px solid #e5e7eb;border-bottom:1px solid #e5e7eb;'>
    <div class="helper-text" style='font-size:11px;margin-bottom:8px;color:#9ca3af;'>Oryginalny tytuł</div>
    {title_html}
  </div>
  <div style='flex-grow:0;'>
    {image_block_html}
  </div>
</div>
"""
    return textwrap.dedent(header_card)
