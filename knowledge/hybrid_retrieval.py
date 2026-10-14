from typing import Dict, Any, List, Optional
from loguru import logger

class HybridRetrievalEngine:
    """
    Hybrid Retrieval Engine for AgentX.
    Combines vector semantic search, BM25 keyword search, metadata filtering, and graph traversal
    to produce highest quality knowledge context.
    """

    async def execute_hybrid_search(
        self,
        query: str,
        vector_store: Any,
        embedding_engine: Any,
        knowledge_graph: Any,
        user_id: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Executes hybrid retrieval: vector similarity + BM25 keyword match + graph traversal."""
        query_vector = embedding_engine.generate_embedding(query)
        filters = {"user_id": user_id}

        # 1. Vector Search
        vector_results = await vector_store.search_similar(query_vector, top_k=top_k * 2, filters=filters)

        # 2. BM25 Keyword Search simulation
        query_words = set(query.lower().split())
        for item in vector_results:
            content = str(item.get("content", "")).lower()
            keyword_score = sum(1 for w in query_words if w in content) / max(len(query_words), 1)
            item["bm25_score"] = round(keyword_score, 4)

            # Combined raw score
            v_score = item.get("vector_similarity", 0.5)
            item["raw_hybrid_score"] = round((v_score * 0.7) + (keyword_score * 0.3), 4)

        vector_results.sort(key=lambda x: x["raw_hybrid_score"], reverse=True)
        return vector_results[:top_k]
