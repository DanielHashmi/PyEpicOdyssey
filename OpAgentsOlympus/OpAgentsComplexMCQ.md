## Complex MCQ: Agent Hooks and Tool Execution

**Scenario:** You have a parent agent with both `RunHooks` and `AgentHooks` configured. This parent agent uses an agent-as-tool (created via `agent.as_tool()`) that also has its own `AgentHooks`. The child agent-as-tool calls another regular function tool during its execution.

**Question:** What is the correct sequence of hook executions when the parent agent invokes the agent-as-tool?

**A)** 
1. Parent's `RunHooks.on_tool_start()`
2. Child's `AgentHooks.on_start()`
3. Child's `AgentHooks.on_tool_start()` (for the function tool)
4. Child's `AgentHooks.on_tool_end()` (for the function tool)
5. Child's `AgentHooks.on_end()`
6. Parent's `RunHooks.on_tool_end()`

**B)**
1. Parent's `RunHooks.on_agent_start()`
2. Parent's `RunHooks.on_tool_start()`
3. Child agent execution (no hooks because it's a tool)
4. Parent's `RunHooks.on_tool_end()`
5. Parent's `RunHooks.on_agent_end()`

**C)**
1. Parent's `AgentHooks.on_tool_start()`
2. Child's `Runner.run()` starts with no hooks
3. Child's function tool executes with no hooks
4. Parent's `AgentHooks.on_tool_end()`

**D)**
1. Parent's `RunHooks.on_tool_start()` and `AgentHooks.on_tool_start()` (parallel)
2. Child's `on_agent_start()` (from child's execution context)
3. Child's `AgentHooks.on_tool_start()` and child's context `RunHooks.on_tool_start()` (parallel, for function tool)
4. Child's `AgentHooks.on_tool_end()` and child's context `RunHooks.on_tool_end()` (parallel, for function tool)
5. Child's `on_agent_end()` (from child's execution context)
6. Parent's `RunHooks.on_tool_end()` and `AgentHooks.on_tool_end()` (parallel)

HopeFully You Found The Answer 🎉

Answer: None of The Above, Instead below is the actual Answer!!

#### These two red ones should not be considered since the question directly starts from: 🟩 when the parent agent invokes the agent-as-tool?
⭕ Parent Runner: on_agent_start called...

⭕ Parent Agent: on_start called...

> 💠 Parent Runner: on_tool_start called...

> 💠 Parent Agent: on_tool_start called...

> 💠 Default Runner: on_agent_start called...

> 💠 Child Agent: on_start called...

> 💠 Default Runner: on_tool_start called...

> 💠 Child Agent: on_tool_start called...

> 💠 Default Runner: on_tool_end called...

> 💠 Child Agent: on_tool_end called...

> 💠 Default Runner: on_agent_end called...

> 💠 Child Agent: on_end called...

> 💠 Parent Runner: on_tool_end called...

> 💠 Parent Agent: on_tool_end called...

> 💠 Parent Runner: on_agent_end called...

> 💠 Parent Agent: on_end called...

🔰 Hello_Tool! I was called by the agent_as_tool() 👈 Tool Answer


### WHY?
🟣 **RunHooks will always run regardless of being configured or not, because if RunHooks are None then by default an instance of RunHooks will be passed to it, even though the async methods inside that class do nothing "pass"**

🟣 **AgentsHooks will only run if they are configured else a function will be executed which do nothing "pass"**

🟣 **both RunHooks and AgentHooks execute concurrently But! you might see RunHooks first, because its the first argument in asyncio.gather and asyncio.gather doesn't guarantee order so this is purely an implementation details!**
