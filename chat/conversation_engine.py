import re
import uuid
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from loguru import logger
from sqlalchemy.future import select

from database.connection import async_session
from database.models import User
from agents.model_manager import ModelManager

# In-memory nickname registry keyed by user_id or conversation_id
_USER_NICKNAMES: Dict[str, str] = {}

class ConversationEngine:
    """
    Layer 1 — Conversation & Direct Assistant Engine for AgentX.
    Handles direct AI responses (< 1s) without invoking the heavy multi-agent mission pipeline.
    Preserves conversational memory, user nickname state, and context across message turns.
    Integrates genuine LLM generation for coding, conceptual explanations, reasoning, and technical Q&A.
    """

    DIRECT_SYSTEM_PROMPT = """You are AgentX, a principal autonomous AI assistant.
Provide direct, articulate, and accurate answers.
When generating code:
- Provide complete, self-contained, working implementations.
- Always wrap code in proper Markdown code blocks with appropriate language tags (e.g., ```c, ```python, ```bash).
- Maintain correct indentation, idiomatic syntax, and clear explanations.
Do not output internal agent tags, debug headers, or raw Python dictionaries."""

    @classmethod
    def get_nickname(cls, user_id: Optional[str] = None, conv_id: Optional[str] = None) -> Optional[str]:
        """Retrieves stored user nickname."""
        if user_id and user_id in _USER_NICKNAMES:
            return _USER_NICKNAMES[user_id]
        if conv_id and conv_id in _USER_NICKNAMES:
            return _USER_NICKNAMES[conv_id]
        return None

    @classmethod
    def set_nickname(cls, nickname: str, user_id: Optional[str] = None, conv_id: Optional[str] = None):
        """Stores user nickname in memory state."""
        clean_nick = nickname.strip().strip('.!,')
        if clean_nick:
            if user_id:
                _USER_NICKNAMES[user_id] = clean_nick
            if conv_id:
                _USER_NICKNAMES[conv_id] = clean_nick

    @classmethod
    async def extract_and_store_nickname(cls, message: str, user_id: Optional[str] = None, conv_id: Optional[str] = None) -> Optional[str]:
        """Detects nickname setting patterns ('my name is X', 'my nickname is X', 'call me X')."""
        msg_lower = message.lower()
        patterns = [
            r'my nickname is ([a-zA-Z0-9_\- ]+)',
            r'my name is ([a-zA-Z0-9_\- ]+)',
            r'call me ([a-zA-Z0-9_\- ]+)',
            r'i am ([a-zA-Z0-9_\- ]+)'
        ]

        for p in patterns:
            match = re.search(p, msg_lower)
            if match:
                raw_name = match.group(1).strip()
                if raw_name not in ['ready', 'here', 'a developer', 'a user', 'busy', 'fine', 'good']:
                    name_capitalized = raw_name.title()
                    cls.set_nickname(name_capitalized, user_id, conv_id)
                    return name_capitalized

        return cls.get_nickname(user_id, conv_id)

    @classmethod
    async def generate_response(
        cls,
        message: str,
        conversation_id: str,
        user_id: Optional[str] = None,
        messages_history: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Generates a fast, contextual, natural assistant reply.
        Routes trivial greetings and date/time checks locally, and routes all other queries
        directly through the high-performance unified ModelManager.
        """
        msg_clean = message.strip().lower().rstrip('.!?')

        # 1. Extract and update nickname if provided
        nickname = await cls.extract_and_store_nickname(message, user_id, conversation_id)

        # Lookup User.nickname from database if user_id is given
        if not nickname and user_id and len(user_id) >= 8:
            try:
                async with async_session() as db:
                    u_id = uuid.UUID(user_id) if len(user_id) == 36 else uuid.uuid5(uuid.NAMESPACE_DNS, user_id)
                    stmt = select(User).where(User.id == u_id)
                    res = await db.execute(stmt)
                    usr = res.scalars().first()
                    if usr and getattr(usr, 'nickname', None):
                        nickname = usr.nickname
                        cls.set_nickname(nickname, user_id, conversation_id)
            except Exception as e:
                logger.debug(f"Nickname resolution note: {e}")

        name_greeting = f", {nickname}" if nickname else ""

        # 2. Nickname setting confirmation
        if any(p in msg_clean for p in ['my name is', 'my nickname is', 'call me']):
            if nickname:
                return f"Nice to meet you, {nickname}! 👋 I've saved your nickname. How can I help you today?"

        # 3. Time & Date Queries (Real local system time)
        time_tokens = ['what is the time', 'what time is it', 'tell me the time', 'current time', 'whats the time', "what's the time", 'time now', 'time']
        date_tokens = ['what is the date', 'what date is it', 'whats the date', "what's the date", 'today date', "today's date", 'what day is it', 'what day is today', 'tell me the date', 'current date', 'date today', 'date']

        if any(msg_clean == t or msg_clean.startswith(t) for t in time_tokens) and not any(k in msg_clean for k in ['date', 'calendar']):
            now = datetime.now()
            return f"🕒 The current time is **{now.strftime('%I:%M:%S %p')}** ({now.strftime('%A, %B %d, %Y')})."

        if any(msg_clean == d or msg_clean.startswith(d) for d in date_tokens):
            now = datetime.now()
            return f"📅 Today's date is **{now.strftime('%A, %B %d, %Y')}**."

        # 4. Pure Casual Greetings
        greetings = {'hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 'greetings', 'sup', 'yo', 'hi there', 'hello there'}
        if msg_clean in greetings:
            return f"Hello{name_greeting}! 👋\nWelcome back. How can I help you today?"

        # 5. Pure Thanks
        thanks = {'thanks', 'thank you', 'thanks a lot', 'thx', 'thank u', 'many thanks', 'appreciate it'}
        if msg_clean in thanks:
            return f"You're very welcome{name_greeting}! Happy to help. Let me know if you need anything else."

        # 6. Pure Farewell
        farewells = {'bye', 'goodbye', 'good night', 'see ya', 'see you', 'take care'}
        if msg_clean in farewells:
            return f"Goodbye{name_greeting}! Have a wonderful day!"

        # 7. Pure Identity
        identity = {'who are you', 'what is your name', 'introduce yourself', 'what are you', 'tell me about yourself'}
        if msg_clean in identity:
            return f"I'm AgentX, your autonomous AI assistant. I can help you answer questions, write code, explain complex concepts, research topics, and organize multi-step plans. What would you like to work on today?"

        # 8. Pure How are you / Status
        how_are_you = {'how are you', 'how are u', 'how r u', 'how is it going', 'how do you do', 'whats up', "what's up"}
        if msg_clean in how_are_you:
            return f"I'm doing great, thank you for asking{name_greeting}! How can I assist you right now?"

        # 9. Pure Acks
        acks_yes = {'yes', 'yep', 'yeah', 'sure', 'ok', 'okay', 'alright', 'certainly', 'absolutely'}
        acks_no = {'no', 'nope', 'nah', 'not now', 'negative'}
        if msg_clean in acks_yes:
            return f"Sounds great! How would you like to proceed?"
        if msg_clean in acks_no:
            return f"Understood. Let me know whenever you're ready or if you'd like to try something else."

        # 10. For ALL OTHER substantive queries: invoke ModelManager directly!
        logger.info(f"ConversationEngine: Invoking ModelManager for substantive query: '{message[:60]}'")
        model_manager = ModelManager()

        # Build prompt with conversation context if history exists
        full_prompt = message
        if messages_history and len(messages_history) > 0:
            context_snippets = []
            for m in messages_history[-4:]:
                role = "User" if m.get("role") == "user" else "Assistant"
                content = m.get("content", "")
                if content and not content.startswith("**[AgentX Configuration Required]**"):
                    context_snippets.append(f"{role}: {content[:300]}")
            if context_snippets:
                full_prompt = "Conversation Context:\n" + "\n".join(context_snippets) + f"\n\nCurrent Request:\n{message}"

        # Determine alias
        alias = model_manager.analyze_complexity(message)

        try:
            response_text = await model_manager.generate(
                prompt=full_prompt,
                system_instruction=cls.DIRECT_SYSTEM_PROMPT,
                provider=alias,
                task_id=str(uuid.uuid4())
            )
            return response_text
        except Exception as e:
            logger.error(f"ConversationEngine: Model generation error: {e}")
            return f"I encountered an error while processing your request: {str(e)}"

    @classmethod
    async def stream_response(
        cls,
        message: str,
        conversation_id: str,
        user_id: Optional[str] = None,
        messages_history: Optional[List[Dict[str, Any]]] = None
    ):
        """
        Streams generated response tokens directly from ModelManager.
        For quick conversational checks (greetings, date, time), yields instant text.
        For substantive queries, streams real tokens as they arrive from the model provider.
        """
        msg_clean = message.strip().lower().rstrip('.!?')

        # Check if query matches direct fast answers
        fast_response = None
        nickname = await cls.extract_and_store_nickname(message, user_id, conversation_id)
        name_greeting = f", {nickname}" if nickname else ""

        if any(p in msg_clean for p in ['my name is', 'my nickname is', 'call me']) and nickname:
            fast_response = f"Nice to meet you, {nickname}! 👋 I've saved your nickname. How can I help you today?"
        elif any(msg_clean == t or msg_clean.startswith(t) for t in ['what is the time', 'what time is it', 'tell me the time', 'current time', 'time']) and not any(k in msg_clean for k in ['date', 'calendar']):
            now = datetime.now()
            fast_response = f"🕒 The current time is **{now.strftime('%I:%M:%S %p')}** ({now.strftime('%A, %B %d, %Y')})."
        elif any(msg_clean == d or msg_clean.startswith(d) for d in ['what is the date', 'what date is it', 'today date', "today's date", 'current date', 'date']):
            now = datetime.now()
            fast_response = f"📅 Today's date is **{now.strftime('%A, %B %d, %Y')}**."
        elif msg_clean in {'hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 'greetings', 'sup', 'yo'}:
            fast_response = f"Hello{name_greeting}! 👋\nWelcome back. How can I help you today?"
        elif msg_clean in {'thanks', 'thank you', 'thanks a lot', 'thx', 'thank u', 'many thanks'}:
            fast_response = f"You're very welcome{name_greeting}! Happy to help. Let me know if you need anything else."
        elif msg_clean in {'bye', 'goodbye', 'good night', 'see ya', 'see you', 'take care'}:
            fast_response = f"Goodbye{name_greeting}! Have a wonderful day!"
        elif msg_clean in {'who are you', 'what is your name', 'introduce yourself', 'what are you'}:
            fast_response = "I'm AgentX, your autonomous AI assistant. I can help you answer questions, write code, explain complex concepts, research topics, and organize multi-step plans. What would you like to work on today?"

        if fast_response:
            yield fast_response
            return

        # For substantive requests: stream from ModelManager
        model_manager = ModelManager()
        full_prompt = message
        if messages_history and len(messages_history) > 0:
            context_snippets = []
            for m in messages_history[-4:]:
                role = "User" if m.get("role") == "user" else "Assistant"
                content = m.get("content", "")
                if content and not content.startswith("**[AgentX Configuration Required]**"):
                    context_snippets.append(f"{role}: {content[:300]}")
            if context_snippets:
                full_prompt = "Conversation Context:\n" + "\n".join(context_snippets) + f"\n\nCurrent Request:\n{message}"

        alias = model_manager.analyze_complexity(message)
        try:
            async for token in model_manager.stream(
                prompt=full_prompt,
                system_instruction=cls.DIRECT_SYSTEM_PROMPT,
                provider=alias
            ):
                yield token
        except Exception as e:
            logger.error(f"ConversationEngine: Streaming error: {e}")
            yield f"[Model Provider Error] {str(e)}"
