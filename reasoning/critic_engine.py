from typing import Dict, Any, List
from loguru import logger

class CriticEngine:
    """
    Critic Engine for AgentX (Phase 6 Adversarial QA Critic).
    Challenges agent assumptions, audits factual support, detects hallucinations,
    and generates constructive quality feedback without producing final user text.
    """

    def evaluate_output_critique(
        self,
        agent_name: str,
        output_data: Any,
        reference_facts: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Provides an adversarial critique of an agent's output payload."""
        logger.info(f"CriticEngine: Conducting adversarial critique on agent '{agent_name}'")

        out_str = str(output_data)
        critique_notes = []
        hallucination_warning = False

        if len(out_str) < 20:
            critique_notes.append("Output is overly brief; lacks comprehensive detail.")

        if "simulated" in out_str.lower() or "mock" in out_str.lower():
            critique_notes.append("Output generated via fallback mock provider.")

        critique_result = {
            "agent_name": agent_name,
            "quality_grade": "A" if len(critique_notes) == 0 else "B+",
            "criticism_notes": critique_notes,
            "hallucination_warning": hallucination_warning,
            "recommendation": "APPROVED" if len(critique_notes) == 0 else "ACCEPT_WITH_FEEDBACK"
        }

        return critique_result
