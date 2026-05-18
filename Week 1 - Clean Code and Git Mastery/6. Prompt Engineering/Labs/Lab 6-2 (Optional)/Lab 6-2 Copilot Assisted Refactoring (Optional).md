# Optional Lab 6-2: Refactoring a Monolithic Java Application with GitHub Copilot

**This is an optional lab. It is the same as Lab 3-1 but it illustrates how to do the refactoring using and AI Assistant**

> Note: Since this is an optional lab, it has not been tested in the VM environment so use is "as is".
> 
> This is primarily provided for your reference
> 
## Overview

One of the most common refactoring tasks in real codebases is taking a "blob" of tightly coupled code (UI, business logic, and data access all tangled together in one file) and decomposing it into clean, modular layers. This is not glamorous work, but it is the work that turns a prototype into a maintainable system.

In this lab you will start with a deliberately bad Java program: a small "Task Tracker" CLI that works correctly but breaks nearly every principle of structured design. You will use GitHub Copilot to first understand *why* it is bad, then drive a five-step refactoring that produces a clean, layered application with a domain layer, a repository layer, a service layer, and a thin UI layer.

You will work mostly in **Agent mode** because you are making real code changes, but you will switch to **Ask mode** for the explanation and design questions where you want analysis without edits.

**Estimated time:** 60 to 90 minutes
**Difficulty:** Intermediate

**Prerequisites:**

- A paid GitHub Copilot plan with Claude models available in the picker.
- VS Code with the GitHub Copilot Chat extension installed and authenticated.
- Claude Sonnet 4.6 selected in the chat model picker.
- A Java Development Kit (JDK 17 or later) installed and on your PATH (`javac --version` should print 17.x or higher).
- Basic familiarity with Java syntax and `javac` / `java` from the command line.
- Completion of an earlier Copilot lab (or equivalent familiarity with Copilot Chat modes).

---

## Learning Objectives

By the end of this lab, you will be able to:

1. Use Copilot in Ask mode to identify the design problems in a poorly structured program.
2. Use Copilot in Agent mode to drive a multi-step refactor one layer at a time, reviewing each change.
3. Apply five core refactoring patterns: encapsulation, elimination of global state, introduction of a repository abstraction, introduction of an application service layer, and separation of UI from domain.
4. Explain the rationale for each architectural layer (domain, infrastructure, application, presentation) and what depends on what.
5. Verify that a refactor preserves behaviour by exercising the application before and after.

---

## Part 1: Set Up the Workspace

### Step 1.1: Create the lab directory

In a terminal:

```bash
mkdir -p ~/refactor-lab
cd ~/refactor-lab
code .
```

VS Code opens the empty directory as a workspace. When prompted, click **Yes, I trust the authors**.

### Step 1.2: Create the starter file

Create a new file called `BadTaskApp.java` and paste the following content into it exactly as shown. Do not modify it yet. Save the file (`Ctrl+S`).

```java
import java.util.*;

class Task {
    // Public instance variables (no encapsulation)
    public String title;
    public boolean done;
    public int priority; // 1=high, 3=low
}

class BadTaskStore {
    // Global mutable state, no abstraction boundary
    public static List<Task> tasks = new ArrayList<>();
}

public class BadTaskApp {
    // Mixes UI, business logic, and data access in one place
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        System.out.println("Task Tracker (bad version)");
        while (true) {
            System.out.print("[a]dd, [l]ist, [d]one <idx>, [q]uit: ");
            String cmd = sc.nextLine().trim();

            if (cmd.equals("a")) {
                Task t = new Task();
                System.out.print("title: ");
                t.title = sc.nextLine();           // direct field access
                System.out.print("priority (1..3): ");
                t.priority = Integer.parseInt(sc.nextLine());
                t.done = false;
                BadTaskStore.tasks.add(t);         // store accessed directly
            } else if (cmd.equals("l")) {
                int i = 0;
                for (Task t : BadTaskStore.tasks) {
                    System.out.println(i + ": [" + (t.done ? "x" : " ") + "] "
                            + t.title + " (p" + t.priority + ")");
                    i++;
                }
            } else if (cmd.startsWith("d")) {
                // UI directly mutates data structure by index
                String[] parts = cmd.split("\\s+");
                if (parts.length > 1) {
                    int idx = Integer.parseInt(parts[1]);
                    if (idx >= 0 && idx < BadTaskStore.tasks.size()) {
                        BadTaskStore.tasks.get(idx).done = true; // direct field write
                    }
                }
            } else if (cmd.equals("q")) {
                break;
            }
        }
        sc.close();
    }
}
```

