from open_router_config import config
from agents import Agent, Runner, function_tool
import asyncio
from pydantic import BaseModel


@function_tool
def hello() -> str:
    """Used to say hello"""
    return None  # Return None


class Great(BaseModel):
    great: str


assistant = Agent(
    name="assistant",
    instructions="You are a helpful assistant.",
    tools=[hello],
    output_type=Great,
    tool_use_behavior="stop_on_first_tool",
)


async def main():
    result = await Runner.run(assistant, input="say hello", run_config=config)
    print(type(result.final_output))  # What is the output_type?


asyncio.run(main())
