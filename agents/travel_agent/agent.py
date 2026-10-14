from typing import Dict, Any, List
from loguru import logger
from agents.base_agent import BaseAgent
from agents.model_manager import ModelManager

class TravelAgent(BaseAgent):
    """
    Travel Agent (Phase 2 Specialized Itinerary & Logistics Specialist).
    Plans travel routes, compiles day-by-day itineraries, checks lodging/hotels, and analyzes weather.
    """

    def __init__(self):
        super().__init__(
            name="travel_agent",
            role="travel_concierge",
            description="Specialized Travel Concierge: Crafts curated itineraries, accommodation picks, and route plans.",
            capabilities=["route_planning", "itinerary_generation", "hotel_booking", "weather_forecast", "budget_estimation"],
            supported_mission_types=["travel", "general"],
            priority="NORMAL",
            model_preference="FAST_MODEL"
        )
        self.model_manager = ModelManager()

    def get_tools(self) -> List[Any]:
        return []

    def get_system_prompt(self) -> str:
        return """You are the Travel Agent for AgentX.
Craft rich, day-by-day travel experiences complete with lodging options, scenic highlights, local dining, packing tips, and estimated budgets."""

    async def execute(
        self,
        task_input: Any,
        global_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        if hasattr(task_input, "title"):
            prompt_text = f"Destination/Goal: {getattr(task_input, 'title', '')} {getattr(task_input, 'description', '')}"
            context_obj = task_input
        elif isinstance(task_input, dict):
            prompt_text = str(task_input.get("query") or task_input.get("destination") or task_input.get("input_data") or task_input)
            context_obj = None
        else:
            prompt_text = str(task_input)
            context_obj = None

        logger.info(f"TravelAgent: Formulating travel itinerary for '{prompt_text[:60]}'...")

        res = await self.model_manager.generate(
            prompt=prompt_text,
            system_instruction=self.get_system_prompt(),
            provider=self.model_preference
        )

        result_payload = {
            "status": "completed",
            "result": res,
            "category": "travel"
        }

        if context_obj and hasattr(context_obj, "add_agent_output"):
            context_obj.add_agent_output(self.name, result_payload)

        return result_payload
