from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from loguru import logger

from database.models import KnowledgeDocument, is_sqlite
from rag.embeddings import EmbeddingGenerator

class KnowledgeRetriever:
    """Manages document chunking, indexing, and vector semantic retrieval."""
    
    def __init__(self):
        self.embedding_generator = EmbeddingGenerator()

    async def ingest_document(
        self, 
        db: AsyncSession, 
        title: str, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> KnowledgeDocument:
        """Generate embeddings for document content and save to the database."""
        logger.info(f"KnowledgeRetriever: Ingesting document '{title}'")
        
        # Generate 1536-dim embedding vector
        embedding = await self.embedding_generator.generate_embedding(content)
        
        new_doc = KnowledgeDocument(
            title=title,
            content=content,
            metadata_json=metadata or {},
            embedding=embedding
        )
        db.add(new_doc)
        await db.commit()
        logger.info(f"KnowledgeRetriever: Successfully indexed document '{title}'")
        return new_doc

    async def retrieve_relevant_chunks(
        self, 
        db: AsyncSession, 
        query: str, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Query vector database for similar content chunks."""
        logger.info(f"KnowledgeRetriever: Retrieving content for query '{query}'")
        
        if is_sqlite:
            # SQLite fallback: Keyword search via LIKE query
            logger.warning("KnowledgeRetriever: Running keyword query fallback on SQLite.")
            search_pattern = f"%{query}%"
            stmt = select(KnowledgeDocument).where(
                KnowledgeDocument.content.like(search_pattern) | 
                KnowledgeDocument.title.like(search_pattern)
            ).limit(limit)
            
            result = await db.execute(stmt)
            docs = result.scalars().all()
            
        else:
            # PostgreSQL pgvector similarity query
            query_embedding = await self.embedding_generator.generate_embedding(query)
            
            # Distance comparison `<->`
            stmt = select(KnowledgeDocument).order_by(
                KnowledgeDocument.embedding.l2_distance(query_embedding)
            ).limit(limit)
            
            result = await db.execute(stmt)
            docs = result.scalars().all()
            
        # Format results
        return [
            {
                "id": str(doc.id),
                "title": doc.title,
                "content": doc.content,
                "metadata": doc.metadata_json
            }
            for doc in docs
        ]
