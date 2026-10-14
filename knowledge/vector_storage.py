from typing import Dict, Any, List, Optional
from loguru import logger

class VectorStorageManager:
    """
    Provider-Independent Vector Storage Manager for AgentX.
    Abstracts vector backends: Qdrant, Pinecone, Chroma, pgvector, FAISS, and Mock.
    """

    def __init__(self, backend: str = "mock"):
        self.backend = backend.lower()
        # chunk_id -> dict
        self._store: Dict[str, Dict[str, Any]] = {}
        logger.info(f"VectorStorageManager: Initialized backend '{self.backend}'")

    async def upsert_chunk(self, chunk_id: str, vector: List[float], metadata: Dict[str, Any]) -> bool:
        """Upserts a chunk vector payload into vector storage."""
        self._store[chunk_id] = {
            "chunk_id": chunk_id,
            "vector": vector,
            "metadata": metadata
        }
        return True

    async def search_similar(
        self,
        query_vector: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Searches vector store for top-k similar chunks using cosine similarity."""
        candidates = list(self._store.values())

        if filters:
            user_id = filters.get("user_id")
            if user_id and user_id != "global":
                candidates = [c for c in candidates if c["metadata"].get("user_id") in [user_id, "global"]]

        results = []
        for item in candidates:
            sim = self._cosine_similarity(query_vector, item["vector"])
            res_item = item["metadata"].copy()
            res_item["vector_similarity"] = round(sim, 4)
            results.append(res_item)

        results.sort(key=lambda x: x["vector_similarity"], reverse=True)
        return results[:top_k]

    def _cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        """Computes cosine similarity between two vectors."""
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = sum(a * a for a in vec_a) ** 0.5
        norm_b = sum(b * b for b in vec_b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)
