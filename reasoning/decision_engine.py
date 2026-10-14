from typing import Dict, Any, List
from loguru import logger

class DecisionEngine:
    """
    Decision Engine & Action Ranker for AgentX (Phase 6 Reasoning Engine).
    Evaluates alternatives, ranks candidate execution actions, calculates expected values vs. risks,
    and records decision rationale.
    """

    def rank_actions(
        self,
        candidate_actions: List[Dict[str, Any]],
        goal_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Ranks candidate execution actions by expected value and feasibility."""
        ranked = []
        for act in candidate_actions:
            name = act.get("name", "action")
            feasibility = act.get("feasibility", 0.9)
            impact = act.get("impact", 0.9)
            risk = act.get("risk", 0.1)

            expected_value = round((feasibility * impact) - (risk * 0.5), 4)

            ranked_act = act.copy()
            ranked_act["expected_value"] = expected_value
            ranked_act["decision_rationale"] = f"Action '{name}' selected with expected value {expected_value}."
            ranked.append(ranked_act)

        ranked.sort(key=lambda x: x["expected_value"], reverse=True)
        logger.info(f"DecisionEngine: Ranked {len(ranked)} candidate actions.")
        return ranked
