from agents import Runner, Agent, function_tool
import asyncio
from open_router_config import config


@function_tool
def say_hello():
    print("say_hello was called...")
    return "Hello!"


async def main():
    agent = Agent(
        name="assistant",
        instructions="You are a helpful assistant. you MUST call say_hello tool",
        tools=[say_hello],
        tool_use_behavior=[
            "stop_on_first_tool"
        ],  # Passed a List, This will cause a UserError!
    )

    result = await Runner.run(agent, input="Say Hello!", run_config=config)
    print("\nFinal Output:", result.final_output)


if __name__ == "__main__":
    asyncio.run(main())


# _run_impl.py
# Line 983: raise UserError(f"Invalid tool_use_behavior: {agent.tool_use_behavior}")
