from typing import Dict, Any, List
from loguru import logger
from agents.base_agent import BaseAgent
from agents.model_manager import ModelManager
from core.task_manager.dag_generator import TaskDAGGenerator

class PlannerAgent(BaseAgent):
    """
    Planner Agent (Phase 2 AI Brain Project Manager).
    Decomposes high-level user goals into structured dependency graphs (DAG execution trees),
    estimates subtask costs and latencies, assigns priorities, and identifies reusable outputs.
    """

    def __init__(self):
        super().__init__(
            name="planning_agent",
            role="project_manager",
            description="Project Manager: Breaks complex goals into DAG subtask trees with cost/latency estimates.",
            capabilities=["goal_decomposition", "dag_creation", "priority_assignment", "dependency_graphing"],
            supported_mission_types=["general", "travel", "coding", "research", "learning", "business", "fitness"],
            priority="HIGH",
            model_preference="REASONING_MODEL"
        )
        self.model_manager = ModelManager()
        self.generator = TaskDAGGenerator()

    def get_tools(self) -> List[Any]:
        return []

    def get_system_prompt(self) -> str:
        return """You are the Planner Agent for AgentX.
Your responsibility is to think like an expert Senior Project Manager. Break goals into clean subtask dependency graphs (DAG), assigning candidate agents, priority levels, estimated latency, and cost bounds."""

    async def execute(
        self,
        task_input: Any,
        global_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Decomposes goal into dependency graph tasks.
        Accepts MissionContext or dict as task_input.
        """
        if hasattr(task_input, "title"):
            title = getattr(task_input, "title", "")
            description = getattr(task_input, "description", "")
            context_obj = task_input
        elif isinstance(task_input, dict):
            title = task_input.get("goal") or task_input.get("title", "")
            description = task_input.get("description", "")
            context_obj = None
        else:
            title = str(task_input)
            description = ""
            context_obj = None

        logger.info(f"PlannerAgent: Building subtask DAG execution tree for goal '{title}'...")

        tasks = await self.generator.generate_dag(title, description, self.model_manager)
        
        # Enrich subtasks with dependency graphs and estimates
        for i, t in enumerate(tasks):
            t["step_number"] = i + 1
            t["estimated_latency_s"] = t.get("estimated_execution_time", 30.0)
            t["estimated_tokens"] = t.get("estimated_token_usage", 1500)
            t["reusable_output_keys"] = ["result", "artifacts"]

        result_payload = {
            "status": "success",
            "tasks": tasks,
            "subtask_count": len(tasks),
            "total_estimated_latency_s": sum(t.get("estimated_latency_s", 30.0) for t in tasks)
        }

        if context_obj and hasattr(context_obj, "tasks"):
            context_obj.tasks = tasks
            context_obj.dependencies = [
                {"task_id": str(t.get("id")), "parent_id": str(t.get("parent_task_id")) if t.get("parent_task_id") else None}
                for t in tasks
            ]
            context_obj.add_agent_output(self.name, result_payload)

        return result_payload
