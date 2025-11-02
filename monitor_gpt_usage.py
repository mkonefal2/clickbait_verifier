a#!/usr/bin/env python3
"""
Monitor GPT API usage in real-time
"""
from clickbait_verifier.analyzer import GPTAnalyzer
import json
import time
from pathlib import Path

def monitor_gpt_usage():
    """Run multiple analyses to see usage patterns."""
    
    print("📊 GPT API Usage Monitor")
    print("=" * 40)
    
    analyzer = GPTAnalyzer()
    scraped_dir = Path('reports/scraped')
    
    # Sample article for testing
    sample_article = {
        "id": "test_001",
        "title": "SZOKUJĄCE odkrycie naukowców! To zmieni wszystko co wiemy o...",
        "content": "Naukowcy z uniwersytetu przeprowadzili badanie, które może zmienić nasze rozumienie. Wyniki badania są bardzo interesujące i mogą mieć wpływ na przyszłe badania w tej dziedzinie.",
        "source": "test",
        "url": "https://example.com/test"
    }
    
    print(f"🧪 Testowanie na przykładowym artykule:")
    print(f"📰 Tytuł: {sample_article['title']}")
    
    for i in range(3):
        print(f"\n🔄 Test {i+1}/3:")
        
        start_time = time.time()
        result = analyzer.analyze_article(sample_article)
        end_time = time.time()
        
        if result:
            print(f"   ✅ Sukces! Wynik: {result['score']}/100 ({result['label']})")
            print(f"   ⏱️  Czas: {end_time - start_time:.1f}s")
            print(f"   🧠 Model: {result.get('diagnostics', {}).get('model', 'unknown')}")
            
            # Estimate tokens
            title_tokens = len(sample_article['title'].split())
            content_tokens = len(sample_article['content'].split())
            response_tokens = len(str(result).split())
            total_tokens = title_tokens + content_tokens + response_tokens
            
            print(f"   📊 Szacowane tokeny: ~{total_tokens}")
            print(f"   💰 Szacowany koszt: ~${total_tokens * 0.00000015:.6f}")
        else:
            print(f"   ❌ Błąd analizy")
        
        if i < 2:
            print(f"   ⏳ Czekam 2 sekundy...")
            time.sleep(2)
    
    print(f"\n" + "=" * 40)
    print(f"🎯 Wykonano 3 testy GPT API")
    print(f"💡 Sprawdź dashboard OpenAI za 5-10 minut:")
    print(f"   https://platform.openai.com/usage")

if __name__ == "__main__":
    monitor_gpt_usage()