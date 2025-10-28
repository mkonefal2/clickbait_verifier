"""
Quick script to add image_url to existing scraped files by fetching and parsing HTML again.
"""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from clickbait_verifier.scraper import (
    fetch_html_with_method,
    extract_content_and_title,
    load_extractor_for_source
)

def update_scraped_files(limit=50):
    """Add image_url to scraped files that don't have it."""
    scraped_dir = Path("reports/scraped")
    
    if not scraped_dir.exists():
        print("No scraped directory found!")
        return
    
    # Get scraped files sorted by modification time (newest first)
    files = sorted(
        scraped_dir.glob("scraped_*.json"),
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )[:limit]
    
    updated_count = 0
    skipped_count = 0
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Skip if already has image_url
            if data.get('image_url'):
                skipped_count += 1
                continue
            
            url = data.get('url')
            source = data.get('source', 'unknown')
            
            if not url:
                print(f"Skipping {file_path.name}: no URL")
                continue
            
            print(f"Fetching image_url for: {url}")
            
            # Fetch HTML and extract image
            html = fetch_html_with_method(url, 'auto')
            extractor = load_extractor_for_source(source)
            content, title, published, image_url = extract_content_and_title(html, extractor)
            
            if image_url:
                # Update file with image_url
                data['image_url'] = image_url
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"[OK] Updated {file_path.name}: {image_url[:60]}")
                updated_count += 1
            else:
                print(f"[SKIP] No image found for {file_path.name}")
        
        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")
            continue
    
    print(f"\n[DONE] Updated {updated_count} files, skipped {skipped_count} (already had image_url)")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=50, help='Number of most recent files to process')
    args = parser.parse_args()
    
    update_scraped_files(limit=args.limit)
