from open_router_config import config
from agents import Agent, Runner, function_tool
import asyncio
@function_tool
def hello() -> str:
    """Used to say hello"""
    print('hello was called')
    return 'hello'
@function_tool
def bye() -> str:
    """Used to say bye"""
    print('bye was called')
    return 'bye'

assistant = Agent(
    name="assistant",
    instructions='You are a helpful assistant.',
    tools=[hello, bye],
    tool_use_behavior={'stop_at_tool_names': ['hello']} # stop on hello
)

async def main():
    result = await Runner.run(assistant, input="say hello and bye", run_config=config)
    print(result.final_output)

asyncio.run(main())

# <== Output ==>
# hello was called
# bye was called
# hello