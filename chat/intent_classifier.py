import re
from typing import Dict, Any, List, Optional
from loguru import logger

class ChatIntentClassifier:
    """
    Lightweight Intent Classifier for AgentX Chat Pipeline.
    Determines whether a message is standard human conversation ("conversation")
    or an actionable task requiring multi-agent execution ("mission").
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

    MISSION_KEYWORDS = {
        'plan', 'build', 'create', 'generate', 'write', 'code', 'research',
        'analyze', 'summarize', 'explain', 'design', 'make', 'draft', 'calculate',
        'audit', 'develop', 'setup', 'solve', 'formulate', 'roadmap', 'curriculum',
        'itinerary', 'strategy', 'website', 'api', 'workout', 'diet', 'script',
        'report', 'document', 'pdf', 'presentation', 'diagram', 'chart', 'test',
        'pipeline', 'database', 'backend', 'frontend', 'app', 'system', 'portfolio'
    }

    @classmethod
    def classify(cls, message: str, history: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        Classifies user prompt into 'conversation' or 'mission'.
        """
        if not message:
            return "conversation"

        text_clean = message.strip().lower().rstrip('.!?')

        # 1. Exact match checks for conversational tokens
        if text_clean in cls.CONVERSATIONAL_GREETINGS or text_clean in cls.CONVERSATIONAL_THANKS or text_clean in cls.CONVERSATIONAL_FAREWELLS or text_clean in cls.CONVERSATIONAL_ACKS:
            return "conversation"

        # 2. Starts-with / contains check for greetings & casual responses
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

        # 3. Check for Nickname Setters ("my nickname is...", "my name is...", "call me...")
        if any(p in text_clean for p in ['my name is', 'my nickname is', 'call me', 'i am ']):
            if not any(k in text_clean for k in ['build', 'create', 'write code', 'plan']):
                return "conversation"

        # 4. Check for Time & Date queries
        time_date_patterns = [
            'date', 'time', 'today date', "today's date", 'current date', 'current time',
            'what date', 'whats the date', "what's the date", 'tell me the date',
            'what time', 'whats the time', "what's the time", 'tell me the time',
            'what day is it', 'what day is today', 'what is today', 'day of week',
            'which date', 'which day'
        ]
        if any(p in text_clean for p in time_date_patterns):
            if not any(k in text_clean for k in ['build', 'create', 'code', 'develop', 'script']):
                return "conversation"

        # 5. Word token check for mission task keywords
        words = set(re.findall(r'\b\w+\b', text_clean))
        if words.intersection(cls.MISSION_KEYWORDS):
            return "mission"

        # 6. Length and structure heuristic: short simple queries default to conversation
        if len(text_clean.split()) <= 4 and not any(kw in text_clean for kw in ['plan', 'code', 'trip', 'build', 'create']):
            return "conversation"

        return "mission"
