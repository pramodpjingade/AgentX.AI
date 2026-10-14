import asyncio
import os
import sys

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.knowledge_graph.graph_rag import HybridGraphRAG

async def test_sprint6_knowledge_graph():
    print("\n==================================================")
    print("RUNNING SPRINT 6 KNOWLEDGE GRAPH INTEGRATION TEST")
    print("==================================================")

    # 1. Initialize Hybrid RAG
    print("[Step 1] Initializing HybridGraphRAG engine wrapper...")
    rag_engine = HybridGraphRAG()

    # 2. Ingest Concept Nodes
    print("\n[Step 2] Ingesting relational concepts into graph store...")
    await rag_engine.ingest_concept(
        concept_id="concept_1",
        title="Multi-tenant tenant isolation",
        details="Enforces row-level schema filters matching active organization accounts."
    )
    await rag_engine.ingest_concept(
        concept_id="concept_2",
        title="NATS Streaming workers",
        details="Subscribes event workers dynamically to goal.created queues."
    )
    print("Concept nodes ingestion completed.")

    # 3. Retrieve Hybrid Context
    query = "Explain tenant isolation in AgentX"
    print(f"\n[Step 3] Querying hybrid context for: '{query}'...")
    context = await rag_engine.retrieve_hybrid_context(query)
    
    print("\nRetrieved Unified RAG Context:")
    print(context)

    # 4. Assertions
    assert "Vector Chunk:" in context, "Error: Similarity vector chunk context is missing."
    assert "Multi-tenant tenant isolation" in context, "Error: Relational concept node title is missing."
    assert "Enforces row-level" in context, "Error: Relational concept details are missing."
    print("\nKnowledge Graph hybrid RAG integrations successfully validated!")

    print("\n==================================================")
    print("SPRINT 6 INTEGRATION TEST: ALL TESTS PASSED!")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(test_sprint6_knowledge_graph())
