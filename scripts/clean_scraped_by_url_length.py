#!/usr/bin/env python3
"""Remove (or move) scraped JSON files that look like non-article / 'garbage' entries.

Heuristics used (configurable via CLI):
- min_url_length: remove if full URL length is shorter than this
- min_path_segments: require at least this many non-empty path segments (e.g. /kraj/slug/id => 3 segments)
- blacklist: list of regexes; if path matches any => candidate for removal (e.g. ^/autorzy)
- min_content_chars: remove if 'content' field shorter than this

Defaults are conservative and the script runs in dry-run mode by default.

Examples:
  # Dry run with defaults
  python scripts/clean_scraped_by_url_length.py

  # Remove files with URL length < 40 (ask for confirmation)
  python scripts/clean_scraped_by_url_length.py --min-url-length 40

  # Perform destructive removal (no prompt) and back up removed files
  python scripts/clean_scraped_by_url_length.py --min-url-length 40 --yes --backup

"""
from pathlib import Path
import argparse
import json
import re
import shutil
from urllib.parse import urlparse


def parse_args():
    p = argparse.ArgumentParser(description='Clean scraped JSON files by URL length/path/blacklist')
    p.add_argument('--reports-dir', default='reports/scraped', help='Directory with scraped JSON files')
    p.add_argument('--min-url-length', type=int, default=40, help='Minimum full URL length to keep (default: 40)')
    p.add_argument('--min-path-segments', type=int, default=3, help='Minimum number of non-empty path segments to keep (default: 3)')
    p.add_argument('--min-content-chars', type=int, default=100, help='Minimum content characters to keep (default: 100)')
    p.add_argument('--blacklist', nargs='*', default=['^/autorzy', '^/autorzy/'], help='Path regexes to always consider garbage')
    p.add_argument('--dry-run', action='store_true', default=True, help='Only show files that would be removed (default)')
    p.add_argument('--yes', action='store_true', help='Actually delete/move files without prompt')
    p.add_argument('--backup', action='store_true', help='Move removed files to reports/scraped/removed instead of deleting')
    return p.parse_args()


def load_json(path: Path):
    try:
        with path.open('r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def is_candidate(data, min_url_length, min_segments, min_content_chars, blacklist_re):
    if not data or not isinstance(data, dict):
        return True, 'invalid-json'
    url = data.get('url') or ''
    if not url:
        return True, 'no-url'
    parsed = urlparse(url)
    path = parsed.path or '/'
    # blacklist
    for rx in blacklist_re:
        if rx.search(path):
            return True, f'blacklist:{rx.pattern}'
    # url length
    if min_url_length and len(url) < min_url_length:
        return True, f'short-url:{len(url)}'
    # path segments
    segments = [s for s in path.split('/') if s]
    if min_segments and len(segments) < min_segments:
        return True, f'few-segments:{len(segments)}'
    # content length
    content = data.get('content') or ''
    if min_content_chars and len(content) < min_content_chars:
        return True, f'short-content:{len(content)}'
    return False, None


def main():
    args = parse_args()
    reports = Path(args.reports_dir)
    if not reports.exists() or not reports.is_dir():
        print(f'Reports directory not found: {reports}')
        return 2

    files = sorted(reports.glob('scraped_*.json'))
    if not files:
        print('No scraped_*.json files found in', reports)
        return 0

    blacklist_re = [re.compile(x) for x in (args.blacklist or [])]

    candidates = []
    for f in files:
        data = load_json(f)
        cand, reason = is_candidate(data, args.min_url_length, args.min_path_segments, args.min_content_chars, blacklist_re)
        if cand:
            candidates.append((f, reason, data.get('url') if isinstance(data, dict) else None))

    if not candidates:
        print('No candidate files to remove based on current filters.')
        return 0

    print(f'Found {len(candidates)} candidate files to remove:')
    for p, reason, url in candidates:
        print(f'- {p}  reason={reason} url={url}')

    if args.dry_run and not args.yes:
        print('\nDry-run mode (no files changed). Use --yes to remove and --backup to move files to removed/ directory.')
        return 0

    # proceed with removal
    removed_dir = reports / 'removed'
    if args.backup:
        removed_dir.mkdir(parents=True, exist_ok=True)

    removed_count = 0
    for p, reason, url in candidates:
        try:
            if args.backup:
                dest = removed_dir / p.name
                shutil.move(str(p), str(dest))
            else:
                p.unlink()
            removed_count += 1
        except Exception as e:
            print(f'Failed to remove {p}: {e}')

    print(f'Removed {removed_count} files.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
