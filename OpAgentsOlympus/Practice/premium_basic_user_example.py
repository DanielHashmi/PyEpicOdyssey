import asyncio

from agents import Agent, ItemHelpers, Runner, RunContextWrapper
from open_router_config import config
from dataclasses import dataclass


@dataclass
class UserContext:
    name: str
    is_premium_user: bool
    age: int


daniel = UserContext("Daniel", True, 19)
ahmad = UserContext("Ahmad", False, 21)


def dynamic_instructions(
    ctx: RunContextWrapper[UserContext], _: Agent[UserContext]
) -> str:
    if ctx.context.is_premium_user:
        return "You are a premium agent, You can help the user with premium features."
    return "You are a basic agent, You can help the user with basic tasks."


assistant = Agent(
    name="assistant",
    instructions=dynamic_instructions,
)


async def main():
    msg = "Who are you?"

    result = Runner.run_streamed(assistant, msg, run_config=config, context=daniel)

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
