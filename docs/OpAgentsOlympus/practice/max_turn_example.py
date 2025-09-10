import asyncio

from agents import Agent, ItemHelpers, Runner, function_tool
from open_router_config import config


@function_tool
def get_weather(city: str) -> str:
    return f"Weather in {city} is sunny."


assistant = Agent(
    name="assistant",
    instructions=("You are a helpful assistant."),
    tools=[get_weather],
    tool_use_behavior="stop_on_first_tool",
)


async def main():
    msg = "What is the weather in karachi?"

    result = Runner.run_streamed(assistant, msg, run_config=config, max_turns=1)

    async for event in result.stream_events():
        # We'll ignore the raw responses event deltas
        if event.type == "raw_response_event":
            continue
        elif event.type == "agent_updated_stream_event":
            print(f"Agent updated: {event.new_agent.name}")
            continue
        elif event.type == "run_item_stream_event":
            if event.item.type == "tool_call_item":
                print("-- Tool was called")
            elif event.item.type == "tool_call_output_item":
                print(f"-- Tool output: {event.item.output}")
            elif event.item.type == "message_output_item":
                print(
                    f"-- Message output:\n {ItemHelpers.text_message_output(event.item)}"
                )
            else:
                pass  # Ignore other event types


if __name__ == "__main__":
    asyncio.run(main())
