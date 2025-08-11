from agents import Agent, Runner, OpenAIChatCompletionsModel
from openai import AsyncOpenAI
import os
import asyncio

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

load_dotenv(find_dotenv())
API_KEY = os.environ.get("OPENROUTER_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1"
MODEL = "openai/gpt-4o-mini"

client = AsyncOpenAI(api_key=API_KEY, base_url=BASE_URL)

model = OpenAIChatCompletionsModel(model=MODEL, openai_client=client)
# # Load environment variables
# gemini_api_key = os.getenv("GEMINI_API_KEY")
# set_tracing_disabled(True)

# if not gemini_api_key:
#     raise ValueError("GEMINI_API_KEY is not set. Please define it in your .env file.")

# Setup Gemini client
# external_client = AsyncOpenAI(
#     api_key=gemini_api_key,
#     base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
# )

# Preferred Gemini model setup
# model = OpenAIChatCompletionsModel(
#     model="gemini-2.5-flash-preview-04-17",
#     openai_client=external_client
# )

# Runner config (you can export this)
config = RunConfig(model=model, tracing_disabled=True)

joke_agent = Agent(
    name="joke_agent",
    instructions="You are a joke agent. Your job is to generate jokes.",
)

orchestrator_agent = Agent(
    name="orchestrator_agent",
    instructions="You are an orchestrator agent, you use joke_tool tool to generate jokes",
    tools=[
        joke_agent.as_tool(
            tool_name="joke_tool", tool_description="A Joke Generator Tools"
        )
    ],
)


async def main():
    result = await Runner.run(
        orchestrator_agent,
        "Give me 2 jokes for a person who is a sleepy coder.",
        run_config=config,
    )
    print(result.final_output)


asyncio.run(main())
