from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from database.models import Memory, is_sqlite
from loguru import logger

class LongTermMemory:
    """Manages long-term relational and semantic memory saved in PostgreSQL."""
    
    @staticmethod
    async def add_memory(
        db: AsyncSession, 
        user_id: UUID, 
        content: str, 
        memory_type: str = "semantic",
        embedding: Optional[List[float]] = None
    ) -> Memory:
        """Create and store a long-term memory node."""
        new_memory = Memory(
            user_id=user_id,
            memory_type=memory_type,
            content=content,
            embedding=embedding
        )
        db.add(new_memory)
        await db.commit()
        logger.info(f"LongTermMemory: Added memory for user {user_id} - Type: {memory_type}")
        return new_memory

    @staticmethod
    async def get_memories_by_user(
        db: AsyncSession, 
        user_id: UUID,
        memory_type: Optional[str] = None
    ) -> List[Memory]:
        """Fetch all long term memories for a user."""
        query = select(Memory).where(Memory.user_id == user_id)
        if memory_type:
            query = query.where(Memory.memory_type == memory_type)
            
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def search_semantic_memories(
        db: AsyncSession,
        user_id: UUID,
        query_embedding: List[float],
        limit: int = 5
    ) -> List[Memory]:
        """Search similar memories using pgvector similarity search, falling back to basic select on SQLite."""
        if is_sqlite:
            # SQLite fallback: return recent memories (unable to calculate vector distance dynamically in basic SQLite)
            logger.warning("LongTermMemory: Running semantic search on SQLite. Falling back to recent memory fetch.")
            query = select(Memory).where(
                Memory.user_id == user_id, 
                Memory.memory_type == "semantic"
            ).limit(limit)
            result = await db.execute(query)
            return list(result.scalars().all())
            
        else:
            # PostgreSQL pgvector L2 distance / Cosine distance search
            # `<->` operator calculates Euclidean distance
            query = select(Memory).where(
                Memory.user_id == user_id,
                Memory.memory_type == "semantic"
            ).order_by(
                Memory.embedding.l2_distance(query_embedding)
            ).limit(limit)
            
            result = await db.execute(query)
            return list(result.scalars().all())
