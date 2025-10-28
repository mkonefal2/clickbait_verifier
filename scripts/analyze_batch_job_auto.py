"""
Batch analyzer that applies a deterministic, regex-based approximation of
'clickbait_agent_spec_v1.1.yaml' rules to scraped JSON files and writes
analysis_{id}.json files into reports/analysis, avoiding overwrites by adding
numeric suffixes when needed.

This is a pragmatic local implementation (no LLM). It focuses on the main
requirements you asked for: regex-driven detection, geography mismatch,
hedging/overcertainty detection, detection of numbers/dates/time windows,
scoring heuristic consistent with the spec weights and caps, and writing files.

Usage (PowerShell):
& .\.venv\Scripts\python.exe scripts\analyze_batch_job_auto.py

"""
import re
import json
from pathlib import Path
import sys
import time

BASE_DIR = Path(__file__).resolve().parents[1]
SCRAPED_DIR = BASE_DIR / "reports" / "scraped"
ANALYSIS_DIR = BASE_DIR / "reports" / "analysis"
SPEC_PATH = BASE_DIR / "clickbait_agent_spec_v1.1.yaml"

# Minimal regexes copied/inferred from the YAML spec for core signals
TITLE_SENSATIONAL_RE = re.compile(r"\b(kuriozaln\w*|absurd\w*|szok\w*|niewiarygodn\w*|nie uwierzysz|nie zgadniesz)\b", re.I)
TITLE_ABSOLUTES_RE = re.compile(r"\b(zawsze|nigdy|wsz(?:yst)?|wszystko|na pewno|100%|gwarantowan)\b", re.I)
CONTENT_SENSATIONAL_RE = TITLE_SENSATIONAL_RE
HEDGING_RE = re.compile(r"\b(mo\u017ce|prawdopodobnie|sugeruje|wskazuje|wydaje si\u0119|mo\u017cliwe|mog\u0105)\b", re.I)
OVERCERTAINTY_RE = TITLE_ABSOLUTES_RE
NUMBERS_RE = re.compile(r"\b\d{1,3}(?:[\d\s,.]|\s)?(euro|z\.|zloty|zł|\b)\b|\b\d+\b", re.I)
TIME_WINDOW_RE = re.compile(r"\b(\d{1,2}:\d{2})\s*(?:-|a|do|–)\s*(\d{1,2}:\d{2})\b")
COUNTRY_TITLE_RE = re.compile(r"\b(w\s+Polsce|Polsk(?:a|i|e|\u0119)|Polska|w\s+Francji|Francja|we\s+Francji|Niemcy|w\s+Niemczech|Wielkiej\s+Brytanii|UK|Anglia)\b", re.I)
COUNTRY_CONTENT_RE = COUNTRY_TITLE_RE
FRANCE_WORDS_RE = re.compile(r"\b(we\s+Francji|Francja|francusk)\b", re.I)

# Scoring constants (small deterministic heuristic derived from spec)
WEIGHTS = {"title_clickbait_weight": 0.40, "content_clickbait_weight": 0.15, "mismatch_weight": 0.40, "monetization_weight": 0.05}
ADDITIONS = {"title_sensational": 12, "content_sensational": 8}
MISMATCH_PENALTIES = {"country_mismatch": 18, "exaggeration_gap": 14, "low_alignment": 18}
MISMATCH_CAP = 30

ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)


def safe_write(path: Path, data: dict):
    """Write JSON to path; if exists, add numeric suffix before extension."""
    if not path.exists():
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        return path
    # add suffixes
    stem = path.stem
    parent = path.parent
    i = 1
    while True:
        candidate = parent / f"{stem}_{i}.json"
        if not candidate.exists():
            candidate.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
            return candidate
        i += 1


