from agents import (
    Agent,
    Runner,
    RunConfig,
    ModelProvider,
    OpenAIChatCompletionsModel,
    AsyncOpenAI,
)
from agents.tracing import set_trace_processors
from agents.tracing.processors import BatchTraceProcessor, TracingExporter
from rich.console import Console
from rich.tree import Tree
import os
import dotenv

dotenv.load_dotenv()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

client = AsyncOpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai",
    api_key=GEMINI_API_KEY,
)


class CustomConsoleSpanExporter(TracingExporter):
    def __init__(self):
        self.console = Console()

    def export(self, items):
        for item in items:
            if (
                hasattr(item, "export")
                and item.export().get("span_data", {}).get("type", "unknown")
                == "generation"
            ):
                self._export_span(item)

    def _export_span(self, span):
        span_data = span.export()
        if not span_data:
            return

        span_details = span_data.get("span_data", {})
        span_type = span_details.get("type", "unknown")

        tree = Tree(f"[bold green]Span:[/bold green] {span_type}")

        if span_type == "generation":
            self._add_generation_data(tree, span_details)

        self.console.print(tree)

    def _add_generation_data(self, tree, data):
        if data.get("model"):
            tree.add(
                f"[yellow]🎯 ACTUAL MODEL USED:[/yellow] [bold red]{data['model']}[/bold red]"
            )


comprehensive_processor = BatchTraceProcessor(CustomConsoleSpanExporter())
set_trace_processors([comprehensive_processor])

model1 = OpenAIChatCompletionsModel("gemini-1.5-flash", client)
model2 = OpenAIChatCompletionsModel("gemini-2.0-flash", client)


class CustomProvider(ModelProvider):
    def get_model(self, model_name: str):
        if model_name == "custom-model":
            return model2
        print(f"❌ CustomProvider could not resolve: {model_name}")
        return None


agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant",
    model=model1,  # This will be overridden
)

run_config = RunConfig(
    model="custom-model",
    model_provider=CustomProvider(),
    tracing_disabled=False,  # Enable tracing so that the CustomConsoleSpanExporter be able to log in terminal
)

# This will use gemini-2.0-flash, not gemini-1.5-flash
result = Runner.run_sync(agent, "Hello", run_config=run_config)
print(f"✨ Final output: {result.final_output}")
