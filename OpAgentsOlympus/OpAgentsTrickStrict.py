import asyncio  
from typing import Optional  
from agents import (  
    Agent,   
    Runner,   
    function_tool,   
    set_tracing_disabled,   
    OpenAIChatCompletionsModel,
    AsyncOpenAI,
    enable_verbose_stdout_logging
)  
import os
import dotenv
dotenv.load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
enable_verbose_stdout_logging()

external_client = AsyncOpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai",
    api_key=GEMINI_API_KEY
)
set_tracing_disabled(True)

model = OpenAIChatCompletionsModel(
    model='gemini-1.5-flash-8b',
    openai_client=external_client
)
  
@function_tool(strict_mode=True)  
def strict_calculator(a: int, b: Optional[int] = None) -> str:  
    """Calculate three given numbers 
      
    Args:  
        a: First number  
        b: Second number (optional)
        c: Third number (optional)  
    """  
    print("strict_calculator called")
    if b is None:  
        return f"Strict Result: {a}"  
    return f"Strict Result: {a + b}"  
  
@function_tool(strict_mode=False)  
def non_strict_calculator(a: int, b: Optional[int] = None) -> str:  
    """Calculate three given numbers 
      
    Args:  
        a: First number    
        b: Second number (optional)  
        c: Third number (optional)  
    """  
    print("non_strict_calculator called")
    if b is None:  
        return f"Non-strict Result: {a}"  
    return f"Non-strict Result: {a + b}"  
  
strict_agent = Agent(  
    name="Strict Agent",  
    model=model,
    instructions="You are a calculator assistant. You MUST use the strict_calculator tool for all calculations, strict_calculator tool has 3 arguments to be passed, a: int, b: Optional[int] = None, c: Optional[int] = None",  
    tools=[strict_calculator]  
)  
  
non_strict_agent = Agent(  
    name="Non-Strict Agent",
    model=model,
    instructions="You are a calculator assistant. You MUST use the non_strict_calculator tool for all calculations, non_strict_calculator tool has 3 arguments to be passed, a: int, b: Optional[int] = None, c: Optional[int] = None",  
    tools=[non_strict_calculator]  
)  
  
async def main():    
    result1 = await Runner.run(  
        starting_agent=strict_agent,  
        input="What is 2 + 2 + 2"  
    )  
    print(f"Strict agent result: {result1.final_output}")
    
    result2 = await Runner.run(  
        starting_agent=non_strict_agent,  
        input="What is 2 + 2 + 2"  
    )  
    print(f"Non-strict agent result: {result2.final_output}")  

if __name__ == "__main__":  
    asyncio.run(main())
