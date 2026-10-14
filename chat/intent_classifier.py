import re
from typing import Dict, Any, List, Optional
from loguru import logger

class ChatIntentClassifier:
    """
    Intelligent Request Router and Intent Classifier for AgentX Chat Pipeline.
    Distinguishes between:
    - 'conversation': Direct assistant Q&A, conceptual explanations, code generation,
      debugging, math, and casual chat (handled via direct high-performance LLM generation).
    - 'mission': Complex multi-step tasks requiring task decomposition, DAG generation,
      and multi-agent orchestration (e.g. multi-day trip itineraries, technology roadmaps,
      full-stack software blueprints, deep research reports).
    """

    CONVERSATIONAL_GREETINGS = {
        'hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening',
        'greetings', 'sup', 'yo', 'hi there', 'hello there', 'hey there'
    }

    CONVERSATIONAL_THANKS = {
        'thanks', 'thank you', 'thanks a lot', 'thx', 'thank u', 'many thanks',
        'appreciate it', 'thank you so much'
    }

    CONVERSATIONAL_FAREWELLS = {
        'bye', 'goodbye', 'good night', 'see ya', 'see you', 'catch you later', 'take care'
    }

    CONVERSATIONAL_ACKS = {
        'yes', 'no', 'ok', 'okay', 'yep', 'nope', 'sure', 'got it', 'fine',
        'cool', 'nice', 'great', 'awesome', 'alright', 'understood', 'perfect',
        'sounds good', 'right', 'exact', 'exactly', 'indeed'
    }

    CONVERSATIONAL_IDENTITY = {
        'who are you', 'what is your name', 'introduce yourself', 'what are you',
        'tell me about yourself', 'your name', 'who created you'
    }

    CONVERSATIONAL_STATUS = {
        'how are you', 'how are u', 'how r u', 'how is it going', 'how do you do',
        'whats up', "what's up", 'how have you been'
    }

    # Complex multi-step mission indicators requiring DAG decomposition & multi-agent orchestration
    MULTI_STEP_MISSION_PATTERNS = [
        r'\broadmap\b',
        r'\bitinerary\b',
        r'\bmulti-step\b',
        r'\bstep-by-step plan\b',
        r'\bproject plan\b',
        r'\bcurriculum\b',
        r'\btrip to\b',
        r'\bplan a trip\b',
        r'\bholiday in\b',
        r'\bvacation in\b',
        r'\bdeep research and\b',
        r'\bresearch .* and create a roadmap\b',
        r'\bresearch .* and plan\b',
        r'\bmulti-agent\b',
        r'\borchestrate\b'
    ]

    # Explicit direct query patterns that must NOT trigger heavy multi-agent decomposition
    DIRECT_QUERY_PATTERNS = [
        r'^what is\b',
        r'^what are\b',
        r'^who is\b',
        r'^why is\b',
        r'^why do\b',
        r'^how does\b',
        r'^how do i\b',
        r'^how to\b',
        r'^explain\b',
        r'^give me .* code\b',
        r'^give me a .* program\b',
        r'^write a .* program\b',
        r'^write a .* function\b',
        r'^write a .* script\b',
        r'^write code\b',
        r'^solve\b',
        r'^calculate\b',
        r'^tell me about\b'
    ]

    @classmethod
    def classify(cls, message: str, history: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        Classifies user prompt into 'conversation' (direct assistant) or 'mission' (multi-agent orchestration).
        """
        if not message:
            return "conversation"

        text_clean = message.strip().lower().rstrip('.!?')

        # 1. Exact match checks for conversational tokens
        if (text_clean in cls.CONVERSATIONAL_GREETINGS or 
            text_clean in cls.CONVERSATIONAL_THANKS or 
            text_clean in cls.CONVERSATIONAL_FAREWELLS or 
            text_clean in cls.CONVERSATIONAL_ACKS):
            return "conversation"

        # 2. Starts-with check for greetings & conversational phrases
        for g in cls.CONVERSATIONAL_GREETINGS:
            if text_clean == g or text_clean.startswith(g + " "):
                return "conversation"

        for t in cls.CONVERSATIONAL_THANKS:
            if text_clean == t or text_clean.startswith(t + " "):
                return "conversation"

        for f in cls.CONVERSATIONAL_FAREWELLS:
            if text_clean == f or text_clean.startswith(f + " "):
                return "conversation"

        for a in cls.CONVERSATIONAL_ACKS:
            if text_clean == a or text_clean.startswith(a + " "):
                return "conversation"

        for i in cls.CONVERSATIONAL_IDENTITY:
            if i in text_clean:
                return "conversation"

        for s in cls.CONVERSATIONAL_STATUS:
            if s in text_clean:
                return "conversation"

        # 3. Nickname settings
        if any(p in text_clean for p in ['my name is', 'my nickname is', 'call me', 'i am ']):
            if not any(k in text_clean for k in ['roadmap', 'itinerary', 'trip to']):
                return "conversation"

        # 4. Time & Date queries
        time_date_patterns = [
            'date', 'time', 'today date', "today's date", 'current date', 'current time',
            'what date', 'whats the date', "what's the date", 'tell me the date',
            'what time', 'whats the time', "what's the time", 'tell me the time',
            'what day is it', 'what day is today', 'what is today', 'day of week',
            'which date', 'which day'
        ]
        if any(p in text_clean for p in time_date_patterns):
            if not any(k in text_clean for k in ['roadmap', 'itinerary', 'trip to']):
                return "conversation"

        # 5. Check for complex multi-step mission patterns first
        for pattern in cls.MULTI_STEP_MISSION_PATTERNS:
            if re.search(pattern, text_clean):
                return "mission"

        # 6. Direct query patterns (Code, Explain, What is, Solve, etc.) -> Direct assistant
        for pattern in cls.DIRECT_QUERY_PATTERNS:
            if re.search(pattern, text_clean):
                return "conversation"

        # 7. Short/Medium technical questions -> Direct assistant
        words = text_clean.split()
        if len(words) <= 12 and not any(k in text_clean for k in ['roadmap', 'itinerary', 'trip', 'vacation', 'multi-step']):
            return "conversation"

        # 8. Default to conversation unless explicit multi-agent planning requested
        return "conversation"
