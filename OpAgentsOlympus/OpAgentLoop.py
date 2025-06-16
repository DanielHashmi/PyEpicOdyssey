# ✅ The Exact Steps the Agent Loop Takes When You Send a Request

---

## 1️⃣ **Setup & Start Tracing 📊**

* The runner prepares the objects needed to manage, trace, and track the run:

  * A `RunContextWrapper` is created:

    * Wraps the provided `context` (or `None` if not given).
    * Tracks token usage via a `Usage` object added on each model response.
    * Stores and updates state info across turns (e.g., input, generated items).

  * An `AgentToolUseTracker` is created:

    * Tracks tool usage during turns (for reporting and to assist in tool choice reset logic).

* Tracing:

  * **Non-streaming mode (`Runner.run`)**

    * Uses `TraceCtxManager` to manage trace and spans lifecycle.
    * A new trace is created unless `tracing_disabled=True` in `RunConfig`.

  * **Streaming mode (`Runner.run_streamed`)**

    * If no active trace (`get_current_trace()` returns `None`), creates a new one using `trace()`.
    * If a trace already exists (outer scope), continues within it.
    * `Runner.run_streamed` does not finalize the trace — that happens in `_run_streamed_impl`.

* Trace metadata:

  * Includes `workflow_name`, `trace_id`, `group_id`, `trace_metadata` from `RunConfig`.
  * `trace_include_sensitive_data` controls whether sensitive data is added to spans.

---

## 2️⃣ **Turn Counter & Limit Check 🔢**

* `current_turn` starts at `0` and increments at the start of each loop.
* If `current_turn > max_turns`:

  * Attaches `SpanError` to the current span:

    ```python
    SpanError(message="Max turns exceeded", data={"max_turns": max_turns})
    ```
  * Raises `MaxTurnsExceeded`.
  * **Streaming mode:** Also pushes `QueueCompleteSentinel()` to the event queue to signal termination.

---

## 3️⃣ **Agent Span Management 🎯**

* **Agent Span Creation:**
  * If `current_span is None`, creates a new agent span:
    ```python
    current_span = agent_span(
        name=current_agent.name,
        handoffs=handoff_names,
        output_type=output_type_name,
    )
    ```
  * Span is started with `mark_as_current=True`
  * Tool names are stored: `current_span.span_data.tools = [t.name for t in all_tools]`

* **Span Lifecycle:**
  * Span continues across multiple turns for the same agent
  * Ends when agent changes (handoff) or run completes
  * On handoff: `current_span.finish(reset_current=True)` then `current_span = None`

---

## 4️⃣ **Tools & Handoffs Gathering 🛠️**

* Gathers tools:

  ```python
  all_tools = await agent.get_all_tools(context_wrapper)
  ```

* Gathers handoff options:

  ```python
  handoffs = _get_handoffs(agent)
  ```

  * Converts `Agent` → `Handoff` as needed.

⚠ *`HandoffInputFilter` in `RunConfig` or `Handoff` is not applied at this stage — it is applied during handoff execution.*

---

## 5️⃣ **First Turn: Run Input Guardrails 🛡️**

* Only runs on the first turn (`current_turn == 1`):

  * Combines:

    * `starting_agent.input_guardrails`
    * `run_config.input_guardrails` (if any)

  * **Non-streaming:**

    * Runs `Runner._run_input_guardrails` (which creates tasks for each guardrail).
    * Uses `asyncio.as_completed` inside `Runner._run_input_guardrails` to process them.
    * Cancels remaining tasks if any guardrail tripwire triggers.
    * Attaches `SpanError` and raises `InputGuardrailTripwireTriggered`.

  * **Streaming:**

    * Starts `_run_input_guardrails_with_queue` as a background task:

      * As each finishes, puts result on `streamed_result._input_guardrail_queue`.
      * On tripwire: attaches `SpanError`, pushes to queue.

⚠ *Only the starting agent's input guardrails are run; handoff agents don't re-run them.*

---

## 6️⃣ **Agent Start Hooks 🪝**

* **When agent starts** (controlled by `should_run_agent_start_hooks` flag):
  * Runs when starting the first agent
  * Runs when switching to a new agent after handoff
  * Executes in parallel:
    ```python
    await asyncio.gather(
        hooks.on_agent_start(context_wrapper, agent),
        (agent.hooks.on_start(context_wrapper, agent) 
         if agent.hooks else _coro.noop_coroutine()),
    )
    ```
  * After hooks run, `should_run_agent_start_hooks = False` until next handoff

---

## 7️⃣ **Fetch System Instructions 📋**

* Calls:

  ```python
  system_prompt = await agent.get_system_prompt(context_wrapper)
  ```
* Prepares the model's system instructions for the turn.

---

## 8️⃣ **Send Inputs to Model 🧠**

* Prepares model settings:

  ```python
  model_settings = agent.model_settings.resolve(run_config.model_settings)
  model_settings = RunImpl.maybe_reset_tool_choice(agent, tool_use_tracker, model_settings)
  ```

* Builds input:

  * `system_prompt`
  * Original input + generated items (`input.extend([item.to_input_item() for item in generated_items])`)
  * `model_settings`, `all_tools`, `handoffs`, `output_schema`

* **Non-streaming:**

  * Calls:

    ```python
    await model.get_response(...)
    ```
  * Tracks usage:

    ```python
    context_wrapper.usage.add(new_response.usage)
    ```

