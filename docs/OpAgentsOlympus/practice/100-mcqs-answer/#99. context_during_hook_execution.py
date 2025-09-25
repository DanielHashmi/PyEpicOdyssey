from agents import (
    Agent,
    Runner,
    RunHooks,
    AgentHooks,
    RunContextWrapper,
    ItemHelpers
)

from typing import Any
from local_config import config
from pydantic import BaseModel
import asyncio
from agents.extensions.handoff_prompt import prompt_with_handoff_instructions

class UserData(BaseModel):
    name: str
    height: float

class CustomRunHooks(RunHooks):
    async def on_handoff(
        self,
        context: RunContextWrapper[UserData],
        from_agent: Any,
        to_agent: Any,
    ) -> None:
        print(f"name: {context.context.name}, from_agent: {from_agent.name}, to_agent: {to_agent.name}") # same context

class CustomAgentHooks(AgentHooks):
    async def on_handoff(
        self,
        context: RunContextWrapper[UserData],
        agent: Any,
        source: Any,
    ) -> None:
        print(f"name: {context.context.name}, agent: {agent.name}, source: {source.name}") # same context

user_data = UserData(name='Horain', height=5.8)

numpy_agent = Agent(
    name="numpy_agent",
    instructions=prompt_with_handoff_instructions("You are a master of numpy."),
    hooks=CustomAgentHooks(),
    handoff_description='Master of numpy'
)

python_agent = Agent(
    name="python_agent",
    instructions=prompt_with_handoff_instructions("You are a master of python, If user is asking about something that is related to numpy, handoff to numpy_agent"),
    hooks=CustomAgentHooks(),
    handoffs=[numpy_agent],
    handoff_description='Master of python'
)

triage_agent = Agent(
    name="triage_agent",
    instructions=prompt_with_handoff_instructions("You are a triage_agent. If user is asking about something that is related to python, handoff to python_agent"),
    hooks=CustomAgentHooks(),
    handoffs=[python_agent],
)

async def main():
    result = Runner.run_streamed(
        triage_agent, "What is numpy?", run_config=config, hooks=CustomRunHooks(), context=user_data
    )

    async for event in result.stream_events():
        if event.type == "raw_response_event":
            continue
        elif event.type == "agent_updated_stream_event":
            print(f"Agent updated: {event.new_agent.name}")
            continue
        elif event.type == "run_item_stream_event":
            if event.item.type == "tool_call_item":
                print("-- Tool was called")
            elif event.item.type == "tool_call_output_item":
                print(f"-- Tool output: {event.item.output}")
            elif event.item.type == "message_output_item":
                print(
                    f"-- Message output:\n {ItemHelpers.text_message_output(event.item)}"
                )
            else:
                pass

asyncio.run(main())

# Question: When AgentRunner._start_streaming() processes a NextStepHandoff and switches from one agent to another, how does the RunContextWrapper[TContext] and hook execution behave?
# Answer: B
