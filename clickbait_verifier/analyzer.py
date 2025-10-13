from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from sentence_transformers import SentenceTransformer
from datetime import datetime
from .core.storage import init_db, update_article_analysis, fetch_all_articles, fetch_unanalyzed_articles

MODEL = SentenceTransformer('all-MiniLM-L6-v2')


# Analyzer disabled for local runs; external agent (Copilot) will perform scoring based on exported JSON.

def analyze_batch(ids=None, limit=50):
    # placeholder: analysis is performed by external agent
    return


# keep compute_score in file but mark deprecated

def compute_score(title, content):
    """Deprecated local scoring. Use external analysis agent instead."""
    return 0.0, 'none', '', float('nan')
