from typing import Dict, Any, List
import json
from loguru import logger
from agents.base_agent import BaseAgent
from agents.model_manager import ModelManager
from agents.registry import AgentRegistry

class RouterAgent(BaseAgent):
    """
    Router Agent (Phase 2 AI Brain Dynamic Router).
    Inspects MissionContext, queries AgentRegistry by capabilities and domain suitability,
    determines parallel vs. sequential execution pathways, and provides explainable routing rationale.
    Never hardcodes routing choices.
    """

    def __init__(self):
        super().__init__(
            name="router_agent",
            role="dynamic_router",
            description="Dynamic Router: Queries AgentRegistry capabilities to select optimal execution pathways.",
            capabilities=["dynamic_routing", "capability_matching", "agent_assignment", "parallel_routing"],
            supported_mission_types=["general", "travel", "coding", "research", "learning", "business", "fitness"],
            priority="HIGH",
            model_preference="REASONING_MODEL"
        )
        self.model_manager = ModelManager()
        self.registry = AgentRegistry()

    def get_tools(self) -> List[Any]:
        return []

    def get_system_prompt(self) -> str:
        return """You are the Router Agent for AgentX.
Analyze the mission context, goal, subtasks, and available agent capabilities. Select candidate specialized agents dynamically.

Return valid JSON:
{
  "primary_agent": "agent_name",
  "recommended_agents": ["agent_1", "agent_2"],
  "parallel_groups": [["agent_1", "agent_2"]],
  "fallback_agent": "research_agent",
  "routing_rationale": "Clear explainable reason for agent selection based on capabilities."
}"""

    async def execute(
        self,
        task_input: Any,
        global_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Queries AgentRegistry to dynamically route subtasks and identify parallel execution steps.
        """
        if hasattr(task_input, "title"):
            title = getattr(task_input, "title", "")
            description = getattr(task_input, "description", "")
            mission_type = getattr(task_input, "mission_type", "general")
            tasks = getattr(task_input, "tasks", [])
            context_obj = task_input
        elif isinstance(task_input, dict):
            title = task_input.get("goal") or task_input.get("title", "")
            description = task_input.get("description", "")
            mission_type = task_input.get("mission_type", "general")
            tasks = task_input.get("tasks", [])
            context_obj = None
        else:
            title = str(task_input)
            description = ""
            mission_type = "general"
            tasks = []
            context_obj = None

        logger.info(f"RouterAgent: Inspecting registry capabilities for mission '{title}' (type: {mission_type})...")

        # 1. Query AgentRegistry dynamically based on mission domain
        available_agents = self.registry.find_agents_for_mission_type(mission_type)
        registered_list = list(self.registry.list_agents().keys())

        # Build prompt listing dynamically registered agents & capabilities
        agents_info_prompt = []
        for name in available_agents:
            meta = self.registry.get_agent_metadata(name)
            if meta:
                agents_info_prompt.append(f"- {name}: capabilities={meta.get('capabilities', [])}")

        prompt = f"""Mission Title: {title}
Mission Category: {mission_type}
Subtasks Count: {len(tasks)}

Dynamically Registered Agents:
{chr(10).join(agents_info_prompt)}

Select the optimal agents and identify independent agents that can run in parallel."""

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
            parsed = json.loads(cleaned.strip())

            primary = parsed.get("primary_agent", available_agents[0] if available_agents else "research_agent")
            recommended = parsed.get("recommended_agents", available_agents)
            parallel_groups = parsed.get("parallel_groups", [])
            fallback = parsed.get("fallback_agent", "research_agent")
            rationale = parsed.get("routing_rationale", "Selected dynamically via capability lookup.")

        except Exception as e:
            logger.warning(f"RouterAgent: Routing LLM call exception ({e}), falling back to capability registry lookup.")
            primary = available_agents[0] if available_agents else "research_agent"
            recommended = available_agents
            parallel_groups = [[a for a in available_agents if a not in ["master_agent", "supervisor_agent", "evaluator_agent"]][:2]]
            fallback = "research_agent"
            rationale = f"Dynamic registry lookup fallback for category '{mission_type}'."

        # Validate that selected agents exist in registry
        valid_recommended = [a for a in recommended if a in registered_list]
        if not valid_recommended:
            valid_recommended = [primary] if primary in registered_list else ["research_agent"]

        result_payload = {
            "status": "success",
            "primary_agent": primary if primary in registered_list else valid_recommended[0],
            "recommended_agents": valid_recommended,
            "parallel_groups": parallel_groups,
            "fallback_agent": fallback if fallback in registered_list else "research_agent",
            "explainable_routing_rationale": rationale
        }

        if context_obj and hasattr(context_obj, "add_agent_output"):
            context_obj.add_agent_output(self.name, result_payload)

        return result_payload
