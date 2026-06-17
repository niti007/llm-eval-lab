import json
import time
import numpy as np
import redis
from sentence_transformers import SentenceTransformer
from app.config import REDIS_URL, EMBEDDING_MODEL
from app.utils import normalize_text

r = redis.Redis.from_url(REDIS_URL, decode_responses=True)
embedder = SentenceTransformer(EMBEDDING_MODEL)

CACHE_PREFIX = "semantic_cache:"
CACHE_TTL_SECONDS = 3600
SIMILARITY_THRESHOLD = 0.92

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)

def get_query_embedding(query: str):
    return embedder.encode(normalize_text(query)).tolist()

def get_cache_key(query: str):
    return CACHE_PREFIX + normalize_text(query)

def semantic_cache_lookup(query: str):
    query_emb = get_query_embedding(query)
    best_match = None
    best_score = -1.0

    for key in r.scan_iter(match=f"{CACHE_PREFIX}*"):
        raw = r.get(key)
        if not raw:
            continue

        item = json.loads(raw)
        score = cosine_similarity(query_emb, item["embedding"])
        if score > best_score:
            best_score = score
            best_match = item

    if best_match and best_score >= SIMILARITY_THRESHOLD:
        return {
            "hit": True,
            "score": best_score,
            "response": best_match["response"]
        }

    return {
        "hit": False,
        "score": best_score,
        "response": None
    }

def semantic_cache_store(query: str, response: dict):
    item = {
        "query": query,
        "embedding": get_query_embedding(query),
        "response": response,
        "created_at": time.time()
    }
    r.setex(get_cache_key(query), CACHE_TTL_SECONDS, json.dumps(item))