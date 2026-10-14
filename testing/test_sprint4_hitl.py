import asyncio
import os
import sys
from uuid import uuid4
from sqlalchemy.future import select

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import engine, async_session
from database.models import User, ApprovalRequest
from agents.base_agent import BaseAgent

# Setup simple dummy agent to test approvals
class DummyToolAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="dummy_tool_agent", role="tool_executor")
    def get_tools(self): return []
    def get_system_prompt(self): return ""
    async def execute(self, task_input, global_context=None):
        return {"status": "success"}

async def test_sprint4_hitl_flow():
    print("\n==================================================")
    print("RUNNING SPRINT 4 HITL APPROVALS INTEGRATION TEST")
    print("==================================================")

    # 1. Setup Test User
    async with async_session() as db:
        print("[Step 1] Verifying test user...")
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
            
    # 2. Request tool approval
    print("\n[Step 2] Requesting tool execution authorization...")
    agent = DummyToolAgent()
    params = {"command": "rm -rf /var/logs", "sandbox": True}
    
    approval_id = await agent.request_tool_approval(
        tool_name="code_execution",
        parameters=params,
        task_id=str(uuid4())
    )
    print(f"Approval request registered in DB. ID: {approval_id}")

    # 3. Verify status is initially 'pending'
    print("\n[Step 3] Verifying initial pending state...")
    status = await agent.check_tool_approval(approval_id)
    print(f"Current approval status: '{status}'")
    assert status == "pending", f"Error: Expected 'pending', got '{status}'"

    # 4. Resolve approval (simulate API route action: approve)
    print("\n[Step 4] Resolving request (Action: approved)...")
    async with async_session() as db:
        import uuid
        stmt = select(ApprovalRequest).where(ApprovalRequest.id == uuid.UUID(approval_id))
        result = await db.execute(stmt)
        req = result.scalars().first()
        
        req.status = "approved"
        req.resolved_by = user.id
        await db.commit()

    # 5. Verify status is now 'approved'
    print("\n[Step 5] Checking resolved status...")
    status = await agent.check_tool_approval(approval_id)
    print(f"Updated approval status: '{status}'")
    assert status == "approved", f"Error: Expected 'approved', got '{status}'"
    print("HITL resolution successfully verified!")

    print("\n==================================================")
    print("SPRINT 4 INTEGRATION TEST: ALL TESTS PASSED!")
    print("==================================================")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_sprint4_hitl_flow())
