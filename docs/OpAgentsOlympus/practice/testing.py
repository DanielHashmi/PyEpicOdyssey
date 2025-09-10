from agents import (
    Agent,
    Runner,
    set_tracing_disabled,
    OpenAIChatCompletionsModel,
    function_tool,
    RunHooks,
    AgentHooks,
    RunContextWrapper,
    TContext,
    Tool,
    RunConfig,
)
from typing import Any
import os
from openai import AsyncOpenAI
import dotenv
import asyncio

dotenv.load_dotenv()
set_tracing_disabled(True)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("API key not found!!")
client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
model = OpenAIChatCompletionsModel(model="gemini-1.5-pro", openai_client=client)


class Run_Hooks(RunHooks):
    """A class that receives callbacks on various lifecycle events in an agent run. Subclass and
    override the methods you need.
    """

    async def on_agent_start(
        self, context: RunContextWrapper[TContext], agent: Agent[TContext]
    ) -> None:
        """Called before the agent is invoked. Called each time the current agent changes."""
        print("Parent Runner: on_agent_start called...")

    async def on_agent_end(
        self,
        context: RunContextWrapper[TContext],
        agent: Agent[TContext],
        output: Any,
    ) -> None:
        """Called when the agent produces a final output."""
        print("Parent Runner: on_agent_end called...")

    async def on_handoff(
        self,
        context: RunContextWrapper[TContext],
        from_agent: Agent[TContext],
        to_agent: Agent[TContext],
    ) -> None:
        """Called when a handoff occurs."""
        print("Parent Runner: on_handoff called...")

    async def on_tool_start(
        self,
        context: RunContextWrapper[TContext],
        agent: Agent[TContext],
        tool: Tool,
    ) -> None:
        """Called before a tool is invoked."""
        print("Parent Runner: on_tool_start called...")

    async def on_tool_end(
        self,
        context: RunContextWrapper[TContext],
        agent: Agent[TContext],
        tool: Tool,
        result: str,
    ) -> None:
        """Called after a tool is invoked."""
        print("Parent Runner: on_tool_end called...")


class Agent_Hooks(AgentHooks):
    """A class that receives callbacks on various lifecycle events for a specific agent. You can
    set this on `agent.hooks` to receive events for that specific agent.

    Subclass and override the methods you need.
    """

    async def on_start(
        self, context: RunContextWrapper[TContext], agent: Agent[TContext]
    ) -> None:
        """Called before the agent is invoked. Called each time the running agent is changed to this
        agent."""
        print("Parent Agent: on_start called...")

    async def on_end(
        self,
        context: RunContextWrapper[TContext],
        agent: Agent[TContext],
        output: Any,
    ) -> None:
        """Called when the agent produces a final output."""
        print("Parent Agent: on_end called...")

    async def on_handoff(
        self,
        context: RunContextWrapper[TContext],
        agent: Agent[TContext],
        source: Agent[TContext],
    ) -> None:
        """Called when the agent is being handed off to. The `source` is the agent that is handing
        off to this agent."""
        print("Parent Agent: on_handoff called...")

    async def on_tool_start(
        self,
        context: RunContextWrapper[TContext],
        agent: Agent[TContext],
        tool: Tool,
    ) -> None:
        """Called before a tool is invoked."""
        print("Parent Agent: on_tool_start called...")

    async def on_tool_end(
        self,
        context: RunContextWrapper[TContext],
        agent: Agent[TContext],
        tool: Tool,
        result: str,
    ) -> None:
        """Called after a tool is invoked."""
        print("Parent Agent: on_tool_end called...")


class Child_Agent_Hooks(AgentHooks):
    """A class that receives callbacks on various lifecycle events for a specific agent. You can
    set this on `agent.hooks` to receive events for that specific agent.

    Subclass and override the methods you need.
    """

    async def on_start(
        self, context: RunContextWrapper[TContext], agent: Agent[TContext]
    ) -> None:
        """Called before the agent is invoked. Called each time the running agent is changed to this
        agent."""
        print("Child Agent: on_start called...")

    async def on_end(
        self,
        context: RunContextWrapper[TContext],
        agent: Agent[TContext],
        output: Any,
    ) -> None:
        """Called when the agent produces a final output."""
        print("Child Agent: on_end called...")

    async def on_handoff(
        self,
        context: RunContextWrapper[TContext],
        agent: Agent[TContext],
        source: Agent[TContext],
    ) -> None:
        """Called when the agent is being handed off to. The `source` is the agent that is handing
        off to this agent."""
        print("Child Agent: on_handoff called...")

    async def on_tool_start(
        self,
        context: RunContextWrapper[TContext],
        agent: Agent[TContext],
        tool: Tool,
    ) -> None:
        """Called before a tool is invoked."""
        print("Child Agent: on_tool_start called...")

    async def on_tool_end(
        self,
        context: RunContextWrapper[TContext],
        agent: Agent[TContext],
        tool: Tool,
        result: str,
    ) -> None:
        """Called after a tool is invoked."""
        print("Child Agent: on_tool_end called...")


config = RunConfig(model=model, model_provider=client)


@function_tool
def hello():
    return "Hello! from Say Hello Agent/Tool"


say_hello_agent = Agent(
    name="say_hello_agent",
    instructions="You are a say hello agent, You use tools to respond.",
    tools=[hello],
    # model=model,
    hooks=Child_Agent_Hooks(),
)

agent = Agent(
    name="agent",
    instructions="You are a friendly assistant, You use tools to respond.",
    tools=[say_hello_agent.as_tool("say_hello_tool", "A say hello tool")],
    # model=model,
    hooks=Agent_Hooks(),
)


async def main():
    result = await Runner.run(agent, "Say Hello!", hooks=Run_Hooks(), run_config=config)
    print(result.final_output)


asyncio.run(main())
