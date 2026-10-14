import re
import uuid
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from loguru import logger
from sqlalchemy.future import select

from database.connection import async_session
from database.models import User

# In-memory nickname registry keyed by user_id or conversation_id
_USER_NICKNAMES: Dict[str, str] = {}

class ConversationEngine:
    """
    Layer 1 — Conversation Engine for AgentX.
    Handles fast, natural human conversation (< 500 ms) without invoking the heavy multi-agent mission pipeline.
    Preserves conversational memory, user nickname state, and context across message turns.
    """

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
                # Exclude common words
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
        name_direct = nickname if nickname else "there"

        # 2. Nickname setting confirmation
        if any(p in msg_clean for p in ['my name is', 'my nickname is', 'call me']):
            if nickname:
                return f"Nice to meet you, {nickname}! 👋 I've saved your nickname. How can I help you today?"

        # 3. Time & Date Queries
        time_tokens = ['what is the time', 'what time is it', 'tell me the time', 'current time', 'whats the time', "what's the time", 'time now', 'time']
        date_tokens = ['what is the date', 'what date is it', 'whats the date', "what's the date", 'today date', "today's date", 'what day is it', 'what day is today', 'tell me the date', 'current date', 'date today', 'date']

        if any(t in msg_clean for t in time_tokens) and not any(k in msg_clean for k in ['date', 'calendar']):
            now = datetime.now()
            return f"🕒 The current time is **{now.strftime('%I:%M:%S %p')}** ({now.strftime('%A, %B %d, %Y')})."

        if any(d in msg_clean for d in date_tokens):
            now = datetime.now()
            return f"📅 Today's date is **{now.strftime('%A, %B %d, %Y')}**."

        # 4. Greetings
        greetings = {'hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 'greetings', 'sup', 'yo', 'hi there', 'hello there'}
        if msg_clean in greetings or any(msg_clean == g for g in greetings) or any(msg_clean.startswith(g + " ") for g in greetings):
            return f"Hello{name_greeting}! 👋\nWelcome back. How can I help you today?"

        # 5. Thanks
        thanks = {'thanks', 'thank you', 'thanks a lot', 'thx', 'thank u', 'many thanks', 'appreciate it'}
        if any(msg_clean == t or msg_clean.startswith(t + " ") for t in thanks):
            return f"You're very welcome{name_greeting}! Happy to help. Let me know if you need anything else."

        # 6. Farewell
        farewells = {'bye', 'goodbye', 'good night', 'see ya', 'see you', 'take care'}
        if any(msg_clean == f or msg_clean.startswith(f + " ") for f in farewells):
            return f"Goodbye{name_greeting}! Have a wonderful day!"

        # 7. Identity & Capabilities
        identity = {'who are you', 'what is your name', 'introduce yourself', 'what are you', 'tell me about yourself'}
        if any(i in msg_clean for i in identity):
            return f"I'm AgentX, your autonomous AI assistant. I can help you answer questions, organize plans, write code, research topics, and streamline your workflow. What would you like to work on today?"

        # 8. How are you / Status
        how_are_you = {'how are you', 'how are u', 'how r u', 'how is it going', 'how do you do', 'whats up', "what's up"}
        if any(h in msg_clean for h in how_are_you):
            return f"I'm doing great, thank you for asking{name_greeting}! What can I help you with today?"

        # 9. Acknowledgements & Contextual Continuations ("yes", "no", "ok", "sure", etc.)
        acks_yes = {'yes', 'yep', 'yeah', 'sure', 'ok', 'okay', 'alright', 'certainly', 'absolutely'}
        acks_no = {'no', 'nope', 'nah', 'not now', 'negative'}

        if msg_clean in acks_yes:
            # Look up last assistant message to continue contextually
            last_assistant_msg = ""
            if messages_history:
                for m in reversed(messages_history):
                    if m.get('role') == 'assistant' and m.get('content'):
                        last_assistant_msg = m.get('content')
                        break
            if last_assistant_msg:
                return f"Sounds great! Let's proceed with that. What specific details would you like to add or refine?"
            return f"Great! How would you like to proceed?"

        if msg_clean in acks_no:
            return f"No problem at all! Let me know whenever you're ready or if you'd like to try something else."

        # 10. General conversational fallback
        return f"I'm here to help! Could you share a bit more detail on what you'd like to accomplish?"
