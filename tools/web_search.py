import os
from typing import List, Dict, Any
from loguru import logger

class WebSearchTool:
    """Performs web search queries, falling back gracefully if API keys are missing."""
    
    def __init__(self):
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")

    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Perform semantic search across the web."""
        logger.info(f"WebSearchTool: Executing query '{query}'")
        
        # 1. Try Tavily search if API key is configured
        if self.tavily_api_key and "your-" not in self.tavily_api_key:
            try:
                from tavily import TavilyClient
                client = TavilyClient(api_key=self.tavily_api_key)
                response = client.search(query, max_results=max_results)
                results = []
                for item in response.get("results", []):
                    results.append({
                        "title": item.get("title"),
                        "url": item.get("url"),
                        "content": item.get("content")
                    })
                return results
            except Exception as e:
                logger.error(f"WebSearchTool: Tavily search error: {e}. Falling back...")
                
        # 2. Try DuckDuckGo fallback
        try:
            from langchain_community.tools import DuckDuckGoSearchRun
            ddg = DuckDuckGoSearchRun()
            # ddg.run executes synchronously, we run in executor or just wrap it
            logger.info("WebSearchTool: Using DuckDuckGo search fallback.")
            summary = ddg.run(query)
            return [{
                "title": f"DuckDuckGo search results summary for: {query}",
                "url": "https://duckduckgo.com",
                "content": summary
            }]
        except Exception as e:
            logger.error(f"WebSearchTool: DuckDuckGo search error: {e}. Returning mock results.")
            
        # 3. Return Mock search results
        return [
            {
                "title": f"Mock Weather Search result for {query}",
                "url": "https://example.com/weather",
                "content": f"The weather for {query} is currently sunny and 22°C. Wind is at 10km/h."
            },
            {
                "title": f"Mock Tech Search result for {query}",
                "url": "https://example.com/tech",
                "content": "AgentX is an advanced Autonomous Multi-Agent AI Ecosystem built using Python and Node.js."
            }
        ]
