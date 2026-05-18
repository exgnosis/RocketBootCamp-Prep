# Lab 3-1: Refactoring a Monolithic Java Application

## Overview

One of the most common tasks in real codebases is taking a "blob" of tightly coupled code (UI, business logic, and data access all tangled together in one file) and decomposing it into clean, modular layers. This is not glamorous work, but it is the work that turns a prototype into a maintainable system.

In this lab you will start with a deliberately bad Java program: a small "Task Tracker" CLI that works correctly but breaks nearly every principle of structured design. You will read it, diagnose its problems, and refactor it yourself, one step at a time, into a clean four-layer application: a domain layer, a repository layer, an application service layer, and a thin UI layer.

**This is a hands-on exercise.** You will write the new code by hand, compile it yourself, and run it yourself. The point is to feel where the friction is in each refactoring step, to make the small decisions (what to name a method, where to put validation, when to introduce a new file) that an AI assistant would otherwise make for you, and to come away with the muscle memory that lets you recognize and execute the same pattern on any future codebase.

A companion lab (**Lab 6-2: Refactoring with GitHub Copilot**) walks through the same refactor with an AI assistant. The recommended sequence is to do this lab first, then redo the refactor with Copilot, and compare the two experiences.

>Note. There is a reference refactoring supplied but your refactoring my differ slightly in some details. Compare thoe differences and decide which version is better, it either one is, and why.

**Estimated time:** 90 to 120 minutes
**Difficulty:** Intermediate

**Prerequisites:**

- A Java Development Kit (JDK 17 or later) installed and on your PATH (`javac --version` should print 17.x or higher).
- A text editor or IDE you are comfortable with (VS Code, IntelliJ IDEA, Eclipse, or plain text + terminal all work).
- Comfort with Java syntax: classes, interfaces, enums, generics, collections, exceptions.
- Familiarity with `javac` and `java` from the command line.

---

## Learning Objectives

By the end of this lab, you will be able to:

1. Identify the design problems in a poorly structured program and name the principle each one violates.
2. Sketch a target architecture before changing any code, and use it to guide the refactor.
3. Apply five core refactoring patterns: encapsulation, elimination of global state, introduction of a repository abstraction, introduction of an application service layer, and separation of UI from domain.
4. Refactor in small steps, building and testing after each one, so a broken build never lasts more than a few minutes.
5. Verify that a refactor preserves behaviour by exercising the application before and after.

---

## Part 1: Set Up the Workspace

### Step 1.1: Create the lab directory

In a terminal:

```bash
mkdir -p ~/refactor-lab
cd ~/refactor-lab
```

### Step 1.2: Create the starter file

Create a new file called `BadTaskApp.java` with the following content. Save it.

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

### Step 1.3: Build and run the bad version

Before changing anything, confirm that the bad version actually works. The whole point of refactoring is to preserve behaviour, so you need a baseline you can compare against later.

```bash
javac BadTaskApp.java
java BadTaskApp
```

You should see the prompt. Run through this exact session and write down the output you see:

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

### Step 1.4: Create a lab notebook

Create a file `notebook.md` in the workspace. You will record your diagnosis, decisions, and observations here as you work. Start it with:

```markdown
# Refactoring Lab Notebook

## Part 2: Diagnosis

## Part 3: Refactoring decisions

## Part 5: Verification
```

---

## Part 2: Diagnose the Problems

Before you change a single line of code, you need to understand precisely what is wrong with it. Refactoring without a clear diagnosis is just rearranging deck chairs.

Read the entire `BadTaskApp.java` slowly, then answer these questions in your notebook. Do not look ahead to Part 3 yet. Spend at least 10 minutes on this.

### Question 2.1: What design problems do you see?

For each problem you find, write:
1. A short description of the problem.
2. The principle being violated (encapsulation, single responsibility, information hiding, separation of concerns, etc.).
3. A one-sentence explanation of why it would matter in a larger codebase.

You should find at least **six distinct problems**. If you find fewer, read the file again.

> When you are done, expand the "Reference: what you should have found" section at the end of Part 2 to compare against your own list. Do not peek before you have written your own list.

### Question 2.2: What are the mixed responsibilities?

The `main` method does three different jobs that ought to be separated. Identify the specific lines in `main` that belong to each of these three jobs:

