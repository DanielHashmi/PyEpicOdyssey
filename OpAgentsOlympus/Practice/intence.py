from agents import Agent, Runner
from config import config

def main():
    agent = Agent(
        name="Joker",
        instructions="You are a helpful assistant.",
    )
    result = Runner.run_sync(
        agent, input='hello', run_config=config
    )
    print(result.final_output)

if __name__ == "__main__":
    main()
