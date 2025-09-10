from agents import (
    Agent,
    Runner,
    function_tool,
    StopAtTools,
)
import asyncio
from local_config import config

@function_tool(is_enabled=lambda ctx, agent: True if ctx.context['role'] == 'admin' else False)
def delete_user(user_id: str) -> str:
    """Deletes a user. This is a final action."""
    return f"User {user_id} has been deleted."

admin_agent = Agent(
    name="Admin Agent",
    instructions="Help manage users. First get data, then delete if asked.",
    tools=[delete_user],
    tool_use_behavior=StopAtTools(stop_at_tool_names=["delete_user"]),
)

async def main():
    print("--- Running as a regular user ---")
    result_user = await Runner.run(
        admin_agent, "Please delete user user123.",
        context={"role": "user"},
        run_config=config
    )
    print(f"Final Output: {result_user.final_output}")

    print("\n--- Running as an admin ---")
    result_admin = await Runner.run(
        admin_agent,
        "Please delete user user123.",
        context={"role": "admin"},
        run_config=config
    )
    print(f"Final Output: {result_admin.final_output}")

asyncio.run(main())