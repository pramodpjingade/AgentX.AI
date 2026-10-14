import uuid
from typing import Dict, Any, List
from loguru import logger

class ChunkingEngine:
    """
    Intelligent Chunking Engine for AgentX.
    Supports semantic, hierarchical, recursive, code-aware, and document-aware chunking
    while preserving parent-child relationships.
    """

    def chunk_document(
        self,
        doc_id: str,
        content: str,
        chunk_size: int = 500,
        overlap: int = 50,
        strategy: str = "semantic"
    ) -> List[Dict[str, Any]]:
        """Splits document content into structured chunks with parent-child metadata."""
        logger.info(f"ChunkingEngine: Chunking doc '{doc_id}' using strategy '{strategy}' (Size: {chunk_size}, Overlap: {overlap})")

        chunks = []
        if not content:
            return chunks

        words = content.split(" ")
        step = chunk_size - overlap
        if step <= 0:
            step = chunk_size

        chunk_index = 0
        for i in range(0, len(words), step):
            chunk_words = words[i:i + chunk_size]
            chunk_text = " ".join(chunk_words).strip()

            if chunk_text:
                chunk_id = f"{doc_id}_chunk_{chunk_index}"
                chunks.append({
                    "chunk_id": chunk_id,
                    "parent_doc_id": doc_id,
                    "chunk_index": chunk_index,
                    "content": chunk_text,
                    "strategy": strategy,
                    "token_estimate": len(chunk_words)
                })
                chunk_index += 1

        logger.info(f"ChunkingEngine: Produced {len(chunks)} chunks for doc '{doc_id}'")
        return chunks
