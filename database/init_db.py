import asyncio
import sys
import os
from sqlalchemy import text

# Add the workspace root to python path to avoid import errors
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import engine, Base
from database.models import (
    User, Conversation, Message, Goal, Task, Memory, KnowledgeDocument,
    WorkflowDefinition, PluginVersion, ModelRouterLog, ApprovalRequest, MissionResult, is_sqlite
)

async def seed_development_accounts():
    from authentication.hasher import get_password_hash
    from sqlalchemy.future import select
    from database.connection import async_session
    
    accounts = [
        {"email": "developer@agentx.ai", "password": "Password123!", "role": "developer", "nickname": "DevMaster"},
        {"email": "admin@agentx.ai", "password": "Password123!", "role": "admin", "nickname": "SystemAdmin"},
        {"email": "user@agentx.ai", "password": "Password123!", "role": "user", "nickname": "Pammu"}
    ]
    
    async with async_session() as db:
        for acc in accounts:
            stmt = select(User).where(User.email == acc["email"])
            result = await db.execute(stmt)
            existing_user = result.scalars().first()
            if not existing_user:
                print(f"Seeding account: {acc['email']} with role: {acc['role']}")
                hashed_pw = get_password_hash(acc["password"])
                new_user = User(
                    email=acc["email"],
                    hashed_password=hashed_pw,
                    role=acc["role"],
                    nickname=acc.get("nickname")
                )
                db.add(new_user)
            elif not existing_user.nickname and acc.get("nickname"):
                existing_user.nickname = acc.get("nickname")
        await db.commit()

async def init_database():
    print(f"Connecting to database (SQLite Fallback: {is_sqlite}) and initializing schema...")
    async with engine.begin() as conn:
        if not is_sqlite:
            # Create pgvector extension on PostgreSQL
            print("Creating pgvector extension...")
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        else:
            print("Running in SQLite mode. Skipping pgvector extension creation.")
        
        # Create all tables
        print("Creating all tables...")
        await conn.run_sync(Base.metadata.create_all)
        
        if is_sqlite:
            try:
                await conn.execute(text("ALTER TABLE users ADD COLUMN nickname VARCHAR(100);"))
                print("Migrated SQLite schema: Added missing nickname column to users table.")
            except Exception:
                pass  # Column already exists or table freshly created with nickname
        
    print("Seeding default accounts...")
    await seed_development_accounts()
    print("Database initialization complete!")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_database())