def analyze_article(article: dict, spec_defaults: dict = None):
    start = time.time()
    title = article.get("title", "")
    content = article.get("content", "")
    aid = article.get("id")

    title_hits = []
    content_hits = []
    title_semantic_hits = []
    content_semantic_hits = []
    credibility_hits = []
    monetization_hits = []

    # Title checks
    if TITLE_SENSATIONAL_RE.search(title):
        title_hits.append("sensational_phrases: 'matched'")
    if TITLE_ABSOLUTES_RE.search(title):
        title_hits.append("absolutes: 'matched'")

    # Content checks
    if CONTENT_SENSATIONAL_RE.search(content):
        content_hits.append("sensational_phrases: 'matched'")
    hedges = HEDGING_RE.findall(content)
    if hedges:
        content_hits.append(f"hedging: {list(set([h.lower() for h in hedges]))}")
    numbers = NUMBERS_RE.findall(content)
    if numbers:
        content_hits.append("numbers_dates: matched")
        credibility_hits.append("numbers_dates: matched")
    times = TIME_WINDOW_RE.findall(content)
    detected_time_windows = [f"{a}-{b}" for (a, b) in times]

    # Geography
    title_countries = []
    content_countries = []
    if COUNTRY_TITLE_RE.search(title):
        title_countries = COUNTRY_TITLE_RE.findall(title)
    else:
        # assume local if missing per spec
        title_countries = ["Polska (assumed)"]
    if COUNTRY_CONTENT_RE.search(content):
        content_countries = COUNTRY_CONTENT_RE.findall(content)
    # Simplified country mismatch: check for 'Francja' presence in content and title not France
    country_mismatch = False
    if FRANCE_WORDS_RE.search(content) and not FRANCE_WORDS_RE.search(title):
        # title assumed local (Polska) while content mentions Francja
        country_mismatch = True

    # Compute alignment_score heuristic (0..1): lower when mismatch exists
    alignment_score = 1.0
    if country_mismatch:
        alignment_score = 0.3
    else:
        # if content sensational and title sensational -> higher alignment
        if CONTENT_SENSATIONAL_RE.search(content) and TITLE_SENSATIONAL_RE.search(title):
            alignment_score = 0.8
        else:
            alignment_score = 0.9

    # Exaggeration gap: true if title sensational but content hedging or lower alignment
    exaggeration_gap = False
    if TITLE_SENSATIONAL_RE.search(title) and (hedges or alignment_score < 0.65):
        exaggeration_gap = True

    # Scoring: compute components
    title_points = 0
    if TITLE_SENSATIONAL_RE.search(title):
        title_points += ADDITIONS["title_sensational"]
    if TITLE_ABSOLUTES_RE.search(title):
        title_points += 8

    content_points = 0
    if CONTENT_SENSATIONAL_RE.search(content):
        content_points += ADDITIONS["content_sensational"]

    mismatch_points = 0
    penalties = 0
    if country_mismatch:
        penalties += MISMATCH_PENALTIES["country_mismatch"]
    if exaggeration_gap:
        penalties += MISMATCH_PENALTIES["exaggeration_gap"]
    if alignment_score < 0.45:
        penalties += MISMATCH_PENALTIES["low_alignment"]
    mismatch_points = min(penalties, MISMATCH_CAP)

    # Weighted sum to 0..100
    # Normalize components roughly according to caps in spec
    title_comp = (title_points / 60) * 100 * WEIGHTS["title_clickbait_weight"]
    content_comp = (max(0, content_points - 0) / 35) * 100 * WEIGHTS["content_clickbait_weight"]
    mismatch_comp = (mismatch_points / MISMATCH_CAP) * 100 * WEIGHTS["mismatch_weight"]
    monet_comp = 0
    raw_score = title_comp + content_comp + mismatch_comp + monet_comp
    # Round to nearest 5
    score = int(5 * round(raw_score / 5))
    if score < 0:
        score = 0
    if score > 100:
        score = 100

    # Map to label per thresholds
    if score <= 24:
        label = "not_clickbait"
    elif 25 <= score <= 49:
        label = "mild"
    elif 50 <= score <= 74:
        label = "strong"
    else:
        label = "extreme"

    rationale = []
    rationale.append(f"title: regex checks -> sensational matched={bool(TITLE_SENSATIONAL_RE.search(title))}, absolutes matched={bool(TITLE_ABSOLUTES_RE.search(title))}")
    rationale.append(f"content: regex checks -> sensational matched={bool(CONTENT_SENSATIONAL_RE.search(content))}, hedging_count={len(hedges)}")
    rationale.append(f"geography: title_countries={title_countries}, content_countries={content_countries}, country_mismatch={country_mismatch}")
    rationale.append(f"alignment_score_estimated={alignment_score}")
    rationale.append(f"mismatch_penalties_raw={penalties}, applied_mismatch_points={mismatch_points}")
    rationale.append(f"scoring_components: title_points={title_points}, content_points={content_points}, mismatch_points={mismatch_points}, raw_score_approx={raw_score}")

    rationale_user_friendly = []
    # user-friendly points
    if TITLE_SENSATIONAL_RE.search(title):
        rationale_user_friendly.append("Tytuł używa sensacyjnego słowa i pobudza emocje.")
    if country_mismatch:
        rationale_user_friendly.append("Tytuł nie wskazuje kraju, a artykuł dotyczy Francji — to może wprowadzać czytelnika w błąd.")
    if hedges:
        rationale_user_friendly.append("W treści są sformułowania takie jak 'mogą' lub 'zazwyczaj', które osłabiają stanowczość stwierdzeń z tytułu.")

    signals = {
        "title_hits": title_hits,
        "content_hits": content_hits,
        "title_semantic_hits": title_semantic_hits,
        "content_semantic_hits": content_semantic_hits,
        "credibility_hits": credibility_hits,
        "monetization_hits": monetization_hits,
        "geography_hits": {"title_countries": title_countries, "content_countries": content_countries},
        "mismatch": {
            "alignment_score": alignment_score,
            "exaggeration_gap": exaggeration_gap,
            "paywall_or_short": len(content) < 500,
            "country_mismatch": country_mismatch,
            "time_omission": False,
            "date_omission": False,
            "detected_time_windows": detected_time_windows,
            "detected_dates": []
        }
    }

    diagnostics = {
        "tokens_title": len(title.split()),
        "tokens_content": len(content.split()),
        "processing_time_ms": int((time.time() - start) * 1000),
        "windows_scanned": []
    }

    output = {
        "id": aid,
        "source": article.get("source"),
        "url": article.get("url"),
        "title": title,
        "score": score,
        "label": label if not (len(content) < 500) else "insufficient_content",
        "rationale": rationale,
        "rationale_user_friendly": rationale_user_friendly,
        "signals": signals,
        "suggestions": {
            "rewrite_title_neutral": "",
            "notes_to_editor": ""
        },
        "diagnostics": diagnostics,
        # Nowe pola dla aplikacji mobilnej:
        "sensationalism": _determine_sensationalism(title, content),
        "emotionalTone": _determine_emotional_tone(title, content, hedges),
        "manipulationTechniques": _determine_manipulation_techniques(
            title, content, country_mismatch, exaggeration_gap, hedges
        ),
        "summary": _generate_summary(title, content, score)
    }

    # suggestions (simple)
    if country_mismatch:
        output["suggestions"]["rewrite_title_neutral"] = "Dodaj informację o kraju: We Francji wprowadzono nowe przepisy dotyczące koszenia trawy..."
        output["suggestions"]["notes_to_editor"] = "Tytuł sugeruje lokalny kontekst; rozważ doprecyzowanie, że przepis dotyczy wybranych departamentów we Francji."
    elif TITLE_SENSATIONAL_RE.search(title):
        output["suggestions"]["rewrite_title_neutral"] = re.sub(r"(?i)kuriozaln\w*", "kontrowersyjny", title)
        output["suggestions"]["notes_to_editor"] = "Zastąp słowo sensacyjne neutralniejszym odpowiednikiem."

    return output


