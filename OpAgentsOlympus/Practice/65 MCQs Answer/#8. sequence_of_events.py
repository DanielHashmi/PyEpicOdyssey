import asyncio  
from agents import Agent, Runner  
from agents.stream_events import StreamEvent  
  
async def print_all_streaming_events():  
    agent = Agent(  
        name="Test Agent",  
        instructions="You are a helpful assistant.",  
    )  
      
    result = Runner.run_streamed(agent, input="Hello, tell me a joke and use any tools if needed.")  
      
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
              
        print("=" * 50)  
      
    print(f"\nTotal events processed: {event_count}")  
    print(f"Final output: {result.final_output}")  
  
if __name__ == "__main__":  
    asyncio.run(print_all_streaming_events())