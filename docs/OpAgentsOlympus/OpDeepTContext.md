## 🔸 What is `TContext`?

In the OpenAI Agents SDK, `TContext` means “type of context.”
You can think of it like this:

* You create your **own** class, such as `UserContext`
* This class becomes your **context**
* The SDK calls it `TContext`, but you control what it contains

Example:

```python
@dataclass
class UserContext:
    user_id: str
    is_admin: bool
```

Here, `UserContext` is your **TContext**. The SDK will treat your `UserContext` as the main context during the agent's execution.

---

## 🔸 Two Types of Context (Important to Know)

There are **two completely different types of "context"** in this SDK. Many developers get confused here.

### 1. `TContext` (Local Context)

This is what *you* define.

* It is your Python class
* It is passed to `Runner.run(...)`
* It is used by tools, hooks, and guardrails
* It is **not** sent to the language model (LLM)
* It is used for internal logic, state, and access

### 2. LLM Context

This is the input the LLM sees.

* Includes messages, instructions or system prompt, and tool results
* The LLM uses this to understand and reply
* You do **not** define this with a Python class
* This is **not** your `TContext`

✅ Important: These two contexts are separate. Your `TContext` is not seen by the LLM.

---

## 🔸 How `TContext` Works in Your Code

Let’s define a custom context:

```python
@dataclass
class UserContext:
    user_id: str
    is_pro: bool

    async def get_purchases(self) -> list[str]:
        ...
```

You use this class when creating the agent:

```python
agent = Agent[UserContext](...)
```

Then, in tools, you get access like this:

```python
@function_tool
async def check_pro_status(ctx: RunContextWrapper[UserContext]) -> str:
    return f"User is pro: {ctx.context.is_pro}"
```

✅ The `ctx` object is a **wrapper**. It wraps your `UserContext`.

---

## 🔸 What is `RunContextWrapper`?

You do **not** use `UserContext` directly in tools.

You use `RunContextWrapper[UserContext]`. This gives extra features.

### What it does:

* It gives access to your context: `ctx.context`
* It lets you track tokens used: `ctx.usage.input_tokens`, `ctx.usage.output_tokens`
* It makes all tools work in a consistent way
* It makes the code type-safe

Example:

```python
input_tokens = ctx.usage.input_tokens
output_tokens = ctx.usage.output_tokens
```

✅ `RunContextWrapper` is always used when your tool or hook needs context.

---

## 🔸 Type Safety Rules

You must follow these simple rules:

### Rule 1: All parts of the agent must use the **same** context type

```python
agent = Agent[UserContext](...)  # OK
# Do not mix with AdminContext in the same agent run
```

### Rule 2: Always declare your context type

```python
agent = Agent[UserContext](...)  # Good
```

---

## 🔸 Where `TContext` Is Used

Here is where your context (like `UserContext`) is used:

1. **Function Tools**

   ```python
   def my_tool(ctx: RunContextWrapper[MyContext], ...) -> ...:
   ```

2. **Agent Hooks**
   Lifecycle functions like `on_start`, `on_tool_start`, etc.

3. **Run Hooks**
   Global workflow logic

4. **Dynamic Instructions**
   Custom system messages based on context

5. **Tool Enabling Logic**
   Turn tools on/off depending on context

## 🔸 Summary

Here is everything again, very short:

| Term                | Meaning / Use                                        |
| ------------------- | ---------------------------------------------------- |
| `TContext`          | The context class you define (like `UserContext`)    |
| `RunContextWrapper` | SDK gives this to tools/hooks instead of raw context |
| `.context`          | Access to your actual context object                 |
| `.usage`            | Info about tokens used                               |
| Not sent to LLM     | Your context is **not** seen by the LLM              |
| Must match          | Same context type used across tools/hooks            |

---

If Helped Star ⭐ Happy Coding 💖 
