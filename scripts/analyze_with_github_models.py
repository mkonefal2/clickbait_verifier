"""
Batch analyzer using GitHub Models API (gpt-4o-mini) to analyze scraped articles
according to clickbait_agent_spec_v1.1.yaml rules.

Uses GitHub Personal Access Token (not OpenAI API key).
Free tier limits: ~15 req/min, ~150k tokens/day per model.

Usage:
1. Set GITHUB_TOKEN environment variable:
   $env:GITHUB_TOKEN = "ghp_your_token_here"

2. Run:
   & .\.venv\Scripts\python.exe scripts\analyze_with_github_models.py

3. Optional flags:
   --limit N        Analyze only first N unanalyzed files
   --model MODEL    Use different model (default: gpt-4o-mini)
   --dry-run        Show what would be analyzed without making API calls
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from typing import List, Dict, Optional
import yaml

try:
    from openai import OpenAI
except ImportError:
    print("[ERROR] openai library not installed")
    print("Install with: pip install openai")
    sys.exit(1)

# Paths
BASE_DIR = Path(__file__).resolve().parents[1]
SCRAPED_DIR = BASE_DIR / "reports" / "scraped"
ANALYSIS_DIR = BASE_DIR / "reports" / "analysis"
SPEC_PATH = BASE_DIR / "clickbait_agent_spec_v1.1.yaml"

# Create analysis dir if needed
ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)


def load_spec() -> dict:
    """Load the YAML spec file."""
    if not SPEC_PATH.exists():
        print(f"[WARNING] Spec file not found: {SPEC_PATH}")
        return get_minimal_spec()
    
    try:
        with open(SPEC_PATH, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"[WARNING] Failed to load spec file: {e}")
        print("[INFO] Using minimal spec instead")
        return get_minimal_spec()


def get_minimal_spec() -> dict:
    """Return comprehensive spec with full instructions (used when YAML can't be loaded)."""
    return {
        'meta': {
            'version': '1.2.3',
            'name': 'clickbait_agent_spec'
        },
        'task': {
            'description': 'Analyze if article title is clickbait based on regex patterns, content analysis, and mismatch detection.'
        },
        'llm_prompts': {
            'judgment_prompt': '''Zastosuj ściśle zasady analizy clickbaitu zgodnie z poniższymi instrukcjami.

SCORING RULES (0-100):
- 0-24: not_clickbait (informative, neutral, no exaggeration)
- 25-49: mild (some sensational language, minor issues)
- 50-74: strong (clear clickbait patterns, curiosity gaps)
- 75-100: extreme (severe clickbait, deception)

DETECTION PATTERNS TO LOOK FOR:

1. TITLE ANALYSIS - Check for:
   - Superlatives: "najlepszy", "najgorszy", "największy" (+6 per hit, cap 18)
   - Absolutes: "zawsze", "nigdy", "wszyscy", "nikt", "na pewno", "100%" (+8 per hit, cap 24)
   - Sensational: "szok", "kuriozalny", "absurdalny", "niewiarygodny", "nie uwierzysz" (+12 per hit, cap 36)
   - Alarming: "zagrożenie", "niebezpieczeństwo", "katastrofa", "tragedia" (+10 per hit, cap 20)
   - Curiosity gap: "nie zgadniesz", "nie uwierzysz", "zobacz co się stało", "to musisz zobaczyć" (+6 per hit, cap 18)
   - Listicle: "X powodów", "N rzeczy", "TOP 10" (+6 per hit, cap 12)
   - Punctuation: multiple exclamation marks (+3 per, cap 9), questions (+4), ellipsis (+2 per, cap 6)

2. CONTENT ANALYSIS - Check for:
   - Overcertainty: same absolutes as title (+6 per hit, cap 18)
   - Sensational phrases in content (+8 per hit, cap 24)
   - Credibility REDUCTIONS:
     * Organization names/sources mentioned (-3 per, cap -12)
     * Numbers/dates/statistics (-2 per, cap -10)
     * Quoted speakers (-2 per, cap -8)
     * Scientific/method terms (-2 per, cap -8)
   - Hedging REDUCTIONS: "może", "prawdopodobnie", "wydaje się" (-2 per, cap -10)

3. MISMATCH DETECTION:
   - Calculate alignment_score (0.0-1.0): How well does content support title promises?
     * < 0.45: LOW alignment → penalty +18
     * 0.45-0.65: MEDIUM alignment → penalty +8
     * > 0.65: HIGH alignment → no penalty
   - Exaggeration gap: Title is sensational BUT content has credibility/hedging → penalty +14
   - Country mismatch: Title implies Poland but content is about France/Germany/etc → penalty +18
   - Time/date omission: Content has specific times/dates but title omits them → penalty +8-12

4. GEOGRAPHY CHECK:
   - If title mentions "w Polsce", "Polska", "u nas" or implies local event
   - BUT content clearly refers to different country (e.g., "We Francji", "w Niemczech")
   - → Set country_mismatch = true

5. SCORING CALCULATION:
   - Title additions (weighted 0.40): Sum all title pattern hits, apply caps
   - Content additions (weighted 0.15): Sum content patterns, apply caps
   - Mismatch penalties (weighted 0.40): Apply alignment + country + time penalties, cap at 30
   - Final score = weighted sum, round to nearest 5
   - Cap overall at 100

6. TWO RATIONALES REQUIRED:
   a) 'rationale': Technical explanation with regex mentions, feature names, scoring calculations
      Example: "title_superlative: regex hit 'najlepszy' (+6), content_credibility: org names detected (-3)"
   
   b) 'rationale_user_friendly': Plain language for readers, NO technical jargon
      Example in Polish: 
      - "Tytuł używa mocnego słowa 'najlepszy', które tworzy przesadne oczekiwania"
      - "Artykuł zawiera cytaty ekspertów i dane liczbowe, co zwiększa wiarygodność"
      - "Tytuł sugeruje wydarzenie w Polsce, ale treść dotyczy Francji"

7. SUMMARY GENERATION (CRITICAL):
   Generate 'summary' field with 2-4 sentences, max 400 chars describing ARTICLE CONTENT (not clickbait analysis).
   - Write what the article is ABOUT: main topic, key facts, message
   - Style: Objective, neutral, informative (like news summary)
   - DO NOT comment on title quality or clickbait assessment
   - Good example: "Naukowcy odkryli nowy gatunek żaby w Amazonii. Zwierzę ma niebieskie ubarwienie. Wyniki opublikowano w Nature."
   - Bad example: "Artykuł z sensacyjnym tytułem opisuje żabę" (this describes analysis, not content!)

8. OUTPUT FORMAT:
Return ONLY valid JSON with these fields:
{
  "score": <number 0-100>,
  "label": "not_clickbait" | "mild" | "strong" | "extreme",
  "rationale": [<technical explanations>],
  "rationale_user_friendly": [<plain language explanations in Polish>],
  "signals": {
    "title_hits": [<detected patterns in title>],
    "content_hits": [<detected patterns in content>],
    "credibility_hits": [<credibility signals>],
    "mismatch": {
      "alignment_score": <0.0-1.0>,
      "exaggeration_gap": <boolean>,
      "country_mismatch": <boolean>,
      "time_omission": <boolean>
    }
  },
  "suggestions": {
    "rewrite_title_neutral": "<neutral version of title>",
    "notes_to_editor": "<recommendations>"
  },
  "diagnostics": {
    "tokens_title": <number>,
    "tokens_content": <number>,
    "processing_time_ms": <number>
  },
  "summary": "<2-4 sentences about article content, max 400 chars>"
}

IMPORTANT: Be thorough in pattern detection. Look for ALL applicable patterns, calculate accurate alignment score, and provide detailed rationales.'''
        }
    }


def get_github_models_client(token: Optional[str] = None) -> OpenAI:
    """
    Create OpenAI client configured for GitHub Models API.
    
    Args:
        token: GitHub token (if None, reads from GITHUB_TOKEN env var)
    """
    if token is None:
        token = os.environ.get("GITHUB_TOKEN")
    
    if not token:
        raise ValueError(
            "GITHUB_TOKEN not found!\n"
            "Set it with: $env:GITHUB_TOKEN = 'ghp_your_token'\n"
            "Get token at: https://github.com/settings/tokens"
        )
    
    # GitHub Models endpoint
    return OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=token,
    )


