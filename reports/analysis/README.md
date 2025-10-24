Instrukcja użycia walidatora schematu wyników analizy

Celem: upewnić się, że output LLM zawsze ma kompletną strukturę kluczy (szkielet), nawet jeśli wartości będą uzupełnione później przez pipeline. W produkcji **NIE** należy przekazywać do promptu prefilled wyników (score/label/rationale itp.).

Narzędzie:
 - `tools/enforce_output_schema.py` - walidator i uzupełniacz. Zawiera tryb "strict-template" który:
   - sprawdza, czy wymagane klucze są obecne,
   - wykrywa i zgłasza, gdy wejście zawiera prefilled pola wynikowe,
   - zwraca (do stdout) szkielet `schemas/output_template.json` z połączonymi wartościami (nie nadpisuje istniejących pól wejściowych).

Przykładowe użycie:

# Tryb strict (zalecany przed budowaniem promptu):
python tools/enforce_output_schema.py reports/analysis/some_llm_output.json --strict-template

# Domyślny tryb: waliduje i auto-uzupełnia brakujące wymagane klucze (przycisk "fill"):
python tools/enforce_output_schema.py reports/analysis/some_llm_output.json

Rekomendacje:
 - Zawsze uruchamiaj w trybie `--strict-template` przed dołączeniem szkieletu do promptu i usuń wszelkie prefilled pola.
 - Trzymaj przykłady (fixtures) z rzeczywistymi etykietami tylko w katalogu `tests/fixtures` i nie ładuj ich do promptów produkcyjnych.
 - Jeżeli chcesz aby LLM zwracał JSON o pełnym szkielecie, w prompt podaj `schemas/output_template.json` jako strukturę (klucze + puste wartości), a nie przykładowe wartości.
