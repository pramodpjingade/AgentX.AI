import uuid
import os
import json
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON, Integer, Boolean, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from dotenv import load_dotenv

from database.connection import Base

from pathlib import Path
_project_root = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=_project_root / ".env")

# Determine database engine type
DATABASE_URL = os.getenv("DATABASE_URL", "")
is_sqlite = DATABASE_URL.startswith("sqlite")

# Define fallback types for SQLite compatibility
class SQLiteUUID(TypeDecorator):
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return str(value)
        return None

    def process_result_value(self, value, dialect):
        if value is not None:
            return uuid.UUID(value)
        return None

class SQLiteJSONB(TypeDecorator):
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)
        return None

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return None

class SQLiteVector(TypeDecorator):
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(list(value))
        return None

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return None

# Dynamic Type Selection Helpers
UUID_TYPE = SQLiteUUID if is_sqlite else UUID(as_uuid=True)
JSONB_TYPE = SQLiteJSONB if is_sqlite else JSONB

def VectorColumn(dim: int):
    if is_sqlite:
        return Column(SQLiteVector, nullable=True)
    else:
        from pgvector.sqlalchemy import Vector
        return Column(Vector(dim), nullable=True)


class User(Base):
    __tablename__ = "users"

    id = Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="user")  # admin, user, developer
    nickname = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    memories = relationship("Memory", back_populates="user", cascade="all, delete-orphan")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID_TYPE, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=True)
    metadata_json = Column(JSONB_TYPE, nullable=True, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="conversation")


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID_TYPE, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    sender_type = Column(String(50), nullable=False)  # user, system, agent
    sender_name = Column(String(100), nullable=True)   # master_agent, research_agent, etc.
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")


class Goal(Base):
    __tablename__ = "goals"

    id = Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID_TYPE, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="pending")  # pending, planning, executing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="goals")
    tasks = relationship("Task", back_populates="goal", cascade="all, delete-orphan")
    mission_result = relationship("MissionResult", back_populates="goal", uselist=False, cascade="all, delete-orphan")


class MissionResult(Base):
    __tablename__ = "mission_results"

    id = Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    goal_id = Column(UUID_TYPE, ForeignKey("goals.id", ondelete="CASCADE"), nullable=False, unique=True)
    mission_type = Column(String(50), nullable=False, default="general")
    status = Column(String(50), default="COMPLETED")
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=True)
    structured_output = Column(JSONB_TYPE, nullable=True, default=dict)
    markdown_output = Column(Text, nullable=True)
    json_output = Column(JSONB_TYPE, nullable=True, default=dict)
    artifacts = Column(JSONB_TYPE, nullable=True, default=list)
    attachments = Column(JSONB_TYPE, nullable=True, default=list)
    confidence_score = Column(Integer, default=95)
    execution_time = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    goal = relationship("Goal", back_populates="mission_result")



class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    goal_id = Column(UUID_TYPE, ForeignKey("goals.id", ondelete="CASCADE"), nullable=False)
    conversation_id = Column(UUID_TYPE, ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True)
    parent_task_id = Column(UUID_TYPE, nullable=True, index=True)
    assigned_agent = Column(String(100), nullable=False)
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    input_data = Column(JSONB_TYPE, nullable=True, default=dict)
    output_data = Column(JSONB_TYPE, nullable=True, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    goal = relationship("Goal", back_populates="tasks")
    conversation = relationship("Conversation", back_populates="tasks")


class Memory(Base):
    __tablename__ = "memories"

    id = Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID_TYPE, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    memory_type = Column(String(50), nullable=False)  # semantic, preference, episodic
    content = Column(Text, nullable=False)
    # Use dynamic vector column helper
    embedding = VectorColumn(1536)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="memories")


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id = Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    metadata_json = Column(JSONB_TYPE, nullable=True, default=dict)
    # Use dynamic vector column helper
    embedding = VectorColumn(1536)
    created_at = Column(DateTime, default=datetime.utcnow)


class WorkflowDefinition(Base):
    __tablename__ = "workflow_definitions"

    id = Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    workflow_name = Column(String(100), nullable=False)
    version = Column(String(20), nullable=False)
    dag_schema = Column(JSONB_TYPE, nullable=True, default=dict)
    deployment_status = Column(String(50), default="active")  # active, archived, rolling
    rollback_version = Column(String(20), nullable=True)
    migration_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class PluginVersion(Base):
    __tablename__ = "plugin_versions"

    id = Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    plugin_name = Column(String(100), nullable=False)
    version = Column(String(20), nullable=False)
    dependencies = Column(JSONB_TYPE, nullable=True, default=list)
    min_agentx_version = Column(String(20), nullable=True)
    package_url = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ModelRouterLog(Base):
    __tablename__ = "model_router_logs"

    id = Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID_TYPE, nullable=True)
    provider = Column(String(50), nullable=False)  # openai, anthropic, google, ollama, mock
    model_name = Column(String(100), nullable=False)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    cost = Column(JSONB_TYPE, nullable=True)  # Stores pricing details dynamically
    latency_ms = Column(Integer, default=0)
    status = Column(String(50), default="success")  # success, failed
    created_at = Column(DateTime, default=datetime.utcnow)


class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id = Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID_TYPE, nullable=True)
    agent_name = Column(String(100), nullable=False)
    tool_name = Column(String(100), nullable=False)
    parameters = Column(JSONB_TYPE, nullable=True, default=dict)
    status = Column(String(50), default="pending")  # pending, approved, rejected
    resolved_by = Column(UUID_TYPE, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

