from open_router_config import config
from agents import HandoffInputData, Agent, handoff, Runner
import asyncio
from rich import print


def remove_new_items(handoff_input_data: HandoffInputData) -> HandoffInputData:
    # print("Before:", handoff_input_data)
    filtered = HandoffInputData(
        input_history=handoff_input_data.input_history,
        pre_handoff_items=handoff_input_data.pre_handoff_items,
        new_items=(),
    )
    # print("After:", filtered)
    return filtered  # This data will be received to the next handoff agent.


say_bye_agent = Agent(
    name="say_bye_agent", instructions="You only say bye to everyone."
)

say_hello_agent1 = Agent(
    name="say_hello_agent1",
    instructions="You only say hello to everyone.",
    handoffs=[
        handoff(
            agent=say_bye_agent,
            input_filter=remove_new_items,
        )
    ],
)

say_hello_agent2 = Agent(
    name="say_hello_agent2",
    instructions="You only say hello to everyone.",
    handoffs=[
        handoff(
            agent=say_bye_agent,
        )
    ],
)


async def main():
    result = Runner.run_streamed(
        say_hello_agent2, input="say hello and bye", run_config=config
    )
    event_count = 0
    async for event in result.stream_events():
        event_count += 1
        print(f"\n=== EVENT #{event_count} ===")
        print(f"Type: {event.type}")

        if event.type == "raw_response_event":
            print(f"Raw Event Type: {event.data.type}")
            print(f"Raw Event Data: {event.data}")

        elif event.type == "run_item_stream_event":
            print(f"Item Name: {event.name}")
            print(f"Item Type: {event.item.type}")
            print(f"Item: {event.item}")

        elif event.type == "agent_updated_stream_event":
            print(f"New Agent: {event.new_agent.name}")
        print("Not Filtered:", result.to_input_list())

    # result = Runner.run_streamed(say_hello_agent1, input="say hello and bye", run_config=config)
    # async for _ in result.stream_events():
    #     pass
    print("Filtered:", result.to_input_list())


asyncio.run(main())
