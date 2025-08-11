# The answer is A: "The tool choice remains "required" causing an infinite loop"

# When reset_tool_choice=False, the framework does not reset the tool_choice after a tool call
# The tool_choice remains "required"
# After the first tool call, the results are sent back to the LLM
# Since tool_choice is still "required", the LLM must make another tool call
# This cycle continues indefinitely, creating an infinite loop
# This is exactly why the default behavior (reset_tool_choice=True) exists - to prevent these infinite loops by automatically resetting tool_choice to "auto" after tool calls.

from __future__ import annotations
import asyncio
from open_router_config import config
from agents import Agent, Runner, function_tool, ModelSettings
from agents.exceptions import MaxTurnsExceeded


@function_tool
def simple_tool(message: str):
    """A simple tool that echoes the message back."""
    print(f"Tool called with message: {message}")
    return f"Processed: {message}"


agent = Agent(
    name="TestAgent",
    instructions="You are a helpful assistant. Use the simple_tool whenever possible.",
    tools=[simple_tool],
    reset_tool_choice=False,  # Key setting we're testing
)


async def main():
    config.model_settings = ModelSettings(
        tool_choice="required"
    )  # Key setting we're testing

    try:
        result = await Runner.run(agent, "Hello", run_config=config)
        print("Final output:", result.final_output)
    except MaxTurnsExceeded as e:
        print(f"Max turns exceeded: {e}")
        print(
            "This confirms the agent entered an infinite loop because tool_choice remained 'required'"
        )


if __name__ == "__main__":
    asyncio.run(main())

# <=== Output ===>
# Tool called with message: Hello!
# Tool called with message: Hello!
# Tool called with message: Hello!
# Tool called with message: Hello!
# Tool called with message: Hello!
# Tool called with message: Hello!
# Tool called with message: Hello!
# Tool called with message: Hello!
# Tool called with message: Hello!
# Tool called with message: Hello!
# Max turns exceeded: Max turns (10) exceeded
# This confirms the agent entered an infinite loop because tool_choice remained 'required'
