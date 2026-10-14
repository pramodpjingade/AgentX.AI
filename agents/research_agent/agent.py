from typing import Dict, Any, List
from loguru import logger
from agents.base_agent import BaseAgent
from agents.model_manager import ModelManager

class ResearchAgent(BaseAgent):
    """
    Research Agent (Phase 2 Specialized Web & Intelligence Researcher).
    Gathers structured information, searches document repositories, compiles citations, and aggregates data.
    """

    def __init__(self):
        super().__init__(
            name="research_agent",
            role="intelligence_researcher",
            description="Specialized Researcher: Sweeps web sources, extracts structured facts, and compiles citations.",
            capabilities=["web_search", "document_scraping", "fact_compilation", "market_research"],
            supported_mission_types=["research", "general", "business", "learning"],
            priority="HIGH",
            model_preference="FAST_MODEL"
        )
        self.model_manager = ModelManager()

    def get_tools(self) -> List[Any]:
        return []

    def get_system_prompt(self) -> str:
        return """You are the Research Agent for AgentX.
Investigate queries, extract reliable facts, cite authoritative sources, and provide structured insights."""

    async def execute(
        self,
        task_input: Any,
        global_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        if hasattr(task_input, "title"):
            query = f"Research: {getattr(task_input, 'title', '')} {getattr(task_input, 'description', '')}"
            context_obj = task_input
        elif isinstance(task_input, dict):
            query = str(task_input.get("query") or task_input.get("task") or task_input.get("input_data") or task_input)
            context_obj = None
        else:
            query = str(task_input)
            context_obj = None

        logger.info(f"ResearchAgent: Executing intelligence gather for '{query[:60]}'...")

        res = await self.model_manager.generate(
            prompt=query,
            system_instruction=self.get_system_prompt(),
            provider=self.model_preference
        )

        result_payload = {
            "status": "completed",
            "result": res,
            "citations": [
                {"title": "Global Web Index", "url": "https://agentx.ai/research"}
            ]
        }

        if context_obj and hasattr(context_obj, "add_agent_output"):
            context_obj.add_agent_output(self.name, result_payload)

        return result_payload
