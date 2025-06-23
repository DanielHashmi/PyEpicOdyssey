### The Real Difference Between Strict and Non-Strict Mode

The `strict_json_schema` setting doesn't control whether errors are raised during tool execution, it controls **what schema is sent to the LLM** to guide its JSON generation.

**Strict Mode (`strict_json_schema=True`):**
- The schema sent to the LLM includes `additionalProperties: false`
- This **instructs the LLM** not to generate extra properties in the first place
- The dynamically created Pydantic model processes whatever JSON is received, extracting only the expected fields

**Non-Strict Mode (`strict_json_schema=False`):**
- The schema sent to the LLM allows additional properties
- The LLM is **more likely** to generate extra properties since the schema permits them
- The dynamically created Pydantic model processes the JSON the same way, extracting only expected fields

### Why Both Cases "Work" Without Errors

In both cases the tool execution succeeds because:

1. The JSON is valid regardless of extra properties
2. The SDK creates Pydantic models dynamically using `create_model()` with `BaseModel` as the base
3. Pydantic's default behavior with `BaseModel` is to ignore extra fields during validation
4. The function receives the expected parameters after validation

**Key Technical Detail**: The SDK relies on standard Pydantic behavior where models created with `BaseModel` ignore extra fields by default. This isn't special SDK logic, it's how Pydantic works when validating JSON input against dynamically created models.

### The Real Purpose of Strict Mode

Strict mode's value is **prevention, not error handling**. It reduces the likelihood that the LLM will generate malformed or inefficient JSON. This leads to:

- LLM doesn't waste tokens on unnecessary properties
- LLM follows the schema more precisely  
- When issues occur, they're more likely to be in your expected parameters

**Important Caveat**: Strict mode can raise `UserError` exceptions during schema creation if certain types (like mappings) cannot be made strict-compliant, but this happens at tool definition time, not during execution.

> Happy Coding ✨
