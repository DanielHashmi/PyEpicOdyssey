from config import config
from agents import Agent, Runner, function_tool, ModelSettings, RunContextWrapper


@function_tool
def say_hello() -> int:
    return 'Hello, Guys!'

@function_tool
def say_bye(ctx: RunContextWrapper) -> int:
    return 'Bye, Guys!'

def main():
    assistant = Agent(
        name="assistant",
        instructions='123',
        model_settings=ModelSettings(
            tool_choice='say_bye'
        ),
        tools=[say_bye, say_hello]
    )
    result = Runner.run_sync(
        assistant, input='hello', run_config=config
    )
    print(result.final_output)

if __name__ == "__main__":
    main()
