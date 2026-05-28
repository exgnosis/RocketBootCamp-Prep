# Lab 2-3: Debugging Contracts Between Functions

## Overview

In Lab 2-1 the bug was a missing input check inside a single function (`mean()` with no guard for empty lists). In Lab 2-2 the bug was an erroneous line inside a single function (`Cart.total()` resetting its accumulator each iteration). Both bugs lived entirely within one function: the function was wrong on its own terms, and a careful reader of just that function had everything they needed to find the bug.

This lab is about a different and more insidious situation: **a bug that lives between two functions, both of which are correct on their own terms.** You have a function `subtotal()` that takes a list of line items and returns the total cost. It reads `item["unit_price"] * item["qty"]` for each item. You have a separate function `load_items()` that returns a list of line items in the format `{"price": ..., "qty": ...}`. Each function, in isolation, is well-written and unambiguous. The bug appears only when the output of `load_items()` is fed into `subtotal()`: the first function produces `price`, the second function reads `unit_price`, and Python raises `KeyError`.

This class of bug is called a **contract mismatch**, or sometimes an **interface bug**. It is the most dangerous of the three classes you have seen because:

- Code review catches it least often (a reviewer who reads just one function sees no problem).
- Unit tests catch it least often (a test of either function in isolation will pass).
- Static type checkers catch it most easily, but only if the codebase has invested in type annotations for the shapes being passed around. In a plain `dict`-based design like this one, the contract is invisible to the tools.

The lab is therefore part **reading exercise** (read both functions and decide which one is "wrong"), part **diagnostic exercise** (use logging to capture the data shape at the boundary between them), and part **design exercise** (decide whose contract is the authoritative one, and fix the other side to match).

**This lab is hands-on.** You write the code yourself; no AI assistance is needed or expected for the main exercise. A short stretch step at the end (Part 8) invites you to ask Copilot the same diagnostic question twice (once with one function visible, once with both) to see whether the second answer is better than the first.

---

## Learning Objectives

By the end of this lab, you will be able to:

1. Recognize a contract mismatch as a class of bug distinct from "wrong code inside a function".
2. Read a Python `KeyError` traceback and identify both the producer of the data and the consumer that found it lacking.
3. Use logging at the boundary between two functions to capture the actual shape of the data being passed.
4. Construct a small fault tree to organize hypotheses before testing them.
5. Make and defend a design decision about which side of a contract mismatch to fix, rather than treating the fix as obvious.
6. Name at least one type-system feature (TypedDict, dataclasses, attrs, Pydantic) that would have caught the mismatch at the boundary.

---

## Part 1: Set Up the Workspace

### Step 1.1: Create the lab folder in VS Code

1. Open VS Code.
2. From the menu, choose **File > Open Folder**.
3. Create a new folder called `contract-lab` in your usual workspace location, then open it.
4. When VS Code asks whether you trust the authors of the files in this folder, click **Yes, I trust the authors**.

You should now see an empty Explorer panel on the left with `CONTRACT-LAB` at the top.

### Step 1.2: Confirm Python is available

