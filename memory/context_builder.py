from typing import Dict, Any, List, Optional
from loguru import logger

class ContextBuilder:
    """
    Context Builder Engine for AgentX.
    Assembles hybrid vector search results, knowledge graph triples, user digital twin profiles,
    and recent conversations into optimal context windows for agents.
    """

    def __init__(self):
        logger.info("ContextBuilder: Mission Context Optimizer initialized.")

    def assemble_context(
        self,
        goal_title: str,
        user_twin: Dict[str, Any],
        relevant_memories: List[Dict[str, Any]],
        graph_triples: List[Dict[str, Any]],
        max_tokens: int = 4000
    ) -> Dict[str, Any]:
        """
        Assembles and compresses memories, knowledge graph nodes, and twin profiles into a unified context payload.
        """
        formatted_memories = [m.get("content", "") for m in relevant_memories if m.get("content")]
        formatted_knowledge = [
            f"({t.get('source')} --[{t.get('relation')}]--> {t.get('target')})"
            for t in graph_triples if isinstance(t, dict)
        ]

        compressed_rag_context = "\n".join(formatted_memories[:5])
        compressed_graph_context = "\n".join(formatted_knowledge[:5])

        context_payload = {
            "query": goal_title,
            "digital_twin": user_twin,
            "user_preferences": user_twin.get("learned_preferences", []),
            "user_memories": formatted_memories,
            "rag_context": compressed_rag_context,
            "knowledge_graph_triples": compressed_graph_context,
            "context_built_at": logger.now().isoformat() if hasattr(logger, "now") else ""
        }

        logger.info(f"ContextBuilder: Assembled context for goal '{goal_title}' ({len(formatted_memories)} memories, {len(graph_triples)} graph triples).")
        return context_payload
