import asyncio
import uuid
from config import config

from agents import Agent, Runner, TResponseInputItem, trace, handoff, RunContextWrapper, ItemHelpers

"""
This example shows the handoffs/routing pattern. The triage agent receives the first message, and
then hands off to the appropriate agent based on the language of the request. Responses are
streamed to the user.
"""

def handoff_called(ctx: RunContextWrapper[None]):
    print("Handing off...")

def handoffs(agent: Agent):
    return handoff(agent, on_handoff=handoff_called)

french_agent = Agent(
    name="french_agent",
    instructions="You only speak French, If user asks some other language, transfer to triage agent.",
)

spanish_agent = Agent(
    name="spanish_agent",
    instructions="You only speak Spanish, If user asks some other language, transfer to triage agent.",
)

english_agent = Agent(
    name="english_agent",
    instructions="You only speak English, If user asks some other language, transfer to triage agent.",
)

triage_agent = Agent(
    name="triage_agent",
    instructions="Handoff to the appropriate agent based on the language of the request. You NEVER answer to USER yourself! ALWAYS delegate to specialized agents",
    handoffs=[handoffs(french_agent), handoffs(spanish_agent), handoffs(english_agent)],
    handoff_description="Triage agent who decide which language agent to delegate the task to."
)

french_agent.handoffs.append(handoffs(triage_agent))
spanish_agent.handoffs.append(handoffs(triage_agent))
english_agent.handoffs.append(handoffs(triage_agent))

async def main():
    # We'll create an ID for this conversation, so we can link each trace
    # conversation_id = str(uuid.uuid4().hex[:16])

    msg = input("Hi! We speak French, Spanish and English. How can I help? ")
    agent = triage_agent
    inputs: list[TResponseInputItem] = [{"content": msg, "role": "user"}]

    while True:
        # Each conversation turn is a single trace. Normally, each input from the user would be an
        # API request to your app, and you can wrap the request in a trace()
        # with trace("Routing example", group_id=conversation_id):
        result = Runner.run_streamed(
            agent,
            input=inputs,
            run_config=config
        )
        async for event in result.stream_events():
        # We'll ignore the raw responses event deltas
            if event.type == "raw_response_event":
                continue
            elif event.type == "agent_updated_stream_event":
                print(f"Agent updated: {event.new_agent.name}")
                continue
            elif event.type == "run_item_stream_event":
                if event.item.type == "tool_call_item":
                    print("-- Tool was called")
                elif event.item.type == "tool_call_output_item":
                    print(f"-- Tool output: {event.item.output}")
                elif event.item.type == "message_output_item":
                    print(f"-- Message output:\n {ItemHelpers.text_message_output(event.item)}")
                else:
                    pass  # Ignore other event types


        inputs = result.to_input_list()
        print("\n")

        user_msg = input("Enter a message: ")
        inputs.append({"content": user_msg, "role": "user"})
        agent = result.current_agent


if __name__ == "__main__":
    asyncio.run(main())