### Step 1.3: Confirm Copilot is ready

1. Open the Chat view (`Ctrl+Alt+I`).
2. Confirm the model picker reads **Claude Sonnet 4.6**.
3. Switch the chat mode dropdown to **Ask**. You will start in Ask mode and switch to Agent mode in Part 3.

### Step 1.4: Build and run the starter code

Before changing anything, confirm that the bad version actually works. The whole point of refactoring is to preserve behaviour, so you need a baseline.

In the VS Code terminal (`` Ctrl+` ``):

```bash
javac BadTaskApp.java
java BadTaskApp
```

You should see the prompt. Add two tasks, list them, mark one done, list again, then quit:

```
[a]dd, [l]ist, [d]one <idx>, [q]uit: a
title: buy groceries
priority (1..3): 2
[a]dd, [l]ist, [d]one <idx>, [q]uit: a
title: write lab report
priority (1..3): 1
[a]dd, [l]ist, [d]one <idx>, [q]uit: l
0: [ ] buy groceries (p2)
1: [ ] write lab report (p1)
[a]dd, [l]ist, [d]one <idx>, [q]uit: d 0
[a]dd, [l]ist, [d]one <idx>, [q]uit: l
0: [x] buy groceries (p2)
1: [ ] write lab report (p1)
[a]dd, [l]ist, [d]one <idx>, [q]uit: q
```

The program compiles, runs, and produces correct output. Yet it is bad code. The rest of the lab is about why, and what to do about it.

### Step 1.5: Create a lab notebook file

Create a new file `findings.md` in the workspace. You will record your analyses and Copilot's responses here as you go. Start it with:

```markdown
# Refactoring Lab Notebook

## Part 2: Diagnosis

## Part 3: Refactoring

## Part 4: Design questions

## Part 5: Verification
```

Save it.

---

## Part 2: Diagnose the Problems (Ask Mode)

Before you change a single line of code, you need to understand precisely what is wrong with it. Refactoring without a clear diagnosis is just rearranging deck chairs.

Make sure `BadTaskApp.java` is the active editor tab and you are in **Ask** mode.

### Question 2.1: First-pass critique

In the Chat view, type:

```
#file:BadTaskApp.java This file works correctly but is considered poorly
designed. List every design problem you see. For each one, name the
principle being violated and explain in one sentence why it matters in
a larger codebase.
```

**What to look for in the response:**
- `Task` exposes public mutable fields. Violates **encapsulation**. Any caller can put the object into an invalid state.
- `BadTaskStore.tasks` is a `public static` mutable collection. Violates **information hiding** and creates **global mutable state**, which is impossible to test in isolation and breaks at the first attempt at concurrency.
- `BadTaskApp.main` reads input, parses commands, validates data, writes to the store, and prints output, all in one method. Violates **single responsibility principle**: the UI knows about the storage and about the domain rules.
- Magic numbers: priority values 1, 2, 3 with the meaning encoded only in a comment. Violates **self-documenting code**. A future reader has to find the comment to know what `priority = 2` means.
- The UI mutates a `Task` field directly: `BadTaskStore.tasks.get(idx).done = true`. Violates the **Law of Demeter** and tells you the layers are not separated at all.
- No input validation. Priority outside 1-3 is accepted silently. Empty titles are accepted. Negative or out-of-range indexes in `d` are caught by one specific check but malformed input crashes the program.

Copy the response into your notebook under "Part 2."

### Question 2.2: What are the responsibilities, mixed together?

```
The starter file has three responsibilities tangled together: domain logic,
data access, and user interface. For each responsibility, identify the
specific lines or blocks that belong to it. Then describe what would
have to change if I wanted to swap one of those responsibilities (for
example, replace the CLI with a web UI, or replace the in-memory store
with a database).
```

**What to look for in the response:**
- **Domain logic**: the `Task` class fields (title, done, priority), the priority-meaning comment, the implicit rule that priority is 1-3, the implicit rule that new tasks start undone.
- **Data access**: the `BadTaskStore.tasks` collection, the `add`, `get(idx)`, and `size()` calls, the index-based addressing model.
- **User interface**: the `Scanner`, the `System.out.print` calls, the command parsing (`a`, `l`, `d`, `q`), the formatted output line.
- To swap the CLI for a web UI: you would have to rewrite the entire `main` method because the domain and data access logic is inlined into it. There is no service to call from a controller.
- To swap the in-memory store for a database: you would have to find every place that touches `BadTaskStore.tasks` (currently in three different command branches in `main`) and rewrite each one. There is no central abstraction to replace.

### Question 2.3: Sketch the target architecture

```
Sketch the architecture you would refactor this code into. Name each
layer, describe its responsibility in one sentence, and say what each
layer is allowed to know about (which other layers it depends on).
```

**What to look for in the response:**
- **Domain layer** (or *business logic* layer): the `Task` entity and the `Priority` concept. Knows nothing about storage, UI, or frameworks.
- **Infrastructure layer** (or *data access* layer): the `TaskRepository` interface and an `InMemoryTaskRepository` implementation. Depends on the domain layer (it stores `Task` objects) but knows nothing about UI or services.
- **Application layer** (or *service* layer): a `TaskService` that orchestrates use cases. Depends on the domain layer and on the `TaskRepository` interface (not the implementation). Knows nothing about UI.
- **Presentation layer** (or *UI* layer): the `Main` class with the CLI loop. Depends on the application layer (`TaskService`) only. Does not depend on the repository implementation or directly on domain types beyond what `TaskService` returns.

This is a layered architecture, sometimes called *hexagonal*, *clean*, or *onion* depending on who is teaching it. The key idea is the **dependency direction**: outer layers depend on inner layers, never the reverse. The domain knows nothing about anything else.

Sketch this layered diagram in your notebook. You will refer back to it as you refactor.

---

## Part 3: Drive the Refactor (Agent Mode)

You now know what you want. Time to make it happen.

Switch the chat mode dropdown to **Agent**. Agent mode lets Copilot read files, propose edits across multiple files, and run commands. Each edit still appears as a Keep / Undo diff that you review before accepting.

You will execute the refactor in five steps, matching the five-step plan from the original lab. After each step, build the project to confirm it still compiles, and where useful, run it to confirm it still behaves correctly. **Do not skip the build step.** A refactor that does not compile is not a refactor.

### Step 3.1: Encapsulate the domain (extract `Task` and create `Priority`)

In Agent mode, type:

```
#file:BadTaskApp.java I want to refactor this in five steps. Step 1 of 5:
Encapsulate the Task class. Specifically:

1. Move the Task class into its own file Task.java.
2. Make its fields private and final where appropriate (id and the
   underlying values that should not change after construction).
3. Add a constructor that validates its inputs: non-null trimmed title
   that is not empty, non-null priority.
4. Add behaviour methods: markDone(), rename(String), changePriority(Priority).
5. Add an id field (int) that is assigned in the constructor.
6. Replace the raw int priority with a new Priority enum.
7. Create the Priority enum in its own file Priority.java with values
   HIGH(1), MEDIUM(2), LOW(3), a level() accessor, and a static fromInt(int)
   that throws IllegalArgumentException on invalid input.
8. Update BadTaskApp.java to use the new Task and Priority where it
   previously used the public fields. Keep the program compiling and
   behaving the same as before.

Show me each file change as a diff before applying. I will Keep or Undo
each one.
```

Press Enter. Copilot will propose:
- A new file `Priority.java` with the enum.
- A new file `Task.java` with the encapsulated class.
- Edits to `BadTaskApp.java` to construct `Task` through the constructor instead of setting fields, and to convert the int priority into a `Priority` via `Priority.fromInt`.

Review each diff carefully. **Keep** the changes that match the plan; **Undo** anything that goes beyond the step (Copilot occasionally tries to do steps 2-5 at the same time; if it does, undo those parts and ask it to stick to step 1).

**Build to confirm:**

```bash
javac *.java
```

If the build succeeds, run the program (`java BadTaskApp`) and confirm the same add/list/done flow from Step 1.4 still works. The user-visible behaviour should be identical.

> **Why is this step first?** The domain is the foundation. Every other layer references it. Getting the domain correct now means the rest of the refactor has clean types to work with. If you tried to extract the repository before encapsulating the entity, the repository would be defined in terms of the bad type and you would have to redo it.

### Step 3.2: Remove global state (introduce `TaskRepository`)

```
Step 2 of 5: Remove the global mutable state.

1. Create a new file TaskRepository.java containing an interface with
   these methods:
     Task add(String title, Priority priority);
     List<Task> list();
     Optional<Task> findById(int id);
     boolean markDone(int id);
2. Create a new file InMemoryTaskRepository.java that implements
   TaskRepository. Use a LinkedHashMap<Integer, Task> internally so the
   list preserves insertion order. Generate ids starting at 1.
3. Delete the BadTaskStore class entirely.
4. Update BadTaskApp.java to instantiate InMemoryTaskRepository and call
   it through the TaskRepository interface (declared variable type
   should be the interface, not the concrete class).
5. The UI logic in main still works the same way, just through the
   repository instead of the global list. Replace index-based access
   (BadTaskStore.tasks.get(idx)) with id-based access (repo.markDone(id),
   repo.findById(id)). The "d" command now takes an id, not an index,
   but the user prompt can stay the same for now.

Show diffs one file at a time.
```

Press Enter. Copilot will create the two new files and rework `BadTaskApp.java`. Review each diff.

**Note the architectural shift:** the UI loop in `main` is now talking to an *interface* (`TaskRepository`) instead of a global static field. This is the change that makes future swaps (database, REST API, mock for tests) possible without touching the UI.

**Build and run again** before proceeding. The user-visible behaviour should still be the same (with the caveat that `d <id>` now uses ids starting from 1 instead of indexes starting from 0; verify the list output to see the ids).

### Step 3.3: Introduce the application service layer

```
Step 3 of 5: Introduce a TaskService layer.

1. Create a new file TaskService.java containing a class that takes a
   TaskRepository in its constructor and exposes use-case methods:
     Task createTask(String title, int priorityInt)
       (this method converts the raw int to a Priority via
       Priority.fromInt and delegates to the repo)
     List<Task> listTasks()
     boolean completeTask(int id)
2. Update BadTaskApp.java to instantiate a TaskService that wraps the
   repository, and call the service from the CLI loop instead of
   calling the repository directly.
3. The CLI should now know about TaskService and not about the
   repository. The wiring (which repository implementation to use) is
   the only place main touches the repository class.

Show diffs.
```

Press Enter and review the diffs.

**Why does this layer exist?** Right now the service feels like a thin wrapper around the repository. In a larger app this is where transactions begin and end, where authorization is checked, where multiple repositories are coordinated, and where logging and metrics live. Introducing the layer now means those concerns have a home when they arise later.

**Build and run.**

### Step 3.4: Separate the UI into its own class

```
Step 4 of 5: Move the CLI out of BadTaskApp into a properly named class.

1. Create a new file Main.java with a Main class containing the main()
   method.
2. Move the entire CLI loop from BadTaskApp.java into Main.java.
3. Delete BadTaskApp.java.
4. The wiring (instantiate repository, wrap in service, run the CLI)
   stays in Main.main.
5. Improve the printed output so that it includes the task id (so users
   know what number to pass to "d"). For example:
     "1: [ ] buy groceries (p2)"
   instead of the previous index-based format.

Show diffs.
```

Press Enter and review.

**Build:**

```bash
javac *.java
ls -la *.class
```

You should now have class files for `Main`, `Task`, `Priority`, `TaskRepository`, `InMemoryTaskRepository`, and `TaskService`. The old `BadTaskApp.class` should be gone (delete it manually if Copilot did not remove it).

**Run with the new entry point:**

```bash
java Main
```

### Step 3.5: Tighten input handling

```
Step 5 of 5: Tighten input handling in the CLI.

1. Wrap the priority parsing in a try/catch that prints a helpful error
   message and returns to the prompt if the input is not 1, 2, or 3
   (catch IllegalArgumentException from Priority.fromInt and
   NumberFormatException from Integer.parseInt).
2. Wrap the "d <id>" parsing similarly. If the id is missing or not an
   integer, print a helpful error and return to the prompt.
3. If completeTask returns false (no such id), print "No such task id."
4. If the user enters an unknown command, print "Unknown command."
5. If list is empty, print "(no tasks)" instead of nothing.

Show diffs.
```

Press Enter, review, and Keep the changes.

**Build and run the final version.** Try invalid inputs to confirm the new error handling works:

```
[a]dd, [l]ist, [d]one <id>, [q]uit: a
title:
priority (1..3): 5
Error: Priority must be 1..3
[a]dd, [l]ist, [d]one <id>, [q]uit: d
Usage: d <id>
[a]dd, [l]ist, [d]one <id>, [q]uit: d xyz
Task id must be an integer.
[a]dd, [l]ist, [d]one <id>, [q]uit: d 999
No such task id.
[a]dd, [l]ist, [d]one <id>, [q]uit: l
(no tasks)
[a]dd, [l]ist, [d]one <id>, [q]uit: q
```

The refactor is complete. You now have six files: `Priority.java`, `Task.java`, `TaskRepository.java`, `InMemoryTaskRepository.java`, `TaskService.java`, and `Main.java`.

---

## Part 4: Design and Architecture Questions (Ask Mode)

Switch back to **Ask** mode. The refactor is done; now you reflect on what it produced.

### Question 4.1: Why an interface and an implementation?

```
#file:TaskRepository.java #file:InMemoryTaskRepository.java
Why did the refactor split storage into an interface (TaskRepository)
and a separate implementation (InMemoryTaskRepository)? Couldn't we
just use the InMemoryTaskRepository class directly throughout the
codebase? Name three concrete benefits of having the interface and
one cost.
```

**What to look for in the response:**
- **Benefit 1 (substitutability):** A future `DatabaseTaskRepository` or `FileTaskRepository` can be dropped in without changing `TaskService` or `Main`. The wiring point is one line of code in `Main`.
- **Benefit 2 (testability):** Unit tests for `TaskService` can use a fake or mock `TaskRepository` that records calls and returns canned values. No database, no file system, no shared state between tests.
- **Benefit 3 (clearer contract):** The interface lists exactly what the service layer needs from storage. Anything outside that list (e.g., direct access to the underlying map) is impossible by construction.
- **Cost:** A small amount of indirection and an extra file. For a tiny app this is mild overengineering; for any app that lives more than six months, it pays for itself the first time you want to test or swap storage.

### Question 4.2: The dependency direction

```
#file:Main.java #file:TaskService.java #file:InMemoryTaskRepository.java
#file:Task.java #file:Priority.java

Look at the import statements in each of these files and tell me which
file imports from which. Draw the dependency graph. Then explain why
the graph looks the way it does, and what would be wrong if any of the
arrows went the other way.
```

**What to look for in the response:**
- `Main` imports `TaskService`, `TaskRepository`, `InMemoryTaskRepository`, `Task`, `Priority`.
- `TaskService` imports `TaskRepository`, `Task`, `Priority`. **Does not import `InMemoryTaskRepository`.**
- `InMemoryTaskRepository` imports `TaskRepository`, `Task`, `Priority`.
- `TaskRepository` (interface) imports `Task`, `Priority`.
- `Task` imports `Priority`.
- `Priority` imports nothing from this project.
- **The graph points inward.** The domain (`Priority`, `Task`) is at the centre and imports nothing. The infrastructure and application layers both depend on the domain. The UI sits at the outside and depends on everything else.
- If `Task` imported `TaskRepository`, the domain would know about storage, which would couple every test of `Task` to the repository abstraction. Same problem for any other reversal: outer layers should depend on inner layers, never the reverse.

### Question 4.3: Why an enum instead of an int?

```
The refactor replaced the raw int priority with a Priority enum. Beyond
"magic numbers are bad," what concrete bugs does the enum prevent that
the int allowed? Give me three examples that would compile and run with
the int version but would be caught at compile time with the enum.
```

**What to look for in the response:**
- **Example 1:** `task.priority = 0` or `task.priority = 99`. The int version silently accepted any value; the enum rejects anything other than HIGH, MEDIUM, or LOW.
- **Example 2:** A typo: `task.priority = 2` when the developer meant `priority = 1` (high). With the enum, the developer writes `Priority.HIGH` and there is no number to mistype.
- **Example 3:** Comparing priorities: `if (task.priority < otherTask.priority)`. The int version makes "less than" mean "higher priority" (since HIGH is 1), which is the opposite of what most readers will guess. The enum forces the comparison to go through an explicit method (e.g., `compareTo` or a named `isHigherThan`) where the semantics can be made obvious.

### Question 4.4: Where would you add a feature?

```
Suppose I want to add three features. For each one, tell me exactly
which files I would need to modify, and which would not change. Explain
why.

Feature A: persist tasks to a JSON file so they survive program restart.
Feature B: add a "delete task by id" command.
Feature C: replace the CLI with a REST API using something like Spark or
           Javalin.
```

**What to look for in the response:**
- **Feature A (JSON persistence):** Add a new `JsonFileTaskRepository.java` implementing `TaskRepository`. Change one line in `Main.java` to wire it in. **Do not touch:** `Task`, `Priority`, `TaskService`, `TaskRepository`, `InMemoryTaskRepository`. This is the payoff of the repository abstraction.
- **Feature B (delete):** Add a `delete(int id)` method to `TaskRepository`, implement it in `InMemoryTaskRepository`, add a `deleteTask(int id)` to `TaskService`, add a `d <id>` (or rename `done` to something else and use a new key) handler in `Main`. Four files touched, in clear order from inside out.
- **Feature C (REST API):** Replace `Main.java` with a new entry point that wires the same `TaskService` into a REST framework. **Do not touch:** `Task`, `Priority`, `TaskRepository`, `InMemoryTaskRepository`, `TaskService`. This is the payoff of the service abstraction. The CLI was just one possible front-end; the service is the real API.

The contrast with the original `BadTaskApp.java` is stark: every one of those features would have required surgery on the one God-class file in the old version.

---

## Part 5: Verify Your Understanding

You have built a model of how the refactored application is organized. Test that model.

### Step 5.1: Predict before you run

Without running the code, predict the output for this session:

```
a
review pull request
1
a
deploy to staging
1
l
d 2
l
q
```

Write your prediction in your notebook. Be specific: what are the ids? What priority labels appear? What format is the output line?

### Step 5.2: Run it

```bash
java Main
```

Enter the inputs above one at a time and compare the output to your prediction. If anything is different, do not assume the program is wrong. Re-read the relevant file (probably `Main.java` for output format, or `TaskService.java` for behaviour) and figure out what you got wrong.

### Step 5.3: Behavioural equivalence with the original

You started this lab by running `BadTaskApp` and adding tasks, listing them, marking done, listing again, and quitting. Do the same sequence now with `Main`. The output should be:

- Almost identical for `add`, `list`, and `quit`.
- Different only in that `d` now takes an id (1, 2, 3, ...) instead of an index (0, 1, 2, ...). The list output now shows ids instead of indexes.

If anything else is different, that is a behavioural regression. Use Copilot in Ask mode to find it:

```
The original BadTaskApp printed tasks in the format
  "0: [x] buy groceries (p2)"
but the refactored version prints
  "1: [x] buy groceries (p2)"

Beyond the index-to-id change, are there any other behavioural
differences between the original and the refactored version that I
should know about?
```

### Step 5.4: A small extension

Now that the architecture is in place, try adding **Feature B from Question 4.4 (delete a task)**. Use Copilot in Agent mode and a single well-formed prompt:

```
Add a "delete a task by id" feature. The CLI command should be "x <id>"
(for "x out"). Update TaskRepository, InMemoryTaskRepository, TaskService,
and Main accordingly. Validate input the same way the existing commands
do. Show me the diffs.
```

Notice that the change is mechanical and stays within layer boundaries: a method added to each of three layers, and a new command branch in the UI. Compare this to what the same feature would have looked like in `BadTaskApp.java`. **This is what refactoring buys you.**

---

## Part 6: Reflection

Answer the following in your lab notebook:

1. **Refactoring vs rewriting.** This lab refactored the original code one step at a time, building between each step. You could instead have read the bad code once, then written the refactored version from scratch. What did the incremental approach gain you? What did it cost? When would you choose one over the other?

2. **What did you let Copilot decide?** Across the five refactor steps, what choices were yours and what did Copilot fill in? For example, did you specify that `Priority` should be an enum, or did Copilot suggest it? Does that matter?

3. **The role of the build step.** Each refactor step ended with `javac *.java`. Why did the lab insist on that, even when the change seemed safe? What does the compiler catch that a code review or a Copilot diff review would not?

4. **Verifying Copilot's edits.** Pick one diff Copilot produced during Part 3. Explain how you verified it before clicking Keep. Did you read every line? Did you trust the structure and spot-check the details? What would have caught a subtle bug?

5. **The five-step framework.** The lab walked through five canonical refactor steps: encapsulate the domain, remove globals, introduce a service layer, separate the UI, tighten input handling. Could the same framework be applied to a non-Java program (say, a Python script or a C# console app)? Sketch how you would adapt it.

6. **When to stop.** At what point would you say "the refactor is good enough" and move on? Could this code be improved further? Where would you draw the line for a real project?

---

## Reference: Refactor Step Plan

The five-step plan used in this lab generalizes to many "blob" codebases. Keep it for future use.

| Step | Pattern | Output |
|------|---------|--------|
| 1 | **Encapsulate the domain.** Turn anaemic data classes into entities with validated constructors and behaviour methods. Replace raw ints and strings with enums and value types. | Pure domain classes with no I/O dependencies. |
| 2 | **Remove global state.** Replace static collections with a repository interface and at least one implementation. | A storage abstraction the rest of the code talks to. |
| 3 | **Introduce a service layer.** Extract use-case orchestration from the UI into a service that depends on the domain and the repository interface. | A façade that any UI can call. |
| 4 | **Separate the UI.** Move the entry point out of the monolith into its own class that only does I/O and command parsing. | A UI that knows nothing about storage or domain rules. |
| 5 | **Tighten input handling.** Catch invalid inputs at the boundary, validate against the domain rules in the service, and return clear error messages to the UI. | A program that does not crash on bad input. |

---

## Reference: Useful Prompt Patterns for Refactoring

| Pattern | Example wording | When to use |
|---------|-----------------|-------------|
| **Diagnose first** | "This code works but is considered poorly designed. List every design problem and the principle it violates." | Before any refactor. Without a clear diagnosis, you risk making things worse. |
| **Plan before edit** | "Sketch the architecture you would refactor this into. Name each layer and its responsibility." | Get the target shape on paper before changing any code. |
| **One step at a time** | "Step N of M: do exactly this, no more. Show diffs one file at a time." | The single most important prompt pattern for refactoring. Big-bang refactors fail. |
| **Compile after every step** | (Not a prompt, a habit.) `javac *.java` (or equivalent) between every step. | A refactor that does not compile is not a refactor. |
| **Predict the change surface** | "If I added feature X, which files would change and which would not?" | Tests the architecture. If "all of them" is the answer, the architecture is not done. |
| **Before/after behaviour check** | "Beyond the change I requested, are there any behavioural differences between the original and the new version?" | Catches unintended consequences of refactor steps. |

---

## Troubleshooting

**Copilot tried to do all five refactor steps at once.**
Click **Undo** on any diff that goes beyond the current step, then re-send the prompt with stronger wording: "Do ONLY step 1. Do NOT introduce a repository, service, or new Main class in this step." If it still over-reaches, switch to Ask mode and ask Copilot to outline the step's changes file by file before you switch back to Agent mode and ask for the edits.

**The build fails after a refactor step.**
Do not press on. Read the compile error and either fix it by hand or paste it into Copilot Chat: "After applying these changes, javac reports the following error: [paste]. Show me the fix." The error message almost always points at one missing import, one renamed method, or one type mismatch.

**The refactored program behaves differently from the original.**
The most common cause is the index-to-id change in step 2. Beyond that, look for off-by-one errors in iteration, dropped null checks, or eager exceptions where the original silently absorbed them. Use Question 5.3's "are there any other behavioural differences" prompt.

**Copilot generated code that uses Java features your JDK does not support.**
Check your JDK version with `javac --version`. The reference solution uses switch expressions (`case 1 -> HIGH;`) which require JDK 14 or later. If you are on JDK 11 or earlier, ask Copilot: "Rewrite this without switch expressions, targeting Java 11."

**You ended up with a circular import.**
This is an architectural smell. Stop and go back to Question 4.2's dependency graph. The fix is almost always to move a type from an outer layer into an inner one, or to introduce a new interface that breaks the cycle.

---

## Further Reading

- Refactoring (Martin Fowler), 2nd edition. The canonical reference for incremental code transformation.
- Clean Architecture (Robert C. Martin). On the dependency-inward principle that this lab applied.
- Effective Java (Joshua Bloch), 3rd edition. Items 16 (encapsulation) and 18 (composition over inheritance) are directly relevant.
- Hexagonal Architecture (Alistair Cockburn, original paper): <https://alistair.cockburn.us/hexagonal-architecture/>
- GitHub Copilot documentation on Agent mode: <https://code.visualstudio.com/docs/copilot/chat/chat-agent-mode>
