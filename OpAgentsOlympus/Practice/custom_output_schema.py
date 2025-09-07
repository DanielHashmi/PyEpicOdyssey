from agents import Agent, Runner, AgentOutputSchemaBase
from pydantic import BaseModel
from typing import Any
from config import config

class UserProfile(BaseModel):
    name: str
    age: int
    occupation: str
    interests: list[str]

class UserProfileOutputSchema(AgentOutputSchemaBase):
    def is_plain_text(self) -> bool:
        return False

    def name(self) -> str:
        return "UserProfile"

    def json_schema(self):
        return UserProfile.model_json_schema()

    def is_strict_json_schema(self) -> bool:
        return True

    def validate_json(self, json_str: str) -> Any:
        # Custom validation logic - you could add business rules here
        profile = UserProfile.model_validate_json(json_str)

        # Example: Ensure age is reasonable
        if profile.age < 0 or profile.age > 150:
            raise ValueError("Age must be between 0 and 150")

        return profile

profile_extractor = Agent(
    name="profile_extractor",
    instructions="""
    Extract user profile information from the given text.
    Always include name, age, occupation, and interests as a list.
    """,
    output_type=UserProfileOutputSchema()  # Pass an instance, not the class itself!
)

result = Runner.run_sync(
    starting_agent=profile_extractor,
    input="Hi, I'm Sarah, 28 years old. I work as a software engineer and love hiking, reading, and cooking.",
    run_config=config
)

# The result will be a validated UserProfile object
user_profile = result.final_output
print(f"Name: {user_profile.name}")
print(f"Age: {user_profile.age}")
print(f"Interests: {', '.join(user_profile.interests)}")
