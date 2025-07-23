import asyncio

from pydantic import BaseModel

from agents import Agent, Runner, function_tool
from config import config

class Weather(BaseModel):
    city: str
    temperature_range: str
    conditions: str


@function_tool
def get_weather(city: str) -> Weather:
    print("[debug] get_weather called")
    return Weather(city=city, temperature_range="14-20C", conditions="Sunny with wind.")


Assistant = Agent(
    name="Assistant",
    instructions="You are a helpful Assistant.",
    tools=[get_weather],
)


async def main():
    result = await Runner.run(Assistant, input="What's the weather in Tokyo?", run_config=config)
    print(result.final_output)
    # The weather in Tokyo is sunny.


if __name__ == "__main__":
    asyncio.run(main())