1. **Domain logic** (the rules of what a task is, what valid priorities are, how marking-done works).
2. **Data access** (storing, retrieving, and modifying the collection of tasks).
3. **User interface** (prompting, reading input, parsing commands, printing output).

Highlight or annotate these in your copy of the file. You will use this annotation to guide the refactor.

### Question 2.3: Sketch the target architecture

Before you write a single line of new code, draw the architecture you will refactor into. On paper or in your notebook, sketch a diagram with four layers and answer for each one:

1. What is the layer's name?
2. What is its single responsibility, in one sentence?
3. What classes or types will it contain?
4. Which other layers is it allowed to depend on?

A good answer will have a domain layer (Task, Priority), an infrastructure or data access layer (TaskRepository interface + InMemoryTaskRepository implementation), an application service layer (TaskService), and a presentation layer (Main, the CLI). Dependencies point inward: the UI depends on the service, the service depends on the repository interface and the domain, the repository implementation depends on the domain, the domain depends on nothing.

If your sketch does not look roughly like that, do not panic. The refactor will guide you toward it step by step.

### Reference: what you should have found

After you have written your own diagnosis, compare to this list. You should have identified at least these issues:

1. **Public mutable fields on `Task`.** Violates encapsulation. Any caller can put a `Task` into an invalid state (e.g., `priority = 99`, `title = null`).
2. **`BadTaskStore.tasks` is a `public static` mutable collection.** Global mutable state. Impossible to test in isolation. Breaks at the first attempt at concurrency.
3. **`main` does I/O, command parsing, validation, storage, and output all in one method.** Violates single responsibility. The UI knows about the storage implementation and about the domain rules.
4. **The UI mutates a domain object's field directly:** `BadTaskStore.tasks.get(idx).done = true`. Violates the Law of Demeter and confirms the layers are not separated at all.
5. **Magic numbers for priority** (1, 2, 3). The meaning is encoded only in a comment. A reader has to find the comment to know what `priority = 2` means.
6. **No validation.** Priority outside 1-3 is accepted silently. Empty or null titles are accepted. `Integer.parseInt` on bad input throws an uncaught `NumberFormatException` that crashes the program.
7. **Index-based addressing exposes implementation details.** The user types `d 0` because the storage happens to be an `ArrayList`. If we switch to a `HashMap` or a database, the meaning of "0" changes or disappears entirely.

If you found problems that are not on this list, that is fine. The list is a floor, not a ceiling.

---

## Part 3: Refactor in Five Steps

You will now execute the refactor in five steps. **After every step, run `javac *.java` to confirm the project still compiles, and run the program to confirm the behaviour is still correct.** A refactor that does not compile is not a refactor. A refactor that breaks behaviour is a regression.

Keep your notebook open. After each step, write a one-sentence note about anything that surprised you, or any decision you had to make that the lab did not specify.

### Step 3.1: Encapsulate the domain

**Goal:** Replace the anaemic `Task` class with a proper domain entity. Introduce a `Priority` enum so the magic numbers go away.

Create two new files in the same directory:

**`Priority.java`** is an enum with three values, each carrying its numeric level. It needs:
- Three constants: `HIGH(1)`, `MEDIUM(2)`, `LOW(3)`.
- A private `int level` field, set in the constructor.
- A `level()` accessor that returns the int.
- A static `fromInt(int n)` method that returns the matching enum value, or throws `IllegalArgumentException` for anything other than 1, 2, or 3.

**`Task.java`** is the domain entity. It needs:
- Four private fields: an `int id`, a `String title`, a `Priority priority`, and a `boolean done`.
- The `id` should be `final` (assigned in the constructor and never changes).
- A constructor `Task(int id, String title, Priority priority)` that validates its arguments:
  - `title` is not null, is trimmed, and is not empty after trimming.
  - `priority` is not null.
- Read-only accessors: `getId()`, `getTitle()`, `getPriority()`, `isDone()`.
- A `markDone()` method that sets the done flag to true.
- A `rename(String newTitle)` method that validates and updates the title.
- A `changePriority(Priority p)` method that validates and updates the priority.

Use `Objects.requireNonNull` for non-null checks and throw `IllegalArgumentException` for empty titles.

