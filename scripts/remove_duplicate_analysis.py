#!/usr/bin/env python3
"""
Skrypt do usuwania zduplikowanych plików analysis z sufiksami _1, _2, itp.
Zachowuje tylko oryginalne pliki bez sufiksów.
"""

import os
import re
from pathlib import Path

def remove_duplicate_analysis_files():
    """Usuwa pliki analysis z sufiksami _1, _2, _3 itp."""
    analysis_dir = Path("reports/analysis")
    
    if not analysis_dir.exists():
        print(f"❌ Katalog {analysis_dir} nie istnieje!")
        return
    
    # Pattern dla plików z sufiksami
    pattern = re.compile(r'analysis_\d+_\d+\.json$')
    
    removed_count = 0
    kept_count = 0
    
    print("🔍 Szukam duplikatów w", analysis_dir)
    
    for file_path in analysis_dir.glob("analysis_*.json"):
        if pattern.match(file_path.name):
            # To jest duplikat (ma sufiks _1, _2, itp.)
            try:
                file_path.unlink()
                print(f"🗑️  Usunięto: {file_path.name}")
                removed_count += 1
            except Exception as e:
                print(f"❌ Błąd przy usuwaniu {file_path.name}: {e}")
        else:
            # To jest oryginalny plik (bez sufiksu)
            kept_count += 1
    
    print(f"\n✅ Zakończono!")
    print(f"   Usuniętych duplikatów: {removed_count}")
    print(f"   Zachowanych oryginalnych: {kept_count}")

if __name__ == "__main__":
    remove_duplicate_analysis_files()
