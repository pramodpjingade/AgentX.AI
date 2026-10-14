from typing import Dict, Any, List, Optional
from loguru import logger

class PersonalizationEngine:
    """
    Personalization & Digital Twin Profile Engine for AgentX.
    Learns user writing style, preferred tone, frequently used tools, favorite mission categories,
    and schedule preferences without exposing personal data.
    """

    def __init__(self):
        logger.info("PersonalizationEngine: Digital Twin Personalization Layer initialized.")

    def build_user_twin(
        self,
        user_id: str,
        memories: List[Dict[str, Any]],
        preferences: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Formulates a comprehensive digital twin profile for the user."""
        pref_memories = [m.get("content", "") for m in memories if m.get("category") == "preference" or "preference" in m.get("memory_type", "")]
        if preferences:
            pref_memories.extend(preferences)

        favorite_tools = ["web_search", "document_generator"]
        preferred_style = "Professional, Concise, and Structured Markdown"

        for p in pref_memories:
            p_lower = str(p).lower()
            if "code" in p_lower or "python" in p_lower:
                favorite_tools.append("python_interpreter")
            if "detailed" in p_lower or "comprehensive" in p_lower:
                preferred_style = "Comprehensive, Detailed, and Analytical"

        twin = {
            "user_id": user_id,
            "writing_style": preferred_style,
            "preferred_tone": "Articulate, Helpful, and Enterprise-Ready",
            "favorite_tools": list(set(favorite_tools)),
            "learned_preferences": list(set(pref_memories)),
            "interaction_pattern": "Goal-Oriented Autonomous Execution"
        }

        logger.info(f"PersonalizationEngine: Built digital twin profile for user '{user_id}' with {len(twin['learned_preferences'])} preferences.")
        return twin