In the VS Code integrated terminal (`` Ctrl+` `` or **View > Terminal**):

```bash
python3 --version
```

Python 3.10 or later is sufficient. Python 3.11 or 3.12 is preferred because the traceback messages include arrow underlines (`~~~~^^^^^^^^^^^^^^`) that point at the exact subexpression that failed. Both work for this lab.

### Step 1.3: Create a lab notebook

Create a file called `notebook.md` in the workspace. You will record observations and design decisions as you go. Start it with:

```markdown
# Contract Lab Notebook

## Part 2: Run the program

## Part 3: First-pass diagnosis

## Part 4: Add logging at the boundary

## Part 5: Reconsider (which side is "wrong"?)

## Part 6: Analysis (contracts and fault trees)

## Part 7: Apply the fix

## Part 8: Stretch (Copilot with and without context)

## Part 9: Reflection
```

Save it.

---

## Part 2: Run the Program

### Step 2.1: Create the file

In the Explorer, create a new file called `cart.py` and paste in the following code exactly:

```python
def subtotal(line_items):
    total = 0.0
    for item in line_items:
        total += item["unit_price"] * item["qty"]
    return total


def load_items():
    return [{"price": 10.0, "qty": 2}, {"price": 5.0, "qty": 1}]


if __name__ == "__main__":
    items = load_items()
    print("Subtotal:", subtotal(items))
```

Save the file.

### Step 2.2: Run it

```bash
python3 cart.py
```

Expected output (your line numbers may differ slightly):

```
Traceback (most recent call last):
  File "/path/to/cart.py", line 13, in <module>
    print("Subtotal:", subtotal(items))
                       ^^^^^^^^^^^^^^^
  File "/path/to/cart.py", line 4, in subtotal
    total += item["unit_price"] * item["qty"]
             ~~~~^^^^^^^^^^^^^^
KeyError: 'unit_price'
```

The traceback identifies two locations:
- **Line 13** (`print("Subtotal:", subtotal(items))`): the call site where the program asked `subtotal()` to do its work.
- **Line 4** (`total += item["unit_price"] * item["qty"]`): the line *inside* `subtotal()` that hit the error.

The exception itself is `KeyError: 'unit_price'`, meaning the dictionary access `item["unit_price"]` failed because the key did not exist in `item`.

---

## Part 3: First-Pass Diagnosis

Before adding any logging or running anything else, write your answer to this question in your notebook:

> **What is the bug, based on a careful reading of the code alone?**

Be specific. Two questions to consider:

1. Which line is at fault?
2. If you were the engineer asked to fix this, which line would you change, and why?

If your answer to question 2 sounded obvious to you, pause and ask yourself: did the *code* tell you which side to change, or did you make a choice without realizing you were making one? Note that question in your notebook too.

Do not look at Part 5 or Part 6 until you have written your answers.

---

## Part 4: Add Logging at the Boundary

The bug is presumably about the shape of data passed between two functions. The cheapest way to confirm or refute that hypothesis is to log the data at the boundary, just before `subtotal()` starts processing it.

### Step 4.1: Create a logging version

In the Explorer, create a new file called `cart_logged.py` and paste:

```python
import logging
logging.basicConfig(level=logging.DEBUG)


def subtotal(line_items):
    logging.debug("Computing subtotal for items=%s", line_items)
    total = 0.0
    for item in line_items:
        total += item["unit_price"] * item["qty"]
    return total


def load_items():
    return [{"price": 10.0, "qty": 2}, {"price": 5.0, "qty": 1}]


if __name__ == "__main__":
    items = load_items()
    print("Subtotal:", subtotal(items))
```

Notice the file is named `cart_logged.py`, **not** `logging.py`. Naming a file `logging.py` in the current directory would shadow Python's built-in `logging` module and break the `import logging` line at the top. Same rule as in Lab 2-1.

### Step 4.2: Run it

```bash
python3 cart_logged.py
```

Expected output:

```
DEBUG:root:Computing subtotal for items=[{'price': 10.0, 'qty': 2}, {'price': 5.0, 'qty': 1}]
Traceback (most recent call last):
  File "/path/to/cart_logged.py", line 19, in <module>
    print("Subtotal:", subtotal(items))
                       ^^^^^^^^^^^^^^^
  File "/path/to/cart_logged.py", line 9, in subtotal
    total += item["unit_price"] * item["qty"]
             ~~~~^^^^^^^^^^^^^^
KeyError: 'unit_price'
```

The first line is the new information. It shows you the exact structure that `subtotal()` was given:

```
[{'price': 10.0, 'qty': 2}, {'price': 5.0, 'qty': 1}]
```

The dictionaries have keys `price` and `qty`. The code on the next line tries to read `unit_price`. The mismatch is now visible.

### Step 4.3: Notice the boundary

The log line was placed at the *entry* of `subtotal()`, not deep inside its loop. That position is not an accident; it is the **boundary** between the two functions. Putting a log statement at every function boundary in a system is one of the simplest debugging techniques: when something goes wrong, you can tell which function received which data, and the question "which side is at fault" becomes answerable.

Update your notebook for Part 4 with what the log line told you.

---

## Part 5: Reconsider (Which Side Is "Wrong"?)

You now have two pieces of evidence:

1. **`load_items()` produces** dicts of the shape `{"price": ..., "qty": ...}`.
2. **`subtotal()` expects** dicts of the shape `{"unit_price": ..., "qty": ...}`.

A first reading of this evidence might be: "obviously `load_items()` is wrong, because `subtotal()` is using `unit_price`." A second reading might be: "obviously `subtotal()` is wrong, because `load_items()` is using `price`." Both readings are plausible from the evidence alone.

This is the central point of the lab: **the evidence does not tell you which side is at fault.** The evidence tells you that the two sides disagree. Who is correct is a design judgment, not something the data can answer.

Write a short paragraph in your notebook arguing for *each* side:

- "The producer (`load_items`) is correct; the consumer (`subtotal`) should be changed to read `price`."
- "The consumer (`subtotal`) is correct; the producer (`load_items`) should be changed to produce `unit_price`."

Then write which one you would choose for a real codebase, and why.

> **There is no universally right answer.** Engineering judgment factors include:
>
> - **Which side has more callers?** If `subtotal()` is called from twenty places and `load_items()` from two, changing `subtotal()` is much higher risk.
> - **Which side defines the canonical data shape?** If `load_items()` reads from a database table named `price`, the column name is essentially fixed; the consumer must adapt. If `subtotal()` is part of a published API that other teams depend on, its contract is fixed; the data source must adapt.
> - **Which side is closer to the source of truth?** `load_items()` is closer to where the data comes from. If the database actually stores prices in a `price` column, calling it `unit_price` in code creates a translation point that has to be remembered everywhere.
> - **Which side has clearer semantics?** "Price" is ambiguous in line-item contexts (is it per-unit, or total for the line?); "unit_price" is unambiguous. This argues for `subtotal()`'s naming being better.

Different shops resolve this differently. The point of this section is that you should know which way you are choosing and why.

---

## Part 6: Analysis (Contracts and Fault Trees)

### Contract mismatch

The bug here is a **contract mismatch**. Each function makes implicit promises and expectations about the data it produces or consumes:

| Function | Implicit contract |
|----------|-------------------|
| `load_items()` | Promises to return a list of dicts, each with keys `price` and `qty`. |
| `subtotal()` | Expects a list of dicts, each with keys `unit_price` and `qty`. |

Neither contract is written down anywhere. Neither contract is checked at runtime. Neither contract is enforced by the type system, because the dicts are untyped (`dict`, not `LineItem`).

The bug is the gap between the two implicit contracts. It is not located on any single line; it is located in the *absence* of an explicit contract that both functions agree on.

### Fault tree

A useful technique for organizing the diagnostic process is the **fault tree**: start with the symptom at the top and decompose it into possible causes, each of which can be tested or refuted with evidence.

For this bug:

```
Top: subtotal() raises KeyError
|
|-- 1. subtotal() reads a key that does not exist
|    |-- 1a. subtotal()'s code is wrong (should read a different key)
|    `-- 1b. the data does not contain the key subtotal() expects
|         |-- 1b-i. load_items() produces the wrong shape
|         `-- 1b-ii. load_items() output is being mutated en route
|
`-- 2. (other unrelated bugs - ruled out by traceback location)
```

Each leaf node is a hypothesis you can test. The log line from Part 4 immediately ruled out node `1b-ii` (the data arrives at `subtotal()` unchanged from what `load_items()` returns) and confirmed node `1b`. That left `1a` vs `1b-i` as the design question Part 5 asked you to answer.

In a five-line program, a fault tree feels like overkill. In a five-thousand-line program with three layers of caching between data and consumer, it is often the only way to keep the hypotheses straight.

### Why this bug is hard to catch

This bug survives all three of the most common quality controls:

1. **Code review of `subtotal()` alone**: the function looks fine. It iterates a list of dicts, accesses two keys, accumulates a total. Nothing wrong.
2. **Code review of `load_items()` alone**: also fine. It returns hardcoded data of a plausible shape.
3. **Unit tests of either function alone**: a test of `subtotal([{"unit_price": 10, "qty": 2}])` passes; a test that checks `load_items()` returns a list of dicts passes. The bug only surfaces in an *integration* test that exercises the boundary between them.

The remedies are correspondingly different from the remedies for in-function bugs:

| Remedy | What it does |
|--------|--------------|
| **Type hints + TypedDict** | Declares the shape of `LineItem` once; both functions reference it; mismatches are caught by `mypy` or other type checkers at the point of mismatch. |
| **`@dataclass` or `attrs.define`** | Same idea, with classes instead of dict shapes. Stronger because attribute access fails at definition time, not at first use. |
| **Pydantic models** | Runtime validation; the wrong shape is rejected with a clear message as soon as `load_items()` tries to return it. |
| **Integration tests at the boundary** | A test that calls `subtotal(load_items())` end-to-end. Cheapest fix in an existing codebase. |
| **A written data dictionary** | A short doc that records what `LineItem` looks like, referenced by both functions. Weakest because it is not enforced, but it gives reviewers something to check against. |

For this lab you will apply the cheapest fix (renaming the field on one side). The reflection at the end revisits the heavier-weight remedies.

---

## Part 7: Apply the Fix

The fix you commit to depends on the design decision you made in Part 5. This lab takes the position that **`subtotal()`'s field name is the more explicit and the more durable**, and therefore the producer should adapt to the consumer. This matches the original solution in the curriculum. If your Part 5 reasoning pointed the other way, the alternative fix is documented at the end of this section.

### Step 7.1: Fix load_items() to use unit_price

In the Explorer, create a new file called `cart_fixed.py` and paste:

```python
def subtotal(line_items):
    total = 0.0
    for item in line_items:
        total += item["unit_price"] * item["qty"]
    return total


def load_items():
    return [
        {"unit_price": 10.0, "qty": 2},
        {"unit_price": 5.0, "qty": 1},
    ]


if __name__ == "__main__":
    items = load_items()
    print("Subtotal:", subtotal(items))
```

The only change is in `load_items()`: the key `"price"` becomes `"unit_price"`. `subtotal()` is unchanged.

Save the file.

### Step 7.2: Run and verify

```bash
python3 cart_fixed.py
```

Expected output:

```
Subtotal: 25.0
```

That is `10.0 * 2 + 5.0 * 1`. The program now runs cleanly and produces the correct total.

### Step 7.3: The alternative fix

For completeness, if your Part 5 design judgment pointed at fixing the consumer instead, the alternative version of `cart_fixed.py` would be:

```python
def subtotal(line_items):
    total = 0.0
    for item in line_items:
        total += item["price"] * item["qty"]
    return total


def load_items():
    return [
        {"price": 10.0, "qty": 2},
        {"price": 5.0, "qty": 1},
    ]


if __name__ == "__main__":
    items = load_items()
    print("Subtotal:", subtotal(items))
```

`load_items()` is unchanged; `subtotal()` now reads `item["price"]`. The output is the same `Subtotal: 25.0`.

Either fix works for this small program. In a real codebase, the choice between them is the engineering question; the typing is mechanical. Note in your notebook which fix you used and why.

> **The fix does not address the underlying problem.** Both versions of `cart_fixed.py` still have an *implicit* contract between `load_items()` and `subtotal()`. If a third function someday produces line items with yet a different key (`"cost"`, `"amount"`, `"price_cents"`), the same class of bug will recur. The reference section after Reflection covers the structural remedies that would actually prevent recurrence.

---

## Part 8: Stretch: Copilot With and Without Context

The interesting Copilot question for this lab is whether the AI's diagnosis improves when it can see *both* functions, as opposed to just the one that crashed. This tests whether the AI understands the bug structurally (a contract issue between functions) or only surface-level (a missing key).

### Step 8.1: Open Copilot Chat

Open the Chat view with `Ctrl+Alt+I` (or `Cmd+Alt+I` on macOS). Select **Ask** mode and **Claude Sonnet 4.6** in the model picker. If Claude Sonnet 4.6 is not available, **Auto** is an acceptable fallback (see Lab 1-1 for the full availability notes).

### Step 8.2: First ask, with only the failing function visible

Start a new chat. Without attaching any file, paste this prompt:

```
The following Python function raises a KeyError: 'unit_price' when
called with data from another part of the system:

def subtotal(line_items):
    total = 0.0
    for item in line_items:
        total += item["unit_price"] * item["qty"]
    return total

What is the bug, and how should I fix it?
```

Read the response. Note in your notebook:

1. Did Copilot ask to see the calling code, or did it diagnose immediately?
2. If it diagnosed immediately, did the diagnosis acknowledge the ambiguity (the bug could be in `subtotal` or in its caller), or did it pick one side?
3. What fix did it propose?

### Step 8.3: Second ask, with both functions visible

Open a new chat (do not continue the previous one). Attach `cart.py` (the buggy version from Step 2.1) using the paperclip icon or `#`. Send this prompt:

```
This program raises KeyError: 'unit_price' when run. What is the bug,
and which function should be changed to fix it? Justify the choice
of which function to change.
```

Read the response. In your notebook:

1. Did the second response identify both `load_items()` and `subtotal()` as participants in the bug?
2. Did it acknowledge that the choice of which side to fix is a design decision?
3. Did it pick the same side as you did in Part 7? If not, on what grounds?
4. Did the answer mention any of the structural remedies from Part 6 (TypedDict, dataclasses, Pydantic, integration tests)?

### Step 8.4: Reflect on the difference

The two prompts differ in one dimension: the amount of context Copilot was given. Compare the two responses:

- Was the second response better than the first? In what way?
- Did the first response say things that were technically right but missed the actual situation?
- If your real workflow is "ask Copilot to debug" without attaching files, what kind of bugs is that workflow likely to handle well, and what kind is it likely to miss?

> **What you should observe.** The first prompt gives Copilot the symptom (a `KeyError` on `unit_price`) and the function that hit it, but not the source of the data. A reasonable Copilot response is "I cannot tell without seeing where the data comes from; the function may be right or wrong depending on context." A weaker response would invent context ("you probably meant `price`") and suggest a fix without acknowledging the ambiguity. The second prompt eliminates the ambiguity by giving both functions; a good Copilot response identifies the contract mismatch explicitly and discusses the design choice, rather than picking a fix without reasoning.

---

## Part 9: Reflection

Answer in your notebook. These are open-ended; spend at least ten minutes.

1. **Three classes of bug.** Lab 2-1 was a missing input check. Lab 2-2 was an accumulator reset. Lab 2-3 was a contract mismatch. Rank these three classes from "hardest to introduce without noticing" to "easiest to introduce without noticing", and from "hardest to catch in code review" to "easiest". Do the rankings agree?

2. **Where the contract lives.** In this lab, the "contract" between `load_items()` and `subtotal()` existed only in the heads of the two engineers who wrote them. Name three places (in real code, not just in this lab) where a contract between two functions could live, and rank them by how well each one would prevent this kind of bug.

3. **TypedDict in practice.** Look up `typing.TypedDict` in the Python docs (a link is in Further Reading). Sketch in your notebook what the `LineItem` `TypedDict` would look like, and how both `load_items()` and `subtotal()` would reference it. How much extra code does this cost? What is the payoff?

4. **The integration test that would have caught it.** Write the body of a pytest function `test_subtotal_with_loaded_items()` that would have failed before the fix and passed after. How many lines of test code? Where in a real codebase would this test live (in the same file as `subtotal()`, in the same file as `load_items()`, in a separate integration test module)?

5. **Boundary logging as a habit.** Step 4.3 introduced the idea of logging at the boundary between functions. Would you adopt this as a default practice for all functions you write? What are the costs (verbose logs, performance, log-file size)? What are the benefits beyond debugging?

6. **The harder version of this bug.** This lab's bug raised a `KeyError`, which is loud. Imagine the same contract mismatch where both sides use the same key (`price`) but mean different things: `load_items()` returns `price` in *cents* (`1000`, meaning ten dollars), `subtotal()` treats `price` as *dollars* (`1000.0`, meaning a thousand dollars). What is the failure mode now? How would you discover the bug? Which remedies from Part 6 would have caught it?

7. **AI as a debugging partner (again).** Across Labs 2-1, 2-2, and 2-3, was Copilot more or less useful as the bugs got more structural? Did the AI's strengths and weaknesses change with the class of bug, or did they stay roughly constant?

---

## Reference: TypedDict in Five Lines

The `TypedDict` mechanism from `typing` (added in Python 3.8) lets you declare the shape of a dictionary without giving up the convenience of plain dict access:

```python
from typing import TypedDict

class LineItem(TypedDict):
    unit_price: float
    qty: int

def subtotal(line_items: list[LineItem]) -> float:
    ...

def load_items() -> list[LineItem]:
    return [{"unit_price": 10.0, "qty": 2}, {"unit_price": 5.0, "qty": 1}]
```

If you run `mypy` against this code with the buggy `load_items()` (returning `price` instead of `unit_price`), it reports:

```
error: Dict entry 0 has incompatible type "str": "float";
       expected "Literal['unit_price', 'qty']": ...
```

The error is at the offending line, not at the runtime crash site. The contract is enforced by the type checker without changing the runtime behavior.

`TypedDict` is the right choice when the data shape needs to remain a `dict` (for JSON serialization, for an API that consumes plain dicts, for compatibility with existing code). When you have freedom to introduce a class, a `@dataclass` or a `pydantic.BaseModel` is usually a better choice; both fail faster and have more capabilities.

---

## Reference: When Each Remedy Is Worth Adopting

| Remedy | Cost | When to adopt |
|--------|------|---------------|
| **A short comment naming the contract** | Almost free | Tiny projects, scripts, prototypes. Better than nothing; not enforced. |
| **`TypedDict` annotations + `mypy`** | A few lines, plus configuring `mypy` once | Any project that uses Python type hints already. Catches mismatches in CI. |
| **`@dataclass` instances** | One class definition, refactoring callers | Projects where the line item is a domain concept used in many places, not just one boundary. |
| **`pydantic.BaseModel`** | A pydantic dependency, slightly heavier syntax | Projects that already use pydantic (FastAPI services, settings management) or where runtime validation is required. |
| **End-to-end integration tests** | A test module, CI configuration | Always worth adding. Catches contract issues regardless of whether type tools are configured. |

The cheapest combination for a new project is "type hints with TypedDict, plus a handful of integration tests." That gives you compile-time guarantees for the contracts and runtime guarantees for the behavior, with very little ceremony.

---

## Reference: Fault Trees in Half a Page

A fault tree starts with an observed failure at the top and decomposes it, level by level, into the things that could cause it. Each node is a hypothesis. Each leaf is a hypothesis you can test with concrete evidence (a log line, a debugger session, a unit test, reading a specific piece of code).

The discipline of building a fault tree is most useful before you start collecting evidence. Without it, debugging often becomes a random walk: you check the first thing that comes to mind, then the second, then the third, with no way to tell whether you have ruled things out or are just spinning in place. With it, you can mark each branch as confirmed, refuted, or untested as your evidence accumulates.

A small fault tree for this lab, more compact than the one in Part 6:

```
KeyError: 'unit_price' inside subtotal()
|
|-- subtotal() reads the wrong key
`-- load_items() produces the wrong shape
    (logging at the boundary ruled in this branch)
```

Two leaves, one of them confirmed by evidence. The remaining question (which one to fix) is a design decision, not a diagnostic one. The fault tree's job ends where the design decision begins.

---

## Troubleshooting

**`python3: command not found`.**
On some systems the interpreter is invoked as `python`. Try `python --version`; if it gives Python 3.10 or later, use `python` in place of `python3` for the rest of the lab.

**`ImportError: cannot import name 'subtotal' ...` in some follow-up of yours.**
Files must be in the same folder and you must run `python3 cart.py` (or `cart_fixed.py`) from inside that folder. The Python import statement looks at the current directory first.

**`cart_logged.py` raises `ImportError` referring to itself or to `logging`.**
You named the file `logging.py` and Python is trying to import your file when it sees `import logging`. Rename to `cart_logged.py` and rerun. Same footgun as in Lab 2-1.

**Logging is configured but no output appears.**
A `logging.basicConfig` call elsewhere (perhaps in another imported module) already configured the root logger. Once it is configured, subsequent calls are ignored. Confirm `cart_logged.py` is being run as a script, not imported.

**The traceback does not include the `~~~~^^^^^^^^^^^^^^` arrows.**
You are on Python 3.10 or earlier. The arrows were added in Python 3.11. The traceback still names the file, line, and exception type; just no arrows.

**Copilot in Step 8.3 claims `Hello.py` is attached when you attached `cart.py`.**
Copilot occasionally references the wrong file when the chat history is long. Start a new chat (the `+` icon), attach `cart.py` again, and confirm the attachment chip shows `cart.py` before sending the prompt.

**Copilot in Step 8.2 fabricates a calling function that does not exist.**
This is a known failure mode when the prompt is ambiguous. The "weaker response" pattern described in the Step 8.4 sidebar is exactly this. Notice it, write it down, and use it as evidence in Reflection question 7.

**`cart_fixed.py` runs but prints `Subtotal: 0.0`.**
You changed `load_items()` to use `unit_price` but accidentally also removed the values (left `{"unit_price": 0.0, "qty": 0}` or similar). Restore the original numeric values; the values should be `10.0` with `qty=2` and `5.0` with `qty=1` for the expected `25.0` output.

---

## Further Reading

- **Python `typing.TypedDict` documentation** at <https://docs.python.org/3/library/typing.html#typing.TypedDict>. The canonical reference for the structural remedy this lab introduces. Short and worth reading once.
- **`dataclasses` documentation** at <https://docs.python.org/3/library/dataclasses.html>. The standard-library mechanism for typed records with attribute access. Most production Python code that does not need plain dicts uses dataclasses.
- **Pydantic documentation** at <https://docs.pydantic.dev>. Goes further than `dataclasses` by validating data at runtime, which is essential when the data comes from outside your program (JSON APIs, configuration files, user input).
- **"Programming as Theory Building"** (Peter Naur, 1985). A short, classic essay arguing that a program is really the *understanding* its authors have of the problem; bugs like the one in this lab live in the gap between two engineers' partially-overlapping theories. A useful frame for thinking about contract mismatches.
- **The Pragmatic Programmer, 20th anniversary edition** (Hunt and Thomas), tip 43: "Design by Contract". The original advocacy for treating function contracts as explicit, checked artifacts.
- **"Why Programs Fail"** (Andreas Zeller, 2nd edition, 2009). The book referenced in Labs 2-1 and 2-2. Chapter 12 covers systematic debugging including formal fault trees and the "scientific method" approach this lab informally applies.
