import sys
import argparse
import json
import os
from pathlib import Path
from .scraper import run_scraper, fetch_and_save_url
from .analyzer import GPTAnalyzer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def analyze_scraped_file(file_path: str, analyzer: GPTAnalyzer) -> bool:
    """Analyze a single scraped file and save result."""
    try:
        # Load scraped data
        with open(file_path, 'r', encoding='utf-8') as f:
            article = json.load(f)
        
        logger.info(f"Analyzing: {article.get('title', 'Unknown title')[:60]}...")
        
        # Analyze with GPT
        result = analyzer.analyze_article(article)
        
        if result:
            # Save analysis
            base_dir = Path(file_path).parent.parent
            analysis_dir = base_dir / "analysis"
            analysis_dir.mkdir(exist_ok=True)
            
            aid = article.get('id')
            analysis_path = analysis_dir / f"analysis_{aid}.json"
            
            # Handle existing files
            counter = 1
            while analysis_path.exists():
                analysis_path = analysis_dir / f"analysis_{aid}_{counter}.json"
                counter += 1
            
            with open(analysis_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Analysis saved to: {analysis_path}")
            logger.info(f"   Score: {result.get('score')}, Label: {result.get('label')}")
            return True
        else:
            logger.error("❌ Analysis failed")
            return False
            
    except Exception as e:
        logger.error(f"Error analyzing {file_path}: {e}")
        return False


def run_with_analysis(scrape_args=None, analyze_all=False, auto_analyze=False, api_key=None, model="gpt-4o-mini"):
    """
    Run scraper with optional automatic analysis.
    
    Args:
        scrape_args: Arguments for scraping (url, source, method)
        analyze_all: If True, analyze all unanalyzed scraped files
        auto_analyze: If True, automatically analyze newly scraped content
        api_key: OpenAI API key
        model: OpenAI model to use
    """
    
    # Initialize analyzer if needed
    analyzer = None
    if analyze_all or auto_analyze:
        try:
            analyzer = GPTAnalyzer(api_key=api_key, model=model)
            logger.info(f"✅ GPT Analyzer initialized with model: {model}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize GPT analyzer: {e}")
            return False
    
    # Run scraper
    scrape_result = None
    if scrape_args:
        url, source, method = scrape_args
        scrape_result = fetch_and_save_url(url, source_name=source, fetch_method=method)
    else:
        run_scraper()
    
    # Auto-analyze newly scraped content
    if auto_analyze and analyzer and scrape_result and not scrape_result.get('existed'):
        file_path = scrape_result.get('path')
        if file_path and os.path.exists(file_path):
            logger.info("🔄 Auto-analyzing newly scraped content...")
            analyze_scraped_file(file_path, analyzer)
    
    # Analyze all unanalyzed content
    if analyze_all and analyzer:
        logger.info("🔄 Analyzing all unanalyzed content...")
        
        # Find scraped files
        base_dir = Path(__file__).parent.parent
        scraped_dir = base_dir / "reports" / "scraped"
        analysis_dir = base_dir / "reports" / "analysis"
        
        if not scraped_dir.exists():
            logger.warning(f"Scraped directory not found: {scraped_dir}")
            return True
        
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
        
        # Process unanalyzed files
        scraped_files = list(scraped_dir.glob("scraped_*.json"))
        analyzed_count = 0
        
        for scraped_file in scraped_files:
            try:
                with open(scraped_file, 'r', encoding='utf-8') as f:
                    article = json.load(f)
                
                aid = str(article.get('id', ''))
                if aid and aid not in existing_analyses:
                    if analyze_scraped_file(str(scraped_file), analyzer):
                        analyzed_count += 1
                        existing_analyses.add(aid)  # Avoid re-analyzing
                        
                        # Rate limiting
                        import time
                        time.sleep(1)
                        
            except Exception as e:
                logger.error(f"Error processing {scraped_file}: {e}")
        
        logger.info(f"✅ Analyzed {analyzed_count} new articles")
    
    return True


def main():
    """Main entry point with command line interface."""
    parser = argparse.ArgumentParser(
        description="Clickbait Verifier - scraping and analysis tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape all sources from config.yaml
  python -m clickbait_verifier.main
  
  # Scrape single URL
  python -m clickbait_verifier.main --url "https://example.com/article" --source "Example"
  
  # Scrape single URL with auto-analysis
  python -m clickbait_verifier.main --url "https://example.com/article" --analyze
  
  # Analyze all unanalyzed scraped content
  python -m clickbait_verifier.main --analyze-all
  
  # Analyze with custom model
  python -m clickbait_verifier.main --analyze-all --model gpt-4
        """
    )
    
    # Scraping options
    parser.add_argument('--url', help='URL to scrape (single article mode)')
    parser.add_argument('--source', default='CLI', help='Source name (default: CLI)')
    parser.add_argument('--method', default='auto', choices=['auto', 'requests', 'playwright'], 
                       help='Fetch method (default: auto)')
    
    # Analysis options
    parser.add_argument('--analyze', action='store_true', 
                       help='Auto-analyze newly scraped content')
    parser.add_argument('--analyze-all', action='store_true',
                       help='Analyze all unanalyzed scraped content')
    parser.add_argument('--api-key', help='OpenAI API key (or set OPENAI_API_KEY env var)')
    parser.add_argument('--model', default='gpt-4o-mini', help='OpenAI model (default: gpt-4o-mini)')
    
    # Legacy support for positional arguments
    parser.add_argument('legacy_args', nargs='*', help='Legacy: [url] [source] [method]')
    
    args = parser.parse_args()
    
    # Handle legacy positional arguments
    if args.legacy_args:
        if len(args.legacy_args) >= 1:
            args.url = args.legacy_args[0]
        if len(args.legacy_args) >= 2:
            args.source = args.legacy_args[1]
        if len(args.legacy_args) >= 3:
            args.method = args.legacy_args[2]
    
    # Determine scraping arguments
    scrape_args = None
    if args.url:
        scrape_args = (args.url, args.source, args.method)
    
    # Run with analysis options
    success = run_with_analysis(
        scrape_args=scrape_args,
        analyze_all=args.analyze_all,
        auto_analyze=args.analyze,
        api_key=args.api_key,
        model=args.model
    )
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
