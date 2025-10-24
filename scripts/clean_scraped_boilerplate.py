#!/usr/bin/env python3
"""Skrypt do usuwania (lub symulacji usuwania) plików JSON w reports/scraped,
które zawierają w polu 'content' określoną frazę boilerplate.

Użycie:
  python scripts/clean_scraped_boilerplate.py         # tylko podgląd (dry-run)
  python scripts/clean_scraped_boilerplate.py --yes   # usuń pasujące pliki
  python scripts/clean_scraped_boilerplate.py --phrase "Skorzystaj z naszego bota" --yes
  python scripts/clean_scraped_boilerplate.py --yes --backup

Opcje:
  --yes       Wykonaj faktyczne usunięcie plików. Bez tej opcji domyślnie działa jako "dry-run".
  --phrase    Fraza (literalna, case-insensitive) do wyszukania w polu 'content'.
  --backup    Jeśli podano, przenieś usuwane pliki do katalogu reports/scraped/removed zamiast usuwać.
"""
import argparse
import glob
import json
import os
import shutil
from pathlib import Path

DEFAULT_PHRASE = "skorzystaj z naszego bota"


def find_scraped_files(reports_dir: Path):
    p = reports_dir / 'scraped'
    return sorted(p.glob('scraped_*.json')) if p.exists() else []


def main():
    parser = argparse.ArgumentParser(description='Usuń pliki scraped_*.json zawierające boilerplate')
    parser.add_argument('--yes', action='store_true', help='Faktycznie usuń pliki (bez --yes tylko dry-run)')
    parser.add_argument('--phrase', type=str, default=DEFAULT_PHRASE, help='Fraza do wyszukania (case-insensitive)')
    parser.add_argument('--backup', action='store_true', help='Przenieś usuwane pliki do reports/scraped/removed zamiast kasować')
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    reports_dir = repo_root / 'reports'
    scraped_dir = reports_dir / 'scraped'

    files = find_scraped_files(reports_dir)
    if not files:
        print('Brak plików scraped_*.json w katalogu reports/scraped')
        return

    phrase = args.phrase.strip().lower()
    to_delete = []

    for f in files:
        try:
            with open(f, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
        except Exception as e:
            print(f'Nie można odczytać {f}: {e}')
            continue
        content = (data.get('content') or '')
        if phrase in content.lower():
            to_delete.append((f, data))

    print(f'Znaleziono {len(to_delete)} plików pasujących do frazy "{phrase}" (spośród {len(files)} plików)')
    if not to_delete:
        return

    if not args.yes:
        print('Dry-run: podaj --yes aby usunąć pliki. Pliki które pasują:')
        for f, _ in to_delete:
            print(' -', f)
        return

    # wykonujemy operację usunięcia lub przeniesienia
    removed_dir = scraped_dir / 'removed'
    if args.backup:
        removed_dir.mkdir(parents=True, exist_ok=True)

    deleted = []
    for f, data in to_delete:
        try:
            if args.backup:
                dest = removed_dir / f.name
                shutil.move(str(f), str(dest))
                deleted.append(dest)
                print(f'Przeniesiono: {f} -> {dest}')
            else:
                os.remove(f)
                deleted.append(f)
                print(f'Usunięto: {f}')
        except Exception as e:
            print(f'Błąd przy usuwaniu {f}: {e}')

    # zapis logu usuniętych plików
    try:
        log_path = scraped_dir / 'removed_log.json'
        log_entries = [{'file': str(x), 'title': (d.get('title') if (d:=data) else None)} for x, data in to_delete]
        with open(log_path, 'w', encoding='utf-8') as lf:
            json.dump(log_entries, lf, ensure_ascii=False, indent=2)
        print(f'Zapisano log usuniętych plików do {log_path}')
    except Exception:
        pass


if __name__ == '__main__':
    main()
