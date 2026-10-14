from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
import uuid
import time
from loguru import logger

class BaseAgent(ABC):
    """
    Abstract Base Class for all AI Agents in AgentX (Phase 2 Brain Core).
    Defines mandatory attributes, telemetry tracking, health monitoring, retry policies,
    and standard MissionContext execution interface.
    """

    def __init__(
        self,
        name: str,
        role: str,
        description: str = "",
        capabilities: Optional[List[str]] = None,
        supported_mission_types: Optional[List[str]] = None,
        supported_tools: Optional[List[str]] = None,
        priority: str = "NORMAL",
        model_preference: str = "FAST_MODEL",
        configuration: Optional[Dict[str, Any]] = None,
        retry_policy: Optional[Dict[str, Any]] = None,
        timeout_policy: float = 60.0
    ):
        self.agent_id: str = str(uuid.uuid4())
        self.name: str = name
        self.role: str = role
        self.description: str = description or f"{name} specialized agent."
        self.capabilities: List[str] = capabilities or []
        self.supported_mission_types: List[str] = supported_mission_types or ["general"]
        self.supported_tools: List[str] = supported_tools or []
        self.priority: str = priority  # HIGH, NORMAL, LOW
        self.health_status: str = "HEALTHY"  # HEALTHY, DEGRADED, UNHEALTHY
        self.model_preference: str = model_preference
        self.configuration: Dict[str, Any] = configuration or {}
        self.retry_policy: Dict[str, Any] = retry_policy or {"max_retries": 3, "backoff_factor": 1.5}
        self.timeout_policy: float = timeout_policy
        self.telemetry: Dict[str, Any] = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "total_latency_ms": 0,
            "avg_latency_ms": 0.0,
            "last_execution_timestamp": None,
            "last_error": None
        }

    @abstractmethod
    async def execute(
        self,
        task_input: Any,
        global_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Core reasoning and processing loop for the agent.
        Must be implemented by all concrete agent subclasses.
        
        Args:
            task_input: Dictionary or MissionContext object holding input parameters.
            global_context: Optional dictionary containing shared system state.

        Returns:
            Dictionary containing the task execution result payload.
        """
        pass

    async def execute_context(self, context: Any) -> Any:
        """
        Standard Phase 2 MissionContext Execution Wrapper.
        Wraps `execute()` with automated telemetry, latency measurement, and context updates.

        Args:
            context: MissionContext object.

        Returns:
            Updated MissionContext object.
        """
        start_time = time.time()
        self.telemetry["total_executions"] += 1
        self.telemetry["last_execution_timestamp"] = time.time()

        task_input = context.to_dict() if hasattr(context, "to_dict") else context
        global_ctx = getattr(context, "memory", None)

        try:
            result = await self.execute(task_input, global_ctx)
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Update telemetry stats
            self.telemetry["successful_executions"] += 1
            self.telemetry["total_latency_ms"] += latency_ms
            self.telemetry["avg_latency_ms"] = (
                self.telemetry["total_latency_ms"] / max(self.telemetry["successful_executions"], 1)
            )

            # Record in context
            if hasattr(context, "add_agent_output"):
                context.add_agent_output(self.name, result)
            if hasattr(context, "record_metric"):
                context.record_metric(f"{self.name}_latency_ms", latency_ms)

            return context

        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            self.telemetry["failed_executions"] += 1
            self.telemetry["last_error"] = str(e)
            self.health_status = "DEGRADED" if self.telemetry["failed_executions"] < 5 else "UNHEALTHY"
            
            logger.error(f"BaseAgent [{self.name}]: Execution failure: {e}")
            if hasattr(context, "add_error"):
                context.add_error(f"Agent [{self.name}] failed: {e}")
            return context

    @abstractmethod
    def get_tools(self) -> List[Any]:
        """Return list of active tools bound to this agent."""
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return system prompt/instructions for this agent."""
        pass

    async def call_tool(
        self,
        tool_name_or_capability: str,
        parameters: Dict[str, Any],
        context: Optional[Any] = None,
        user_permissions: Optional[List[str]] = None
    ):
        """
        Universal Tool Invocation Entrypoint for Agents.
        Routes request through ToolManager to execute tool, validate permissions, and update context.
        """
        from tools.manager import ToolManager
        manager = ToolManager()
        logger.info(f"BaseAgent [{self.name}]: Requesting tool '{tool_name_or_capability}' via ToolManager")
        return await manager.execute_tool(
            tool_name_or_capability=tool_name_or_capability,
            parameters=parameters,
            user_permissions=user_permissions,
            context=context
        )

    def get_metadata(self) -> Dict[str, Any]:
        """Returns comprehensive metadata footprint for registry and telemetry lookup."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role,
            "description": self.description,
            "capabilities": self.capabilities,
            "supported_mission_types": self.supported_mission_types,
            "supported_tools": self.supported_tools,
            "priority": self.priority,
            "health_status": self.health_status,
            "model_preference": self.model_preference,
            "configuration": self.configuration,
            "telemetry": self.telemetry
        }

    # Enterprise Lifecycle Hooks
    async def initialize(self) -> None:
        """Invoked on startup to pre-load models and local variables."""
        pass

    async def validate(self, input_payload: Dict[str, Any]) -> bool:
        """Verifies schema parameters and permissions before run."""
        return True

    async def plan(self, input_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Optional task DAG planning hook."""
        return []

    async def evaluate(self, output_payload: Dict[str, Any]) -> bool:
        """Audits self-output quality before completing step."""
        return True

    async def cleanup(self) -> None:
        """Closes connections, file descriptors, or handles errors."""
        pass

    async def shutdown(self) -> None:
        """Executes before thread eviction."""
        pass

    async def request_tool_approval(self, tool_name: str, parameters: Dict[str, Any], task_id: Any = None) -> str:
        """Helper to create a pending tool execution approval request in database."""
        from database.connection import async_session
        from database.models import ApprovalRequest
        
        async with async_session() as db:
            req = ApprovalRequest(
                task_id=uuid.UUID(str(task_id)) if task_id else None,
                agent_name=self.name,
                tool_name=tool_name,
                parameters=parameters,
                status="pending"
            )
            db.add(req)
            await db.commit()
            await db.refresh(req)
            return str(req.id)

    async def check_tool_approval(self, approval_id: str) -> str:
        """Checks current status of an approval request."""
        from database.connection import async_session
        from database.models import ApprovalRequest
        from sqlalchemy.future import select
        
        async with async_session() as db:
            stmt = select(ApprovalRequest).where(ApprovalRequest.id == uuid.UUID(approval_id))
            result = await db.execute(stmt)
            req = result.scalars().first()
            if req:
                return req.status
            return "not_found"
