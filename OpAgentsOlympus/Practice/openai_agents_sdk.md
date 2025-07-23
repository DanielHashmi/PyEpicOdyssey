# OpenAI Agents SDK Cheat Sheet

## 1. Introduction to OpenAI Agents SDK

### What is the OpenAI Agents SDK?
The OpenAI Agents SDK is an open-source Python library designed to simplify the development of agentic applications powered by OpenAI's LLMs. It offers a modular, composable set of tools and primitives to create deterministic flows, iterative loops, and multi-agent systems with minimal abstractions.

### Key Features and Benefits
- **Lightweight**: Minimal overhead for rapid development.
- **Flexible**: Supports custom workflows, tools, and agent handoffs.
- **Powerful**: Leverages OpenAI's state-of-the-art LLMs.
- **Structured Outputs**: Integrates with Pydantic for typed responses.
- **Metrics Tracking**: Built-in usage monitoring for optimization.

---

## 2. Core Components

### Agents
Agents are the central entities in the SDK, representing an LLM configured with:
- **Name**: A unique identifier.
- **Instructions**: A string defining the agent's behavior and purpose.
- **Model**: The underlying LLM (e.g., `gpt-4o`, `gpt-3.5-turbo`).
- **Tools**: Functions or services the agent can utilize.

### Tools
Tools extend agent capabilities by allowing them to interact with external systems or perform specific tasks:
- **Custom Tools**: Defined using the `@function_tool` decorator.
- **Hosted Tools**: Pre-built tools like `FileSearchTool`, `WebSearchTool`, and `ComputerTool`.

### Runners
Runners manage the execution of agents, handling input processing and output generation:
- **Asynchronous**: For non-blocking execution.
- **Synchronous**: For simpler, blocking workflows.
- **Streaming**: For real-time event handling.

### Guardrails
Guardrails ensure data integrity and enforce constraints:
- Defined with the `@guardrail` decorator.
- Validate inputs and outputs (e.g., length, format, content).

### Handoffs
Handoffs enable multi-agent collaboration by allowing one agent to delegate tasks to another, creating complex workflows.

---

## 3. Setting Up the SDK

