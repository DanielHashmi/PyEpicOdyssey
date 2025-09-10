**Only LLM consume tokens**, the token consumption includes various components that are part of those LLM requests and responses. 

**1. Input Tokens Include Tool Schemas**
When tools are provided to an agent, their schemas are sent as part of the input tokens to the model.

The `Converter.convert_tools()` method processes tool definitions into the format expected by the API, and these tool schemas consume input tokens.

**2. Output Tokens Include Function Call Arguments**
When the model decides to call a tool, the function call arguments are generated as output tokens.

The usage tracking captures both `completion_tokens` (output) and `prompt_tokens` (input) from the model response.

**3. Usage Tracking Captures All Components**
The SDK's `Usage` class tracks comprehensive token consumption including input tokens (system instructions, conversation history, tool schemas), output tokens (responses, function calls), reasoning tokens, and cached tokens. 

This pattern is consistent across all model implementations:
- **OpenAI Responses API**: 
- **OpenAI Chat Completions**: 
- **LiteLLM**: 

Token consumption is fundamentally tied to LLM Requests and Responses, but those include more than just the user's message, they encompass tool schemas, system instructions, conversation history, and generated function calls. The SDK provides comprehensive tracking of all these token-consuming components through the `Usage` class.
