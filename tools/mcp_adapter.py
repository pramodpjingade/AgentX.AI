from typing import Dict, Any, List, Optional, Callable
from loguru import logger
from tools.base_tool import BaseTool, ToolResult
import time

class MCPToolAdapter(BaseTool):
    """
    Model Context Protocol (MCP) Tool Adapter for AgentX.
    Wraps external MCP server tool declarations and JSON-RPC endpoints into BaseTool instances.
    """

    def __init__(
        self,
        mcp_name: str,
        description: str,
        capabilities: List[str],
        handler_callable: Callable,
        version: str = "1.0.0-mcp",
        permissions: Optional[List[str]] = None,
        input_schema: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            name=mcp_name,
            description=description,
            version=version,
            capabilities=capabilities,
            permissions=permissions or ["mcp_execution"],
            input_schema=input_schema or {},
            ttl_seconds=30
        )
        self.handler_callable = handler_callable

    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Executes MCP tool handler asynchronously."""
        start_time = time.time()
        logger.info(f"MCPToolAdapter [{self.name}]: Executing MCP protocol handler...")

        try:
            if callable(self.handler_callable):
                import inspect
                if inspect.iscoroutinefunction(self.handler_callable):
                    res_data = await self.handler_callable(parameters)
                else:
                    res_data = self.handler_callable(parameters)
            else:
                res_data = {"result": f"MCP execution payload for {self.name}"}

            execution_time = time.time() - start_time
            latency = int(execution_time * 1000)

            return ToolResult(
                status="success",
                success=True,
                data=res_data,
                metadata={"mcp_server": self.name, "protocol_version": "2024-11-05"},
                latency=latency,
                execution_time=execution_time,
                logs=[f"MCP tool '{self.name}' executed successfully."]
            )

        except Exception as e:
            execution_time = time.time() - start_time
            latency = int(execution_time * 1000)
            logger.error(f"MCPToolAdapter [{self.name}]: Protocol execution failure: {e}")
            return ToolResult(
                status="failed",
                success=False,
                data=None,
                errors=[str(e)],
                latency=latency,
                execution_time=execution_time
            )
