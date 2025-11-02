# Migracja do GPT API - Przewodnik

System Clickbait Verifier został zmigrowany do wykorzystania OpenAI GPT API do analizy artykułów. Oto kompletny przewodnik po nowych możliwościach.

## 🚀 Szybki Start

### 1. Wymagania

```bash
# Zainstaluj wymagane zależności (już w requirements.txt)
pip install openai

# Ustaw klucz API OpenAI
export OPENAI_API_KEY="sk-your-api-key"
# lub na Windows PowerShell:
$env:OPENAI_API_KEY="sk-your-api-key"
```

### 2. Podstawowe użycie

```bash
# Scrapowanie + automatyczna analiza nowego artykułu
python -m clickbait_verifier.main --url "https://example.com/article" --analyze

# Analiza wszystkich dotychczas niezanalizowanych artykułów
python -m clickbait_verifier.main --analyze-all

# Scrapowanie bez analizy (jak dotychczas)
python -m clickbait_verifier.main --url "https://example.com/article"

# Scrapowanie wszystkich źródeł z config.yaml + analiza
python -m clickbait_verifier.main --analyze-all
```

## 📋 Dostępne opcje

### Opcje scrapowania
- `--url URL` - URL artykułu do analizy
- `--source SOURCE` - nazwa źródła (domyślnie: CLI)
- `--method {auto,requests,playwright}` - metoda pobierania (domyślnie: auto)

### Opcje analizy GPT
- `--analyze` - automatyczna analiza nowo scrapowanych artykułów
- `--analyze-all` - analiza wszystkich dotychczas niezanalizowanych artykułów
- `--api-key KEY` - klucz OpenAI API (alternatywa do zmiennej środowiskowej)
- `--model MODEL` - model OpenAI (domyślnie: gpt-4o-mini)

## 💻 Użycie programistyczne

### Klasa GPTAnalyzer

```python
from clickbait_verifier.analyzer import GPTAnalyzer

# Inicjalizacja
analyzer = GPTAnalyzer(
    api_key="your-api-key",  # opcjonalne, użyje OPENAI_API_KEY
    model="gpt-4o-mini"      # lub gpt-4, gpt-3.5-turbo, etc.
)

# Analiza pojedynczego artykułu
article = {
    'id': 123,
    'title': 'Przykładowy tytuł artykułu',
    'content': 'Treść artykułu...',
    'url': 'https://example.com/article',
    'source': 'example'
}

result = analyzer.analyze_article(article)
print(f"Wynik: {result['score']} - {result['label']}")
print(f"Uzasadnienie: {result['rationale_user_friendly']}")

# Analiza wielu artykułów (z rate limiting)
articles = [article1, article2, ...]
results = analyzer.analyze_batch(articles, delay_seconds=1.0)
```

### Integracja z istniejącym kodem

```python
# Legacy support - stara funkcja nadal działa
from clickbait_verifier.analyzer import analyze_batch

try:
    results = analyze_batch([article])
    print("Analiza zakończona pomyślnie")
except RuntimeError as e:
    print(f"Błąd analizy: {e}")
```

## 🔧 Konfiguracja

### Modele OpenAI

Dostępne modele (według kosztów i jakości):

- **gpt-4o-mini** (domyślny) - najlepsza cena/jakość
- **gpt-4o** - najlepsza jakość, droższy
- **gpt-3.5-turbo** - najtańszy, niższa jakość

```bash
# Użycie konkretnego modelu
python -m clickbait_verifier.main --analyze-all --model gpt-4o
```

### Specyfikacja analizy

System używa pliku `clickbait_agent_spec_v1.1.yaml` do konfiguracji:

- Wzorce regex dla fraz sensacyjnych
- Wagi punktacji (tytuł vs treść vs mismatch)  
- Progi klasyfikacji (not_clickbait, mild, strong, extreme)
- Instrukcje dla modelu GPT

## 📊 Format wyniku analizy

Każda analiza generuje plik JSON z następującymi polami:

