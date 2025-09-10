### What Are Bitwise Operations?

Bitwise operations work directly on the **binary representations** of numbers (or other data). Instead of treating numbers as numerical values, we manipulate their individual **bits** (0s and 1s). These operations are fast, low-level, and super useful in scenarios like:

- Optimizing code for performance.
- Working with hardware, networking, or cryptography.
- Manipulating flags, permissions, or pixel data in images.

Python provides six main bitwise operators: **AND**, **OR**, **XOR**, **NOT**, **Left Shift**, and **Right Shift**. Let’s learn each one with examples.

---

### Step 1: Understanding Binary Numbers

Before we jump into the operators, you need to know how numbers are represented in binary. For example:

- The number `5` in binary is `0101`.
- The number `3` in binary is `0011`.

Each digit in a binary number is a **bit**. The rightmost bit is the **least significant bit (LSB)**, and the leftmost is the **most significant bit (MSB)**.

You can convert integers to binary in Python using the `bin()` function:

```python
print(bin(5))  # Output: 0b101 (0b indicates binary)
print(bin(3))  # Output: 0b11
```

---

### Step 2: The Bitwise Operators

Let’s explore each bitwise operator, what it does, and how to use it in Python.

#### 1. Bitwise AND (`&`)
- **What it does**: Compares each bit of two numbers. If **both bits** are `1`, the result is `1`; otherwise, it’s `0`.
- **Use case**: Masking (selecting specific bits) or checking if certain bits are set.

**Example**:
```python
a = 5  # 0101
b = 3  # 0011
result = a & b  # 0101 & 0011 = 0001
print(result)  # Output: 1
```

**How it works**:
```
  0101  (5)
& 0011  (3)
-------
  0001  (1)
```

#### 2. Bitwise OR (`|`)
- **What it does**: Compares each bit of two numbers. If **at least one bit** is `1`, the result is `1`; otherwise, it’s `0`.
- **Use case**: Setting specific bits or combining flags.

**Example**:
```python
a = 5  # 0101
b = 3  # 0011
result = a | b  # 0101 | 0011 = 0111
print(result)  # Output: 7
```

**How it works**:
```
  0101  (5)
| 0011  (3)
-------
  0111  (7)
```

#### 3. Bitwise XOR (`^`)
- **What it does**: Compares each bit of two numbers. If the bits are **different** (one is `1`, the other is `0`), the result is `1`; otherwise, it’s `0`.
- **Use case**: Toggling bits, encryption, or finding unique elements.

**Example**:
```python
a = 5  # 0101
b = 3  # 0011
result = a ^ b  # 0101 ^ 0011 = 0110
print(result)  # Output: 6
```

**How it works**:
```
  0101  (5)
^ 0011  (3)
-------
  0110  (6)
```

**Fun Fact**: XORing a number with itself gives `0`, and XORing a number with `0` gives the number itself.

#### 4. Bitwise NOT (`~`)
- **What it does**: Flips all the bits of a number (`0` becomes `1`, `1` becomes `0`). In Python, this is equivalent to `-(x + 1)` due to how negative numbers are represented (two’s complement).
- **Use case**: Inverting bits or computing complements.

**Example**:
```python
a = 5  # 0101
result = ~a  # ~0101 = ...11111010 (in two’s complement, this is -6)
print(result)  # Output: -6
```

**Explanation**:
- For a number `x`, `~x = -(x + 1)`.
- So, `~5 = -(5 + 1) = -6`.

#### 5. Left Shift (`<<`)
- **What it does**: Shifts all bits of a number to the **left** by a specified number of positions. Zeros are filled in from the right. This is equivalent to multiplying by `2^n` (where `n` is the shift amount).
- **Use case**: Fast multiplication or aligning bits.

**Example**:
```python
a = 5  # 0101
result = a << 2  # 0101 << 2 = 010100 (shift left by 2)
print(result)  # Output: 20
```

**How it works**:
```
0101 << 2 = 010100
5 * (2^2) = 5 * 4 = 20
```

#### 6. Right Shift (`>>`)
- **What it does**: Shifts all bits of a number to the **right** by a specified number of positions. For positive numbers, zeros are filled in from the left. This is equivalent to dividing by `2^n` (integer division).
- **Use case**: Fast division or extracting specific bits.

**Example**:
```python
a = 20  # 10100
result = a >> 2  # 10100 >> 2 = 00101
print(result)  # Output: 5
```

**How it works**:
```
10100 >> 2 = 00101
20 // (2^2) = 20 // 4 = 5
```

---

### Step 3: Practical Examples

Let’s apply bitwise operations to solve some real-world problems.

#### Example 1: Checking if a Number is Even or Odd
- A number is even if its least significant bit (LSB) is `0`, and odd if it’s `1`.
- We can use `&` with `1` to check the LSB.

```python
def is_even(n):
    return (n & 1) == 0

print(is_even(4))  # True (4 is 100, LSB is 0)
print(is_even(7))  # False (7 is 111, LSB is 1)
```

#### Example 2: Swapping Two Numbers Without a Temporary Variable
- XOR can be used to swap values efficiently.

```python
a = 5  # 0101
b = 3  # 0011
a ^= b  # a = 0101 ^ 0011 = 0110
b ^= a  # b = 0011 ^ 0110 = 0101
a ^= b  # a = 0110 ^ 0101 = 0011
print(a, b)  # Output: 3 5
```

#### Example 3: Setting and Clearing Bits
- Use `|` to set a bit (turn it to `1`) and `&` with `~` to clear a bit (turn it to `0`).

```python
# Set the 2nd bit (position 1, counting from 0)
number = 8  # 1000
mask = 1 << 1  # 0010
number |= mask  # 1000 | 0010 = 1010
print(number)  # Output: 10

# Clear the 3rd bit (position 2)
number = 12  # 1100
mask = ~(1 << 2)  # ~(0100) = ...1011
number &= mask  # 1100 & 1011 = 1000
print(number)  # Output: 8
```

#### Example 4: Counting Set Bits (Hamming Weight)
- Count the number of `1` bits in a number’s binary representation.

```python
def count_set_bits(n):
    count = 0
    while n:
        count += n & 1  # Check LSB
        n >>= 1  # Shift right
    return count

print(count_set_bits(13))  # 13 = 1101, Output: 3
```