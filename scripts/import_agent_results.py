"""Import analyzed JSONs produced by external LLM agent.
The agent should produce a file with same ids and added fields: score, label, reasons, similarity, analyzed_at.
This script will update DB and produce a markdown report `reports/report_<date>_agent.md`.
"""
import sys
import os
import json
from datetime import datetime

repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from clickbait_verifier.core.storage import init_db, update_article_analysis, fetch_article_by_id


def import_results(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    init_db()
    for item in data:
        id_ = item.get('id')
        score = item.get('score')
        label = item.get('label')
        reasons = item.get('reasons')
        similarity = item.get('similarity')
        analyzed_at = item.get('analyzed_at') or datetime.utcnow().isoformat()
        update_article_analysis(id_, score, label, reasons, similarity)
    # generate markdown report
    date = datetime.utcnow().strftime('%Y-%m-%d')
    md_path = f'reports/report_{date}_agent.md'
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write('# Agent Analysis Report\n\n')
        for item in data:
            row = fetch_article_by_id(item.get('id'))
            if row:
                _, source, title, url, *_ = row
            else:
                source = item.get('source')
                title = item.get('title')
                url = item.get('url')
            f.write(f"- [{source}] {title} ({item.get('score')}) - {url}\n")
            if item.get('reasons'):
                f.write(f"  - reasons: {item.get('reasons')}\n")
            if item.get('excerpt'):
                f.write(f"  - excerpt: {item.get('excerpt')}\n")
    print('Imported', len(data), 'results and wrote', md_path)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: import_agent_results.py <path-to-agent-json>')
        sys.exit(1)
    import_results(sys.argv[1])
