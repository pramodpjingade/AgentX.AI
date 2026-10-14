import asyncio
import os
import sys
from uuid import uuid4

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.orchestrator.workflow_engine import WorkflowEngine

async def test_sprint8_workflow_transitions():
    print("\n==================================================")
    print("RUNNING SPRINT 8 WORKFLOW CONTROL INTEGRATION TEST")
    print("==================================================")

    # 1. Initialize Engine
    print("[Step 1] Initializing WorkflowEngine singleton...")
    engine = WorkflowEngine()

    # 2. Register Goal ID
    goal_id = str(uuid4())
    print(f"\n[Step 2] Registering active execution flow for goal ID: {goal_id}...")
    await engine.register_workflow(goal_id)
    
    # 3. Assert initial state is running
    status = await engine.get_status(goal_id)
    print(f"Initial status: '{status}'")
    assert status == "running", f"Error: Expected 'running', got '{status}'"

    # 4. Trigger Pause
    print("\n[Step 3] Dispatching pause command payload...")
    paused = await engine.pause_workflow(goal_id)
    assert paused is True, "Error: Pause operation failed to return True."
    
    status = await engine.get_status(goal_id)
    print(f"Status after pause: '{status}'")
    assert status == "paused", f"Error: Expected 'paused', got '{status}'"

    # 5. Trigger Resume
    print("\n[Step 4] Dispatching resume command payload...")
    resumed = await engine.resume_workflow(goal_id)
    assert resumed is True, "Error: Resume operation failed to return True."
    
    status = await engine.get_status(goal_id)
    print(f"Status after resume: '{status}'")
    assert status == "running", f"Error: Expected 'running', got '{status}'"

    # 6. Trigger Cancel
    print("\n[Step 5] Dispatching cancellation command payload...")
    cancelled = await engine.cancel_workflow(goal_id)
    assert cancelled is True, "Error: Cancel operation failed to return True."
    
    status = await engine.get_status(goal_id)
    print(f"Status after cancellation: '{status}'")
    assert status == "cancelled", f"Error: Expected 'cancelled', got '{status}'"

    print("\nWorkflow engine dynamic state control successfully validated!")

    print("\n==================================================")
    print("SPRINT 8 INTEGRATION TEST: ALL TESTS PASSED!")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(test_sprint8_workflow_transitions())
