import time
from typing import Dict, Any, List, Optional
from loguru import logger

class EnterpriseKnowledgeGraph:
    """
    Enterprise Knowledge Graph Engine for AgentX.
    Indexes enterprise entities (People, Organizations, Departments, Repositories, Documents, Code, Files, Events, Agents, Tools, Tasks)
    and directed relationships for multi-hop graph reasoning.
    """

    def __init__(self):
        # entity_id -> dict
        self._nodes: Dict[str, Dict[str, Any]] = {}
        # edges list
        self._edges: List[Dict[str, Any]] = []
        logger.info("EnterpriseKnowledgeGraph: Enterprise Multi-Hop Knowledge Graph initialized.")

    def add_node(self, node_id: str, name: str, node_type: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Adds or updates an enterprise entity node in the graph."""
        node = {
            "id": node_id,
            "name": name,
            "type": node_type.lower(),  # person, organization, repository, document, file, agent, tool, task
            "metadata": metadata or {},
            "created_at": time.time()
        }
        self._nodes[node_id] = node
        return node

    def add_edge(self, source_id: str, relation: str, target_id: str, weight: float = 1.0) -> Dict[str, Any]:
        """Adds a directed relationship edge between enterprise entity nodes."""
        edge = {
            "source": source_id,
            "relation": relation.upper(),  # OWNS, CONTAINS, CREATED, REFERENCES, DEPENDS_ON, EXECUTED
            "target": target_id,
            "weight": weight,
            "timestamp": time.time()
        }
        self._edges.append(edge)
        return edge

    def query_graph_neighbors(self, node_id: str, max_depth: int = 2) -> List[Dict[str, Any]]:
        """Traverses knowledge graph starting from node_id up to max_depth."""
        results = []
        visited = set()

        def _traverse(curr_id: str, depth: int):
            if depth <= 0 or curr_id in visited:
                return
            visited.add(curr_id)

            for e in self._edges:
                if e["source"] == curr_id:
                    src_node = self._nodes.get(curr_id)
                    tgt_node = self._nodes.get(e["target"])
                    results.append({
                        "source": src_node["name"] if src_node else curr_id,
                        "relation": e["relation"],
                        "target": tgt_node["name"] if tgt_node else e["target"]
                    })
                    _traverse(e["target"], depth - 1)

        _traverse(node_id, max_depth)
        return results
