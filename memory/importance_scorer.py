import time
import math
from typing import Dict, Any

class MemoryImportanceScorer:
    """
    Memory Importance & Ranking Scorer for AgentX.
    Calculates composite importance score (0.0 to 1.0) based on recency decay, access frequency,
    user feedback, and mission relevance weights.
    """

    @staticmethod
    def calculate_score(
        created_timestamp: float,
        access_count: int = 1,
        user_feedback_score: float = 1.0,
        is_preference: bool = False,
        category: str = "long_term"
    ) -> float:
        """Calculates dynamic memory importance score."""
        if is_preference or category in ["preference", "procedural"]:
            return 1.0  # Preferences and procedures never decay

        # Recency decay (half-life of 7 days = 604800s)
        age_seconds = max(time.time() - created_timestamp, 0)
        recency_decay = math.exp(-age_seconds / (7 * 86400))

        # Frequency boost (logarithmic scale)
        frequency_weight = min(math.log(access_count + 1) / 3.0, 1.0)

        # Composite score calculation
        composite = (recency_decay * 0.4) + (frequency_weight * 0.3) + (user_feedback_score * 0.3)
        return round(min(max(composite, 0.0), 1.0), 4)
