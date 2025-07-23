from pydantic import BaseModel
from agents import Agent, GuardrailFunctionOutput, OutputGuardrailTripwireTriggered, RunContextWrapper, Runner, output_guardrail, set_tracing_disabled, OpenAIChatCompletionsModel, function_tool
import os
from openai import AsyncOpenAI
import dotenv
from dataclasses import dataclass
import asyncio
from config import config
# dotenv.load_dotenv()
# set_tracing_disabled(True)
# GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# if not GEMINI_API_KEY:
#     raise ValueError("API key not found!!")

# client = AsyncOpenAI(
#     api_key='12345',
#     base_url='http://127.0.0.1:1337/v1'
# )

# model = OpenAIChatCompletionsModel('gemma-3-4b', client)

@dataclass
class Purchase:
    item: str
    price: float

@dataclass
class UserContext:
    uid: str
    is_pro_user: bool
    
    def fetch_purchases(self) -> list[Purchase]:
        purchases = [Purchase('LG V60', 443.5), Purchase('DELL Precision 5510', 888.2)]
        return purchases
    
@function_tool
def get_user_data(ctx: RunContextWrapper[UserContext]):
    """Used to get the USER DATA and PURCHASES"""
    user_data = {
        'uid': ctx.context.uid,
        'is_pro_user': ctx.context.is_pro_user,
        'user_purchases': ctx.context.fetch_purchases()
    }
    return user_data

user_context = UserContext('123', True)
sells_agent = Agent[UserContext](
    name='sells_agent',
    instructions='You are a sells agent, USE get_user_data tool to get the USER DATA and PURCHASES, dont wait or ask just do it directly',
    tools=[get_user_data],
    # model=model
)

# @function_tool
# def get_weather(city: str) -> str:
#     return f"The weather in {city} is cold"

# agent = Agent(
#     name="Haiku agent",
#     instructions="Always respond in haiku form",
#     model=model,
#     tools=[get_weather],
# )

result = Runner.run_sync(sells_agent, 'What i the USER has bought?', context=user_context, run_config=config)

print(result.final_output)