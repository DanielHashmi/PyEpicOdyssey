import asyncio
from agents import Agent, Runner, AgentHooks, RunContextWrapper, TContext
from config import config
from pydantic import BaseModel

class UserData(BaseModel):
    name: str
    height: float

class CustomAgentHooks(AgentHooks):
    async def on_start(self, context, agent: Agent) -> None: # Context is accessible without RunContextWrapper
        """Called before the agent is invoked. Called each time the running agent is changed to this agent."""
        print(f"Agent {agent.name} started with context: {context.context}")

async def main():  
    agent = Agent(  
        name="Super Assistant",  
        instructions="You are a helpful assistant.",
        hooks=CustomAgentHooks()
    )
    
    userdata = UserData(name='Daniel', height=5.11)
  
    result = await Runner.run(agent, input="how are you?", context=userdata, run_config=config)  
    print(result.final_output)
  
if __name__ == "__main__":  
    asyncio.run(main())