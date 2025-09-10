from agents import Agent, InputGuardrail, OutputGuardrail, GuardrailFunctionOutput, Runner  
import asyncio  
from open_router_config import config

async def agent_input_guardrail(ctx, agent, input_data):  
    print("Agent input guardrail...")  
    return GuardrailFunctionOutput(  
        output_info="agent_input_guardrail",  
        tripwire_triggered=False,
    )  
  
async def agent_output_guardrail(ctx, agent, output):  
    print("Agent output guardrail...")  
    return GuardrailFunctionOutput(  
        output_info='agent_output_guardrail',  
        tripwire_triggered=False,  
    )  
    
async def runner_input_guardrail(ctx, agent, input_data):  
    print("Runner input guardrail...")  
    return GuardrailFunctionOutput(  
        output_info="runner_input_guardrail",  
        tripwire_triggered=False,  
    )  
  
async def runner_output_guardrail(ctx, agent, output):  
    print("Runner output guardrail...")  
    return GuardrailFunctionOutput(  
        output_info="runner_output_guardrail",  
        tripwire_triggered=False,  
    )  
  
math_agent = Agent(  
    name="Math Tutor",  
    instructions="Help with math problems. Provide step-by-step solutions.",  
    input_guardrails=[InputGuardrail(guardrail_function=agent_input_guardrail)],  
    output_guardrails=[OutputGuardrail(guardrail_function=agent_output_guardrail)],  
)  
  
history_agent = Agent(  
    name="History Tutor",   
    instructions="Help with history questions. Provide detailed historical context.",  
)  
  
triage_agent = Agent(  
    name="Triage Agent",  
    instructions="Determine which specialist agent to use based on the question.",  
    handoffs=[math_agent, history_agent],  
    input_guardrails=[InputGuardrail(guardrail_function=agent_input_guardrail)],  
    output_guardrails=[OutputGuardrail(guardrail_function=agent_output_guardrail)], 
)  
  
async def main():  
    config.input_guardrails=[InputGuardrail(guardrail_function=runner_input_guardrail)]
    config.output_guardrails=[OutputGuardrail(guardrail_function=runner_output_guardrail)]
    await Runner.run(  
        triage_agent,   
        "What is 2 + 2? Please explain step by step.",  
        run_config=config  
    )  

if __name__ == "__main__":  
    asyncio.run(main())
    
    
# <== Output ==>
# Agent input guardrail...
# Runner input guardrail...
# Agent output guardrail...
# Runner output guardrail...