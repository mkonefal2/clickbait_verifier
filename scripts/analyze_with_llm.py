#!/usr/bin/env python3
"""
Analyze scraped articles using OpenAI GPT model (e.g., gpt-4o-mini) according to
clickbait_agent_spec_v1.1.yaml specification.

Usage:
    python scripts/analyze_with_llm.py [--model gpt-4o-mini] [--limit 10] [--source rmf24]

Options:
    --model         OpenAI model name (default: gpt-4o-mini)
    --limit         Max number of articles to analyze (default: all unanalyzed)
    --source        Filter by source name (case-insensitive)
    --api-key       OpenAI API key (or set OPENAI_API_KEY env var)
    --dry-run       List articles that would be analyzed without actually calling API
    --overwrite     Re-analyze even if analysis file exists

Requirements:
    pip install openai pyyaml

Example:
    # Analyze first 10 unanalyzed rmf24 articles
    python scripts/analyze_with_llm.py --limit 10 --source rmf24

    # Dry run to see what would be analyzed
    python scripts/analyze_with_llm.py --dry-run

    # Use specific API key
    python scripts/analyze_with_llm.py --api-key sk-...
"""
import os
import sys
import json
import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Optional
import time

try:
    from openai import OpenAI
except ImportError:
    print("ERROR: openai library not installed. Run: pip install openai pyyaml")
    sys.exit(1)


BASE_DIR = Path(__file__).resolve().parents[1]
SCRAPED_DIR = BASE_DIR / "reports" / "scraped"
ANALYSIS_DIR = BASE_DIR / "reports" / "analysis"
SPEC_PATH = BASE_DIR / "clickbait_agent_spec_v1.1.yaml"
OUTPUT_TEMPLATE_PATH = BASE_DIR / "schemas" / "output_template.json"


def parse_args():
    p = argparse.ArgumentParser(description='Analyze scraped articles with OpenAI LLM')
    p.add_argument('--model', default='gpt-4o-mini', help='OpenAI model name')
    p.add_argument('--limit', type=int, default=None, help='Max articles to analyze')
    p.add_argument('--source', default=None, help='Filter by source (case-insensitive)')
    p.add_argument('--api-key', default=None, help='OpenAI API key (or use OPENAI_API_KEY env)')
    p.add_argument('--dry-run', action='store_true', help='List articles without analyzing')
    p.add_argument('--overwrite', action='store_true', help='Re-analyze existing analyses')
    return p.parse_args()


