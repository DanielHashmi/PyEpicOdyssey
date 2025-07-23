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
    return filtered # This data will be received to the next handoff agent.

say_bye_agent = Agent(
    name="say_bye_agent",
    instructions='You only say bye to everyone.'
)

say_hello_agent1 = Agent(
    name="say_hello_agent1",
    instructions='You only say hello to everyone.',
    handoffs=[
        handoff(
            agent=say_bye_agent,
            input_filter=remove_new_items,
        )
    ],
)

say_hello_agent2 = Agent(
    name="say_hello_agent2",
    instructions='You only say hello to everyone.',
    handoffs=[
        handoff(
            agent=say_bye_agent,
        )
    ],
)

async def main():
    result = Runner.run_streamed(say_hello_agent2, input="say hello and bye", run_config=config)
    async for _ in result.stream_events():
        pass
    print("Not Filtered:", result.to_input_list())
    
    result = Runner.run_streamed(say_hello_agent1, input="say hello and bye", run_config=config)
    async for _ in result.stream_events():
        pass
    print("Filtered:", result.to_input_list())

asyncio.run(main())