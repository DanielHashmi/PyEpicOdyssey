from agents import Agent, Runner, AgentOutputSchemaBase
from pydantic import BaseModel
from typing import Any
from config import config

class UserContext(BaseModel):
    name: str
    age: int
    is_alive: bool

class CustomOutputSchema(AgentOutputSchemaBase):

    def is_plain_text(self) -> bool:
        return False

    def name(self) -> str:
        return "UserContext"

    def json_schema(self):
        return UserContext.model_json_schema()

    def is_strict_json_schema(self) -> bool:
        return True

    def validate_json(self, json_str: str) -> Any:
        return UserContext.model_validate_json(json_str)


assistant = Agent(
    name="assistant",
    instructions="You are a helpful assistant.",
    output_type=CustomOutputSchema # Pass an instance, not the class itself!
)

result = Runner.run_sync(
    starting_agent=assistant,
    input="Hello!",
    run_config=config
)

print(result.final_output)