Now update `BadTaskApp.java`:
- Remove the old `Task` class definition from the top of the file (since it is now in its own file).
- In the `a` command, instead of `Task t = new Task(); t.title = ...; t.priority = ...;`, construct the task through the new constructor: `Task t = new Task(nextId++, title, Priority.fromInt(priorityInt));`. You will need a local `int nextId = 1;` somewhere reasonable for now (this is temporary; it goes away in Step 3.2).
- Wrap the priority parse and `Priority.fromInt` call in a try/catch so invalid input prints an error and returns to the prompt instead of crashing.
- In the `l` command, replace `t.done`, `t.title`, `t.priority` with the new accessors: `t.isDone()`, `t.getTitle()`, `t.getPriority().level()`.
- In the `d` command, replace `BadTaskStore.tasks.get(idx).done = true` with `BadTaskStore.tasks.get(idx).markDone()`.

**Build and run.** Confirm the same add/list/done sequence from Step 1.3 still works.

> **Reflection:** Try the bad input now. What happens if you enter priority `5`? What happens if you enter an empty title? The constructor catches these but the CLI still crashes because we have not yet wrapped the construction in a try/catch. That is fine; we tighten input handling in Step 3.5.

### Step 3.2: Remove the global mutable state

**Goal:** Replace the `BadTaskStore` static collection with a proper repository abstraction.

Create two new files:

**`TaskRepository.java`** is the interface. It declares four methods:

```java
public interface TaskRepository {
    Task add(String title, Priority priority);
    List<Task> list();
    Optional<Task> findById(int id);
    boolean markDone(int id);
}
```

Note the design choices here:
- `add` takes the title and priority and returns the constructed `Task` (because the repository owns id assignment).
- `list` returns a `List<Task>` (a snapshot, not a live view into the storage).
- `findById` returns `Optional<Task>` so callers cannot accidentally NPE on a missing id.
- `markDone` returns `boolean` so callers know whether the id was found.

**`InMemoryTaskRepository.java`** implements the interface. It needs:
- A private `Map<Integer, Task>` field. Use `LinkedHashMap` so list output preserves insertion order.
- A private `int nextId` field starting at 1.
- An `add(...)` implementation that increments `nextId`, constructs the `Task`, puts it in the map, and returns it.
- A `list()` implementation that returns a new `ArrayList` over the map values (so the caller cannot mutate the storage).
- A `findById(...)` implementation that wraps `map.get(id)` in `Optional.ofNullable`.
- A `markDone(...)` implementation that looks up the task and calls `markDone()` on it; returns true if found, false if not.

Now update `BadTaskApp.java`:
- Delete the `BadTaskStore` class entirely.
- At the top of `main`, before the loop, declare: `TaskRepository repo = new InMemoryTaskRepository();`. Note the type is the **interface**, not the implementation.
- In the `a` command, replace the `Task t = new Task(...)` and `BadTaskStore.tasks.add(t)` with a single call: `Task t = repo.add(title, Priority.fromInt(priorityInt));`. Remove the temporary `nextId` you added in Step 3.1 (the repository owns id generation now).
- In the `l` command, replace `for (Task t : BadTaskStore.tasks)` with `for (Task t : repo.list())`.
- In the `d` command, you have a choice to make. The current command takes a 0-based index. The repository works by id (1-based). **Switch the command to take an id.** Replace the `idx`-based logic with `boolean ok = repo.markDone(id);` and print "Marked done." or "No such task id." based on the result. The user prompt and `l` output can stay as they are for now; we will fix the displayed id in Step 3.4.

**Build and run.** Note the behavioural change: `d` now takes an id (1, 2, 3...) instead of an index (0, 1, 2...). For the moment the listed output still shows old-style indexes; you will fix that in Step 3.4.

> **Why a `LinkedHashMap`?** A plain `HashMap` would not preserve insertion order, so the list output would appear in an unpredictable sequence. `LinkedHashMap` gives you O(1) lookup like `HashMap` while keeping insertion-order iteration. This is the kind of small choice you make a hundred times when refactoring; the answer is "use the simplest collection that gives you the guarantees the contract requires."

### Step 3.3: Introduce the application service layer

**Goal:** Stop having the UI call the repository directly. Put a service layer between them.

Create **`TaskService.java`**:

