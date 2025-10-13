Instrukcje dla zewnętrznego agenta (np. GitHub Copilot coding agent)

Cel
- Otrzymujesz plik JSON z zescrapowanymi artykułami: reports/scraped_for_copilot_<timestamp>.json
- Twoim zadaniem jest porównać nagłówki (title) z treścią (content) i ocenić "clickbaitowość" każdego artykułu.
- Zwróć przetworzony plik JSON z dodatkowymi polami oraz wygeneruj raport markdown.

Wejście (format)
- Plik: reports/scraped_for_copilot_*.json
- Każdy obiekt ma pola: id, source, title, content, url, published, fetched_at

Wyjście (format)
- JSON: reports/for_copilot_analyzed_<timestamp>.json — lista obiektów z dodatkowymi polami:
  - id (jak w wejściu)
  - score: liczba 0-100 (wyższa = bardziej clickbait)
  - similarity: liczba 0.0-1.0 (semantyczne podobieństwo title vs content)
  - label: jeden z {none, low, medium, high}
  - reasons: string lub lista przyczyn/cech (np. "sensational_language, missing_evidence")
  - analyzed_at: ISO 8601 timestamp
  - (opcjonalnie) excerpt: krótki fragment contentu uzasadniający ocenę

Wytyczne scoringu (rozszerzone, z przykładami i wskazówkami)

- similarity (0.0 - 1.0)
  - Co to jest: miara semantycznego pokrycia między tytułem a treścią artykułu. 1.0 = tytuł dokładnie odzwierciedla treść; 0.0 = tytuł i treść są niepowiązane.
  - Wskazówki jak oceniać:
    - Sprawdź czy wszystkie kluczowe twierdzenia z tytułu pojawiają się w treści (np. konkretne odkrycie, liczby, wydarzenie). Jeśli tak, similarity bliżej 1.0.
    - Jeśli tytuł używa słów ogólnych, metafor lub nadmiernej uogólnionej sensacji ("wywraca naukę"), ale treść opisuje konkretne wyniki, similarity umiarkowane (~0.4–0.7).
    - Jeśli tytuł wprowadza nowy fakt, którego brak w tekście (niepotwierdzone twierdzenie), similarity niskie (<0.3).

  - Przykłady (title -> excerpt z content -> suggested similarity):
    1) "Nowe badanie: lek X leczy raka" -> content: szczegółowe badania na modelach i wyniki kliniczne potwierdzające -> similarity 0.9–1.0
    2) "Lek X może pomóc w leczeniu raka" -> content: wstępne badania na komórkach, brak dowodów klinicznych -> similarity 0.6–0.8
    3) "Lek X leczy raka" -> content: artykuł opisuje hipotezę bez dowodów -> similarity 0.1–0.3
    4) "Sensacja: znaleziono życie na Marsie" -> content: artykuł omawia badania wskazujące na związki chemiczne, bez dowodu życia -> similarity 0.2–0.4
    5) "Mała skamieniałość może zmienić historię ewolucji" -> content: dane i analiza mówiące o przesunięciu datowania -> similarity 0.5–0.8

- score (0–100)
  - Podstawa: score = (1 - similarity) * 100 — im mniejsze pokrycie semantyczne, tym wyższy score.
  - Modyfikatory (dodaj/odejmij po obliczeniu bazowym):
    - +10 jeśli tytuł używa mocnych/sensacyjnych słów lub nadawanego wpływu (słowa-klucze: "rewolucja", "wywraca", "zmienia historię", "sensacja", "szokujące") — gdy nagłówek sugeruje przebiegłą zmianę, a treść nie potwierdza proporcjonalnie.
    - -10 jeśli treść wyraźnie wspiera tytuł konkretnymi dowodami (badania, cytowania, daty, linki do publikacji, dane liczbowe).
    - +5 jeśli tytuł zawiera nierzeczywiste uogólnienia (np. "wszyscy", "zawsze", "nigdy") a treść ma ograniczony kontekst.
    - -5 jeśli tytuł jest powściągliwy i treść ma szerokie potwierdzenia.
  - Ogranicz score do przedziału 0–100 po zastosowaniu modyfikatorów.

  - Przykłady obliczeń:
    1) similarity=0.90 -> base=(1-0.9)*100=10; tytuł umiarkowany, treść wspiera -> -10 => score=0 -> label=none
    2) similarity=0.55 -> base=45; tytuł mocny (+10), treść częściowo wspiera (-10) => 45+10-10=45 -> label=low
    3) similarity=0.25 -> base=75; tytuł mocny (+10), brak dowodów => 85 -> label=high
    4) similarity=0.60 -> base=40; treść ma solidne cytowania (-10) => 30 -> label=low

