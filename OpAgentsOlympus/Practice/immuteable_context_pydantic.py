from pydantic import BaseModel, ConfigDict  
from agents import Agent, RunContextWrapper, Runner, function_tool  
from config import config
import asyncio

class ImmutableUserInfo(BaseModel):  
    model_config = ConfigDict(frozen=True)  # Makes Pydantic model immutable  
      
    name: str  
    uid: int  
    age: int = 60 # 😁
    friends: tuple[str, ...] # Use tuple instead of list for immutability  
  
@function_tool(failure_error_function=None) # Set failure_error_function=None so we can see the error.
async def get_user_age(wrapper: RunContextWrapper[ImmutableUserInfo]) -> str:  
    """Get the user's age - cannot modify context."""  
    # wrapper.context.name = "John" # This would raise an error
    # wrapper.context.friends.append('Ahmad Memon') # This will also raise an error because tuple has no attribute append 🤷‍♂️
    return f"The user {wrapper.context.name} is {wrapper.context.age} years old"  

async def main():  
    user_info = ImmutableUserInfo(name="Daniel", uid=123, friends=['Junaid', 'Ali'])
    
    agent = Agent[ImmutableUserInfo](  
        name="Assistant",  
        tools=[get_user_age],  
    )  
      
    result = await Runner.run(  
        starting_agent=agent,  
        input="What is the user's age?",  
        context=user_info,
        run_config=config
    )
    print(result.final_output)
    
asyncio.run(main())