from typing import Dict, Any, List, Optional
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
    Ensures internal agent names, task IDs, and raw execution dictionaries are NEVER exposed to the user.
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

        # Extract substantive subtask contents while filtering internal infrastructure metadata
        substantive_findings = []
        failed_tasks = []

        internal_agents = {
            "supervisor_agent", "planning_agent", "router_agent", 
            "safety_agent", "governance_layer", "fact_verification_agent", "evaluator_agent"
        }

        for agent_name, output in subtasks_results.items():
            if isinstance(output, dict):
                status = output.get("status", "")
                if status == "failed":
                    failed_tasks.append(f"{agent_name}: {output.get('result', 'Task execution failure')}")
                    continue

                res_str = output.get("result") or output.get("markdown_output") or output.get("output")
                if not res_str and output.get("deliverable"):
                    deliv = output["deliverable"]
                    res_str = deliv.get("content") or deliv.get("summary") if isinstance(deliv, dict) else str(deliv)

                if res_str and agent_name not in internal_agents:
                    substantive_findings.append(str(res_str).strip())
            elif isinstance(output, str) and output.strip():
                if agent_name not in internal_agents:
                    substantive_findings.append(output.strip())

        # Build clean synthesis prompt
        prompt = f"Goal: '{goal_title}'\n"
        if goal_desc:
            prompt += f"Description: {goal_desc}\n\n"

        if substantive_findings:
            prompt += "Findings and deliverables produced by execution:\n\n"
            for idx, finding in enumerate(substantive_findings, 1):
                prompt += f"--- Finding {idx} ---\n{finding}\n\n"
        else:
            prompt += f"Please generate a comprehensive, polished deliverable for: '{goal_title}'.\n"

        if failed_tasks:
            prompt += f"\nNote: The following operations reported issues: {'; '.join(failed_tasks)}. Account for this gracefully without alarming the user.\n"

        prompt += """\nInstructions:
Synthesize this into a cohesive, user-facing final deliverable in clean Markdown.
- Provide direct, thorough, articulate answers.
- Format all code with correct syntax highlighting (e.g. ```c, ```python).
- Use organized sections, tables, or bullet points where appropriate.
- NEVER include internal agent names (e.g. 'coding_agent', 'safety_agent'), internal dictionaries, task status codes, or raw JSON in your response."""

        # Generate result using unified Model Management Layer with REASONING_MODEL
        try:
            consolidated_output = await self.model_manager.generate(
                prompt=prompt,
                system_instruction=self.get_system_prompt(),
                provider="REASONING_MODEL",
                task_id=str(goal_id)
            )
        except Exception as e:
            logger.error(f"MasterAgent: ModelManager generation error: {e}")
            if substantive_findings:
                consolidated_output = "\n\n".join(substantive_findings)
            else:
                consolidated_output = f"I have processed your request for **{goal_title}**."

        # Extract first non-heading line as summary
        summary_lines = [
            line.strip() for line in consolidated_output.split("\n") 
            if line.strip() and not line.startswith("#") and not line.startswith("*") and not line.startswith("`")
        ]
        summary = summary_lines[0] if summary_lines else f"Completed mission synthesis for '{goal_title}'."

        # Save trace to episodic memory
        try:
            self.memory.add_episode(
                task_id=goal_id,
                action="consolidate_goal_results",
                result=consolidated_output
            )
        except Exception as mem_err:
            logger.debug(f"MasterAgent memory episode note: {mem_err}")

        # Follow-up suggestions
        follow_up_suggestions = [
            f"Explore further customization for {goal_title}",
            "Export deliverable as Markdown / Code Bundle",
            "Refine specific sections of this plan"
        ]

        result_payload = {
            "status": "completed" if not failed_tasks or substantive_findings else "failed",
            "result": consolidated_output,
            "markdown_output": consolidated_output,
            "summary": summary,
            "raw_agent_outputs": subtasks_results,
            "follow_up_suggestions": follow_up_suggestions,
            "citations": []
        }

        if context_obj and hasattr(context_obj, "add_agent_output"):
            context_obj.add_agent_output(self.name, result_payload)

        return result_payload

    def get_tools(self) -> List[Any]:
        """Return tools available to Master Agent."""
        return self.tools.get_tools_list()

    def get_system_prompt(self) -> str:
        """Return Master Agent system prompt instructions."""
        return """You are the Master Agent and AI Director for AgentX.
Your role is to synthesize complex outputs into a single, cohesive, authoritative deliverable for the user.
Write with clarity, professional depth, and flawless Markdown formatting.
Never output raw system dictionaries, agent tags, debug headers, or internal trace metadata."""
