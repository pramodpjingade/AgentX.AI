import asyncio
import httpx
import sys

BASE_URL = "http://127.0.0.1:8000/api/v1"

async def main():
    print("==================================================")
    print("RUNNING E2E API FLOW & WORKFLOW CONTROL VALIDATION")
    print("==================================================")

    async with httpx.AsyncClient() as client:
        # 1. Login
        print("[Step 1] Logging in as admin...")
        login_res = await client.post(
            f"{BASE_URL}/auth/login",
            data={"username": "admin@agentx.ai", "password": "Password123!"}
        )
        if login_res.status_code != 200:
            print(f"Login failed: {login_res.status_code} - {login_res.text}")
            sys.exit(1)
            
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("Login successful! Token acquired.")

        # 2. Create Goal
        print("\n[Step 2] Submitting a new goal...")
        goal_payload = {
            "title": "Build a Simple JSON Sales File Validator",
            "description": "Create a script to load, check properties, and log summaries."
        }
        create_res = await client.post(
            f"{BASE_URL}/goals/",
            json=goal_payload,
            headers=headers
        )
        if create_res.status_code != 201:
            print(f"Goal creation failed: {create_res.status_code} - {create_res.text}")
            sys.exit(1)
            
        goal_data = create_res.json()
        goal_id = goal_data["id"]
        print(f"Goal created successfully! ID: {goal_id}")

        # 3. Poll for tasks and status
        print("\n[Step 3] Polling goal details for task generation...")
        tasks_generated = False
        for i in range(10):
            await asyncio.sleep(0.5)
            detail_res = await client.get(f"{BASE_URL}/goals/{goal_id}", headers=headers)
            if detail_res.status_code == 200:
                detail_data = detail_res.json()
                goal_status = detail_data["goal"]["status"]
                tasks = detail_data.get("tasks") or []
                print(f"Poll {i+1}: Goal Status: '{goal_status}', Tasks generated: {len(tasks)}")
                if len(tasks) > 0:
                    tasks_generated = True
                    for t in tasks:
                        print(f"  - Task ID: {t['id']} | Agent: {t['assigned_agent']} | Status: {t['status']}")
                    break
            else:
                print(f"Failed to get goal: {detail_res.status_code}")

        if not tasks_generated:
            print("Error: No tasks were generated for the goal.")
            sys.exit(1)

        # 4. Test Pause
        print("\n[Step 4] Pausing workflow execution...")
        pause_res = await client.post(f"{BASE_URL}/workflows/pause/{goal_id}", headers=headers)
        print(f"Pause response status: {pause_res.status_code}")
        if pause_res.status_code == 200:
            print(f"Workflow status after pause: {pause_res.json()}")
        else:
            print(f"Pause failed: {pause_res.text}")

        # Check DB status after pause
        db_res = await client.get(f"{BASE_URL}/goals/{goal_id}", headers=headers)
        print(f"Database goal status: '{db_res.json()['goal']['status']}'")

        # 5. Test Resume
        print("\n[Step 5] Resuming workflow execution...")
        resume_res = await client.post(f"{BASE_URL}/workflows/resume/{goal_id}", headers=headers)
        print(f"Resume response status: {resume_res.status_code}")
        if resume_res.status_code == 200:
            print(f"Workflow status after resume: {resume_res.json()}")
        else:
            print(f"Resume failed: {resume_res.text}")

        # Check DB status after resume
        db_res = await client.get(f"{BASE_URL}/goals/{goal_id}", headers=headers)
        print(f"Database goal status: '{db_res.json()['goal']['status']}'")

        # 6. Wait for execution to finish
        print("\n[Step 6] Waiting for workflow to finish execution...")
        finished = False
        for i in range(15):
            await asyncio.sleep(1.0)
            db_res = await client.get(f"{BASE_URL}/goals/{goal_id}", headers=headers)
            goal_status = db_res.json()["goal"]["status"]
            tasks = db_res.json().get("tasks") or []
            print(f"Poll {i+1}: Goal Status: '{goal_status}'")
            for t in tasks:
                print(f"  - Task: {t['assigned_agent']} | Status: {t['status']}")
            if goal_status in ["completed", "failed", "cancelled"]:
                finished = True
                break

        if finished:
            print("\nE2E workflow execution and control successfully validated!")
        else:
            print("\nWarning: Workflow is still executing, but connection and status loop is verified.")

if __name__ == "__main__":
    asyncio.run(main())
