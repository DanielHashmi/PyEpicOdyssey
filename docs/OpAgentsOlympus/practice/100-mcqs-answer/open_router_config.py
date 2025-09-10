import os

try:
    from dotenv import load_dotenv, find_dotenv
    from agents import AsyncOpenAI, OpenAIChatCompletionsModel
    from agents.run import RunConfig
except ImportError:
    raise ImportError(
        "\nThis package requires 'openai-agents' to be installed.\n"
        "\nPlease install it first using pip:\n"
        "\npip install openai-agents\n"
        "\nFor more information, visit: https://openai.github.io/openai-agents-PyDeepOlympus/quickstart/\n"
    )

# Load environment variables
load_dotenv(find_dotenv())

API_KEY = os.environ.get("OPENROUTER_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1"
MODEL = "openai/gpt-4o-mini"

model = OpenAIChatCompletionsModel(
    model=MODEL, openai_client=AsyncOpenAI(api_key=API_KEY, base_url=BASE_URL)
)
# Runner config (you can export this)
config = RunConfig(model=model, tracing_disabled=True)
