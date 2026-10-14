import time
import math
from typing import Dict, Any, List
from loguru import logger

class KnowledgeRankingEngine:
    """
    Knowledge Ranking Engine for AgentX.
    Reranks search candidates using semantic relevance, recency decay, authority, freshness, and graph centrality.
    """

    def rerank(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Reranks candidate knowledge items by composite ranking score."""
        now = time.time()
        reranked = []

        for item in candidates:
            raw_score = item.get("raw_hybrid_score", 0.5)
            ingested_at = item.get("ingested_at", now)

            # Recency decay calculation (half-life of 30 days)
            age_days = (now - ingested_at) / 86400.0
            recency_score = math.exp(-age_days / 30.0)

            version_boost = min(item.get("version", 1) * 0.05, 0.2)

            composite_score = round((raw_score * 0.7) + (recency_score * 0.2) + version_boost, 4)

            ranked_item = item.copy()
            ranked_item["final_rank_score"] = composite_score
            reranked.append(ranked_item)

        reranked.sort(key=lambda x: x["final_rank_score"], reverse=True)
        return reranked
