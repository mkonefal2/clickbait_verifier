"""Batch analysis job intended to be run by GitHub Copilot as a job runner.
This script reads up to N unanalyzed articles from DB and runs analyzer.analyze_batch on them.
It prints IDs processed to stdout for the job system to collect results.
"""
from clickbait_verifier.core.storage import fetch_unanalyzed_articles
import os
import glob
import subprocess

LIMIT = 50

rows = fetch_unanalyzed_articles(LIMIT)
if not rows:
    print('NO_WORK')
else:
    ids = [r[0] for r in rows]
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    python = os.path.join(repo_root, '.venv', 'Scripts', 'python.exe')
    ret = subprocess.run([python, os.path.join(repo_root, 'scripts', 'export_for_agent.py')])
    if ret.returncode != 0:
        print('EXPORT_FAILED')
    else:
        files = glob.glob(os.path.join(repo_root, 'reports', 'for_copilot_*.json'))
        print('EXPORTED_FILES', ','.join(files))
