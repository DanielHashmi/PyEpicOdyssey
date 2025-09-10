from agents import Agent, Runner, OpenAIChatCompletionsModel, RunConfig, function_tool, RunContextWrapper, AgentBase
from openai import AsyncOpenAI
from pydantic import BaseModel
from typing import Any
import os
import dotenv

dotenv.load_dotenv()
API_KEY = os.environ.get("GEMINI_API_KEY")

client = AsyncOpenAI(
    api_key=API_KEY,
    base_url='https://generativelanguage.googleapis.com/v1beta/openai'
)

model = OpenAIChatCompletionsModel(
    model='gemini-1.5-flash',
    openai_client=client
)

config = RunConfig(model)

class UserContext(BaseModel):
    is_user_admin: bool

def is_user_admin(ctx, agent: AgentBase[Any]): # Specifying type hints for context is only required for tools not for other functions (e.g dynamic instructions, is_enabled, hooks, guardrails etc..)
    return True if ctx.context.is_user_admin else False

@function_tool(is_enabled=is_user_admin, failure_error_function=None)
def weather_tool(ctx: RunContextWrapper[UserContext], city: str) -> str: # Specifying type hint for the context is must for tools, because the SDK performs runtime type hint interception to detect these context types and excludes them from the JSON schema sent to the LLM, RunContextWrapper must be the first parameter.
    """Used to get weather in a city
    city: str
    """
    return f"The weather in {city} is sunny." if ctx.context.is_user_admin else 'Weather not found!'

assistant = Agent(
    name='assistant',
    instructions='You are a helpful assistant. use `weather_tool` tool to get weather of a city.',
    tools=[weather_tool]
)
user_data = UserContext(is_user_admin=True)
result =  Runner.run_sync(
    assistant,
    'What is weather in karachi?',
    run_config=config,
    context=user_data
)

print(result.final_output)