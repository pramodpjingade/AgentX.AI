import time
from typing import Dict, Any, List, Optional
from loguru import logger

from reasoning.modes import ReasoningMode, ReasoningStrategyManager
from reasoning.uncertainty_engine import UncertaintyEngine
from reasoning.decision_engine import DecisionEngine
from reasoning.reflection_engine import ReflectionEngine
from reasoning.critic_engine import CriticEngine
from reasoning.verification_engine import VerificationEngine
from reasoning.recovery_engine import RecoveryEngine
from reasoning.meta_reasoning import MetaReasoningEngine

class ReasoningEngine:
    """
    Central Autonomous Reasoning & Self-Reflection Engine for AgentX (Phase 6 Cognitive Core).
    Coordinates reasoning mode selection, uncertainty tracking, decision ranking,
    continuous reflection, adversarial criticism, verification, adaptive recovery, and explainability.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ReasoningEngine, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return

        self.strategy_manager = ReasoningStrategyManager()
        self.uncertainty_engine = UncertaintyEngine()
        self.decision_engine = DecisionEngine()
        self.reflection_engine = ReflectionEngine()
        self.critic_engine = CriticEngine()
        self.verification_engine = VerificationEngine()
        self.recovery_engine = RecoveryEngine()
        self.meta_reasoning = MetaReasoningEngine()
        self._initialized = True
        logger.info("ReasoningEngine: Central Autonomous Reasoning & Self-Reflection Engine initialized.")

    async def process_mission_cognition(self, context: Any) -> Any:
        """
        Executes full cognitive reasoning, uncertainty estimation, reflection audit,
        criticism, verification, and updates MissionContext.
        """
        goal_title = getattr(context, "title", "Mission Goal")
        domain_category = getattr(context, "mission_type", "general")
        complexity_score = getattr(context, "execution_metadata", {}).get("complexity_score", 5)

        logger.info(f"ReasoningEngine: Initiating cognitive reasoning pipeline for goal '{goal_title}'...")

        # 1. Select Reasoning Mode & Generate Reasoning Trace
        mode = self.strategy_manager.select_mode(goal_title, complexity_score, domain_category)
        reasoning_trace = self.strategy_manager.generate_reasoning_trace(mode, goal_title)

        # 2. Uncertainty & Risk Estimation
        memories = getattr(context, "memory", {}).get("user_memories", [])
        tool_results = getattr(context, "tool_results", {})
        agent_outputs = getattr(context, "agent_outputs", {})
        uncertainty_metrics = self.uncertainty_engine.estimate_uncertainty(goal_title, memories, tool_results, agent_outputs)

        # 3. Continuous Self-Reflection Audit
        reflections = []
        for step_name, output in agent_outputs.items():
            reflection = self.reflection_engine.reflect_on_step(step_name, output, context.to_dict() if hasattr(context, "to_dict") else {})
            reflections.append(reflection)

        # 4. Adversarial Critic Audit
        critiques = []
        for agent_name, output in agent_outputs.items():
            critique = self.critic_engine.evaluate_output_critique(agent_name, output)
            critiques.append(critique)

        # 5. Mission Completeness Verification
        tasks = getattr(context, "tasks", [])
        verification_report = self.verification_engine.verify_mission_completeness(goal_title, tasks, agent_outputs)

        # 6. Meta-Reasoning & Explainability Trace
        explainability_trace = self.meta_reasoning.generate_explainability_trace(
            goal_title=goal_title,
            reasoning_mode=mode.value,
            confidence_metrics=uncertainty_metrics,
            reflections=reflections
        )

        # Record Cognitive State into MissionContext
        if hasattr(context, "reasoning_metadata"):
            context.reasoning_metadata.update({
                "reasoning_mode": mode.value,
                "reasoning_trace": reasoning_trace,
                "uncertainty_metrics": uncertainty_metrics,
                "reflection_logs": reflections,
                "critic_feedback": critiques,
                "verification_report": verification_report,
                "explainability_trace": explainability_trace
            })

        logger.info(f"ReasoningEngine: Cognitive processing complete for '{goal_title}' (Mode: {mode.value})")
        return context
