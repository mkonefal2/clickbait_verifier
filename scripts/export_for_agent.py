"""Export scraped articles to JSON (scraping-only simplified exporter).
Exports fields: id, source, title, content, url, published, fetched_at
"""

import sys
import os
# ensure repository root is on sys.path when running this script directly
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from clickbait_verifier.core.storage import fetch_all_articles
import json
from datetime import datetime

rows = fetch_all_articles()
entries = []
for r in rows:
    # tuple order: id, source, title, url, published, fetched_at, content, score, label, reasons, similarity, analyzed_at
    id_, source, title, url, published, fetched_at, content, *_ = r
    entries.append({
        'id': id_,
        'source': source,
        'title': title,
        'content': content,
        'url': url,
        'published': str(published) if published is not None else None,
        'fetched_at': str(fetched_at) if fetched_at is not None else None
    })

os.makedirs('reports', exist_ok=True)
now = datetime.utcnow().strftime('%Y-%m-%dT%H%M%SZ')
out_path = f'reports/scraped_for_copilot_{now}.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(entries, f, ensure_ascii=False, indent=2)

print('Exported', len(entries), 'articles to', out_path)
