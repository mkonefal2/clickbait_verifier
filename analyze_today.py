#!/usr/bin/env python3
"""
Batch analyze today's scraped articles with GPT
"""
import json
import time
from pathlib import Path
from datetime import datetime, timezone
from clickbait_verifier.analyzer import GPTAnalyzer

def analyze_todays_articles():
    """Analyze articles scraped today with GPT."""
    
    # Get today's date dynamically
    today = datetime.now(timezone.utc)
    today_str = today.strftime("%d %B %Y")
    
    # Calculate timestamp range for today (00:00 to 23:59 UTC)
    today_start = int(today.replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000)
    today_end = int(today.replace(hour=23, minute=59, second=59, microsecond=999999).timestamp() * 1000)
    
    print(f"🚀 Analiza GPT artykułów z dzisiaj ({today_str})")
    print("=" * 60)
    
    # Initialize analyzer
    try:
        analyzer = GPTAnalyzer()
        print("✅ GPT Analyzer zainicjalizowany (model: gpt-4o-mini)")
    except Exception as e:
        print(f"❌ Błąd inicjalizacji: {e}")
        return
    
    scraped_dir = Path('reports/scraped')
    analysis_dir = Path('reports/analysis')
    analysis_dir.mkdir(exist_ok=True)
    
    # Find existing analyses
    existing = set()
    if analysis_dir.exists():
        for f in analysis_dir.glob('analysis_*.json'):
            try:
                with open(f, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    existing.add(str(data.get('id')))
            except: 
                pass
    
    print(f"📊 Istniejące analizy: {len(existing)}")
    
    # Find today's articles using timestamp range instead of prefix
    all_scraped_files = list(scraped_dir.glob('scraped_*.json'))
    todays_files = []
    
    for file in all_scraped_files:
        try:
            # Extract timestamp from filename
            timestamp = int(file.stem.replace('scraped_', ''))
            if today_start <= timestamp <= today_end:
                todays_files.append(file)
        except ValueError:
            pass  # Skip files with invalid timestamp format
    
    to_analyze = []
    seen_titles = set()  # Track titles to avoid duplicates
    
    for file in todays_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                article = json.load(f)
            aid = str(article.get('id', ''))
            title = article.get('title', '')
            
            # Skip if already analyzed OR if we've seen this title
            if aid and aid not in existing and title not in seen_titles:
                to_analyze.append((file, article, aid))
                seen_titles.add(title)
            elif title in seen_titles:
                print(f"⏭️  Pominięto duplikat: {title[:50]}...")
        except Exception as e:
            print(f"⚠️  Błąd ładowania {file}: {e}")
    
    print(f"🎯 Nowych artykułów do analizy: {len(to_analyze)}")
    print(f"📅 Wszystkie z dzisiaj ({today_str})")
    print()
    
    if not to_analyze:
        print("✅ Wszystkie dzisiejsze artykuły już przeanalizowane!")
        return
    
    # Analyze in batches
    batch_size = 5
    total_batches = (len(to_analyze) + batch_size - 1) // batch_size
    
    analyzed_count = 0
    failed_count = 0
    
    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, len(to_analyze))
        batch = to_analyze[start_idx:end_idx]
        
        print(f"📦 Przetwarzam batch {batch_num + 1}/{total_batches} ({len(batch)} artykułów)")
        
        for i, (file, article, aid) in enumerate(batch):
            try:
                title = article.get('title', 'Brak tytułu')[:60]
                source = article.get('source', 'unknown')
                
                print(f"  [{start_idx + i + 1}/{len(to_analyze)}] {source}: {title}...")
                
                # Analyze with GPT
                start_time = time.time()
                result = analyzer.analyze_article(article)
                elapsed = time.time() - start_time
                
                if result:
                    # Save analysis
                    analysis_path = analysis_dir / f'analysis_{aid}.json'
                    
                    with open(analysis_path, 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                    
                    score = result.get('score', 0)
                    label = result.get('label', 'unknown')
                    
                    print(f"    ✅ {score}/100 ({label}) [{elapsed:.1f}s]")
                    analyzed_count += 1
                else:
                    print(f"    ❌ Analiza nieudana [{elapsed:.1f}s]")
                    failed_count += 1
                
                # Rate limiting (1 second between requests)
                time.sleep(1)
                
            except KeyboardInterrupt:
                print(f"\n⏹️  Przerwano przez użytkownika")
                print(f"📊 Przeanalizowano: {analyzed_count}, Błędy: {failed_count}")
                return
                
            except Exception as e:
                print(f"    ❌ Błąd: {str(e)[:50]}...")
                failed_count += 1
        
        print(f"  📦 Batch {batch_num + 1} zakończony\n")
        
        # Brief pause between batches
        if batch_num < total_batches - 1:
            print("  ⏳ Krótka pauza...")
            time.sleep(2)
    
    print("=" * 60)
    print(f"🎉 ANALIZA ZAKOŃCZONA!")
    print(f"✅ Przeanalizowanych artykułów: {analyzed_count}")
    print(f"❌ Nieudanych analiz: {failed_count}")
    print(f"💰 Szacowany koszt: ${analyzed_count * 0.0001:.4f}")
    print(f"🕐 Całkowity czas: ~{(analyzed_count + failed_count) * 12 / 60:.1f} minut")
    print()
    print("🌐 Zobacz wyniki w aplikacji Streamlit:")
    print("   http://localhost:8501")

if __name__ == "__main__":
    analyze_todays_articles()