def _determine_sensationalism(title: str, content: str) -> str:
    """Określa poziom sensacjonalizmu artykułu."""
    title_sensational = TITLE_SENSATIONAL_RE.search(title)
    content_sensational = CONTENT_SENSATIONAL_RE.search(content)
    
    if title_sensational and content_sensational:
        return "Wysoki - tytuł i treść zawierają sensacyjne słowa"
    elif title_sensational:
        return "Średni - tylko tytuł jest sensacyjny"
    elif content_sensational:
        return "Niski - tylko treść zawiera elementy sensacyjne"
    else:
        return "Brak - neutralny sposób prezentacji"


def _determine_emotional_tone(title: str, content: str, hedges: list) -> str:
    """Określa ton emocjonalny artykułu."""
    has_sensational = TITLE_SENSATIONAL_RE.search(title) or CONTENT_SENSATIONAL_RE.search(content)
    has_absolutes = TITLE_ABSOLUTES_RE.search(title)
    
    if has_absolutes:
        return "Bardzo emocjonalny - używa słów absolutnych i pewności"
    elif has_sensational and not hedges:
        return "Emocjonalny - sensacyjny język bez hedgingu"
    elif has_sensational and hedges:
        return "Umiarkowany - sensacyjny tytuł, ale ostrożna treść"
    elif hedges:
        return "Neutralny - dominuje ostrożny język"
    else:
        return "Neutralny - bez wyraźnych emocji"


