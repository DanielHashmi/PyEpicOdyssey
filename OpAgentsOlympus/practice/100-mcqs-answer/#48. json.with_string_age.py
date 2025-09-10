     from agents import Agent, AgentOutputSchema
     from typing import Dict, Any

     class UserProfile(BaseModel):
          name: str
          age: int
          active: bool = True

     agent = Agent(
          name="ProfileAgent",
          instructions="Return user profile data",
          output_type=AgentOutputSchema(UserProfile, strict_json_schema=False)
     )
