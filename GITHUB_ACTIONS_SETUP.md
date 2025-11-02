# GitHub Actions - Automatyczne Scrapowanie i Analiza GPT

## 🎯 Co robi?
GitHub Actions automatycznie:
1. **Scrapuje** artykuły z skonfigurowanych źródeł
2. **Analizuje** je przez OpenAI GPT API
3. **Commituje** wyniki do repozytorium
4. **Uruchamia się** codziennie o 8:00 i 20:00 UTC

## 📋 Kroki konfiguracji

### 1. Dodaj GitHub Secret
Przejdź do swojego repo na GitHubie:
```
Settings → Secrets and variables → Actions → New repository secret
```

**Nazwa:** `OPENAI_API_KEY`  
**Wartość:** Twój klucz API (sk-proj-GIHDRX...)

### 2. Upewnij się, że Actions mają uprawnienia do commitów
```
Settings → Actions → General → Workflow permissions
→ Zaznacz "Read and write permissions"
→ Save
```

### 3. Push workflow do GitHub
```bash
git add .github/workflows/auto-scrape-analyze.yml
git commit -m "Add GitHub Actions workflow for auto-scraping"
git push
```

### 4. Sprawdź uruchomienie
```
Actions → Scrape and Analyze Articles with GPT
```

## 🕐 Harmonogram

**Domyślnie:** Codziennie o 8:00 i 20:00 UTC (10:00 i 22:00 w Polsce w zimie)

Zmień harmonogram w pliku `.github/workflows/auto-scrape-analyze.yml`:
```yaml
schedule:
  - cron: '0 8,20 * * *'  # 8:00 i 20:00 UTC
  # - cron: '0 */6 * * *'   # Co 6 godzin
  # - cron: '0 0 * * *'     # Raz dziennie o północy
```

## 🔧 Ręczne uruchomienie

Możesz uruchomić workflow ręcznie:
```
Actions → Scrape and Analyze Articles with GPT → Run workflow
```

## 📊 Co się dzieje?

1. **Checkout** - pobiera kod z repozytorium
2. **Setup Python** - instaluje Python 3.11
3. **Install dependencies** - instaluje pakiety z requirements.txt
4. **Scrape articles** - uruchamia scraper
5. **Analyze with GPT** - analizuje artykuły przez OpenAI API
6. **Commit results** - zapisuje wyniki do repo
7. **Summary** - pokazuje statystyki

## 💰 Koszty

**GitHub Actions:** Darmowe dla publicznych repo (2000 minut/miesiąc dla prywatnych)

**OpenAI API:**
- ~$0.0001 za artykuł (gpt-4o-mini)
- ~50 artykułów dziennie × 2 uruchomienia = 100 analiz
- **~$0.01/dzień** = **~$3/rok**

## ⚠️ Uwagi

1. **Limity rate**: Workflow czeka 1s między requestami do OpenAI
2. **Duplicates**: `analyze_today.py` automatycznie pomija duplikaty
3. **Errors**: `continue-on-error: true` zapewnia, że workflow się nie zatrzyma przy błędach
4. **Commit conflicts**: Jeśli committujesz manualnie, może być conflict - workflow to obsłuży

## 🔍 Monitoring

Sprawdź logi workflow:
```
Actions → [wybierz uruchomienie] → [kliknij job]
```

Zobacz użycie OpenAI API:
```
https://platform.openai.com/usage
```

## 🚀 Dodatkowe opcje

### Playwright dla dynamicznych stron
Odkomentuj w workflow:
```yaml
# pip install playwright
# python -m playwright install chromium
```

### Notyfikacje (Discord/Slack)
Dodaj webhook w workflow:
```yaml
- name: Notify Discord
  if: always()
  run: |
    curl -X POST ${{ secrets.DISCORD_WEBHOOK }} \
      -H "Content-Type: application/json" \
      -d '{"content": "✅ Analysis complete: $(ls reports/analysis/ | wc -l) files"}'
```

### Deploy do GitHub Pages
Dodaj krok generujący statyczny HTML z wynikami:
```yaml
- name: Deploy to GitHub Pages
  uses: peaceiris/actions-gh-pages@v3
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    publish_dir: ./reports
```

## 📧 Pytania?

Sprawdź logi workflow lub otwórz issue w repo!
