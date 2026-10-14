from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import time
from datetime import datetime

@dataclass
class MissionContext:
    """
    Shared Execution Context for AI Missions in AgentX (Phase 2 Brain Core).
    Encapsulates all transient state, conversation history, long-term memory, knowledge vectors,
    tool outputs, artifacts, LLM responses, execution metrics, and reasoning metadata.
    """
    goal_id: str
    title: str
    description: str = ""
    user_id: Optional[str] = None
    mission_type: str = "general"
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    memory: Dict[str, Any] = field(default_factory=dict)
    knowledge: Dict[str, Any] = field(default_factory=dict)
    tasks: List[Dict[str, Any]] = field(default_factory=list)
    current_task_index: int = 0
    tool_results: Dict[str, Any] = field(default_factory=dict)
    agent_outputs: Dict[str, Any] = field(default_factory=dict)
    llm_responses: Dict[str, Any] = field(default_factory=dict)
    artifacts: List[Dict[str, Any]] = field(default_factory=list)
    current_status: str = "CREATED"
    progress_percentage: int = 0
    execution_metadata: Dict[str, Any] = field(default_factory=dict)
    execution_metrics: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    observations: List[Dict[str, Any]] = field(default_factory=list)
    reasoning_metadata: Dict[str, Any] = field(default_factory=dict)
    timings: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def goal(self) -> str:
        """Returns consolidated goal representation."""
        if self.description:
            return f"{self.title}: {self.description}"
        return self.title

    @property
    def mission(self) -> Dict[str, Any]:
        """Returns mission metadata representation."""
        return {
            "goal_id": self.goal_id,
            "title": self.title,
            "description": self.description,
            "user_id": self.user_id,
            "category": self.mission_type,
            "status": self.current_status
        }

    @property
    def conversation(self) -> List[Dict[str, Any]]:
        """Returns conversation history."""
        return self.conversation_history

    def update_status(self, new_status: str, progress_pct: Optional[int] = None):
        """Updates current mission execution status and progress percentage."""
        self.current_status = new_status
        if progress_pct is not None:
            self.progress_percentage = progress_pct
        self.timings[new_status.lower()] = time.time()

    def add_agent_output(self, agent_name: str, output: Dict[str, Any]):
        """Records output payload from a specialized agent."""
        self.agent_outputs[agent_name] = output

    def add_artifact(self, artifact: Dict[str, Any]):
        """Appends a generated file, code snippet, table, or downloadable item to artifacts."""
        self.artifacts.append(artifact)

    def add_observation(self, agent_name: str, observation: str):
        """Appends an agent observation/thought to reasoning trace."""
        self.observations.append({
            "agent": agent_name,
            "observation": observation,
            "timestamp": datetime.utcnow().isoformat()
        })

    def add_error(self, error_msg: str):
        """Appends an error message to execution log."""
        self.errors.append(error_msg)

    def record_metric(self, key: str, value: Any):
        """Records telemetry execution metrics."""
        self.execution_metrics[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """Serializes MissionContext to a comprehensive dictionary."""
        return {
            "goal_id": self.goal_id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "mission_type": self.mission_type,
            "mission": self.mission,
            "conversation_history": self.conversation_history,
            "memory": self.memory,
            "knowledge": self.knowledge,
            "tasks": self.tasks,
            "current_task_index": self.current_task_index,
            "tool_results": self.tool_results,
            "agent_outputs": self.agent_outputs,
            "llm_responses": self.llm_responses,
            "artifacts": self.artifacts,
            "current_status": self.current_status,
            "progress_percentage": self.progress_percentage,
            "execution_metadata": self.execution_metadata,
            "execution_metrics": self.execution_metrics,
            "dependencies": self.dependencies,
            "errors": self.errors,
            "observations": self.observations,
            "reasoning_metadata": self.reasoning_metadata,
            "timings": self.timings,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MissionContext":
        """Instantiates MissionContext from a dictionary."""
        return cls(
            goal_id=data.get("goal_id", ""),
            title=data.get("title", ""),
            description=data.get("description", ""),
            user_id=data.get("user_id"),
            mission_type=data.get("mission_type", "general"),
            conversation_history=data.get("conversation_history", []),
            memory=data.get("memory", {}),
            knowledge=data.get("knowledge", {}),
            tasks=data.get("tasks", []),
            current_task_index=data.get("current_task_index", 0),
            tool_results=data.get("tool_results", {}),
            agent_outputs=data.get("agent_outputs", {}),
            llm_responses=data.get("llm_responses", {}),
            artifacts=data.get("artifacts", []),
            current_status=data.get("current_status", "CREATED"),
            progress_percentage=data.get("progress_percentage", 0),
            execution_metadata=data.get("execution_metadata", {}),
            execution_metrics=data.get("execution_metrics", {}),
            dependencies=data.get("dependencies", []),
            errors=data.get("errors", []),
            observations=data.get("observations", []),
            reasoning_metadata=data.get("reasoning_metadata", {}),
            timings=data.get("timings", {})
        )
