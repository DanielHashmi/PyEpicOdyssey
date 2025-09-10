from dataclasses import dataclass  
from agents import Agent, RunContextWrapper, Runner, function_tool  
from config import config
import asyncio

@dataclass(frozen=True)  # Makes the dataclass immutable  
class ImmutableUserInfo:  
    name: str  
    uid: int  
    age: int = 47  
  
@function_tool(failure_error_function=None) # Set failure_error_function=None so we can see the error.
async def get_user_age(wrapper: RunContextWrapper[ImmutableUserInfo]) -> str:  
    """Get the user's age - cannot modify context."""  
    wrapper.context.name = "John" # This would raise an error
    return f"The user {wrapper.context.name} is {wrapper.context.age} years old"  
  
async def main():  
    user_info = ImmutableUserInfo(name="Daniel", uid=123)
    
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