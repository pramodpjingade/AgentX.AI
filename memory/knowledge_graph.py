import time
from typing import Dict, Any, List, Optional
from loguru import logger

class KnowledgeGraphEngine:
    """
    Knowledge Graph Engine for AgentX (Phase 4 Cognitive Graph).
    Indexes entities (People, Organizations, Projects, Files, Events, Concepts, Goals, Agents, Tools, Missions)
    and their semantic relationships to enable graph-based reasoning and contextual retrieval.
    """

    def __init__(self):
        # Nodes: entity_id (str) -> dict {"id": str, "name": str, "type": str, "metadata": dict}
        self._nodes: Dict[str, Dict[str, Any]] = {}
        # Edges: list of dicts {"source": str, "relation": str, "target": str, "weight": float}
        self._edges: List[Dict[str, Any]] = []
        logger.info("KnowledgeGraphEngine: Central Knowledge Graph initialized.")

    def add_entity(self, entity_id: str, name: str, entity_type: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Adds or updates an entity node in the Knowledge Graph."""
        node = {
            "id": entity_id,
            "name": name,
            "type": entity_type.lower(),  # person, organization, project, file, goal, agent, tool, etc.
            "metadata": metadata or {},
            "updated_at": time.time()
        }
        self._nodes[entity_id] = node
        logger.info(f"KnowledgeGraphEngine: Added node [{entity_type.upper()}] '{name}' ({entity_id})")
        return node

    def add_relationship(self, source_id: str, relation: str, target_id: str, weight: float = 1.0) -> Dict[str, Any]:
        """Adds a directed relationship edge between two entity nodes."""
        edge = {
            "source": source_id,
            "relation": relation.upper(),  # PREFERS, USES, BELONGS_TO, DEPENDS_ON, CREATED, EXECUTED
            "target": target_id,
            "weight": weight,
            "timestamp": time.time()
        }
        self._edges.append(edge)
        logger.info(f"KnowledgeGraphEngine: Created edge '{source_id}' --[{relation.upper()}]--> '{target_id}'")
        return edge

    def query_relationships(self, entity_id: str, max_depth: int = 2) -> List[Dict[str, Any]]:
        """Traverses knowledge graph starting from target entity up to specified depth."""
        connected_triples = []
        visited = set()

        def _traverse(current_id: str, depth: int):
            if depth <= 0 or current_id in visited:
                return
            visited.add(current_id)

            for edge in self._edges:
                if edge["source"] == current_id:
                    target_node = self._nodes.get(edge["target"])
                    source_node = self._nodes.get(current_id)
                    connected_triples.append({
                        "source": source_node["name"] if source_node else current_id,
                        "relation": edge["relation"],
                        "target": target_node["name"] if target_node else edge["target"],
                        "weight": edge["weight"]
                    })
                    _traverse(edge["target"], depth - 1)

        _traverse(entity_id, max_depth)
        return connected_triples

    def find_entities_by_type(self, entity_type: str) -> List[Dict[str, Any]]:
        """Finds all entity nodes of a specified type."""
        type_lower = entity_type.lower()
        return [node for node in self._nodes.values() if node["type"] == type_lower]

    def to_dict(self) -> Dict[str, Any]:
        """Exports graph state snapshot."""
        return {
            "node_count": len(self._nodes),
            "edge_count": len(self._edges),
            "nodes": list(self._nodes.values()),
            "edges": self._edges
        }
