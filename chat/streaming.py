import json
import asyncio
from typing import Dict, Any, AsyncGenerator
from loguru import logger
from chat.schemas import ChatStreamChunk

class ChatStreamer:
    """
    Chat Streamer for AgentX.
    Streams ONLY assistant text and human-friendly status updates ("Understanding your request...",
    "Planning your trip...", "Preparing recommendations...").
    Never streams raw backend logs or agent names to normal users.
    """

    HUMAN_STATUS_STEPS = [
        (15, "Understanding your request & objectives..."),
        (35, "Formulating multi-step strategy..."),
        (60, "Gathering facts & analyzing recommendations..."),
        (85, "Reflecting & verifying deliverable quality..."),
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
        intent = ChatIntentClassifier.classify(final_content)
        is_casual = (intent == "conversation") or any(final_content.strip().startswith(prefix) for prefix in ["Hello", "You're", "Goodbye", "I'm AgentX", "Great to see you", "🕒", "📅", "Nice to meet you", "Sounds great", "No problem", "I'm here to help"])

        # 1. Stream human-friendly status updates (skip for casual responses)
        if not is_casual:
            for pct, step_msg in cls.HUMAN_STATUS_STEPS[:-1]:
                chunk = ChatStreamChunk(
                    event="status_update",
                    conversation_id=conversation_id,
                    message_id=message_id,
                    status_message=step_msg,
                    progress_percentage=pct
                )
                yield f"data: {chunk.model_dump_json()}\n\n"
                await asyncio.sleep(0.08)

        # 2. Stream assistant text in clean word chunks
        words = final_content.split(" ")
        accumulated = ""
        for i in range(0, len(words), 3):
            chunk_words = words[i:i + 3]
            chunk_text = " ".join(chunk_words) + (" " if i + 3 < len(words) else "")
            accumulated += chunk_text

            chunk = ChatStreamChunk(
                event="assistant_stream",
                conversation_id=conversation_id,
                message_id=message_id,
                content=chunk_text
            )
            yield f"data: {chunk.model_dump_json()}\n\n"
            await asyncio.sleep(0.05)

        # 3. Stream completion event
        final_chunk = ChatStreamChunk(
            event="mission_completed",
            conversation_id=conversation_id,
            message_id=message_id,
            status_message="Done.",
            progress_percentage=100
        )
        yield f"data: {final_chunk.model_dump_json()}\n\n"