```json
{
  "id": 1761747039027,
  "source": "onet",
  "url": "https://example.com/article",
  "title": "Tytuł artykułu",
  "score": 45,
  "label": "mild",
  "rationale": [
    "Techniczne uzasadnienie dla audytu...",
    "Wykryto frazy sensacyjne w tytule..."
  ],
  "rationale_user_friendly": [
    "Tytuł zawiera elementy clickbait...",
    "Treść jest zgodna z tytułem..."
  ],
  "summary": "Obiektywne streszczenie treści artykułu w 2-4 zdaniach.",
  "signals": {
    "title_hits": ["wykryte frazy w tytule"],
    "content_hits": ["wykryte frazy w treści"],
    "credibility_hits": ["sygnały wiarygodności"],
    "mismatch": {
      "detected": false,
      "severity": "none"
    }
  },
  "suggestions": {
    "rewrite_title_neutral": "Propozycja neutralnego tytułu",
    "notes_to_editor": "Uwagi dla redaktora"
  },
  "diagnostics": {
    "tokens_title": 15,
    "tokens_content": 250,
    "processing_time_ms": 1250,
    "model": "gpt-4o-mini"
  }
}
```

## 🚦 Rate Limiting

System automatycznie implementuje rate limiting:

- Domyślnie 1 sekunda przerwy między zapytaniami
- Można dostosować w `analyzer.analyze_batch(articles, delay_seconds=2.0)`
- OpenAI ma limity API - sprawdź swoje konto

## 💰 Koszty

Orientacyjne koszty (październik 2024):

- **gpt-4o-mini**: ~$0.0001 za artykuł (bardzo tani)
- **gpt-4o**: ~$0.005 za artykuł  
- **gpt-3.5-turbo**: ~$0.00005 za artykuł

*Rzeczywiste koszty zależą od długości artykułu i aktualnych cen OpenAI*

## 🔍 Przykłady użycia

### Analiza konkretnego artykułu

```bash
# Przykład z rzeczywistym artykułem
python -m clickbait_verifier.main \
  --url "https://wiadomosci.onet.pl/swiat/rosja-walczy-z-czasem-analitycy-osw-o-strategii-kremla-wpadli-w-pulapke-jaka-sami-na/67xd3nv" \
  --source "onet" \
  --analyze
```

### Batch analiza wszystkich artykułów

```bash
# Przeanalizuj wszystkie dotychczas niezanalizowane artykuły
python -m clickbait_verifier.main --analyze-all

# Z custom modelem
python -m clickbait_verifier.main --analyze-all --model gpt-4o
```

### Debug i testowanie

```bash
# Sprawdź co będzie analizowane (bez API calls)
python scripts/analyze_with_llm.py --dry-run

# Analiza z limitem
python scripts/analyze_with_llm.py --limit 5 --model gpt-4o-mini
```

## 🏗️ Architektura

```
clickbait_verifier/
├── main.py              # Główny punkt wejścia z obsługą GPT
├── analyzer.py          # Klasa GPTAnalyzer
├── scraper.py           # Scrapowanie (bez zmian)
└── ...

scripts/
├── analyze_with_llm.py  # Standalone GPT analyzer
└── ...

reports/
├── scraped/             # Surowe artykuły
└── analysis/            # Wyniki analiz GPT
```

## 🆕 Nowe funkcje

1. **Podwójne uzasadnienie**: 
   - `rationale` - techniczne dla audytu
   - `rationale_user_friendly` - przystępne dla użytkownika

2. **Obiektywne streszczenia**:
   - Pole `summary` z krótkim streszczeniem treści
   - Neutralny ton, bez ocen clickbaitu

3. **Zaawansowane diagnostyki**:
   - Liczba tokenów, czas przetwarzania
   - Użyty model GPT

4. **Elastyczna konfiguracja**:
   - Różne modele OpenAI
   - Konfigurowalny rate limiting
   - Wsparcie dla kluczy API

## 🔧 Troubleshooting

### Błąd: "openai library not installed"
```bash
pip install openai
```

### Błąd: "OpenAI API key required"
```bash
export OPENAI_API_KEY="sk-your-api-key"
# lub użyj --api-key sk-your-api-key
```

### Błąd: "Rate limit exceeded"
- Zwiększ `delay_seconds` w `analyze_batch()`
- Sprawdź limity na swoim koncie OpenAI
- Użyj tańszego modelu (gpt-4o-mini)

### Błąd: "Spec file not found"
- Upewnij się że plik `clickbait_agent_spec_v1.1.yaml` istnieje w głównym katalogu

## 📚 Dodatkowe zasoby

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [OpenAI Pricing](https://openai.com/pricing)
- [Specyfikacja clickbait](./clickbait_agent_spec_v1.1.yaml)
- [Legacy skrypty](./scripts/) - kompatybilne z nowym systemem

---

**Migracja zakończona!** 🎉 Stary interfejs nadal działa, ale teraz używa GPT API.