from agents import (
    Agent,
    Runner,
    RunContextWrapper,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    RunConfig,
    function_tool,
)
import os
import dotenv

dotenv.load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set. Please define it in your .env file.")

external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# Preferred Gemini model setup
model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash", openai_client=external_client
)

# Runner config (you can export this)
config = RunConfig(model=model, model_provider=external_client)


# Tool 1: Get current location
@function_tool
def get_current_location(ctx: RunContextWrapper[None]) -> str:
    """Returns the user's current location."""
    # Dummy location for demonstration
    return "New York, USA"


# Tool 2: Get breaking news
@function_tool
def get_breaking_news(ctx: RunContextWrapper[None]) -> list[str]:
    """Returns a list of breaking news headlines."""
    return [
        "Global markets rally amid economic optimism.",
        "Major breakthrough in renewable energy announced.",
    ]


# Tool 3: Explain photosynthesis
@function_tool
def explain_photosynthesis(ctx: RunContextWrapper[None]) -> str:
    """Explains the process of photosynthesis."""
    return "Photosynthesis is the process by which green plants use sunlight to synthesize foods from carbon dioxide and water."


agent = Agent[None](
    name="multi_query_agent",
    instructions="Answer each query using the appropriate tools. MUST call TOOLS",
    tools=[get_current_location, get_breaking_news, explain_photosynthesis],
)

config.tracing_disabled = False  # Make sure tracing is not disabled

result = Runner.run_sync(
    agent,
    """
    1. What is my current location?
    2. Any breaking news?
    3. What is photosynthesis
    """,
    run_config=config,
)

print("=" * 50)
print("Result: ", result.last_agent.name)
# print(result.new_items)
print("Result: ", result.final_output)
