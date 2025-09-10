from agents import Agent, Runner, function_tool, RunContextWrapper, RunHooks, TContext, TResponseInputItem, ModelResponse
from typing import Optional, Any
from open_router_config import config

class HelloRunHooks(RunHooks):

    async def on_llm_start(
        self,
        context: RunContextWrapper[TContext],
        agent: Agent[TContext],
        system_prompt: Optional[str],
        input_items: list[TResponseInputItem],
    ) -> None:
        """Called just before invoking the LLM for this agent."""
        print('on_llm_start')

    async def on_llm_end(
        self,
        context: RunContextWrapper[TContext],
        agent: Agent[TContext],
        response: ModelResponse,
    ) -> None:
        """Called immediately after the LLM call returns for this agent."""
        print('on_llm_end')

    async def on_agent_start(self, context: RunContextWrapper[TContext], agent: Any) -> None:
        """Called before the agent is invoked. Called each time the current agent changes."""
        print('on_agent_start')

    async def on_agent_end(
        self,
        context: RunContextWrapper[TContext],
        agent: Any,
        output: Any,
    ) -> None:
        """Called when the agent produces a final output."""
        print('on_agent_end')
        
    async def on_handoff(
        self,
        context: RunContextWrapper[TContext],
        from_agent: Any,
        to_agent: Any,
    ) -> None:
        """Called when a handoff occurs."""
        print('on_handoff')

    async def on_tool_start(
        self,
        context: RunContextWrapper[TContext],
        agent: Any,
        tool: Any,
    ) -> None:
        """Called concurrently with tool invocation."""
        print('on_tool_start')

    async def on_tool_end(
        self,
        context: RunContextWrapper[TContext],
        agent: Any,
        tool: Any,
        result: str,
    ) -> None:
        """Called after a tool is invoked."""
        print('on_tool_tool')


@function_tool
def get_weather(city: str) -> str:
    """A simple function to get the weather for a user."""
    return f"The weather for {city} is sunny."

news_agent: Agent = Agent(
    name="NewsAgent",
    instructions="You are a helpful news assistant.",
)

base_agent: Agent = Agent(
    name="WeatherAgent",
    instructions="You are a helpful assistant. Talk about weather and let news_agent handle the news things",
    tools=[get_weather],
    handoffs=[news_agent]
)

res = Runner.run_sync(
    starting_agent=base_agent, 
    input="What's the latest news about Qwen Code - seems like it can give though time to claude code.",
    hooks=HelloRunHooks(),
    run_config=config
)

print(res.last_agent.name)
print(res.final_output)