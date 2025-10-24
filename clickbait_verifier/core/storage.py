import json
import os
from datetime import datetime
import time
from dateutil import parser as dateparser

# When True, do not persist changes to disk storage; keep new records only in-memory.
NO_PERSISTENCE = True

JSON_PATH = os.path.join('data', 'articles.json')

# Column order expected by callers
_COLUMNS = ['id','source','title','url','published','fetched_at','content','score','label','reasons','similarity','analyzed_at']

# In-memory store used when NO_PERSISTENCE is True
_in_memory_records = []


def _ensure_data_dir():
    d = os.path.dirname(JSON_PATH)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)


def init_db():
    """Ensure the JSON storage file exists. Still creates file even when NO_PERSISTENCE is True so legacy persisted records remain available."""
    _ensure_data_dir()
    if not os.path.exists(JSON_PATH):
        with open(JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False)


def _load_all():
    _ensure_data_dir()
    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            records = json.load(f)
    except Exception:
        records = []
    # when running in NO_PERSISTENCE mode, include in-memory records on top
    if NO_PERSISTENCE and _in_memory_records:
        # return persisted records first, then in-memory
        return records + list(_in_memory_records)
    return records


def _save_all(records):
    _ensure_data_dir()
    # If persistence is disabled, do not write to disk
    if NO_PERSISTENCE:
        return
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2, default=str)


def _now_iso():
    return datetime.now().isoformat()


def _normalize_published(published_raw):
    if published_raw is None:
        return None
    if isinstance(published_raw, datetime):
        return published_raw.isoformat()
    try:
        # time.struct_time
        if hasattr(published_raw, 'tm_year'):
            return datetime.fromtimestamp(time.mktime(published_raw)).isoformat()
    except Exception:
        pass
    try:
        # string parse
        return dateparser.parse(str(published_raw)).isoformat()
    except Exception:
        return None


def _row_from_record(rec):
    # Return a tuple in the expected column order
    return tuple(rec.get(col) for col in _COLUMNS)


def save_article(rec):
    """Insert article unless URL already exists. If exists, update title/content when missing.
    Returns the article id (int) inserted or existing.
    In NO_PERSISTENCE mode new records are kept only in-memory.
    """
    init_db()
    # load persisted records to check duplicates
    persisted = []
    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            persisted = json.load(f)
    except Exception:
        persisted = []

    url = rec.get('url')
    now_iso = _now_iso()
    published = _normalize_published(rec.get('published'))

    # check persisted records first
    if url:
        for r in persisted:
            if r.get('url') == url:
                eid = int(r.get('id'))
                needs_update = False
                if (not r.get('title') or str(r.get('title')).strip() == '') and rec.get('title'):
                    r['title'] = rec.get('title')
                    needs_update = True
                if (not r.get('content') or str(r.get('content')).strip() == '') and rec.get('content'):
                    r['content'] = rec.get('content')
                    r['fetched_at'] = now_iso
                    if published:
                        r['published'] = published
                    needs_update = True
                if needs_update and not NO_PERSISTENCE:
                    _save_all(persisted)
                return int(eid)
    # check in-memory records
    for r in _in_memory_records:
        if r.get('url') == url:
            eid = int(r.get('id'))
            needs_update = False
            if (not r.get('title') or str(r.get('title')).strip() == '') and rec.get('title'):
                r['title'] = rec.get('title')
                needs_update = True
            if (not r.get('content') or str(r.get('content')).strip() == '') and rec.get('content'):
                r['content'] = rec.get('content')
                r['fetched_at'] = now_iso
                if published:
                    r['published'] = published
                needs_update = True
            # in-memory update already effective
            return int(eid)

    # insert new
    new_id = int(time.time() * 1000)
    new_rec = {
        'id': new_id,
        'source': rec.get('source'),
        'title': rec.get('title'),
        'url': rec.get('url'),
        'published': published,
        'fetched_at': now_iso,
        'content': rec.get('content'),
        'score': rec.get('score'),
        'label': rec.get('label'),
        'reasons': rec.get('reasons'),
        'similarity': rec.get('similarity'),
        'analyzed_at': rec.get('analyzed_at')
    }
    if NO_PERSISTENCE:
        _in_memory_records.append(new_rec)
    else:
        # persist to disk
        records = persisted
        records.append(new_rec)
        _save_all(records)
    return int(new_id)


def fetch_all_articles():
    records = _load_all()
    return [_row_from_record(r) for r in records]


def fetch_article_by_id(id_):
    # check in-memory first
    for r in _in_memory_records:
        if int(r.get('id')) == int(id_):
            return _row_from_record(r)
    # then check persisted
    records = _load_all()
    for r in records:
        if int(r.get('id')) == int(id_):
            return _row_from_record(r)
    return None


def fetch_article_by_url(url):
    if not url:
        return None
    # check in-memory first
    for r in _in_memory_records:
        if r.get('url') == url:
            return _row_from_record(r)
    # then check persisted
    records = _load_all()
    for r in records:
        if r.get('url') == url:
            return _row_from_record(r)
    return None


def update_article_analysis(id_, score, label, reasons, similarity):
    # update in-memory if present
    for r in _in_memory_records:
        if int(r.get('id')) == int(id_):
            r['score'] = score
            r['label'] = label
            r['reasons'] = reasons
            r['similarity'] = similarity
            r['analyzed_at'] = _now_iso()
            return
    # otherwise update persisted (if allowed)
    records = _load_all()
    changed = False
    for r in records:
        if int(r.get('id')) == int(id_):
            r['score'] = score
            r['label'] = label
            r['reasons'] = reasons
            r['similarity'] = similarity
            r['analyzed_at'] = _now_iso()
            changed = True
            break
    if changed and not NO_PERSISTENCE:
        _save_all(records)


def remove_duplicates():
    records = _load_all()
    seen = {}
    keep = []
    for r in records:
        url = r.get('url')
        if url in seen:
            # keep the one with smallest id
            existing = seen[url]
            if int(r.get('id')) < int(existing.get('id')):
                # replace
                seen[url] = r
        else:
            seen[url] = r
    keep = list(seen.values())
    if not NO_PERSISTENCE:
        _save_all(keep)


def fetch_unanalyzed_articles(limit=50):
    records = _load_all()
    unan = [r for r in records if not r.get('analyzed_at')]
    unan = sorted(unan, key=lambda x: x.get('fetched_at') or '')
    return [_row_from_record(r) for r in unan[:limit]]
