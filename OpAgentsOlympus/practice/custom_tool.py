from agents import FunctionTool, RunContextWrapper, Agent, Runner
from pydantic import BaseModel
from typing import Any
from open_router_config import config


class ProcessArgs(BaseModel):
    city: str


async def fetch_weather_function(ctx: RunContextWrapper[Any], args: str) -> str:
    parsed = ProcessArgs.model_validate_json(args)
    return f"The weather in {parsed.city} is Sunny."


fetch_weather_tool = FunctionTool(
    name="fetch_weather_tool",
    description="Fetch weather for a city:str",
    params_json_schema=ProcessArgs.model_json_schema(),
    on_invoke_tool=fetch_weather_function,
    strict_json_schema=True,
)
print(ProcessArgs.model_json_schema())
assistant = Agent(
    name="Assistant",
    instructions="You are a friendly assistant.",
    tools=[fetch_weather_tool],
)

result = Runner.run_sync(
    assistant, "What is the weather in karachi?", run_config=config
)
print(result.final_output)
