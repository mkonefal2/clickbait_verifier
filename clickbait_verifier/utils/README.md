# Utils Module

Ten katalog zawiera funkcje pomocnicze i narzędzia wspierające aplikację.

## Pliki

- **`helpers.py`** - Ogólne funkcje pomocnicze (pobieranie obrazów, rerun)
- **`file_loader.py`** - Zarządzanie plikami JSON (ładowanie, parsowanie, organizacja)

## Konwencje

- Funkcje są stateless (bezstanowe) gdzie to możliwe
- Używaj type hints dla wszystkich parametrów i zwracanych wartości
- Obsługuj błędy gracefully i zwracaj None/puste kolekcje zamiast rzucać wyjątki
- Dokumentuj funkcje za pomocą docstringów
