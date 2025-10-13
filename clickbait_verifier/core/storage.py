import duckdb
from datetime import datetime

DB_PATH = "data/db.duckdb"


def init_db():
    con = duckdb.connect(DB_PATH)
    con.execute('''
    CREATE TABLE IF NOT EXISTS articles (
      id BIGINT,
      source TEXT,
      title TEXT,
      url TEXT,
      published TIMESTAMP,
      fetched_at TIMESTAMP,
      content TEXT,
      score DOUBLE,
      label TEXT,
      reasons TEXT,
      similarity DOUBLE,
      analyzed_at TIMESTAMP
    )
    ''')
    con.close()


def save_article(rec):
    """Insert article unless URL already exists. If exists, update title/content when missing."""
    con = duckdb.connect(DB_PATH)
    url = rec.get("url")
    now = datetime.now()
    if url:
        existing = con.execute('SELECT id, title, content FROM articles WHERE url = ? LIMIT 1', [url]).fetchone()
        if existing:
            eid, etitle, econtent = existing
            needs_update = False
            params = []
            set_parts = []
            if (not etitle or str(etitle).strip() == '') and rec.get("title"):
                set_parts.append('title = ?')
                params.append(rec.get("title"))
                needs_update = True
            if (not econtent or str(econtent).strip() == '') and rec.get("content"):
                set_parts.append('content = ?')
                params.append(rec.get("content"))
                set_parts.append('fetched_at = ?')
                params.append(now)
                set_parts.append('published = ?')
                params.append(rec.get("published"))
                needs_update = True
            if needs_update:
                params.append(eid)
                sql = 'UPDATE articles SET ' + ', '.join(set_parts) + ' WHERE id = ?'
                con.execute(sql, params)
                con.close()
                return True
            con.close()
            return False
    # insert new
    con.execute("INSERT INTO articles (id, source, title, url, published, fetched_at, content) VALUES (?,?,?,?,?,?,?)",
                [int(now.timestamp()*1000), rec.get("source"), rec.get("title"), rec.get("url"), rec.get("published"), now, rec.get("content")])
    con.close()
    return True


def fetch_all_articles():
    con = duckdb.connect(DB_PATH)
    df = con.execute('SELECT * FROM articles').fetchall()
    con.close()
    return df


def update_article_analysis(id_, score, label, reasons, similarity):
    con = duckdb.connect(DB_PATH)
    con.execute('UPDATE articles SET score = ?, label = ?, reasons = ?, similarity = ?, analyzed_at = ? WHERE id = ?',
                [score, label, reasons, similarity, datetime.now(), id_])
    con.close()


def remove_duplicates():
    """Remove duplicate articles keeping the one with the smallest id for each URL."""
    con = duckdb.connect(DB_PATH)
    con.execute("DELETE FROM articles WHERE id NOT IN (SELECT MIN(id) FROM articles GROUP BY url)")
    con.close()


def fetch_unanalyzed_articles(limit=50):
    con = duckdb.connect(DB_PATH)
    df = con.execute('SELECT * FROM articles WHERE analyzed_at IS NULL ORDER BY fetched_at LIMIT ?', [limit]).fetchall()
    con.close()
    return df


def fetch_article_by_id(id_):
    con = duckdb.connect(DB_PATH)
    row = con.execute('SELECT id, source, title, url, published, fetched_at, content, score, label, reasons, similarity, analyzed_at FROM articles WHERE id = ?', [id_]).fetchone()
    con.close()
    return row
