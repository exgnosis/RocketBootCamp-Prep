# Lab 2-2: Debugging Java with the VS Code Debugger

## Overview

In Lab 2-1 you debugged a Python program that crashed with a clear traceback. The traceback was misleading (it pointed at the wrong line) but it was at least *loud*: the program stopped running and announced that something was wrong. This lab is about a different and more dangerous class of bug: code that runs to completion, returns no error, and reports a wrong answer.

You will work with a small Java program that totals a shopping cart. The program prints `Expect 6.0 => 3.0` when given the list `[1.0, 2.0, 3.0]`. The expectation in the print statement is right (`1.0 + 2.0 + 3.0` should be `6.0`); the computed value is wrong. Nothing in the program's behavior, output, or exit code signals the discrepancy. If the print statement said only `3.0` (without the "Expect 6.0 =>" hint), a reviewer might never notice.

The right tool for this kind of bug is the **interactive debugger**, not log messages. A debugger lets you pause execution at a chosen line, inspect every variable in scope at that moment, then step forward one line at a time and watch the values change. For an accumulator-style bug where you can clearly see the *output is wrong* but you cannot tell *which iteration broke it*, the debugger is faster than any logging strategy. This lab teaches you the four debugger skills that handle most situations in practice: setting a breakpoint, stepping through code, inspecting variables, and using a conditional breakpoint to skip to the iteration that matters.

The lab is therefore part **reading exercise** (look at the code, form a hypothesis about what is wrong), part **tooling exercise** (drive the VS Code Java debugger with confidence), and part **design exercise** (understand the accumulator pattern that the bug violates and recognize it in other code).

**This lab is hands-on.** You write the prompts yourself; no AI assistance is needed or expected for the main exercise. A short stretch step at the end (Part 8) invites you to compare your diagnosis to one from Copilot, but only after you have done the analysis yourself.

---

## Learning Objectives

By the end of this lab, you will be able to:

1. Recognize a silent wrong-answer bug, where the program runs without errors but produces an incorrect result.
2. Set, hit, and remove breakpoints in the VS Code Java debugger.
3. Step through code one line at a time using **Step Over**, **Step Into**, and **Continue**.
4. Inspect variable values in the **Variables** panel and the **Debug Console** while paused at a breakpoint.
5. Use a **conditional breakpoint** to pause only when a specific condition is true, skipping past iterations that are not interesting.
6. Recognize the **accumulator pattern** (initialize once before a loop, update inside) and identify violations of it.
7. Explain why this class of bug is harder to detect by reading alone than a bug that produces an exception.

---

## Part 1: Set Up the Workspace

### Step 1.1: Create the lab folder in VS Code

1. Open VS Code.
2. From the menu, choose **File > Open Folder**.
3. Create a new folder called `java-debug-lab` in your usual workspace location, then open it.
4. When VS Code asks whether you trust the authors of the files in this folder, click **Yes, I trust the authors**.

You should now see an empty Explorer panel on the left with `JAVA-DEBUG-LAB` at the top.

### Step 1.2: Confirm Java and the Extension Pack are installed

