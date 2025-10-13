import duckdb
import pandas as pd
from datetime import datetime


def generate_daily_report():
    con = duckdb.connect('data/db.duckdb')
    df = con.execute('SELECT source, title, url, score, label, reasons FROM articles').fetchdf()
    if df.empty:
        print('No articles to report')
        return
    today = datetime.now().strftime('%Y-%m-%d')
    md_path = f'reports/report_{today}.md'
    csv_path = f'reports/report_{today}.csv'
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write('# Daily Clickbait Report\n\n')
        for _, r in df.iterrows():
            f.write(f"- [{r['source']}] {r['title']} ({r['score']}) - {r['url']}\n")
    df.to_csv(csv_path, index=False)
    print('Report generated:', md_path, csv_path)
    con.close()
