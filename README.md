# Clickbait Verifier

A clickable project for assessing the clickbaitiness of articles.

Quick start (Windows PowerShell)

1) Create and activate a virtualenv:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Install dependencies:

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

3) (Optional) Playwright — if you want to render JS pages:

```powershell
pip install playwright
python -m playwright install chromium
```

4) Configure sources: edit `config.yaml` (located in the project directory). Example entry:

# Clickbait Verifier

A clickable project for assessing the clickbaitiness of articles. This README contains two separate usage paths:

- Developer version — full installation, run and debugging instructions (for project developers).
- Demo version (Demo feed) — simplified steps to quickly run a demo using prepared data and UI.

---

## Developer version

Intended for people who will develop, test and debug the project.

Requirements:
- Python 3.10+ (recommended)
- `pip` and (optionally) `playwright` if you want to render JS pages

1) Create and activate a virtualenv (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Install dependencies:

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

3) (Optional) Playwright — if you want to render JS pages (useful for dynamic sites):

```powershell
pip install playwright
python -m playwright install chromium
```

4) Configure sources:
- Edit `config.yaml` in the project directory. Example entry:

```yaml
- name: rmf24
  url: https://www.rmf24.pl/...
  enabled: true
  fetch_method: auto   # 'auto' | 'requests' | 'playwright'
  ask_for_url: false
```

5) Running and testing:

- Run the scraper for all sources from `config.yaml`:

```powershell
python -m clickbait_verifier.main
```

- Run the scraper for a single URL (quick test):

```powershell
python -m clickbait_verifier.main "https://example.com/article" "SourceName" "auto"
```

After running:
- Scraped JSON: `reports/scraped/scraped_<id>_<timestamp>.json`
- Analysis: `reports/analysis/analysis_<id>_<timestamp>.json`

6) Interface (Streamlit) — local GUI for browsing analyses:

```powershell
pip install streamlit
streamlit run clickbait_verifier/streamlit_app.py
```

7) Project structure — brief overview of important directories:
- `clickbait_verifier/` — main package: scraper, analyzer, reporter, UI
- `clickbait_verifier/core/` — abstractions for fetcher, parser, storage
- `clickbait_verifier/extractors/` — source configurations (yaml)
- `reports/` — output: `scraped/` and `analysis/`
- `scripts/` — helper scripts (exports, migrations, debug)

8) Developer tools and tests (optional):
- Add unit tests following the project convention (pytest).
- We can add CI to run linter/pytest on each PR.

---

## Demo version (Demo feed)

A quick path for presentation or demo, without running the full scraping process.

Assumptions:
- We want to show the UI and example analyses using existing prepared JSON files from `reports/`.

Steps:

1) Prepare (or choose) a sample scraped/analysis file
- The repository contains example files in `reports/scraped/` and `reports/analysis/`.
- If you want a separate demo, copy one of the sample files to `reports/analysis/` (Streamlit reads that directory):

```powershell
# example: copy an existing scraped/ or analysis file to the directory used by the GUI
Copy-Item .\reports\scraped\scraped_1761128130371.json .\reports\analysis\ -Force
```

2) Run the simple demo feed (ready-made Streamlit feed):

```powershell
pip install streamlit
streamlit run clickbait_verifier/streamlit_feed_app.py
```

3) What you'll see in the demo:
- A list of sample articles (from files in `reports/analysis/`)
- Content preview and clickbait analysis results

Demo limitations:
- The demo does not perform real fetching or live analysis — it uses prepared files.
- For full, up-to-date analysis (live pages) run the developer version with the appropriate fetch_method.
