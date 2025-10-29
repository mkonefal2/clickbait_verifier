# Analiza artykułów z GitHub Models API

Automatyczna analiza clickbaitu używająca **GitHub Models** (gpt-4o-mini) zamiast OpenAI API.

## ✅ Zalety

- **Darmowe** (w limitach: ~15 req/min, ~150k tokens/dzień)
- Nie wymaga klucza OpenAI API
- Używa tylko GitHub Personal Access Token
- Zgodne z `clickbait_agent_spec_v1.1.yaml`

---

## 🚀 Szybki start

### 1. Przygotowanie

**A) Zainstaluj bibliotekę (jednorazowo):**
```powershell
cd D:\clickbait
.\.venv\Scripts\python.exe -m pip install openai pyyaml
```

**B) Ustaw GitHub token:**
```powershell
# Opcja 1: Tymczasowo (na tę sesję):
$env:GITHUB_TOKEN = "ghp_twoj_token_tutaj"

# Opcja 2: Trwale (zapisz w systemie):
[System.Environment]::SetEnvironmentVariable('GITHUB_TOKEN', 'ghp_twoj_token', 'User')
```

> **Gdzie wziąć token?** https://github.com/settings/tokens
> - Zaznacz: `repo` (Full control of private repositories)
> - Generate token → skopiuj (zaczyna się `ghp_...`)

---

### 2. Użycie

**Analiza wszystkich niezanalizowanych artykułów:**
```powershell
.\.venv\Scripts\python.exe scripts\analyze_with_github_models.py
```

**Z limitami (zalecane na start):**
```powershell
# Tylko pierwsze 10 plików
.\.venv\Scripts\python.exe scripts\analyze_with_github_models.py --limit 10

# Dłuższe opóźnienie między requestami (unikaj rate limiting)
.\.venv\Scripts\python.exe scripts\analyze_with_github_models.py --limit 10 --delay 5
```

**Dry-run (zobacz co zostanie przeanalizowane):**
```powershell
.\.venv\Scripts\python.exe scripts\analyze_with_github_models.py --dry-run
```

**Użyj innego modelu:**
```powershell
# GPT-4o (lepszy ale wolniejszy)
.\.venv\Scripts\python.exe scripts\analyze_with_github_models.py --model gpt-4o --limit 5

# Claude 3.5 Sonnet
.\.venv\Scripts\python.exe scripts\analyze_with_github_models.py --model claude-3.5-sonnet --limit 5
```

---

## 📊 Przykładowy output

```
============================================================
📊 Clickbait Analyzer - GitHub Models Edition
============================================================

📋 Loading specification...
✅ Loaded spec version 1.2.3

🔍 Scanning for unanalyzed articles...
Found 47 unanalyzed articles
Processing first 10 (--limit 10)

🔑 Connecting to GitHub Models API...
✅ Connected! Using model: gpt-4o-mini

🚀 Starting analysis (delay: 4.0s between requests)...
------------------------------------------------------------

[1/10] Analyzing scraped_1761325508299.json...
✅ Saved to analysis_1761325508299.json
   Score: 42, Label: mild

[2/10] Analyzing scraped_1761325510755.json...
✅ Saved to analysis_1761325510755.json
   Score: 68, Label: strong

...

============================================================
📊 Analysis Complete!
============================================================
✅ Successful: 10
❌ Errors: 0
📁 Results saved to: D:\clickbait\reports\analysis
```

---

## 🔧 Opcje wiersza poleceń

| Opcja | Opis | Przykład |
|-------|------|----------|
| `--limit N` | Analizuj tylko pierwsze N plików | `--limit 10` |
| `--model MODEL` | Użyj innego modelu | `--model gpt-4o` |
| `--delay SECS` | Opóźnienie między requestami (domyślnie 4s) | `--delay 5` |
| `--dry-run` | Pokaż co zostanie przeanalizowane bez API calls | `--dry-run` |

---

## 📝 Dostępne modele w GitHub Models

