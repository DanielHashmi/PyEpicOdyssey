from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Literal
from rich.markdown import Markdown
from rich.console import Console
from agents import Agent, ItemHelpers, Runner, TResponseInputItem
from config import config

"""
This example shows the LLM as a judge pattern. The first agent generates an outline for a story.
The second agent judges the outline and provides feedback. We loop until the judge is satisfied
with the outline.
"""

console = Console()

story_outline_generator = Agent(
    name="story_outline_generator",
    instructions=(
        "You generate a very short story outline based on the user's input."
        "If there is any feedback provided, use it to improve the outline."
    ),
)


@dataclass
class EvaluationFeedback:
    feedback: str
    score: Literal["pass", "needs_improvement", "fail"]


evaluator = Agent[None](
    name="evaluator",
    instructions=(
        "You evaluate a story outline and decide if it's good enough."
        "If it's not good enough, you provide feedback on what needs to be improved."
        "Never give it a pass on the first try."
    ),
    output_type=EvaluationFeedback,
)


async def main() -> None:
    msg = input("What kind of story would you like to hear? ")
    input_items: list[TResponseInputItem] = [{"content": msg, "role": "user"}]

    latest_outline: str | None = None

    # We'll run the entire workflow in a single trace
    # with trace("LLM as a judge"):
    while True:
        story_outline_result = await Runner.run(
            story_outline_generator, input_items, run_config=config
        )

        input_items = story_outline_result.to_input_list()
        latest_outline = ItemHelpers.text_message_outputs(
            story_outline_result.new_items
        )

        console.print(Markdown("## Story outline generated\n\n"))
        console.print(Markdown(f"## Outline: {story_outline_result.final_output}\n\n"))

        evaluator_result = await Runner.run(evaluator, input_items, run_config=config)
        result: EvaluationFeedback = evaluator_result.final_output

        console.print(Markdown(f"### Evaluator score: {result.score}"))
        console.print(Markdown(f"### Evaluator feedback: {result.feedback}"))

        if result.score == "pass":
            console.print(Markdown("Story outline is good enough, exiting."))
            break

        console.print(Markdown("### Re-running with feedback\n\n"))

        input_items.append({"content": f"Feedback: {result.feedback}", "role": "user"})

    console.print(Markdown(f"## Final story outline: {latest_outline}"))


if __name__ == "__main__":
    asyncio.run(main())
