from .scraper import run_scraper
from .reporter import generate_daily_report

if __name__ == "__main__":
    run_scraper()
    generate_daily_report()
