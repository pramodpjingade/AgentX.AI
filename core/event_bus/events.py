from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime
from uuid import uuid4

class AgentMessageEnvelope(BaseModel):
    """Universal message schema envelope for all AgentX event transactions."""
    message_version: str = "1.0"
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    correlation_id: str = Field(default_factory=lambda: str(uuid4()))
    trace_id: str = Field(default_factory=lambda: str(uuid4()))
    source_agent: str
    target_agent: str
    event_type: str
    priority: str = "NORMAL"  # CRITICAL, HIGH, NORMAL, LOW, BACKGROUND
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    payload: Dict[str, Any] = Field(default_factory=dict)
    status: str = "pending"
    metadata: Dict[str, Any] = Field(default_factory=dict)

# --- Mission Event Types ---
class MissionEvents:
    MISSION_CREATED = "MissionCreated"
    MISSION_STARTED = "MissionStarted"
    MISSION_PLANNING = "MissionPlanning"
    MISSION_EXECUTING = "MissionExecuting"
    MISSION_EVALUATING = "MissionEvaluating"
    MISSION_FINALIZING = "MissionFinalizing"
    MISSION_PROGRESS = "MissionProgress"
    MISSION_COMPLETED = "MissionCompleted"
    MISSION_FAILED = "MissionFailed"
    MISSION_RESULT_CREATED = "MissionResultCreated"
    MISSION_ARTIFACT_GENERATED = "MissionArtifactGenerated"


