### Disclaimer: This is going to be Complicated!

Let’s figure out why this Python code raises a **TypeError**:

```python
class A:
    def process(self):
        print("From: A")

class B(A):
    def process(self):
        print("From: B")
        super().process()

class C(A):
    def process(self):
        print("From: C")
        super().process()

class First(B, C): pass
class Second(C, B): pass

class Combined(First, Second): pass  # TypeError
```
---

### **1. What is MRO and C3 Linearization?**

- **MRO** stands for **Method Resolution Order**. It’s the sequence Python uses to look for methods or attributes in a class and its parents. For example, if `Combined` needs a method, Python follows the MRO to decide where to look first, second, and so on.
- When a class inherits from multiple parents (like `First` and `Second` here), Python uses an algorithm called **C3 linearization** to build this sequence. It has to be consistent and make sense.
- In C3, we **merge** lists (the MROs of the parent classes plus the list of parents) into one order. Each list has a **head** (the first item) and a **tail** (everything after the head). The rule is: **Pick a head only if it’s not in any other list’s tail.** If we can’t pick anything, the merge fails, and we get a `TypeError`.

---

### **2. What Are the MROs of `First` and `Second`?**

let’s figure out the MROs for its parents: `First` and `Second`.

- **`First` is `class First(B, C)`**:
  - It inherits from `B` and `C`, in that order.
  - `B` inherits from `A`.
  - `C` inherits from `A`.
  - Python starts with `First`, then follows the order of parents: `B`, then `C`, then `A` (since both `B` and `C` lead to `A`), and finally `object` (the ultimate base class in Python).
  - So, the MRO is: **`[First, B, C, A, object]`**.

- **`Second` is `class Second(C, B)`**:
  - It inherits from `C` and `B`, in that order.
  - `C` inherits from `A`.
  - `B` inherits from `A`.
  - Starting with `Second`, it goes `C`, then `B`, then `A`, and `object`.
  - So, the MRO is: **`[Second, C, B, A, object]`**.

Notice the difference: `First` has `B` before `C`, while `Second` has `C` before `B`.

---

### **3. Why Does `Combined` Fail?**

Now, `Combined` is defined as `class Combined(First, Second)`. Python needs to build its MRO by merging:
- The MRO of `First`: `[First, B, C, A, object]`
- The MRO of `Second`: `[Second, C, B, A, object]`
- The list of parents: `[First, Second]`

The MRO starts with `Combined`, then merges these three lists using the C3 rule. Let’s do it step by step:

#### **Starting Lists:**
```
L1 = [First, B, C, A, object]    # MRO of First
L2 = [Second, C, B, A, object]   # MRO of Second
L3 = [First, Second]             # Parents of Combined
```

#### **Step 1: Pick the First Item**
- Heads: `First` (L1), `Second` (L2), `First` (L3).
- Check `First`:
  - Tail of L1: `[B, C, A, object]` → no `First`.
  - Tail of L2: `[C, B, A, object]` → no `First`.
  - Tail of L3: `[Second]` → no `First`.
  - `First` isn’t in any tail, so pick it.
- New MRO: `[Combined, First]`.
- Update lists:
  ```
  L1 = [B, C, A, object]
  L2 = [Second, C, B, A, object]
  L3 = [Second]
  ```

#### **Step 2: Pick the Next Item**
- Heads: `B` (L1), `Second` (L2), `Second` (L3).
- Check `B`:
  - Tail of L1: `[C, A, object]` → no `B`.
  - Tail of L2: `[C, B, A, object]` → has `B`.
  - Tail of L3: `[]` → no `B`.
  - `B` is in L2’s tail, so we can’t pick it.
- Check `Second`:
  - Tail of L1: `[C, A, object]` → no `Second`.
  - Tail of L2: `[C, B, A, object]` → no `Second`.
  - Tail of L3: `[]` → no `Second`.
  - `Second` isn’t in any tail, so pick it.
- New MRO: `[Combined, First, Second]`.
- Update lists:
  ```
  L1 = [B, C, A, object]
  L2 = [C, B, A, object]
  L3 = []  # Empty now
  ```

#### **Step 3: Pick the Next Item**
- Heads: `B` (L1), `C` (L2). (L3 is empty, so ignore it.)
- Check `B`:
  - Tail of L1: `[C, A, object]` → no `B`.
  - Tail of L2: `[B, A, object]` → has `B`.
  - `B` is in L2’s tail, so we can’t pick it.
- Check `C`:
  - Tail of L1: `[C, A, object]` → has `C`.
  - Tail of L2: `[B, A, object]` → no `C`.
  - `C` is in L1’s tail, so we can’t pick it.

#### **Problem!**
- `B` can’t be picked because it’s in L2’s tail (`[B, A, object]`).
- `C` can’t be picked because it’s in L1’s tail (`[C, A, object]`).
- There’s no head we can choose! The merge gets stuck.

---

### **4. Why the TypeError?**

Python’s C3 algorithm fails when it can’t find a consistent order. Here:
- `First` wants `B` before `C` (from `[First, B, C, A, object]`).
- `Second` wants `C` before `B` (from `[Second, C, B, A, object]`).
- `Combined` inherits from both, but `B` and `C` can’t agree on who comes first, and neither can be skipped or ignored.

Since Python can’t resolve this conflict, it raises:

```
TypeError: Cannot create a consistent method resolution order (MRO) for bases First, Second
```

**Bones:** Java doesn't support multiple inheritance specifically to avoid the complexity and ambiguity caused by the **Diamond Problem**.
