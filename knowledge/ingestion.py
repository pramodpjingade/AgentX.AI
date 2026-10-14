import time
import hashlib
from typing import Dict, Any, Optional
from loguru import logger

class IngestionEngine:
    """
    Ingestion Engine for AgentX (Phase 7 Enterprise Knowledge Platform).
    Handles document import, metadata normalization, SHA-256 duplicate detection,
    version tracking, and ingestion reporting.
    """

    def __init__(self):
        # document_hash -> metadata dict
        self._doc_hashes: Dict[str, Dict[str, Any]] = {}
        logger.info("IngestionEngine: Enterprise Document Ingestion Engine initialized.")

    def ingest(
        self,
        doc_id: str,
        content: str,
        source_name: str = "raw_document",
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Ingests, validates, normalizes, and versions an incoming document."""
        now = time.time()
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

        is_duplicate = content_hash in self._doc_hashes
        version = (self._doc_hashes.get(content_hash, {}).get("version", 0) + 1) if is_duplicate else 1

        normalized_metadata = metadata or {}
        normalized_metadata.update({
            "doc_id": doc_id,
            "source_name": source_name,
            "user_id": user_id or "global",
            "content_hash": content_hash,
            "is_duplicate": is_duplicate,
            "version": version,
            "ingested_at": now,
            "char_count": len(content)
        })

        self._doc_hashes[content_hash] = normalized_metadata
        logger.info(f"IngestionEngine: Ingested document '{doc_id}' (Source: '{source_name}', Version: {version}, Dup: {is_duplicate})")

        return {
            "doc_id": doc_id,
            "content": content,
            "metadata": normalized_metadata
        }