### Prerequisites
- Python 3.8+
- OpenAI API key (available from [platform.openai.com](https://platform.openai.com))

### Installation
Install the SDK via pip:

```bash
pip install openai-agents
```

### Configuration
Set your API key in the environment:

```python
import os
os.environ["OPENAI_API_KEY"] = "sk-your-api-key-here"
```

Optionally, configure a custom API base URL:

```python
os.environ["OPENAI_API_BASE"] = "https://api.openai.com/v1"
```

---

## 4. Building Agents

### Defining an Agent
Create an agent with a name, instructions, model, and optional tools:

```python
from agents import Agent

agent = Agent(
    name="CustomerSupportAgent",
    instructions="You are a polite and knowledgeable support assistant.",
    model="gpt-4o",
    tools=[],
)
```

### Configuring Instructions
Instructions should be clear and specific to shape the agent's behavior:

```python
instructions = """
You are an expert in Python programming.
Provide concise, accurate answers and include code examples when possible.
"""
agent = Agent(name="PythonExpert", instructions=instructions, model="gpt-4o")
```

### Selecting Models
Supported models include:
- `gpt-4o`: Latest high-performance model.
- `gpt-3.5-turbo`: Cost-effective and fast.
- Custom fine-tuned models (if available).

### Adding Tools
Attach tools to an agent for enhanced functionality:

```python
agent = Agent(
    name="MathAgent",
    instructions="Solve math problems.",
    model="gpt-4o",
    tools=[add_numbers],  # Defined below
)
```

---

## 5. Tools and Decorators

### @function_tool
Convert a Python function into an agent-callable tool:

```python
from agents import function_tool

@function_tool
def multiply(a: int, b: int) -> int:
    """Multiplies two integers."""
    return a * b
```

- Automatically generates a JSON schema for parameters.
- Supports type hints for validation.

### @guardrail
Define validation logic for inputs or outputs:

```python
from agents import guardrail

@guardrail
def restrict_length(text: str) -> bool:
    """Ensures text is between 1 and 100 characters."""
    return 1 <= len(text) <= 100
```

- Returns `True` if valid, `False` otherwise.
- Can be applied to tools or standalone.

### Hosted Tools
Pre-built tools provided by the SDK:
- **`FileSearchTool`**: Search within files.
- **`WebSearchTool`**: Query the web.
- **`ComputerTool`**: Execute OS-level commands.

Example usage:

```python
from agents.tools import WebSearchTool

agent = Agent(
    name="ResearchAgent",
    instructions="Find information online.",
    model="gpt-4o",
    tools=[WebSearchTool()],
)
```

---

## 6. Running Agents

### Asynchronous Execution
Run an agent asynchronously for non-blocking workflows:

```python
from agents import Runner

async def run_agent():
    result = await Runner.run(agent, "What is the weather today?")
    print(result.final_output)

import asyncio
asyncio.run(run_agent())
```

### Synchronous Execution
Run an agent synchronously for simpler use cases:

```python
result = Runner.run_sync(agent, "Calculate 5 + 3")
print(result.final_output)  # Output: 8
```

### Streaming Results
Stream agent responses in real-time:

```python
async def stream_agent():
    async for event in Runner.run_streamed(agent, "Tell me a story"):
        print(event.content, end="")

asyncio.run(stream_agent())
```

- Events include intermediate outputs, tool calls, and final results.

---

## 7. Multi-Agent Workflows

### Handoffs
Delegate tasks between agents:

```python
research_agent = Agent(name="Researcher", instructions="Gather data.")
writer_agent = Agent(name="Writer", instructions="Write summaries.")
router = Agent(
    name="Coordinator",
    instructions="Route tasks to the right agent.",
    handoffs=[research_agent, writer_agent],
)

result = Runner.run_sync(router, "Research and summarize AI trends.")
print(result.final_output)
```

### Agents as Tools
Use an agent as a callable tool:

```python
@function_tool
def consult_expert(input: str) -> str:
    expert = Agent(name="Expert", instructions="Provide detailed answers.")
    return Runner.run_sync(expert, input).final_output

main_agent = Agent(
    name="MainAgent",
    instructions="Use the expert when needed.",
    tools=[consult_expert],
)
```

---

## 8. Structured Outputs

### Using Pydantic Models
Define structured responses with Pydantic:

```python
from pydantic import BaseModel

class MathResult(BaseModel):
    result: int
    steps: str

agent = Agent(
    name="MathSolver",
    instructions="Solve math problems and explain steps.",
    model="gpt-4o",
    output_type=MathResult,
)

result = Runner.run_sync(agent, "What is 7 * 8?")
print(result.final_output.result)  # 56
print(result.final_output.steps)   # Explanation
```

- Ensures type safety and consistent output formats.

---

## 9. Usage Metrics

### Tracking Requests and Tokens
Monitor API usage via the `RunResult` object:

```python
result = Runner.run_sync(agent, "Hello, world!")
print(f"Requests: {result.usage.requests}")
print(f"Input Tokens: {result.usage.input_tokens}")
print(f"Output Tokens: {result.usage.output_tokens}")
```

- Useful for cost estimation and performance optimization.

---

## 10. Advanced Features

### Customizing Agent Behavior
Adjust agent settings:
- **Temperature**: Controls randomness (0.0–2.0, default 1.0).
- **Max Tokens**: Limits response length.

```python
agent = Agent(
    name="CreativeAgent",
    instructions="Write creative stories.",
    model="gpt-4o",
    temperature=1.5,
    max_tokens=500,
)
```

### Error Handling
Handle exceptions gracefully:

```python
try:
    result = Runner.run_sync(agent, "Invalid input")
except Exception as e:
    print(f"Error: {e}")
```

### Debugging
Enable debug mode for detailed logs:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
result = Runner.run_sync(agent, "Test run")
```

---

## 11. Best Practices

- **Clear Instructions**: Use precise language to define agent roles.
- **Modular Design**: Create reusable tools and agents.
- **Validation**: Apply guardrails to enforce constraints.
- **Optimization**: Monitor usage metrics to reduce costs.
- **Testing**: Simulate edge cases to ensure robustness.
- **Version Control**: Track changes to agent configurations.

---

## 12. Additional Resources

- **[Official Documentation](https://openai.github.io/openai-agents-python/)**: Full SDK reference.
- **[OpenAI Platform Docs](https://platform.openai.com/docs)**: API details and model info.
- **[Building Agents Guide](https://cdn.openai.com/guides/building-agents)**: Step-by-step tutorials.
- **[GitHub Repository](https://github.com/openai/openai-agents-python)**: Source code and issues.
- **[YouTube Tutorials](https://www.youtube.com/playlist?list=PL1234567890)**: Video guides.

---

Happy coding Guys!
