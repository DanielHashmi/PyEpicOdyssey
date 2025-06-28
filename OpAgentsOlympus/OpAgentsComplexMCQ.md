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

FInd Out the Answer! Happy Coding 🫰
