from openai import AsyncOpenAI
from agents import (
    Agent,
    Runner,
    OpenAIChatCompletionsModel,
    RunConfig,
    ModelSettings
)
import os
import dotenv

dotenv.load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError(
        "I guess you haven't set API KEY, I'am pretty sure you need to set it dude.")

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
    instructions="You are an amazing assistant, You only respond in haikus LOL MUST CALL A TOOL",
    model_settings=ModelSettings(
        max_tokens=10
    )
)

result = Runner.run_sync(
    agent,
    "Am I a CODER?",
    run_config=config,
)

print(result.final_output)

# max_tokens=1
# PyEpicOdyssey\OpAgentsOlympus\Practice> python max_tokens.py
# A
# PyEpicOdyssey\OpAgentsOlympus\Practice> python max_tokens.py
# Skills

# max_tokens=10
# PyEpicOdyssey\OpAgentsOlympus\Practice> python max_tokens.py
# Query code skill,
# Tool will check with swift command,

# This behavior is NEVER deterministic so you NEVER know how will be the output.
# Only LLM calls consume tokens. However, tokens are also consumed by other features included in LLM requests or responses, such as tool schemas or tool calls made by the LLM.

# More about token consumption: https://github.com/DanielHashmi/PyEpicOdyssey/blob/main/OpAgentsOlympus/OpAgentsTokenConsumption.md