from agents import (
    Runner,
    Agent,
    OpenAIChatCompletionsModel,
    AsyncOpenAI,
    function_tool,
    RunConfig,
    RunContextWrapper,
)
import os
from dotenv import load_dotenv
import asyncio
from dataclasses import dataclass

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in the environment variables.")

# Set up the API provider
provider = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# Define the AI model
model = OpenAIChatCompletionsModel(model="gemini-1.5-flash", openai_client=provider)

# Configure the run
config = RunConfig(model=model, model_provider=provider, tracing_disabled=True)


@dataclass
class Person:
    name: str
    age: int
    occupation: str


@function_tool
def info(ctx: RunContextWrapper[Person]) -> str:
    """
    Get name and age about a person.
    """
    # This is a placeholder implementation. Replace with actual information fetching logic.
    return f"{ctx.context.name} is {ctx.context.age} years old."


@function_tool
def occupation(ctx: RunContextWrapper[Person]) -> str:
    """
    Get occupation of a person.
    """
    return f"{ctx.context.name} is a {ctx.context.occupation}."


async def main():
    person = Person(name="Alice", age=30, occupation="Software Engineer")

    agent = Agent(
        name="info_agent",
        instructions="You are a helpful assistant that provides details about people using tools.",
        tools=[info, occupation],
    )

    result = await Runner.run(
        agent, input="tell me about the age of  person", context=person
    )
    print("\nFinal Output:", result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
