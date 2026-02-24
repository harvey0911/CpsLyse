import numpy as np
import json
import os
import uuid
from pathlib import Path

# Use a local JSON file for persistence since ChromaDB is unavailable on Python 3.14
STORAGE_FILE = Path("./vector_store_data.json")

def _load_data():
    if not STORAGE_FILE.exists():
        return {"documents": [], "metadatas": [], "embeddings": [], "ids": []}
    try:
        with open(STORAGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"documents": [], "metadatas": [], "embeddings": [], "ids": []}

def _save_data(data):
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_decree_article(article_text: str, article_number: str, source_file: str, embedding: list[float]):
    """
    Add a single decree article to the lightweight vector store.
    """
    if not embedding:
        return

    data = _load_data()
    data["documents"].append(article_text)
    data["metadatas"].append({
        "article_number": article_number,
        "source": source_file,
        "type": "decree"
    })
    data["embeddings"].append(embedding)
    data["ids"].append(str(uuid.uuid4()))
    _save_data(data)

def query_decree_articles(query_embedding: list[float], n_results: int = 3):
    """
    Search for relevant decree articles using numpy cosine similarity.
    """
    if not query_embedding:
        return []

    data = _load_data()
    if not data["embeddings"]:
        return []

    # Convert to numpy arrays for calculation
    embeddings = np.array(data["embeddings"])
    query = np.array(query_embedding)

    # Normalize vectors for cosine similarity
    norm_embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    norm_query = query / np.linalg.norm(query)

    # Calculate cosine similarity (dot product of normalized vectors)
    similarities = np.dot(norm_embeddings, norm_query)

    # Get top N indices
    top_indices = np.argsort(similarities)[::-1][:n_results]

    formatted_results = []
    for idx in top_indices:
        formatted_results.append({
            "content": data["documents"][idx],
            "metadata": data["metadatas"][idx],
            "distance": float(1.0 - similarities[idx]) # Convert to "distance" (lower is better)
        })
            
    return formatted_results
