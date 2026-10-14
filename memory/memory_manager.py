import time
import uuid
from typing import Dict, Any, List, Optional
from loguru import logger

from memory.vector_provider import VectorMemoryProvider
from memory.knowledge_graph import KnowledgeGraphEngine
from memory.memory_router import MemoryRouter
from memory.importance_scorer import MemoryImportanceScorer
from memory.forgetting_engine import ForgettingEngine
from memory.personalization import PersonalizationEngine
from memory.context_builder import ContextBuilder
from core.event_bus.event_bus import EventBus
from core.event_bus.events import AgentMessageEnvelope

class MemoryManager:
    """
    Central Cognitive Memory Manager for AgentX (Phase 4 Cognitive Brain Core).
    Serves as the single unified entrypoint for storing, retrieving, ranking,
    graph indexing, personalizing, forgetting, and building context across all 10 memory categories.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MemoryManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return

        self.vector_provider = VectorMemoryProvider()
        self.knowledge_graph = KnowledgeGraphEngine()
        self.router = MemoryRouter()
        self.importance_scorer = MemoryImportanceScorer()
        self.forgetting_engine = ForgettingEngine()
        self.personalization = PersonalizationEngine()
        self.context_builder = ContextBuilder()
        self.event_bus = EventBus()

        # In-memory storage for active session nodes: memory_id (str) -> dict
        self._memory_store: Dict[str, Dict[str, Any]] = {}
        self._initialized = True
        logger.info("MemoryManager: Central Cognitive Memory Manager initialized.")

    async def store_memory(
        self,
        content: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ttl_seconds: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Stores a memory node, automatically routes to memory category, generates vector embedding,
        indexes entity nodes in Knowledge Graph, and publishes MemoryCreated event.
        """
        meta = metadata or {}
        memory_id = str(uuid.uuid4())
        category = self.router.route_memory(content, meta)
        embedding = self.vector_provider.generate_embedding(content)
        now = time.time()

        memory_node = {
            "id": memory_id,
            "user_id": user_id or "global",
            "content": content,
            "category": category,
            "memory_type": category,
            "embedding": embedding,
            "metadata": meta,
            "ttl_seconds": ttl_seconds,
            "access_count": 1,
            "created_at_ts": now,
            "importance_score": 1.0
        }

        self._memory_store[memory_id] = memory_node

        # Index entity node in Knowledge Graph
        if user_id:
            self.knowledge_graph.add_entity(user_id, f"User_{user_id[:6]}", "person")
            self.knowledge_graph.add_entity(memory_id, f"Memory_{category}", "concept", {"content": content[:40]})
            self.knowledge_graph.add_relationship(user_id, "HAS_MEMORY", memory_id)

        # Publish MemoryCreated Event
        await self.event_bus.publish(
            "memory.created",
            AgentMessageEnvelope(
                source_agent="memory_manager",
                target_agent="gateway",
                event_type="MemoryCreated",
                correlation_id=memory_id,
                payload={"memory_id": memory_id, "category": category, "user_id": user_id}
            )
        )

        logger.info(f"MemoryManager: Stored [{category.upper()}] memory ID '{memory_id}'")
        return memory_node

    async def retrieve_memories(
        self,
        query: str,
        user_id: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Performs hybrid memory retrieval: vector similarity + importance score ranking.
        """
        query_vector = self.vector_provider.generate_embedding(query)
        candidates = list(self._memory_store.values())

        if user_id:
            candidates = [m for m in candidates if m.get("user_id") in [user_id, "global"]]

        if category:
            candidates = [m for m in candidates if m.get("category") == category]

        # Audit and prune expired / low importance memories
        candidates = self.forgetting_engine.audit_and_prune(candidates)

        # Vector search
        scored_nodes = await self.vector_provider.search_similar(query_vector, candidates, limit=limit * 2)

        # Composite score ranking (vector score * importance score)
        for node in scored_nodes:
            v_score = node.get("vector_score", 0.5)
            imp_score = node.get("importance_score", 1.0)
            node["composite_rank_score"] = round((v_score * 0.6) + (imp_score * 0.4), 4)

            # Update access count telemetry
            original = self._memory_store.get(node["id"])
            if original:
                original["access_count"] = original.get("access_count", 1) + 1

        scored_nodes.sort(key=lambda x: x["composite_rank_score"], reverse=True)
        return scored_nodes[:limit]

    async def build_mission_context(
        self,
        user_id: Optional[str],
        goal_title: str,
        explicit_preferences: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Assembles complete mission context: digital twin, relevant vector memories, and knowledge graph triples.
        """
        user_str = user_id or "default_user"
        candidates = list(self._memory_store.values())

        # Build Digital Twin profile
        user_twin = self.personalization.build_user_twin(user_str, candidates, explicit_preferences)

        # Retrieve relevant memories
        relevant = await self.retrieve_memories(goal_title, user_id=user_str, limit=5)

        # Retrieve Knowledge Graph Triples
        graph_triples = self.knowledge_graph.query_relationships(user_str, max_depth=2)

        # Build optimized context payload
        context_payload = self.context_builder.assemble_context(
            goal_title=goal_title,
            user_twin=user_twin,
            relevant_memories=relevant,
            graph_triples=graph_triples
        )

        # Publish ContextBuilt event
        await self.event_bus.publish(
            "context.built",
            AgentMessageEnvelope(
                source_agent="memory_manager",
                target_agent="gateway",
                event_type="ContextBuilt",
                correlation_id=str(uuid.uuid4()),
                payload={"user_id": user_str, "query": goal_title}
            )
        )

        return context_payload

    async def forget_memory(self, memory_id: str) -> bool:
        """GDPR-compliant deletion of a memory by ID."""
        if memory_id in self._memory_store:
            del self._memory_store[memory_id]
            await self.event_bus.publish(
                "memory.deleted",
                AgentMessageEnvelope(
                    source_agent="memory_manager",
                    target_agent="gateway",
                    event_type="MemoryDeleted",
                    correlation_id=memory_id,
                    payload={"memory_id": memory_id}
                )
            )
            logger.info(f"MemoryManager: Deleted memory ID '{memory_id}' for GDPR compliance.")
            return True
        return False
