from agents import (
    Agent,
    Runner,
    input_guardrail,
    RunContextWrapper,
    GuardrailFunctionOutput,
)
from pydantic import BaseModel
from open_router_config import config
# dotenv.load_dotenv()
# gemini_api_key = os.getenv("GEMINI_API_KEY")

# if not gemini_api_key:
#     raise ValueError("GEMINI_API_KEY is not set. Please define it in your .env file.")

# external_client = AsyncOpenAI(
#     api_key=gemini_api_key,
#     base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
# )

# # Preferred Gemini model setup
# model = OpenAIChatCompletionsModel(
#     model="gemini-2.0-flash", openai_client=external_client
# )

# # Runner config (you can export this)
# config = RunConfig(model=model, model_provider=external_client)


class CheckGuardrailOutput(BaseModel):
    is_study_related: bool
    student_input: str
    reasoning: str


@input_guardrail
async def check_prompt(ctx: RunContextWrapper, agent: Agent, input: str):
    check_input_agent = Agent(
        name="check_input_agent",
        instructions="You check the input of the student, If they are asking study related question or asking something that they should not ask.",
        output_type=CheckGuardrailOutput,
    )

    result = (
        await Runner.run(
            check_input_agent, f"Student Input: {input}", run_config=config
        )
    ).final_output_as(CheckGuardrailOutput)

    return GuardrailFunctionOutput(
        output_info=f"Reasoning: {result.reasoning}, Student Input: {result.student_input}",
        tripwire_triggered=not result.is_study_related,
    )


teacher = Agent(
    name="teacher",
    instructions="You are a helpful teacher",
    input_guardrails=[check_prompt],
)

result = Runner.run_sync(
    teacher, "I want to change my class timings 😭😭", run_config=config
)
print(result.final_output)
