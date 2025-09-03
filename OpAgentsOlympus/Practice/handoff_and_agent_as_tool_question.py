from agents import Agent, Runner
import asyncio
from config import model

say_hello  = Agent(name="say_hello",  instructions="used to say hello.", model=model)

assistant = Agent(
    name="assistant",
    instructions=(
        "You are a helpful assistant. You can handoff or call tools"
    ),
    tools=[say_hello.as_tool(tool_name='say_hello', tool_description='used to say hello.')],
    handoffs=[say_hello],
    model=model
)

async def main():
    result = await Runner.run(assistant, "Say hello to daniel!.")
    print(result.final_output)

asyncio.run(main())

# What will happen?