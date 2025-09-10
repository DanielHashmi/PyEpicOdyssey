from agents import AgentOutputSchema
from pydantic import BaseModel
from typing import Any


class Human(BaseModel):
    name: str
    age: int
    friends: list[str]


# Strict JSON Schema False
output_wrapper = AgentOutputSchema(output_type=Human, strict_json_schema=False)

print(output_wrapper, "\n\n")

assert (
    not output_wrapper.is_strict_json_schema()
)  # This will return False, But not will make it True again, so this will pass
assert (
    output_wrapper.json_schema() == Human.model_json_schema()
)  # Both are equal since strict_json_schema=False (No Changes)

print(output_wrapper.json_schema(), "\n\n")

print(Human.model_json_schema(), "\n\n")

print("All Tests Passed!\n\n")

# Strict JSON Schema True
output_wrapper = AgentOutputSchema(output_type=Human, strict_json_schema=True)

print(output_wrapper, "\n\n")

assert output_wrapper.is_strict_json_schema()
# assert output_wrapper.json_schema() == Human.model_json_schema() # This will fail, Because we have an extra additionalProperties key inside output_wrapper.json_schema()

print("Before", output_wrapper.json_schema(), "\n\n")
del output_wrapper.json_schema()["additionalProperties"]
print("After", output_wrapper.json_schema(), "\n\n")

assert (
    output_wrapper.json_schema() == Human.model_json_schema()
)  # Now ths will pass, Because we have deleted the additionalProperties key

print(Human.model_json_schema(), "\n\n")

print("All Tests Passed!\n\n")

# Manually forcing both to be Equal
strict_false = AgentOutputSchema(output_type=Human, strict_json_schema=False)
strict_true = AgentOutputSchema(output_type=Human, strict_json_schema=True)

print("Strict False", strict_false, "\n")
print("Strict True", strict_true, "\n")

print("Are Both Equal?", strict_false == strict_true, "\n")  # Are Both Equal? False


# Force Modifying
def __eq__(self: AgentOutputSchema, other: AgentOutputSchema | Any):
    if not isinstance(other, AgentOutputSchema):
        return False
    return (
        self.output_type == other.output_type
        and self._strict_json_schema == other._strict_json_schema
        and self._is_wrapped == other._is_wrapped
        and self._output_schema == other._output_schema
    )


AgentOutputSchema.__eq__ = __eq__  # Custom __eq__ method to check for equality

del strict_true.json_schema()["additionalProperties"]  # Delete additionalProperties
strict_true._strict_json_schema = (
    False  # Assign False to _strict_json_schema private attribute
)

print(
    "Are Both Equal Now?", strict_false == strict_true, "\n"
)  # Are Both Equal Now? True

# When strict_json_schema=True (the default), the schema is processed through ensure_strict_json_schema() to make it compliant with OpenAI's structured output requirements.
# When set to False, the schema uses the original Pydantic model schema without strict constraints.
# The AgentRunner._get_output_schema() method creates an AgentOutputSchema instance for agents with non-string output types.

# Answer
# B. Whether to use strict or non-strict JSON schemas for output validation is what AgentOutputSchema allows you to customize.
