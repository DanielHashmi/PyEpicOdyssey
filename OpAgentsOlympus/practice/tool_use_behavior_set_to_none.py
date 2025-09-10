from agents import Agent, Runner
from config import config

def main():
    agent = Agent(
        name="assistant",
        instructions="You are a helpful assistant.",
        tool_use_behavior=None # TypeError: Agent tool_use_behavior must be 'run_llm_again', 'stop_on_first_tool', StopAtTools dict, or callable, got NoneType
    )
    result = Runner.run_sync(
        agent, input='hello', run_config=config
    )
    print(result.final_output)

if __name__ == "__main__":
    main()
