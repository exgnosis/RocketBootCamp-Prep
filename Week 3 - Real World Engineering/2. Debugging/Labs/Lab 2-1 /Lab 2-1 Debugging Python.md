# Lab 2-1: Debugging in Python

## Overview

Debugging is the activity of finding the *cause* of an unexpected behavior, not just the place where the program failed. Those are often different. A crash with `ZeroDivisionError` on line 5 of `mean.py` will, of course, point your debugger at line 5. The defect that produced the crash may live somewhere else entirely, or may be the absence of code that should have been written but wasn't. New engineers commonly stop at the crash site and try to patch it locally; experienced engineers ask "what should have been true at this point in the program that wasn't, and what code is missing to ensure it would have been true?" That distinction is the entire content of this lab.

You will work with a small function that computes the arithmetic mean of a list of numbers. When called with non-empty input, the function works. When called with an empty list, it crashes with `ZeroDivisionError`. You will be tempted to conclude that the division on the last line is the bug. The lab will then walk you through why that conclusion is wrong, what the actual defect is, and how to fix it in a way that helps callers handle the situation gracefully instead of forcing them to wrap every call in a generic `except Exception`.

The lab is therefore part **reading exercise** (look at the traceback carefully and decide what it tells you), part **diagnostic exercise** (use logging to confirm or refute hypotheses), and part **design exercise** (decide what the fix should do for the code that calls this function).

**This lab is hands-on.** You write the code yourself; no AI assistance is needed or expected for the main exercise. A short stretch step at the end (Part 8) does invite you to compare your diagnosis to one from Copilot, but only after you have done the analysis yourself.

---

## Learning Objectives

By the end of this lab, you will be able to:

1. Distinguish the location of a failure (where the exception is raised) from the location of the defect (the code that should have prevented the failure).
2. Read a Python traceback and identify the call site, the failure site, and the exception type.
3. Use `logging` at the entry of a function to capture the values that caused a failure.
4. Write a guard clause that converts an unhandled crash into a documented, catchable exception.
5. Explain why a function that *raises* an exception on bad input is more useful to its callers than a function that returns a silent default.
6. Use `try`/`except` at a call site to handle bad input without losing the rest of the work in a batch.

---

## Part 1: Set Up the Workspace

### Step 1.1: Create the lab folder in VS Code

1. Open VS Code.
2. From the menu, choose **File > Open Folder**.
3. Create a new folder called `debug-lab` in your usual workspace location, then open it.
4. When VS Code asks whether you trust the authors of the files in this folder, click **Yes, I trust the authors**.

You should now see an empty Explorer panel on the left with `DEBUG-LAB` at the top.

### Step 1.2: Confirm Python is available

