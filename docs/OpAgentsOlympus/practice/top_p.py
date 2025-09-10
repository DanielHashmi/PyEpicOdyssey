import os
import dotenv
from openai import AsyncOpenAI
from agents import (
    Agent,
    Runner,
    OpenAIChatCompletionsModel,
    RunConfig,
    ModelSettings,
)

dotenv.load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("I guess you haven't set API KEY, I'am pretty sure you need to set it dude.")

client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash", openai_client=client
)

config = RunConfig(model=model)

agent = Agent[None](
    name="assistant",
    instructions="You are a bro agent",
    model_settings=ModelSettings(
        top_p=0.1,
        max_tokens=50,
    ),
)

result = Runner.run_sync(
    agent,
    "What is an apple?",
    run_config=config,
)

print(result.final_output)
