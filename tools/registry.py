from typing import Dict, Any, List, Type, Optional
from loguru import logger
from tools.base_tool import BaseTool

class ToolRegistry:
    """
    Tool Registry (Phase 3 Tool Execution Layer Core).
    Manages auto-discovery, tool registration, version tracking, health auditing,
    capability indexing, and metadata lookup for all tools in AgentX.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ToolRegistry, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return

        self._registry: Dict[str, BaseTool] = {}
        self._initialized = True
        logger.info("ToolRegistry: Central Tool Registry initialized.")

    def register_tool(self, tool: BaseTool) -> BaseTool:
        """Registers a BaseTool instance into the system."""
        self._registry[tool.name] = tool
        logger.info(f"ToolRegistry: Registered tool '{tool.name}' (v{tool.version}) with capabilities {tool.capabilities}")
        return tool

    def unregister_tool(self, tool_name: str) -> bool:
        """Removes a tool from the registry."""
        if tool_name in self._registry:
            del self._registry[tool_name]
            logger.info(f"ToolRegistry: Unregistered tool '{tool_name}'")
            return True
        return False

    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Retrieves a registered tool instance by name."""
        return self._registry.get(tool_name)

    def list_tools(self) -> Dict[str, Dict[str, Any]]:
        """Lists all registered tools and their metadata descriptors."""
        return {
            name: tool.metadata()
            for name, tool in self._registry.items()
        }

    def find_tools_by_capability(self, capability: str) -> List[BaseTool]:
        """Finds all tools that match the specified capability token."""
        matches = []
        cap_lower = capability.lower()
        for tool in self._registry.values():
            if cap_lower in [c.lower() for c in tool.capabilities]:
                matches.append(tool)
        return matches

    def check_health(self) -> Dict[str, Any]:
        """Audits the health status of all registered tools."""
        return {
            name: {
                "health": tool.health(),
                "telemetry": tool.telemetry
            }
            for name, tool in self._registry.items()
        }
