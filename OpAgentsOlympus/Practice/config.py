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
        "\nFor more information, visit: https://openai.github.io/openai-agents-python/quickstart/\n"
    )

# Load environment variables
load_dotenv(find_dotenv())
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set. Please define it in your .env file.")

# Setup Gemini client
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# Preferred Gemini model setup
model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash", openai_client=external_client
)

# Runner config (you can export this)
config = RunConfig(model=model, model_provider=external_client, tracing_disabled=True)
