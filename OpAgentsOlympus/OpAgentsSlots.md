`__slots__` is a Python class attribute that fundamentally changes how Python stores instance attributes. <cite/>

### Normal Python Classes (without `__slots__`)

By default, Python stores instance attributes in a dictionary called `__dict__` for each object. <cite/> This means:
- You can add any attribute to an instance at runtime
- Each instance has its own `__dict__` dictionary
- Memory overhead includes the dictionary structure

### With `__slots__`

When you define `__slots__`, Python:
1. **Eliminates the `__dict__`** - No dictionary is created for each instance <cite/>
2. **Pre-allocates fixed slots** - Creates a fixed number of memory slots for the specified attributes
3. **Restricts attribute assignment** - You can only set attributes listed in `__slots__` <cite/>

### Concrete Example from the Codebase

Looking at `AgentSpanData`, it defines `__slots__ = ("name", "handoffs", "tools", "output_type")`. This means:

- Each `AgentSpanData` instance can only have these 4 attributes
- No `__dict__` is created
- Memory is pre-allocated for exactly these 4 slots
- You cannot do `instance.some_random_attribute = value` - it will raise an `AttributeError`

### Memory Impact

For classes like `FunctionSpanData` with `__slots__ = ("name", "input", "output", "mcp_data")`, each instance uses significantly less memory because it avoids the overhead of a dictionary. In a tracing system that might create thousands of span objects, this memory savings adds up quickly. <cite/>

## Notes

The trade-off is flexibility vs efficiency - you lose the ability to dynamically add attributes but gain substantial memory and performance benefits. This is why it's used extensively in the span data classes where the structure is well-defined and performance matters.
