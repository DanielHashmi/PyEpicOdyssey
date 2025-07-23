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
  
async def main():  
    result = Runner.run_streamed(agent, "Do both tasks", run_config=config)  
  
    # Consume first batch of events  
    events = []  
    async for event in result.stream_events():  
        events.append(event.type)  
        print(f'Event: {event.type}')  
        if len(events) == 3:  
            break  
          
    print("Stream Complete:", result.is_complete)
    print(f"First batch events: {events}, Length: {len(events)}")

    # Resume consuming events  
    async for event in result.stream_events():  
        events.append(event.type)  
        print(f'Resumed event: {event.type}')  
        # if len(events) == 10:
        #     break
    print("Stream Complete:", result.is_complete)
    print(f"Second batch events: {events}, Length: {len(events)}")
  
asyncio.run(main())