from agents import Agent, Runner, handoff, enable_verbose_stdout_logging, OpenAIChatCompletionsModel, AsyncOpenAI, set_tracing_disabled, function_tool # type: ignore
from agents.handoffs import HandoffInputData
import os
import dotenv
import asyncio

dotenv.load_dotenv()
set_tracing_disabled(True)
api_key = os.environ.get("GEMINI_API_KEY")

client = AsyncOpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
model = OpenAIChatCompletionsModel(model='gemini-2.0-flash', openai_client=client)
enable_verbose_stdout_logging()

# Define some example function tools
@function_tool
def tool_1():  
    """First parallel tool"""  
    return "Result from tool 1"  
  
@function_tool
def tool_2():  
    """Second parallel tool"""  
    return "Result from tool 2"  
  
@function_tool
def tool_3():  
    """Third parallel tool"""  
    return "Result from tool 3"  
  
# Custom input filter that modifies pre_handoff_items and prints debug info  
def custom_input_filter(handoff_input_data: HandoffInputData) -> HandoffInputData:  
    print("=== BEFORE FILTERING ===")  
    print(f"Input history length: {len(handoff_input_data.input_history) if isinstance(handoff_input_data.input_history, tuple) else 'string'}")  
    print(f"Pre-handoff items count: {len(handoff_input_data.pre_handoff_items)}")  
    print(f"New items count: {len(handoff_input_data.new_items)}")  
      
    # Clear pre_handoff_items to demonstrate filtering  
    filtered_data = HandoffInputData(  
        input_history=handoff_input_data.input_history,  
        pre_handoff_items=(),  # Clear pre_handoff_items  
        new_items=handoff_input_data.new_items,  
    )  
      
    print("=== AFTER FILTERING ===")  
    print(f"Input history length: {len(filtered_data.input_history) if isinstance(filtered_data.input_history, tuple) else 'string'}")  
    print(f"Pre-handoff items count: {len(filtered_data.pre_handoff_items)}")  
    print(f"New items count: {len(filtered_data.new_items)}")  
      
    return filtered_data  
  
# Agent B with debug printing  
class DebugAgent(Agent):  
    def __init__(self, *args, **kwargs):  
        super().__init__(*args, **kwargs)  
      
    async def _on_agent_start(self, context):  
        print(f"=== AGENT B RECEIVED INPUT ===")  
        # This would show what Agent B actually receives after filtering  
        print(f"Agent B starting with context")  
  
# Agent B (target of handoff)  
agent_b = DebugAgent(  
    name="Agent B",  
    instructions="You are Agent B, handling tasks after handoff.",
    model=model
)  
  
# Agent A (source agent with tools and handoff)  
agent_a = Agent(  
    name="Agent A",  
    instructions="You are Agent A. Use your tools and then handoff to Agent B.",  
    tools=[tool_1, tool_2, tool_3],
    model=model,
    handoffs=[  
        handoff(  
            agent=agent_b,  
            input_filter=custom_input_filter  # This modifies pre_handoff_items  
        )  
    ]  
)  
  
# Run the scenario
async def main():
    result = await Runner.run(  
        agent_a,
        input="Please use all your tools and then handoff to Agent B"  
    )
    print(f"Final result: {result.final_output}")  
    print(f"Final agent: {result.last_agent.name}")
    print(result)

asyncio.run(main())