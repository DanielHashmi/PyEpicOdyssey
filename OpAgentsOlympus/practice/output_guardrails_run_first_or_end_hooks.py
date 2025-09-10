from typing import Any  
from agents import (  
    Agent,   
    Runner,   
    RunContextWrapper,   
    OutputGuardrail,   
    GuardrailFunctionOutput,  
    AgentHooks,  
    RunHooks  
)  
from config import config
import asyncio

execution_order = []  
  
class TestHooks(AgentHooks[Any]):  
    async def on_end(self, context: RunContextWrapper[Any], agent: Agent[Any], final_output: Any):  
        execution_order.append("on_end_hook")  
  
class TestRunHooks(RunHooks[Any]):  
    async def on_agent_end(self, context: RunContextWrapper[Any], agent: Agent[Any], final_output: Any):  
        execution_order.append("on_agent_end_hook")  
  
def output_guardrail(context: RunContextWrapper[Any], agent: Agent[Any], agent_output: Any) -> GuardrailFunctionOutput:  
    execution_order.append("output_guardrail")  
    return GuardrailFunctionOutput(  
        output_info="validated",  
        tripwire_triggered=False  
    )  

async def main():  
    global execution_order  
    execution_order = []
    
    agent = Agent(  
        name="test_agent",  
        instructions="You are a test agent",  
        hooks=TestHooks(),  
        output_guardrails=[OutputGuardrail(guardrail_function=output_guardrail)]  
    )  
    
    run_hooks = TestRunHooks()  

    await Runner.run(  
        agent,  
        "Hello, please respond with a simple message",  
        hooks=run_hooks,
        run_config=config
    ) 
    print(execution_order) # ['on_agent_end_hook', 'on_end_hook', 'output_guardrail']
    
asyncio.run(main())