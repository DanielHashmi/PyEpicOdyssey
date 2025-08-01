import os

try:
    from dotenv import load_dotenv, find_dotenv
    from agents.run import RunConfig
    from agents.extensions.models.litellm_model import LitellmModel
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

model=LitellmModel(model='gemini/gemini-2.0-flash', api_key=gemini_api_key)

# Runner config (you can export this)
config = RunConfig(
    model=model,
    tracing_disabled=True
)