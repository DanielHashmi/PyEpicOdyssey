import asyncio
from agents import Agent, Runner, function_tool
from langsmith import traceable
from open_router_config import config


@traceable
async def traced_agent_run(agent, question, config):
    return await Runner.run(agent, question, run_config=config)


@function_tool
def get_weather(city: str):
    return f"The weather in {city} is sunny"


async def main():
    agent = Agent(
        name="Assistant", instructions="You are helpful Assistant.", tools=[get_weather]
    )

    result = await traced_agent_run(agent, "What is the weather in karachi?", config)
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
