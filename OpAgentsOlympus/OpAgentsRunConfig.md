# **Everything you need to know about RunConfig!**

## What is RunConfig?

`RunConfig` is a dataclass that holds all the global settings for an entire agent run. When you start a workflow with `Runner.run()`, `Runner.run_sync()`, or `Runner.run_streamed()`, you can pass a `RunConfig` to override default behaviors and apply consistent settings across all agents in your workflow.

## Core Configuration Options

### 🤖 Model Configuration
- **`model`**: Override which AI model to use for ALL agents in the run
  - Can be a string like `"gpt-4"` or a `Model` object
  - If set, this completely overrides each agent's individual model setting
- **`model_provider`**: The service that resolves model names (defaults to `MultiProvider`)
- **`model_settings`**: Global model parameters (temperature, max tokens, etc.) that override agent-specific settings

### 🛡️ Guardrails Configuration  
- **`input_guardrails`**: Safety checks that run on the very first input to your workflow
- **`output_guardrails`**: Safety checks that run on the final output before returning results
- These get combined with any guardrails already defined on individual agents

### 🔄 Handoff Configuration
- **`handoff_input_filter`**: A function that can modify inputs when agents hand off to each other
- This applies globally unless a specific handoff has its own filter defined

### 📊 Tracing Configuration
Tracing helps you monitor and debug your agent workflows:
- **`tracing_disabled`**: Turn off all tracing for this run
- **`trace_include_sensitive_data`**: Whether to include actual inputs/outputs in traces (vs just metadata)
- **`workflow_name`**: A human-readable name for this workflow (like "Customer Support Bot")
- **`trace_id`**: Custom ID for this specific run (auto-generated if not provided)
- **`group_id`**: Links multiple runs together (like all runs in the same chat conversation)
- **`trace_metadata`**: Extra information to attach to the trace

## How to Use RunConfig

### Basic Example
```python
from agents import Runner, RunConfig

# Create your configuration
config = RunConfig(
    model="gpt-4",  # Use GPT-4 for all agents
    workflow_name="Email Assistant",
    tracing_disabled=False  # Keep tracing on
)

# Run your agent with the config
result = await Runner.run(
    my_agent,
    "Help me write an email",
    run_config=config
)
```

### Advanced Example
```python
config = RunConfig(
    model="gpt-4o",
    model_settings=ModelSettings(temperature=0.1),
    input_guardrails=[safety_checker, content_filter],
    output_guardrails=[quality_checker],
    workflow_name="Content Generation Pipeline",
    group_id="user_session_123",
    trace_metadata={"user_id": "user_456", "version": "v2.1"}
)
```

## How Model Selection Works

The system picks which model to use in this priority order:
1. `RunConfig.model` (if it's a Model object) ← **Highest priority**
2. `RunConfig.model` (if it's a string, resolved through `model_provider`)
3. `Agent.model` (if it's a Model object)  
4. `Agent.model` (if it's a string, resolved through `model_provider`) ← **Lowest priority**

This means `RunConfig` always wins over individual agent settings!

## What Happens Behind the Scenes

When you pass a `RunConfig` to `Runner.run()`:

1. **Initialization**: If you don't provide one, it creates `RunConfig()` with defaults
2. **Tracing Setup**: Your tracing settings are applied using `TraceCtxManager`
3. **Model Resolution**: Each time an agent needs to run, the system uses `_get_model()` to pick the right model based on your config
4. **Guardrails Merging**: Your global guardrails get combined with each agent's individual guardrails
5. **Execution**: All agents in the workflow use these consistent settings

## Key Benefits

- **Consistency**: All agents in your workflow use the same model and settings
- **Runtime Flexibility**: Change behavior without modifying agent code
- **Environment Control**: Different configs for development, testing, and production
- **Monitoring**: Comprehensive tracing and debugging capabilities
- **Safety**: Global guardrails ensure all agents follow the same safety rules

## Important Notes

- If you don't provide a `RunConfig`, the system creates one with sensible defaults
- Global settings in `RunConfig` always override individual agent settings
- Only the first agent's input guardrails run, but they're combined with global ones
- Output guardrails run on the final result, combining agent-specific and global ones
- Tracing can be completely disabled for privacy-sensitive applications

If this really helped you please give a ⭐
