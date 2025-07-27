import asyncio
from agents import Agent, Runner, input_guardrail, GuardrailFunctionOutput, TResponseInputItem
from config import config
from pydantic import BaseModel

class UserData(BaseModel):
    name: str
    height: float

@input_guardrail
async def input_guardrail(context, agent: Agent, input: str | list[TResponseInputItem]) -> GuardrailFunctionOutput: # Context is accessible without RunContextWrapper
    print(f"Input Guardrail of agent {agent.name} started with context: {context.context}")
    return GuardrailFunctionOutput(
        output_info='Worked!',
        tripwire_triggered=False
    )

async def main():  
    agent = Agent(  
        name="Super Assistant",  
        instructions="You are a helpful assistant.",
        input_guardrails=[input_guardrail]
    )
    
    userdata = UserData(name='Daniel', height=5.11)
  
    result = await Runner.run(agent, input="how are you?", context=userdata, run_config=config)  
    print(result.final_output)
  
if __name__ == "__main__":  
    asyncio.run(main())