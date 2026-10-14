import uuid
from typing import Dict, Any, List, Optional
from loguru import logger

from knowledge.ingestion import IngestionEngine
from knowledge.parser import ParserEngine
from knowledge.chunking import ChunkingEngine
from knowledge.embedding import EmbeddingEngine
from knowledge.vector_storage import VectorStorageManager
from knowledge.enterprise_graph import EnterpriseKnowledgeGraph
from knowledge.security import KnowledgeSecurityManager
from knowledge.hybrid_retrieval import HybridRetrievalEngine
from knowledge.ranking import KnowledgeRankingEngine
from core.event_bus.event_bus import EventBus
from core.event_bus.events import AgentMessageEnvelope

class KnowledgePlatform:
    """
    Central Enterprise Knowledge Intelligence Platform for AgentX (Phase 7 Knowledge OS Core).
    Serves as the single unified gateway for document ingestion, multi-format parsing,
    intelligent chunking, multi-provider embeddings, vector/graph indexing, security filtering,
    hybrid retrieval, ranking, and EventBus lifecycle events.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(KnowledgePlatform, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return

        self.ingestion = IngestionEngine()
        self.parser = ParserEngine()
        self.chunker = ChunkingEngine()
        self.embedding = EmbeddingEngine()
        self.vector_store = VectorStorageManager()
        self.graph = EnterpriseKnowledgeGraph()
        self.security = KnowledgeSecurityManager()
        self.retrieval = HybridRetrievalEngine()
        self.ranking = KnowledgeRankingEngine()
        self.event_bus = EventBus()

        self._initialized = True
        logger.info("KnowledgePlatform: Enterprise Knowledge Intelligence Platform initialized.")

    async def ingest_document(
        self,
        doc_id: str,
        content: str,
        source_name: str = "raw_doc",
        format_type: str = "txt",
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ingests, parses, chunks, generates embeddings, indexes in vector/graph stores,
        and publishes EventBus knowledge lifecycle events.
        """
        # 1. Ingestion & Versioning
        ingested = self.ingestion.ingest(doc_id, content, source_name, user_id, metadata)

        # Publish KnowledgeSourceAdded
        await self.event_bus.publish(
            "knowledge.source_added",
            AgentMessageEnvelope(
                source_agent="knowledge_platform",
                target_agent="gateway",
                event_type="KnowledgeSourceAdded",
                correlation_id=doc_id,
                payload={"doc_id": doc_id, "source_name": source_name}
            )
        )

        # 2. Parsing
        parsed = self.parser.parse(content, format_type)

        # 3. Chunking
        chunks = self.chunker.chunk_document(doc_id, parsed["text"])

        # 4. Embeddings & Vector Storage
        for chunk in chunks:
            vector = self.embedding.generate_embedding(chunk["content"])
            chunk_meta = ingested["metadata"].copy()
            chunk_meta.update(chunk)

            await self.vector_store.upsert_chunk(chunk["chunk_id"], vector, chunk_meta)

            # Publish EmbeddingCreated event
            await self.event_bus.publish(
                "knowledge.embedding_created",
                AgentMessageEnvelope(
                    source_agent="knowledge_platform",
                    target_agent="gateway",
                    event_type="EmbeddingCreated",
                    correlation_id=chunk["chunk_id"],
                    payload={"chunk_id": chunk["chunk_id"], "doc_id": doc_id}
                )
            )

        # 5. Enterprise Knowledge Graph Node & Edges
        self.graph.add_node(doc_id, source_name, "document", ingested["metadata"])
        if user_id:
            self.graph.add_node(user_id, f"User_{user_id[:6]}", "person")
            self.graph.add_edge(user_id, "OWNS_DOCUMENT", doc_id)

        # Publish KnowledgeIndexed
        await self.event_bus.publish(
            "knowledge.indexed",
            AgentMessageEnvelope(
                source_agent="knowledge_platform",
                target_agent="gateway",
                event_type="KnowledgeIndexed",
                correlation_id=doc_id,
                payload={"doc_id": doc_id, "chunks_count": len(chunks)}
            )
        )

        logger.info(f"KnowledgePlatform: Fully indexed document '{doc_id}' ({len(chunks)} chunks).")
        return {
            "doc_id": doc_id,
            "chunks_indexed": len(chunks),
            "metadata": ingested["metadata"]
        }

    async def retrieve_knowledge(
        self,
        query: str,
        user_id: Optional[str] = None,
        user_roles: Optional[List[str]] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Performs enterprise hybrid retrieval: vector search + BM25 + graph traversal + security filter + reranking.
        """
        # 1. Hybrid Search
        raw_results = await self.retrieval.execute_hybrid_search(
            query=query,
            vector_store=self.vector_store,
            embedding_engine=self.embedding,
            knowledge_graph=self.graph,
            user_id=user_id,
            top_k=top_k * 2
        )

        # 2. Security Permission Filtering
        permitted = self.security.filter_permitted_results(raw_results, user_id=user_id, user_roles=user_roles)

        # 3. Knowledge Reranking
        ranked_results = self.ranking.rerank(permitted)
        final_results = ranked_results[:top_k]

        # 4. Publish RetrievalCompleted event
        await self.event_bus.publish(
            "knowledge.retrieval_completed",
            AgentMessageEnvelope(
                source_agent="knowledge_platform",
                target_agent="gateway",
                event_type="RetrievalCompleted",
                correlation_id=str(uuid.uuid4()),
                payload={"query": query, "results_count": len(final_results)}
            )
        )

        return final_results