```java
public class TaskService {
    private final TaskRepository repo;

    public TaskService(TaskRepository repo) {
        this.repo = repo;
    }

    public Task createTask(String title, int priorityInt) {
        Priority p = Priority.fromInt(priorityInt);
        return repo.add(title, p);
    }

    public List<Task> listTasks() {
        return repo.list();
    }

    public boolean completeTask(int id) {
        return repo.markDone(id);
    }
}
```

Now update `BadTaskApp.java`:
- After constructing the repository, also construct the service: `TaskService service = new TaskService(repo);`.
- In the `a` command, call `service.createTask(title, p)` instead of `repo.add(title, Priority.fromInt(p))`. Note that the int-to-Priority conversion has moved into the service. The CLI no longer needs to know about the `Priority` enum at all (except for whatever it prints to the user).
- In the `l` command, call `service.listTasks()` instead of `repo.list()`.
- In the `d` command, call `service.completeTask(id)` instead of `repo.markDone(id)`.

The CLI now talks only to `TaskService`. It still has to instantiate the repository because someone has to wire them together at startup, but no command logic touches the repository directly.

**Build and run.** Behaviour should be unchanged from Step 3.2.

> **Why does this layer exist if it is just a passthrough?** Right now the service is a thin wrapper, and it is reasonable to ask whether it earns its keep. In a real application this layer is where transactions begin and end, where authorization is checked, where multiple repositories are coordinated, where logging and metrics are recorded, and where domain events are published. Introducing the layer when the app is small means those concerns have an obvious home when they arise later. Adding the layer retroactively to a large codebase is a much harder migration.

### Step 3.4: Separate the UI into its own class

**Goal:** The CLI should not be inside a class called `BadTaskApp`. Move it to a properly named class.

Create **`Main.java`**:
- Define a `public class Main` with a `public static void main(String[] args)` method.
- Move the entire body of `BadTaskApp.main` into `Main.main`.

While you are at it, improve the list output so it shows the task id (not a positional index). The output line should look like:

```
1: [ ] buy groceries (p2)
2: [x] write lab report (p1)
```

The format string for that is:

```java
System.out.printf("%d: [%s] %s (p%d)%n",
    t.getId(), (t.isDone() ? "x" : " "), t.getTitle(), t.getPriority().level());
```

Delete `BadTaskApp.java` entirely. You no longer need it.

**Build:**

```bash
javac *.java
ls -la *.class
```

You should now have class files for `Priority`, `Task`, `TaskRepository`, `InMemoryTaskRepository`, `TaskService`, and `Main`. Delete the old `BadTaskApp.class` if it is still hanging around.

**Run with the new entry point:**

```bash
java Main
```

The session should look like:

```
[a]dd, [l]ist, [d]one <id>, [q]uit: a
title: buy groceries
priority (1..3): 2
[a]dd, [l]ist, [d]one <id>, [q]uit: l
1: [ ] buy groceries (p2)
[a]dd, [l]ist, [d]one <id>, [q]uit: d 1
[a]dd, [l]ist, [d]one <id>, [q]uit: l
1: [x] buy groceries (p2)
[a]dd, [l]ist, [d]one <id>, [q]uit: q
```

### Step 3.5: Tighten input handling

**Goal:** The program should no longer crash on bad input. Every place that could throw an exception from user input should catch it and print a helpful message instead.

Audit `Main.java` and add try/catch handling where it is missing. Specifically:

- **Priority parsing in the `a` command:** wrap `Integer.parseInt` and the call to `service.createTask` in a single try block. Catch `NumberFormatException` (bad number format) and `IllegalArgumentException` (priority out of range, or empty title from the `Task` constructor). Print the exception's message and continue the loop.
- **The `d` command:** validate that the line has exactly two tokens before parsing. If not, print `Usage: d <id>` and continue. Wrap `Integer.parseInt(parts[1])` in a try/catch for `NumberFormatException` and print "Task id must be an integer." If `service.completeTask(id)` returns false, print "No such task id."
- **Empty list:** if `service.listTasks()` returns an empty list, print "(no tasks)" rather than nothing.
- **Unknown command:** add an `else` branch that prints "Unknown command."

**Build and run the final version.** Confirm that all of these inputs produce helpful messages instead of crashes:

