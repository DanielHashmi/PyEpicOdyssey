from agents import FunctionTool, RunContextWrapper, Agent, Runner, function_tool
from pydantic import BaseModel
from typing import Any
from config import config

def custom_error_handler(ctx: RunContextWrapper[Any], error: Exception) -> str:
    print("Error occurred")
    return f"Error: Tool failed with {error.__class__.__name__}: {str(error)}"

@function_tool(failure_error_function=custom_error_handler)
def multiply_by_2(x: int) -> int:
    raise ValueError()
    print(f"Multiplying {x} by 2")
    return x * 2

assistant = Agent(
    name='assistant',
    instructions='You are a friendly assistant.',
    tools=[multiply_by_2]
)

result = Runner.run_sync(assistant, "multiply 4 with 2", run_config=config)
print(result.final_output)