from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime

# --- User & Auth Schemas ---

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")
    nickname: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    role: str
    nickname: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[UUID] = None

# --- Goal Schemas ---

class GoalCreate(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None

class GoalResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    description: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Task Schemas ---

class TaskResponse(BaseModel):
    id: UUID
    goal_id: UUID
    conversation_id: Optional[UUID] = None
    parent_task_id: Optional[UUID] = None
    assigned_agent: str
    status: str
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True

# --- Mission Result & Progress Schemas ---

class MissionResultResponse(BaseModel):
    id: UUID
    goal_id: UUID
    mission_type: str
    status: str
    title: str
    summary: Optional[str] = None
    structured_output: Optional[Dict[str, Any]] = None
    markdown_output: Optional[str] = None
    json_output: Optional[Dict[str, Any]] = None
    artifacts: Optional[List[Any]] = None
    attachments: Optional[List[Any]] = None
    confidence_score: Optional[int] = 95
    execution_time: Optional[int] = 0
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: datetime

    class Config:
        from_attributes = True

class MissionProgressResponse(BaseModel):
    goal_id: UUID
    status: str
    step_message: str
    progress_percentage: int
    updated_at: datetime

# --- Detailed Execution Schemas ---

class GoalDetailResponse(BaseModel):
    goal: GoalResponse
    tasks: Optional[List[TaskResponse]] = None
    mission_result: Optional[MissionResultResponse] = None
    progress: Optional[MissionProgressResponse] = None

