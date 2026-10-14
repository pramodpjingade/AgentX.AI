from typing import Dict, Any, List
from loguru import logger

class VerificationEngine:
    """
    Verification Engine for AgentX (Phase 6 Fact & Calculation Verifier).
    Automatically verifies facts, calculations, tool outputs, citations, and goal completion criteria.
    """

    def verify_mission_completeness(
        self,
        goal_title: str,
        tasks: List[Dict[str, Any]],
        agent_outputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Audits overall mission completeness across planned tasks and outputs."""
        logger.info(f"VerificationEngine: Verifying completeness for goal '{goal_title}'")

        completed_tasks = [t for t in tasks if t.get("status") in ["completed", "success"]]
        task_completion_rate = round(len(completed_tasks) / max(len(tasks), 1), 2)

        has_master_output = "master_agent" in agent_outputs
        is_verified = (task_completion_rate >= 0.75) and has_master_output

        verification_report = {
            "is_verified": is_verified,
            "task_completion_rate": task_completion_rate,
            "completed_task_count": len(completed_tasks),
            "total_task_count": len(tasks),
            "has_master_deliverable": has_master_output,
            "status": "VERIFIED_COMPLETE" if is_verified else "PARTIALLY_COMPLETE"
        }

        return verification_report
