from open_router_config import config
from agents import Agent, Runner, function_tool, ModelSettings, RunContextWrapper, StopAtTools

@function_tool
def say_hello() -> int:
    return 'Hello, Guys!'

@function_tool
def say_bye(ctx: RunContextWrapper) -> int:
    return 'Bye, Guys!'

def main():
    assistant = Agent(
        name="assistant",
        instructions='You are a helpful assistant.',
        model_settings=ModelSettings(
            tool_choice='say_bye',
            parallel_tool_calls=False,
        ),
        reset_tool_choice=False,
        tool_use_behavior=StopAtTools(stop_at_tool_names=['say_hello']),
        tools=[say_hello, say_bye]
    )
    result = Runner.run_sync(
        assistant, input='say bye first then hello', run_config=config
    )
    print(result.final_output)

if __name__ == "__main__":
    main()


# <-- Another Example -->
# assistant = Agent(
#     name="assistant",
#     instructions='You are a helpful assistant.',
#     model_settings=ModelSettings(
#         parallel_tool_calls=True,
#     ),
#     tool_use_behavior='stop_on_first_tool',
#     tools=[say_hello, say_bye]
# )
# result = Runner.run_sync(
#     assistant, input='say bye first then hello', run_config=config
# )

# Question: Why the result of say_bye will be the final_output?