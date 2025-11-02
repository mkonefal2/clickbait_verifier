"""
Analyze ALL unanalyzed scraped articles (regardless of date) using GPT API.
"""
import json
import time
from pathlib import Path
from clickbait_verifier.analyzer import GPTAnalyzer

def main():
    print("🚀 Analiza GPT wszystkich niezanalizowanych artykułów")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = GPTAnalyzer()
    print(f"✅ GPT Analyzer zainicjalizowany (model: {analyzer.model})")
    
    # Get all scraped files
    scraped_dir = Path("reports/scraped")
    analysis_dir = Path("reports/analysis")
    
    scraped_files = list(scraped_dir.glob("scraped_*.json"))
    existing_analyses = {f.stem.replace('analysis_', ''): f for f in analysis_dir.glob("analysis_*.json")}
    
    print(f"📊 Wszystkich scraped: {len(scraped_files)}")
    print(f"📊 Istniejących analiz: {len(existing_analyses)}")
    
    # Find unanalyzed
    to_analyze = []
    for scraped_file in scraped_files:
        scraped_id = scraped_file.stem.replace('scraped_', '')
        if scraped_id not in existing_analyses:
            to_analyze.append(scraped_file)
    
    print(f"🎯 Do przeanalizowania: {len(to_analyze)}")
    
    if not to_analyze:
        print("✅ Wszystkie artykuły już przeanalizowane!")
        return
    
    # Deduplicate by title
    seen_titles = set()
    unique_to_analyze = []
    
    for file in to_analyze:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                title = data.get('title', '').strip()
                if title and title not in seen_titles:
                    seen_titles.add(title)
                    unique_to_analyze.append(file)
        except Exception:
            continue
    
    print(f"🎯 Unikalne (po deduplikacji): {len(unique_to_analyze)}")
    print()
    
    # Analyze in batches
    batch_size = 5
    total = len(unique_to_analyze)
    
    for i in range(0, total, batch_size):
        batch = unique_to_analyze[i:i+batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (total + batch_size - 1) // batch_size
        
        print(f"📦 Przetwarzam batch {batch_num}/{total_batches} ({len(batch)} artykułów)")
        
        for j, scraped_file in enumerate(batch, 1):
            try:
                with open(scraped_file, 'r', encoding='utf-8') as f:
                    article = json.load(f)
                
                source = article.get('source', 'unknown')
                title = article.get('title', 'No title')[:60]
                article_num = i + j
                
                print(f"  [{article_num}/{total}] {source}: {title}...", end=' ', flush=True)
                
                start_time = time.time()
                result = analyzer.analyze_article(article)
                elapsed = time.time() - start_time
                
                if result:
                    # Save analysis
                    article_id = article.get('id', scraped_file.stem.replace('scraped_', ''))
                    analysis_file = analysis_dir / f"analysis_{article_id}.json"
                    
                    with open(analysis_file, 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                    
                    score = result.get('score', 0)
                    label = result.get('label', 'unknown')
                    print(f"✅ {score}/100 ({label}) [{elapsed:.1f}s]")
                else:
                    print(f"❌ Błąd analizy [{elapsed:.1f}s]")
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Błąd: {e}")
        
        print()
    
    print("=" * 60)
    print(f"✅ Zakończono! Przeanalizowano {len(unique_to_analyze)} artykułów")
    
    # Final stats
    final_analyses = list(analysis_dir.glob("analysis_*.json"))
    print(f"📊 Łącznie analiz: {len(final_analyses)}")

if __name__ == "__main__":
    main()
