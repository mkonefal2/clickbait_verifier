#!/usr/bin/env python3
"""
Test GPT analysis on a single article
"""
import json
from pathlib import Path
from clickbait_verifier.analyzer import GPTAnalyzer

def test_single_article():
    """Test GPT analysis on one unanalyzed article."""
    
    print("🧪 Testing GPT Analysis on Single Article")
    print("=" * 50)
    
    # Find directories
    scraped_dir = Path('reports/scraped')
    analysis_dir = Path('reports/analysis')
    
    if not scraped_dir.exists():
        print("❌ No scraped directory found!")
        return
    
    # Get existing analysis IDs
    existing_analyses = set()
    if analysis_dir.exists():
        for analysis_file in analysis_dir.glob('analysis_*.json'):
            try:
                with open(analysis_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'id' in data:
                        existing_analyses.add(str(data['id']))
            except Exception:
                continue
    
    print(f"📊 Found {len(existing_analyses)} existing analyses")
    
    # Find first unanalyzed article
    test_article = None
    test_file = None
    
    for scraped_file in scraped_dir.glob('scraped_*.json'):
        try:
            with open(scraped_file, 'r', encoding='utf-8') as f:
                article = json.load(f)
            
            aid = str(article.get('id', ''))
            if aid and aid not in existing_analyses:
                test_article = article
                test_file = scraped_file
                break
                
        except Exception as e:
            print(f"❌ Error loading {scraped_file}: {e}")
            continue
    
    if not test_article:
        print("📋 All articles already analyzed! Using first available article...")
        # Take first article for demo
        try:
            first_file = next(scraped_dir.glob('scraped_*.json'))
            with open(first_file, 'r', encoding='utf-8') as f:
                test_article = json.load(f)
            test_file = first_file
        except Exception as e:
            print(f"❌ No articles available: {e}")
            return
    
    print(f"\n🎯 Testing on: {test_file.name}")
    print(f"📰 Title: {test_article.get('title', 'No title')[:80]}...")
    print(f"🔗 Source: {test_article.get('source', 'Unknown')}")
    print(f"📏 Content length: {len(test_article.get('content', ''))} chars")
    
    # Create GPT analyzer
    try:
        print(f"\n🤖 Creating GPT Analyzer...")
        analyzer = GPTAnalyzer()
        print("✅ Analyzer created successfully!")
        
        print(f"\n📊 Analyzing with GPT...")
        result = analyzer.analyze_article(test_article)
        
        if result:
            print("\n🎉 ANALYSIS SUCCESSFUL!")
            print(f"📈 Score: {result['score']}/100")
            print(f"🏷️  Label: {result['label']}")
            print(f"📝 Summary: {result.get('summary', 'No summary')}")
            print(f"⏱️  Processing time: {result.get('diagnostics', {}).get('processing_time_ms', 0)}ms")
            print(f"🧠 Model: {result.get('diagnostics', {}).get('model', 'unknown')}")
            
            print(f"\n💡 User-friendly explanation:")
            for reason in result.get('rationale_user_friendly', [])[:2]:
                print(f"   • {reason}")
            
            # Save result for demo
            if analysis_dir:
                analysis_dir.mkdir(exist_ok=True)
                aid = test_article.get('id')
                analysis_path = analysis_dir / f"analysis_{aid}_test.json"
                
                with open(analysis_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                
                print(f"\n💾 Result saved to: {analysis_path}")
            
        else:
            print("\n❌ ANALYSIS FAILED!")
            
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_single_article()