def find_unanalyzed_files() -> List[Path]:
    """Find all scraped JSON files that don't have corresponding analysis files."""
    scraped_files = list(SCRAPED_DIR.glob("scraped_*.json"))
    unanalyzed = []
    
    for scraped_file in scraped_files:
        # Extract ID from filename: scraped_1234567890.json -> 1234567890
        try:
            file_id = scraped_file.stem.replace("scraped_", "")
            analysis_file = ANALYSIS_DIR / f"analysis_{file_id}.json"
            
            if not analysis_file.exists():
                unanalyzed.append(scraped_file)
        except Exception as e:
            print(f"[WARNING] Error processing {scraped_file.name}: {e}")
            continue
    
    return sorted(unanalyzed)


def build_analysis_prompt(spec: dict, scraped_data: dict) -> str:
    """Build the LLM prompt from spec and scraped article data."""
    
    # Extract core components from spec
    meta = spec.get('meta', {})
    task = spec.get('task', {})
    output_schema = spec.get('output_schema', {})
    llm_prompts = spec.get('llm_prompts', {})
    
    title = scraped_data.get('title', '')
    content = scraped_data.get('content', '')
    url = scraped_data.get('url', '')
    
    # Build prompt
    prompt = f"""# Task: Clickbait Analysis
Version: {meta.get('version', 'unknown')}

## Article to analyze:
**URL:** {url}
**Title:** {title}
**Content (first 3000 chars):**
{content[:3000]}

## Your task:
{task.get('description', 'Analyze if this article title is clickbait.')}

## Analysis instructions:
{llm_prompts.get('judgment_prompt', 'Provide clickbait analysis with score 0-100.')}

## Required output format (JSON):
Return ONLY a valid JSON object with these fields:
- score (number 0-100)
- label (string: "not_clickbait", "mild", or "strong")
- rationale (array of strings explaining the scoring)
- rationale_user_friendly (array of strings in Polish for end users)
- signals (object with detected patterns)
- suggestions (object with neutral rewrite and editor notes)
- diagnostics (object with processing metadata)
- summary (string: 2-4 sentences, max 400 chars, neutral description of article content)

Return ONLY the JSON object, no markdown formatting or extra text.
"""
    
    return prompt