- label (kategoryzacja)
  - none: score <= 20 — tytuł dobrze odzwierciedla treść, niewiele cech clickbaitowych
  - low: 20 < score <= 50 — umiarkowana sensacyjność; wymaga krótkiej weryfikacji
  - medium: 50 < score <= 80 — wyraźne elementy clickbaitowe; rekomendowana redakcyjna korekta
  - high: score > 80 — tytuł prawdopodobnie wprowadza w błąd lub jest przesadny; wymagane działanie redakcyjne

- reasons (wyjaśnienie, krótkie klucze)
  - Zawsze zwracaj listę krótkich kluczy (CSV lub JSON array) objaśniających przyczyny oceny. Przykładowe klucze:
    - sensational_language — tytuł używa mocnych słów/sensacji
    - missing_evidence — treść nie zawiera dowodów na twierdzenia z tytułu
    - supported_by_references — treść zawiera odwołania do badań/źródeł
    - short_title — tytuł bardzo krótki i nieprecyzyjny
    - speculative_language — tytuł formułowany jako hipoteza bez potwierdzenia
    - overgeneralization — tytuł uogólnia ("wszyscy", "zawsze")
    - numbers_mismatch — liczby/rok/wyniki w tytule nie znajdują potwierdzenia w treści
    - ambiguous_subject — brak jasnego podmiotu w tytule

  - Przykłady reason dla naszych przypadków:
    1) Tytuł: "Nowy lek leczy raka"; content: hipoteza -> reasons=["sensational_language","missing_evidence","speculative_language"]
    2) Tytuł: "Naukowcy zmieniają historię ewolucji"; content: analiza datowania, cytowania badań -> reasons=["sensational_language","supported_by_references"]
    3) Tytuł: "Powiązano X z Y"; content: meta-analiza i liczne odwołania -> reasons=["supported_by_references"]

- excerpt
  - Jeśli to możliwe, dołącz krótki fragment (1-2 zdania) z treści, który dowodzi lub obala twierdzenie w tytule. To ułatwi redakcji szybką weryfikację.

- Dodatkowe wskazówki techniczne
  - Jeśli title albo content są puste lub krótkie, ustaw similarity=0 i reason "missing_content".
  - Dla artykułów zawierających listy/FAQ sprawdź, czy poszczególne punkty wspierają twierdzenie z tytułu.
  - Użyj prostych NLP / embeddingów do estymacji similarity; jeśli brak modelu, heurystyka oparta na pokryciu słów kluczowych i fraz też akceptowalna.

- Bogate przypadki testowe (przykłady uczące)
  1) Title: "Naukowcy odkryli lek na Alzheimer"; Content: obiecujące wyniki na myszach, brak badań klinicznych -> similarity 0.3–0.4; score ~60; reasons: ["sensational_language","missing_evidence","speculative_language"]
  2) Title: "Badanie pokazuje związek między kawą a długowiecznością"; Content: duża kohorta, kontrolowane zmienne, jasne ograniczenia -> similarity 0.7–0.85; score ~15–30; reasons: ["supported_by_references"]
  3) Title: "Cudowny sposób na schudnięcie bez diety"; Content: artykuł promocyjny, brak badań -> similarity 0.1; score ~90; reasons: ["sensational_language","missing_evidence"]
  4) Title: "Mała skamieniałość może zmienić historię ewolucji"; Content: analiza datowania i argumenty naukowe -> similarity 0.5–0.75; score ~25–55 depending on modifiers; reasons: ["sensational_language","supported_by_references"]
  5) Title: "Nowe odkrycie: X prawdopodobnie nie wpływa na Y"; Content: meta-analiza przecząca hipotezie -> similarity 0.6–0.9; score niskie; reasons: ["supported_by_references"]

- Format wyjściowy (przykład)
{
  "id": 1760308377777,
  "score": 40.08,
  "similarity": 0.5489,
  "label": "low",
  "reasons": ["sensational_language","supported_by_references"],
  "analyzed_at": "2025-10-13T12:34:56Z",
  "excerpt": "Gdy paleontolog spacerujący po plaży w Devon natrafił na niepozorną skamieniałość..."
}

Dalsze kroki po wygenerowaniu wyników
1) Umieść plik `reports/for_copilot_analyzed_<timestamp>.json` jako artifact lub commit do repo.
2) Uruchomić lokalnie: `python scripts/import_agent_results.py reports/for_copilot_analyzed_<timestamp>.json` — skrypt zaktualizuje DB i wygeneruje markdown raport.

Kontakt
- Jeśli potrzebujesz dodatkowych reguł scoringu, dodaj je tutaj lub w pliku konfiguracyjnym projektu.
