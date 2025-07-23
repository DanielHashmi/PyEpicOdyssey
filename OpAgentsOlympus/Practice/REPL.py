from __future__ import annotations

from typing import Any
import asyncio
import os
import dotenv
from openai.types.responses.response_text_delta_event import ResponseTextDeltaEvent
from agents import Agent, Runner, TResponseInputItem, OpenAIChatCompletionsModel, set_tracing_disabled, function_tool
from openai import AsyncOpenAI
from agents.result import RunResultBase
from agents.stream_events import RawResponsesStreamEvent, RunItemStreamEvent, AgentUpdatedStreamEvent

dotenv.load_dotenv()
set_tracing_disabled(True)
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

if not GEMINI_API_KEY:
    raise ValueError("API key not found!!")

client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
model = OpenAIChatCompletionsModel(model='gemini-2.0-flash', openai_client=client)

async def run_demo_loop(agent: Agent[Any], *, stream: bool = True) -> None:
    """Run a simple REPL loop with the given agent.

    This utility allows quick manual testing and debugging of an agent from the
    command line. Conversation state is preserved across turns. Enter ``exit``
    or ``quit`` to stop the loop.

    Args:
        agent: The starting agent to run.
        stream: Whether to stream the agent output.
    """

    current_agent = agent
    input_items: list[TResponseInputItem] = []
    while True:
        try:
            user_input = input(" > ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if user_input.strip().lower() in {"exit", "quit"}:
            break
        if not user_input:
            continue

        input_items.append({"role": "user", "content": user_input})

        result: RunResultBase
        if stream:
            result = Runner.run_streamed(current_agent, input=input_items)
            async for event in result.stream_events():
                if isinstance(event, RawResponsesStreamEvent):
                    if isinstance(event.data, ResponseTextDeltaEvent):
                        print(event.data.delta, end="", flush=True)
                elif isinstance(event, RunItemStreamEvent):
                    if event.item.type == "tool_call_item":
                        print("\n[tool called]", flush=True)
                    elif event.item.type == "tool_call_output_item":
                        print(f"\n[tool output: {event.item.output}]", flush=True)
                elif isinstance(event, AgentUpdatedStreamEvent):
                    print(f"\n[Agent updated: {event.new_agent.name}]", flush=True)
            print()
        else:
            result = await Runner.run(current_agent, input_items)
            if result.final_output is not None:
                print(result.final_output)

        current_agent = result.last_agent
        input_items = result.to_input_list()
        
async def main():
    @function_tool
    def say_hello(name: str):
        """Used to say hello
        
        args:
            name (str): name of the person to whom you say hello
        """
        return f"Hello! {name}"
    
    education_assistant = Agent(name="education_assistant", instructions="You are a helpful Education Assistant.", handoff_description='Used to get help with educations', model=model)
    agent = Agent(name="Assistant", instructions="You are a helpful assistant.", model=model, tools=[say_hello], handoffs=[education_assistant])
    education_assistant.handoffs.append(agent)
    await run_demo_loop(agent, stream=True)

if __name__ == "__main__":
    asyncio.run(main())