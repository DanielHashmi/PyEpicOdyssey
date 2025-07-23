from agents import Agent, function_tool, WebSearchTool, ToolsToFinalOutputResult, Runner
from open_router_config import config

@function_tool
def analyzer(data: str) -> str:
    return f"Analyzed: {data}"

@function_tool
def processor(data: str) -> str:
    return f"Processed: {data}"

def selective_handler(ctx, tool_results):
    function_results = [r for r in tool_results if r.tool_name in ["analyzer", "processor"]]
    if len(function_results) >= 2:
        return ToolsToFinalOutputResult(
            is_final_output=True,
            final_output=f"Combined: {', '.join(r.output for r in function_results)}"
        )
    return ToolsToFinalOutputResult(is_final_output=False)

agent = Agent(
    name="MixedToolAgent",
    tools=[WebSearchTool(), analyzer, processor],
    tool_use_behavior=selective_handler
)

result = Runner.run_sync(agent, 'Use all tools', run_config=config)