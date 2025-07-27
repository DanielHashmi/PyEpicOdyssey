import asyncio
from agents import Agent, Runner, function_tool, GuardrailFunctionOutput, RunContextWrapper
from config import config
from pydantic import BaseModel

class UserData(BaseModel):
    name: str
    height: float

@function_tool
async def get_user_data(context: RunContextWrapper[UserData]) -> GuardrailFunctionOutput: # Context is not accessible without RunContextWrapper
    """This tool can be used to get the user data so that the llm can understand about the user"""
    print(f"Getting user data...")
    return context.context

async def main():  
    agent = Agent(  
        name="Super Assistant",
        instructions=(
            "You are Super Assistant, an expert and proactive AI assistant. "
            "Use available tools to retrieve information you do not know. "
            "You DON'T need to ask the user for calling tools. "
        ),
        tools=[get_user_data]
    )
    
    userdata = UserData(name='Daniel', height=5.11)
  
    result = await Runner.run(agent, input="What is the name of the user?", context=userdata, run_config=config)  
    print(result.final_output)
  
if __name__ == "__main__":  
    asyncio.run(main())