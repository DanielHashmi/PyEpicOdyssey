from openai import AsyncOpenAI
from agents import (
    Agent,
    Runner,
    OpenAIChatCompletionsModel,
    RunConfig,
    ModelSettings,
    function_tool
)
import os
import dotenv

dotenv.load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("I guess you haven't set API KEY, I'am pretty sure you need to set it dude.")

client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash", openai_client=client
)

config = RunConfig(model=model)

@function_tool
def am_i_coder():
    return 'Maybe 🤷‍♂️'

@function_tool
def do_i_deserve_it():
    return 'Maybe 🤷‍♂️'

agent = Agent[None](
    name="assistant",
    instructions="You are an amazing assistant, You only respond in haikus LOL MUST CALL A TOOL",
    model_settings=ModelSettings(
        parallel_tool_calls=False # Setting parallel_tool_calls=False only works with OpenAI Models
    ),
    tools=[am_i_coder, do_i_deserve_it]
)

result = Runner.run_sync(
    agent,
    "Am I a CODER?"
    "Do i deserve it?",
    run_config=config,
)

print(result.final_output)