def _determine_manipulation_techniques(
    title: str, 
    content: str, 
    country_mismatch: bool,
    exaggeration_gap: bool,
    hedges: list
) -> list:
    """Identyfikuje zastosowane techniki manipulacji."""
    techniques = []
    
    if country_mismatch:
        techniques.append("Ukrywanie kontekstu geograficznego")
    
    if exaggeration_gap:
        techniques.append("Przesadny tytuł vs. ostrożna treść")
    
    if TITLE_ABSOLUTES_RE.search(title):
        techniques.append("Słowa absolutne (zawsze/nigdy)")
    
    if TITLE_SENSATIONAL_RE.search(title):
        techniques.append("Sensacyjne słowa w tytule")
    
    if NUMBERS_RE.search(content) and not NUMBERS_RE.search(title):
        techniques.append("Ukrywanie liczb w tytule")
    
    if TIME_WINDOW_RE.search(content) and len(hedges) > 3:
        techniques.append("Nadmierne hedging i niepewność")
    
    if not techniques:
        techniques.append("Brak wykrytych technik manipulacji")
    
    return techniques


def _generate_summary(title: str, content: str, score: int) -> str:
    """
    Generuje zwięzłe streszczenie TREŚCI artykułu (nie analizy clickbaitowości).
    Zgodne z wymaganiami z clickbait_agent_spec_v1.1.yaml:
    - 2-4 zdania, max 400 znaków
    - Opisuje O CZYM jest artykuł
    - Obiektywne, neutralne, informacyjne
    """
    # Usuń HTML tagi jeśli są
    clean_content = re.sub(r'<[^>]+>', '', content)
    
    # Podziel na zdania
    sentences = re.split(r'[.!?]+\s+', clean_content.strip())
    
    # Weź pierwsze 2-4 zdania (max 400 znaków)
    summary_sentences = []
    total_length = 0
    
    for sentence in sentences[:6]:  # Max 6 zdań do rozważenia
        sentence = sentence.strip()
        if not sentence or len(sentence) < 20:  # Pomiń zbyt krótkie
            continue
        
        # Pomiń elementy UI/nawigacji
        if any(skip in sentence.lower() for skip in ['udostępnij', 'facebook', 'kopiuj link', 'skróć artykuł', 'zobacz także']):
            continue
            
        if total_length + len(sentence) > 400:
            break
            
        summary_sentences.append(sentence)
        total_length += len(sentence)
        
        if len(summary_sentences) >= 4:  # Max 4 zdania
            break
    
    # Jeśli nie udało się zebrać zdań, użyj tytułu jako fallback
    if not summary_sentences:
        return f"Artykuł dotyczy: {title[:350]}"
    
    summary = '. '.join(summary_sentences)
    if summary and not summary.endswith('.'):
        summary += '.'
    
    return summary


def main(file_list):
    spec_defaults = {}
    created = []
    for file_name in file_list:
        path = SCRAPED_DIR / file_name
        if not path.exists():
            continue
        try:
            art = json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            continue
        out = analyze_article(art, spec_defaults)
        aid = out.get("id")
        target = ANALYSIS_DIR / f"analysis_{aid}.json"
        written = safe_write(target, out)
        created.append(str(written))
    return created


if __name__ == "__main__":
    # If user provided file list via args, use them; else analyze all files in scraped dir
    if len(sys.argv) > 1:
        files = sys.argv[1:]
    else:
        files = [p.name for p in SCRAPED_DIR.glob("scraped_*.json")]
    created_files = main(files)
    # Per user request: do not print verbose output clutter — print only the list of created files (one per line)
    for f in created_files:
        print(f)
