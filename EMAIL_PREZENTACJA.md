# Prezentacja projektu: Clickbait Verifier

---

**Temat:** Clickbait Verifier - System automatycznej analizy clickbaitu w mediach internetowych

**Od:** [Twoje imię i nazwisko]  
**Data:** 29 października 2025

---

Dzień dobry,

Chciałbym/Chciałabym zaprezentować projekt **Clickbait Verifier** - system do automatycznej analizy i oceny poziomu clickbaitu w polskich mediach internetowych, rozwijany w publicznym repozytorium GitHub.

## Czym jest Clickbait Verifier?

To narzędzie wykorzystujące AI i analizę semantyczną do obiektywnej oceny, na ile tytuły artykułów prasowych są clickbaitowe (sensacyjne, wprowadzające w błąd). System automatycznie:

- **Monitoruje** artykuły z głównych polskich portali informacyjnych (RMF24, Onet, Focus, Nauka w Polsce)
- **Analizuje** semantyczne różnice między tytułem a rzeczywistą treścią artykułu
- **Ocenia** stopień clickbaitowości w skali 0-100
- **Raportuje** wyniki w przejrzystych raportach dziennych (CSV, Markdown)

## Kluczowe funkcjonalności

### 1. **Backend - Silnik analityczny**
- Automatyczny scraping artykułów z RSS i stron WWW
- Inteligentne ekstrakcje treści (z obsługą dynamicznych stron JS poprzez Playwright)
- Analiza semantyczna (embeddings, cosine similarity)
- Heurystyki clickbaitu (znaki zapytania, wykrzykniki, słowa kluczowe)
- Baza danych DuckDB/PostgreSQL do przechowywania analiz
- REST API do integracji z aplikacjami klienckimi

### 2. **Proof of Concept - Interfejs Streamlit**
- Interaktywny dashboard do przeglądania wyników analiz
- Widok feedu z kolorowym wskaźnikiem poziomu clickbait
- Filtrowanie artykułów po źródłach
- Narzędzia diagnostyczne dla scraperów
- Statystyki i wizualizacje

### 3. **Automatyzacja z GitHub Copilot Agent**
- Automatyczna aktualizacja konfiguracji ekstraktorów HTML
- Analiza logów i błędów scraperów
- Samodoskonalący się system

## Architektura techniczna

**Backend:**
- Python 3.10+ (asyncio)
- DuckDB / PostgreSQL
- Sentence Transformers (AI embeddings)
- Playwright / Requests (scraping)
- FastAPI (REST API)

**Frontend (PoC):**
- Streamlit - szybkie prototypowanie interfejsu
- Interaktywne komponenty i wykresy
- Real-time data refresh

**DevOps:**
- GitHub repository (publiczne)
- GitHub Actions (CI/CD)
- Task Scheduler / Cron (automatyczne harmonogramy)
- Docker-ready

## Przykładowe wyniki

System codziennie analizuje dziesiątki artykułów i generuje raporty pokazujące:
- Ranking najbardziej clickbaitowych tytułów
- Porównanie różnych źródeł informacji
- Trendy w czasie
- Szczegółowe uzasadnienia ocen

## Rozwój w GitHub

Projekt jest aktywnie rozwijany w publicznym repozytorium GitHub:
- **Repository:** mkonefal2/clickbait_verifier
- Pełna historia commitów i dokumentacja zmian
- Issue tracking i planowanie funkcjonalności
- CI/CD pipeline z GitHub Actions
- Otwarta współpraca i code review
- Automatyzacja z GitHub Copilot Agent

Całość kodu źródłowego, dokumentacji i przykładowych danych jest dostępna publicznie, co umożliwia transparentność metodologii oraz potencjalną współpracę.

## Jak uruchomić?

### Quick Start - Demo Feed (3 minuty)

```powershell
# 1. Klonowanie repozytorium
git clone https://github.com/mkonefal2/clickbait_verifier.git
cd clickbait_verifier

# 2. Środowisko Python
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 3. Uruchom interfejs Feed (PoC)
streamlit run clickbait_verifier\streamlit_feed_app.py

# 4. Otwórz przeglądarkę: http://localhost:8501
```

### Backend API (opcjonalnie)
```powershell
python api_server.py
# API dostępne na http://localhost:8000
```

## Struktura projektu

```
clickbait-verifier/
├─ clickbait_verifier/       # Główny moduł Python
│  ├─ scraper.py             # Pobieranie artykułów
│  ├─ analyzer.py            # Analiza clickbaitu
│  ├─ reporter.py            # Generowanie raportów
│  ├─ extractors/            # Konfiguracje dla portali
│  └─ ui/                    # Komponenty UI (Streamlit)
├─ scripts/                  # Narzędzia automatyzacji
├─ reports/                  # Wygenerowane raporty
├─ config.yaml               # Konfiguracja źródeł
└─ api_server.py             # REST API
```

## Zastosowania

- **Badania naukowe** - analiza jakości dziennikarstwa
- **Edukacja medialna** - uczenie krytycznego myślenia
- **Monitoring mediów** - śledzenie trendów w komunikacji
- **Weryfikacja faktów** - wsparcie dla fact-checkerów
- **Personal tool** - świadome konsumowanie treści

## Dokumentacja

Projekt zawiera kompleksową dokumentację w repozytorium:
- `README.md` - instrukcje instalacji i użytkowania
- `clickbait_verifier_full_system_specification.md` - pełna specyfikacja systemu
- `QUICKSTART_GITHUB_MODELS.md` - integracja z AI models
- `docs/` - szczegółowe przewodniki (scoring, automatyzacja, analiza LLM)

## Dalszy rozwój

Planowane funkcje:
- Rozszerzenie o więcej źródeł informacji
- Integracja z dodatkowymi modelami AI (OpenAI, Azure, GitHub Models)
- Dashboard w React/Vue jako następca PoC Streamlit
- Eksport do Power BI
- Aplikacja mobilna (Android/iOS)
- Analiza sentiment i ton emocjonalny
- API webhooks dla integracji zewnętrznych

---

## Demo

System jest w pełni funkcjonalny i gotowy do prezentacji live. Chętnie przeprowadzę demonstrację wszystkich komponentów:
- Live scraping artykułów
- Analiza w czasie rzeczywistym
- Przeglądanie feedu w interfejsie Streamlit
- Generowanie raportów

---

Jestem otwarty/a na pytania, sugestie i dyskusję o projekcie. System jest modularny i łatwo rozszerzalny o nowe funkcjonalności.

**Kontakt:**  
[Twój email]  
[Opcjonalnie: telefon, LinkedIn]

**GitHub:**  
https://github.com/mkonefal2/clickbait_verifier

---

**Załączniki:**
- Screenshot interfejsu Streamlit
- Przykładowy raport dzienny (CSV/Markdown)
- Diagram architektury

---

Z poważaniem,  
[Twoje imię i nazwisko]

---

## Technical Details (Opcjonalnie - dla technicznego odbiorcy)

**Performance:**
- Scraping: ~50-100 artykułów/minutę
- Analiza: ~5-10 artykułów/sekundę
- Storage: ~100KB/artykuł (z metadanymi)

**Scalability:**
- Horizontal scaling przez API
- Database partitioning
- Async processing queues

**Security:**
- Input validation & sanitization
- Rate limiting
- CORS configuration
- API authentication ready

**Testing:**
- Unit tests dla core logic
- Integration tests dla extractors
- E2E tests dla API
