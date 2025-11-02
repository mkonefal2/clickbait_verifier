"""
OpenAI GPT-based analyzer for clickbait detection.
Integrates with the existing scraping infrastructure.
"""
import os
import json
import yaml
import time
from pathlib import Path
from typing import Dict, Optional, List
import logging

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# Try to load .env file if available
try:
    from dotenv import load_dotenv
    # Load .env from project root
    env_path = Path(__file__).resolve().parents[1] / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    # dotenv not available, skip
    pass

logger = logging.getLogger(__name__)


class GPTAnalyzer:
    """OpenAI GPT-based clickbait analyzer."""
    
    def __init__(self, 
                 api_key: Optional[str] = None, 
                 model: str = "gpt-4o-mini",
                 spec_path: Optional[str] = None):
        """
        Initialize GPT analyzer.
        
        Args:
            api_key: OpenAI API key (if None, uses OPENAI_API_KEY env var)
            model: OpenAI model name (default: gpt-4o-mini)
            spec_path: Path to YAML specification file
        """
        if OpenAI is None:
            raise ImportError("openai library not installed. Run: pip install openai")
            
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY env var or pass api_key parameter")
            
        self.model = model
        self.client = OpenAI(api_key=self.api_key)
        
        # Load specification
        if spec_path is None:
            # Default to project spec
            base_dir = Path(__file__).resolve().parents[1]
            spec_path = base_dir / "clickbait_agent_spec_simple.yaml"
            
        self.spec = self._load_spec(spec_path)
        
    def _load_spec(self, spec_path: Path) -> dict:
        """Load YAML specification."""
        if not Path(spec_path).exists():
            raise FileNotFoundError(f"Spec file not found: {spec_path}")
            
        with open(spec_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _build_system_prompt(self) -> str:
        """Build system prompt from specification."""
        meta = self.spec.get('meta', {})
        scoring = self.spec.get('scoring', {})
        
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
    
    def _build_user_prompt(self, article: dict) -> str:
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
    
    def analyze_article(self, article: dict) -> Optional[dict]:
        """
        Analyze a single article for clickbait.
        
        Args:
            article: Dictionary with article data (id, title, content, source, url)
            
        Returns:
            Analysis result dictionary or None if failed
        """
        try:
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(article)
            
            start_time = time.time()
            response = self.client.chat.completions.create(
                model=self.model,
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
            result['diagnostics']['model'] = self.model
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze article {article.get('id', 'unknown')}: {e}")
            return None
    
    def analyze_batch(self, articles: List[dict], delay_seconds: float = 1.0) -> List[dict]:
        """
        Analyze multiple articles with rate limiting.
        
        Args:
            articles: List of article dictionaries
            delay_seconds: Delay between API calls for rate limiting
            
        Returns:
            List of analysis results (may contain None for failed analyses)
        """
        results = []
        
        for i, article in enumerate(articles):
            logger.info(f"Analyzing article {i+1}/{len(articles)}: {article.get('id', 'unknown')}")
            
            result = self.analyze_article(article)
            results.append(result)
            
            # Rate limiting
            if i < len(articles) - 1:
                time.sleep(delay_seconds)
                
        return results


# Legacy function for backwards compatibility
def analyze_batch(*args, **kwargs):
    """Legacy function - now uses GPT analyzer."""
    logger.warning("analyze_batch called with legacy interface - consider using GPTAnalyzer class directly")
    
    # Try to create analyzer with default settings
    try:
        analyzer = GPTAnalyzer()
        # Assume first argument is list of articles
        if args:
            return analyzer.analyze_batch(args[0])
        return []
    except Exception as e:
        logger.error(f"Legacy analyze_batch failed: {e}")
        raise RuntimeError(f'Analyzer failed: {e}')
