import asyncio
from agents import Agent, Runner, set_trace_processors
from langsmith.wrappers import OpenAIAgentsTracingProcessor
from open_router_config import config
async def main():
    assistant = Agent(
        name="Assistant",
        instructions="You are helpful Assistant.",
    )

    question = "How are you?."
    result = await Runner.run(agent, question, run_config=config)
    print(result.final_output)

if __name__ == "__main__":
    set_trace_processors([OpenAIAgentsTracingProcessor()])
    asyncio.run(main()) 