```
[a]dd, [l]ist, [d]one <id>, [q]uit: a
title: review pull request
priority (1..3): 5
Error: Priority must be 1..3

[a]dd, [l]ist, [d]one <id>, [q]uit: a
title:
priority (1..3): 1
Error: Title cannot be empty

[a]dd, [l]ist, [d]one <id>, [q]uit: d
Usage: d <id>

[a]dd, [l]ist, [d]one <id>, [q]uit: d xyz
Task id must be an integer.

[a]dd, [l]ist, [d]one <id>, [q]uit: d 999
No such task id.

[a]dd, [l]ist, [d]one <id>, [q]uit: l
(no tasks)

[a]dd, [l]ist, [d]one <id>, [q]uit: huh?
Unknown command.

[a]dd, [l]ist, [d]one <id>, [q]uit: q
```

The refactor is complete. You should have six files in the directory: `Priority.java`, `Task.java`, `TaskRepository.java`, `InMemoryTaskRepository.java`, `TaskService.java`, and `Main.java`. The original `BadTaskApp.java` is gone.

---

## Part 4: Reason About What You Built

Now that the refactor is done, take a step back and think about the structure you produced. Answer the following in your notebook.

### Question 4.1: Why an interface and an implementation?

`TaskRepository` is an interface and `InMemoryTaskRepository` is a class that implements it. Why did the refactor split storage into two types instead of just using `InMemoryTaskRepository` directly throughout the code? Name three concrete benefits and one cost.

(Hint: think about testing, swapping implementations, and what the rest of the code is allowed to know about storage.)

### Question 4.2: The dependency direction

Look at the `import` statements in each of your six files. Which file imports from which? Sketch the dependency graph on paper.

A correct sketch will show arrows pointing inward: `Main` depends on everything, `TaskService` depends on `TaskRepository` and the domain types but **not** on `InMemoryTaskRepository`, `InMemoryTaskRepository` and `TaskRepository` depend on the domain, and the domain depends on nothing project-specific.

What would be wrong if `Task` imported `TaskRepository`? What would be wrong if `TaskService` imported `InMemoryTaskRepository`?

### Question 4.3: Why an enum instead of an int?

Beyond "magic numbers are bad," what specific bugs does the `Priority` enum prevent that the original `int priority` allowed?

Try to come up with three concrete examples of code that would compile and run with the old int-based design but would be caught at compile time or fail-fast at runtime with the new enum-based design.

### Question 4.4: Where would you add a feature?

Suppose you needed to add each of these features. For each one, list which files you would modify and which would not need to change. Justify each answer.

- **Feature A:** Persist tasks to a JSON file so they survive program restart.
- **Feature B:** Add a "delete task by id" command (`x <id>`).
- **Feature C:** Replace the CLI with a REST API.

(Compare your answers to what you would have had to change in the original `BadTaskApp.java`. The contrast is the point of the refactor.)

---

## Part 5: Verify Behaviour Preservation

