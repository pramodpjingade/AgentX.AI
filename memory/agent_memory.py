from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from loguru import logger

from database.models import Message
from memory.long_term import LongTermMemory
from agents.model_manager import ModelManager

class AgentMemoryConsolidator:
    """Consolidates short-term conversation episodes into long-term semantic facts and preferences."""
    
    def __init__(self):
        self.model_manager = ModelManager()

    async def consolidate_session_to_long_term(
        self, 
        db: AsyncSession, 
        user_id: UUID, 
        conversation_id: UUID,
        limit_messages: int = 20
    ):
        """Analyze recent conversation history, extract facts/preferences, and save to Long Term Memory."""
        logger.info(f"MemoryConsolidator: Consolidating conversation {conversation_id}...")
        
        # 1. Fetch recent messages
        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.timestamp.desc())
            .limit(limit_messages)
        )
        messages = list(result.scalars().all())
        messages.reverse()  # Chronological order
        
        if not messages:
            logger.info("MemoryConsolidator: No messages found to consolidate.")
            return
            
        # 2. Build conversation dump
        chat_dump = ""
        for m in messages:
            sender = m.sender_name or m.sender_type
            chat_dump += f"{sender}: {m.content}\n"
            
        # 3. Request LLM consolidation extraction
        prompt = f"""You are the Memory Consolidation Agent of the AgentX Multi-Agent Ecosystem.
Analyze the following recent chat conversation. Extract any key user preferences, permanent facts, goals, or learned workflows.
Only extract facts that are valuable for personalizing future interactions.

Recent Conversation:
{chat_dump}

Response Format:
Return a bulleted list of clean facts. Do not write introductory or concluding sentences. If nothing valuable is found, write 'None'.
"""
        
        extracted_facts = await self.model_manager.generate(
            prompt=prompt,
            system_instruction="You are a precise information extraction system.",
            provider="mock"  # Defaults to mock if live key not configured
        )
        
        if "None" in extracted_facts or not extracted_facts.strip():
            logger.info("MemoryConsolidator: No semantic facts to consolidate in this session.")
            return
            
        logger.info(f"MemoryConsolidator: Extracted facts for consolidation:\n{extracted_facts}")
        
        # 4. Generate embeddings and save each extracted fact
        facts_list = [f.strip("- ").strip() for f in extracted_facts.split("\n") if f.strip()]
        
        for fact in facts_list:
            if not fact:
                continue
                
            # Dummy embedding vector (1536 dim) for local fallback
            # In a live setup, we would generate this via RAG embedding pipeline (Phase 9)
            dummy_embedding = [0.0] * 1536
            
            await LongTermMemory.add_memory(
                db=db,
                user_id=user_id,
                content=fact,
                memory_type="semantic",
                embedding=dummy_embedding
            )
            
        logger.info(f"MemoryConsolidator: Consolidate session complete! Saved {len(facts_list)} facts.")