* **Streaming:**

  * Calls:

    ```python
    async for event in model.stream_response(...)
    ```
  * For each event:

    ```python
    streamed_result._event_queue.put_nowait(RawResponsesStreamEvent(data=event))
    ```
  * On `ResponseCompletedEvent`:

    * Builds `ModelResponse` with usage data
    * Adds usage: `context_wrapper.usage.add(usage)`
  * If no final response:

    ```python
    raise ModelBehaviorError("Model did not produce a final response!")
    ```

---

## 9️⃣ **Process Response 🔍**

* Calls:

  ```python
  RunImpl.process_model_response(...)
  ```
* Determines:

  * Final output (if valid per output schema or plain string)
  * Tools requested
  * Handoff requested
* Updates `AgentToolUseTracker` with tools used:
  ```python
  tool_use_tracker.add_tool_use(agent, processed_response.tools_used)
  ```

---

## 🔟 **Execute Tools & Side Effects 🔧**

* Calls:
  ```python
  await RunImpl.execute_tools_and_side_effects(...)
  ```
* Updates `generated_items` with new tool results
* Returns `SingleStepResult` with next step information

* **Streaming mode additional step:**
  ```python
  RunImpl.stream_step_result_to_queue(single_step_result, streamed_result._event_queue)
  ```

---

## 1️⃣1️⃣ **Next Step Decision & Execution 🚀**

### **Final Output Path ✅**

* If `isinstance(turn_result.next_step, NextStepFinalOutput)`:

* Runs output guardrails:

  ```python
  _run_output_guardrails(
      current_agent.output_guardrails + (run_config.output_guardrails or []),
      current_agent,
      turn_result.next_step.output,
      context_wrapper,
  )
  ```

* **Non-streaming:**

  * Cancels guardrail tasks on tripwire, raises `OutputGuardrailTripwireTriggered`.
  * Returns:

    ```python
    RunResult(
        input=original_input,
        new_items=generated_items,
        raw_responses=model_responses,
        final_output=turn_result.next_step.output,
        _last_agent=current_agent,
        input_guardrail_results=input_guardrail_results,
        output_guardrail_results=output_guardrail_results,
        context_wrapper=context_wrapper,
    )
    ```

* **Streaming:**

  * Runs output guardrails as background task: `streamed_result._output_guardrails_task`
  * On success: sets `final_output`, `is_complete = True`, pushes `QueueCompleteSentinel()`.

### **Handoff Path 🤝**

* If `isinstance(turn_result.next_step, NextStepHandoff)`:

  * Switches `current_agent = cast(Agent[TContext], turn_result.next_step.new_agent)`
  * Finishes current agent's span:

    ```python
    current_span.finish(reset_current=True)
    current_span = None
    ```
  * Sets `should_run_agent_start_hooks = True` for new agent
  * **Streaming:** Emits `AgentUpdatedStreamEvent(new_agent=current_agent)`

### **Continue Loop Path 🔄**

* If `isinstance(turn_result.next_step, NextStepRunAgain)`:
  * Simply continues to next iteration (no special action)

---

## 1️⃣2️⃣ **Exception Handling & Cleanup 🚨**

### **AgentsException Handling:**
* Populates `exc.run_data` with `RunErrorDetails`:
  ```python
  exc.run_data = RunErrorDetails(
      input=original_input,
      new_items=generated_items,
      raw_responses=model_responses,
      last_agent=current_agent,
      context_wrapper=context_wrapper,
      input_guardrail_results=input_guardrail_results,
      output_guardrail_results=[],
  )
  ```

### **Other Exception Handling:**
* **Streaming:** Attaches error to current span, sets `is_complete = True`, pushes `QueueCompleteSentinel()`
* **Non-streaming:** Error attached to span via `_error_tracing.attach_error_to_span()`

### **Finally Block Cleanup:**
* **Always executed:**
  ```python
  if current_span:
      current_span.finish(reset_current=True)
  ```
* **Streaming only:**
  ```python
  if streamed_result.trace:
      streamed_result.trace.finish(reset_current=True)
  ```

---

## 🔄 **Loop Continuation Logic**

* Loop continues until:
  * Final output produced (`NextStepFinalOutput`)
  * Exception raised
  * Max turns exceeded
  * **Streaming:** `streamed_result.is_complete = True`

* State carried between turns:
  * `original_input` (updated by tool results)
  * `generated_items` (accumulated tool outputs)
  * `model_responses` (all model responses)
  * `current_agent` (changes on handoff)
  * `current_span` (per-agent span)
  * `tool_use_tracker` (cumulative tool usage)

---

## 📊 **Key Differences: Streaming vs Non-Streaming**

| Aspect | Non-Streaming | Streaming |
|--------|---------------|-----------|
| **Trace Management** | `TraceCtxManager` context | Manual `trace.start()` / `trace.finish()` |
| **Model Response** | `await model.get_response()` | `async for event in model.stream_response()` |
| **Event Handling** | Direct processing | Queue-based via `_event_queue` |
| **Guardrails** | Block until complete | Background tasks with queue |
| **Error Handling** | Direct exception propagation | Queue sentinel + `is_complete` flag |
| **Return Type** | `RunResult` | `RunResultStreaming` |
