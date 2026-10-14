from enum import Enum
from typing import Dict, Any, List
from loguru import logger

class ReasoningMode(str, Enum):
    CHAIN_OF_THOUGHT = "chain_of_thought"
    TREE_OF_THOUGHT = "tree_of_thought"
    GRAPH_OF_THOUGHT = "graph_of_thought"
    HYPOTHESIS_TESTING = "hypothesis_testing"
    DEDUCTIVE = "deductive"
    INDUCTIVE = "inductive"
    ABDUCTIVE = "abductive"
    COUNTERFACTUAL = "counterfactual"
    RISK_ANALYSIS = "risk_analysis"

class ReasoningStrategyManager:
    """
    Reasoning Strategy Selector for AgentX (Phase 6 Reasoning Engine).
    Selects the optimal cognitive reasoning mode based on goal complexity, uncertainty, and domain type.
    """

    @staticmethod
    def select_mode(goal_title: str, complexity_score: int = 5, domain_category: str = "general") -> ReasoningMode:
        """Selects appropriate reasoning strategy mode."""
        title_lower = goal_title.lower()

        if any(w in title_lower for w in ["what if", "alternative", "counterfactual", "compare"]):
            return ReasoningMode.COUNTERFACTUAL
        elif any(w in title_lower for w in ["hypothesis", "test", "verify", "scientific"]):
            return ReasoningMode.HYPOTHESIS_TESTING
        elif any(w in title_lower for w in ["risk", "security", "threat", "safety"]):
            return ReasoningMode.RISK_ANALYSIS
        elif complexity_score >= 8 or domain_category in ["coding", "architecture"]:
            return ReasoningMode.GRAPH_OF_THOUGHT
        elif complexity_score >= 6:
            return ReasoningMode.TREE_OF_THOUGHT
        else:
            return ReasoningMode.CHAIN_OF_THOUGHT

    @staticmethod
    def generate_reasoning_trace(mode: ReasoningMode, goal_title: str) -> Dict[str, Any]:
        """Generates structured initial reasoning graph trace."""
        logger.info(f"ReasoningStrategyManager: Generating reasoning trace for mode '{mode.value}'")
        return {
            "strategy_mode": mode.value,
            "goal": goal_title,
            "hypotheses": [f"Hypothesis 1: Execution pathway for {goal_title}"],
            "assumptions": ["Goal requirements are well-formed", "Specialized agents and tools are operational"],
            "steps": [
                {"step_id": 1, "description": "Decompose problem requirements", "status": "completed"},
                {"step_id": 2, "description": "Evaluate execution pathways", "status": "active"},
                {"step_id": 3, "description": "Verify intermediate results", "status": "pending"}
            ]
        }
