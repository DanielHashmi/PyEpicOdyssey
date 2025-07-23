from agents import Agent, Runner, RunConfig, ModelProvider, OpenAIChatCompletionsModel, AsyncOpenAI, set_tracing_disabled
from open_router_config import model
import os
import dotenv

dotenv.load_dotenv()
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
set_tracing_disabled(True)

client = AsyncOpenAI(
    base_url='https://generativelanguage.googleapis.com/v1beta/openai',
    api_key=GEMINI_API_KEY
)

model1 = OpenAIChatCompletionsModel('gemini-1.5-flash', client)
model2 = OpenAIChatCompletionsModel('gemini-2.0-flash', client)

class CustomProvider(ModelProvider):
    def get_model(self, model_name: str):
        if model_name == "custom-model":
            print('Using (Gemini-2.0-Flash)')
            return model2
        return None

agent = Agent(
    name="Test",
    instructions="You are a helpful assistant",
    model=model1 # This will be overridden
)

run_config = RunConfig(
    model='custom-model',
    model_provider=CustomProvider()
)

# This will use gemini-2.0-flash, not gemini-1.5-flash
result = Runner.run_sync(agent, "Hello", run_config=run_config)
