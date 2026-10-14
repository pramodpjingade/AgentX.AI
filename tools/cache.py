import time
import hashlib
import json
from typing import Dict, Any, Optional
from loguru import logger
from tools.base_tool import ToolResult

class ToolCache:
    """
    Intelligent In-Memory Tool Result Cache with TTL expiration for AgentX.
    Prevents redundant external API calls and optimizes response latency.
    """

    def __init__(self):
        # Key (str) -> dict {"result": ToolResult, "expires_at": float}
        self._cache: Dict[str, Dict[str, Any]] = {}
        logger.info("ToolCache: Intelligent Tool Execution Cache initialized.")

    def _generate_key(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """Generates a deterministic hash key based on tool name and serialized parameters."""
        serialized = json.dumps(parameters, sort_keys=True, default=str)
        raw_key = f"{tool_name}:{serialized}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    def get(self, tool_name: str, parameters: Dict[str, Any]) -> Optional[ToolResult]:
        """Retrieves a cached ToolResult if not expired."""
        key = self._generate_key(tool_name, parameters)
        entry = self._cache.get(key)

        if not entry:
            return None

        if time.time() > entry["expires_at"]:
            logger.info(f"ToolCache: Cache entry expired for tool '{tool_name}'")
            del self._cache[key]
            return None

        cached_res: ToolResult = entry["result"]
        cached_res.status = "cached"
        logger.info(f"ToolCache: Cache HIT for tool '{tool_name}'")
        return cached_res

    def set(self, tool_name: str, parameters: Dict[str, Any], result: ToolResult, ttl_seconds: int = 60):
        """Stores a ToolResult in cache with specified TTL."""
        if not result.success:
            return  # Do not cache failed executions

        key = self._generate_key(tool_name, parameters)
        expires_at = time.time() + ttl_seconds
        self._cache[key] = {
            "result": result,
            "expires_at": expires_at
        }
        logger.info(f"ToolCache: Cached result for tool '{tool_name}' (TTL: {ttl_seconds}s)")

    def clear(self):
        """Evicts all cached entries."""
        self._cache.clear()
        logger.info("ToolCache: Cache cleared.")
