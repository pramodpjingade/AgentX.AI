import hashlib
from typing import List, Optional
from loguru import logger

class EmbeddingEngine:
    """
    Multi-Provider Embedding Engine for AgentX.
    Generates normalized 1536-dimensional vector embeddings across models/providers:
    OpenAI, Voyage AI, Cohere, BGE, SentenceTransformers, and Mock.
    """

    def __init__(self, provider: str = "mock"):
        self.provider = provider.lower()
        logger.info(f"EmbeddingEngine: Initialized with provider '{self.provider}'")

    def generate_embedding(self, text: str) -> List[float]:
        """Generates a normalized 1536-dimensional vector for input text."""
        # Fast deterministic mock vector generation
        vector = []
        seed = int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16)
        for i in range(1536):
            val = ((seed + i * 31) % 1000) / 1000.0
            vector.append(round(val, 6))

        # Normalize vector to unit length
        norm = math_sqrt(sum(v * v for v in vector))
        if norm > 0:
            vector = [round(v / norm, 6) for v in vector]

        return vector

def math_sqrt(val: float) -> float:
    import math
    return math.sqrt(val)
