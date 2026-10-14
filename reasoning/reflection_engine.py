from typing import Dict, Any, List
from loguru import logger

class ReflectionEngine:
    """
    Reflection Engine for AgentX (Phase 6 Continuous Self-Reflection Core).
    Audits step outputs throughout mission execution, detects inconsistencies,
    improves intermediate deliverables, and triggers dynamic replanning if necessary.
    """

    def reflect_on_step(
        self,
        step_name: str,
        step_output: Any,
        context_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Conducts self-reflection audit on a completed execution step."""
        logger.info(f"ReflectionEngine: Conducting self-reflection on step '{step_name}'")

        out_str = str(step_output)
        inconsistencies = []
        improvements = []
        requires_replanning = False

        if not out_str or out_str.strip() == "":
            inconsistencies.append("Step output was empty.")
            requires_replanning = True
        elif "error" in out_str.lower() or "failed" in out_str.lower():
            inconsistencies.append("Step output indicates execution failure.")
            improvements.append("Consider fallback tool or alternative model adapter.")
            requires_replanning = True

        reflection_summary = {
            "step_name": step_name,
            "passed_reflection": len(inconsistencies) == 0,
            "inconsistencies_detected": inconsistencies,
            "suggested_improvements": improvements,
            "requires_replanning": requires_replanning,
            "reflection_audit_log": f"Reflection audit for '{step_name}': Passed={len(inconsistencies) == 0}"
        }

        return reflection_summary
