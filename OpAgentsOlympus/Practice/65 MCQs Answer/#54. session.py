from agents import Agent, Runner, SQLiteSession
from open_router_config import config
import asyncio

session = SQLiteSession("test.db")
agent = Agent(name="assistant", instructions='You are a helpful assistant')

async def main():
    # First run adds to session
    result1 = await Runner.run(agent, "my name is daniel and my height is 5.11", session=session, run_config=config)
    print(result1.final_output)
    
    # Second run with same session
    result2 = await Runner.run(agent, "what is my name?", session=session, run_config=config)
    print(result2.final_output)
    
    result2 = await Runner.run(agent, "what is my height?", session=session, run_config=config)
    print(result2.final_output)
    
asyncio.run(main())