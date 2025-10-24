import sys
from .scraper import run_scraper, fetch_and_save_url

if __name__ == "__main__":
    # Usage: python -m clickbait_verifier.main [url] [source_name] [fetch_method]
    if len(sys.argv) > 1:
        url = sys.argv[1]
        source = sys.argv[2] if len(sys.argv) > 2 else 'CLI'
        method = sys.argv[3] if len(sys.argv) > 3 else 'auto'
        fetch_and_save_url(url, source_name=source, fetch_method=method)
    else:
        run_scraper()