In the VS Code integrated terminal (`` Ctrl+` `` or **View > Terminal**):

```bash
python3 --version
```

Python 3.10 or later is sufficient. Python 3.11 or 3.12 is preferred because the traceback messages include the underline arrows (`~~~~~~^~~~~~~~~~~`) that pinpoint the exact subexpression that failed; older Pythons print the same traceback without the arrows. Both are fine for this lab; the arrows just make a few observations easier.

### Step 1.3: Create a lab notebook

Create a file called `notebook.md` in the workspace. You will record observations and your own analysis as you go. Start it with:

```markdown
# Debugging Lab Notebook

## Part 2: The working version

## Part 3: Make it crash

## Part 4: Add logging

## Part 5: Analysis (the fault is not the failure)

## Part 6: Apply the fix

## Part 7: Try/except at the call site

## Part 8: Stretch (compare your analysis to Copilot's)

## Part 9: Reflection
```

Save it.

---

## Part 2: Run the Working Version

### Step 2.1: Create the file

In the Explorer, create a new file called `mean.py` and paste in the following code exactly:

```python
def mean(nums):
    total = 0
    for n in nums:
        total += n
    return total / len(nums)

if __name__ == "__main__":
    print(mean([4, 5, 6]))
```

Save the file.

### Step 2.2: Run it

In the integrated terminal:

```bash
python3 mean.py
```

Expected output:

```
5.0
```

The function works. Or rather: it works for this input. Write one sentence in your notebook describing what you have just confirmed. (Be precise. "The function works" is too strong; "the function works for non-empty input" is closer to what you actually know.)

> **A note on confidence.** A common engineering mistake is to run a function once with a "normal" input, see a sensible result, and conclude the function is correct. That conclusion is unsupported by the evidence. All you have shown is that the function returns a sensible result for one particular input. The rest of the lab is what happens when you give it a different input.

---

## Part 3: Make It Crash

Now you will provoke the failure that the lab exists to investigate.

### Step 3.1: Change the call

In `mean.py`, change the last two lines from:

```python
if __name__ == "__main__":
    print(mean([4, 5, 6]))
```

to:

```python
if __name__ == "__main__":
    print(mean([]))
```

The only change is the argument: an empty list instead of `[4, 5, 6]`. Save the file.

### Step 3.2: Run and observe the crash

```bash
python3 mean.py
```

Expected output (your line numbers may differ slightly depending on Python version and whitespace):

```
Traceback (most recent call last):
  File "/path/to/mean.py", line 8, in <module>
    print(mean([]))
          ^^^^^^^^
  File "/path/to/mean.py", line 5, in mean
    return total / len(nums)
           ~~~~~~^~~~~~~~~~~
ZeroDivisionError: division by zero
```

### Step 3.3: First-pass diagnosis (your turn)

Before moving on to Part 4, write your answer to this question in your notebook:

> **What is the bug in this program?**

Be specific. Name the line you think is at fault and explain what is wrong with it. If you think more than one thing is wrong, list each one. Do not look at Part 5 (Analysis) until you have written your answer.

This is not a trick question. There is a defensible first-pass answer based on the traceback alone. The point of Part 4 and Part 5 is to discover whether your first-pass answer is the full answer.

---

## Part 4: Add Logging to See the Context

A traceback tells you *where* a program failed and *what* exception was raised. It does not directly tell you *why*: it does not show you the values of the variables involved at the moment of the crash. To see those, you need to add observation points.

The cheapest observation point is a `print` statement, but `print` is hard to turn off in production and gets entangled with the program's real output. The professional alternative is the `logging` module, which lets you control verbosity centrally and route output separately from the program's own stdout.

### Step 4.1: Create a logging version

In the Explorer, create a new file called `mean_logged.py` and paste:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

def mean(nums):
    logging.debug("Computing mean for nums=%s (len=%d)", nums, len(nums))
    total = 0
    for n in nums:
        total += n
    return total / len(nums)

if __name__ == "__main__":
    print(mean([]))
```

Notice the file is named `mean_logged.py`, **not** `logging.py`. Naming a file `logging.py` in the current directory would shadow Python's built-in `logging` module and break the `import logging` line at the top. This is a small but real footgun in Python; the rule of thumb is never to give a script the same name as a standard library module.

### Step 4.2: Run it

```bash
python3 mean_logged.py
```

Expected output:

```
DEBUG:root:Computing mean for nums=[] (len=0)
Traceback (most recent call last):
  File "/path/to/mean_logged.py", line 12, in <module>
    print(mean([]))
          ^^^^^^^^
  File "/path/to/mean_logged.py", line 9, in mean
    return total / len(nums)
           ~~~~~~^~~~~~~~~~~
ZeroDivisionError: division by zero
```

The first line of the output is the new information. The `DEBUG:root:` prefix is the format `basicConfig` defaults to: log level, logger name (`root` is the default), and the message. The message contains the answer to "why did this crash": `nums=[]`, `len=0`. The function was called with an empty list and a length of zero.

### Step 4.3: Reconsider

Now look back at the answer you wrote in Step 3.3. With the additional information from logging, does your answer change?

There is a meaningful distinction here that the lab is asking you to notice. The crash happened on line 9 of `mean_logged.py` (`return total / len(nums)`). But the logging output, captured at the *entry* of the function on line 5, already shows that the function was given an empty list. The defect, in other words, was visible *before* the line where the crash occurred. The crash is downstream of the defect, not the defect itself.

Update your notebook entry for Part 4 to capture what you now think. Then go to Part 5.

---

## Part 5: Analysis (The Fault Is Not the Failure)

Engineering vocabulary distinguishes three related concepts:

- A **failure** is the observable misbehavior of the running program (the `ZeroDivisionError` crash).
- A **fault** is the static defect in the code that is responsible for the failure (the missing check on the length of `nums`).
- An **error** is the difference between the program's actual state and its intended state (the function was reached with an input it was not designed to handle).

The traceback in Step 3.2 points you at the *failure*. The line in question (`return total / len(nums)`) is the place where the failure becomes visible. But that line is doing exactly what it is supposed to do given the inputs it received: it is dividing the total by the count, both of which happen to be zero. If you "fix" line 9 (for example, by silently returning `0` when `len(nums) == 0`), you have changed the failure mode (no more crash) without addressing the underlying problem (the function still has no documented opinion about whether empty input is acceptable).

The actual fault in the code is the **absence of a check on the input**. The function does not say what it expects of `nums`, and it does not test that `nums` meets those expectations. The crash is the consequence of that absence.

Write a sentence or two in your notebook capturing this distinction in your own words. You will be returning to it in the reflection.

> **Why the distinction matters in practice.** When you triage a production failure, the most common temptation is to put a band-aid on the line that crashed. Sometimes that is the right fix. More often, the line that crashed is the messenger; the fault is somewhere else, often in code that exists *or fails to exist* far from the crash site. The discipline of asking "what is the fault, as opposed to what is the failure" is what separates a debug session that takes 20 minutes from one that takes 4 hours.

---

## Part 6: Apply the Fix

The fix is not "change line 9 to not divide by zero." The fix is to make the function explicit about what it expects and what happens when it does not get it.

### Step 6.1: Create the fixed version

In the Explorer, create a new file called `mean_fixed.py` and paste:

```python
def mean(nums):
    if len(nums) == 0:
        raise ValueError("mean() of empty list is undefined")
    total = 0
    for n in nums:
        total += n
    return total / len(nums)

if __name__ == "__main__":
    print(mean([]))
```

Two new lines at the start of the function: a check, and an informative exception. Save the file.

### Step 6.2: Run it

```bash
python3 mean_fixed.py
```

Expected output:

```
Traceback (most recent call last):
  File "/path/to/mean_fixed.py", line 10, in <module>
    print(mean([]))
          ^^^^^^^^
  File "/path/to/mean_fixed.py", line 3, in mean
    raise ValueError("mean() of empty list is undefined")
ValueError: mean() of empty list is undefined
```

### Step 6.3: Notice what did and did not change

The program still fails, and a casual reader could be forgiven for asking "what was the point?" Two important things changed even though the program still crashed:

1. **The exception type changed** from `ZeroDivisionError` to `ValueError`. `ZeroDivisionError` is a low-level arithmetic exception; it tells the caller that some math broke. `ValueError` is a semantic exception; it tells the caller that a value they supplied was not valid. The new exception correctly describes what happened.

2. **The exception message changed** from `division by zero` to `mean() of empty list is undefined`. The new message names the function, the offending input, and the reason. A future engineer reading the traceback gets all the context they need without having to read the source.

The function did not become bulletproof. Bad input still produces a failure. But the failure now carries the information the caller needs to handle it sensibly, which is what Part 7 will demonstrate.

> **A general principle.** It is rarely possible to prevent bad input from reaching a function (the caller may be reading from a file, a network, a user, a database query, all of which can be empty for reasons outside your control). It is almost always possible to detect bad input and signal it with a structured exception. Doing the second well is more important than trying for the first.

---

## Part 7: Try/Except at the Call Site

The fix in Part 6 was useful only because it gave callers a typed, named exception they can choose to handle. To see what that looks like in practice, you will write a tiny driver that calls `mean()` on a batch of datasets, some of which are valid and one of which is empty. With the right `try`/`except`, the driver will skip the bad entry and continue processing the rest.

### Step 7.1: Create a caller

In the Explorer, create a new file called `caller.py` and paste:

```python
from mean_fixed import mean

datasets = [
    [4, 5, 6],
    [10, 20, 30, 40],
    [],
    [3.5, 7.5],
]

for data in datasets:
    try:
        result = mean(data)
        print(f"mean({data}) = {result}")
    except ValueError as e:
        print(f"mean({data}) skipped: {e}")
```

This driver imports the function from `mean_fixed.py` and calls it on four datasets, one of which is empty. The `try`/`except` block catches the specific `ValueError` raised by the empty-list case and reports it, but does not let it stop the loop.

Save the file.

### Step 7.2: Run it

```bash
python3 caller.py
```

Expected output:

```
mean([4, 5, 6]) = 5.0
mean([10, 20, 30, 40]) = 25.0
mean([]) skipped: mean() of empty list is undefined
mean([3.5, 7.5]) = 5.5
```

Three numerical results, one structured skip. The empty list is reported in a way the operator can act on (perhaps re-fetch the data, perhaps log it, perhaps email someone), but the rest of the batch was processed.

Contrast this with the original `mean.py` from Part 3. There, an empty list anywhere in the batch would have stopped the whole program with a `ZeroDivisionError` traceback. Two of the three good results would never have been computed. The fix in Part 6 is what makes the difference; the `try`/`except` here is only useful because the function now raises an exception that names the case it represents.

### Step 7.3: Note the trade-off

What would have happened if you had written the `except` clause as `except Exception` instead of `except ValueError`? The driver would still work for this specific case, but it would also silently swallow any other exception the function might raise in the future, including ones that represent serious bugs. The narrower the `except`, the easier it is to tell "expected error case I have handled" from "unexpected bug I need to know about."

Write a sentence in your notebook about why specific exceptions are easier to handle than generic ones.

---

## Part 8: Stretch: Compare Your Diagnosis to Copilot's

This step is the only one in the lab that uses Copilot. The goal is to compare a human diagnosis (yours) to an AI diagnosis (Copilot's) and notice where they agree, where they disagree, and what each one misses.

### Step 8.1: Open Copilot Chat

Open the Chat view with `Ctrl+Alt+I` (or `Cmd+Alt+I` on macOS). Select **Ask** mode and **Claude Sonnet 4.6** in the model picker. If Claude Sonnet 4.6 is not available, **Auto** is an acceptable fallback (see Lab 1-1 for the full availability notes).

### Step 8.2: Attach the buggy file and ask the question

Attach `mean.py` (the version from Step 3.1 that crashes on empty input) using the paperclip icon or `#`. Send this prompt:

```
What is the bug in this program? Be specific about the difference
between the line that fails and the underlying defect.
```

Read the response. Compare it, point by point, to the diagnosis you wrote in your notebook in Step 3.3 and updated in Step 4.3.

### Step 8.3: Notebook entry

In your notebook, write three or four sentences:

1. Did Copilot identify the same fault you did?
2. Did Copilot make the distinction between failure and fault that Part 5 emphasized? (If yes, in roughly the same words?)
3. Did Copilot suggest the same fix you would have? Did it suggest fixes you had not considered?
4. If you had asked Copilot to fix the bug instead of describing it, would the fix have matched the structured `raise ValueError` approach, or would it have been a band-aid on the divide-by-zero line?

You do not have to actually ask the fix-it question; the point is to predict what Copilot would do based on its diagnosis. This is a way of checking whether the diagnosis is deep or shallow.

> **What you should observe.** A well-prompted Claude Sonnet response on this prompt will typically identify the missing input check as the underlying defect, not just the divide-by-zero. It may or may not use the failure/fault/error vocabulary explicitly, but the substance should match. If it gives only a shallow diagnosis ("the function divides by zero when the list is empty; add a check"), notice that the conclusion is right but the reasoning is the kind you would have gotten without going through the lab. The lab's value is in the reasoning, not the conclusion.

---

## Part 9: Reflection

Answer in your notebook. These are open-ended; spend at least ten minutes.

1. **Failure, fault, error.** In your own words, define each of the three concepts and give a small example of each from your own experience programming (in this lab, in earlier labs, or in any code you have worked on). Are these distinctions always crisp, or are there cases where two of them collapse into one?

2. **The cost of band-aids.** Suppose you had "fixed" the original `mean.py` by changing line 5 to `return total / max(len(nums), 1)`. The program no longer crashes; it returns `0.0` for an empty list. What problems does this fix create that the `raise ValueError` fix does not? Think about callers who could not tell the difference between "the average is genuinely zero" and "the input was empty."

3. **Specific vs. generic exceptions.** Python has many built-in exception types: `ValueError`, `TypeError`, `KeyError`, `IndexError`, `ZeroDivisionError`, `StopIteration`, and dozens more. Pick three and give an example of when each one is the appropriate exception for a guard clause to raise. Why is matching the exception type to the error case worth the small extra effort?

4. **Where logging belongs.** This lab put one `logging.debug(...)` call at the entry of the function. In a larger function (say, one with three branches and a loop), where else would you put logging calls? What is the difference between logging at function boundaries versus logging inside loops?

5. **The cost of debug-then-remove.** A common pattern is to add `print` or `logging.debug` calls during a debug session, then remove them once the bug is fixed. The `logging` module makes the removal optional: you can set the log level to `INFO` or `WARNING` and the `DEBUG` calls become silent. What is the case for leaving the `logging.debug` line in the final code? What is the case against?

6. **AI as a debugging partner.** Based on Part 8, what is the right division of labor between you and Copilot when investigating a bug? When is Copilot's diagnosis a useful starting point, and when is it a substitute for thinking that you should resist?

---

## Reference: Failure, Fault, and Error

This vocabulary is from the IEEE Standard Glossary of Software Engineering Terminology (originally IEEE 610.12-1990, now folded into ISO/IEC/IEEE 24765). The definitions matter because casual use of "bug" blurs them.

| Term | Definition | Example in this lab |
|------|------------|---------------------|
| Failure | The observable inability of the program to perform a required function. | `ZeroDivisionError` traceback at runtime. |
| Fault | A defect in the program that, when activated, can cause a failure. | The absence of a guard clause checking `len(nums)`. |
| Error | A human action that produces a fault, or the program state that differs from intent. | Writing `mean` without specifying its precondition. |

A failure is what the user sees. A fault is what is wrong in the source. An error is what produced the fault. In casual conversation, all three are called "bugs"; in engineering documentation, the distinction is preserved.

---

## Reference: Logging Levels

Python's `logging` module defines five built-in levels, in increasing severity:

| Level | When to use |
|-------|-------------|
| `DEBUG` | Detailed diagnostic information, only useful while investigating a defect. |
| `INFO` | Confirmation that things are working as expected; e.g., milestones in a long batch job. |
| `WARNING` | Something unexpected happened, but the program is still working. |
| `ERROR` | A serious problem; the program could not perform some function. |
| `CRITICAL` | The program may not be able to continue running. |

The level passed to `logging.basicConfig(level=...)` is the *minimum* level that will be emitted. `logging.basicConfig(level=logging.DEBUG)` shows everything; `logging.basicConfig(level=logging.WARNING)` shows only `WARNING`, `ERROR`, and `CRITICAL`. Changing the level (typically via environment variable or configuration file) lets you turn debug output on for an investigation and off for production, without removing the log lines.

---

## Reference: When to Raise vs. When to Return a Default

A function that detects bad input has three options:

1. **Raise a specific exception** (`raise ValueError(...)`). This is the right choice when the caller might want to handle the case, when the input represents a logical impossibility that should be loud, or when downstream code would produce wrong results if the bad input were silently substituted.
2. **Return a sentinel value** (`return None`, `return float('nan')`, `return 0.0`). Acceptable for functions whose callers are known to handle the sentinel, and where the cost of an exception is high (in tight inner loops, in code paths that must not crash). The risk is that callers forget to check the sentinel and bad data propagates silently.
3. **Return a result type** (`Optional[float]`, `Result[float, str]`, a dataclass with a status field). The compromise. Forces callers to handle the case (you cannot use an `Optional[float]` as a `float` without an unwrap step), but adds verbosity at every call site.

For the `mean()` function in this lab, option 1 is the standard choice: callers should know when they passed an empty list, and `ValueError` is the conventional way to tell them.

---

## Troubleshooting

**`python3: command not found`.**
On some systems the Python interpreter is invoked as `python` rather than `python3`. Try `python --version` first. If that gives Python 3.10 or later, use `python` in place of `python3` for the rest of the lab.

**`ImportError: cannot import name 'mean' from 'mean_fixed'` in Part 7.**
The `caller.py` and `mean_fixed.py` files must be in the same folder, and you must run `python3 caller.py` from inside that folder. Use `pwd` (macOS/Linux) or `cd` (Windows) to confirm. The Python import statement looks in the current directory first.

**The traceback does not include the `~~~~~~^~~~~~~~~~~` arrows under the failing expression.**
You are on Python 3.10 or earlier. The arrows were added in Python 3.11. This does not affect the lab; the traceback still names the file and line.

**`logging.basicConfig(...)` produces no output at all.**
There is most likely a `logging.basicConfig` call earlier in the process (perhaps in another imported module) that already set up the root logger. Once `basicConfig` is configured, subsequent calls are ignored. For this lab the simplest workaround is to confirm `mean_logged.py` is being run as a script (not imported by something else); if it is, the issue is elsewhere.

**You see two `DEBUG:root:` lines instead of one.**
You probably ran the script twice and the second run inherited the first run's logger configuration. This does not actually happen across separate `python3` invocations; if it is happening you are running the file inside a single REPL session. Open a fresh terminal and run again.

**`mean_logged.py` raises `ImportError` referring to itself or to `logging`.**
You named the file `logging.py` and Python is trying to satisfy `import logging` by importing your file. Rename to `mean_logged.py` and rerun. This is the footgun mentioned in Step 4.1.

**Copilot in Part 8 says "I cannot see the file" or returns a generic response.**
The attachment did not register. Look at the chat input area before you send: there should be a visible chip showing `mean.py`. If not, click the paperclip icon and select the file explicitly, or type `#mean.py` and pick the autocomplete suggestion. Then resend.

---

## Further Reading

- **The Practice of Programming** (Kernighan and Pike, 1999), chapter 5: "Debugging". The classic short treatment of the discipline, written for working programmers. The advice in this lab paraphrases the chapter's central message: "stabilize the bug, understand it, then fix it; do not skip understanding."
- **Python `logging` module documentation** at <https://docs.python.org/3/library/logging.html>. The reference for everything in the Reference section on logging levels, plus much more (formatters, handlers, configuration files).
- **IEEE Standard Glossary of Software Engineering Terminology** (IEEE 610.12, superseded by ISO/IEC/IEEE 24765). The source of the failure/fault/error definitions in Part 5.
- **PEP 8 on exception handling** at <https://peps.python.org/pep-0008/#programming-recommendations>. The case for specific `except` clauses over `except Exception`, which Step 7.3 referenced.
- **Effective Python, 3rd edition** (Brett Slatkin), Item 87: "Raise Specific Exceptions to Iron Out Bugs." A focused treatment of the same point this lab makes in Part 6.
