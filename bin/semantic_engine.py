#!/usr/bin/env python3
"""
Semantic Embedding & Vector Similarity Engine for agy-memory-pkm.
Uses paraphrase-multilingual-MiniLM-L12-v2 (via fastembed ONNX) for 384-dimensional dense semantic vectors.
Supports English and full CJK (Chinese, Japanese, Korean) semantic alignment.
"""

import os
import sys
import math

try:
    from fastembed import TextEmbedding
    HAS_FASTEMBED = True
except ImportError:
    HAS_FASTEMBED = False

DEFAULT_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
_MODEL_INSTANCE = None

def get_embedding_model(model_name=None):
    global _MODEL_INSTANCE
    target_name = model_name or os.environ.get("AGY_EMBEDDING_MODEL", DEFAULT_MODEL_NAME)
    if HAS_FASTEMBED and _MODEL_INSTANCE is None:
        try:
            os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
            _MODEL_INSTANCE = TextEmbedding(model_name=target_name)
        except Exception:
            _MODEL_INSTANCE = None
    return _MODEL_INSTANCE

def embed_texts(texts):
    """Returns a list of list-of-floats (384-d) for input strings."""
    if not texts:
        return []
    model = get_embedding_model()
    if model is not None:
        try:
            embs = list(model.embed(texts))
            return [e.tolist() if hasattr(e, "tolist") else list(e) for e in embs]
        except Exception:
            pass
    return None

def embed_single(text):
    if not text:
        return None
    res = embed_texts([text])
    return res[0] if res else None

def cosine_similarity(vec_a, vec_b):
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    dot = 0.0
    norm_a = 0.0
    norm_b = 0.0
    for a, b in zip(vec_a, vec_b):
        dot += a * b
        norm_a += a * a
        norm_b += b * b
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (math.sqrt(norm_a) * math.sqrt(norm_b))

def rank_items(query_vec, items, vec_fn, top_k=5, min_threshold=0.20):
    """Ranks a list of items by cosine similarity to query_vec."""
    if not query_vec or not items:
        return []
    scored = []
    for item in items:
        v = vec_fn(item)
        if v:
            sim = cosine_similarity(query_vec, v)
            if sim >= min_threshold:
                scored.append((sim, item))
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:top_k]
