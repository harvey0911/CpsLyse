from sentence_transformers import SentenceTransformer

# Load a lightweight, multilingual model
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
model = SentenceTransformer(MODEL_NAME, device="cpu")

def get_embedding(text: str) -> list[float]:
    """
    Generate an embedding for the given text.
    """
    if not text or not text.strip():
        return []
    
    embedding = model.encode(text)
    return embedding.tolist()
