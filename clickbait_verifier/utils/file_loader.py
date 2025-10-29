"""File loading and management utilities."""

import os
import json
import glob
from typing import Dict, List, Tuple, Optional


class FileConfig:
    """Configuration for file paths."""
    
    def __init__(self, reports_dir: str):
        self.reports_dir = os.path.normpath(reports_dir)
        self.analysis_dir = os.path.join(self.reports_dir, 'analysis')
        self.scraped_dir = os.path.join(self.reports_dir, 'scraped')


def load_json_if_exists(path: str) -> Optional[dict]:
    """Load JSON file if it exists.
    
    Args:
        path: Path to the JSON file.
        
    Returns:
        Dictionary with JSON content or None if file doesn't exist or is invalid.
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def get_analysis_files(analysis_dir: str) -> List[str]:
    """Get sorted list of analysis JSON files.
    
    Args:
        analysis_dir: Directory containing analysis files.
        
    Returns:
        Sorted list of file paths.
    """
    return sorted(glob.glob(os.path.join(analysis_dir, 'analysis_*.json')))


def get_scraped_files(scraped_dir: str) -> List[str]:
    """Get sorted list of scraped JSON files.
    
    Args:
        scraped_dir: Directory containing scraped files.
        
    Returns:
        Sorted list of file paths.
    """
    return sorted(glob.glob(os.path.join(scraped_dir, 'scraped_*.json')))


def build_display_map(analysis_files: List[str], scraped_files: List[str]) -> Dict[str, dict]:
    """Build a map of display names to file information.
    
    Args:
        analysis_files: List of analysis file paths.
        scraped_files: List of scraped file paths.
        
    Returns:
        Dictionary mapping display names to file info (type and path).
    """
    display_map = {}
    analysis_ids = set()

    # Process analysis files
    for p in analysis_files:
        try:
            with open(p, 'r', encoding='utf-8') as f:
                a = json.load(f)
            src = a.get('source', 'unknown')
            title = a.get('title', '')
            display = f"{src} — {title if len(title) <= 120 else title[:117] + '...'}"
            if a.get('id') is not None:
                analysis_ids.add(a.get('id'))
        except Exception:
            display = os.path.basename(p)
        
        key = display
        i = 1
        while key in display_map:
            key = f"{display} ({i})"
            i += 1
        display_map[key] = {'type': 'analysis', 'path': p}

    # Process scraped files (skip if analysis exists for same id)
    for p in scraped_files:
        try:
            with open(p, 'r', encoding='utf-8') as f:
                s = json.load(f)
            if s.get('id') in analysis_ids:
                continue
            src = s.get('source', 'unknown')
            title = s.get('title', os.path.basename(p))
            display = f"SCRAPED — {src} — {title if len(title) <= 120 else title[:117] + '...'}"
        except Exception:
            display = os.path.basename(p)
        
        key = display
        i = 1
        while key in display_map:
            key = f"{display} ({i})"
            i += 1
        display_map[key] = {'type': 'scraped', 'path': p}

    return display_map


def load_analysis_data(sel_info: dict, scraped_dir: str) -> Tuple[Optional[dict], Optional[str], Optional[str]]:
    """Load analysis data based on selection info.
    
    Args:
        sel_info: Selection info dictionary with 'type' and 'path' keys.
        scraped_dir: Directory containing scraped files.
        
    Returns:
        Tuple of (analysis dict, scraped_path, analysis_name).
    """
    analysis = None
    scraped_path = None
    analysis_name = None

    if sel_info['type'] == 'analysis':
        sel_path = sel_info['path']
        analysis_name = os.path.basename(sel_path)
        with open(sel_path, 'r', encoding='utf-8') as f:
            analysis = json.load(f)
        
        # Try to locate scraped file for this analysis id
        try:
            scraped_pattern = os.path.join(scraped_dir, f"scraped_{analysis.get('id')}*.json")
            s_matches = sorted(glob.glob(scraped_pattern))
            if s_matches:
                scraped_path = s_matches[-1]
        except Exception:
            scraped_path = None
            
    elif sel_info['type'] == 'scraped':
        scraped_path = sel_info['path']
        with open(scraped_path, 'r', encoding='utf-8') as f:
            scraped = json.load(f)
        analysis = {
            'id': scraped.get('id'),
            'source': scraped.get('source'),
            'title': scraped.get('title'),
            'url': scraped.get('url'),
            'score': None,
            'label': None,
            'suggestions': {},
            'rationale': [],
            'signals': {}
        }
    else:
        # Placeholder when no files exist
        analysis = {
            'id': None,
            'source': None,
            'title': 'Brak plików - użyj panelu scrapowania po prawej',
            'url': None,
            'score': None,
            'label': None,
            'suggestions': {},
            'rationale': [],
            'signals': {}
        }

    return analysis, scraped_path, analysis_name


def get_candidates_for_feed(analysis_files: List[str], scraped_files: List[str]) -> List[Tuple[float, str]]:
    """Get list of candidates for feed view sorted by modification time.
    
    Shows ONLY analyzed articles (analysis files).
    
    Args:
        analysis_files: List of analysis file paths.
        scraped_files: List of scraped file paths (ignored - kept for compatibility).
        
    Returns:
        List of (mtime, path) tuples sorted by mtime descending.
    """
    candidates: List[Tuple[float, str]] = []

    # Collect only analysis files (skip scraped-only items)
    for p in analysis_files:
        try:
            m = os.path.getmtime(p)
        except Exception:
            m = 0
        candidates.append((m, p))

    candidates.sort(reverse=True)
    return candidates
