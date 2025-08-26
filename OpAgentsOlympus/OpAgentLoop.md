✅ **The Exact Steps the Agent Loop Takes When You Send a Request**

When you call `Runner.run()` in OpenAI’s Agents SDK, here’s what happens👇

---

## 1️⃣ **Setup & Start Tracing 📊**

* The runner sets up objects to manage the agent run:

  * A **RunContextWrapper** keeps track of context, token usage, and state across turns.
  * A **tool tracker** watches which tools are used on each turn.
* It sets up **tracing** so you can follow what the agent does. If tracing is disabled, it skips this.

---

## 2️⃣ **Turn Counter & Max Turns Check 🔢**

* The loop starts with turn number `0` and adds `1` each time.
* If the turn goes over your max setting, it raises an error and stops execution.

---

## 3️⃣ **Agent Span (Tracing Block) 🎯**

* If no active span yet, it starts one for the current agent.
* The span stays active until the agent changes (handoff) or the loop ends.

---

## 4️⃣ **Get Tools & Handoff Options 🛠️**

* Each turn, it collects the tools that the agent can use.
* It also checks if there are handoff options (if control should move to another agent).

---

## 5️⃣ **Run Input Guardrails (1st Turn Only) 🛡️**

* On the first turn, it runs **input guardrails** (safety checks).
* If any guardrail triggers a tripwire, it stops and reports an error.

---

## 6️⃣ **Run Agent Start Hooks 🪝**

* The first time an agent runs (or after handoff), it triggers **start hooks** — custom code that runs at the start.

---

## 7️⃣ **Get System Instructions 📋**

* The agent provides system instructions (like a system prompt) that help the model understand the task.

---

## 8️⃣ **Send Inputs to the Model 🧠**

* It prepares all needed info: system instructions, input, tool list, settings, etc.
* It sends this to the model:

  * **Non-streaming:** waits for the model’s full response.
  * **Streaming:** handles the model’s response as it comes in, piece-by-piece.

---

## 9️⃣ **Process the Model’s Response 🔍**

* The response is processed to figure out:

  * Did the agent produce a final output?
  * Are tools needed?
  * Is a handoff needed?
* It updates tool tracking based on what the agent used.

---

## 🔟 **Run Tools & Handle Side Effects 🔧**

* If tools were called, it runs them and stores their results for the next turn.

---

## 1️⃣1️⃣ **Decide What Happens Next 🚀**

* If there’s a **final output**, it runs output guardrails (final checks) and returns the result.
* If it’s a **handoff**, it switches to the new agent and resets tracing for the new agent.
* If it needs to **run again**, it simply loops for another turn.

---

## 1️⃣2️⃣ **Handle Errors & Clean Up 🚨**

* If something goes wrong (like a tripwire or max turns hit), it records the error in the trace.
* It makes sure spans and traces are finished properly.

---

## 🔄 **When Does the Loop Stop?**

* When the agent gives final output.
* When an error happens.
* When max turns are hit.

---

💡 **Streaming vs Non-Streaming**

| What’s different?      | Non-Streaming          | Streaming               |
| ---------------------- | ---------------------- | ----------------------- |
| How the model responds | Whole response at once | Piece-by-piece          |
| How events are handled | Directly               | Put into a queue        |
| Error handling         | Raises error           | Signals error via queue |

---

Hopefully this was simple to understand! 💖
