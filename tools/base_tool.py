from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import time
import uuid

@dataclass
class ToolResult:
    """
    Standardized Output Payload for all Tool Invocations in AgentX.
    Guarantees consistent data structure across all external system providers.
    """
    status: str = "success"  # success, failed, cached, permission_denied, timeout
    success: bool = True
    data: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    latency: int = 0  # milliseconds
    execution_time: float = 0.0  # seconds
    logs: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    citations: List[Dict[str, Any]] = field(default_factory=list)
    artifacts: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        """Serializes ToolResult into a dictionary."""
        return {
            "status": self.status,
            "success": self.success,
            "data": self.data,
            "metadata": self.metadata,
            "latency": self.latency,
            "execution_time": self.execution_time,
            "logs": self.logs,
            "errors": self.errors,
            "warnings": self.warnings,
            "citations": self.citations,
            "artifacts": self.artifacts,
            "confidence": self.confidence
        }

class BaseTool(ABC):
    """
    Abstract Base Class for all Tools in AgentX (Phase 3 Tool Execution Layer).
    Defines standard tool lifecycle methods, permissions, schemas, and health reporting.
    """

    def __init__(
        self,
        name: str,
        description: str,
        version: str = "1.0.0",
        capabilities: Optional[List[str]] = None,
        permissions: Optional[List[str]] = None,
        input_schema: Optional[Dict[str, Any]] = None,
        output_schema: Optional[Dict[str, Any]] = None,
        ttl_seconds: int = 60
    ):
        self.tool_id: str = str(uuid.uuid4())
        self.name: str = name
        self.description: str = description
        self.version: str = version
        self.capabilities: List[str] = capabilities or []
        self.permissions: List[str] = permissions or []
        self.input_schema: Dict[str, Any] = input_schema or {}
        self.output_schema: Dict[str, Any] = output_schema or {}
        self.ttl_seconds: int = ttl_seconds
        self.health_status: str = "HEALTHY"  # HEALTHY, DEGRADED, UNHEALTHY
        self.telemetry: Dict[str, Any] = {
            "total_calls": 0,
            "success_calls": 0,
            "failed_calls": 0,
            "cache_hits": 0,
            "total_latency_ms": 0,
            "avg_latency_ms": 0.0,
            "last_call_timestamp": None,
            "last_error": None
        }

    async def initialize(self) -> None:
        """Lifecycle hook invoked before first execution."""
        pass

    async def validate(self, parameters: Dict[str, Any]) -> bool:
        """Validates tool parameters against input schema."""
        return True

    @abstractmethod
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """
        Executes the tool logic and returns a standardized ToolResult.
        Must be implemented by all concrete tool subclasses.
        """
        pass

    async def cleanup(self) -> None:
        """Lifecycle hook invoked on system shutdown or error cleanup."""
        pass

    def health(self) -> str:
        """Returns the health status of the tool."""
        return self.health_status

    def metadata(self) -> Dict[str, Any]:
        """Returns full metadata descriptor for registry registration."""
        return {
            "tool_id": self.tool_id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "capabilities": self.capabilities,
            "permissions": self.permissions,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "ttl_seconds": self.ttl_seconds,
            "health_status": self.health_status,
            "telemetry": self.telemetry
        }
