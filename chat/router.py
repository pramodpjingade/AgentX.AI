from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from loguru import logger

from chat.schemas import ChatRequest, StandardChatResponse, ConversationHistory
from chat.controller import ChatController
from chat.streaming import ChatStreamer
from authentication.jwt_handler import get_current_user
from database.models import User

router = APIRouter()
controller = ChatController()

@router.post("", response_model=StandardChatResponse, summary="Send message to AgentX AI Operating System")
async def send_chat_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Official Authoritative User Chat Gateway Endpoint.
    Sends user prompt to AgentX AI Core and returns standardized assistant response object.
    """
    user_id = str(current_user.id)
    logger.info(f"CHAT_TRACE_START conversation_id={request.conversation_id} user_id={user_id} message='{request.message[:40]}' endpoint=/chat route=send_chat_message")
    
    response = await controller.process_chat_message(request, user_id=user_id)
    
    logger.info(f"CHAT_TRACE_RESPONSE conversation_id={response.conversation_id} message_id={response.message_id} status={response.status}")
    return response

@router.post("/stream", summary="Stream message execution via Server-Sent Events (SSE)")
async def stream_chat_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Streams assistant response text via Server-Sent Events (SSE).
    """
    user_id = str(current_user.id)
    logger.info(f"CHAT_TRACE_START conversation_id={request.conversation_id} user_id={user_id} message='{request.message[:40]}' endpoint=/chat/stream route=stream_chat_message")
    
    response = await controller.process_chat_message(request, user_id=user_id)

    logger.info(f"CHAT_TRACE_RESPONSE conversation_id={response.conversation_id} message_id={response.message_id} status={response.status}")
    return StreamingResponse(
        ChatStreamer.generate_chat_stream(
            conversation_id=response.conversation_id,
            message_id=response.message_id,
            final_content=response.content,
            user_message=request.message
        ),
        media_type="text/event-stream"
    )

@router.get("/history", summary="List user conversation threads")
async def get_chat_history(
    current_user: User = Depends(get_current_user)
):
    """Lists all active user conversation threads."""
    user_id = str(current_user.id)
    return await controller.get_history(user_id=user_id)

@router.get("/{conversation_id}", summary="Get conversation detail")
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user)
):
    """Retrieves conversation thread by ID."""
    conv = await controller.get_conversation_detail(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation thread not found.")
    return conv

@router.delete("/{conversation_id}", summary="Delete conversation thread")
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user)
):
    """Deletes conversation thread."""
    success = await controller.delete_conversation(conversation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation thread not found.")
    return {"message": "Conversation deleted successfully."}

@router.post("/{conversation_id}/regenerate", response_model=StandardChatResponse, summary="Regenerate last assistant message")
async def regenerate_message(
    conversation_id: str,
    current_user: User = Depends(get_current_user)
):
    """Regenerates the last assistant response for a conversation thread."""
    conv = await controller.get_conversation_detail(conversation_id)
    if not conv or not conv.get("messages"):
        raise HTTPException(status_code=404, detail="Conversation not found or empty.")

    # Find last user message
    user_msg = "Regenerate request"
    for m in reversed(conv["messages"]):
        if m.get("role") == "user":
            user_msg = m.get("content", user_msg)
            break

    user_id = str(current_user.id)
    request = ChatRequest(message=user_msg, conversation_id=conversation_id)
    return await controller.process_chat_message(request, user_id=user_id)
