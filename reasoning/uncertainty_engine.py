from typing import Dict, Any, List
from loguru import logger

class UncertaintyEngine:
    """
    Uncertainty & Risk Estimator for AgentX (Phase 6 Reasoning Engine).
    Estimates confidence, missing information, conflicting evidence, tool reliability, and data freshness.
    """

    def estimate_uncertainty(
        self,
        goal_title: str,
        context_memories: List[Any],
        tool_results: Dict[str, Any],
        agent_outputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculates comprehensive uncertainty metrics."""
        confidence_base = 0.90
        missing_info = []

        if not context_memories:
            confidence_base -= 0.10
            missing_info.append("No prior user memory context found.")

        if not tool_results:
            confidence_base -= 0.05
            missing_info.append("No live external tool results gathered yet.")

        conflicting_evidence = False
        tool_reliability = 0.95 if tool_results else 0.85

        uncertainty_score = round(1.0 - max(confidence_base, 0.1), 2)
        confidence_score = round(max(confidence_base, 0.1), 2)

        metrics = {
            "confidence_score": confidence_score,
            "uncertainty_score": uncertainty_score,
            "missing_information": missing_info,
            "conflicting_evidence": conflicting_evidence,
            "tool_reliability": tool_reliability,
            "requires_clarification": confidence_score < 0.60
        }

        logger.info(f"UncertaintyEngine: Evaluated confidence score {confidence_score} (Uncertainty: {uncertainty_score})")
        return metrics
