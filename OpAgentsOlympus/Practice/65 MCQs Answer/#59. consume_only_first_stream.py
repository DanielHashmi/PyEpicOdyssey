from agents import Agent, Runner, input_guardrail, GuardrailFunctionOutput
from open_router_config import config
import asyncio

@input_guardrail
async def async_validation(ctx, agent, input_data):
    await asyncio.sleep(1)  # Simulates async validation
    return GuardrailFunctionOutput(output_info="Validated", tripwire_triggered=False)

agent = Agent(name="Validator", input_guardrails=[async_validation])

async def test_streaming():
    result = Runner.run_streamed(agent, "Test input", run_config=config)

    # Consume only the first event
    first_event = await result.stream_events().__anext__()

    # Check completion status immediately
    print(result.is_complete, first_event.type)
    
    # Check completion regardless of consuming events
    # while True:
    #     # print('Ongoing')
    #     if result.is_complete:
    #         print('Finished')
    #         break
    #     await asyncio.sleep(0.1)
    
asyncio.run(test_streaming())