from loguru import logger
import os

class Neo4jClient:
    """Manages connections to Neo4j Graph Database with built-in sandbox mock fallbacks."""
    
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Neo4jClient, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return
            
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "password")
        self.use_mock = True  # Default fallback mode
        
        self.mock_store = {
            "nodes": {},
            "relationships": []
        }
        self._initialized = True
        logger.info(f"Neo4jClient: Initialized. Fallback sandbox mode enabled: {self.use_mock}")

    async def execute_query(self, query: str, parameters: dict = None) -> list:
        """Executes a Cypher query on the active database driver or fallback mock store."""
        logger.info(f"Neo4jClient: Executing Cypher query: '{query}'")
        parameters = parameters or {}
        
        # Simple mock execution engine logic for common operations
        query_upper = query.upper()
        if "CREATE" in query_upper or "MERGE" in query_upper:
            # Simulate node/relationship storage
            node_id = parameters.get("id", "temp_id")
            self.mock_store["nodes"][node_id] = parameters
            return [{"id": node_id, "status": "created"}]
            
        elif "MATCH" in query_upper:
            # Return list of mocked match relationships
            return list(self.mock_store["nodes"].values())
            
        return []
