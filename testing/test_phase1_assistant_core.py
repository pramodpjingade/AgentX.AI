import os
import sys
import uuid
import asyncio
import unittest
from datetime import datetime

# Add root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chat.service import ChatService
from chat.schemas import StandardChatResponse, ChatRequest
from chat.streaming import ChatStreamer
from chat.intent_classifier import ChatIntentClassifier
from chat.response_formatter import ResponseFormatter
from intelligence.router import IntelligenceRouter
from agents.model_manager import ModelManager
from agents.master_agent.agent import MasterAgent
from agents.coding_agent.agent import CodingAgent

class TestPhase1AssistantCore(unittest.IsolatedAsyncioTestCase):
    """
    Official Phase 1 Verification Test Suite for AgentX AI Assistant.
    Validates all 10 core requirements established in Section 9 of the specification.
    """

    async def asyncSetUp(self):
        # Enable explicit mock mode for offline test reproducibility
        os.environ["AGENTX_ALLOW_MOCK"] = "true"
        self.service = ChatService()

    # TEST 1: "What is Python?"
    async def test_01_what_is_python(self):
        """Expected: A meaningful explanation without raw agent metadata."""
        prompt = "What is Python?"
        response = await self.service.process_message(
            message=prompt,
            conversation_id=str(uuid.uuid4()),
            streaming=False
        )

        self.assertIsInstance(response, StandardChatResponse)
        self.assertEqual(response.role, "assistant")
        content = response.content

        # Meaningful content
        self.assertTrue(len(content) > 30, f"Response too short: {content}")
        self.assertTrue("python" in content.lower(), "Response does not mention Python")
        self.assertTrue(any(w in content.lower() for w in ["programming", "language", "interpreted", "high-level"]), 
                        f"Response lacks explanation: {content}")

        # No raw agent metadata or internal traces
        self.assertNotIn("Agent Result", content)
        self.assertNotIn("safety_agent", content)
        self.assertNotIn("intent_agent", content)
        self.assertNotIn("education_agent", content)
        self.assertNotIn("{'status':", content)
        self.assertNotIn('{"status":', content)

    # TEST 2: "What is today's date?"
    async def test_02_todays_date(self):
        """Expected: A correct answer based on available date/time source."""
        prompt = "What is today's date?"
        response = await self.service.process_message(
            message=prompt,
            conversation_id=str(uuid.uuid4()),
            streaming=False
        )

        content = response.content
        current_year = str(datetime.now().year)

        self.assertIn(current_year, content, f"Current year {current_year} not found in: {content}")
        self.assertTrue("date" in content.lower() or "today" in content.lower())
        self.assertNotIn("Agent Result", content)
        self.assertNotIn("{'status':", content)

    # TEST 3: "Give me a simple C program to add two numbers."
    async def test_03_c_program_addition(self):
        """Expected: A complete C program in a correctly formatted code block."""
        prompt = "Give me a simple C program to add two numbers."
        response = await self.service.process_message(
            message=prompt,
            conversation_id=str(uuid.uuid4()),
            streaming=False
        )

        content = response.content
        self.assertIn("```c", content, "Code block with 'c' language tag missing")
        self.assertIn("#include <stdio.h>", content, "Standard C include header missing")
        self.assertIn("main", content, "C main function missing")
        self.assertTrue("+" in content, "Addition operation missing in C code")
        self.assertNotIn("Agent Result", content)

    # TEST 4: "Write a Python program to reverse a string."
    async def test_04_python_program_reverse_string(self):
        """Expected: A valid Python solution in a correctly formatted code block."""
        prompt = "Write a Python program to reverse a string."
        response = await self.service.process_message(
            message=prompt,
            conversation_id=str(uuid.uuid4()),
            streaming=False
        )

        content = response.content
        self.assertIn("```python", content, "Python code block missing")
        self.assertTrue("reverse" in content.lower())
        self.assertTrue("[::-1]" in content or "reversed(" in content or "join" in content, 
                        "String reversal logic missing")
        self.assertNotIn("Agent Result", content)

    # TEST 5: "Explain recursion with an example."
    async def test_05_explain_recursion(self):
        """Expected: A useful explanation and example."""
        prompt = "Explain recursion with an example."
        response = await self.service.process_message(
            message=prompt,
            conversation_id=str(uuid.uuid4()),
            streaming=False
        )

        content = response.content
        self.assertTrue("base case" in content.lower(), "Explanation missing 'base case'")
        self.assertTrue("recursive" in content.lower() or "recursion" in content.lower())
        self.assertIn("```python", content, "Code example missing in recursion explanation")
        self.assertNotIn("Agent Result", content)

    # TEST 6: Specialized agent failure handling
    async def test_06_specialized_agent_failure_handling(self):
        """Expected: The failure is handled correctly and is not represented as successful completion."""
        # 1. Test coding agent failure behavior
        original_key = os.environ.get("AGENTX_ALLOW_MOCK")
        os.environ["AGENTX_ALLOW_MOCK"] = "false"
        
        # Test MasterAgent handling of failed subtask
        master = MasterAgent()
        failed_subtasks = {
            "coding_agent": {
                "status": "failed",
                "result": "SyntaxError: Compilation terminated abnormally on compiler node 4"
            }
        }
        res = await master.execute({
            "goal_id": "test-goal",
            "title": "Build a compiler plugin",
            "results": failed_subtasks
        })

        # Must record status failed when critical subtask failed without substantive results
        self.assertEqual(res["status"], "failed")
        # Must not contain raw JSON or internal agent names in the user text
        self.assertNotIn("--- Agent Result (coding_agent) ---", res["result"])

        os.environ["AGENTX_ALLOW_MOCK"] = original_key or "true"

    # TEST 7: Model API key is missing
    async def test_07_missing_api_key_configuration_error(self):
        """Expected: A clear configuration error without fabricated output."""
        original_mock_setting = os.environ.get("AGENTX_ALLOW_MOCK")
        os.environ["AGENTX_ALLOW_MOCK"] = "false"

        router = IntelligenceRouter()
        # Force a provider whose key is missing
        res = await router.generate(
            prompt="Write a Python script",
            provider="openai"
        )

        self.assertEqual(res.finish_reason, "error")
        self.assertTrue("Configuration Required" in res.response_text or "API Key Not Configured" in res.response_text,
                        f"Expected configuration guidance, got: {res.response_text}")
        self.assertTrue(any(k in res.response_text for k in ["OPENAI_API_KEY", "GOOGLE_API_KEY", "ANTHROPIC_API_KEY"]))

        os.environ["AGENTX_ALLOW_MOCK"] = original_mock_setting or "true"

    # TEST 8: Model provider is unavailable / error handling
    async def test_08_provider_unavailable_handling(self):
        """Expected: Controlled error handling or an explicitly configured fallback."""
        router = IntelligenceRouter()
        # Test simulated provider error via Ollama with invalid port
        old_url = os.environ.get("OLLAMA_BASE_URL")
        os.environ["OLLAMA_BASE_URL"] = "http://127.0.0.1:59999"

        from intelligence.adapters.ollama_adapter import OllamaAdapter
        adapter = OllamaAdapter()
        res = await adapter.execute("Hello")

        self.assertEqual(res.finish_reason, "error")
        self.assertTrue(len(res.safety_flags) > 0)
        self.assertTrue("Error" in res.response_text or "unavailable" in res.response_text)

        if old_url:
            os.environ["OLLAMA_BASE_URL"] = old_url

    # TEST 9: Backend returns a successful assistant response contract
    async def test_09_backend_frontend_contract(self):
        """Expected: The frontend displays the actual answer, not internal dictionaries."""
        prompt = "What is Python?"
        response = await self.service.process_message(
            message=prompt,
            conversation_id=str(uuid.uuid4()),
            streaming=False
        )

        # Validate StandardChatResponse schema
        self.assertTrue(hasattr(response, "conversation_id"))
        self.assertTrue(hasattr(response, "message_id"))
        self.assertTrue(hasattr(response, "role"))
        self.assertTrue(hasattr(response, "content"))
        self.assertEqual(response.role, "assistant")
        self.assertEqual(response.status, "completed")
        self.assertIsInstance(response.content, str)

        # Content must not be a stringified dictionary
        self.assertFalse(response.content.strip().startswith("{'"))
        self.assertFalse(response.content.strip().startswith('{"status"'))

        # Test SSE Streamer reconstruction
        chunks = []
        async for chunk_str in ChatStreamer.generate_chat_stream(
            conversation_id=response.conversation_id,
            message_id=response.message_id,
            final_content=response.content,
            user_message=prompt
        ):
            chunks.append(chunk_str)

        self.assertTrue(len(chunks) > 0)
        # Verify valid SSE data lines
        for c in chunks:
            self.assertTrue(c.startswith("data: "))

    # TEST 10: Assistant generates code with preserved formatting
    async def test_10_code_formatting_preservation(self):
        """Expected: Indentation, Markdown, and code formatting are preserved."""
        c_code_input = """#include <stdio.h>

int main() {
    int a = 5;
    int b = 10;
    int sum = a + b;
    printf("Sum = %d\\n", sum);
    return 0;
}"""

        # Verify ResponseFormatter preserves indentation and code blocks
        formatted = ResponseFormatter.sanitize_output(f"Here is your code:\n\n```c\n{c_code_input}\n```")
        self.assertIn("```c", formatted)
        self.assertIn("    int a = 5;", formatted, "Indentation was lost in formatter")
        self.assertIn("    int sum = a + b;", formatted, "Indentation was lost in formatter")

        # Test streaming word chunking preserves whitespace and newlines
        stream_chunks = []
        async for chunk_str in ChatStreamer.generate_chat_stream(
            conversation_id="conv-1",
            message_id="msg-1",
            final_content=f"```c\n{c_code_input}\n```",
            user_message="code test"
        ):
            if '"event":"assistant_stream"' in chunk_str:
                import json
                data = json.loads(chunk_str.replace("data: ", "").strip())
                stream_chunks.append(data.get("content", ""))

        reconstructed = "".join(stream_chunks)
        self.assertIn("    int a = 5;", reconstructed, "Indentation was lost in stream chunking")
        self.assertIn("```c\n#include <stdio.h>", reconstructed)

if __name__ == "__main__":
    unittest.main()
