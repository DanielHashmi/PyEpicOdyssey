import asyncio
from agents import (
    Agent,
    Runner,
    function_tool,
    input_guardrail,
    GuardrailFunctionOutput,
)


@input_guardrail
async def failing_guardrail(ctx, agent, input_data):
    if "cascade" in str(input_data).lower():
        raise ValueError("Cascading validation failure")
    return GuardrailFunctionOutput(output_info="Valid", tripwire_triggered=False)


@function_tool
async def nested_operation(query: str) -> str:
    if "nested_fail" in query:
        raise RuntimeError("Nested operation failed")
    return f"Success: {query}"


async def test_valueerror_no_context():
    agent = Agent(
        name="TestAgent",
        tools=[nested_operation],
        input_guardrails=[failing_guardrail],
        tool_use_behavior="run_llm_again",
    )

    result = Runner.run_streamed(agent, "cascade nested_fail test")

    try:
        async for event in result.stream_events():
            pass
    except Exception as e:
        exception_type = type(e).__name__
        has_run_data = hasattr(e, "run_data")
        guardrail_results = e.run_data.input_guardrail_results if has_run_data else None

        print(f"Exception: {exception_type}")
        print(f"Has run_data: {has_run_data}")
        print(f"Guardrail results: {guardrail_results}")

        # This validates our expectation: ValueError with no context
        assert exception_type == "ValueError"
        assert not has_run_data
        assert guardrail_results is None

        return exception_type, has_run_data, guardrail_results


# Run the test
if __name__ == "__main__":
    result = asyncio.run(test_valueerror_no_context())
    print(f"Result: {result}")  # Expected: ('ValueError', False, None)
