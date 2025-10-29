"""
Simple CLI wrapper for running the scraper from scripts directory.
This makes it easier to call from GitHub Actions.
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import clickbait_verifier
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from clickbait_verifier.scraper import run_scraper

if __name__ == '__main__':
    print("Starting scraper...")
    run_scraper()
    print("Scraping complete!")
