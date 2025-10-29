# Automatyczna Analiza - GitHub Actions

Repozytorium ma 3 zautomatyzowane workflow do analizy artykułów:

## 🕐 1. Codzienna automatyczna analiza

**Plik:** `.github/workflows/daily-analysis.yml`

**Kiedy się uruchamia:**
- Automatycznie codziennie o **6:00 UTC** (7:00/8:00 czasu polskiego)
- Analizuje WSZYSTKIE niezanalizowane artykuły

**Co robi:**
1. Sprawdza ile jest niezanalizowanych artykułów
2. Analizuje je używając GitHub Models API
3. Commituje wyniki z wiadomością: `🤖 Automatic daily analysis: X new articles analyzed`
4. Pushuje na GitHub

**Konfiguracja:**
```yaml
schedule:
  - cron: '0 6 * * *'  # 6:00 UTC
```

**Zmiana godziny:**
- Edytuj plik `.github/workflows/daily-analysis.yml`
- Zmień `'0 6 * * *'` na np. `'0 22 * * *'` dla 22:00 UTC (23:00/00:00 PL)
- Format: `'minuty godziny * * *'`

---

## 🎯 2. Analiza na żądanie (ręczna)

**Plik:** `.github/workflows/analyze-on-demand.yml`

**Jak uruchomić:**
1. Idź do: https://github.com/mkonefal2/clickbait_verifier/actions
2. Kliknij **"Analyze New Articles (On-Demand)"** z lewej strony
3. Kliknij **"Run workflow"** (prawy górny róg)
4. Wybierz opcje:
   - **Limit:** 5 / 10 / 20 / 50 / all
   - **Delay:** 4-10 sekund między requestami
5. Kliknij **"Run workflow"** (zielony przycisk)

**Użycie:**
- Testowanie
- Szybka analiza małej partii
- Kontrola nad parametrami

---

## ⚡ 3. Auto-analiza po push scraped

**Plik:** `.github/workflows/auto-analyze-on-push.yml`

**Kiedy się uruchamia:**
- Automatycznie gdy wpushujesz nowe pliki `reports/scraped/scraped_*.json`

**Co robi:**
1. Wykrywa ile nowych plików scraped zostało dodanych
2. Automatycznie analizuje te nowe artykuły
3. Commituje wyniki

**Przykład:**
```bash
# Lokalnie scrape'ujesz nowe artykuły
python clickbait_verifier/scraper.py

# Commituje i pushujesz
git add reports/scraped/scraped_*.json
git commit -m "Add 10 new scraped articles"
git push

# GitHub Actions automatycznie:
# - Wykryje 10 nowych plików
# - Przeanalizuje je
# - Wcommituje wyniki
```

---

## 📊 Monitorowanie

### Sprawdź status workflow:
https://github.com/mkonefal2/clickbait_verifier/actions

### Logi z każdego uruchomienia:
1. Kliknij na workflow run
2. Zobacz "Summary" - ile artykułów przeanalizowano
3. Kliknij na job "analyze" → szczegółowe logi

---

## 🔧 Konfiguracja

### Rate Limiting (unikanie limitów API)

Wszystkie workflow używają `--delay 5` lub `--delay 6` (5-6 sekund między requestami).

**GitHub Models limity:**
- ~15 requestów/minutę
- Delay 5s = ~12 req/min (bezpieczne)
- Delay 6s = ~10 req/min (bardzo bezpieczne)

**Zmiana delay:**
Edytuj w pliku workflow:
```yaml
python scripts/analyze_with_github_models.py --delay 7  # Wolniej
```

### Zmiana godziny codziennej analizy

Edytuj `.github/workflows/daily-analysis.yml`:
```yaml
schedule:
  - cron: '0 22 * * *'  # 22:00 UTC = 23:00/00:00 czasu polskiego
```

**Przykłady cron:**
- `'0 6 * * *'` - 6:00 UTC (7:00/8:00 PL) ⭐ domyślne
- `'0 12 * * *'` - 12:00 UTC (13:00/14:00 PL)
- `'0 22 * * *'` - 22:00 UTC (23:00/00:00 PL)
- `'0 */6 * * *'` - co 6 godzin
- `'0 8 * * 1-5'` - 8:00 UTC, tylko dni robocze

---

## 🐛 Troubleshooting

### Workflow nie uruchamia się

**Sprawdź:**
1. Czy workflow są włączone: Settings → Actions → General → "Allow all actions"
2. Czy masz uprawnienia: Settings → Actions → General → Workflow permissions → "Read and write"

### "Rate limit exceeded"

**Rozwiązanie:**
- Zwiększ `--delay` w workflow (np. do 7-10 sekund)
- Zmniejsz liczbę analizowanych artykułów na raz

### Brak commitów

**Sprawdź:**
- Czy były nowe artykuły do analizowania?
- Zobacz logi: Actions → ostatni run → "Summary"

---

## 💡 Best Practices

1. **Codzienna analiza:** Pozostaw włączoną (daily-analysis.yml)
2. **On-demand:** Użyj dla testów lub pilnych analiz
3. **Auto-analyze:** Świetne gdy regularnie scrapujesz artykuły

**Kombinacja idealna:**
- Daily: Analizuje wszystko co zostało zescrapowane poprzedniego dnia
- Auto: Instant analiza gdy wpushujesz nowe scraped
- On-demand: Kontrola manualna gdy potrzeba

---

## 📈 Koszty

**GitHub Models API:**
- ✅ Darmowe w limitach
- ~15 req/min, ~150k tokenów/dzień
- Wystarczy na ~200-300 artykułów dziennie

**GitHub Actions:**
- ✅ Darmowe dla public repos
- 2000 minut/miesiąc dla prywatnych
- Każda analiza: ~2-5 minut

**Total: $0** 🎉

---

## 🚀 Następne kroki

1. **Commit workflows do repo:**
```bash
git add .github/workflows/
git commit -m "Add automated analysis workflows"
git push
```

2. **Włącz Actions (jeśli wyłączone):**
   - Settings → Actions → General
   - "Allow all actions and reusable workflows"

3. **Testuj:**
   - Uruchom "Analyze New Articles (On-Demand)" ręcznie
   - Sprawdź czy działa
   - Poczekaj na codzienną automatyczną analizę

4. **Monitoruj:**
   - https://github.com/mkonefal2/clickbait_verifier/actions
   - Włącz email notifications dla failed runs (opcjonalnie)
