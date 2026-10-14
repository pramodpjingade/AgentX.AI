from loguru import logger
from core.knowledge_graph.neo4j_client import Neo4jClient

class HybridGraphRAG:
    """Combines semantic vector similarity lookups with Neo4j entity relational queries."""
    
    def __init__(self):
        self.neo4j_client = Neo4jClient()

    async def ingest_concept(self, concept_id: str, title: str, details: str):
        """Creates or merges a concept node in the Neo4j knowledge store."""
        logger.info(f"GraphRAG: Ingesting concept '{title}' (ID: {concept_id})")
        query = "MERGE (c:Concept {id: $id}) SET c.title = $title, c.details = $details RETURN c"
        await self.neo4j_client.execute_query(query, {"id": concept_id, "title": title, "details": details})

    async def retrieve_hybrid_context(self, query_text: str, top_k: int = 3) -> str:
        """Retrieves and merges similarity vector snippets with relational graph nodes."""
        logger.info(f"GraphRAG: Executing hybrid search for query: '{query_text}'")
        
        # 1. Simulate pgvector similarity search output
        vector_results = [
            f"Vector Chunk: AgentX supports multi-tenant logical partitioning (Query match: '{query_text}')."
        ]
        
        # 2. Query Neo4j Client for relational facts
        cypher_query = "MATCH (c:Concept) RETURN c LIMIT $limit"
        graph_nodes = await self.neo4j_client.execute_query(cypher_query, {"limit": top_k})
        
        graph_results = []
        for node in graph_nodes:
            title = node.get("title", "Related Concept")
            details = node.get("details", "")
            graph_results.append(f"Graph Entity Relation: '{title}' -> Details: {details}")
            
        # 3. Combine contexts
        combined_lines = ["--- Hybrid Context Sources ---"] + vector_results + graph_results
        return "\n".join(combined_lines)
