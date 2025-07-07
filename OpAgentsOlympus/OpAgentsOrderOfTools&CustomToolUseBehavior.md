When you pass a function to `tool_use_behavior`, **tools are called first**, and then your function is called with the tool results to determine if execution should stop or continue.

The execution flow works as follows:

1. **Tools execute first**: All function tools are executed in parallel using `asyncio.gather()`

2. **Your function is called with results**: After tools complete, the system calls `_check_for_final_output_from_tools()` which evaluates your custom function, passing it the `RunContextWrapper` and list of `FunctionToolResult` objects

3. **Decision based on your function's return**: Your function returns a `ToolsToFinalOutputResult` that determines whether to stop execution (using tool output as final result) or continue the conversation loop

## Notes

This behavior is specific to `FunctionTool` objects. Hosted tools (like file search, web search) are always processed by the LLM regardless of the `tool_use_behavior` setting.
