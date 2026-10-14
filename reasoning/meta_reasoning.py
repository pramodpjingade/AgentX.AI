from typing import Dict, Any, List
from loguru import logger

class MetaReasoningEngine:
    """
    Meta-Reasoning & Explainability Engine for AgentX.
    Evaluates reasoning strategy efficiency, tracks cognitive performance metrics,
    and formulates human-readable explainability traces when requested.
    """

    def generate_explainability_trace(
        self,
        goal_title: str,
        reasoning_mode: str,
        confidence_metrics: Dict[str, Any],
        reflections: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Formulates an explainable cognitive trace describing system decision rationale."""
        logger.info(f"MetaReasoningEngine: Formulating explainability trace for goal '{goal_title}'")

        trace = {
            "mission_goal": goal_title,
            "chosen_reasoning_strategy": reasoning_mode,
            "system_confidence": confidence_metrics.get("confidence_score", 0.95),
            "uncertainty_level": confidence_metrics.get("uncertainty_score", 0.05),
            "reflection_checkpoints_passed": len([r for r in reflections if r.get("passed_reflection")]),
            "explanation_summary": f"AgentX executed goal '{goal_title}' using {reasoning_mode} strategy with system confidence of {confidence_metrics.get('confidence_score', 0.95) * 100}%."
        }

        return trace
