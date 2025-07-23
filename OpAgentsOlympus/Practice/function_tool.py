from pydantic import BaseModel
from agents import Agent, GuardrailFunctionOutput, Runner, set_tracing_disabled, OpenAIChatCompletionsModel, InputGuardrail, RunConfig, enable_verbose_stdout_logging
from openai.types.responses import ResponseTextDeltaEvent
import os
from openai import AsyncOpenAI
import dotenv
import asyncio
from config import config
enable_verbose_stdout_logging()
# dotenv.load_dotenv()
# set_tracing_disabled(True)
# GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# if not GEMINI_API_KEY:
#     raise ValueError("API key not found!!")

# client = AsyncOpenAI(
#     api_key=GEMINI_API_KEY,
#     base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
# )
# model = OpenAIChatCompletionsModel(model='gemini-2.0-flash', openai_client=client)
# config = RunConfig(model=model, model_provider=client)

class HomeworkOutput(BaseModel):
    is_homework: bool
    reasoning: str

guardrail_agent = Agent(
    name="Guardrail check",
    instructions="Check if the user is asking about homework.",
    output_type=HomeworkOutput,
)

math_tutor_agent = Agent(
    name="Math Tutor",
    handoff_description="Specialist agent for math questions",
    instructions="You provide help with math problems. Explain your reasoning at each step and include examples",
)

history_tutor_agent = Agent(
    name="History Tutor",
    handoff_description="Specialist agent for historical questions",
    instructions="You provide assistance with historical queries. Explain important events and context clearly.",
)


async def homework_guardrail(ctx, agent, input_data):
    result = await Runner.run(guardrail_agent, input_data, context=ctx.context, run_config=config)
    final_output = result.final_output_as(HomeworkOutput)
    print(final_output)
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=not final_output.is_homework,
    )

triage_agent = Agent(
    name="Triage Agent",
    instructions="You determine which agent to use based on the user's homework question",
    handoffs=[history_tutor_agent, math_tutor_agent],
    input_guardrails=[
        InputGuardrail(guardrail_function=homework_guardrail),
    ]
)

async def main():
    # result =  Runner.run_streamed(triage_agent, "What is 2 + 2?", run_config=config)

    result = Runner.run_streamed(triage_agent, "Solve this homework question: What is 2 + 2 = _ ", run_config=config)
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)
    # print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())