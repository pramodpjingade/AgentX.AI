import re
import json
import asyncio
from typing import Dict, Any, AsyncGenerator
from loguru import logger
from chat.schemas import ChatStreamChunk

class ChatStreamer:
    """
    Chat Streamer for AgentX.
    Streams assistant text and human-friendly status updates ("Understanding your request...",
    "Planning your trip...", "Preparing recommendations...").
    Preserves all Markdown code blocks, indentation, and newlines exactly as generated.
    Never streams raw backend logs or internal agent names to normal users.
    """

    HUMAN_STATUS_STEPS = [
        (15, "Understanding your request & objectives..."),
        (35, "Formulating execution strategy..."),
        (60, "Gathering facts & analyzing results..."),
        (85, "Reflecting & verifying quality..."),
        (95, "Finalizing your assistant deliverable..."),
        (100, "Done.")
    ]

    @classmethod
    async def generate_chat_stream(
        cls,
        conversation_id: str,
        message_id: str,
        final_content: str,
        user_message: str = ""
    ) -> AsyncGenerator[str, None]:
        """Generates Server-Sent Events (SSE) stream of human-friendly progress followed by assistant text."""
        from chat.intent_classifier import ChatIntentClassifier
        intent = ChatIntentClassifier.classify(user_message or final_content)
        is_casual = (intent == "conversation") or any(
            final_content.strip().startswith(prefix) 
            for prefix in ["Hello", "You're", "Goodbye", "I'm AgentX", "🕒", "📅", "Nice to meet you", "Sounds great", "Understood", "No problem"]
        )

        # 1. Stream human-friendly status updates (skip for casual direct responses)
        if not is_casual and intent == "mission":
            for pct, step_msg in cls.HUMAN_STATUS_STEPS[:-1]:
                chunk = ChatStreamChunk(
                    event="status_update",
                    conversation_id=conversation_id,
                    message_id=message_id,
                    status_message=step_msg,
                    progress_percentage=pct
                )
                yield f"data: {chunk.model_dump_json()}\n\n"
                await asyncio.sleep(0.04)

        # 2. Stream assistant text in chunks, perfectly preserving newlines and indentation
        pattern = re.compile(r'(\S+\s*)')
        tokens = pattern.findall(final_content)
        if not tokens and final_content:
            tokens = [final_content]

        chunk_size = 3
        for i in range(0, len(tokens), chunk_size):
            chunk_text = "".join(tokens[i:i + chunk_size])

            chunk = ChatStreamChunk(
                event="assistant_stream",
                conversation_id=conversation_id,
                message_id=message_id,
                content=chunk_text
            )
            yield f"data: {chunk.model_dump_json()}\n\n"
            await asyncio.sleep(0.02)

        # 3. Stream completion event
        final_chunk = ChatStreamChunk(
            event="mission_completed",
            conversation_id=conversation_id,
            message_id=message_id,
            status_message="Done.",
            progress_percentage=100
        )
        yield f"data: {final_chunk.model_dump_json()}\n\n"
