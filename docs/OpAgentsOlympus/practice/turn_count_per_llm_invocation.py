from agents import Agent, Runner, function_tool, AgentHooks, RunContextWrapper, ModelResponse, TResponseInputItem
from typing import Optional, Any
from local_config import config


class LLMCallTracker(AgentHooks):
    def __init__(self):
        self.llm_call_count = 0

    async def on_llm_start(
        self,
        context: RunContextWrapper,
        agent: Agent,
        system_prompt: Optional[str],
        input_items: list[TResponseInputItem],
    ) -> None:
        self.llm_call_count += 1
        print(f"LLM Call #{self.llm_call_count}")

    async def on_llm_end(
        self,
        context: RunContextWrapper,
        agent: Agent,
        response: ModelResponse,
    ) -> None:
        print(f"LLM Call #{self.llm_call_count} completed")

    async def on_tool_start(
        self,
        context: RunContextWrapper[Any],
        agent: Any,
        tool: Any,
    ) -> None:
        """Called concurrently with tool invocation."""
        print('Tool started!')

    async def on_tool_end(
        self,
        context: RunContextWrapper[Any],
        agent: Any,
        tool: Any,
        result: str,
    ) -> None:
        """Called after a tool is invoked."""
        print('Tool ended!')


@function_tool
def get_weather(city: str) -> str:
    """Get weather information for a city."""
    return f"The weather in {city} is sunny and 75°F"


async def main():
    tracker = LLMCallTracker()

    agent = Agent(
        name="Assistant",
        instructions="Help users with weather information. Use the appropriate tools.",
        tools=[get_weather],
        hooks=tracker
    )

    print("Starting workflow demonstrations...")
    print("=" * 60)

    print("First Runner.run() call:")

    result1 = await Runner.run(
        agent,
        input="What's the weather in Tokyo and what time is it there?",
        run_config=config
    )

    print("Workflow completed!")
    print(f"Final output: {result1.final_output}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

# Add "print(f"Turn: {current_turn}#")" under "current_turn += 1" inside Runner.run's while loop to actually see how many times did the turn counter increased for each LLM call.


# < =======Output======= >
# Starting workflow demonstrations...
# ============================================================
# First Runner.run() call:
# Turn: 1#
# LLM Call #1
# LLM Call #1 completed
# Tool started!
# Tool ended!
# Turn: 2#
# LLM Call #2
# LLM Call #2 completed
# Workflow completed!
# Final output: <think>
# Okay, the user asked for the weather in Tokyo and the time there. I called the get_weather function and got back that the weather is sunny and 75°F. Now I need to answer the user's question based on this response. The user also asked about the time, but the tool doesn't provide time information. So I should mention the weather details and clarify that the time isn't available with the current tools. Let me make sure the answer is clear and helpful.
# </think>

# The weather in Tokyo is currently sunny with a temperature of 75°F. Note that the exact time in Tokyo isn't provided by the available tools. Let me know if you need further weather details!
