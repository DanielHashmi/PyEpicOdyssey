# Everything you need to know about Tools In OpenAI Agents SDK

## Tool System Architecture

The SDK supports three primary tool types:

**Hosted Tools** run on OpenAI's servers alongside AI models, including `WebSearchTool`, `FileSearchTool`, `ComputerTool`, `CodeInterpreterTool`, and others.

**Function Tools** allow any Python function to become an agent tool through automatic schema generation.

**Agent as Tools** enable agents to orchestrate other agents without handoff using the `agent.as_tool()` method.

## Function Schema Core Components

### FuncSchema Dataclass

The `FuncSchema` class captures all metadata required to represent a Python function as an LLM tool:

Key fields include the function name, description extracted from docstrings, a dynamically generated Pydantic model for parameters, the resulting JSON schema, and metadata about context parameter usage. 

The `to_call_args()` method converts validated Pydantic data back into Python function arguments, handling, `*args`, and `**kwargs` parameters appropriately.

### Documentation Extraction

The `FuncDocumentation` class extracts metadata from function docstrings using the `griffe` library:

The system supports multiple docstring styles with automatic detection, including Google (`Args:`, `Returns:`), Sphinx (`:param`, `:type`, `:return:`), and NumPy (`Parameters\n-------`) formats

## The @function_tool Decorator

The `@function_tool` decorator automatically converts Python functions into `FunctionTool` instances through a multi-step process: 

```python
@function_tool
async def fetch_weather(location: Location) -> str:
    """Fetch the weather for a given location.
    
    Args:
        location: The location to fetch the weather for.
    """
    return "sunny"
``` 

The decorator extracts function signatures using Python's `inspect` module, parses docstrings with `griffe`, and creates Pydantic models for schema generation. 

### Context Parameter Support

Functions can optionally accept context as their first parameter, which is automatically detected and excluded from the JSON schema: 

```python
@function_tool
def read_file(ctx: RunContextWrapper[Any], path: str) -> str:
    """Read file contents with access to run context."""
    return "<file contents>"
``` 

## Schema Generation Process

The `function_schema()` function performs comprehensive analysis of Python functions: 

1. **Docstring Analysis**: Extracts descriptions and parameter documentation using `generate_func_documentation()` 

2. **Signature Inspection**: Uses `inspect.signature()` and `get_type_hints()` to analyze function parameters 

3. **Context Detection**: Identifies `RunContextWrapper` or `ToolContext` parameters 

4. **Dynamic Model Creation**: Builds Pydantic models using `create_model()` with proper field definitions 

5. **JSON Schema Generation**: Creates strict JSON schemas with `"additionalProperties": false` by default 

### Parameter Type Handling

The system handles various parameter types including `VAR_POSITIONAL` (*args) and `VAR_KEYWORD` (**kwargs): 

For `*args`, it converts tuple type hints to list types and provides empty list defaults.

For `**kwargs`, it handles dictionary type hints and provides empty dictionary defaults.

## Tool Invocation and Error Handling

The `FunctionTool` class wraps the generated schema and provides invocation logic: 

During invocation, the system parses JSON input, validates it against the Pydantic model, converts to function arguments, and executes the function: 

Error handling is managed through configurable error functions, with `default_tool_error_function` providing standard error message formatting for LLMs: 

## Manual Tool Creation

For advanced use cases, you can create `FunctionTool` instances manually by providing the name, description, JSON schema, and invocation handler: 

```python
tool = FunctionTool(
    name="process_user",
    description="Processes extracted user data",
    params_json_schema=FunctionArgs.model_json_schema(),
    on_invoke_tool=run_function,
)
``` 

## Notes

The function schema system uses strict JSON schemas by default to improve LLM compliance, automatically detects docstring formats, and supports complex parameter patterns including variadic arguments. The schema generation code lives in `src/OpAgentsOlympus/function_schema.py` and integrates with the broader tool system through the `@function_tool` decorator and `FunctionTool` class. 

To Learn More About Strict Mode:

[The Real Difference Between Strict and Non-Strict Mode](https://github.com/DanielHashmi/PyEpicOdyssey/blob/main/OpAgentsOlympus/OpAgentsStrictMode.md)

[None-Strict Mode Behavior (Code Example)](https://github.com/DanielHashmi/PyEpicOdyssey/blob/main/OpAgentsOlympus/OpAgentsTrickStrict.py)
