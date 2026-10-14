import sys
import os

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.task_manager.dag_generator import TaskDAGGenerator

def test_sprint10_semantic_task_planner():
    print("\n==================================================")
    print("RUNNING SPRINT 10 SEMANTIC PLANNER INTEGRATION TEST")
    print("==================================================")

    # 1. Generate plan
    print("[Step 1] Initializing TaskDAGGenerator and generating plan...")
    generator = TaskDAGGenerator()
    tasks = generator.generate_heuristic_dag(
        goal_title="Build a python analytics tool",
        goal_description="Create charts and tables summarizing monthly store profits."
    )
    
    print(f"Generated task plan list containing {len(tasks)} items.")
    assert len(tasks) > 0, "Error: Task list should not be empty."

    # 2. Assert semantic fields on the first task
    print("\n[Step 2] Validating semantic fields on tasks...")
    first_task = tasks[0]
    
    assert "priority" in first_task, "Error: missing priority field."
    assert "dependencies" in first_task, "Error: missing dependencies field."
    assert isinstance(first_task["dependencies"], list), "Error: dependencies must be a list."
    assert "estimated_execution_time" in first_task, "Error: missing execution time estimate."
    assert "estimated_token_usage" in first_task, "Error: missing token usage estimate."
    assert "required_apis" in first_task, "Error: missing required APIs field."
    assert "required_tools" in first_task, "Error: missing required tools field."
    assert "confidence_score" in first_task, "Error: missing confidence score."
    assert "expected_output" in first_task, "Error: missing expected output description."
    assert "retry_policy" in first_task, "Error: missing retry policy config."
    
    print(f"First task details checked: {first_task}")
    print("\nSemantic task planner successfully validated!")

    print("\n==================================================")
    print("SPRINT 10 INTEGRATION TEST: ALL TESTS PASSED!")
    print("==================================================")

if __name__ == "__main__":
    test_sprint10_semantic_task_planner()
