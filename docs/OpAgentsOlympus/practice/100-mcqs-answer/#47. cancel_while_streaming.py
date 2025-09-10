from agents import Agent, Runner, function_tool
import asyncio
from open_router_config import config


@function_tool
async def long_running_task(query: str) -> str:
    await asyncio.sleep(5)  # Long operation
    return f"Completed {query}"


@function_tool
def quick_task(data: str) -> str:
    return f"Quick: {data}"


agent = Agent(
    name="Worker",
    tools=[long_running_task, quick_task],
)


async def test_cancellation():
    result = Runner.run_streamed(agent, "Do both tasks", run_config=config)

    # Cancel after 2 seconds
    await asyncio.sleep(2)
    result.cancel()

    # Try to consume remaining events
    events = []
    async for event in result.stream_events():
        events.append(event.type)

    print(result.final_output, len(events))


asyncio.run(test_cancellation())
