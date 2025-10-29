# Analiza artykułów za pomocą GPT-4o-mini

## Instalacja wymaganych bibliotek

```powershell
.\.venv\Scripts\python.exe -m pip install openai pyyaml
```

## Ustawienie klucza API

### Opcja 1: Zmienna środowiskowa (zalecane)
```powershell
$env:OPENAI_API_KEY = "sk-twoj-klucz-api"
```

### Opcja 2: Parametr w komendzie
```powershell
--api-key sk-twoj-klucz-api
```

## Podstawowe użycie

### 1. Sprawdź co zostanie przeanalizowane (dry-run)
```powershell
.\.venv\Scripts\python.exe scripts\analyze_with_llm.py --dry-run
```

### 2. Przeanalizuj wszystkie niezanalizowane artykuły
```powershell
.\.venv\Scripts\python.exe scripts\analyze_with_llm.py
```

### 3. Przeanalizuj tylko artykuły z konkretnego źródła
```powershell
# Tylko rmf24
.\.venv\Scripts\python.exe scripts\analyze_with_llm.py --source rmf24

# Tylko onet
.\.venv\Scripts\python.exe scripts\analyze_with_llm.py --source onet
```

### 4. Ogranicz liczbę artykułów (do testów)
```powershell
# Przeanalizuj tylko 10 pierwszych
.\.venv\Scripts\python.exe scripts\analyze_with_llm.py --limit 10

# Przeanalizuj 5 artykułów z rmf24
.\.venv\Scripts\python.exe scripts\analyze_with_llm.py --limit 5 --source rmf24
```

### 5. Ponowna analiza istniejących plików
```powershell
.\.venv\Scripts\python.exe scripts\analyze_with_llm.py --overwrite --limit 10
```

## Zaawansowane opcje

### Użycie innego modelu OpenAI
```powershell
# GPT-4 (droższy, lepszy)
.\.venv\Scripts\python.exe scripts\analyze_with_llm.py --model gpt-4o --limit 5

# GPT-3.5 Turbo (tańszy)
.\.venv\Scripts\python.exe scripts\analyze_with_llm.py --model gpt-3.5-turbo
```

### Kombinacja parametrów
```powershell
# Przeanalizuj 20 artykułów z rmf24 używając GPT-4o-mini
.\.venv\Scripts\python.exe scripts\analyze_with_llm.py `
    --model gpt-4o-mini `
    --source rmf24 `
    --limit 20
```

## Lista dostępnych niezanalizowanych artykułów

```powershell
# Zobacz które artykuły czekają na analizę
.\.venv\Scripts\python.exe scripts\list_unanalyzed.py

# Eksportuj listę do JSON
.\.venv\Scripts\python.exe scripts\list_unanalyzed.py --write-json unanalyzed.json

# Tylko dla konkretnego źródła
.\.venv\Scripts\python.exe scripts\list_unanalyzed.py --source rmf24
```

## Przykładowy workflow

```powershell
# 1. Sprawdź ile artykułów czeka na analizę
.\.venv\Scripts\python.exe scripts\list_unanalyzed.py

# 2. Testuj na 3 artykułach (dry-run)
.\.venv\Scripts\python.exe scripts\analyze_with_llm.py --limit 3 --dry-run

# 3. Przeanalizuj testowe 3 artykuły
.\.venv\Scripts\python.exe scripts\analyze_with_llm.py --limit 3

# 4. Jeśli OK, przeanalizuj wszystkie z jednego źródła
.\.venv\Scripts\python.exe scripts\analyze_with_llm.py --source rmf24

# 5. Następnie pozostałe źródła
.\.venv\Scripts\python.exe scripts\analyze_with_llm.py --source onet
```

## Co robi skrypt?

1. **Wczytuje specyfikację** z `clickbait_agent_spec_v1.1.yaml`
2. **Znajduje niezanalizowane artykuły** w `reports/scraped/`
3. **Dla każdego artykułu:**
   - Wysyła tytuł + treść do OpenAI GPT
   - Model analizuje wg reguł ze specyfikacji
   - Generuje pełny JSON z oceną clickbaitu
   - **Automatycznie tworzy pole `summary`** (obiektywne streszczenie treści)
4. **Zapisuje wyniki** do `reports/analysis/analysis_{id}.json`

## Format wyjściowy

Każda analiza zawiera:
```json
{
  "id": 1761328130371,
  "source": "rmf24",
  "url": "https://...",
  "title": "...",
  "score": 34,
  "label": "mild",
  "rationale": ["Techniczne uzasadnienie..."],
  "rationale_user_friendly": ["Przystępne wyjaśnienie..."],
  "summary": "Obiektywne streszczenie treści artykułu w 2-4 zdaniach (max 400 znaków)",
  "signals": {
    "title_hits": ["..."],
    "content_hits": ["..."],
    "credibility_hits": ["..."],
    "mismatch": {...}
  },
  "suggestions": {
    "rewrite_title_neutral": "...",
    "notes_to_editor": "..."
  },
  "diagnostics": {
    "tokens_title": 10,
    "tokens_content": 450,
    "processing_time_ms": 1234,
    "model": "gpt-4o-mini"
  }
}
```

## Koszty

Przybliżone koszty dla **gpt-4o-mini** (2025):
- Input: ~$0.15 / 1M tokenów
- Output: ~$0.60 / 1M tokenów
- Średnio ~2000 tokenów na artykuł
- **Koszt: ~$0.001-0.002 za artykuł** (około 0.5 grosza)

Dla 100 artykułów: ~$0.10-0.20 (około 50 groszy)

## Troubleshooting

### Błąd: "openai library not installed"
```powershell
.\.venv\Scripts\python.exe -m pip install openai pyyaml
```

### Błąd: "OpenAI API key required"
```powershell
$env:OPENAI_API_KEY = "sk-twoj-klucz"
```

### Rate limit exceeded
Skrypt automatycznie czeka 1 sekundę między requestami. Jeśli nadal błąd:
- Zmniejsz `--limit`
- Zwiększ opóźnienie w kodzie (edytuj `time.sleep(1)` → `time.sleep(2)`)

### Timeout / długie artykuły
Skrypt przycina treść do 8000 znaków. Możesz zmienić w kodzie:
```python
max_content = 8000  # zwiększ jeśli potrzeba
```

## Porównanie z metodą automatyczną

| Metoda | Prędkość | Jakość | Koszt | Summary |
|--------|----------|--------|-------|---------|
| `analyze_batch_job_auto.py` | ⚡ Bardzo szybka | 📊 Dobra (regex) | 💚 Darmowa | ❌ Podstawowe (heurystyka) |
| `analyze_with_llm.py` | 🐌 Wolna (1s/art.) | 🎯 Doskonała (AI) | 💰 ~0.5gr/art. | ✅ Wysokiej jakości |

**Zalecenie:** 
- Użyj LLM dla finalnych analiz publikowanych dla użytkowników
- Użyj auto dla szybkich testów i dużych wolumenów
