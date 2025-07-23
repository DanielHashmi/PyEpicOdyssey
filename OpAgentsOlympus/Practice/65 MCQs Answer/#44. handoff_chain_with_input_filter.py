from agents import Agent, handoff, HandoffInputData, Runner
from open_router_config import config
from rich import print

def remove_transfer_data(data: HandoffInputData) -> HandoffInputData:
    if isinstance(data.input_history, str):
        return HandoffInputData(
            input_history=data.input_history,
            pre_handoff_items=data.pre_handoff_items,
            new_items=()
        )

    filtered_history = tuple(
        item for item in data.input_history
        if item.get("name") != "transfer_to_b"
    )

    return HandoffInputData(
        input_history=filtered_history,
        pre_handoff_items=data.pre_handoff_items,
        new_items=()
    )

def add_context(data: HandoffInputData) -> HandoffInputData:
    context_item = {"role": "assistant", "content": "You are now the specialist agent"}
    if isinstance(data.input_history, str):
        return HandoffInputData(
            input_history=(context_item, {"role": "user", "content": data.input_history}),
            pre_handoff_items=data.pre_handoff_items,
            new_items=data.new_items
        )

    return HandoffInputData(
        input_history=(context_item,) + data.input_history,
        pre_handoff_items=data.pre_handoff_items,
        new_items=data.new_items
    )

agent_a = Agent(name="A")
agent_b = Agent(name="B", handoffs=[handoff(agent_a, input_filter=add_context)])
agent_c = Agent(name="C", handoffs=[handoff(agent_b, input_filter=remove_transfer_data)])

result = Runner.run_sync(agent_c, 'keep handing off', run_config=config)
print(result.to_input_list())