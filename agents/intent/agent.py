import json
from typing import Dict, Any, List
from loguru import logger
from agents.base_agent import BaseAgent
from agents.model_manager import ModelManager

class IntentAgent(BaseAgent):
    """Parses raw user prompts to classify intent, complexity, goals, and variables."""
    
    def __init__(self):
        super().__init__(name="intent_agent", role="intent_parser")
        self.model_manager = ModelManager()

    def get_tools(self) -> List[Any]:
        return []

    def get_system_prompt(self) -> str:
        return """You are the Intent Understanding Agent for AgentX (PAMMU AI).
Your task is to analyze user queries and output a structured JSON containing:
1. 'goal_title': A short, clear summary of the user's objective.
2. 'goal_description': Detailed goals/requirements.
3. 'complexity': Estimated complexity: 'simple', 'medium', or 'complex'.
4. 'parameters': A dictionary of key variables found (e.g. language, budget, duration, etc.).

Return ONLY valid JSON. No other text."""

    async def execute(
        self, 
        task_input: Dict[str, Any], 
        global_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Analyze the query from input and return structured intent dictionary."""
        query = task_input.get("query", "")
        logger.info(f"IntentAgent: Processing query: '{query[:50]}...'")
        
        prompt = f"Analyze this user query and output structured intent:\nQuery: {query}"
        
        # Use FAST_MODEL alias for quick classification
        response = await self.model_manager.generate(
            prompt=prompt,
            system_instruction=self.get_system_prompt(),
            provider="FAST_MODEL"
        )
        
        try:
            # Strip any markdown formatting like ```json
            cleaned_response = response.strip()
            if cleaned_response.startswith("```"):
                cleaned_response = cleaned_response.split("```")[1]
                if cleaned_response.startswith("json"):
                    cleaned_response = cleaned_response[4:]
                    
            parsed_intent = json.loads(cleaned_response.strip())
            logger.info("IntentAgent: Parsing completed successfully.")
            return {
                "status": "success",
                "intent": parsed_intent
            }
        except Exception as e:
            logger.error(f"IntentAgent: Failed to parse JSON response: {e}. Returning fallback classification.")
            # Fallback output
            return {
                "status": "success",
                "intent": {
                    "goal_title": "Direct Execution Task",
                    "goal_description": query,
                    "complexity": "simple",
                    "parameters": {}
                }
            }
