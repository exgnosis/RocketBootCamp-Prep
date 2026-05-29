# Lab 3-1: Refactoring to a Design Pattern

## Overview

Refactoring is the discipline of changing the structure of working code without changing its observable behaviour. The goal is to make the code easier to read, easier to change, and harder to break the next time someone needs to extend it. Refactoring is not "rewriting"; the program does the same thing before and after. What changes is who is allowed to call what, where the responsibilities live, and how easily a new feature would slot into the design.

This lab walks you through a small refactor in two stages. You start with a working `calc` package of three computational classes (`Adder`, `Multiplier`, `Divider`) that are used directly by client code. The starter compiles and produces the right answers, but the design has a problem that will get worse as the package grows: every client knows every concrete class, so any change to the package risks breaking every client. In Part 3 you will fix this by introducing a **Facade**: a single public class that hides the package's internals behind a stable interface. In Part 5 (a stretch) you will go one step further and add a uniform dispatch method that lets the Facade route requests by name, opening the door to handling operations that have not been written yet.

The lab is therefore part **reading exercise** (look at the starter and find the design problems before changing anything), part **implementation exercise** (apply the Facade pattern), and part **comparison exercise** (verify the refactored code produces identical output, which is the litmus test for whether your refactor was behaviour-preserving).

**This lab is hands-on.** You write the code yourself; no AI assistance is needed or expected for the main exercise. A short stretch step at the end (Part 6) invites you to ask Copilot to perform the same refactor and compare its result to yours.

---

## Learning Objectives

By the end of this lab, you will be able to:

1. Identify two design weaknesses in code that "works": high coupling between callers and concrete classes, and an implicit interface that grows by accretion as the package grows.
2. Apply the **Facade pattern**: reduce the visibility of internal classes to package-private and route all calls through a single public class.
3. Use Java's package-private access (the absence of an access modifier) to encapsulate implementation details within a package.
4. Verify that a refactor preserved behaviour by comparing the program's output before and after, byte for byte.
5. Recognize when a string-keyed dispatch method (the "Challenge" pattern) is appropriate and when a full Command pattern with one class per operation is the better fit.
6. Explain how the Open/Closed Principle relates to each design and identify what each design must change to support a new operation.

---

## Part 1: Set Up the Workspace

### Step 1.1: Create the lab folder in VS Code

1. Open VS Code.
2. From the menu, choose **File > Open Folder**.
3. Create a new folder called `refactor-lab` in your usual workspace location, then open it.
4. When VS Code asks whether you trust the authors of the files in this folder, click **Yes, I trust the authors**.

You should now see an empty Explorer panel on the left with `REFACTOR-LAB` at the top.

### Step 1.2: Confirm Java and the Extension Pack are installed

