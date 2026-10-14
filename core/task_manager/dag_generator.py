import uuid
from typing import List, Dict, Any, Optional
from loguru import logger

class TaskDAGGenerator:
    """Decomposes a user's high-level goal into a Directed Acyclic Graph (DAG) of sub-tasks."""
    
    @staticmethod
    def generate_heuristic_dag(goal_title: str, goal_description: str) -> List[Dict[str, Any]]:
        """Generate a rule-based execution plan based on keywords in the goal description."""
        title = (goal_title.lower() + " " + (goal_description or "").lower()).strip()
        tasks = []
        
        # 0. Date / Time / Clock Goals
        if any(w in title for w in ["date", "time", "clock", "calendar", "day is it"]):
            task_1_id = uuid.uuid4()
            task_2_id = uuid.uuid4()
            tasks = [
                {
                    "id": task_1_id,
                    "assigned_agent": "research_agent",
                    "input_data": {"query": f"Retrieve current date and time information for: {goal_title}"},
                    "parent_task_id": None,
                    "dependencies": [],
                    "status": "pending",
                    "priority": "HIGH",
                    "estimated_execution_time": 5.0,
                    "estimated_token_usage": 200,
                    "required_apis": [],
                    "required_tools": [],
                    "confidence_score": 0.99,
                    "expected_output": "Formatted date and time information",
                    "retry_policy": {"max_retries": 1, "delay": 1}
                },
                {
                    "id": task_2_id,
                    "assigned_agent": "evaluator_agent",
                    "input_data": {"action": "Verify response clarity and formatting"},
                    "parent_task_id": task_1_id,
                    "dependencies": [task_1_id],
                    "status": "pending",
                    "priority": "NORMAL",
                    "estimated_execution_time": 5.0,
                    "estimated_token_usage": 100,
                    "required_apis": [],
                    "required_tools": [],
                    "confidence_score": 0.99,
                    "expected_output": "Validation status",
                    "retry_policy": {"max_retries": 1, "delay": 1}
                }
            ]
        # 1. Travel / Trip / Kerala Goals
        elif any(w in title for w in ["trip", "kerala", "travel", "holiday", "explore", "vacation"]):
            task_1_id = uuid.uuid4()
            task_2_id = uuid.uuid4()
            task_3_id = uuid.uuid4()
            task_4_id = uuid.uuid4()
            
            tasks = [
                {
                    "id": task_1_id,
                    "assigned_agent": "research_agent",
                    "input_data": {"query": f"Gather tourist attractions, climate details, and lodging categories for: {goal_title}"},
                    "parent_task_id": None,
                    "dependencies": [],
                    "status": "pending",
                    "priority": "HIGH",
                    "estimated_execution_time": 30.0,
                    "estimated_token_usage": 1500,
                    "required_apis": ["google_search"],
                    "required_tools": ["web_scraper"],
                    "confidence_score": 0.95,
                    "expected_output": "Kerala sights and travel details list",
                    "retry_policy": {"max_retries": 3, "delay": 5}
                },
                {
                    "id": task_2_id,
                    "assigned_agent": "travel_agent",
                    "input_data": {"query": f"Construct detailed 7-day itinerary for: {goal_title}"},
                    "parent_task_id": task_1_id,
                    "dependencies": [task_1_id],
                    "status": "pending",
                    "priority": "HIGH",
                    "estimated_execution_time": 60.0,
                    "estimated_token_usage": 2500,
                    "required_apis": [],
                    "required_tools": ["itinerary_builder"],
                    "confidence_score": 0.92,
                    "expected_output": "Detailed daily travel plan",
                    "retry_policy": {"max_retries": 2, "delay": 5}
                },
                {
                    "id": task_3_id,
                    "assigned_agent": "fact_verification_agent",
                    "input_data": {"action": f"Verify transport, cost approximations, and safety parameters for: {goal_title}"},
                    "parent_task_id": task_2_id,
                    "dependencies": [task_2_id],
                    "status": "pending",
                    "priority": "NORMAL",
                    "estimated_execution_time": 25.0,
                    "estimated_token_usage": 1000,
                    "required_apis": [],
                    "required_tools": ["fact_checker"],
                    "confidence_score": 0.94,
                    "expected_output": "Factual verification check report",
                    "retry_policy": {"max_retries": 2, "delay": 5}
                },
                {
                    "id": task_4_id,
                    "assigned_agent": "governance_layer",
                    "input_data": {"action": "Perform compliance check for travel regulations and safety limits"},
                    "parent_task_id": task_3_id,
                    "dependencies": [task_3_id],
                    "status": "pending",
                    "priority": "NORMAL",
                    "estimated_execution_time": 15.0,
                    "estimated_token_usage": 800,
                    "required_apis": [],
                    "required_tools": ["compliance_checker"],
                    "confidence_score": 0.98,
                    "expected_output": "Compliance audit certification",
                    "retry_policy": {"max_retries": 2, "delay": 5}
                }
            ]
            
        # 2. Basketball / Teaching / Education Goals
        elif any(w in title for w in ["basketball", "teach", "learn", "education", "coach", "train"]):
            task_1_id = uuid.uuid4()
            task_2_id = uuid.uuid4()
            task_3_id = uuid.uuid4()
            task_4_id = uuid.uuid4()
            
            tasks = [
                {
                    "id": task_1_id,
                    "assigned_agent": "research_agent",
                    "input_data": {"query": f"Gather professional standard guides and techniques for: {goal_title}"},
                    "parent_task_id": None,
                    "dependencies": [],
                    "status": "pending",
                    "priority": "HIGH",
                    "estimated_execution_time": 35.0,
                    "estimated_token_usage": 1800,
                    "required_apis": ["google_search"],
                    "required_tools": ["web_scraper"],
                    "confidence_score": 0.93,
                    "expected_output": "Technique guidelines bibliography",
                    "retry_policy": {"max_retries": 2, "delay": 5}
                },
                {
                    "id": task_2_id,
                    "assigned_agent": "education_agent",
                    "input_data": {"subject": f"Design complete beginners coaching syllabus for: {goal_title}"},
                    "parent_task_id": task_1_id,
                    "dependencies": [task_1_id],
                    "status": "pending",
                    "priority": "HIGH",
                    "estimated_execution_time": 50.0,
                    "estimated_token_usage": 3000,
                    "required_apis": [],
                    "required_tools": ["curriculum_designer"],
                    "confidence_score": 0.90,
                    "expected_output": "Structured learning modules",
                    "retry_policy": {"max_retries": 2, "delay": 5}
                },
                {
                    "id": task_3_id,
                    "assigned_agent": "fitness_agent",
                    "input_data": {"focus": f"Generate workout conditioning regimes and safety guidelines to support: {goal_title}"},
                    "parent_task_id": task_2_id,
                    "dependencies": [task_2_id],
                    "status": "pending",
                    "priority": "NORMAL",
                    "estimated_execution_time": 30.0,
                    "estimated_token_usage": 1500,
                    "required_apis": [],
                    "required_tools": ["workout_planner"],
                    "confidence_score": 0.92,
                    "expected_output": "Strength & conditioning plan",
                    "retry_policy": {"max_retries": 3, "delay": 5}
                },
                {
                    "id": task_4_id,
                    "assigned_agent": "evaluator_agent",
                    "input_data": {"action": "Create skill benchmarking testing scorecard to monitor training goals"},
                    "parent_task_id": task_3_id,
                    "dependencies": [task_3_id],
                    "status": "pending",
                    "priority": "NORMAL",
                    "estimated_execution_time": 20.0,
                    "estimated_token_usage": 1000,
                    "required_apis": [],
                    "required_tools": ["qa_auditor"],
                    "confidence_score": 0.95,
                    "expected_output": "Self-assessment scorecard",
                    "retry_policy": {"max_retries": 2, "delay": 5}
                }
            ]
            
        # 3. Fitness / Workout / Health Goals
        elif any(w in title for w in ["fitness", "workout", "gym", "bodybuilding", "diet", "nutrition"]):
            task_1_id = uuid.uuid4()
            task_2_id = uuid.uuid4()
            task_3_id = uuid.uuid4()
            
            tasks = [
                {
                    "id": task_1_id,
                    "assigned_agent": "research_agent",
                    "input_data": {"query": f"Gather physiological parameters and safety rules for: {goal_title}"},
                    "parent_task_id": None,
                    "dependencies": [],
                    "status": "pending",
                    "priority": "NORMAL",
                    "estimated_execution_time": 30.0,
                    "estimated_token_usage": 1200,
                    "required_apis": ["google_search"],
                    "required_tools": ["web_scraper"],
                    "confidence_score": 0.94,
                    "expected_output": "Safety limits and guidelines context",
                    "retry_policy": {"max_retries": 2, "delay": 5}
                },
                {
                    "id": task_2_id,
                    "assigned_agent": "fitness_agent",
                    "input_data": {"goal": f"Create specialized physical split routines and diet structure for: {goal_title}"},
                    "parent_task_id": task_1_id,
                    "dependencies": [task_1_id],
                    "status": "pending",
                    "priority": "HIGH",
                    "estimated_execution_time": 45.0,
                    "estimated_token_usage": 2000,
                    "required_apis": [],
                    "required_tools": ["diet_planner"],
                    "confidence_score": 0.92,
                    "expected_output": "Custom split routine sheets",
                    "retry_policy": {"max_retries": 2, "delay": 5}
                },
                {
                    "id": task_3_id,
                    "assigned_agent": "evaluator_agent",
                    "input_data": {"action": "Perform movement mechanical safety audit and workload validation"},
                    "parent_task_id": task_2_id,
                    "dependencies": [task_2_id],
                    "status": "pending",
                    "priority": "NORMAL",
                    "estimated_execution_time": 20.0,
                    "estimated_token_usage": 1000,
                    "required_apis": [],
                    "required_tools": ["safety_scanner"],
                    "confidence_score": 0.96,
                    "expected_output": "Mechanical audit logs status",
                    "retry_policy": {"max_retries": 2, "delay": 5}
                }
            ]
            
        # 4. Coding / Web / API Goals
        elif any(w in title for w in ["code", "build", "program", "website", "api", "app", "database", "backend"]):
            task_1_id = uuid.uuid4()
            task_2_id = uuid.uuid4()
            task_3_id = uuid.uuid4()
            task_4_id = uuid.uuid4()
            
            tasks = [
                {
                    "id": task_1_id,
                    "assigned_agent": "research_agent",
                    "input_data": {"query": f"Gather architectural requirements and standard specs for: {goal_title}"},
                    "parent_task_id": None,
                    "dependencies": [],
                    "status": "pending",
                    "priority": "HIGH",
                    "estimated_execution_time": 45.0,
                    "estimated_token_usage": 1500,
                    "required_apis": ["google_search"],
                    "required_tools": ["web_scraper"],
                    "confidence_score": 0.95,
                    "expected_output": "Comprehensive specification document",
                    "retry_policy": {"max_retries": 3, "delay": 5}
                },
                {
                    "id": task_2_id,
                    "assigned_agent": "coding_agent",
                    "input_data": {"instructions": f"Develop source code repository files for: {goal_title}"},
                    "parent_task_id": task_1_id,
                    "dependencies": [task_1_id],
                    "status": "pending",
                    "priority": "HIGH",
                    "estimated_execution_time": 120.0,
                    "estimated_token_usage": 5000,
                    "required_apis": [],
                    "required_tools": ["code_writer"],
                    "confidence_score": 0.88,
                    "expected_output": "Complete source code file output",
                    "retry_policy": {"max_retries": 2, "delay": 10}
                },
                {
                    "id": task_3_id,
                    "assigned_agent": "cybersecurity_agent",
                    "input_data": {"action": "Perform static analysis and code security audit on the developed codebase"},
                    "parent_task_id": task_2_id,
                    "dependencies": [task_2_id],
                    "status": "pending",
                    "priority": "NORMAL",
                    "estimated_execution_time": 60.0,
                    "estimated_token_usage": 2000,
                    "required_apis": [],
                    "required_tools": ["security_scanner"],
                    "confidence_score": 0.90,
                    "expected_output": "Vulnerability report logs",
                    "retry_policy": {"max_retries": 3, "delay": 5}
                },
                {
                    "id": task_4_id,
                    "assigned_agent": "evaluator_agent",
                    "input_data": {"action": "Audit functional test suite execution and evaluate standard coverage"},
                    "parent_task_id": task_3_id,
                    "dependencies": [task_3_id],
                    "status": "pending",
                    "priority": "NORMAL",
                    "estimated_execution_time": 20.0,
                    "estimated_token_usage": 1000,
                    "required_apis": [],
                    "required_tools": ["qa_auditor"],
                    "confidence_score": 0.95,
                    "expected_output": "Testing validation report",
                    "retry_policy": {"max_retries": 2, "delay": 5}
                }
            ]
            
        # 5. Data Analytics / Charts / Visualize Goals
        elif any(w in title for w in ["analyze", "data", "chart", "visualize", "report", "excel"]):
            task_1_id = uuid.uuid4()
            task_2_id = uuid.uuid4()
            task_3_id = uuid.uuid4()
            
            tasks = [
                {
                    "id": task_1_id,
                    "assigned_agent": "research_agent",
                    "input_data": {"query": f"Find data sources and metrics schema for: {goal_title}"},
                    "parent_task_id": None,
                    "dependencies": [],
                    "status": "pending",
                    "priority": "NORMAL",
                    "estimated_execution_time": 30.0,
                    "estimated_token_usage": 1000,
                    "required_apis": ["google_search"],
                    "required_tools": ["web_scraper"],
                    "confidence_score": 0.92,
                    "expected_output": "Data source links and schemas",
                    "retry_policy": {"max_retries": 2, "delay": 5}
                },
                {
                    "id": task_2_id,
                    "assigned_agent": "data_agent",
                    "input_data": {"analysis_instructions": f"Process, clean, and visualize data related to: {goal_title}"},
                    "parent_task_id": task_1_id,
                    "dependencies": [task_1_id],
                    "status": "pending",
                    "priority": "HIGH",
                    "estimated_execution_time": 90.0,
                    "estimated_token_usage": 3000,
                    "required_apis": [],
                    "required_tools": ["python_interpreter"],
                    "confidence_score": 0.94,
                    "expected_output": "Cleaned datasets and charts",
                    "retry_policy": {"max_retries": 2, "delay": 5}
                },
                {
                    "id": task_3_id,
                    "assigned_agent": "business_agent",
                    "input_data": {"market_eval": f"Perform market and economic analysis on results: {goal_title}"},
                    "parent_task_id": task_2_id,
                    "dependencies": [task_2_id],
                    "status": "pending",
                    "priority": "NORMAL",
                    "estimated_execution_time": 45.0,
                    "estimated_token_usage": 2000,
                    "required_apis": [],
                    "required_tools": ["market_reporter"],
                    "confidence_score": 0.85,
                    "expected_output": "Market analysis report",
                    "retry_policy": {"max_retries": 3, "delay": 10}
                }
            ]
            
        # 6. Fallback General Research-Report Goals
        else:
            task_1_id = uuid.uuid4()
            task_2_id = uuid.uuid4()
            task_3_id = uuid.uuid4()
            task_4_id = uuid.uuid4()
            
            tasks = [
                {
                    "id": task_1_id,
                    "assigned_agent": "research_agent",
                    "input_data": {"query": f"Gather reference materials and facts on: {goal_title} - {goal_description}"},
                    "parent_task_id": None,
                    "dependencies": [],
                    "status": "pending",
                    "priority": "NORMAL",
                    "estimated_execution_time": 30.0,
                    "estimated_token_usage": 1200,
                    "required_apis": ["google_search"],
                    "required_tools": ["web_scraper"],
                    "confidence_score": 0.90,
                    "expected_output": "Research bibliography and raw facts",
                    "retry_policy": {"max_retries": 2, "delay": 5}
                },
                {
                    "id": task_2_id,
                    "assigned_agent": "business_agent",
                    "input_data": {"goal": f"Summarize research findings and output recommendations for: {goal_title}"},
                    "parent_task_id": task_1_id,
                    "dependencies": [task_1_id],
                    "status": "pending",
                    "priority": "NORMAL",
                    "estimated_execution_time": 45.0,
                    "estimated_token_usage": 1800,
                    "required_apis": [],
                    "required_tools": ["summarizer"],
                    "confidence_score": 0.88,
                    "expected_output": "Executive summary report",
                    "retry_policy": {"max_retries": 2, "delay": 5}
                },
                {
                    "id": task_3_id,
                    "assigned_agent": "fact_verification_agent",
                    "input_data": {"action": "Perform fact checking verification and hallucination auditing"},
                    "parent_task_id": task_2_id,
                    "dependencies": [task_2_id],
                    "status": "pending",
                    "priority": "NORMAL",
                    "estimated_execution_time": 20.0,
                    "estimated_token_usage": 1000,
                    "required_apis": [],
                    "required_tools": ["fact_checker"],
                    "confidence_score": 0.92,
                    "expected_output": "Fact verification scorecard",
                    "retry_policy": {"max_retries": 2, "delay": 5}
                },
                {
                    "id": task_4_id,
                    "assigned_agent": "evaluator_agent",
                    "input_data": {"action": "Assess synthesized data formatting and grounding quality parameters"},
                    "parent_task_id": task_3_id,
                    "dependencies": [task_3_id],
                    "status": "pending",
                    "priority": "NORMAL",
                    "estimated_execution_time": 20.0,
                    "estimated_token_usage": 1000,
                    "required_apis": [],
                    "required_tools": ["qa_auditor"],
                    "confidence_score": 0.95,
                    "expected_output": "QA evaluation report",
                    "retry_policy": {"max_retries": 2, "delay": 5}
                }
            ]
            
        logger.info(f"Generated heuristic DAG with {len(tasks)} tasks for goal: {goal_title}")
        return tasks

    async def generate_dag(
        self, 
        goal_title: str, 
        goal_description: str, 
        model_manager: Optional[Any] = None
    ) -> List[Dict[str, Any]]:
        """Decomposes goal into subtasks, using LLM if available, otherwise falling back to heuristics."""
        if model_manager and hasattr(model_manager, "is_configured") and model_manager.is_configured():
            try:
                # LLM planning agent decomposition logic
                logger.info("TaskDAGGenerator: Attempting LLM dynamic planning...")
                prompt = f"Goal Title: {goal_title}\nGoal Description: {goal_description}\nDecompose this goal into a list of tasks. Return a JSON array."
                resp = await model_manager.generate(
                    prompt=prompt,
                    system_instruction="You are the planning_agent. Decompose high-level goals into dynamic task lists.",
                    provider="REASONING_MODEL"
                )
                import json
                cleaned = resp.strip()
                if cleaned.startswith("```"):
                    cleaned = cleaned.split("```")[1]
                    if cleaned.startswith("json"):
                        cleaned = cleaned[4:]
                tasks = json.loads(cleaned.strip())
                # Add UUIDs if missing
                for t in tasks:
                    if "id" not in t:
                        t["id"] = uuid.uuid4()
                    if "status" not in t:
                        t["status"] = "pending"
                return tasks
            except Exception as e:
                logger.error(f"Error during LLM task decomposition: {e}. Falling back to heuristics.")
        
        return self.generate_heuristic_dag(goal_title, goal_description)
