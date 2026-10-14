import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.orchestrator.graph import orchestrator_graph

async def test_kerala():
    inputs = {
        "goal_id": "00000000-0000-0000-0000-000000000002",
        "goal_title": "Plan a trip to Kerala",
        "goal_description": "Create a detailed travel itinerary for a 7-day holiday.",
        "tasks": [],
        "current_task_index": 0,
        "results": {},
        "next_agent": None,
        "global_context": {},
        "output": "",
        "errors": []
    }
    
    print("Running orchestrator for Kerala...")
    try:
        final_state = await orchestrator_graph.ainvoke(inputs)
        print("Success! Output:")
        print(final_state.get("output"))
    except Exception as e:
        print("Failure:", e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_kerala())
