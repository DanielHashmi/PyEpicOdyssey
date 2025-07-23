from open_router_config import config
from agents import Agent, Runner, function_tool, RunContextWrapper
import asyncio
from rich import print
from pydantic import BaseModel
from typing import Any
class UserData(BaseModel):
    name: str
    age: int

@function_tool
def hello(ctx: RunContextWrapper[Any]) -> str:
    """Used to say hello"""
    try:
        print(f'Name: {ctx.context.name} Age: {ctx.context.age}')
    except Exception as e:
        print('Context Unavailable!')
    return 'None' # Return None

class Great(BaseModel):
    great: str

userdata = UserData(name='Daniel', age=18)

assistant = Agent(
    name="assistant",
    instructions='You are a helpful assistant.',
    tools=[hello],
    # output_type=Great,
    # tool_use_behavior='stop_on_first_tool' # This means no further LLM processing, The output of the first tool directly become the final_output
)

async def main():
    result = await Runner.run(assistant, input="say hello", run_config=config, context=userdata)
    print(result.final_output)
    print(type(result.final_output))

asyncio.run(main())