In the VS Code integrated terminal (`` Ctrl+` ``):

```bash
java --version
```

Java 17 or later is required. This lab uses a multi-file Java project with a package, so it needs the **Extension Pack for Java** (Microsoft) installed in VS Code; the pack provides the Java language server and the Run / Debug CodeLens links above `main` methods. If you have completed any earlier Java lab in this bootcamp, the pack is already installed.

### Step 1.3: Create the starter code

You will create four source files: three in a `calc` package and one driver class outside the package.

In the Explorer, create the directory structure:

1. Right-click in the Explorer and create a new folder named `calc`.
2. Inside `calc/`, create three files: `Adder.java`, `Multiplier.java`, `Divider.java`.
3. Outside `calc/` (at the project root), create `Main.java`.

Paste the following code into each file exactly:

**`calc/Adder.java`:**

```java
package calc;

public class Adder {
    public int add(int a, int b) {
        return a + b;
    }
}
```

**`calc/Multiplier.java`:**

```java
package calc;

public class Multiplier {
    public int multiply(int a, int b) {
        return a * b;
    }
}
```

**`calc/Divider.java`:**

```java
package calc;

public class Divider {
    // integer division for simplicity; caller is responsible for zero-check
    public int divide(int a, int b) {
        if (b == 0) throw new IllegalArgumentException("b must not be zero");
        return a / b;
    }
}
```

**`Main.java`** (at the project root, not inside `calc/`):

```java
import calc.*;

public class Main {
    public static void main(String[] args) {
        System.out.println(new Adder().add(2, 3));           // 5
        System.out.println(new Multiplier().multiply(4, 6)); // 24
        System.out.println(new Divider().divide(8, 2));      // 4
    }
}
```

Save all four files. The Explorer should now show:

```
REFACTOR-LAB
├── Main.java
└── calc/
    ├── Adder.java
    ├── Multiplier.java
    └── Divider.java
```

### Step 1.4: Run the starter to see the baseline

Click **Run** above the `main` method in `Main.java`. The **Debug Console** pane opens at the bottom of the window. After a moment you should see:

```
5
24
4
```

Three lines, each the result of a calculation: `2 + 3 = 5`, `4 * 6 = 24`, `8 / 2 = 4`.

**Save this output as the baseline** for the refactor:

1. Click anywhere in the Debug Console pane.
2. Press `Ctrl+A` then `Ctrl+C` to copy.
3. In the Explorer panel, create a new file `baseline.txt`.
4. Paste the output and save.

The refactored version in Part 3 will be required to produce exactly this same output, byte for byte. If it doesn't, the refactor has changed behaviour and is broken. That is the entire definition of "behaviour-preserving refactor."

### Step 1.5: Create a lab notebook

Create a file called `notebook.md` in the workspace. You will record your analyses, decisions, and observations as you go:

```markdown
# Refactoring Lab Notebook

## Part 2: Reading the starter

## Part 3: Applying the Facade pattern

## Part 4: Verification

## Part 5: Stretch (uniform dispatch)

## Part 6: Reflection (and Copilot comparison)
```

Save it.

---

## Part 2: Read the Starter Before You Change It

The starter compiles and produces correct results, but its design has weaknesses that will become expensive as the codebase grows. Before you refactor, you should be able to articulate what is wrong. Spend at least 10 minutes on this section.

### Question 2.1: The coupling problem

Look at `Main.java`. It does three things, and each one names a specific class from the `calc` package:

```java
new Adder().add(2, 3);
new Multiplier().multiply(4, 6);
new Divider().divide(8, 2);
```

Answer in your notebook:

1. How many things does `Main.java` need to know about the `calc` package to compile? List each one (each class name, each method name, each parameter type).
2. Imagine the `calc` package grows to have ten classes (`Subtractor`, `Squarer`, `Mean`, etc.). What does the client code now have to know about?
3. Suppose someone on the `calc` team renames `Adder.add` to `Adder.sum` because they think it reads better. How many client files would break? Who has to fix them?

The general principle this illustrates is **coupling**: when two pieces of code depend on each other, a change in one can force a change in the other. Tightly coupled code is hard to evolve. Loosely coupled code can be changed in one place without rippling across the codebase.

### Question 2.2: The implicit interface

The classes in `calc` have no formal "interface" in the Java `interface` sense. But from a *design* point of view, the set of public methods across all the classes in the package functions like an interface: it is what clients depend on, and it is what changes will break clients.

Answer in your notebook:

1. List all the public methods clients can call right now: `Adder.add`, `Multiplier.multiply`, `Divider.divide`. That is the *implicit* interface of the `calc` package.
2. If you add a class `Subtractor` with a public method `subtract`, has the interface changed? Did you write down the new interface anywhere?
3. Implicit interfaces are dangerous because they grow without anyone deciding they should. What would it take to make the interface *explicit*?

### Question 2.3: The Open/Closed Principle

The **Open/Closed Principle** (Bertrand Meyer, 1988; popularized by Robert C. Martin) says:

> Software entities should be open for extension, but closed for modification.

In plain English: when you need to add a new feature, you should be able to do it by *adding* new code, not by *editing* existing code. Existing, tested, working code should not have to be reopened just because you have a new requirement.

Answer in your notebook:

1. To add a `Subtractor` class to the current `calc` package, what existing files do you have to edit? Just the new file, or others as well?
2. To call the new `Subtractor` from `Main`, what existing files do you have to edit? (Hint: `Main` currently calls `Adder`, `Multiplier`, `Divider` by name.)
3. How does this compare to the desired property "open for extension, closed for modification"?

### Reference: Things you should have noticed

Check your answers against this list:

**Coupling (Q2.1):** `Main.java` knows three class names, three method names, and the parameter types of each method. That is nine distinct facts about `calc`. With ten classes, it would be roughly thirty. Every rename in `calc` forces a change in `Main`. With many clients (not just one), every rename forces a change in every client.

**Implicit interface (Q2.2):** The interface is the set of public methods across all classes. Today it is three methods; tomorrow it could be thirty, with no document recording when each one was added. Nothing in the language requires anyone to write down what the interface is. The result: clients break, and reviewers cannot tell whether a proposed change to `calc` is a small fix or a breaking API change.

**Open/Closed (Q2.3):** Adding a new operation means writing one new class (good, that is extension) *and* editing `Main` to call it (bad, that is modification). With many clients, every new operation forces edits across the whole client base. The code is *partly* open for extension (you can add classes) and *not* closed for modification (you have to edit consumers). The Facade pattern in Part 3 will fix the second half.

---

## Part 3: Refactor to the Facade Pattern

You will refactor in two coordinated steps:

1. Reduce the visibility of the existing classes from `public` to package-private so that clients outside `calc` can no longer see them.
2. Introduce a new public class `Facade` that exposes a stable, uniform interface and routes calls to the package-private implementations.

After both steps, `Main` will no longer mention `Adder`, `Multiplier`, or `Divider` by name; it will only know about `Facade`. The implementation classes become an internal detail of the `calc` package.

### Step 3.1: Reduce visibility

Edit `Adder.java`, `Multiplier.java`, and `Divider.java`. Remove the `public` keyword from both the class declaration and the method declaration in each one. The result for each file should look like:

**`calc/Adder.java`:**

```java
package calc;

class Adder {
    int add(int a, int b) {
        return a + b;
    }
}
```

**`calc/Multiplier.java`:**

```java
package calc;

class Multiplier {
    int multiply(int a, int b) {
        return a * b;
    }
}
```

**`calc/Divider.java`:**

```java
package calc;

class Divider {
    // integer division for simplicity; caller is responsible for zero-check
    int divide(int a, int b) {
        if (b == 0) throw new IllegalArgumentException("b must not be zero");
        return a / b;
    }
}
```

Save all three.

> **A note on Java access modifiers.** Java has four levels: `public` (everyone), `protected` (subclasses and same package), no modifier ("package-private", same package only), and `private` (same class only). The absence of a keyword on a class or method declaration means package-private. This is the right level for code that is an implementation detail of a package but needs to be reachable from other classes inside the same package (like the Facade you are about to write).

### Step 3.2: Verify that `Main` now fails to compile

In the Explorer, click on `Main.java`. You should immediately see red underlines under `Adder`, `Multiplier`, and `Divider`: the Java language server has noticed that these classes are no longer visible from outside `calc`. Open the **Problems** pane (`Ctrl+Shift+M`); you should see three errors:

```
The type Adder is not visible
The type Multiplier is not visible
The type Divider is not visible
```

This is the expected and desired state. The visibility change has done its job: clients can no longer name the internal classes. Now you need to give them something they *can* name.

### Step 3.3: Create the Facade

In the Explorer, inside the `calc/` folder, create a new file `Facade.java`. Paste in:

```java
package calc;

public class Facade {

    // Composition keeps internals swappable and testable
    private final Adder adder;
    private final Multiplier multiplier;
    private final Divider divider;

    // Default constructor wires the package-private implementations.
    public Facade() {
        this(new Adder(), new Multiplier(), new Divider());
    }

    // Visible for testing if you want to swap implementations later.
    Facade(Adder adder, Multiplier multiplier, Divider divider) {
        this.adder = adder;
        this.multiplier = multiplier;
        this.divider = divider;
    }

    public int add(int a, int b) {
        return adder.add(a, b);
    }

    public int multiply(int a, int b) {
        return multiplier.multiply(a, b);
    }

    public int divide(int a, int b) {
        return divider.divide(a, b);
    }
}
```

Save the file.

Three design points worth noticing as you read this:

1. **`Facade` is `public`.** It is the only thing outside the package that the world can see. The whole point is to have exactly one entry point into the package.
2. **The fields are `private final`.** The Facade owns its dependencies, and they are immutable references. Clients cannot reach in and replace them.
3. **The second constructor is package-private.** It takes the three internal classes as parameters, which is useful for testing (you can pass mocks or alternate implementations from a test class in the same package). External code cannot call it because it cannot name `Adder`, `Multiplier`, or `Divider`.

### Step 3.4: Update `Main` to use the Facade

Edit `Main.java`:

```java
import calc.Facade;

public class Main {
    public static void main(String[] args) {
        Facade c = new Facade();
        System.out.println(c.add(2, 3));         // 5
        System.out.println(c.multiply(4, 6));    // 24
        System.out.println(c.divide(8, 2));      // 4
    }
}
```

Save it.

Notice what changed:

- The import is now `import calc.Facade;` (one class), not `import calc.*;`.
- `Main` mentions exactly one type from `calc`: the `Facade`.
- The internal classes (`Adder`, `Multiplier`, `Divider`) are not named anywhere in `Main`.

This is the structural payoff of the refactor. If the `calc` team decides tomorrow to rename `Adder` to `AdditionEngine` or change its method signature, `Main` is unaffected. The contract between the package and its clients lives entirely in `Facade`.

---

## Part 4: Verify Against the Expected Output

A refactor is supposed to leave behaviour unchanged. Confirm that yours did.

### Step 4.1: Run the refactored code

Click **Run** above the `main` method in `Main.java`. The Debug Console should show:

```
5
24
4
```

### Step 4.2: Compare to the baseline

Apply the **Run-and-Compare procedure**:

1. Copy the new output from the Debug Console (`Ctrl+A`, `Ctrl+C`).
2. Create a new file `refactored.txt` in the Explorer and paste.
3. In the Explorer, click `baseline.txt` to select it. `Ctrl+click` (Windows/Linux) or `Cmd+click` (macOS) `refactored.txt`.
4. Right-click either file and choose **Compare Selected**.

VS Code opens a side-by-side diff. The two panels should be **identical with no highlighted differences**. If they are, your refactor preserved behaviour and the lab's main exercise is done.

### If your output differs

1. **The Facade forwards to the wrong method.** Open `Facade.java` and check each forwarding method. It is easy to type `multiplier.add(a, b)` by mistake when the surrounding methods all look similar. The compiler will not catch this because every method has the same signature.
2. **You changed an integer literal in `Main`.** If you accidentally typed `c.add(3, 3)` instead of `c.add(2, 3)`, the output number will differ. Restore the original arguments.
3. **You used `divide(8, 4)` instead of `divide(8, 2)`.** Same as above; check the values.

If the diff shows differences you cannot explain, revert to the original `Main.java` (or restore from the baseline you captured) and start the refactor again, this time being especially careful with the forwarding methods.

---

## Part 5: Stretch: Uniform Dispatch by Operation Name

The Facade pattern from Part 3 fixed the *visibility* problem but did not fully solve the *Open/Closed* problem. Look at `Facade.java` again: to support a new operation (say, `subtract`), you would have to:

1. Add a `Subtractor` class to the package.
2. Add a `Subtractor` field to `Facade`.
3. Wire it up in both constructors.
4. Add a `public int subtract(int, int)` method to `Facade`.
5. Edit `Main` to call `facade.subtract(...)`.

That is still a lot of edits. In particular, `Facade` has to be modified for every new operation, which is "modification," not "extension."

In this stretch, you will add a single uniform dispatch method to `Facade` that accepts an operation name and an array of arguments and routes the request internally. With this, *clients* never have to change again for a new operation. They always call `facade.calculate(operationName, args)`. The internal change to support a new operation still requires editing `Facade`, but the client interface becomes stable.

### Step 5.1: Add the dispatch method

In `Facade.java`, add this method alongside the existing `add`, `multiply`, `divide`:

```java
public int calculate(String operationType, int[] args) {
    if (operationType.equals("add")) {
        return adder.add(args[0], args[1]);
    }
    if (operationType.equals("multiply")) {
        return multiplier.multiply(args[0], args[1]);
    }
    if (operationType.equals("divide")) {
        return divider.divide(args[0], args[1]);
    }
    throw new IllegalArgumentException("Unknown operation: " + operationType);
}
```

Save the file.

Two design notes worth pausing on:

1. **`operationType.equals("add")`, not `operationType == "add"`.** In Java, `==` on strings compares object references, not contents. Two strings with the same characters may or may not be the same object, depending on how they were created. Always use `.equals()` for string content comparison.
2. **The unknown-operation branch throws an exception.** If a client passes an unknown operation name, the program fails loudly with a useful message. The alternative (silently returning 0, or returning a sentinel like -1) would hide bugs and propagate wrong answers downstream. This is the same defensive-programming principle from Lab 2-1.

### Step 5.2: Exercise the dispatch method from `Main`

Update `Main.java` to use the new dispatch method:

```java
import calc.Facade;

public class Main {
    public static void main(String[] args) {
        Facade c = new Facade();
        System.out.println(c.calculate("add", new int[]{2, 3}));         // 5
        System.out.println(c.calculate("multiply", new int[]{4, 6}));    // 24
        System.out.println(c.calculate("divide", new int[]{8, 2}));      // 4

        // Try an operation that does not exist
        try {
            c.calculate("subtract", new int[]{5, 2});
        } catch (IllegalArgumentException e) {
            System.out.println("Error: " + e.getMessage());
        }
    }
}
```

Run it. Expected output:

```
5
24
4
Error: Unknown operation: subtract
```

The first three lines match the baseline. The fourth line demonstrates the error handling for an unknown operation.

### Step 5.3: Notice what is, and is not, Open/Closed

To add a `Subtractor` operation now, you would still need to:

1. Create a new `Subtractor.java` in the package.
2. Add a `Subtractor` field to `Facade` and wire it up in both constructors.
3. Add a new branch to the `calculate` method.

Step 3 is *modification of existing code*. The dispatch table inside `calculate` has to grow. Strict adherents of the Open/Closed Principle would say this is not a real fix; it has only moved the problem from `Main` to `Facade`.

The textbook answer to this objection is the **Command pattern**: instead of an `if/else` chain inside `calculate`, you maintain a `Map<String, Operation>` (a dispatch table) where each operation is its own object implementing a common interface. Adding a new operation is then a matter of registering a new entry in the map, which can be done at startup or in a configuration file. The `calculate` method does not change.

The reference section after the reflection compares the two approaches in detail. For this lab, the dispatch-table-with-`if/else` is the simpler answer and is what the original assignment asks for. The Command pattern is the next step you would take in a real project that needs to add operations dynamically.

---

## Part 6: Stretch with Copilot, and Reflection

### Step 6.1: Compare your refactor to Copilot's

Open Copilot Chat in VS Code (`Ctrl+Alt+I` or `Cmd+Alt+I` on macOS). Select **Ask** mode and **Claude Sonnet 4.6** in the model picker.

Attach all four original files (the public-class versions from Step 1.3) to the chat using the paperclip icon or `#`:

- `Adder.java`
- `Multiplier.java`
- `Divider.java`
- `Main.java`

Send this prompt:

```
Apply the Facade pattern to this code. The goal is that Main should not
import or name any of the concrete computation classes; it should depend
only on a single public Facade class in the calc package. Show me the
refactored files. Keep the program's output unchanged.
```

Compare Copilot's refactor to yours. In your notebook:

1. Did Copilot reduce the visibility of `Adder`, `Multiplier`, and `Divider` to package-private?
2. Did it introduce a single `Facade` class with one method per operation, the way you did?
3. Did it keep the original method names (`add`, `multiply`, `divide`) on the Facade, or did it choose different names?
4. Did it add anything you did not (a separate `Calculator` interface, factory methods, dependency injection setup)?
5. Did it preserve the integer-division zero-check in `Divider`? If yes, did it surface that check to the Facade in any way?
6. Was Copilot's output identical to yours when run, byte for byte?

The point of the comparison is not to declare a winner; it is to notice what design decisions Copilot makes by default. AI-generated refactors are typically *more decorated* than human-written ones (they tend to add interfaces, factories, and dependency injection even when these are not needed for the immediate problem). Whether that decoration is helpful or harmful depends on what the codebase needs.

### Step 6.2: Reflection questions

Answer in your notebook. These are open-ended; spend at least 10 minutes.

1. **The cost of the Facade.** You added a class and changed three others. In return, you reduced the surface area `Main` depends on from three classes to one. Is this a good trade? At what number of operations does it become a clear win? Could you imagine a `calc` package small enough that adding a Facade would be over-engineering?

2. **The two stretches.** Part 5 added a uniform dispatch method that takes operation names as strings. The Command pattern (described in the reference section below) does the same job with objects per operation. For each design, list one situation where it is the right answer and one situation where it is over-engineered.

3. **Open/Closed in practice.** Refactor exercises in textbooks tend to make Open/Closed look like an absolute virtue: "design so that you never have to modify existing code." In practice, full Open/Closed compliance has costs (more files, more indirection, more setup). When is partial Open/Closed (the Part 3 design) enough? When is full Open/Closed (the Command pattern in the reference) worth the cost?

4. **Behaviour-preserving refactors.** The litmus test for a refactor is that the program's output before and after is identical. What about the program's *internal* behaviour (memory layout, method count, thread safety, performance)? Are those allowed to change in a "behaviour-preserving" refactor? Where do you draw the line?

5. **Copilot's defaults.** Based on Step 6.1, what is Copilot's "house style" for a Java refactor? Does it tend to add interfaces and abstractions you did not ask for? Is that a feature (it is teaching you to write more flexible code) or a problem (it is adding complexity you do not need)? How would you tune the prompt to get the simpler refactor you actually wrote?

6. **What is missing?** This lab's `calc` package would not survive in real production code. List three things you would want to add before deploying it. (Hints: error handling, thread safety, logging, observability.)

---

## Reference: The Facade Pattern in One Picture

```
              Before                        After
        +-----------+                +---------------+
        |   Main    |                |     Main      |
        +-----------+                +---------------+
              |                              |
        +-----+-----+                        v
        |     |     |                +---------------+
        v     v     v                |    Facade     |   <-- the only public class
   +-------+ +---+ +-------+         +---------------+
   | Adder | |...| | Divider|             |    |    |
   +-------+ +---+ +-------+              v    v    v
                                     +-------+ +---+ +-------+
                                     | Adder | |...| | Divider|  (package-private)
                                     +-------+ +---+ +-------+
```

**Before:** Every client depends on every concrete class. N clients * M classes = N*M dependencies.

**After:** Every client depends on the Facade. The Facade depends on every concrete class. N clients * 1 Facade + 1 Facade * M classes = N + M dependencies.

The reduction from multiplication to addition is the structural payoff. It scales as both N (clients) and M (operations) grow.

---

## Reference: The Open/Closed Principle in This Lab

The Open/Closed Principle says "open for extension, closed for modification." This lab's three designs satisfy the principle to different degrees:

| Design | Adding a new operation requires editing... | Open/Closed score |
|--------|---------------------------------------------|-------------------|
| **Part 1 (no Facade)** | New class, plus every client that calls it | Weakest |
| **Part 3 (Facade with per-op methods)** | New class, plus the Facade (add field and method) | Better; clients are stable |
| **Part 5 (Facade with `calculate(String, int[])`)** | New class, plus a branch in the Facade's `calculate` method | Better; new client calls do not require Facade changes |
| **Reference (Command pattern, below)** | Just a new class plus a registry entry | Strongest |

Each row reduces the number of files that have to change when a new operation is added. The Command pattern is the only design where adding a new operation requires no modification of any existing code (just registering a new entry).

---

## Reference: The Command Pattern, the Textbook Version

The Command pattern (Gang of Four, 1994) turns each operation into an object. A simple implementation looks like this:

**`calc/Calculation.java`:**

```java
package calc;

interface Calculation {
    int apply(int[] args);
}
```

**`calc/Facade.java`** (modified to use a registry):

```java
package calc;

import java.util.HashMap;
import java.util.Map;

public class Facade {
    private final Map<String, Calculation> registry = new HashMap<>();

    public Facade() {
        registry.put("add",      args -> args[0] + args[1]);
        registry.put("multiply", args -> args[0] * args[1]);
        registry.put("divide",   args -> {
            if (args[1] == 0) throw new IllegalArgumentException("b must not be zero");
            return args[0] / args[1];
        });
    }

    public int calculate(String operationType, int[] args) {
        Calculation op = registry.get(operationType);
        if (op == null) {
            throw new IllegalArgumentException("Unknown operation: " + operationType);
        }
        return op.apply(args);
    }
}
```

Adding `subtract` is now a one-line change to `Facade`:

```java
registry.put("subtract", args -> args[0] - args[1]);
```

The `calculate` method itself does not change. In a larger system, the registry would be populated by an external configuration file or by classpath scanning, so even the registry initialization in the constructor becomes "extension" rather than "modification."

The tradeoffs vs. the Part 5 string-dispatch version:

| Tradeoff | String-dispatch (Part 5) | Command pattern (this reference) |
|----------|--------------------------|----------------------------------|
| Lines of code | ~10 in `Facade.calculate` | ~20 across `Calculation` and `Facade` |
| Adding an operation | Edit `calculate` (add an `if`) | Register a new entry (one line) |
| Operation-specific logic | Inline in `calculate` | Lives inside the operation's object |
| Reflection / configuration-driven | Hard to externalize | Easy to externalize |
| Readability for newcomers | Familiar `if`/`else` | Requires understanding the registry |

For a small, fixed set of operations, the string-dispatch version is simpler and clear. For a system where the set of operations grows (or where operations are loaded from a plugin system), the Command pattern earns its keep.

---

## Reference: Refactoring Etiquette

A few habits that distinguish a clean refactor from a sloppy one:

| Habit | What it means |
|-------|---------------|
| **Capture the baseline first** | Save the program's output before changing anything. The output is your contract; the refactor preserves it or fails. |
| **Run after every meaningful change** | A multi-step refactor should compile and run at each intermediate step. If step 7 breaks the build, you should not be on step 8. |
| **One refactoring at a time** | Do not mix "introduce Facade" with "rename methods" with "add thread safety" in the same change. Each kind of edit is reviewable on its own merits. |
| **Test the boundary cases** | The Part 3 refactor changed nothing about `Divider`'s zero-check. Did your refactor break it? Run `divide(8, 0)` and check that the exception still fires. |
| **Read your own diff before you commit** | What did you actually change? Did any change happen that you did not intend? Reviewing your own diff catches sloppy edits before others see them. |

These habits matter more than which pattern you applied. A clean refactor with a wrong-pattern-but-working result is more useful to a team than a right-pattern but-buggy result.

---

## Troubleshooting

**`error: cannot find symbol Adder` after Step 3.1.**
This is the expected and correct state. You removed `public` from `Adder`, and `Main.java` (which lives outside the `calc` package) can no longer see it. The fix is to continue to Step 3.3 and introduce the Facade.

**`error: the public type Adder must be defined in its own file`.**
Java requires that a `public` class live in a file matching its name. If you accidentally added `public` to the wrong file (for instance, made the `Facade` constructor public when there is already a public class declared), this error appears. Make sure each file has at most one `public` class, and that the public class's name matches the file name.

**The Run button does not appear above `main`.**
The Java extension has not finished indexing the project, or the Extension Pack for Java is not installed. Wait a moment for the "Java: Building..." indicator in the status bar to disappear; if it never does, install or enable the Extension Pack from the Extensions view (`Ctrl+Shift+X`).

**The refactored code compiles but the output is different from the baseline.**
The single most common cause is a typo in one of the Facade's forwarding methods (e.g., `multiplier.add(a, b)` instead of `multiplier.multiply(a, b)`). All three forwarding methods have similar shapes, and the compiler does not catch a misplaced one because every method has the same signature (`int op(int, int)`). Read each forwarding method out loud, comparing the field name to the method name.

**Copilot's refactor uses an interface `Calculator` that you did not have.**
This is the "Copilot adds decoration" pattern from Step 6.1. The interface is not wrong; it is just unnecessary for this small example. The reflection asks you to compare your simpler refactor to Copilot's more abstracted one and consider which is appropriate for the situation.

**Copilot kept the classes `public` and just wrapped them in a Facade.**
This is a partial refactor. The Facade is in place but the original direct-access path is still available. Ask Copilot to also reduce the visibility of the implementation classes: "Make `Adder`, `Multiplier`, and `Divider` package-private so they cannot be accessed from outside the `calc` package."

---

## Further Reading

- **Design Patterns: Elements of Reusable Object-Oriented Software** (Gamma, Helm, Johnson, Vlissides, 1994). The original Gang of Four book. The Facade chapter is short and explicit; the Command chapter is the canonical reference for the registry-based approach in the reference section.
- **Refactoring: Improving the Design of Existing Code** (Martin Fowler), 2nd edition. The book-length treatment of behaviour-preserving code transformations. The "Encapsulate" and "Hide Delegate" refactorings (chapter 7) are the named operations this lab applies.
- **Effective Java** (Joshua Bloch), 3rd edition. Item 15 ("Minimize the accessibility of classes and members") is the canonical argument for the visibility-reduction step in Part 3. Item 17 ("Minimize mutability") informs the use of `private final` in the Facade.
- **Refactoring Guru: Facade pattern** at <https://refactoring.guru/design-patterns/facade>. Free online walkthrough with diagrams and code samples in multiple languages.
- **The Open-Closed Principle (Bertrand Meyer, 1988; Robert C. Martin, 1996)**. The original statement is in Meyer's *Object-Oriented Software Construction*; Martin's paper "The Open-Closed Principle" is widely cited and freely available online.
