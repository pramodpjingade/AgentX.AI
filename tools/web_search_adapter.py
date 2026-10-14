import time
from typing import Dict, Any, List
from loguru import logger
from tools.base_tool import BaseTool, ToolResult
from tools.web_search import WebSearchTool

class WebSearchToolAdapter(BaseTool):
    """Universal Web Search Tool Adapter for AgentX."""

    def __init__(self):
        super().__init__(
            name="web_search",
            description="Performs semantic search across the web, fetching reliable sources and citations.",
            version="1.2.0",
            capabilities=["web_search", "search_web", "google_search"],
            permissions=["web_search"],
            ttl_seconds=600  # 10 minutes cache
        )
        self.underlying_search = WebSearchTool()

    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        start_time = time.time()
        query = parameters.get("query") or parameters.get("q") or ""
        max_results = parameters.get("max_results", 5)

        logger.info(f"WebSearchToolAdapter: Executing web search for query '{query}'")

        try:
            results = await self.underlying_search.search(query, max_results=max_results)
            execution_time = time.time() - start_time
            latency = int(execution_time * 1000)

            citations = [
                {"title": item.get("title"), "url": item.get("url")}
                for item in results if isinstance(item, dict) and item.get("url")
            ]

            if not results:
                return ToolResult(
                    status="no_results",
                    success=True,
                    data=[],
                    metadata={"query": query, "results_count": 0},
                    latency=latency,
                    execution_time=execution_time,
                    citations=[],
                    logs=[f"Web search executed for '{query}' but no live results were returned."]
                )

            return ToolResult(
                status="success",
                success=True,
                data=results,
                metadata={"query": query, "results_count": len(results)},
                latency=latency,
                execution_time=execution_time,
                citations=citations,
                logs=[f"Web search completed for query '{query}' ({len(results)} items)."]
            )
        except Exception as e:
            execution_time = time.time() - start_time
            latency = int(execution_time * 1000)
            logger.error(f"WebSearchToolAdapter error: {e}")
            return ToolResult(
                status="failed",
                success=False,
                data=[],
                errors=[str(e)],
                latency=latency,
                execution_time=execution_time
            )
