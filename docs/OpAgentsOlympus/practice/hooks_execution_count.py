from agents import Agent, Runner, function_tool, AgentHooks, RunHooks, RunContextWrapper
from typing import Any
from config import config
import asyncio

class HookCounter:
    def __init__(self):
        self.counts = {
            "on_start": 0,
            "on_end": 0,
            "on_agent_start": 0,
            "on_agent_end": 0,
            "on_handoff": 0,
            "on_tool_start": 0,
            "on_tool_end": 0,
        }

    def inc(self, key: str):
        if key in self.counts:
            self.counts[key] += 1

    def report(self):
        for k, v in self.counts.items():
            print(f"{k}_hook_count: {v}")

hook_counter = HookCounter()

class CustomAgentHooks(AgentHooks[Any]):
    async def on_start(self, context: RunContextWrapper[Any], agent: Any) -> None:
        hook_counter.inc("on_start")

    async def on_end(self, context: RunContextWrapper[Any], agent: Any, output: Any) -> None:
        hook_counter.inc("on_end")

    async def on_handoff(self, context: RunContextWrapper[Any], agent: Any, source: Any) -> None:
        hook_counter.inc("on_handoff")

    async def on_tool_start(self, context: RunContextWrapper[Any], agent: Any, tool: Any) -> None:
        hook_counter.inc("on_tool_start")

    async def on_tool_end(self, context: RunContextWrapper[Any], agent: Any, tool: Any, result: str) -> None:
        hook_counter.inc("on_tool_end")

class CustomRunHooks(RunHooks):
    async def on_agent_start(self, context: RunContextWrapper[Any], agent: Any) -> None:
        hook_counter.inc("on_agent_start")

    async def on_agent_end(self, context: RunContextWrapper[Any], agent: Any, output: Any) -> None:
        hook_counter.inc("on_agent_end")

    async def on_handoff(self, context: RunContextWrapper[Any], from_agent: Any, to_agent: Any) -> None:
        hook_counter.inc("on_handoff")

    async def on_tool_start(self, context: RunContextWrapper[Any], agent: Any, tool: Any) -> None:
        hook_counter.inc("on_tool_start")

    async def on_tool_end(self, context: RunContextWrapper[Any], agent: Any, tool: Any, result: str) -> None:
        hook_counter.inc("on_tool_end")

@function_tool
def tool1():
    """MUST call me"""
    print("tool1 was called!")

@function_tool
def tool2():
    """MUST call me"""
    print("tool2 was called!")

@function_tool
def tool3():
    """MUST call me"""
    print("tool3 was called!")

@function_tool
def tool4():
    """MUST call me"""
    print("tool4 was called!")

agent_C = Agent(name="agent_C", hooks=CustomAgentHooks())
agent_B = Agent(
    name="agent_B",
    instructions="MUST call both tools, MUST handoff to agent_C",
    tools=[tool3, tool4],
    handoffs=[agent_C],
    hooks=CustomAgentHooks()
)
agent_A = Agent(
    name="agent_A",
    instructions="MUST call both tools, MUST handoff to agent_B",
    tools=[tool1, tool2],
    handoffs=[agent_B],
    hooks=CustomAgentHooks()
)

async def main():
    await Runner.run(
        agent_A, input="Start the workflow.", run_config=config, hooks=CustomRunHooks()
    )
    hook_counter.report()

if __name__ == "__main__":
    asyncio.run(main())

# If there are three agents agent_A, agent_B and agent_C,
# agent_A handoff to agent_B, agent_B handoff to agent_C,
# Before each handoff two tools will be called and we have configured RunHooks as well <= (means both, RunHooks + AgentHooks)
# How many time each hook was called?

# Make sure the LLm you are using is capable of executing all tools and handoffs!!
# <== OUTPUT ==>
# tool1 was called!
# tool2 was called!
# tool3 was called!
# tool4 was called!
# on_start_hook_count: 3
# on_end_hook_count: 1
# on_agent_start_hook_count: 3
# on_agent_end_hook_count: 1
# on_handoff_hook_count: 4
# on_tool_start_hook_count: 8
# on_tool_end_hook_count: 8