A refactor is only a refactor if external behaviour is preserved. Take the behavioural baseline you captured in Step 1.3 (the bad version's add/list/done session) and run the equivalent session against the refactored version.

### Step 5.1: Run the equivalent session

```bash
java Main
```

Enter the same inputs you used in Step 1.3:

```
a
buy groceries
2
a
write lab report
1
l
d <use the id of the first task, which is now 1 instead of 0>
l
q
```

### Step 5.2: Diff the outputs

Compare the output line by line against your Step 1.3 baseline. There should be exactly two differences:

1. The list now shows ids (1, 2) instead of indexes (0, 1).
2. The `d` command takes an id instead of an index.

If anything else differs, you have a regression. Read the code carefully and figure out where the behaviour changed.

### Step 5.3: Try an extension

Now that the architecture is in place, add **Feature B from Question 4.4** by hand: a delete-task-by-id command.

You should need to touch exactly four files:

- **`TaskRepository.java`:** add a `boolean delete(int id);` method to the interface.
- **`InMemoryTaskRepository.java`:** implement it (`return storage.remove(id) != null;`).
- **`TaskService.java`:** add a `public boolean deleteTask(int id)` method that delegates to `repo.delete(id)`.
- **`Main.java`:** add an `else if (cmd.startsWith("x"))` branch with the same input validation as the `d` command, calling `service.deleteTask(id)`.

Build, run, and test the new command. Notice that no other file needs to change. The architecture absorbed the new feature without disruption.

Compare this to what the same feature would have looked like in the original `BadTaskApp.java`. **This is what refactoring buys you.**

---

## Part 6: Reflection

Answer the following in your notebook. These are open-ended; spend at least 15 minutes on this section.

1. **The five-step sequence.** Why does the lab refactor in this specific order: domain first, then storage, then service, then UI, then input handling? What would have gone wrong if you had started with the UI or the service?

2. **Build between every step.** The lab insisted on running `javac *.java` after every step. Why is that important? What is the cost of doing a large refactor as one big change and only compiling at the end?

3. **Choices the lab did not specify.** Look back at your notebook entries from Part 3. What decisions did you have to make that the instructions did not pin down (variable names, helper method placement, where to put a try/catch, what to log)? How did you decide?

4. **When did the design improvement become visible?** At what step did the architecture start to feel meaningfully better than the original? Was it after extracting the domain (Step 3.1), after the repository (3.2), the service (3.3), or only at the end? Why?

5. **When to stop refactoring.** Could this code be improved further? List three things you could still do (for example: a logger, a configuration file, more validation, better separation of read and write operations). For each one, decide whether it would be worth doing in a real project and why.

6. **What you would do differently.** If you were starting the refactor again from scratch, what would you do differently? Are there steps that should be split or combined? Are there decisions you would revisit?

---


---

## Reference: The Five-Step Refactor Plan

The plan you executed in this lab generalizes to many "blob" codebases. Keep it for future use.

| Step | Pattern | Output |
|------|---------|--------|
| 1 | **Encapsulate the domain.** Turn anaemic data classes into entities with validated constructors and behaviour methods. Replace raw ints and strings with enums and value types. | Pure domain classes with no I/O dependencies. |
| 2 | **Remove global state.** Replace static collections with a repository interface and at least one implementation. | A storage abstraction the rest of the code talks to. |
| 3 | **Introduce a service layer.** Extract use-case orchestration from the UI into a service that depends on the domain and the repository interface. | A façade that any UI can call. |
| 4 | **Separate the UI.** Move the entry point out of the monolith into its own class that only does I/O and command parsing. | A UI that knows nothing about storage or domain rules. |
| 5 | **Tighten input handling.** Catch invalid inputs at the boundary, validate against the domain rules in the service, and return clear error messages to the UI. | A program that does not crash on bad input. |

---

## Troubleshooting

**`javac` cannot find one of the new files.**
Make sure all six files are in the same directory and you are running `javac *.java` (not `javac BadTaskApp.java`). Java's default rule is "one public class per file, named after the file." If you accidentally made two public classes in one file, the compiler will complain.

**`NullPointerException` in the `l` command.**
Most likely you are calling `t.getPriority().level()` on a task whose priority is null. This should not happen if your `Task` constructor uses `Objects.requireNonNull(priority)`, but check that you actually added that check.

**`IllegalArgumentException: Priority must be 1..3` in normal flow.**
You probably forgot to wrap the priority parsing in a try/catch in Step 3.5. The constructor and `Priority.fromInt` correctly reject bad input by throwing; the UI is supposed to catch the throw and print an error.

**The list shows ids 1, 3, 5 instead of 1, 2, 3.**
You are incrementing `nextId` somewhere it should not be incremented, or `add` is being called more times than you think. Check that `nextId++` only appears once in `InMemoryTaskRepository.add`.

**The build succeeds but `java Main` complains "could not find or load main class Main."**
The `Main.class` file is not on the classpath. Make sure you are running `java Main` (not `java Main.class`) from the same directory where the class files live, or use `java -cp . Main` to be explicit about the classpath.

**You ended up with a circular import.**
This is an architectural smell. Stop and look at your dependency sketch from Question 4.2. The fix is almost always to move a type from an outer layer into an inner one, or to introduce a new interface that breaks the cycle.

---

## Further Reading

- Refactoring (Martin Fowler), 2nd edition. The canonical reference for incremental code transformation.
- Clean Architecture (Robert C. Martin). On the dependency-inward principle that this lab applied.
- Effective Java (Joshua Bloch), 3rd edition. Items 16 (encapsulation) and 18 (composition over inheritance) are directly relevant.
- Hexagonal Architecture (Alistair Cockburn, original paper): <https://alistair.cockburn.us/hexagonal-architecture/>
- Domain-Driven Design Distilled (Vaughn Vernon). A short introduction to the layering you applied here.
