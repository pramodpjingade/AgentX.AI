import time
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from loguru import logger
from sqlalchemy.future import select
from sqlalchemy import desc

from database.connection import async_session
from database.models import Goal, MissionResult, Conversation, Message, User
from core.orchestrator.mission_executor import MissionExecutor
from memory.memory_manager import MemoryManager
from knowledge.platform import KnowledgePlatform
from chat.schemas import StandardChatResponse, ResponseMetadata, ArtifactDescriptor, ActionDescriptor
from chat.response_formatter import ResponseFormatter

from chat.intent_classifier import ChatIntentClassifier
from chat.conversation_engine import ConversationEngine


class ChatService:
    """
    Central Chat Service for AgentX.
    Orchestrates two-layer routing:
    - Layer 1 (Conversation Engine): Fast (<500ms) human conversation without Goal/MissionExecutor.
    - Layer 2 (Mission Engine): Multi-agent execution pipeline for complex actionable task requests.
    
    Conversations and messages are persisted to the database for durability across server restarts.
    """

    def __init__(self):
        self.mission_executor = MissionExecutor()
        self.memory_manager = MemoryManager()
        self.knowledge_platform = KnowledgePlatform()
        logger.info("ChatService: Central 2-Layer Professional Chat Service initialized.")

    async def process_message(
        self,
        message: str,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        streaming: bool = True,
        preferences: Optional[List[str]] = None
    ) -> StandardChatResponse:
        """
        Processes a user chat message end-to-end through the two-layer AI pipeline.
        Persists conversations and messages to the database.
        """
        msg_id = str(uuid.uuid4())
        now = datetime.utcnow()

        logger.info(f"ChatService: Processing message for conversation '{conversation_id}' (User: '{user_id}')")

        # Resolve user UUID
        user_uuid = None
        if user_id:
            try:
                user_uuid = uuid.UUID(user_id) if len(user_id) == 36 else uuid.uuid5(uuid.NAMESPACE_DNS, user_id)
            except ValueError:
                user_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, user_id)

        # 1. Get or create conversation in DB
        conv_db_id = None
        conv_title = message[:60]
        
        async with async_session() as db:
            if conversation_id:
                try:
                    conv_uuid = uuid.UUID(conversation_id)
                    result = await db.execute(select(Conversation).where(Conversation.id == conv_uuid))
                    conv_obj = result.scalars().first()
                    if conv_obj:
                        conv_db_id = str(conv_obj.id)
                        conv_title = conv_obj.title or conv_title
                except Exception:
                    pass

            # Create new conversation if not found
            if not conv_db_id:
                if user_uuid:
                    new_conv = Conversation(
                        user_id=user_uuid,
                        title=message[:60],
                        metadata_json={}
                    )
                    db.add(new_conv)
                    await db.flush()
                    conv_db_id = str(new_conv.id)
                else:
                    # Fallback: use provided or generate new ID without DB
                    conv_db_id = conversation_id or str(uuid.uuid4())

            # 2. Store user message in DB
            if user_uuid:
                try:
                    conv_uuid = uuid.UUID(conv_db_id)
                    user_msg_db = Message(
                        conversation_id=conv_uuid,
                        sender_type="user",
                        sender_name="user",
                        content=message,
                        timestamp=now
                    )
                    db.add(user_msg_db)
                    await db.flush()
                except Exception as e:
                    logger.warning(f"ChatService: Could not store user message: {e}")

            await db.commit()

        # 3. Build message history for context
        messages_history = await self._load_conversation_history(conv_db_id)

        # 4. Classify intent: "conversation" vs "mission"
        intent = ChatIntentClassifier.classify(message, messages_history)
        logger.info(f"CHAT_TRACE_SERVICE conv_id={conv_db_id} user_id={user_id} intent={intent}")
        mission_result = None

        if intent == "conversation":
            logger.info(f"CHAT_TRACE_INTENT conv_id={conv_db_id} mode=layer1_conversation_engine")
            assistant_content = await ConversationEngine.generate_response(
                message=message,
                conversation_id=conv_db_id,
                user_id=user_id,
                messages_history=messages_history
            )
        else:
            logger.info(f"CHAT_TRACE_INTENT conv_id={conv_db_id} mode=layer2_mission_engine")
            goal_obj = None
            if user_uuid:
                try:
                    async with async_session() as db:
                        goal_obj = Goal(
                            user_id=user_uuid,
                            title=message[:200],
                            description=message,
                            status="in_progress"
                        )
                        db.add(goal_obj)
                        await db.commit()
                        await db.refresh(goal_obj)
                        logger.info(f"CHAT_TRACE_EXECUTION goal_created={goal_obj.id}")
                except Exception as e:
                    logger.warning(f"ChatService: Database Goal creation note: {e}")

            # Execute Mission via MissionExecutor ONLY when goal was successfully created
            if goal_obj:
                try:
                    mission_result = await self.mission_executor.execute_mission(str(goal_obj.id))
                except Exception as e:
                    logger.error(f"ChatService: Mission execution error: {e}")

            # Format Assistant Response via ResponseFormatter
            if mission_result:
                assistant_content = ResponseFormatter.format_mission_result(mission_result, message)
            else:
                # Provide a helpful response even when mission executor isn't configured
                assistant_content = (
                    f"I understand you'd like help with: **{message}**\n\n"
                    f"I'm ready to assist! Here's how I can approach this:\n\n"
                    f"1. **Analysis** — Breaking down the core requirements\n"
                    f"2. **Planning** — Structuring a step-by-step execution approach\n"
                    f"3. **Execution** — Delivering the requested output\n\n"
                    f"To get the best results, could you provide a bit more context about your specific requirements or constraints? "
                    f"I can then tailor my response more precisely to your needs."
                )

        # 5. Build Artifact Descriptors
        artifacts = []
        if mission_result:
            artifacts.append(ArtifactDescriptor(
                id=str(uuid.uuid4()),
                name="Mission_Deliverable.md",
                type="Markdown",
                download_url=f"/api/v1/missions/{str(mission_result.id)}/download"
            ))

        # 6. Persist assistant message to DB
        async with async_session() as db:
            try:
                conv_uuid = uuid.UUID(conv_db_id)
                asst_msg_db = Message(
                    conversation_id=conv_uuid,
                    sender_type="assistant",
                    sender_name="agentx",
                    content=assistant_content,
                    timestamp=datetime.utcnow()
                )
                db.add(asst_msg_db)
                await db.commit()
            except Exception as e:
                logger.warning(f"ChatService: Could not persist assistant message: {e}")

        # 7. Store Memory Node in Cognitive Memory Engine
        try:
            await self.memory_manager.store_memory(
                content=f"User: {message}\nAssistant: {assistant_content[:200]}",
                user_id=user_id,
                metadata={"conversation_id": conv_db_id, "category": "conversation"}
            )
        except Exception as e:
            logger.debug(f"ChatService: Memory storage note: {e}")

        return StandardChatResponse(
            conversation_id=conv_db_id,
            message_id=msg_id,
            role="assistant",
            content=assistant_content,
            artifacts=artifacts,
            actions=[],
            status="completed",
            timestamp=time.time(),
            metadata=ResponseMetadata(
                streaming=streaming,
                conversation_title=conv_title
            )
        )

    async def _load_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Loads conversation message history from DB."""
        try:
            conv_uuid = uuid.UUID(conversation_id)
            async with async_session() as db:
                result = await db.execute(
                    select(Message)
                    .where(Message.conversation_id == conv_uuid)
                    .order_by(Message.timestamp)
                    .limit(50)
                )
                messages = result.scalars().all()
                return [
                    {
                        "message_id": str(m.id),
                        "conversation_id": conversation_id,
                        "role": "user" if m.sender_type == "user" else "assistant",
                        "content": m.content,
                        "timestamp": m.timestamp.timestamp() if m.timestamp else time.time()
                    }
                    for m in messages
                ]
        except Exception as e:
            logger.debug(f"ChatService: History load note: {e}")
            return []

    async def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a conversation thread with messages from DB."""
        try:
            conv_uuid = uuid.UUID(conversation_id)
            async with async_session() as db:
                result = await db.execute(select(Conversation).where(Conversation.id == conv_uuid))
                conv_obj = result.scalars().first()
                if not conv_obj:
                    return None

                messages = await self._load_conversation_history(conversation_id)
                return {
                    "conversation_id": str(conv_obj.id),
                    "title": conv_obj.title or "Conversation",
                    "user_id": str(conv_obj.user_id),
                    "created_at": conv_obj.created_at.timestamp() if conv_obj.created_at else time.time(),
                    "updated_at": conv_obj.created_at.timestamp() if conv_obj.created_at else time.time(),
                    "messages": messages
                }
        except Exception as e:
            logger.error(f"ChatService: get_conversation error: {e}")
            return None

    async def list_conversations(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lists active conversation threads from DB."""
        try:
            async with async_session() as db:
                if user_id:
                    try:
                        user_uuid = uuid.UUID(user_id) if len(user_id) == 36 else uuid.uuid5(uuid.NAMESPACE_DNS, user_id)
                        result = await db.execute(
                            select(Conversation)
                            .where(Conversation.user_id == user_uuid)
                            .order_by(desc(Conversation.created_at))
                            .limit(50)
                        )
                    except Exception:
                        result = await db.execute(
                            select(Conversation).order_by(desc(Conversation.created_at)).limit(50)
                        )
                else:
                    result = await db.execute(
                        select(Conversation).order_by(desc(Conversation.created_at)).limit(50)
                    )
                
                convs = result.scalars().all()
                return [
                    {
                        "conversation_id": str(c.id),
                        "title": c.title or "Conversation",
                        "user_id": str(c.user_id),
                        "created_at": c.created_at.timestamp() if c.created_at else time.time(),
                        "updated_at": c.created_at.timestamp() if c.created_at else time.time(),
                        "messages": []
                    }
                    for c in convs
                ]
        except Exception as e:
            logger.error(f"ChatService: list_conversations error: {e}")
            return []

    async def delete_conversation(self, conversation_id: str) -> bool:
        """Deletes a conversation thread from DB."""
        try:
            conv_uuid = uuid.UUID(conversation_id)
            async with async_session() as db:
                result = await db.execute(select(Conversation).where(Conversation.id == conv_uuid))
                conv_obj = result.scalars().first()
                if not conv_obj:
                    return False
                await db.delete(conv_obj)
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"ChatService: delete_conversation error: {e}")
            return False