def analyze_article(client: OpenAI, spec: dict, scraped_data: dict, model: str = "gpt-4o-mini") -> Optional[dict]:
    """
    Send article to GitHub Models API for analysis.
    
    Args:
        client: OpenAI client configured for GitHub Models
        spec: Loaded YAML spec
        scraped_data: Scraped article data
        model: Model name (default: gpt-4o-mini)
    
    Returns:
        Analysis dict or None if error
    """
    prompt = build_analysis_prompt(spec, scraped_data)
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a clickbait analysis expert. Return only valid JSON, no markdown."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,  # Lower temp for more consistent analysis
            max_tokens=2000,
        )
        
        # Extract and parse response
        response_text = response.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()
        
        analysis = json.loads(response_text)
        
        # Add metadata
        analysis['id'] = scraped_data.get('id')
        analysis['source'] = scraped_data.get('source')
        analysis['url'] = scraped_data.get('url')
        analysis['title'] = scraped_data.get('title')
        
        # Add generation metadata
        if 'diagnostics' not in analysis:
            analysis['diagnostics'] = {}
        analysis['diagnostics']['analyzer'] = 'github_models'
        analysis['diagnostics']['model'] = model
        analysis['diagnostics']['analyzed_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
        
        return analysis
        
    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to parse JSON response: {e}")
        print(f"Raw response: {response_text[:200]}...")
        return None
    except Exception as e:
        error_str = str(e)
        # Check if it's Azure content filter error
        if 'content_filter' in error_str or 'ResponsibleAIPolicyViolation' in error_str:
            print(f"[SKIP] Content filtered by Azure policy (sensitive content)")
            print(f"       This article will be skipped due to content policy restrictions")
            # Return a special marker to indicate this should be skipped, not retried
            return {'_skipped': True, 'reason': 'content_filter'}
        print(f"[ERROR] API error: {e}")
        return None


def save_analysis(analysis: dict, file_id: str):
    """Save analysis to JSON file."""
    output_path = ANALYSIS_DIR / f"analysis_{file_id}.json"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Analyze articles using GitHub Models API")
    parser.add_argument("--limit", type=int, help="Analyze only first N files")
    parser.add_argument("--model", default="gpt-4o-mini", help="Model to use (default: gpt-4o-mini)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be analyzed without API calls")
    parser.add_argument("--delay", type=float, default=4.0, help="Delay between requests in seconds (default: 4)")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Clickbait Analyzer - GitHub Models Edition")
    print("=" * 60)
    
    # Load spec
    print("\nLoading specification...")
    spec = load_spec()
    if not spec:
        print("Failed to load spec file")
        return 1
    print(f"Loaded spec version {spec.get('meta', {}).get('version', 'unknown')}")
    
    # Find unanalyzed files
    print("\nScanning for unanalyzed articles...")
    unanalyzed = find_unanalyzed_files()
    
    if not unanalyzed:
        print("All articles already analyzed!")
        return 0
    
    total = len(unanalyzed)
    to_process = unanalyzed[:args.limit] if args.limit else unanalyzed
    
    print(f"Found {total} unanalyzed articles")
    if args.limit:
        print(f"Processing first {len(to_process)} (--limit {args.limit})")
    
    if args.dry_run:
        print("\nDRY RUN - Would analyze:")
        for f in to_process:
            print(f"  * {f.name}")
        return 0
    
    # Initialize GitHub Models client
    print("\nConnecting to GitHub Models API...")
    try:
        client = get_github_models_client()
        print(f"Connected! Using model: {args.model}")
    except ValueError as e:
        print(f"ERROR: {e}")
        return 1
    
    # Process files
    print(f"\nStarting analysis (delay: {args.delay}s between requests)...")
    print("-" * 60)
    
    success_count = 0
    error_count = 0
    skipped_count = 0
    
    for idx, scraped_file in enumerate(to_process, 1):
        file_id = scraped_file.stem.replace("scraped_", "")
        
        print(f"\n[{idx}/{len(to_process)}] Analyzing {scraped_file.name}...")
        
        try:
            # Load scraped data
            with open(scraped_file, 'r', encoding='utf-8') as f:
                scraped_data = json.load(f)
            
            # Analyze
            analysis = analyze_article(client, spec, scraped_data, model=args.model)
            
            if analysis:
                # Check if this was skipped due to content filter
                if analysis.get('_skipped'):
                    print(f"[SKIP] Skipped due to: {analysis.get('reason', 'unknown')}")
                    skipped_count += 1
                else:
                    # Save
                    output_path = save_analysis(analysis, file_id)
                    score = analysis.get('score', 'N/A')
                    label = analysis.get('label', 'N/A')
                    print(f"[OK] Saved to {output_path.name}")
                    print(f"     Score: {score}, Label: {label}")
                    success_count += 1
            else:
                print(f"[ERROR] Analysis failed")
                error_count += 1
            
            # Rate limiting
            if idx < len(to_process):  # Don't delay after last item
                time.sleep(args.delay)
                
        except Exception as e:
            print(f"[ERROR] Error processing {scraped_file.name}: {e}")
            error_count += 1
            continue
    
    # Summary
    print("\n" + "=" * 60)
    print("Analysis Complete!")
    print("=" * 60)
    print(f"[OK] Successful: {success_count}")
    if skipped_count > 0:
        print(f"[SKIP] Skipped (content filter): {skipped_count}")
    print(f"[ERROR] Errors: {error_count}")
    print(f"Results saved to: {ANALYSIS_DIR}")
    
    return 0 if error_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
