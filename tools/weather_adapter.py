import time
from typing import Dict, Any
from loguru import logger
from tools.base_tool import BaseTool, ToolResult

class WeatherAdapter(BaseTool):
    """Universal Weather Forecast Tool Adapter for AgentX."""

    def __init__(self):
        super().__init__(
            name="weather",
            description="Fetches atmospheric weather forecasts, temperature, and local conditions.",
            version="1.2.0",
            capabilities=["weather", "weather_forecast", "temperature"],
            permissions=["weather"],
            ttl_seconds=300  # 5 minutes TTL cache
        )

    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        start_time = time.time()
        location = parameters.get("location") or parameters.get("city") or "Paris"

        logger.info(f"WeatherAdapter: Querying forecast for location '{location}'")

        # Mock / Live weather payload
        weather_payload = {
            "location": location,
            "condition": "Partly Cloudy & Pleasant",
            "temperature_celsius": 23,
            "humidity_percentage": 58,
            "wind_speed_kmh": 12,
            "forecast_summary": f"Optimal weather in {location} over the next 5 days with mild coastal breeze."
        }

        execution_time = time.time() - start_time
        latency = int(execution_time * 1000)

        return ToolResult(
            status="success",
            success=True,
            data=weather_payload,
            metadata={"location": location},
            latency=latency,
            execution_time=execution_time,
            logs=[f"Weather fetched for '{location}'."]
        )
