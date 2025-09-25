from agents import (
    Agent,
    Runner,
    RunHooks,
    TContext,
    RunContextWrapper,
    AgentsException,
    function_tool,
    Tool
)
from typing import Any
from local_config import config

class CustomRunHooks(RunHooks):
    async def on_tool_start( # tool start hooks and tool itself are called currently, But! you will see the hooks running first because they are the starting arguments in the asyncio.gather
        self,
        context: RunContextWrapper[TContext],
        agent: Any,
        tool: Tool,
    ) -> None:
        print('on_tool_start...')
        raise ValueError('Error Occurred!') # ValueError is not an instance of AgentException, under the hood SDK catches this ValueError and raises a UserError instead!
    
    async def on_tool_end( # on_tool_end will not be invoked since all subsequent hooks will be skipped if error occurs!
        self,
        context: RunContextWrapper[TContext],
        agent: Any,
        tool: Tool,
        result: str,
    ) -> None:
        print('on_tool_end...')

@function_tool
def say_hello_to_user(user: str):
    print('tool called...')
    return f'Hello, {user}!'

assistant = Agent(
    name="assistant",
    instructions="You are a helpful assistant, ALWAYS USE A TOOL",
    tools=[say_hello_to_user],
)
try:
    result = Runner.run_sync(
        assistant, "Say hello to user: Daniel", run_config=config, hooks=CustomRunHooks()
    )
    print(result.final_output)
except AgentsException as e:
    print(e.run_data) # run_data is only available in AgentException instances
    
# =====> Result <=====
# on_tool_start...
# tool called...
# RunErrorDetails:
# - Last agent: Agent(name="assistant", ...)
# - 0 new item(s)
# - 0 raw response(s)
# - 0 input guardrail result(s)
# (See `RunErrorDetails` for more details)