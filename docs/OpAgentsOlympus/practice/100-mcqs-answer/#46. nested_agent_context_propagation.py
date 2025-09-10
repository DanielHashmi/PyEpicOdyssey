     from agents import Agent, function_tool, Runner

     @function_tool
     def get_user_data(ctx, user_id: str) -> str:
          # Access context from parent agent
          return f"User {user_id} data from {ctx.context.database_name}"

     class DatabaseContext:
          def __init__(self, db_name: str):
                self.database_name = db_name

     inner_agent = Agent(
          name="DataAgent",
          tools=[get_user_data],
          instructions="Fetch user data from the database"
     )

     outer_agent = Agent(
          name="MainAgent",
          tools=[inner_agent.as_tool(tool_name="fetch_user_data")],
          instructions="Use the data agent to get user information"
     )

     context = DatabaseContext("production_db")
     result = await Runner.run(outer_agent, "Get data for user 123", context=context)