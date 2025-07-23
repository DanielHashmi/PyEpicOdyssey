from agents import Agent, Runner, function_tool

@function_tool
def delegate_work(task: str) -> str:
    # This tool internally uses another agent
    specialist = Agent(name="Specialist", instructions="Handle specialized tasks")
    result = Runner.run_sync(specialist, f"Process: {task}")
    return result.final_output

main_agent = Agent(
    name="MainAgent",
    tools=[delegate_work],
    tool_use_behavior="run_llm_again"
)

result = await Runner.run(main_agent, "Complete complex task", max_turns=3)