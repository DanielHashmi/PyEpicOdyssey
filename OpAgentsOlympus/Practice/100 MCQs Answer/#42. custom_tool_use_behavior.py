from agents import Agent, ModelSettings, function_tool, ToolsToFinalOutputResult, Runner
from open_router_config import config


@function_tool
def fetch_data(query: str) -> str:
    return f"Data for {query}"


@function_tool
def process_data(data: str) -> str:
    return f"Processed: {data}"


def custom_tool_handler(ctx, tool_results):
    print(len(tool_results))  # Output: 2

    if len(tool_results) > 1:
        return ToolsToFinalOutputResult(
            is_final_output=True,
            final_output=tool_results[-1].output,  # return only the last tool's result
        )
    return ToolsToFinalOutputResult(is_final_output=False)


agent = Agent(
    name="DataProcessor",
    tools=[fetch_data, process_data],
    model_settings=ModelSettings(tool_choice="required"),
    tool_use_behavior=custom_tool_handler,  # custom tool use behavior
    reset_tool_choice=False,
)

result = Runner.run_sync(agent, "call all tools", run_config=config)


print(result.final_output)
