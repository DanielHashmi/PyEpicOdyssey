from agents import (
    Agent,
    Runner,
    RunHooks,
    AgentHooks,
    RunContextWrapper,
    function_tool,
    TContext,
    set_tracing_disabled
)

from typing import Any
from config import model
import asyncio
from agents.extensions.handoff_prompt import prompt_with_handoff_instructions

set_tracing_disabled(True)

class CustomRunHooks(RunHooks): # RunHooks are configured by default so they will run anyway, but since they don't do anything (pass), that's why i have customized them to print.
    async def on_agent_start(self, context: RunContextWrapper[TContext], agent: Any) -> None:
        print('RunHook: on_agent_start...')

class CustomAgentHooks(AgentHooks):
    async def on_start(self, context: RunContextWrapper[TContext], agent: Any) -> None:
        print('AgentHook: on_start...')

@function_tool
def say_hello_to_user(user: str):
    print('calling tool...')
    return f"Hello, {user}!"

say_hello_to_user_agent = Agent( # as_tool will run this agent entirely independent, Everything that you pass in the Runner methods (except context and user input) is new: max_turns, hooks, run_config etc...
    name="say_hello_to_user_agent",
    instructions=prompt_with_handoff_instructions("You are say_hello_to_user_agent, MUST call say_hello_to_user tool"),
    tools=[say_hello_to_user],
    hooks=CustomAgentHooks(),
    model=model
)

triage_agent = Agent(
    name="triage_agent",
    instructions=prompt_with_handoff_instructions("You are a helpful assistant, MUST call say_hello_to_user tool"),
    hooks=CustomAgentHooks(),
    tools=[say_hello_to_user_agent.as_tool(tool_name='say_hello_to_user', tool_description='used to say hello to a user')],
    model=model
)

async def main():
    result = await Runner.run(
        triage_agent, "say hello to daniel!", hooks=CustomRunHooks()
    )
    print(result.final_output)

asyncio.run(main())

# ====== Results ======
# RunHook: on_agent_start...
# AgentHook: on_start...
# AgentHook: on_start... You will only see agent hooks running for the as_tool agent, because it's run hooks are doing nothing (pass), we haven't customized run hooks of as_tool agent!
# calling tool...
# Hello, daniel!

# Problems with .as_tool
# Problem: Unexpected errors because of missing parameters like custom run_config if using non-openai models. Solution: avoid using config in Runner, instead set model in individual agents
# Problem: Not enough customizable. Solution: build your custom .as_tool (call agent inside a tool)


# Source Code in openai-agents-python/src/agents/agent.py:
# async def run_agent(context: RunContextWrapper, input: str) -> str:
#     from .run import Runner

#     output = await Runner.run(
#         starting_agent=self,
#         input=input,
#         context=context.context,
#     )
#     if custom_output_extractor:
#         return await custom_output_extractor(output)

#     return ItemHelpers.text_message_outputs(output.new_items)

# The source code above is a function_tool inside as_tool method which runs an agent with an independent Runner. You can see it's a basic Runner.run that only inherits context and user input from the parent Runner.


# Question: When the parent agent invokes the agent-as-tool, what is the correct relationship between the parent's hook system and the child agent's independent execution context?
# Answer: B
