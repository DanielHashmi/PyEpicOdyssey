from agents import (
    Agent,
    Runner,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    RunConfig,
    ModelSettings
)
import os
import dotenv

dotenv.load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set. Please define it in your .env file.")

external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash", openai_client=external_client
)

config = RunConfig(model=model, model_provider=external_client)

agent = Agent[None](
    name="assistant",
    instructions="You are an amazing assistant, You only respond in haikus",
    model_settings=ModelSettings(
        temperature=0.9
    )
)

result = Runner.run_sync(
    agent,
    "What is an apple?",
    run_config=config,
)

print(result.final_output)

# Temperature = 0.1
# PyEpicOdyssey\OpAgentsOlympus\Practice> python model_settings.py
# A fruit, round and red,
# Grows upon an apple tree,
# Sweet and crisp to bite.

# PyEpicOdyssey\OpAgentsOlympus\Practice> python model_settings.py
# A fruit, red and round,
# Grows upon an apple tree,
# Sweet and crisp to bite.

# PyEpicOdyssey\OpAgentsOlympus\Practice> python model_settings.py
# A fruit, red and round,
# Grows upon an apple tree,
# Sweet and crisp to bite.


# Temperature = 0.9
# PyEpicOdyssey\OpAgentsOlympus\Practice> python model_settings.py
# A fruit, round and red,
# Or green, a sweet, crisp delight,
# From the apple tree.

# PyEpicOdyssey\OpAgentsOlympus\Practice> python model_settings.py
# A fruit, red or green,
# Grows upon an apple tree,
# Sweet taste, good to eat.

# PyEpicOdyssey\OpAgentsOlympus\Practice> python model_settings.py
# A fruit, red and sweet,
# Grows upon an apple tree,
# A healthy snack too.

# Min/Max (0.0 - 2.0)