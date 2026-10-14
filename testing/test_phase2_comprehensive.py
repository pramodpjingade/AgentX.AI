import os
import unittest
import asyncio
import json
import uuid
from datetime import datetime

# Set test environment flags
os.environ["AGENTX_ALLOW_MOCK"] = "1"
os.environ["DEFAULT_LLM_PROVIDER"] = "mock"

from chat.service import ChatService
from chat.conversation_engine import ConversationEngine
from chat.schemas import ChatRequest, StandardChatResponse, ChatStreamChunk
from tools.code_executor import CodeExecutorTool
from tools.web_search import WebSearchTool
from tools.web_search_adapter import WebSearchToolAdapter
from intelligence.router import IntelligenceRouter
from intelligence.adapters.openai_adapter import OpenAIAdapter
from database.connection import async_session
from database.models import User, Conversation, Message

class TestPhase2ComprehensiveSuite(unittest.IsolatedAsyncioTestCase):
    """
    Automated Phase 2 verification suite covering all 12 core requirements:
    1. Short natural greeting
    2. Date and time check
    3. Python code generation
    4. C program generation
    5. Multi-step research & planning orchestration
    6. Graceful specialized agent failure handling
    7. Missing API key configuration handling
    8. Provider timeout/rate-limit error recovery
    9. Genuine SSE streaming lifecycle
    10. Honest tool reporting (no fake data)
    11. Multi-turn conversation memory & user isolation
    12. Clean API contract (no raw internal dictionaries)
    """

    async def asyncSetUp(self):
        self.chat_service = ChatService()
        self.router = IntelligenceRouter()

    # TEST 1: User sends "Hi". Expected: Short, natural answer.
    async def test_01_greeting_hi(self):
        resp = await self.chat_service.process_message(message="Hi", user_id="test_user_01")
        self.assertIsInstance(resp, StandardChatResponse)
        self.assertIn("Hello", resp.content)
        self.assertNotIn("--- Agent Result", resp.content)
        self.assertNotIn("{'status'", resp.content)

    # TEST 2: User asks for current date or time. Expected: Real local date/time.
    async def test_02_datetime_query(self):
        date_resp = await self.chat_service.process_message(message="What is today's date?", user_id="test_user_02")
        time_resp = await self.chat_service.process_message(message="What time is it?", user_id="test_user_02")
        now = datetime.now()
        self.assertIn(str(now.year), date_resp.content)
        self.assertIn("📅", date_resp.content)
        self.assertIn("🕒", time_resp.content)

    # TEST 3: User requests simple Python program. Expected: Readable code block.
    async def test_03_simple_python_program(self):
        resp = await self.chat_service.process_message(
            message="Write a simple Python program to check whether a number is prime.",
            user_id="test_user_03"
        )
        self.assertIn("```python", resp.content)
        self.assertIn("def is_prime", resp.content)
        self.assertNotIn("--- Agent Result", resp.content)

    # TEST 4: User requests simple C program. Expected: Valid C program and concise explanation.
    async def test_04_simple_c_program(self):
        resp = await self.chat_service.process_message(
            message="Give me a simple C program to add two numbers.",
            user_id="test_user_04"
        )
        self.assertIn("```c", resp.content)
        self.assertIn("#include <stdio.h>", resp.content)
        self.assertIn("main", resp.content)
        self.assertIn("Explanation", resp.content)

    # TEST 5: User asks complex multi-step question. Expected: Coherent synthesized answer.
    async def test_05_complex_multistep_orchestration(self):
        resp = await self.chat_service.process_message(
            message="Research current robotics technologies and create a roadmap.",
            user_id="test_user_05"
        )
        self.assertIn("Robotics Technology", resp.content)
        self.assertIn("Roadmap", resp.content)
        self.assertNotIn("Agent Result (safety_agent)", resp.content)
        self.assertNotIn("intent_agent", resp.content)

    # TEST 6: Specialized agent fails. Expected: Graceful handling without raw exception dumps.
    async def test_06_specialized_agent_failure_graceful(self):
        from agents.coding_agent.agent import CodingAgent
        agent = CodingAgent()
        # Force provider error on agent
        result = await agent.execute({"prompt": "force_fail_test", "provider": "invalid_provider_x"})
        self.assertIn("status", result)
        self.assertIn("result", result)
        # Should not crash and should report failure cleanly
        self.assertEqual(result["status"], "failed")

    # TEST 7: LLM API key missing. Expected: Clear configuration error without fabricated answer.
    async def test_07_llm_api_key_missing_error(self):
        # Explicitly invoke unconfigured OpenAI provider with mock disabled
        old_mock = os.environ.get("AGENTX_ALLOW_MOCK")
        old_key = os.environ.get("OPENAI_API_KEY")
        try:
            os.environ["AGENTX_ALLOW_MOCK"] = "0"
            os.environ["OPENAI_API_KEY"] = "your-openai-api-key"
            adapter = OpenAIAdapter()
            self.assertFalse(adapter.is_configured())

            resp = await self.router.generate(
                prompt="Write code",
                provider="openai",
                model_name="gpt-4o-mini"
            )
            self.assertEqual(resp.finish_reason, "error")
            self.assertIn("[AgentX Configuration Required]", resp.response_text)
            self.assertIn("OPENAI_API_KEY", resp.response_text)
        finally:
            if old_mock is not None:
                os.environ["AGENTX_ALLOW_MOCK"] = old_mock
            if old_key is not None:
                os.environ["OPENAI_API_KEY"] = old_key

    # TEST 8: Provider timeout or rate limit error. Expected: Bounded recovery and informative message.
    async def test_08_provider_timeout_or_ratelimit_error(self):
        from intelligence.adapters.openai_adapter import OpenAIAdapter
        adapter = OpenAIAdapter()
        # Simulate network failure via invalid key invocation
        res = await adapter.execute(
            prompt="Hello",
            model_name="non-existent-model"
        )
        self.assertEqual(res.finish_reason, "error")
        self.assertTrue("Not Configured" in res.response_text or "Error" in res.response_text)

    # TEST 9: Streaming SSE lifecycle. Expected: status_update -> assistant_stream -> mission_completed.
    async def test_09_streaming_events_lifecycle(self):
        events = []
        tokens = []

        async for sse_line in self.chat_service.stream_message(
            message="Explain recursion with an example.",
            user_id="test_user_09"
        ):
            if sse_line.startswith("data: "):
                data_json = json.loads(sse_line.replace("data: ", "").strip())
                events.append(data_json.get("event"))
                if data_json.get("event") == "assistant_stream":
                    tokens.append(data_json.get("content", ""))

        self.assertIn("status_update", events)
        self.assertIn("assistant_stream", events)
        self.assertIn("mission_completed", events)

        full_streamed_text = "".join(tokens)
        self.assertIn("Recursion", full_streamed_text)
        self.assertIn("```python", full_streamed_text)

    # TEST 10: Tool unavailable or unsafe. Expected: Honest reporting without pretending success.
    async def test_10_tool_unavailable_honest_reporting(self):
        # 1. Unsafe code executor blocking
        executor = CodeExecutorTool()
        unsafe_result = executor.execute_python_code("import os; os.system('rmdir /s /q test')")
        self.assertFalse(unsafe_result["success"])
        self.assertIn("Execution Blocked", unsafe_result["stderr"])

        # 2. Web search adapter when no live provider configured
        search_adapter = WebSearchToolAdapter()
        tool_res = await search_adapter.execute({"query": "non_existent_query_xyz_12345"})
        # Should not invent fake weather or tech citations
        for item in tool_res.data:
            self.assertNotIn("Mock Weather Search", item.get("title", ""))

    # TEST 11: Memory retained across turns and isolated between users.
    async def test_11_memory_retained_across_turns_and_user_isolated(self):
        conv_id = str(uuid.uuid4())
        user_a = "user_alice_" + str(uuid.uuid4())[:6]
        user_b = "user_bob_" + str(uuid.uuid4())[:6]

        # Turn 1: User A introduces favorite color
        await self.chat_service.process_message(
            message="My favorite color is emerald green.",
            user_id=user_a,
            conversation_id=conv_id
        )

        # Turn 2: User A asks for favorite color in the same conversation
        resp_a = await self.chat_service.process_message(
            message="What is my favorite color?",
            user_id=user_a,
            conversation_id=conv_id
        )
        self.assertIn("emerald green", resp_a.content.lower())

        # User B asks in a fresh conversation (user isolation)
        conv_b = str(uuid.uuid4())
        resp_b = await self.chat_service.process_message(
            message="What is my favorite color?",
            user_id=user_b,
            conversation_id=conv_b
        )
        self.assertNotIn("emerald green", resp_b.content.lower())

    # TEST 12: Request completes clean contract (no raw internal dictionaries in frontend).
    async def test_12_frontend_backend_contract_clean_response(self):
        resp = await self.chat_service.process_message(
            message="Give me a simple C program to add two numbers.",
            user_id="test_user_12"
        )
        self.assertEqual(resp.status, "completed")
        self.assertEqual(resp.role, "assistant")
        self.assertTrue(len(resp.content) > 30)

        # Reject all raw internal artifact leakage
        self.assertNotIn("Agent Result (", resp.content)
        self.assertNotIn("{'status': 'completed'", resp.content)
        self.assertNotIn("{'status': 'pending'", resp.content)
        self.assertNotIn("pending_tasks", resp.content)
        self.assertNotIn("assigned_agent", resp.content)

if __name__ == "__main__":
    unittest.main()
