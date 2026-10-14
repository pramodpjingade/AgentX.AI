import time
from typing import Dict, Any, List
from loguru import logger
from memory.importance_scorer import MemoryImportanceScorer

class ForgettingEngine:
    """
    Intelligent Forgetting & Lifecycle Manager for AgentX.
    Handles temporary memory expiration, low-value memory archiving, and GDPR-compliant deletion.
    """

    def __init__(self, score_threshold: float = 0.15):
        self.score_threshold = score_threshold
        logger.info("ForgettingEngine: Lifecycle & GDPR Forgetting Engine initialized.")

    def audit_and_prune(self, memory_nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Audits memory nodes, evicting expired working memories and low-importance stale nodes."""
        active_nodes = []
        now = time.time()

        for node in memory_nodes:
            category = node.get("category", "long_term")

            # 1. TTL Expiration check for working memory
            ttl = node.get("ttl_seconds")
            created_at = node.get("created_at_ts", now)
            if ttl and (now - created_at > ttl):
                logger.info(f"ForgettingEngine: Evicted TTL-expired working memory '{node.get('id')}'")
                continue

            # 2. Importance score audit
            access_count = node.get("access_count", 1)
            score = MemoryImportanceScorer.calculate_score(
                created_timestamp=created_at,
                access_count=access_count,
                category=category
            )
            node["importance_score"] = score

            if score < self.score_threshold and category not in ["preference", "procedural"]:
                logger.info(f"ForgettingEngine: Archived low-importance memory '{node.get('id')}' (score: {score})")
                continue

            active_nodes.append(node)

        return active_nodes

    def forget_by_id(self, memory_nodes: List[Dict[str, Any]], target_id: str) -> List[Dict[str, Any]]:
        """GDPR-compliant memory deletion for specific memory ID."""
        filtered = [n for n in memory_nodes if n.get("id") != target_id]
        logger.info(f"ForgettingEngine: GDPR deletion executed for memory ID '{target_id}'")
        return filtered

    def forget_by_keyword(self, memory_nodes: List[Dict[str, Any]], keyword: str) -> List[Dict[str, Any]]:
        """GDPR-compliant memory deletion for specific keyword or PII content."""
        kw_lower = keyword.lower()
        filtered = [n for n in memory_nodes if kw_lower not in str(n.get("content", "")).lower()]
        logger.info(f"ForgettingEngine: GDPR keyword purge executed for '{keyword}'")
        return filtered
