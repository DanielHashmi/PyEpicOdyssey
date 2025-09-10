from agents import AsyncOpenAI, OpenAIChatCompletionsModel
from agents.run import RunConfig

external_client = AsyncOpenAI(
    api_key='1234',
    base_url="http://localhost:8000/v1",
)
model = OpenAIChatCompletionsModel(
    model="gemma-3b", openai_client=external_client
)
config = RunConfig(model=model, model_provider=external_client, tracing_disabled=True)

# This configuration is for ollama!