def load_json(path: Path) -> Optional[dict]:
    try:
        with path.open('r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️  Failed to load {path.name}: {e}")
        return None


def load_spec() -> dict:
    """Load the YAML spec."""
    if not SPEC_PATH.exists():
        print(f"❌ Spec file not found: {SPEC_PATH}")
        sys.exit(1)
    with SPEC_PATH.open('r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_output_template() -> dict:
    """Load output template if available."""
    if OUTPUT_TEMPLATE_PATH.exists():
        return load_json(OUTPUT_TEMPLATE_PATH) or {}
    return {}


def find_analysis_map(analysis_dir: Path) -> Dict[str, Path]:
    """Return map of article id -> analysis file path."""
    m = {}
    if not analysis_dir.exists():
        return m
    for p in analysis_dir.glob('analysis_*.json'):
        name = p.stem
        rest = name[len('analysis_'):]
        idpart = rest.split('_')[0]
        if idpart not in m:
            m[idpart] = p
    return m


def build_system_prompt(spec: dict) -> str:
    """Build system prompt from spec."""
    meta = spec.get('meta', {})
    features = spec.get('features', {})
    scoring = spec.get('scoring', {})
    
    prompt = f"""Jesteś ekspertem od analizy clickbaitu dla polskich artykułów wg specyfikacji {meta.get('name', 'clickbait_assessment_spec')} v{meta.get('version', '1.2.3')}.

Twoim zadaniem jest ocena stopnia clickbaitu w artykule na podstawie:
1. Analizy tytułu (title) i treści (content)
2. Wykrywania fraz sensacyjnych, absolutów, luk ciekawości wg wzorców regex
3. Oceny zgodności tytułu z treścią (mismatch detection)
4. Wykrywania sygnałów wiarygodności (cytaty, liczby, źródła)
5. Generowania obiektywnego streszczenia artykułu (summary)

WAŻNE: Zawsze generuj dwa uzasadnienia:
- 'rationale': techniczne, dla audytu (jak działał algorytm)
- 'rationale_user_friendly': przystępne dla czytelnika (bez żargonu)

OBOWIĄZKOWE pole 'summary':
- 2–4 zdania opisujące TREŚĆ artykułu (nie clickbaitowość!)
- Maksymalnie 400 znaków
- Neutralny ton, obiektywne fakty
- Bez ocen typu "tytuł jest sensacyjny" — tylko co artykuł opisuje

Scoring:
- not_clickbait: 0-24 pkt
- mild: 25-49 pkt  
- strong: 50-74 pkt
- extreme: 75+ pkt

Wagi: title={scoring.get('weights', {}).get('title_clickbait_weight', 0.4)}, content={scoring.get('weights', {}).get('content_clickbait_weight', 0.15)}, mismatch={scoring.get('weights', {}).get('mismatch_weight', 0.4)}

Zwróć odpowiedź w formacie JSON zgodnym z szablonem output_template.json.
"""
    return prompt


def build_user_prompt(article: dict, spec: dict) -> str:
    """Build user prompt with article data."""
    title = article.get('title', '')
    content = article.get('content', '')
    url = article.get('url', '')
    source = article.get('source', '')
    
    # Truncate content if too long (GPT context limits)
    max_content = 8000
    if len(content) > max_content:
        content = content[:max_content] + "\n[... treść przycięta ...]"
    
    prompt = f"""Przeanalizuj poniższy artykuł wg specyfikacji clickbait.

ARTYKUŁ:
Źródło: {source}
URL: {url}
Tytuł: {title}

Treść:
{content}

Zwróć JSON z polami:
- id: {article.get('id')}
- source: "{source}"
- url: "{url}"
- title: "{title}"
- score: (liczba 0-100)
- label: ("not_clickbait" | "mild" | "strong" | "extreme")
- rationale: [lista zdań - techniczne uzasadnienie]
- rationale_user_friendly: [lista zdań - przystępne wyjaśnienie]
- summary: "2-4 zdania opisujące TREŚĆ artykułu (max 400 znaków)"
- signals: {{title_hits: [...], content_hits: [...], credibility_hits: [...], mismatch: {{...}}}}
- suggestions: {{rewrite_title_neutral: "...", notes_to_editor: "..."}}
- diagnostics: {{tokens_title: N, tokens_content: N, processing_time_ms: N}}

PAMIĘTAJ: 'summary' to streszczenie TREŚCI (co artykuł opisuje), nie ocena clickbaitu!
"""
    return prompt


def analyze_with_llm(client: OpenAI, model: str, article: dict, spec: dict) -> Optional[dict]:
    """Call OpenAI API to analyze article."""
    system_prompt = build_system_prompt(spec)
    user_prompt = build_user_prompt(article, spec)
    
    try:
        start_time = time.time()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        result = json.loads(response.choices[0].message.content)
        
        # Ensure diagnostics includes processing time
        if 'diagnostics' not in result:
            result['diagnostics'] = {}
        result['diagnostics']['processing_time_ms'] = elapsed_ms
        result['diagnostics']['model'] = model
        
        return result
        
    except Exception as e:
        print(f"❌ API call failed: {e}")
        return None


def safe_write_analysis(aid: str, data: dict) -> Path:
    """Write analysis JSON; add suffix if file exists."""
    path = ANALYSIS_DIR / f"analysis_{aid}.json"
    if not path.exists():
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        return path
    
    i = 1
    while True:
        candidate = ANALYSIS_DIR / f"analysis_{aid}_{i}.json"
        if not candidate.exists():
            candidate.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
            return candidate
        i += 1


def main():
    args = parse_args()
    
    # Setup API key
    api_key = args.api_key or os.getenv('OPENAI_API_KEY')
    if not api_key and not args.dry_run:
        print("❌ OpenAI API key required. Set OPENAI_API_KEY env var or use --api-key")
        sys.exit(1)
    
    # Load spec and find unanalyzed articles
    spec = load_spec()
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    
    if not SCRAPED_DIR.exists():
        print(f"❌ Scraped directory not found: {SCRAPED_DIR}")
        sys.exit(1)
    
    analysis_map = find_analysis_map(ANALYSIS_DIR)
    scraped_files = sorted(SCRAPED_DIR.glob('scraped_*.json'))
    
    to_analyze = []
    for p in scraped_files:
        data = load_json(p)
        if not data:
            continue
        
        # Filter by source
        if args.source:
            src = (data.get('source') or '').lower()
            if src != args.source.lower():
                continue
        
        aid = str(data.get('id')) if data.get('id') else None
        if not aid:
            continue
        
        # Skip if already analyzed (unless --overwrite)
        if aid in analysis_map and not args.overwrite:
            continue
        
        to_analyze.append((p, data, aid))
    
    # Apply limit
    if args.limit:
        to_analyze = to_analyze[:args.limit]
    
    print(f"\n📊 Found {len(to_analyze)} articles to analyze")
    if args.source:
        print(f"   (filtered by source: {args.source})")
    
    if args.dry_run:
        print("\n🔍 DRY RUN - would analyze:")
        for p, data, aid in to_analyze:
            print(f"   • {p.name} (id={aid}, source={data.get('source')})")
            print(f"     Title: {data.get('title', '')[:80]}...")
        return 0
    
    if not to_analyze:
        print("✅ All articles already analyzed!")
        return 0
    
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    # Analyze articles
    success = 0
    failed = 0
    
    for idx, (p, data, aid) in enumerate(to_analyze, 1):
        print(f"\n[{idx}/{len(to_analyze)}] Analyzing {p.name}...")
        print(f"  Title: {data.get('title', '')[:80]}...")
        
        result = analyze_with_llm(client, args.model, data, spec)
        
        if result:
            output_path = safe_write_analysis(aid, result)
            print(f"  ✅ Saved to {output_path.name}")
            print(f"     Score: {result.get('score')}, Label: {result.get('label')}")
            success += 1
        else:
            print(f"  ❌ Analysis failed")
            failed += 1
        
        # Rate limiting (OpenAI has limits)
        if idx < len(to_analyze):
            time.sleep(1)
    
    print(f"\n{'='*60}")
    print(f"✅ Successfully analyzed: {success}")
    if failed > 0:
        print(f"❌ Failed: {failed}")
    print(f"{'='*60}\n")
    
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
