from typing import Dict, Any, List
from loguru import logger
from agents.base_agent import BaseAgent
from agents.master_agent.config import MasterAgentConfig
from agents.master_agent.prompts import SYSTEM_INSTRUCTION
from agents.master_agent.tools import MasterAgentTools
from agents.master_agent.memory import MasterAgentMemory
from agents.model_manager import ModelManager

class MasterAgent(BaseAgent):
    """
    Master Agent (Phase 2 AI Director / CEO).
    The single authoritative component allowed to formulate the final user response.
    Merges subtask outputs, resolves conflicts, removes duplicate information,
    rewrites naturally, and generates Markdown, JSON, tables, cards, artifacts, citations, and follow-ups.
    """
    
    def __init__(self):
        super().__init__(
            name="master_agent",
            role="ai_director",
            description="AI Director: Consolidates subtask outputs into cohesive user deliverables.",
            capabilities=["synthesis", "coordination", "final_response_generation", "deliverable_formulation"],
            supported_mission_types=["general", "travel", "coding", "research", "learning", "business", "fitness"],
            priority="HIGH",
            model_preference="REASONING_MODEL"
        )
        self.config = MasterAgentConfig()
        self.model_manager = ModelManager()
        self.memory = MasterAgentMemory()
        self.tools = MasterAgentTools()

    async def execute(
        self, 
        task_input: Any, 
        global_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Consolidates all subtask execution outputs into a cohesive final goal deliverable.
        """
        if hasattr(task_input, "title"):
            goal_id = getattr(task_input, "goal_id", "goal-uuid")
            goal_title = getattr(task_input, "title", "Unknown Goal")
            goal_desc = getattr(task_input, "description", "")
            subtasks_results = getattr(task_input, "agent_outputs", {})
            user_mem = getattr(task_input, "memory", {})
            context_obj = task_input
        elif isinstance(task_input, dict):
            goal_id = task_input.get("goal_id", "goal-uuid")
            goal_title = task_input.get("goal_title") or task_input.get("title", "Unknown Goal")
            goal_desc = task_input.get("description", "")
            subtasks_results = task_input.get("results") or task_input.get("agent_outputs", {})
            user_mem = global_context or {}
            context_obj = None
        else:
            goal_id = "goal-uuid"
            goal_title = str(task_input)
            goal_desc = ""
            subtasks_results = {}
            user_mem = global_context or {}
            context_obj = None

        logger.info(f"MasterAgent: Synthesizing final operating system answer for goal '{goal_title}'...")

        # Build prompt to consolidate subtask outputs
        prompt = f"Goal: '{goal_title}'\nDescription: {goal_desc}\n\n"
        prompt += "Below are the individual execution results from specialized agents:\n\n"
        
        for agent_name, output in subtasks_results.items():
            if agent_name in ["supervisor_agent", "planning_agent", "router_agent"]:
                continue  # Skip internal orchestration metadata from body text
            prompt += f"--- Agent Result ({agent_name}) ---\n"
            if isinstance(output, dict):
                res_str = output.get('result') or output.get('audit_summary') or str(output)
            else:
                res_str = str(output)
            prompt += f"{res_str}\n\n"
            
        prompt += """Synthesize this into a polished, comprehensive answer.
Format with clean Markdown, key takeaways, tables or structured blocks where appropriate, citations if applicable, and follow-up recommendations."""
        
        # Generate result using unified Model Management Layer
        consolidated_output = await self.model_manager.generate(
            prompt=prompt,
            system_instruction=self.get_system_prompt(),
            provider="master_agent"
        )

        # Extract first paragraph as summary if available
        summary_lines = [line.strip() for line in consolidated_output.split("\n") if line.strip() and not line.startswith("#")]
        summary = summary_lines[0] if summary_lines else f"Completed mission synthesis for '{goal_title}'."

        # Save trace to episodic memory
        self.memory.add_episode(
            task_id=goal_id,
            action="consolidate_goal_results",
            result=consolidated_output
        )

        # Generate follow-up suggestions
        follow_up_suggestions = [
            f"Explore further customization for {goal_title}",
            "Export deliverable as PDF / Code Bundle",
            "Schedule automated recurring execution"
        ]

        result_payload = {
            "status": "completed",
            "result": consolidated_output,
            "markdown_output": consolidated_output,
            "summary": summary,
            "raw_agent_outputs": subtasks_results,
            "follow_up_suggestions": follow_up_suggestions,
            "citations": [
                {"title": "AgentX Knowledge Index", "url": "https://agentx.ai/docs"}
            ]
        }

        if context_obj and hasattr(context_obj, "add_agent_output"):
            context_obj.add_agent_output(self.name, result_payload)

        return result_payload

    def get_tools(self) -> List[Any]:
        """Return tools available to Master Agent."""
        return self.tools.get_tools_list()

    def get_system_prompt(self) -> str:
        """Return Master Agent system prompt instructions."""
        return SYSTEM_INSTRUCTION
