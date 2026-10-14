from typing import Dict, Any, List
from loguru import logger
from agents.base_agent import BaseAgent
from agents.model_manager import ModelManager

class CodingAgent(BaseAgent):
    """
    Coding Agent (Phase 2 Specialized Software Engineer).
    Generates high-quality code, refactors scripts, conducts linting, and designs API structures.
    """

    def __init__(self):
        super().__init__(
            name="coding_agent",
            role="software_engineer",
            description="Specialized Software Engineer: Generates clean, robust, multi-language code and architectures.",
            capabilities=["code_generation", "linting", "debugging", "refactoring", "software_architecture"],
            supported_mission_types=["coding", "general"],
            priority="HIGH",
            model_preference="CODING_MODEL"
        )
        self.model_manager = ModelManager()

    def get_tools(self) -> List[Any]:
        return []

    def get_system_prompt(self) -> str:
        return """You are the Coding Agent for AgentX.
Generate production-ready code, complete with error handling, proper imports, and modern best practices."""

    async def execute(
        self,
        task_input: Any,
        global_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        if hasattr(task_input, "title"):
            prompt_text = f"Goal: {getattr(task_input, 'title', '')}\n{getattr(task_input, 'description', '')}"
            context_obj = task_input
        elif isinstance(task_input, dict):
            prompt_text = str(task_input.get("query") or task_input.get("instructions") or task_input.get("input_data") or task_input)
            context_obj = None
        else:
            prompt_text = str(task_input)
            context_obj = None

        logger.info(f"CodingAgent: Generating code implementation for '{prompt_text[:60]}'...")

        res = await self.model_manager.generate(
            prompt=prompt_text,
            system_instruction=self.get_system_prompt(),
            provider=self.model_preference
        )

        result_payload = {
            "status": "completed",
            "result": res,
            "code_snippets": [res]
        }

        if context_obj and hasattr(context_obj, "add_agent_output"):
            context_obj.add_agent_output(self.name, result_payload)

        return result_payload
