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
from chat.schemas import StandardChatResponse, ResponseMetadata, ArtifactDescriptor, ActionDescriptor, ChatStreamChunk
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
                target_uuid = None
                if conversation_id:
                    try:
                        target_uuid = uuid.UUID(conversation_id)
                    except Exception:
                        pass
                if not target_uuid:
                    target_uuid = uuid.uuid4()

                if user_uuid:
                    new_conv = Conversation(
                        id=target_uuid,
                        user_id=user_uuid,
                        title=message[:60],
                        metadata_json={}
                    )
                    db.add(new_conv)
                    await db.flush()
                    conv_db_id = str(new_conv.id)
                else:
                    conv_db_id = str(target_uuid)

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
                # Seamless fallback to direct model generation
                logger.info(f"ChatService: Mission executor produced no result; falling back to direct AI generation.")
                assistant_content = await ConversationEngine.generate_response(
                    message=message,
                    conversation_id=conv_db_id,
                    user_id=user_id,
                    messages_history=messages_history
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

    async def stream_message(
        self,
        message: str,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        preferences: Optional[List[str]] = None
    ):
        """
        Streams assistant execution via Server-Sent Events (SSE).
        For conversational queries: yields live tokens directly as generated by the LLM provider.
        For multi-agent mission queries: streams status updates through each phase and delivers the synthesized response.
        Persists message history to database and updates cognitive memory.
        """
        import asyncio
        msg_id = str(uuid.uuid4())
        now = datetime.utcnow()

        user_uuid = None
        if user_id:
            try:
                user_uuid = uuid.UUID(user_id) if len(user_id) == 36 else uuid.uuid5(uuid.NAMESPACE_DNS, user_id)
            except ValueError:
                user_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, user_id)

        conv_db_id = None
        async with async_session() as db:
            if conversation_id:
                try:
                    conv_uuid = uuid.UUID(conversation_id)
                    result = await db.execute(select(Conversation).where(Conversation.id == conv_uuid))
                    conv_obj = result.scalars().first()
                    if conv_obj:
                        conv_db_id = str(conv_obj.id)
                except Exception:
                    pass

            if not conv_db_id:
                target_uuid = None
                if conversation_id:
                    try:
                        target_uuid = uuid.UUID(conversation_id)
                    except Exception:
                        pass
                if not target_uuid:
                    target_uuid = uuid.uuid4()

                if user_uuid:
                    new_conv = Conversation(
                        id=target_uuid,
                        user_id=user_uuid,
                        title=message[:60],
                        metadata_json={}
                    )
                    db.add(new_conv)
                    await db.flush()
                    conv_db_id = str(new_conv.id)
                else:
                    conv_db_id = str(target_uuid)

            if user_uuid:
                try:
                    user_msg_db = Message(
                        conversation_id=uuid.UUID(conv_db_id),
                        sender_type="user",
                        sender_name="user",
                        content=message,
                        timestamp=now
                    )
                    db.add(user_msg_db)
                    await db.flush()
                except Exception as e:
                    logger.warning(f"ChatService stream: Could not store user message: {e}")

            await db.commit()

        messages_history = await self._load_conversation_history(conv_db_id)
        intent = ChatIntentClassifier.classify(message, messages_history)

        full_content = ""
        try:
            if intent == "conversation":
                status_chunk = ChatStreamChunk(
                    event="status_update",
                    conversation_id=conv_db_id,
                    message_id=msg_id,
                    status_message="Formulating response...",
                    progress_percentage=20
                )
                yield f"data: {status_chunk.model_dump_json()}\n\n"

                async for token in ConversationEngine.stream_response(
                    message=message,
                    conversation_id=conv_db_id,
                    user_id=user_id,
                    messages_history=messages_history
                ):
                    full_content += token
                    chunk = ChatStreamChunk(
                        event="assistant_stream",
                        conversation_id=conv_db_id,
                        message_id=msg_id,
                        content=token
                    )
                    yield f"data: {chunk.model_dump_json()}\n\n"

            else:
                steps = [
                    (20, "Analyzing user intent & objectives..."),
                    (40, "Coordinating specialized agents..."),
                    (70, "Executing tasks & synthesizing results..."),
                    (90, "Verifying quality and final deliverable...")
                ]
                for pct, step_msg in steps:
                    chunk = ChatStreamChunk(
                        event="status_update",
                        conversation_id=conv_db_id,
                        message_id=msg_id,
                        status_message=step_msg,
                        progress_percentage=pct
                    )
                    yield f"data: {chunk.model_dump_json()}\n\n"
                    await asyncio.sleep(0.02)

                goal_obj = None
                mission_result = None
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
                    except Exception as e:
                        logger.warning(f"ChatService stream: Goal creation note: {e}")

                if goal_obj:
                    try:
                        mission_result = await self.mission_executor.execute_mission(str(goal_obj.id))
                    except Exception as e:
                        logger.error(f"ChatService stream: Mission error: {e}")

                if mission_result:
                    full_content = ResponseFormatter.format_mission_result(mission_result, message)
                else:
                    full_content = await ConversationEngine.generate_response(
                        message=message,
                        conversation_id=conv_db_id,
                        user_id=user_id,
                        messages_history=messages_history
                    )

                import re
                tokens = re.findall(r'(\S+\s*)', full_content) or [full_content]
                for i in range(0, len(tokens), 3):
                    chunk_text = "".join(tokens[i:i+3])
                    chunk = ChatStreamChunk(
                        event="assistant_stream",
                        conversation_id=conv_db_id,
                        message_id=msg_id,
                        content=chunk_text
                    )
                    yield f"data: {chunk.model_dump_json()}\n\n"

            completed_chunk = ChatStreamChunk(
                event="mission_completed",
                conversation_id=conv_db_id,
                message_id=msg_id,
                status_message="Done.",
                progress_percentage=100
            )
            yield f"data: {completed_chunk.model_dump_json()}\n\n"

        except (asyncio.CancelledError, GeneratorExit):
            logger.info(f"ChatService: Client cancelled stream for conversation '{conv_db_id}'")
            return
        except Exception as e:
            logger.error(f"ChatService: Stream generation error: {e}")
            err_chunk = ChatStreamChunk(
                event="assistant_stream",
                conversation_id=conv_db_id,
                message_id=msg_id,
                content=f"\n\n[Stream Error] {str(e)}"
            )
            yield f"data: {err_chunk.model_dump_json()}\n\n"
        finally:
            if full_content:
                async with async_session() as db:
                    try:
                        conv_uuid = uuid.UUID(conv_db_id)
                        asst_msg_db = Message(
                            conversation_id=conv_uuid,
                            sender_type="assistant",
                            sender_name="agentx",
                            content=full_content,
                            timestamp=datetime.utcnow()
                        )
                        db.add(asst_msg_db)
                        await db.commit()
                    except Exception as e:
                        logger.warning(f"ChatService: Could not persist stream assistant message: {e}")

                try:
                    await self.memory_manager.store_memory(
                        content=f"User: {message}\nAssistant: {full_content[:200]}",
                        user_id=user_id,
                        metadata={"conversation_id": conv_db_id, "category": "conversation"}
                    )
                except Exception as e:
                    logger.debug(f"ChatService: Memory note: {e}")

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
