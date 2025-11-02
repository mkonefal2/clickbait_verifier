#!/usr/bin/env python3
"""
Demo script showing GPT integration without requiring actual API key.
Creates mock analysis results to demonstrate the new system.
"""

import json
import time
from pathlib import Path


def create_mock_analysis(article_data):
    """Create a mock analysis result for demonstration."""
    title = article_data.get('title', '')
    
    # Simple clickbait detection based on keywords
    clickbait_keywords = ['szok', 'niewiarygodny', 'nie uwierzysz', 'sekret', 'bomba', 'dramat']
    sensational_count = sum(1 for word in clickbait_keywords if word.lower() in title.lower())
    
    # Mock scoring
    base_score = sensational_count * 15
    if len(title) > 100:
        base_score += 10
    if '!' in title:
        base_score += 5
    if title.isupper():
        base_score += 20
        
    score = min(base_score, 100)
    
    # Determine label
    if score < 25:
        label = "not_clickbait"
    elif score < 50:
        label = "mild"
    elif score < 75:
        label = "strong"
    else:
        label = "extreme"
    
    # Create mock analysis result
    result = {
        "id": article_data.get('id'),
        "source": article_data.get('source'),
        "url": article_data.get('url'),
        "title": title,
        "score": score,
        "label": label,
        "rationale": [
            f"Wykryto {sensational_count} fraz sensacyjnych w tytule",
            f"Długość tytułu: {len(title)} znaków" + (" (ponad 100 - dodatkowe punkty)" if len(title) > 100 else ""),
            f"Obecność wykrzykników: {'tak' if '!' in title else 'nie'}",
            f"Końcowy wynik: {score} punktów → kategoria '{label}'"
        ],
        "rationale_user_friendly": [
            f"Tytuł {'zawiera' if sensational_count > 0 else 'nie zawiera'} słowa pobudzające emocje",
            f"Długość tytułu {'może' if len(title) > 100 else 'nie'} sugerować clickbait",
            f"Ogólna ocena: {'wysoki' if score >= 50 else 'niski' if score < 25 else 'średni'} poziom clickbaitu"
        ],
        "summary": f"Artykuł z portalu {article_data.get('source', 'unknown')} opisuje wydarzenia związane z tematyką poruszaną w tytule. Treść zawiera {len(article_data.get('content', ''))} znaków tekstu.",
        "signals": {
            "title_hits": [word for word in clickbait_keywords if word.lower() in title.lower()],
            "content_hits": [],
            "credibility_hits": [],
            "mismatch": {
                "detected": False,
                "severity": "none"
            }
        },
        "suggestions": {
            "rewrite_title_neutral": title.replace("szok", "wydarzenie").replace("niewiarygodny", "niezwykły"),
            "notes_to_editor": f"Rozważyć zmniejszenie sensacyjności tytułu (obecny wynik: {score}/100)"
        },
        "diagnostics": {
            "tokens_title": len(title.split()),
            "tokens_content": len(article_data.get('content', '').split()),
            "processing_time_ms": 1200,
            "model": "mock-analyzer-v1.0",
            "mock_analysis": True
        }
    }
    
    return result


def main():
    """Demo GPT analysis integration."""
    print("🚀 Clickbait Verifier - Demo analizy GPT")
    print("="*50)
    
    # Find scraped articles
    base_dir = Path(__file__).parent
    scraped_dir = base_dir / "reports" / "scraped"
    analysis_dir = base_dir / "reports" / "analysis"
    
    if not scraped_dir.exists():
        print("❌ Katalog scraped nie istnieje!")
        return
    
    # Create analysis directory if needed
    analysis_dir.mkdir(exist_ok=True)
    
    # Find existing analyses
    existing_analyses = set()
    if analysis_dir.exists():
        for analysis_file in analysis_dir.glob("analysis_*.json"):
            try:
                with open(analysis_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'id' in data:
                        existing_analyses.add(str(data['id']))
            except Exception:
                continue
    
    # Process a few articles for demo
    scraped_files = sorted(scraped_dir.glob("scraped_*.json"))[:5]  # Just first 5
    
    print(f"📊 Znaleziono {len(scraped_files)} artykułów do zademonstrowania")
    print(f"🔍 Już przeanalizowano: {len(existing_analyses)} artykułów")
    print()
    
    analyzed_count = 0
    
    for scraped_file in scraped_files:
        try:
            # Load article
            with open(scraped_file, 'r', encoding='utf-8') as f:
                article = json.load(f)
            
            aid = str(article.get('id', ''))
            if aid in existing_analyses:
                print(f"⏭️  Pominięto (już przeanalizowano): {scraped_file.name}")
                continue
            
            # Mock analysis
            print(f"🔄 Analizuję: {article.get('title', 'Brak tytułu')[:60]}...")
            
            # Simulate processing time
            time.sleep(0.5)
            
            result = create_mock_analysis(article)
            
            # Save result
            analysis_path = analysis_dir / f"analysis_{aid}.json"
            with open(analysis_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Zapisano do: {analysis_path.name}")
            print(f"   📈 Wynik: {result['score']}/100 ({result['label']})")
            print(f"   💡 {result['rationale_user_friendly'][0]}")
            print()
            
            analyzed_count += 1
            
        except Exception as e:
            print(f"❌ Błąd przetwarzania {scraped_file}: {e}")
    
    print("="*50)
    print(f"🎉 Demo zakończone! Przeanalizowano {analyzed_count} artykułów")
    print()
    print("📋 Następne kroki z prawdziwym GPT API:")
    print("   1. Ustaw OPENAI_API_KEY")
    print("   2. python -m clickbait_verifier.main --analyze-all")
    print("   3. Sprawdź wyniki w aplikacji Streamlit")
    print()
    print("🌐 Uruchom aplikację Streamlit:")
    print("   streamlit run run_app.py")


if __name__ == "__main__":
    main()