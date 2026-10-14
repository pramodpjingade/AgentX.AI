import time
import uuid
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(..., description="User prompt or mission request text")
    conversation_id: Optional[str] = Field(None, description="ID of existing conversation thread")
    streaming: bool = Field(True, description="Enable real-time token and status streaming")
    preferences: Optional[List[str]] = Field(default_factory=list, description="Optional user explicit preferences")

class ArtifactDescriptor(BaseModel):
    id: str
    name: str
    type: str
    download_url: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ActionDescriptor(BaseModel):
    id: str
    action_type: str
    label: str
    payload: Dict[str, Any] = Field(default_factory=dict)

class ResponseMetadata(BaseModel):
    streaming: bool = True
    conversation_title: Optional[str] = None
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    follow_up_questions: List[str] = Field(default_factory=list)

class StandardChatResponse(BaseModel):
    conversation_id: str
    message_id: str
    role: str = "assistant"
    content: str
    artifacts: List[ArtifactDescriptor] = Field(default_factory=list)
    actions: List[ActionDescriptor] = Field(default_factory=list)
    status: str = "completed"  # completed, in_progress, failed
    timestamp: float = Field(default_factory=time.time)
    metadata: ResponseMetadata = Field(default_factory=ResponseMetadata)

class ChatMessage(BaseModel):
    message_id: str
    conversation_id: str
    role: str  # user, assistant
    content: str
    timestamp: float
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ConversationHistory(BaseModel):
    conversation_id: str
    title: str
    created_at: float
    updated_at: float
    messages: List[ChatMessage] = Field(default_factory=list)

class ChatStreamChunk(BaseModel):
    event: str  # assistant_stream, status_update, artifact_ready, mission_completed
    conversation_id: str
    message_id: str
    content: Optional[str] = None
    status_message: Optional[str] = None
    progress_percentage: Optional[int] = None
