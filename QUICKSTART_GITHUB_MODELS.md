# Quick Start: Analiza z GitHub Models

## 🎯 Szybkie kroki (5 minut)

### 1. Ustaw token
```powershell
$env:GITHUB_TOKEN = "ghp_twoj_token_tutaj"
```

### 2. Test (dry-run)
```powershell
cd D:\clickbait
.\.venv\Scripts\python.exe scripts\analyze_with_github_models.py --dry-run
```

### 3. Analiza (start małym testem!)
```powershell
# Pierwsze 5 artykułów (test)
.\.venv\Scripts\python.exe scripts\analyze_with_github_models.py --limit 5

# Jeśli działa OK, więcej:
.\.venv\Scripts\python.exe scripts\analyze_with_github_models.py --limit 20 --delay 5
```

### 4. Sprawdź wyniki
```powershell
Get-ChildItem reports\analysis\*.json | Select-Object -Last 5
```

---

## 📋 Pełna dokumentacja
Zobacz: `scripts\README_GITHUB_MODELS.md`

---

## ⚡ Najczęstsze komendy

```powershell
# Test co zostanie przeanalizowane
.\.venv\Scripts\python.exe scripts\analyze_with_github_models.py --dry-run

# Analiza 10 artykułów
.\.venv\Scripts\python.exe scripts\analyze_with_github_models.py --limit 10

# Wolniejsze tempo (unikanie rate limit)
.\.venv\Scripts\python.exe scripts\analyze_with_github_models.py --limit 10 --delay 6

# Wszystkie niezanalizowane (może trwać długo!)
.\.venv\Scripts\python.exe scripts\analyze_with_github_models.py
```

---

## ✅ Co działa

- ✅ Znajduje niezanalizowane scraped_*.json
- ✅ Używa GitHub Models API (darmowe w limitach)
- ✅ Generuje analizy zgodne ze specyfikacją
- ✅ Zapisuje do reports/analysis/
- ✅ Dodaje pole summary (2-4 zdania, max 400 znaków)
- ✅ Działa z tokenem GitHub (nie wymaga OpenAI API key)

---

## 🐛 Problemy?

**Brak tokenu:**
```powershell
$env:GITHUB_TOKEN = "ghp_..."
```

**Rate limit:**
```powershell
# Zwiększ delay
--delay 7
```

**Błąd YAML:**
- Skrypt automatycznie użyje minimalnej specyfikacji
- Analiza będzie działać normalnie

---

## 📊 Przykład output

```
============================================================
Clickbait Analyzer - GitHub Models Edition
============================================================

Loading specification...
Loaded spec version 1.2.3

Scanning for unanalyzed articles...
Found 54 unanalyzed articles

Connecting to GitHub Models API...
Connected! Using model: gpt-4o-mini

Starting analysis (delay: 4.0s between requests)...
------------------------------------------------------------

[1/5] Analyzing scraped_1761516140565.json...
[OK] Saved to analysis_1761516140565.json
     Score: 34, Label: mild

[2/5] Analyzing scraped_1761516141249.json...
[OK] Saved to analysis_1761516141249.json
     Score: 68, Label: strong

...

============================================================
Analysis Complete!
============================================================
[OK] Successful: 5
[ERROR] Errors: 0
Results saved to: D:\clickbait\reports\analysis
```

---

## 🚀 Następne kroki

1. **Przeanalizuj wszystkie** (po testach):
   ```powershell
   .\.venv\Scripts\python.exe scripts\analyze_with_github_models.py --delay 5
   ```

2. **Commit wyników**:
   ```powershell
   git add reports/analysis/
   git commit -m "Add AI-powered clickbait analysis"
   git push
   ```

3. **Zobacz w UI**:
   ```powershell
   .\.venv\Scripts\streamlit.exe run clickbait_verifier\streamlit_app.py
   ```
