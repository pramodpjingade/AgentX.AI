from typing import Dict, Any, List, Optional
from loguru import logger
from chat.service import ChatService
from chat.schemas import ChatRequest, StandardChatResponse, ConversationHistory

class ChatController:
    """
    Chat Controller for AgentX.
    Handles request validation, auth delegation, conversation history queries,
    error recovery, and delegates directly to ChatService. No business logic.
    """

    def __init__(self):
        self.service = ChatService()

    async def process_chat_message(self, request: ChatRequest, user_id: Optional[str] = None) -> StandardChatResponse:
        """Processes incoming user chat message."""
        return await self.service.process_message(
            message=request.message,
            user_id=user_id,
            conversation_id=request.conversation_id,
            streaming=request.streaming,
            preferences=request.preferences
        )

    async def get_history(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lists user conversation threads from DB."""
        return await self.service.list_conversations(user_id=user_id)

    async def get_conversation_detail(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves single conversation thread detail from DB."""
        return await self.service.get_conversation(conversation_id)

    async def delete_conversation(self, conversation_id: str) -> bool:
        """Deletes a conversation thread from DB."""
        return await self.service.delete_conversation(conversation_id)
