#!/usr/bin/env python3
"""List scraped articles that don't have a corresponding analysis file.

Compares files in `reports/scraped/scraped_*.json` with `reports/analysis/analysis_*.json`.
By default prints a short summary and a list of scraped files without analysis.

Options:
  --scraped-dir    Path to scraped files (default: reports/scraped)
  --analysis-dir   Path to analysis files (default: reports/analysis)
  --source         Only consider scraped files for this source (case-insensitive)
  --write-json     Write result list to a JSON file path
  --check-contents If set, also flag analysis files that exist but look empty (no 'score' or 'label')

Example:
  python scripts/list_unanalyzed.py --source onet --write-json unanalyzed_onet.json

"""
from pathlib import Path
import json
import argparse
from typing import Dict, List


def parse_args():
    p = argparse.ArgumentParser(description='List scraped articles without analysis')
    p.add_argument('--scraped-dir', default='reports/scraped', help='Directory with scraped JSON files')
    p.add_argument('--analysis-dir', default='reports/analysis', help='Directory with analysis JSON files')
    p.add_argument('--source', default=None, help='Filter scraped files by source (case-insensitive)')
    p.add_argument('--write-json', default=None, help='Write output list to given JSON file')
    p.add_argument('--check-contents', action='store_true', help="Also mark analyses that exist but lack 'score' or 'label'")
    return p.parse_args()


def load_json(path: Path):
    try:
        with path.open('r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def find_analysis_map(analysis_dir: Path) -> Dict[str, Path]:
    """Return map of id (as string) -> analysis path(s).

    If multiple analysis files exist for same id, keep the first.
    """
    m = {}
    if not analysis_dir.exists():
        return m
    for p in analysis_dir.glob('analysis_*.json'):
        name = p.stem  # analysis_<id> or analysis_<id>_n
        # get id part after 'analysis_'
        rest = name[len('analysis_'):]
        # id may be like '1761328130371' or '1761328130371_1'
        idpart = rest.split('_')[0]
        if idpart not in m:
            m[idpart] = p
    return m


def main():
    args = parse_args()
    scraped_dir = Path(args.scraped_dir)
    analysis_dir = Path(args.analysis_dir)

    if not scraped_dir.exists():
        print(f'Scraped directory not found: {scraped_dir}')
        return 2
    if not analysis_dir.exists():
        print(f'Analysis directory not found: {analysis_dir} (will treat as empty)')

    analysis_map = find_analysis_map(analysis_dir)

    scraped_files = sorted(scraped_dir.glob('scraped_*.json'))
    unanalyzed = []
    partially = []

    for p in scraped_files:
        data = load_json(p)
        if not data or not isinstance(data, dict):
            unanalyzed.append({'file': str(p), 'reason': 'invalid-json'})
            continue
        src = (data.get('source') or '').lower()
        if args.source and args.source.lower() != src:
            continue
        id_ = str(data.get('id')) if data.get('id') is not None else None
        if not id_:
            unanalyzed.append({'file': str(p), 'url': data.get('url'), 'reason': 'no-id'})
            continue
        if id_ not in analysis_map:
            unanalyzed.append({'file': str(p), 'id': id_, 'url': data.get('url')})
        else:
            if args.check_contents:
                a = load_json(analysis_map[id_])
                if not a or (not a.get('score') and not a.get('label')):
                    partially.append({'file': str(p), 'id': id_, 'analysis': str(analysis_map[id_])})

    total_scraped = len([p for p in scraped_files if (not args.source) or (load_json(p) and ((load_json(p).get('source') or '').lower() == args.source.lower() if args.source else True))])
    print('\nSummary:')
    print(f'  scraped files scanned: {total_scraped}')
    print(f'  unanalyzed (no analysis file): {len(unanalyzed)}')
    if args.check_contents:
        print(f'  analyses present but incomplete: {len(partially)}')

    if unanalyzed:
        print('\nUnanalyzed files:')
        for u in unanalyzed:
            print(f"- {u.get('file')}  id={u.get('id')} url={u.get('url')} reason={u.get('reason')}")

    if args.check_contents and partially:
        print('\nPartial/empty analyses:')
        for u in partially:
            print(f"- {u.get('file')}  id={u.get('id')} analysis_file={u.get('analysis')}")

    if args.write_json:
        out = {'unanalyzed': unanalyzed, 'partial': partially}
        try:
            with open(args.write_json, 'w', encoding='utf-8') as f:
                json.dump(out, f, ensure_ascii=False, indent=2)
            print(f'Wrote output to {args.write_json}')
        except Exception as e:
            print('Failed to write JSON:', e)

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
