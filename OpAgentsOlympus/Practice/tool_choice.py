from agents import (
    Agent,
    Runner,
    AsyncOpenAI,
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

external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash", openai_client=external_client
)

config = RunConfig(model=model, model_provider=external_client)

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
        tool_choice='do_i_deserve_it'
    ),
    tools=[am_i_coder, do_i_deserve_it]
)

result = Runner.run_sync(
    agent,
    "Am I a CODER?",
    run_config=config,
)

print(result.final_output)

# tool_choice = "none"  <-- The tools will be hidden from the LLM.
# Lines of code you write,
# Logic flows from your own mind,
# Coder, you may be. <----------- Don't be confused with this "may be", Trust me the LLM didn't even saw the tools.

# tool_choice = None  <-- The behavior depends on the LLM provider's defaults.
# Perhaps you code well,
# Or maybe just a little, <------- Tool was called!
# The tool is unsure.

# Difference between None and "none"
# tool_choice=None → returns NOT_GIVEN
# tool_choice='none' → returns "none"

# Difference between None and "auto"
# tool_choice=None → Uses whatever default the LLM provider has configured
# tool_choice="auto" → Explicitly tells the LLM it can decide whether to use tools or not

# tool_choice='required' → Must call a tool
# tool_choice='tool_name' → Must call that tool
