from agents import AsyncOpenAI, OpenAIChatCompletionsModel, Agent, Runner, function_tool, set_tracing_disabled, ModelSettings
import os
import dotenv

set_tracing_disabled(True)
dotenv.load_dotenv()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url='https://generativelanguage.googleapis.com/v1beta/openai',
)

model = OpenAIChatCompletionsModel(
    'gemini-2.0-flash',
    openai_client=client
)

@function_tool(name_override='add_tool')
def add(a: int, b: int) -> int:
    print("Adding...")
    return a + b

@function_tool
def subtract(a: int, b: int) -> int:
    print("Subtracting...")
    return a - b

assistant = Agent(
    name='assistant',
    instructions='You are a helpful assistant.',
    tools=[add, subtract],
    model=model,
    model_settings=ModelSettings(
        tool_choice='subtract'
    )
)

result = Runner.run_sync(assistant, 'Hello')
print(result.final_output)