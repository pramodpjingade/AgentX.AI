import asyncio
import time
from typing import Dict, Any, List, Optional
from loguru import logger

from tools.base_tool import BaseTool, ToolResult
from tools.registry import ToolRegistry
from tools.cache import ToolCache
from tools.security import ToolSecurityManager

class ToolManager:
    """
    Universal Tool Execution Gateway for AgentX (Phase 3 AI Execution Backbone).
    Decouples AI agents from direct API calls.
    Provides tool discovery, smart capability routing, permission validation,
    rate-limiting, intelligent caching, retries with exponential backoff, telemetry, and MissionContext logging.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ToolManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return

        self.registry = ToolRegistry()
        self.cache = ToolCache()
        self.security = ToolSecurityManager()
        self._initialized = True
        self._register_default_tools()
        logger.info("ToolManager: Universal Tool Execution Gateway initialized.")

    def list_tools(self) -> Dict[str, Dict[str, Any]]:
        """Lists all registered tools and their descriptors."""
        return self.registry.list_tools()

    def find_tool_by_capability(self, capability: str) -> Optional[BaseTool]:
        """Smart Tool Routing: Finds the best healthy tool matching requested capability."""
        matches = self.registry.find_tools_by_capability(capability)
        healthy_matches = [t for t in matches if t.health() == "HEALTHY"]
        if healthy_matches:
            # Sort by lowest average latency if available
            healthy_matches.sort(key=lambda t: t.telemetry.get("avg_latency_ms", 0))
            return healthy_matches[0]
        elif matches:
            return matches[0]
        return None

    async def execute_tool(
        self,
        tool_name_or_capability: str,
        parameters: Dict[str, Any],
        user_permissions: Optional[List[str]] = None,
        context: Optional[Any] = None,
        use_cache: bool = True,
        max_retries: int = 2
    ) -> ToolResult:
        """
        Universal Tool Execution Entrypoint.
        Routes tool request through security checks, cache lookups, execution retries, and MissionContext logging.
        """
        start_time = time.time()

        # 1. Resolve Tool Instance (by exact name or capability matching)
        tool = self.registry.get_tool(tool_name_or_capability)
        if not tool:
            tool = self.find_tool_by_capability(tool_name_or_capability)

        if not tool:
            logger.error(f"ToolManager: Tool or capability '{tool_name_or_capability}' not found in registry.")
            return ToolResult(
                status="failed",
                success=False,
                data=None,
                errors=[f"Tool or capability '{tool_name_or_capability}' is not registered in the system."]
            )

        # 2. Check Security & Permissions
        if not self.security.validate_tool_access(tool, user_permissions):
            return self.security.create_permission_denied_result(tool.name, tool.permissions)

        # 3. Cache Lookup
        if use_cache and tool.ttl_seconds > 0:
            cached_res = self.cache.get(tool.name, parameters)
            if cached_res:
                tool.telemetry["cache_hits"] += 1
                self._record_tool_in_context(tool.name, cached_res, context)
                return cached_res

        # 4. Execute with Retries & Telemetry Tracking
        tool.telemetry["total_calls"] += 1
        tool.telemetry["last_call_timestamp"] = time.time()
        last_exception = None
        result = None

        for attempt in range(max_retries + 1):
            try:
                # Parameter validation
                await tool.validate(parameters)

                # Execute Tool Logic
                result = await tool.execute(parameters)
                if result.success:
                    break
                else:
                    logger.warning(f"ToolManager: Execution attempt {attempt + 1} for '{tool.name}' failed. Retrying...")
            except Exception as e:
                last_exception = e
                logger.warning(f"ToolManager: Exception during execution attempt {attempt + 1} for '{tool.name}': {e}")
                if attempt < max_retries:
                    await asyncio.sleep(1.0 * (attempt + 1))  # Exponential backoff

        execution_time = time.time() - start_time
        latency_ms = int(execution_time * 1000)

        if not result:
            tool.telemetry["failed_calls"] += 1
            tool.telemetry["last_error"] = str(last_exception) if last_exception else "Tool execution failed"
            result = ToolResult(
                status="failed",
                success=False,
                data=None,
                errors=[f"Tool '{tool.name}' execution failed after {max_retries + 1} attempts: {last_exception}"],
                latency=latency_ms,
                execution_time=execution_time
            )

        if result.success:
            tool.telemetry["success_calls"] += 1
            tool.telemetry["total_latency_ms"] += latency_ms
            tool.telemetry["avg_latency_ms"] = (
                tool.telemetry["total_latency_ms"] / max(tool.telemetry["success_calls"], 1)
            )
            # Store in cache if enabled
            if use_cache and tool.ttl_seconds > 0:
                self.cache.set(tool.name, parameters, result, tool.ttl_seconds)

        # 5. Record Tool Results & Artifacts into MissionContext
        self._record_tool_in_context(tool.name, result, context)
        return result

    def _record_tool_in_context(self, tool_name: str, result: ToolResult, context: Optional[Any]):
        """Helper to append tool execution payloads, artifacts, and observations to MissionContext."""
        if not context:
            return

        if hasattr(context, "tool_results"):
            context.tool_results[tool_name] = result.to_dict()

        if hasattr(context, "artifacts") and result.artifacts:
            for art in result.artifacts:
                context.add_artifact(art)

        if hasattr(context, "add_observation"):
            obs_msg = f"Tool '{tool_name}' returned status={result.status} (latency: {result.latency}ms)"
            context.add_observation("tool_manager", obs_msg)

    def _register_default_tools(self):
        """Pre-registers default built-in tool adapters."""
        from tools.web_search_adapter import WebSearchToolAdapter
        from tools.python_interpreter_adapter import PythonInterpreterAdapter
        from tools.filesystem_adapter import FileSystemAdapter
        from tools.weather_adapter import WeatherAdapter
        from tools.database_adapter import DatabaseAdapter
        from tools.document_generator_adapter import DocumentGeneratorAdapter

        self.registry.register_tool(WebSearchToolAdapter())
        self.registry.register_tool(PythonInterpreterAdapter())
        self.registry.register_tool(FileSystemAdapter())
        self.registry.register_tool(WeatherAdapter())
        self.registry.register_tool(DatabaseAdapter())
        self.registry.register_tool(DocumentGeneratorAdapter())
