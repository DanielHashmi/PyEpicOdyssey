from agents import Agent, Runner, SQLiteSession
from open_router_config import config
import asyncio

session = SQLiteSession("workflow.db")
agent = Agent(name="Stateful", instructions="Remember our conversation")

async def main():
    # First execution
    result1 = await Runner.run(agent, "My name is Alice", session=session, run_config=config)

    # Second execution with different input format
    result2 = await Runner.run(agent, [
        {"role": "user", "content": "What's my name?"}
    ], session=session)

asyncio.run(main())