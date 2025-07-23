from agents import Agent, Runner, input_guardrail, output_guardrail, GuardrailFunctionOutput
import asyncio
from config import config
@input_guardrail
async def slow_input_check(ctx, agent, input_data):
    await asyncio.sleep(2)  # Simulates slow guardrail
    return GuardrailFunctionOutput(output_info="Checked", tripwire_triggered=False)

@output_guardrail
async def fast_output_check(ctx, agent, output):
    return GuardrailFunctionOutput(output_info="Fast check", tripwire_triggered=False)

specialist = Agent(name="Specialist", output_guardrails=[fast_output_check])

main_agent = Agent(
    name="Main",
    input_guardrails=[slow_input_check],
    handoffs=[specialist]
)

async def main():
    result = Runner.run_streamed(main_agent, "Process this request", run_config=config)
    events = []
    async for event in result.stream_events():
        if event.type not in events:
            events.append(event.type)
    print(events)

asyncio.run(main())