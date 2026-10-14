import asyncio
import os
import sys
from uuid import uuid4
from sqlalchemy.future import select

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import engine, async_session
from database.models import User, ModelRouterLog, PluginVersion
from agents.model_manager import ModelManager

async def test_sprint1_integration():
    print("\n==================================================")
    print("RUNNING SPRINT 1 INTEGRATION TEST SUITE")
    print("==================================================")
    
    # 1. Setup Test User
    async with async_session() as db:
        print("\n[Step 1] Creating a developer test user...")
        # Clean existing test user if any
        stmt = select(User).where(User.email == "dev_tester@agentx.ai")
        result = await db.execute(stmt)
        user = result.scalars().first()
        
        if not user:
            user = User(
                email="dev_tester@agentx.ai",
                hashed_password="hashed_developer_password",
                role="developer"
            )
            db.add(user)
            await db.commit()
            print("Developer test user created successfully.")
        else:
            print("Developer test user already exists.")
            
    # 2. Test Model Manager Router and Alias Mapping
    print("\n[Step 2] Testing Model Router Alias queries...")
    model_manager = ModelManager()
    
    # Let's route simple prompt via FAST_MODEL alias
    prompt_fast = "Hello, what is 2+2?"
    print(f"Routing query: '{prompt_fast}' via FAST_MODEL...")
    response_fast = await model_manager.generate(
        prompt=prompt_fast,
        provider="FAST_MODEL",
        task_id=str(uuid4())
    )
    print(f"FAST_MODEL response: '{response_fast.strip()}'")
    
    # Let's route complex coding query via CODING_MODEL alias
    prompt_coding = "Write a python function to print hello world."
    print(f"\nRouting query: '{prompt_coding}' via CODING_MODEL...")
    response_coding = await model_manager.generate(
        prompt=prompt_coding,
        provider="CODING_MODEL",
        task_id=str(uuid4())
    )
    print("CODING_MODEL query complete.")

    # 3. Verify Model Router logs persistence
    print("\n[Step 3] Verifying Model Router Database Logs...")
    async with async_session() as db:
        stmt = select(ModelRouterLog).order_by(ModelRouterLog.created_at.desc()).limit(2)
        result = await db.execute(stmt)
        logs = result.scalars().all()
        
        print(f"Found {len(logs)} model log entries in database.")
        for log in logs:
            cost = log.cost.get("usd") if log.cost else 0.0
            print(f"  - Log: Provider: {log.provider}, Model: {log.model_name}, Latency: {log.latency_ms}ms, Est. Cost: ${cost:.6f}, Status: {log.status}")
            
        assert len(logs) >= 2, "Error: Expected at least 2 model logs to be persisted."
        print("Model log persistence successfully verified!")

    # 4. Test Dynamic Plugin Marketplace registrations
    print("\n[Step 4] Testing Plugin Marketplace dynamic registration...")
    plugin_name = "stock_analysis_agent"
    plugin_version = "1.0.0"
    
    async with async_session() as db:
        # Clean existing plugin if any
        stmt = select(PluginVersion).where(
            PluginVersion.plugin_name == plugin_name,
            PluginVersion.version == plugin_version
        )
        result = await db.execute(stmt)
        existing_plugin = result.scalars().first()
        if existing_plugin:
            await db.delete(existing_plugin)
            await db.commit()
            print(f"Cleaned up previous version of plugin '{plugin_name}'.")

        # Install dynamic plugin
        print(f"Installing plugin '{plugin_name}' version '{plugin_version}'...")
        new_plugin = PluginVersion(
            plugin_name=plugin_name,
            version=plugin_version,
            dependencies=["research_agent"],
            min_agentx_version="1.0.0"
        )
        db.add(new_plugin)
        await db.commit()
        
        # Verify active plugin exists
        stmt = select(PluginVersion).where(
            PluginVersion.plugin_name == plugin_name,
            PluginVersion.is_active == True
        )
        result = await db.execute(stmt)
        active_plugin = result.scalars().first()
        assert active_plugin is not None, "Error: Installed plugin was not found active in database."
        print(f"Plugin '{plugin_name}' installed and active verification passed.")

        # Uninstall dynamic plugin (set active = False)
        print(f"Uninstalling plugin '{plugin_name}'...")
        active_plugin.is_active = False
        await db.commit()

        # Verify plugin is now inactive
        stmt = select(PluginVersion).where(
            PluginVersion.plugin_name == plugin_name,
            PluginVersion.is_active == True
        )
        result = await db.execute(stmt)
        active_plugin = result.scalars().first()
        assert active_plugin is None, "Error: Uninstalled plugin should not be found active."
        print(f"Plugin '{plugin_name}' uninstall verification passed.")

    print("\n==================================================")
    print("SPRINT 1 INTEGRATION TEST SUITE: ALL TESTS PASSED!")
    print("==================================================")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_sprint1_integration())
