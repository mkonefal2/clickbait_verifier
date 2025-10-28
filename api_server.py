"""
Simple FastAPI server for Android app
Serves analyzed articles from reports/analysis/ folder
"""
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json
import os
from typing import List, Dict, Any
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

app = FastAPI(title="Clickbait Verifier API")

# Enable CORS for Android emulator
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def fetch_image_from_url(url: str) -> str | None:
    """Try to retrieve image URL from page meta tags (og:image, twitter:image)"""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible)"}
        resp = requests.get(url, headers=headers, timeout=6)
        if resp.status_code != 200:
            return None
        soup = BeautifulSoup(resp.text, "lxml")
        # Try common meta tags
        meta_props = ["og:image", "twitter:image", "image", "og:image:url"]
        for prop in meta_props:
            m = soup.find("meta", property=prop) or soup.find("meta", attrs={"name": prop})
            if m:
                val = m.get("content") or m.get("value")
                if val:
                    return urljoin(resp.url, val)
        return None
    except Exception as e:
        print(f"Error fetching image from {url}: {e}")
        return None

def load_analysis_files(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """Load analysis JSON files from reports/analysis/ directory"""
    analysis_dir = Path("reports/analysis")
    
    if not analysis_dir.exists():
        return []
    
    articles = []
    
    # Get all JSON files sorted by modification time (newest first)
    # Filter out duplicates (files with _1, _2, etc. suffix)
    all_files = analysis_dir.glob("analysis_*.json")
    filtered_files = [f for f in all_files if not any(f.stem.endswith(f"_{i}") for i in range(1, 100))]
    json_files = sorted(
        filtered_files,
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )

    # apply offset and limit (limit==0 => return all starting from offset)
    if limit and limit > 0:
        json_files = json_files[offset: offset + limit]
    else:
        json_files = json_files[offset:]
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Extract relevant fields - use 'score' field from JSON
                score = float(data.get("score", data.get("clickbait_score", 0)))
                suggestions = data.get("suggestions", {})
                article_id = json_file.stem.replace("analysis_", "")
                article_url = data.get("url", "")
                
                # Try to load image from scraped file
                image_url = None
                # First try by ID
                scraped_file = Path(f"reports/scraped/scraped_{article_id}.json")
                if not scraped_file.exists() and article_url:
                    # If not found by ID, search by URL
                    scraped_dir = Path("reports/scraped")
                    for scraped_path in scraped_dir.glob("scraped_*.json"):
                        try:
                            with open(scraped_path, 'r', encoding='utf-8') as sf:
                                scraped_data = json.load(sf)
                                if scraped_data.get('url') == article_url:
                                    scraped_file = scraped_path
                                    break
                        except Exception:
                            continue
                
                if scraped_file.exists():
                    try:
                        with open(scraped_file, 'r', encoding='utf-8') as sf:
                            scraped_data = json.load(sf)
                            # Check for image_url field first (new format)
                            image_url = scraped_data.get('image_url') or scraped_data.get('lead_image_url') or scraped_data.get('image')
                            # Fallback to meta tags
                            if not image_url:
                                meta = scraped_data.get('meta', {})
                                if isinstance(meta, dict):
                                    image_url = meta.get('og:image') or meta.get('twitter:image')
                    except Exception:
                        pass
                
                # Fallback to placeholder (don't fetch from URL - too slow!)
                if not image_url:
                    source_name = data.get("source", "nieznane").lower()
                    image_url = f"https://via.placeholder.com/400x250/5E35B1/FFFFFF?text={source_name.upper()}"
                
                article = {
                    "id": article_id,
                    "title": data.get("title", "Brak tytułu"),
                    "url": data.get("url", ""),
                    "source": data.get("source", "nieznane"),
                    "imageUrl": image_url,
                    "publishedAt": data.get("published", data.get("date", "")),
                    "content": data.get("content", "")[:500] + "...",  # First 500 chars
                    "analysis": {
                        "clickbaitScore": score,
                        "hasClickbait": score > 50,
                        "emotionalTone": data.get("emotional_tone", "neutral"),
                        "sensationalism": data.get("sensationalism_level", data.get("label", "low")),
                        "summary": data.get("summary", data.get("content", "")[:200] + "..."),  # Short article summary
                        "reasoning": "\n".join(data.get("rationale_user_friendly", data.get("rationale", ["Brak uzasadnienia"]))),
                        "manipulationTechniques": data.get("manipulation_techniques", data.get("signals", {}).get("title_hits", [])),
                        "factualBasis": data.get("factual_basis", "nieznana"),
                        "suggestedTitle": suggestions.get("rewrite_title_neutral", None)
                    }
                }
                articles.append(article)
        except Exception as e:
            print(f"Error loading {json_file}: {e}")
            continue
    
    return articles

@app.get("/")
def read_root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "Clickbait Verifier API is running",
        "endpoints": [
            "/api/articles",
            "/api/articles/{article_id}"
        ]
    }

@app.get("/api/articles")
def get_articles(limit: int = Query(default=50, ge=0, le=200), offset: int = Query(default=0, ge=0)):
    """
    Get list of analyzed articles
    
    Parameters:
    - limit: Maximum number of articles to return (1-200)
    """
    articles = load_analysis_files(limit=limit, offset=offset)
    
    return {
        "articles": articles,
        "total": len(articles),
        "limit": limit
    }

@app.get("/api/articles/{article_id}")
def get_article(article_id: str):
    """Get single article by ID"""
    analysis_file = Path(f"reports/analysis/analysis_{article_id}.json")
    
    if not analysis_file.exists():
        return {"error": "Article not found"}, 404
    
    try:
        with open(analysis_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        score = float(data.get("score", data.get("clickbait_score", 0)))
        suggestions = data.get("suggestions", {})
        
        # Generate placeholder image based on source
        source_name = data.get("source", "nieznane").lower()
        placeholder_url = f"https://via.placeholder.com/400x250/5E35B1/FFFFFF?text={source_name.upper()}"
            
        return {
            "id": article_id,
            "title": data.get("title", "Brak tytułu"),
            "url": data.get("url", ""),
            "source": data.get("source", "nieznane"),
            "imageUrl": data.get("image_url", placeholder_url),
            "publishedAt": data.get("published", data.get("date", "")),
            "content": data.get("content", ""),
            "analysis": {
                "clickbaitScore": score,
                "hasClickbait": score > 50,
                "emotionalTone": data.get("emotional_tone", "neutral"),
                "sensationalism": data.get("sensationalism_level", data.get("label", "low")),
                "summary": data.get("summary", "\n".join(data.get("rationale_user_friendly", ["Brak podsumowania"]))),
                "reasoning": "\n".join(data.get("rationale", data.get("reasoning", ["Brak uzasadnienia"]))),
                "manipulationTechniques": data.get("manipulation_techniques", data.get("signals", {}).get("title_hits", [])),
                "factualBasis": data.get("factual_basis", "nieznana"),
                "suggestedTitle": suggestions.get("rewrite_title_neutral", None),
                # editorNotes intentionally omitted from list response
            }
        }
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Clickbait Verifier API server...")
    print("📱 Android app should connect to: http://10.0.2.2:8000")
    print("🌐 Web browser: http://localhost:8000")
    print("📖 API docs: http://localhost:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
