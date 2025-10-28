# Changelog - Version 1.2.3

**Data:** 2025-10-28  
**Typ:** Minor Update - Rozszerzenie schematu wyjściowego

## 🆕 Nowe funkcje

### Pole `summary` w analizach

Dodano wymagane pole `summary` do wszystkich analiz clickbaitowych. 

**Charakterystyka:**
- **Długość:** 2-4 zdania, maksymalnie 400 znaków
- **Treść:** Obiektywne streszczenie TREŚCI artykułu (nie analizy clickbaitowości)
- **Cel:** Pozwala użytkownikom szybko zrozumieć o czym jest artykuł bez jego czytania
- **Styl:** Neutralny, informacyjny, jak w kronice prasowej

**Przykład streszczenia:**
```json
{
  "summary": "Naukowcy z Uniwersytetu Warszawskiego odkryli nowy gatunek żaby w Amazonii. Zwierzę wyróżnia się niebieskim ubarwieniem i wydaje nietypowe dźwięki. Odkrycie zostało opublikowane w czasopiśmie Nature."
}
```

## 📝 Zmodyfikowane pliki

### 1. `clickbait_agent_spec_v1.1.yaml`
- **Wersja:** 1.2.2 → 1.2.3
- **Zmiany:**
  - Dodano `summary` do listy wymaganych pól w `output_schema`
  - Rozszerzono `llm_prompts.judgment_prompt` o punkt 10) z instrukcjami generowania streszczenia
  - Zaktualizowano metadane (`meta.version`, `meta.last_updated`, `meta.description`)

### 2. `schemas/output_template.json`
- Dodano pole `"summary": ""` do szablonu JSON

### 3. `scripts/analyze_batch_job_auto.py`
- Przepisano funkcję `_generate_summary()` aby generowała streszczenie treści artykułu zamiast analizy
- Dodano filtrowanie elementów UI/nawigacji (np. "Udostępnij", "Facebook")
- Poprawiono logikę wyboru zdań (pomiń zbyt krótkie, max 400 znaków)

### 4. `schemas/README.md`
- Zaktualizowano dokumentację o informacje o nowym polu `summary`
- Dodano `summary` do checklist sanitizacji i walidacji
- Zaktualizowano punkt 6 w "Guidelines for integrators"

### 5. `scripts/add_article_summaries.py`
- Skrypt już wcześniej obsługiwał dodawanie streszczeń
- Zgodny z nowymi wymaganiami (działa poprawnie)

## 🔄 Kompatybilność wsteczna

**Status:** ⚠️ Breaking change (minor)

- Wszystkie **nowe** analizy będą zawierać pole `summary`
- **Istniejące** analizy bez pola `summary` są nadal ważne, ale zaleca się:
  - Uruchomienie `scripts/add_article_summaries.py` aby dodać streszczenia do starszych analiz
  - Aktualizację narzędzi/UI które mogą oczekiwać tego pola

## 🧪 Testowanie

### Jak przetestować zmiany:

1. **Wygeneruj nową analizę:**
   ```powershell
   .\.venv\Scripts\python.exe scripts\analyze_batch_job_auto.py
   ```

2. **Sprawdź strukturę outputu:**
   ```powershell
   Get-Content "reports\analysis\analysis_<id>.json" | ConvertFrom-Json | Select-Object id, title, summary, score, label
   ```

3. **Dodaj streszczenia do istniejących analiz:**
   ```powershell
   .\.venv\Scripts\python.exe scripts\add_article_summaries.py
   ```

## 📊 Wpływ na istniejące dane

- **56** istniejących analiz zostało zaktualizowanych o pole `summary` (uruchomiono `add_article_summaries.py`)
- **3** najstarsze analizy nie otrzymały streszczeń (brak powiązanych plików scraped)

## ⚙️ Wymagania dla integracji LLM

Przy integracji z prawdziwym LLM-em (np. OpenAI, Anthropic), upewnij się że:
1. Prompt zawiera instrukcje z punktu 10) z `llm_prompts.judgment_prompt`
2. LLM generuje obiektywne, neutralne streszczenie treści (NIE analizy!)
3. Walidacja sprawdza obecność i długość pola `summary` (max 400 znaków)
4. Podczas sanitizacji inputu usuwane jest pole `summary` jeśli istnieje

## 🔗 Powiązane pliki

- Specyfikacja: `clickbait_agent_spec_v1.1.yaml`
- Szablon: `schemas/output_template.json`
- Dokumentacja: `schemas/README.md`
- Skrypt batch: `scripts/analyze_batch_job_auto.py`
- Skrypt dodawania: `scripts/add_article_summaries.py`

---

**Autorzy:** System automatyczny + GitHub Copilot  
**Review:** Wymagany przed wdrożeniem produkcyjnym
