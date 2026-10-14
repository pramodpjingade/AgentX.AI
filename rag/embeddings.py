import os
import hashlib
from typing import List
from loguru import logger

class EmbeddingGenerator:
    """Generates high-dimensional vector representations for text blocks."""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")

    def _is_configured(self) -> bool:
        return self.api_key is not None and "your-" not in self.api_key

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate a 1536-dimensional vector embedding."""
        if self._is_configured():
            try:
                from langchain_openai import OpenAIEmbeddings
                client = OpenAIEmbeddings(openai_api_key=self.api_key)
                # embed_query is a blocking synchronous call, run it directly
                embedding = client.embed_query(text)
                return embedding
            except Exception as e:
                logger.error(f"EmbeddingGenerator: Failed generating OpenAI embedding: {e}. Falling back...")
                
        # Fallback: Deterministic vector mapping using MD5 hash (1536 floats)
        return self._generate_deterministic_vector(text)

    def _generate_deterministic_vector(self, text: str) -> List[float]:
        """Creates a repeatable, normalized 1536 float list based on the text hash."""
        vector = []
        # Calculate seed hash
        h = hashlib.md5(text.encode("utf-8")).hexdigest()
        seed = int(h, 16)
        
        # Simple LCG pseudorandom number generator to fill 1536 dimensions
        val = seed
        for _ in range(1536):
            val = (1103515245 * val + 12345) & 0xffffffff
            # Map integer to float range [-1.0, 1.0]
            vector.append((val / 0xffffffff) * 2.0 - 1.0)
            
        # Normalize vector to unit length
        sq_sum = sum(x*x for x in vector)
        norm = sq_sum ** 0.5
        if norm > 0:
            vector = [x / norm for x in vector]
            
        return vector
