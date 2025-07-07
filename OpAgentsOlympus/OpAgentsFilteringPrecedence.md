## Input Filter Precedence

```py
input_filter = handoff.input_filter or (
    run_config.handoff_input_filter if run_config else None
)
```

The precedence logic is implemented in the `execute_handoffs` method where it first checks for a handoff-specific `input_filter`, and only falls back to the global `run_config.handoff_input_filter` if no specific filter is defined

This means:
1. If `handoff.input_filter` is set, it takes precedence and is used
2. If `handoff.input_filter` is `None`, then `run_config.handoff_input_filter` is used as a fallback
3. Only one filter is applied - they are not applied in parallel or combined


## Notes

The handoff input filtering system provides a mechanism to transform conversation state data before it's passed to the target agent during handoffs. The HandoffInputData structure is a frozen dataclass that encapsulates three distinct components of the conversation state:

- `input_history`: The original input provided to Runner.run() (either a string or tuple of input items)

- `pre_handoff_items`: Items generated before the current agent turn, that triggered the handoff 

- `new_items`: Items generated during the current turn, including the handoff trigger and handoff output message

The filter function receives this complete HandoffInputData object and must return a modified HandoffInputData object

The filtered data then replaces the original conversation state that gets passed to the target agent, The filtering happens during handoff execution in RunImpl.execute_handoffs().


> Input Filter in Red Box 🔴

![Input Filter in Red Box](https://iili.io/F0B6mEF.png)