In the VS Code integrated terminal (`` Ctrl+` `` or **View > Terminal**):

```bash
java --version
```

Java 17 or later is required (any modern LTS works). The lab uses the single-source-file launcher (`java Main.java`) which compiles and runs in one step; you do not need a separate `javac` invocation.

This lab also requires VS Code's **Extension Pack for Java** (Microsoft). The pack provides the Run and Debug CodeLens links above `main` methods, the Java language server, and the debugger you will be driving in Part 4. To confirm it is installed, open the Extensions view (`Ctrl+Shift+X`), search for "Extension Pack for Java", and check that it is installed and enabled. If it is missing, install it now and reload VS Code when prompted.

### Step 1.3: Create a lab notebook

Create a file called `notebook.md` in the workspace. You will record your analysis and observations as you go. Start it with:

```markdown
# Java Debugging Lab Notebook

## Part 2: Run the program

## Part 3: First-pass diagnosis

## Part 4: Step through with the debugger

## Part 5: Conditional breakpoint

## Part 6: Analysis (the accumulator pattern)

## Part 7: Apply the fix

## Part 8: Stretch (compare your analysis to Copilot's)

## Part 9: Reflection
```

Save it.

---

## Part 2: Run the Program

### Step 2.1: Create the file

In the Explorer panel, create a new file called `Main.java` and paste in the following code exactly:

```java
import java.util.Arrays;
import java.util.List;


public class Main {
    public static void main(String[] args) {
        System.out.println("Expect 6.0 => " + Cart.total(Arrays.asList(1.0, 2.0, 3.0)));
    }
}


class Cart {
    public static double total(List<Double> prices) {
        double total = 0.0;
        for (double p : prices) {
            total = 0.0;
            total = total + p;
        }
        return total;
    }
}
```

Save the file. Notice the file is named `Main.java`, matching the `public class Main` declaration; this is required by Java.

### Step 2.2: Run the program

Just above the `public static void main(String[] args)` line, the Java extension renders two clickable text links: **Run | Debug**.

Click **Run**.

The **Debug Console** pane opens at the bottom of the window. After a moment you should see:

```
Expect 6.0 => 3.0
```

### Step 2.3: Observe the failure mode

This is the failure mode the lab is about. The program:

- Compiled without warnings.
- Ran to completion without throwing any exception.
- Exited normally with status zero.
- Printed a wrong answer.

The only reason you can tell something is wrong is that the print statement includes the literal text `Expect 6.0 =>` for comparison. Without that hint, the line `3.0` would look like a perfectly plausible total. In a larger program where the result is consumed by other code (not just printed for a human to read), the wrong answer would propagate silently. Subsequent calculations would compound the error, and the eventual failure might surface far from the actual bug, or never surface at all.

Write a sentence in your notebook about why a silent wrong-answer bug is more dangerous than a crash.

> **A note on assertions.** In a real codebase, instead of `System.out.println("Expect 6.0 => " + ...)`, you would write an assertion or a unit test:
>
> ```java
> assert Cart.total(Arrays.asList(1.0, 2.0, 3.0)) == 6.0 : "total should be 6.0";
> ```
>
> An assertion would have failed loudly here. The lab uses the print form because it lets you see the wrong answer with your own eyes; tests will come later in the curriculum.

---

## Part 3: First-Pass Diagnosis

Before opening the debugger, read the code one more time and write your hypothesis in your notebook.

> **What is the bug, based on a careful reading of the source alone?**

Be specific. Name the line you think is at fault and explain what is wrong with it. If you think the bug might be in `main` instead of in `Cart.total`, say so. If you think the inputs are wrong, say so. Do not look at Part 4 (the debugger walkthrough) or Part 6 (the analysis) until you have written your answer.

This is the same discipline you used in Lab 2-1: form a hypothesis based on reading, then test it with a tool. The point is to find out whether you spotted the bug by eye, or whether you need the debugger to find it. Both outcomes are common; both are useful information about your own code-reading habits.

---

## Part 4: Step Through with the Debugger

This part introduces VS Code's interactive Java debugger. If you have never used a debugger before, follow each step carefully and watch the panels in the lower-left of the editor; they tell you everything about the program's state.

### Step 4.1: Set a breakpoint

In `Main.java`, find the line:

```java
for (double p : prices) {
```

Click in the gutter (the empty area just to the left of the line number). A solid red circle appears. That is a **breakpoint**: when you run the program in debug mode, execution will pause just before this line executes.

> **Removing or moving breakpoints.** Clicking the red circle again removes it. You can have any number of breakpoints active at once. The **Breakpoints** panel in the Debug view lists all of them and lets you enable, disable, or remove them with checkboxes.

### Step 4.2: Start a debug session

Click **Debug** above the `main` method (next to the **Run** link you used in Step 2.2). Alternatively, press `F5`.

The bottom panels change. The **Debug Console** is still there, but a new set of panels appears in the left sidebar: **Variables**, **Watch**, **Call Stack**, and **Breakpoints**. The editor highlights the line at the breakpoint in yellow, indicating that execution is paused at that line, about to execute it.

The **Variables** panel currently shows the local variables visible at this point in the call stack. You should see something like:

```
Locals
  prices: ArrayList<Double>(size=3) = [1.0, 2.0, 3.0]
  total: 0.0
```

`p` is not visible yet because the loop has not entered its first iteration.

### Step 4.3: Step over the loop, one line at a time

At the top of the editor, a small debug toolbar appears with five icons. The ones you will use most are:

| Icon | Name | Keyboard | What it does |
|------|------|----------|---------------|
| Curved arrow over a dot | **Step Over** | `F10` | Execute the current line, pause at the next line in the same function. |
| Arrow into a dot | **Step Into** | `F11` | If the current line calls a function, descend into it. |
| Arrow out of a dot | **Step Out** | `Shift+F11` | Run until the current function returns. |
| Triangle | **Continue** | `F5` | Resume execution until the next breakpoint. |
| Square | **Stop** | `Shift+F5` | End the debug session. |

Press `F10` to step over the `for` line. Execution moves to the line:

```java
total = 0.0;
```

Look at the Variables panel. `p` now exists and has the value `1.0` (the first element of the list). `total` still has the value `0.0` from its initialization before the loop.

Press `F10` again. Execution moves to:

```java
total = total + p;
```

The `total = 0.0;` line just executed. Look at the Variables panel: `total` is still `0.0`, because it was already `0.0` and was reassigned to `0.0`. This is correct on the *first* iteration, but it should be the warning sign for what happens on the next.

Press `F10` again. Execution moves back to the top of the loop. Look at the Variables panel: `total` is now `1.0`, the result of `0.0 + 1.0`.

So far so good. The first iteration of the loop computed `0.0 + 1.0 = 1.0` and stored it in `total`. Watch what happens in the second iteration.

Press `F10`. Execution moves to `total = 0.0;` again. Variables: `p` is now `2.0` (the second element), `total` is `1.0` (the running sum from the previous iteration).

Press `F10`. **Watch the Variables panel closely.** `total` changes from `1.0` to `0.0`. The work the first iteration did has just been discarded.

Press `F10`. `total` becomes `0.0 + 2.0 = 2.0`. Not `1.0 + 2.0 = 3.0` as you would expect. The previous iteration's work was lost.

The third iteration completes the picture. `total` becomes `0.0` again, then `0.0 + 3.0 = 3.0`. The loop returns, and `total` is `3.0` instead of `6.0`. This matches the wrong answer you saw in Part 2.

### Step 4.4: Confirm and stop

Press **Continue** (`F5`) to let the program run to completion, or **Stop** (`Shift+F5`) to end the debug session immediately. Either way, in your notebook update your Part 3 diagnosis with what you actually saw. Did the bug match your hypothesis from Step 3? If not, exactly when did the debugger contradict your hypothesis?

> **What the debugger gave you that reading alone did not.** The bug was on a specific line and could in principle have been found by careful reading. In practice, two lines that both reference `total` and both look like ordinary assignments form a visual block that the eye reads as a unit. The debugger forced you to look at `total` separately on each step, which exposed the reset for what it was: a discarding of accumulated work.

---

## Part 5: Use a Conditional Breakpoint

In a three-element loop, stepping through every iteration is fine. In a thousand-element loop, it is not. **Conditional breakpoints** let you pause only on iterations that meet a condition you specify, skipping past the rest.

### Step 5.1: Make the breakpoint conditional

Right-click the red breakpoint dot on the `for` line. A small menu appears. Choose **Edit Breakpoint** (or **Add Conditional Breakpoint** if you are creating a new one).

A small input field opens. The dropdown defaults to **Expression**. Type:

```
p == 3.0
```

Press Enter. The breakpoint changes appearance slightly (often to a red dot with an `=` inside, depending on your VS Code theme), indicating it is now conditional.

### Step 5.2: Run with the conditional breakpoint

Start a new debug session (`F5`). Execution should now skip past the first two iterations of the loop and pause at the top of the third iteration, when `p == 3.0`. Confirm by looking at the Variables panel: `p` is `3.0`, and `total` is `2.0` (the broken running total from the second iteration).

Step through the third iteration with `F10`. You will see `total` reset to `0.0`, then become `3.0`. This is the same observation you made in Part 4, but you got to it directly without manually stepping through the first two iterations.

> **When conditional breakpoints earn their keep.** Stepping through 100 iterations to reach iteration 73 is tedious and error-prone. A conditional breakpoint on `i == 73` (or `customerId.equals("X-12345")`, or `transaction.amount > 10000`) takes you to the interesting case in one keystroke. Use them aggressively once you are comfortable with the basic breakpoint mechanic.

### Step 5.3: Stop the debug session

Press `Shift+F5` to end the session. Remove the breakpoint by clicking the red dot in the gutter, or convert it back to an unconditional breakpoint via the right-click menu.

---

## Part 6: Analysis (The Accumulator Pattern)

The bug is the line `total = 0.0;` inside the loop body. It resets the running total at the start of every iteration, discarding the work the previous iterations did. The line after it (`total = total + p;`) then adds the current price to a zero, so each iteration replaces `total` rather than augmenting it.

The pattern that the code violates is the **accumulator pattern**, one of the oldest and most common patterns in programming. The pattern has two parts:

1. **Initialize the accumulator once, before the loop.**
2. **Update the accumulator inside the loop.**

In the corrected code, those two parts are:

```java
double total = 0.0;        // initialize once, before the loop
for (double p : prices) {
    total = total + p;     // update inside the loop
}
```

The buggy code performs the initialization step *twice*: once before the loop (correctly) and once at the top of each iteration (incorrectly). The repeated initialization is what destroys the accumulator's running state.

This is a worth-remembering pattern because it shows up everywhere a loop builds up a result: summing numbers, counting matches, joining strings, collecting items into a list, finding a maximum, computing a hash. The same shape of bug ("I accidentally reset my accumulator inside the loop") can appear in any of those.

### Step 6.1: Why this bug is easy to write

Look at the two lines together:

```java
total = 0.0;
total = total + p;
```

They are visually symmetrical: both start with `total =`. Both are short. Both are single statements. They form a small "block" of code that the eye reads as a unit. A reviewer skimming the function is likely to see "two lines that adjust `total`" and move on without realizing that the first line *destroys* what the second line is trying to build.

This is also the kind of bug that a copy-paste error can introduce: someone copies the initialization line from above the loop, pastes it inside, and forgets to delete it. Or someone refactors the function (perhaps extracting it from a longer method) and accidentally duplicates the initialization.

Write a sentence or two in your notebook about why this bug is harder to spot by reading than by running the debugger.

> **A general lesson.** Reading code is not a reliable substitute for running it. Reading is reliable for catching some classes of bugs (typos, missing semicolons, misnamed variables) but unreliable for catching others (accumulator resets, off-by-one errors in indices, subtle ordering issues). When you have a wrong-answer bug and reading is not finding it, switch to the debugger. Do not spend an hour staring at code that the debugger could explain in five minutes.

---

## Part 7: Apply the Fix

### Step 7.1: Make the fix in Main.java

Delete the line `total = 0.0;` from inside the loop. The corrected `Cart.total` method should look like:

```java
public static double total(List<Double> prices) {
    double total = 0.0;
    for (double p : prices) {
        total = total + p;
    }
    return total;
}
```

Three lines of code became two; one line was the bug. Save the file.

### Step 7.2: Run and verify

Click **Run** above the `main` method (not Debug; the bug is fixed, no debugger needed).

Expected output:

```
Expect 6.0 => 6.0
```

The result now matches the expectation. The program still does not enforce that match (it prints "Expect 6.0 =>" as static text, not as a check), but the numbers agree.

### Step 7.3: Save a clean copy

In the Explorer, create a file called `Solution.java` and paste the corrected version, renaming the public class from `Main` to `Solution`:

```java
import java.util.Arrays;
import java.util.List;


public class Solution {
    public static void main(String[] args) {
        System.out.println("Expect 6.0 => " + Cart.total(Arrays.asList(1.0, 2.0, 3.0)));
    }
}


class Cart {
    public static double total(List<Double> prices) {
        double total = 0.0;
        for (double p : prices) {
            total = total + p;
        }
        return total;
    }
}
```

Run it (click **Run** above the `main` in `Solution.java`). Same expected output. You now have both versions side by side, which is useful for the comparison in Part 8.

> **Why a new class name?** Java requires the file name to match the name of the public class inside it. A file named `Solution.java` must declare `public class Solution`, not `public class Main`. Renaming the public class to match the file is the cleanest way to keep both versions in the same folder without confusing the Java tooling.

---

## Part 8: Stretch: Compare Your Diagnosis to Copilot's

As in Lab 2-1, the goal of this step is to compare a human diagnosis to an AI diagnosis and notice where they agree, where they disagree, and what each misses.

### Step 8.1: Open Copilot Chat

Open the Chat view with `Ctrl+Alt+I` (or `Cmd+Alt+I` on macOS). Select **Ask** mode and **Claude Sonnet 4.6** in the model picker. If Claude Sonnet 4.6 is not available, **Auto** is an acceptable fallback (see Lab 1-1 for the full availability notes).

### Step 8.2: Attach the buggy file and ask the question

Attach `Main.java` (the version from Step 7.1 *before* you made the fix; if you already fixed it, paste the original buggy code from Step 2.1 back in temporarily) using the paperclip icon or `#`.

Send this prompt:

```
This program prints "Expect 6.0 => 3.0" when it should print
"Expect 6.0 => 6.0". What is the bug? Identify the specific line
at fault and explain the pattern that the code violates.
```

Read the response. Compare it, point by point, to the diagnosis you wrote in Step 3 and refined in Step 4.

### Step 8.3: Notebook entry

In your notebook, write three or four sentences:

1. Did Copilot identify the same line as the bug?
2. Did Copilot name the **accumulator pattern** explicitly, or did it describe the problem in less general terms?
3. Did Copilot suggest the same fix you would have? Did it suggest anything you had not considered (such as a `Stream.reduce` rewrite, an enhanced for loop using a stream, or a Java records-based alternative)?
4. Did Copilot mention testing or assertions? If yes, did its suggestion match the assertion idea from the Part 2 sidebar?

> **What you should observe.** A well-prompted Claude Sonnet response on this prompt will typically identify the duplicate initialization as the bug. It may go further than you did: it might suggest replacing the entire loop with `prices.stream().mapToDouble(Double::doubleValue).sum()`, which is the idiomatic Java solution. Notice when Copilot's answer is **better** than yours, and notice when its answer is **broader** than the question asked (offering refactors and alternatives when you only asked for the bug). Both observations are useful: the first tells you something to learn; the second tells you something about how Copilot expands its scope by default.

If you fixed `Main.java` and then restored the buggy code for this step, fix it again now so the file is left in a clean state.

---

## Part 9: Reflection

Answer in your notebook. These are open-ended; spend at least ten minutes.

1. **Silent failure versus loud failure.** Lab 2-1's bug crashed with a traceback. Lab 2-2's bug ran to completion and printed a wrong number. From an engineering standpoint, which class of bug is more dangerous and why? What practices would help you catch the silent-failure class earlier?

2. **Debugger versus log statements.** This lab used the debugger. Lab 2-1 used `logging`. For the bug in this lab, would a strategic `System.out.println(total)` inside the loop have led you to the same conclusion as the debugger? In what situations is each tool clearly the right choice?

3. **The visual symmetry trap.** Step 6.1 argued that the two lines `total = 0.0;` and `total = total + p;` are easy to misread as a unit. Have you seen this pattern (visually symmetric code that hides a bug) in your own programming? What review or coding practices could help catch it?

4. **The accumulator pattern in other shapes.** Pick three other common accumulator-style operations: counting matches in a list, joining strings with a separator, finding a maximum, building a histogram. For each one, write the canonical correct shape and the analogous bug (initialization in the wrong place). Are some accumulator bugs harder to spot than others?

5. **Conditional breakpoints in real work.** In a loop with 10,000 iterations, where iteration 7,342 is the one that triggers a bug, what condition would you set on a breakpoint? Brainstorm three different conditions you might try (based on the loop index, on a specific input value, on a state predicate) and discuss when each one would be most useful.

6. **What the test would have caught.** The bug here would have been caught immediately by a unit test asserting `Cart.total(Arrays.asList(1.0, 2.0, 3.0)) == 6.0`. The program *prints* an expected value but does not *check* it. Spell out the difference between a print-and-eyeball verification and an automated assertion. Why does the difference matter once a project has more than a handful of tests?

7. **AI as a debugging partner (again).** In Lab 2-1's Part 8 you compared a Python diagnosis from Copilot to yours. Here you did the same for a Java bug. Was Copilot's performance similar across the two languages, or did it find one bug class more reliably than the other? What might explain the difference (if any)?

---

## Reference: The Debugger Cheat Sheet

| Action | Default keyboard shortcut |
|--------|--------------------------|
| Toggle a breakpoint at the current line | `F9` |
| Start a debug session | `F5` |
| Continue (run until next breakpoint) | `F5` while paused |
| Step Over (execute the current line, do not enter functions) | `F10` |
| Step Into (descend into a function call) | `F11` |
| Step Out (run until the current function returns) | `Shift+F11` |
| Stop the debug session | `Shift+F5` |
| Restart the debug session | `Ctrl+Shift+F5` |
| Add a conditional breakpoint | Right-click in the gutter, **Add Conditional Breakpoint** |
| Edit an existing breakpoint's condition | Right-click the red dot, **Edit Breakpoint** |

These shortcuts apply to most VS Code debuggers (Java, Python, JavaScript, C/C++); the visual panels are the same across languages.

---

## Reference: Types of Breakpoints

VS Code's Java debugger supports several kinds of breakpoints beyond the basic line breakpoint used in this lab.

| Type | When it pauses |
|------|----------------|
| **Line breakpoint** | When execution reaches the line. The default. |
| **Conditional breakpoint** | When the line is reached *and* a Boolean expression you specify is true. Used in Part 5. |
| **Hit-count breakpoint** | When the line has been reached a specified number of times (e.g., on the 100th iteration). |
| **Logpoint** | The line is reached, but instead of pausing, a message is written to the Debug Console. Useful when you want logging temporarily without modifying the source. |
| **Exception breakpoint** | When a specific exception type is thrown anywhere in the program, regardless of whether it is caught. Configured in the **Breakpoints** panel. |

For the bug in this lab, the line breakpoint and the conditional breakpoint were sufficient. In a larger investigation (a `NullPointerException` deep inside framework code, for example), the exception breakpoint is often the first thing to try.

---

## Reference: The Accumulator Pattern in Other Forms

The accumulator pattern is "initialize once outside the loop, update inside." The corrected `Cart.total` is the canonical numeric form. The same shape applies to other types of running result:

| Goal | Initialize outside | Update inside |
|------|---------------------|---------------|
| Sum numbers | `double total = 0.0;` | `total = total + p;` |
| Count matches | `int count = 0;` | `if (matches(x)) count++;` |
| Join strings | `StringBuilder sb = new StringBuilder();` | `sb.append(s);` |
| Find maximum | `double max = Double.NEGATIVE_INFINITY;` | `if (x > max) max = x;` |
| Build a list | `List<T> result = new ArrayList<>();` | `result.add(x);` |
| Compute a product | `long product = 1L;` | `product *= n;` |

The bug in each row is the same shape: putting the "initialize outside" line *also* inside the loop. The symptom in each row is the same: the running result is replaced by the contribution of only the last iteration. Once you have seen the pattern in one form, you can recognize it in any of the others.

A common modern idiom is to skip the explicit accumulator loop entirely and use a stream:

```java
double total = prices.stream().mapToDouble(Double::doubleValue).sum();
```

This form is harder to break in this particular way because there is no explicit accumulator variable to accidentally reset. It is not always more readable than the loop, but for simple accumulation operations it is often the right choice.

---

## Troubleshooting

**Clicking "Run" or "Debug" does nothing; no Run/Debug CodeLens appears above `main`.**
The Extension Pack for Java is not installed or not enabled. Open the Extensions view (`Ctrl+Shift+X`), search for "Extension Pack for Java" by Microsoft, install or enable it, and reload VS Code when prompted. The Run/Debug links should appear after the workspace finishes indexing (look for a "Java: Building..." message in the status bar).

**`error: cannot find main(String[]) method in class: Cart`.**
The Java single-source-file launcher uses the *first* top-level type in the file as the launch class, regardless of which one is `public`. If your code has `class Cart` declared before `public class Main`, the launcher will try to run `Cart` and fail. Make sure `public class Main` appears first in the file, before `class Cart`. The starter in Step 2.1 has them in the correct order; do not reorder.

**`error: class Solution is public, should be declared in a file named Solution.java`.**
You renamed `public class Main` to `public class Solution` but did not rename the file, or vice versa. In Java, the public class name must match the file name. Fix one to match the other.

**The Variables panel is empty when paused at a breakpoint.**
The variable may be out of scope at this exact line, or the debugger may be paused at a position where the local variables have not yet been initialized. Step forward one line (`F10`); the variables should appear once the corresponding declarations have executed.

**The breakpoint is not being hit; the program runs to completion as if Run, not Debug.**
You pressed Run (which ignores breakpoints) instead of Debug. Click the **Debug** link above `main`, or press `F5`, or use the Run and Debug view in the sidebar. The red dot in the gutter must still be visible; a hollow red circle indicates the breakpoint is disabled (right-click and re-enable).

**The conditional breakpoint pauses on iterations where the condition is false.**
The expression syntax is Java, not pseudocode. `p == 3.0` is correct for the `double` variable in this lab; `p = 3.0` (single `=`) would be an assignment and is rejected. Equality on `double` is reliable for exact constants like `3.0` but unreliable for values produced by floating-point arithmetic; use `Math.abs(p - 3.0) < 1e-9` in that case.

**Stepping with F10 unexpectedly enters another function.**
You pressed `F11` (Step Into) instead of `F10` (Step Over). Step Into descends into any function call on the current line, including library calls. Step Over stays in the current function. Press `Shift+F11` (Step Out) to climb back up and continue with `F10`.

**Copilot in Part 8 suggests a stream-based rewrite that does not compile.**
Confirm that `prices` is `List<Double>` and that the stream call is `.stream().mapToDouble(Double::doubleValue).sum()`. The intermediate `mapToDouble(Double::doubleValue)` is necessary because `List<Double>.stream()` produces a `Stream<Double>`, which has no `.sum()` method; `mapToDouble` unboxes to a `DoubleStream`, which does. If Copilot suggested `.mapToDouble(d -> d).sum()`, that works too; both forms compile.

---

## Further Reading

- **Visual Studio Code Java debugging documentation** at <https://code.visualstudio.com/docs/java/java-debugging>. The official reference for everything in the Debugger Cheat Sheet, plus configurations like launch.json that this lab did not use.
- **The Practice of Programming** (Kernighan and Pike, 1999), chapter 5: "Debugging". Referenced in Lab 2-1; equally relevant here. The chapter's distinction between "thinking" and "stepping" maps directly to the choice between reading code and using the debugger.
- **Effective Java, 3rd edition** (Joshua Bloch), Item 1: "Consider static factory methods instead of constructors". Tangentially relevant because the stream-based rewrite is a static method; more broadly, Bloch's book is the canonical resource for idiomatic modern Java.
- **JEP 330: Launch Single-File Source-Code Programs** at <https://openjdk.org/jeps/330>. The feature that makes `java Main.java` work without a separate `javac` step. Useful background for understanding the lab's tooling.
- **"Why Programs Fail"** (Andreas Zeller, 2nd edition, 2009). A book-length treatment of debugging, including the failure-fault-error vocabulary used in Lab 2-1 and chapters on systematic debugging strategies. Recommended for engineers who want to go deeper than this lab.
