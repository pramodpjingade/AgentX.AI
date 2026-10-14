from typing import Dict, Any, List
from loguru import logger

class MemoryRouter:
    """
    Memory Router for AgentX (Phase 4 Cognitive Router).
    Inspects incoming memory content, intent, and tags to route memories automatically
    into one of 10 memory categories:
    1. Working Memory (Short-lived, active mission)
    2. Conversation Memory (Multi-session history)
    3. Long-Term Memory (Persistent cross-session)
    4. Episodic Memory (Missions, achievements, failures)
    5. Semantic Memory (Facts, definitions, knowledge)
    6. Procedural Memory (Workflows, how-to, automation)
    7. Preference Memory (Theme, tools, tone, style)
    8. Agent Memory (Operational agent state)
    9. Organizational Memory (Teams, projects, departments)
    10. Tool Memory (API history, cached tool outputs)
    """

    MEMORY_CATEGORIES = [
        "working", "conversation", "long_term", "episodic",
        "semantic", "procedural", "preference", "agent",
        "organizational", "tool"
    ]

    def route_memory(self, content: str, metadata: Dict[str, Any]) -> str:
        """Determines the appropriate memory category for storage."""
        explicit_cat = metadata.get("category") or metadata.get("memory_type")
        if explicit_cat and explicit_cat.lower() in self.MEMORY_CATEGORIES:
            return explicit_cat.lower()

        content_lower = content.lower()

        # Keyword / Heuristic Routing Rules
        if any(w in content_lower for w in ["like", "prefer", "favorite", "style", "tone", "always use", "never use"]):
            return "preference"
        elif any(w in content_lower for w in ["how to", "step 1", "workflow", "procedure", "automation", "script to"]):
            return "procedural"
        elif any(w in content_lower for w in ["mission completed", "achievement", "failed", "retried", "lesson learned"]):
            return "episodic"
        elif any(w in content_lower for w in ["team", "department", "org", "company policy", "shared project"]):
            return "organizational"
        elif any(w in content_lower for w in ["api result", "cached", "tool output", "downloaded file"]):
            return "tool"
        elif any(w in content_lower for w in ["definition", "fact", "concept", "is a", "refers to"]):
            return "semantic"
        elif any(w in content_lower for w in ["agent output", "internal state", "subtask result"]):
            return "agent"
        elif metadata.get("session_id") or "user:" in content_lower or "system:" in content_lower:
            return "conversation"
        elif metadata.get("temporary"):
            return "working"
        else:
            return "long_term"
