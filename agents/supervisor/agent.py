import json
from typing import Dict, Any, List
from loguru import logger
from agents.base_agent import BaseAgent
from agents.model_manager import ModelManager

class SupervisorAgent(BaseAgent):
    """
    Supervisor Agent (Phase 2 AI Brain Director).
    Understands user intent, classifies missions, estimates complexity, assesses risks,
    allocates token/time budgets, determines execution strategy, and identifies candidate agents.
    Never performs actual domain task execution.
    """
    
    def __init__(self):
        super().__init__(
            name="supervisor_agent",
            role="executive_director",
            description="Executive Supervisor: Classifies mission complexity, assesses risks, and crafts strategy.",
            capabilities=["intent_classification", "risk_identification", "strategy_formulation", "budget_allocation"],
            supported_mission_types=["general", "travel", "coding", "research", "learning", "business", "fitness"],
            priority="HIGH",
            model_preference="REASONING_MODEL"
        )
        self.model_manager = ModelManager()

    def get_tools(self) -> List[Any]:
        return []

    def get_system_prompt(self) -> str:
        return """You are the Executive Supervisor Agent for AgentX (AI Operating System).
Your role is purely executive coordination and risk/strategy management. You DO NOT perform actual domain work.

Analyze the user's goal, description, and context. Output valid JSON containing:
{
  "mission_category": "travel | coding | research | learning | business | fitness | general",
  "complexity_score": 1 to 10 rating,
  "intent_summary": "Clean summary of user intent",
  "execution_strategy": "High level multi-step strategy",
  "estimated_agents": ["research_agent", "travel_agent", etc.],
  "identified_risks": ["Potential API rate limits", "Validation requirement", etc.],
  "budget_allocation": {"max_tokens": 10000, "estimated_latency_s": 15},
  "status": "APPROVED"
}

Return ONLY valid JSON. No other text."""

    async def execute(
        self, 
        task_input: Any, 
        global_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Executes intent analysis and risk assessment on MissionContext or dict.
        """
        if hasattr(task_input, "title"):
            goal_title = getattr(task_input, "title", "")
            goal_desc = getattr(task_input, "description", "")
            context_obj = task_input
        elif isinstance(task_input, dict):
            goal_title = task_input.get("goal") or task_input.get("title", "")
            goal_desc = task_input.get("description", "")
            context_obj = None
        else:
            goal_title = str(task_input)
            goal_desc = ""
            context_obj = None

        logger.info(f"SupervisorAgent: Evaluating strategy & complexity for goal '{goal_title}'...")

        prompt = f"Goal Title: {goal_title}\nGoal Description: {goal_desc}"

        try:
            raw_response = await self.model_manager.generate(
                prompt=prompt,
                system_instruction=self.get_system_prompt(),
                provider=self.model_preference
            )

            cleaned = raw_response.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("```")[1]
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:]

            decision = json.loads(cleaned.strip())
        except Exception as e:
            logger.warning(f"SupervisorAgent: JSON parsing error ({e}), utilizing strategic fallback.")
            from core.orchestrator.response_composer import ResponseComposer
            category = ResponseComposer.classify_category(goal_title, goal_desc)
            decision = {
                "mission_category": category,
                "complexity_score": 5,
                "intent_summary": f"Process user request for '{goal_title}'",
                "execution_strategy": "Standard multi-agent execution pipeline",
                "estimated_agents": ["research_agent", "evaluator_agent"],
                "identified_risks": ["Standard execution verification required"],
                "budget_allocation": {"max_tokens": 8000, "estimated_latency_s": 10},
                "status": "APPROVED"
            }

        result_payload = {
            "status": "success",
            "supervisor_decision": decision,
            "mission_category": decision.get("mission_category", "general"),
            "complexity_score": decision.get("complexity_score", 5),
            "execution_strategy": decision.get("execution_strategy", ""),
            "estimated_agents": decision.get("estimated_agents", [])
        }

        if context_obj and hasattr(context_obj, "add_agent_output"):
            context_obj.add_agent_output(self.name, result_payload)
            context_obj.mission_type = decision.get("mission_category", "general")

        return result_payload