| Model | Opis | Prędkość | Limity |
|-------|------|----------|--------|
| **gpt-4o-mini** ⭐ | Zalecany: szybki i tani | Bardzo szybka | 15 req/min, 150k tokens/dzień |
| `gpt-4o` | Lepszy ale wolniejszy | Średnia | 10 req/min, 50k tokens/dzień |
| `claude-3.5-sonnet` | Anthropic Claude | Średnia | Podobne limity |
| `llama-3.3-70b` | Meta Llama (open source) | Szybka | Wyższe limity |

Pełna lista: https://github.com/marketplace/models

---

## ⚠️ Rate Limiting

**GitHub Models ma limity:**
- ~15 requestów na minutę
- ~150,000 tokenów dziennie (gpt-4o-mini)

**Jak uniknąć limitów:**
```powershell
# Większe opóźnienie (7 sekund = max 8.5 req/min)
.\.venv\Scripts\python.exe scripts\analyze_with_github_models.py --delay 7

# Małe partie
.\.venv\Scripts\python.exe scripts\analyze_with_github_models.py --limit 10
# Poczekaj 5 minut...
.\.venv\Scripts\python.exe scripts\analyze_with_github_models.py --limit 10
```

---

## 🐛 Troubleshooting

### ❌ "GITHUB_TOKEN not found"
**Problem:** Brak tokenu w zmiennej środowiskowej

**Rozwiązanie:**
```powershell
$env:GITHUB_TOKEN = "ghp_twoj_token"
```

### ❌ "Import openai could not be resolved"
**Problem:** Brak biblioteki openai

**Rozwiązanie:**
```powershell
.\.venv\Scripts\python.exe -m pip install openai pyyaml
```

### ❌ "Rate limit exceeded"
**Problem:** Za dużo requestów na minutę

**Rozwiązanie:**
```powershell
# Zwiększ opóźnienie
.\.venv\Scripts\python.exe scripts\analyze_with_github_models.py --delay 10

# Lub czekaj między batches
```

### ❌ "Failed to parse JSON response"
**Problem:** Model zwrócił nieprawidłowy JSON

**Rozwiązanie:**
- Sprawdź czy model jest wspierany: https://github.com/marketplace/models
- Spróbuj `gpt-4o-mini` (najbardziej stabilny)
- Zgłoś issue jeśli problem się powtarza

---

## 📚 Porównanie metod analizy

| Metoda | Koszt | Jakość | Prędkość | Setup |
|--------|-------|--------|----------|-------|
| **GitHub Models** ⭐ | Darmowe | 90-95% | Średnia | Token (5 min) |
| OpenAI API | ~$0.03/50 art. | 90-95% | Szybka | Klucz + płatność |
| Regex (analyze_batch_job_auto.py) | Darmowe | 70-80% | Bardzo szybka | Brak |

---

## 🎯 Następne kroki

Po analizie możesz:

1. **Sprawdź wyniki:**
   ```powershell
   Get-ChildItem D:\clickbait\reports\analysis\*.json | Select-Object -First 5
   ```

2. **Commit do GitHub:**
   ```powershell
   git add reports/analysis/
   git commit -m "Add automated clickbait analysis"
   git push
   ```

3. **Uruchom Streamlit UI:**
   ```powershell
   .\.venv\Scripts\streamlit.exe run clickbait_verifier\streamlit_feed_app.py
   ```

---

## 💡 Wskazówki

- **Pierwsza analiza:** Użyj `--limit 5` żeby przetestować
- **Duże batche:** Analizuj 20-30 plików na raz z `--delay 5`
- **Nocne przetwarzanie:** Ustaw większe batche (50+) z długim delay
- **Monitoring kosztów:** GitHub Models są darmowe, ale mają dzienne limity tokenów

---

## 📖 Więcej informacji

- GitHub Models: https://github.com/marketplace/models
- Dokumentacja API: https://github.com/Azure-Samples/azureai-samples/tree/main/scenarios/github-models
- Limity: https://docs.github.com/en/github-models/
