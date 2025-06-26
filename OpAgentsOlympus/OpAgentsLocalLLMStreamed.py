# Imports
from openai import AsyncOpenAI  
from agents import Agent, Runner, OpenAIChatCompletionsModel, set_tracing_disabled
from openai.types.responses import ResponseTextDeltaEvent
import asyncio

# Settings
set_tracing_disabled(True) # Disabled Tracing
custom_model = OpenAIChatCompletionsModel(  
    model="cognito-v1:3b", # Local LLM Using Jan
    openai_client=AsyncOpenAI(  
        base_url="http://localhost:1337/v1", # BASE URL of Jan Local Server
        api_key="12345" # Custom API KEY set in Jan
    )  
)  

# Agent
agent = Agent(  
    name="Assistant",  
    instructions="You are a helpful assistant",   
    model=custom_model  
)

# Streaming
async def main():
    result = Runner.run_streamed(agent, "write a haiku about recursion?")  
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)
            
asyncio.run(main())
