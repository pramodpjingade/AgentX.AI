import asyncio
import os
import sys
from uuid import uuid4

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.event_bus.event_bus import EventBus
from core.event_bus.events import AgentMessageEnvelope
from core.orchestrator.event_worker import OrchestratorEventWorker

from database.connection import async_session
from database.models import Goal, User
from core.orchestrator.workflow_engine import WorkflowEngine
from uuid import UUID
from sqlalchemy.future import select

async def test_sprint5_event_driven_core():
    print("\n==================================================")
    print("RUNNING SPRINT 5 EVENT BUS INTEGRATION TEST SUITE")
    print("==================================================")

    # 1. Initialize Event Bus and Worker
    print("[Step 1] Initializing EventBus singleton and starting OrchestratorEventWorker...")
    event_bus = EventBus()
    await event_bus.connect()
    
    worker = OrchestratorEventWorker()
    await worker.start()

    # 2. Setup verification listener for final workflow completion
    completion_received = asyncio.Event()
    received_envelope = None

    async def workflow_completed_callback(event: AgentMessageEnvelope):
        nonlocal received_envelope
        print(f"Callback: Received 'workflow.completed' event. Correlation ID: {event.correlation_id}")
        received_envelope = event
        completion_received.set()

    print("[Step 2] Subscribing test callback to 'workflow.completed' topic...")
    await event_bus.subscribe("workflow.completed", workflow_completed_callback)

    # 3. Create Goal in DB & Formulate/Publish GoalCreated event
    goal_id_uuid = uuid4()
    correlation_id = str(goal_id_uuid)
    print(f"\n[Step 3] Seeding test Goal in DB and publishing GoalCreated event envelope with correlation ID: {correlation_id}...")
    
    async with async_session() as db:
        user_stmt = select(User).where(User.email == "dev_tester@agentx.ai")
        user_res = await db.execute(user_stmt)
        user = user_res.scalars().first()
        if not user:
            user = User(
                email="dev_tester@agentx.ai",
                hashed_password="hashed_developer_password",
                role="developer"
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)

        new_goal = Goal(
            id=goal_id_uuid,
            user_id=user.id,
            title="Build a Simple JSON Sales File Validator",
            description="Create a script to load, check properties, and log summaries.",
            status="created"
        )
        db.add(new_goal)
        await db.commit()

    engine = WorkflowEngine()
    await engine.register_workflow(correlation_id)

    goal_event = AgentMessageEnvelope(
        source_agent="gateway",
        target_agent="supervisor_agent",
        event_type="GoalCreated",
        correlation_id=correlation_id,
        payload={
            "goal_title": "Build a Simple JSON Sales File Validator",
            "goal_description": "Create a script to load, check properties, and log summaries."
        }
    )
    
    await event_bus.publish("goal.created", goal_event)

    # 4. Wait for async workflow completion loop
    print("Waiting for callback event signal...")
    try:
        await asyncio.wait_for(completion_received.wait(), timeout=10.0)
        
        print("\n[Step 4] Validating received event envelope parameters...")
        assert received_envelope is not None, "Error: Did not receive workflow completion event."
        assert received_envelope.correlation_id == correlation_id, "Error: Correlation ID mismatch."
        assert "output" in received_envelope.payload, "Error: Synthesized output payload is missing."
        print(f"Final output: '{received_envelope.payload.get('output')[:100]}...'")
        
        print("\nSprint 5 Event-driven core successfully validated!")
        
    except asyncio.TimeoutError:
        print("Error: Timed out waiting for workflow completion event.")
        raise TimeoutError("Workflow execution failed to publish completion event.")

    print("\n==================================================")
    print("SPRINT 5 INTEGRATION TEST: ALL TESTS PASSED!")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(test_sprint5_event_driven_core())
