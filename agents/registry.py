from typing import Dict, Any, List, Type, Optional
from loguru import logger
import importlib
from agents.base_agent import BaseAgent

class AgentRegistry:
    """
    Agent Registry (Phase 2 AI Brain Core).
    Manages dynamic discovery, capability lookup, health monitoring, version tracking,
    priority management, performance telemetry aggregation, and future plugin loading.
    """
    
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AgentRegistry, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return
            
        # Dictionary mapping agent_name (str) -> dict of metadata & class type & instances
        self._registry: Dict[str, Dict[str, Any]] = {}
        self._instances: Dict[str, BaseAgent] = {}
        self._initialized = True
        self._register_default_agents()

    def register_agent(
        self, 
        name: str, 
        agent_class: Type[BaseAgent], 
        version: str = "1.2.0", 
        capabilities: Optional[List[str]] = None,
        supported_mission_types: Optional[List[str]] = None,
        status: str = "active",
        priority: str = "NORMAL",
        description: str = ""
    ):
        """Register an agent class with rich metadata."""
        self._registry[name] = {
            "class": agent_class,
            "version": version,
            "capabilities": capabilities or [],
            "supported_mission_types": supported_mission_types or ["general"],
            "status": status,
            "priority": priority,
            "description": description or f"Specialized agent '{name}'"
        }
        logger.info(f"AgentRegistry: Registered agent '{name}' (v{version}) with status '{status}'")

    def unregister_agent(self, name: str) -> bool:
        """Removes an agent from the registry."""
        if name in self._registry:
            del self._registry[name]
            if name in self._instances:
                del self._instances[name]
            logger.info(f"AgentRegistry: Unregistered agent '{name}'")
            return True
        return False

    def get_agent_metadata(self, name: str) -> Optional[Dict[str, Any]]:
        """Retrieve registered metadata for a specific agent."""
        return self._registry.get(name)

    def list_agents(self) -> Dict[str, Dict[str, Any]]:
        """List all registered agents and their metadata."""
        return {
            name: {
                "version": info["version"],
                "capabilities": info["capabilities"],
                "supported_mission_types": info["supported_mission_types"],
                "status": info["status"],
                "priority": info["priority"],
                "description": info["description"]
            }
            for name, info in self._registry.items()
        }

    def instantiate_agent(self, name: str) -> BaseAgent:
        """Dynamically instantiate and return a registered agent class instance."""
        agent_info = self._registry.get(name)
        if not agent_info:
            raise ValueError(f"Agent '{name}' is not registered in the system.")
            
        if agent_info["status"] != "active":
            raise ValueError(f"Agent '{name}' is currently offline/inactive (status: {agent_info['status']})")

        # Reuse instance if cached, otherwise create new
        if name not in self._instances:
            agent_class = agent_info["class"]
            logger.info(f"AgentRegistry: Instantiating class '{agent_class.__name__}' for agent '{name}'")
            self._instances[name] = agent_class()

        return self._instances[name]

    def find_agents_by_capability(self, capability: str) -> List[str]:
        """Returns names of all registered agents that possess the specified capability."""
        matches = []
        for name, info in self._registry.items():
            if capability.lower() in [c.lower() for c in info.get("capabilities", [])]:
                matches.append(name)
        return matches

    def find_agents_by_capabilities(self, capabilities: List[str]) -> List[str]:
        """Returns names of registered agents that match any of the specified capabilities."""
        matches = set()
        for cap in capabilities:
            for name in self.find_agents_by_capability(cap):
                matches.add(name)
        return list(matches)

    def find_agents_for_mission_type(self, mission_type: str) -> List[str]:
        """Returns agent names suited for a given mission domain category."""
        matches = []
        mission_lower = mission_type.lower()
        for name, info in self._registry.items():
            supported = [m.lower() for m in info.get("supported_mission_types", [])]
            if mission_lower in supported or "general" in supported:
                matches.append(name)
        return matches

    def check_health(self) -> Dict[str, Any]:
        """Audits the health status of all registered agents."""
        health_report = {}
        for name, instance in self._instances.items():
            health_report[name] = {
                "health_status": getattr(instance, "health_status", "HEALTHY"),
                "telemetry": getattr(instance, "telemetry", {})
            }
        for name in self._registry:
            if name not in health_report:
                health_report[name] = {"health_status": "HEALTHY", "telemetry": {}}
        return health_report

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Aggregates execution telemetry across all instantiated agents."""
        metrics = {}
        for name, instance in self._instances.items():
            if hasattr(instance, "telemetry"):
                metrics[name] = instance.telemetry
        return metrics

    def register_plugin(self, plugin_module_path: str, agent_class_name: str, name: str):
        """Dynamically loads and registers a third-party marketplace plugin agent."""
        try:
            mod = importlib.import_module(plugin_module_path)
            agent_cls = getattr(mod, agent_class_name)
            self.register_agent(
                name=name,
                agent_class=agent_cls,
                version="1.0.0-plugin",
                capabilities=["plugin_execution"],
                status="active"
            )
            logger.info(f"AgentRegistry: Dynamically loaded plugin agent '{name}' from '{plugin_module_path}'")
        except Exception as e:
            logger.error(f"AgentRegistry: Failed loading plugin '{name}': {e}")
            raise e

    def _register_default_agents(self):
        """Pre-registers all built-in core and specialized system agents."""
        # 1. Register Master Agent (Core Director/CEO)
        from agents.master_agent.agent import MasterAgent
        self.register_agent(
            name="master_agent",
            agent_class=MasterAgent,
            version="1.2.0",
            capabilities=["synthesis", "coordination", "final_response_generation", "deliverable_formulation"],
            supported_mission_types=["general", "travel", "coding", "research", "learning", "business", "fitness"],
            priority="HIGH",
            description="AI Director: Consolidates subtask outputs into cohesive deliverables."
        )
        
        # 2. Register Intent Understanding Agent
        from agents.intent.agent import IntentAgent
        self.register_agent(
            name="intent_agent",
            agent_class=IntentAgent,
            version="1.2.0",
            capabilities=["intent_parsing", "query_classification", "parameter_extraction"],
            supported_mission_types=["general"],
            priority="HIGH",
            description="Parses user input intent and key parameter requirements."
        )

        # 3. Register Safety Guardian Agent
        from agents.safety.agent import SafetyAgent
        self.register_agent(
            name="safety_agent",
            agent_class=SafetyAgent,
            version="1.2.0",
            capabilities=["content_scrubbing", "prompt_injection_check", "pii_scrubbing", "policy_audit"],
            supported_mission_types=["general"],
            priority="HIGH",
            description="Audits inputs and outputs for PII, prompt injection, and policy compliance."
        )

        # 4. Register Evaluation Agent
        from agents.evaluator.agent import EvaluationAgent
        self.register_agent(
            name="evaluator_agent",
            agent_class=EvaluationAgent,
            version="1.2.0",
            capabilities=["output_validation", "grounding_scoring", "hallucination_detection", "quality_metrics"],
            supported_mission_types=["general"],
            priority="HIGH",
            description="QA Auditor: Validates output grounding, factual accuracy, and completeness."
        )

        # 5. Register Supervisor Agent
        from agents.supervisor.agent import SupervisorAgent
        self.register_agent(
            name="supervisor_agent",
            agent_class=SupervisorAgent,
            version="1.2.0",
            capabilities=["intent_classification", "risk_identification", "strategy_formulation", "budget_allocation"],
            supported_mission_types=["general"],
            priority="HIGH",
            description="Orchestrator: Formulates execution strategy and estimates complexity."
        )

        # 6. Register Planner Agent
        from agents.planning_agent.agent import PlannerAgent
        self.register_agent(
            name="planning_agent",
            agent_class=PlannerAgent,
            version="1.2.0",
            capabilities=["goal_decomposition", "dag_creation", "priority_assignment", "dependency_graphing"],
            supported_mission_types=["general"],
            priority="HIGH",
            description="Project Manager: Decomposes goals into structured subtask DAGs."
        )

        # 7. Register Router Agent
        from agents.router_agent.agent import RouterAgent
        self.register_agent(
            name="router_agent",
            agent_class=RouterAgent,
            version="1.2.0",
            capabilities=["dynamic_routing", "capability_matching", "agent_assignment", "parallel_routing"],
            supported_mission_types=["general"],
            priority="HIGH",
            description="Dynamic Router: Matches subtasks to candidate agents based on capabilities."
        )

        # 8. Register Specialized Domain Agents
        self._register_specialized_agents()

    def _register_specialized_agents(self):
        """Registers concrete specialized domain agents."""
        specialized = [
            ("research_agent", ["web_search", "document_scraping", "fact_compilation"], ["research", "general"]),
            ("coding_agent", ["code_generation", "linting", "refactoring", "scripting"], ["coding", "general"]),
            ("cybersecurity_agent", ["security_auditing", "vulnerability_scan"], ["coding", "general"]),
            ("data_agent", ["data_processing", "plotting", "analytics"], ["research", "business"]),
            ("business_agent", ["market_analysis", "seo_strategy", "business_planning"], ["business", "general"]),
            ("travel_agent", ["route_planning", "itinerary_generation", "hotel_booking", "weather"], ["travel", "general"]),
            ("education_agent", ["curriculum_design", "skill_teaching", "tutorial_creation"], ["learning", "general"]),
            ("fitness_agent", ["workout_planning", "nutrition_guidelines", "exercise_coaching"], ["fitness", "general"]),
            ("tool_execution_agent", ["api_invocation", "sandbox_running", "system_commands"], ["general"]),
            ("rag_agent", ["vector_search", "document_parsing", "embedding_retrieval"], ["general"]),
            ("fact_verification_agent", ["fact_checking", "hallucination_check", "source_grounding"], ["general"]),
            ("governance_layer", ["compliance_checking", "privacy_auditing", "pii_redaction"], ["general"])
        ]

        for name, caps, mission_types in specialized:
            # Check if specialized module exists or create dynamic wrapper
            try:
                mod_name = name if name != "governance_layer" else "safety"
                mod = importlib.import_module(f"agents.{mod_name}.agent")
                cls_name = "".join(word.capitalize() for word in name.split("_"))
                agent_cls = getattr(mod, cls_name, None) or getattr(mod, f"{cls_name}Agent", None)
            except Exception:
                agent_cls = None

            if not agent_cls:
                # Create standard BaseAgent dynamic subclass
                class_name = "".join(word.capitalize() for word in name.split("_"))
                def make_init(agent_name=name, capabilities=caps, m_types=mission_types):
                    def init(self):
                        super(self.__class__, self).__init__(
                            name=agent_name,
                            role=f"Specialized domain agent for {agent_name}",
                            capabilities=capabilities,
                            supported_mission_types=m_types
                        )
                    return init

                def make_execute(agent_name=name):
                    async def execute(self, task_input: Dict[str, Any], global_context: Dict[str, Any] = None) -> Dict[str, Any]:
                        logger.info(f"AgentRegistry: Running execution for specialized agent '{agent_name}'")
                        from agents.model_manager import ModelManager
                        manager = ModelManager()
                        res = await manager.generate(
                            prompt=f"Specialized execution for agent: {agent_name} with task: {task_input}",
                            system_instruction=f"You are the {agent_name}.",
                            provider="FAST_MODEL"
                        )
                        return {"status": "completed", "result": res}
                    return execute

                agent_cls = type(
                    class_name,
                    (BaseAgent,),
                    {
                        "__init__": make_init(),
                        "execute": make_execute(),
                        "get_tools": lambda self: [],
                        "get_system_prompt": lambda self: f"You are the {self.name} agent."
                    }
                )

            self.register_agent(
                name=name,
                agent_class=agent_cls,
                version="1.2.0",
                capabilities=caps,
                supported_mission_types=mission_types,
                status="active"
            )
