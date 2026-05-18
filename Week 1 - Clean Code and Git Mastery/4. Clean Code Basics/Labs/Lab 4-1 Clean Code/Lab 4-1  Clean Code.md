# Lab 4-1: Cleaning Up a Python Task Tracker

## Overview

The previous lab (3-1) used a Java program to teach **layered architecture**: where in the system each kind of code belongs, and what depends on what. This lab uses a parallel Python program to teach **clean code at the line level**: how to name things, how to keep functions small and single-purpose, when to introduce a type instead of passing a magic number, how to write comments that explain *why* instead of *what*, and how to eliminate the small duplications that make a codebase tiring to read.

You will start with a deliberately bad Python program: a small task tracker that uses global state, vague names like `T` and `x` and `p`, magic numbers, a single long function that mixes input, validation, business logic, and output, and exception handlers that swallow errors silently. You will read it, list its code smells, and then rewrite it as a clean, modular Python package with the same external behaviour.

**This is a hands-on exercise.** You write the new code yourself. The point is to feel where each smell came from, to make the small decisions an AI assistant would otherwise make for you, and to come away with the muscle memory to recognize the same smells in any future codebase.

A companion lab (**Lab 4-1b: Cleaning Up with GitHub Copilot**) walks through the same exercise with an AI assistant. The recommended sequence is to do this lab first, then redo the cleanup with Copilot, and compare the two experiences.

**Estimated time:** 90 to 120 minutes
**Difficulty:** Intermediate

**Prerequisites:**

- Python 3.10 or later (`python3 --version` should print 3.10.x or higher). The reference solution uses dataclasses, the `IntEnum` class, structural type hints (`list[Task]`, `Task | None`), and `Protocol`-based interfaces, all of which require 3.10+.
- A text editor or IDE you are comfortable with.
- Familiarity with Python syntax: functions, classes, exceptions, modules, list/dict comprehensions.
- Completion of Lab 3-1 (the Java refactoring lab) is recommended but not required. If you have done it, you will notice the same five-step plan; the focus here is the line-level clean code, not the layers.

---

## Learning Objectives

By the end of this lab, you will be able to:

1. Identify a wide range of code smells in a small Python program and name each one.
2. Distinguish between *what* code does and *what is wrong with how it says it*.
3. Replace vague single-letter names with intention-revealing names, magic numbers with named constants or enums, and nested lists with dataclasses.
4. Decompose a long function into small, single-purpose helpers and a clean dispatch structure.
5. Organize a Python project as a package of focused modules.
6. Verify that a cleanup preserves behaviour by exercising the program before and after.

---

## Part 1: Set Up the Workspace

### Step 1.1: Create the lab directory

In a terminal:

```bash
mkdir -p ~/cleancode-lab
cd ~/cleancode-lab
```

### Step 1.2: Create the starter file

Create a file called `bad.py` with the following content. Save it. The file is also supplied as Bad.py in the lab folder.

```python
# bad_task_app.py
# Intentional anti-patterns: globals, magic values, long function, mixed I/O & logic,
# vague names, duplication, no tests, no error handling, comments that explain "what".
T = []  # tasks: [ [title, done, prio] ]

def run():
    print("Task Trkr v0")
    while True:
        cmd = input("[a]dd [l]ist [d]one <idx> [p]rio <idx> <1-3> [q]uit: ").strip()
        if cmd == "a":
        # Process if the option is a
            t = input("title: ")
            p = input("priority (1..3): ")
            if p == "": p = "2"  # default medium
            try:
                p = int(p)
            except:
                p = 2
            if p < 1 or p > 3: p = 2
            T.append([t, False, p])
            print("ok")
        elif cmd == "l":
          # Process if the option is l
            i = 0
            for x in T:
                box = "x" if x[1] else " "
                pr = x[2]
                # Duplicate formatting logic scattered
                print(str(i) + ": [" + box + "] " + x[0] + " (p" + str(pr) + ")")
                i += 1
        elif cmd.startswith("d"):
            parts = cmd.split()
            if len(parts) > 1:
                try:
                    idx = int(parts[1])
                    if idx >= 0 and idx < len(T):
                        T[idx][1] = True
                        print("done")
                except:
                    print("bad idx")
        elif cmd.startswith("p"):
          # Process if the option is p
            parts = cmd.split()
            if len(parts) > 2:
                try:
                    idx = int(parts[1]); pr = int(parts[2])
                    if idx >= 0 and idx < len(T):
                        if pr < 1 or pr > 3: pr = 2
                        T[idx][2] = pr
                        print("prio ok")
                except:
                    print("bad args")
        elif cmd == "q":
          # Process if the option is q
            break
        else:
            print("???")

if __name__ == "__main__":
    run()
```

### Step 1.3: Run the bad version to establish a baseline

Before changing anything, confirm the program works

> Note: There are two version of python on your VM as shown below.
> - Either version should be fine.

```bash 
protech@studentvm:~$ python 
Python 3.13.13 (main, Apr  8 2026, 09:49:30) [GCC 11.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> quit()
protech@studentvm:~$ python3
Python 3.10.12 (main, Mar  3 2026, 11:56:32) [GCC 11.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> quit()
protech@studentvm:~$ 



```

```bash
python3 bad.py
```

You should see the prompt. Run this exact session and write down what you see:

```
[a]dd [l]ist [d]one <idx> [p]rio <idx> <1-3> [q]uit: a
title: Make Bed
priority (1..3): 1
ok
[a]dd [l]ist [d]one <idx> [p]rio <idx> <1-3> [q]uit: l
0: [ ] Make Bed (p1)
[a]dd [l]ist [d]one <idx> [p]rio <idx> <1-3> [q]uit: d 0
done
[a]dd [l]ist [d]one <idx> [p]rio <idx> <1-3> [q]uit: p 0 3
prio ok
[a]dd [l]ist [d]one <idx> [p]rio <idx> <1-3> [q]uit: l
0: [x] Make Bed (p3)
[a]dd [l]ist [d]one <idx> [p]rio <idx> <1-3> [q]uit: q
```

The program runs and produces the right answers. It is also, line for line, hard to read. The rest of the lab is about why, and what to do about it.

### Step 1.4: Create a lab notebook

Create a file `notebook.md` in the workspace. You will record your diagnosis, decisions, and reflections here. Start with:

```markdown
# Clean Code Lab Notebook

## Part 2: Code smells

## Part 3: Cleanup decisions

## Part 5: Verification

## Part 6: Reflection
```

---

## Part 2: Find the Code Smells

Before you change a single line, read `bad.py` slowly and write down everything that is wrong with it. Spend at least 15 minutes. Do not look ahead.

### Question 2.1: Vague and misleading names

List every variable and function name in the file that does not clearly say what it represents. For each one, write down what a better name would be.

You should find at least **eight**. Examples to get you started: `T`, `t`, `p`. Find the rest yourself.

### Question 2.2: Magic numbers and strings

Where in the code is a number or string used whose meaning depends on context that is not in the code? Note that "magic" does not mean "complicated"; the number `1` in `if p < 1` is magic because the reader has to know that 1 means HIGH priority, which is only documented in a comment elsewhere.

List at least **five magic values** with what each one means and how you would replace it.

### Question 2.3: Long function and mixed abstractions

The `run()` function is doing too many things. List every distinct responsibility you can identify inside `run()`. Examples: "print the banner," "read user input," "parse the `d` command's index argument." How many distinct responsibilities are there? (The right answer is more than ten.)

### Question 2.4: Bad comments

Comments should explain *why* code does something, not *what* the code is doing. The `bad.py` file has several comments that violate this rule. Find them and write down what is wrong with each one.

### Question 2.5: Silent failure

The code uses bare `except:` clauses in three places. Read each one and answer: what kinds of exceptions does it catch? What does it do with them? What goes wrong when the wrong exception is silently absorbed?

### Question 2.6: Duplication

Where is the same logic (or nearly the same logic) repeated in the file? Find at least **two duplications**.

### Question 2.7: Coupling to data shape

The tasks are stored as nested lists: `[title, done, prio]`. Every place in the code that touches a task knows the *order* of fields in this list. If you wanted to add a fourth field (say, a creation timestamp), how many places would you have to change? Why is this a problem?

### Reference: what you should have found

After you have written your own list, compare to this one. You should have at least these smells:

**Naming (Q2.1):**
- `T` (the global) is a one-letter all-caps name with no meaning. Should be `tasks`.
- `t` in the add branch is the title. Should be `title`.
- `p` is the priority. Should be `priority` (or just split into `priority_text` for the raw string and `priority_value` for the parsed int).
- `x` in the list loop is a task. Should be `task`.
- `pr` is yet another spelling of priority. Should be `priority`.
- `idx` is a position, but the program would be cleaner if it used ids instead of positions (see Q2.7).
- `cmd` is short but acceptable; `command` is more readable.
- `parts` is generic; `arguments` or `args` is more specific.
- `box` is a clever name for the `[ ]`/`[x]` marker but unclear; `done_marker` is clearer.
- `run` as a function name is fine but `main` or `repl` would be more conventional.

**Magic values (Q2.2):**
- `1`, `2`, `3` appearing as priority values throughout. Should be a `Priority` enum.
- `2` again as the default priority. Should be a named constant or an enum value (`Priority.MEDIUM`).
- The comment-only magic: priority `1` means HIGH and `3` means LOW. The numeric ordering is the opposite of what most readers expect.
- The string `"x"` and `" "` for the done marker. Could be a named constant, though this is a minor point.
- The format string for the list output is duplicated literal punctuation; it would be cleaner with f-strings and a single formatting function.

**Long function (Q2.3):** Pretty much every line in `run()` is a different responsibility. A non-exhaustive list:
- Print banner.
- Prompt for command.
- Parse command character.
- For `a`: prompt for title, prompt for priority, parse priority text, default-on-empty, default-on-parse-error, range-check, default-on-out-of-range, append to global, print confirmation.
- For `l`: maintain an index counter, iterate, format each task, print.
- For `d`: split command line, check argument count, parse int, range-check, mutate global, print confirmation. Plus the silent except.
- For `p`: same as `d` but with two arguments instead of one. Duplicates the parsing pattern.
- For `q`: break the loop.
- For everything else: print "???".

**Bad comments (Q2.4):** `# Process if the option is a` (and the same for `l`, `p`, `q`). These explain what the code below them does, which the code already says. They are noise.

**Silent failure (Q2.5):** Three bare `except:` blocks. The first turns *any* exception during priority parsing into the default value 2 (silently masks bugs in the parse logic, masks `KeyboardInterrupt`, masks `SystemExit`). The second catches any exception during `d` parsing and prints "bad idx" even if the real problem is something else. The third does the same for `p`. None of them tells the user what actually went wrong.

**Duplication (Q2.6):**
- The `d` and `p` command handlers share the same shape: `parts = cmd.split()`, length check, parse int, range check, mutate, print confirmation, silent except.
- The priority validation (`if p < 1 or p > 3: p = 2`) appears in both the `a` and `p` branches.

**Coupling to data shape (Q2.7):** Every place that touches a task knows that `[0]` is the title, `[1]` is the done flag, `[2]` is the priority. Adding a fourth field (timestamp, owner, due date) means hunting through the file for every `x[N]` and `T[idx][N]` and updating it. This is the symptom that says "you need a class, not a list."

If you found smells that are not on this list, they are probably also real. The list is a floor, not a ceiling.

---

## Part 3: Clean It Up in Five Steps

You will now rewrite the program in five steps. **After every step, run the program and confirm it still behaves correctly.** Each step is small enough that you should never go more than a few minutes with a broken program.

By the end you will have a package `clean_task/` with four modules:

```
clean_task/
    __init__.py
    models.py
    repo.py
    service.py
    cli.py
```

You will build it incrementally. The first three steps still produce a single-file program; you only split into modules in Step 3.4.

Make a copy of the bad file so you can compare:

```bash
cp bad.py work.py
```

You will edit `work.py`. The original `bad.py` stays as a reference for comparison.

### Step 3.1: Replace vague names and magic values

**Goal:** Rename everything to say what it means. Replace priority magic numbers with a real type. No structural changes yet; the file is still one function.

In `work.py`:

1. **Rename the global** from `T` to `tasks`. Update every reference.
2. **Rename loop variables** in the list branch: `x` to `task`, `pr` to `priority`, `box` to `done_marker`. Update references.
3. **Rename `t` and `p`** in the add branch to `title` and `priority_text` (for the raw string) and `priority_value` (for the parsed int). Use both names; the raw string and the parsed integer are different things and deserve different names.
4. **Rename `cmd`** to `command` and `parts` to `args`. (Optional but readable.)
5. **Replace the priority magic numbers** with a Python `IntEnum`. At the top of the file, add:

   ```python
   from enum import IntEnum

   class Priority(IntEnum):
       HIGH = 1
       MEDIUM = 2
       LOW = 3
   ```

   Then update every `1`, `2`, `3` that is being used as a priority to use the enum member instead. For example, the default priority becomes `Priority.MEDIUM`, the range check becomes `if priority_value not in (1, 2, 3): priority_value = Priority.MEDIUM`, and the stored priority is the enum value.

6. **Replace the format string** in the list branch with an f-string:

   ```python
   print(f"{task_id}: [{done_marker}] {task.title} (p{int(task.priority)})")
   ```

   This is a small change but eliminates the noisy `str(...)` and `+` concatenation. (Note: you will refactor the list-of-lists into a dataclass in Step 3.2, at which point `task.title` and `task.priority` actually work. For now you may need to keep using `task[0]`, `task[1]`, etc. and adapt the format string accordingly.)

7. **Delete the noise comments** `# Process if the option is X`. They describe what the code does, which the code already says.

8. **Replace `print("???")`** with `print("Unknown command.")`.

**Run the program** and confirm it still works.

> **What did the rename teach you?** Read `work.py` from top to bottom now and compare it mentally to `bad.py`. Same code, same logic, no new abstractions, just better names and a real enum. How much easier is it to read?

### Step 3.2: Introduce a `Task` dataclass

**Goal:** Replace the `[title, done, priority]` list-of-fields with a real type. This is the change that makes every other smell easier to fix.

At the top of `work.py`, add:

```python
from dataclasses import dataclass, field

@dataclass
class Task:
    id: int
    title: str
    priority: Priority
    done: bool = field(default=False)

    def __post_init__(self):
        self.title = self.title.strip()
        if not self.title:
            raise ValueError("Title cannot be empty")
        if not isinstance(self.priority, Priority):
            raise TypeError("priority must be a Priority value")

    def mark_done(self):
        self.done = True

    def rename(self, new_title):
        stripped = new_title.strip()
        if not stripped:
            raise ValueError("Title cannot be empty")
        self.title = stripped

    def change_priority(self, new_priority):
        if not isinstance(new_priority, Priority):
            raise TypeError("priority must be a Priority value")
        self.priority = new_priority
```

Now update `run()`:

- The `tasks` global stays a list, but its element type is now `Task` instead of `list`.
- Maintain a `next_id` counter at function scope (we will move it into a proper repository in Step 3.3).
- In the `a` branch, after parsing and validating the priority, create a Task: `task = Task(id=next_id, title=title, priority=Priority(priority_value)); next_id += 1; tasks.append(task)`.
- In the `l` branch, the format string becomes clean: `print(f"{task.id}: [{done_marker}] {task.title} (p{int(task.priority)})")`.
- In the `d` branch, instead of `T[idx][1] = True`, use `tasks[idx].mark_done()`. (We will fix the index-versus-id question in Step 3.3.)
- In the `p` branch, instead of `T[idx][2] = pr`, use `tasks[idx].change_priority(Priority(priority_value))`.

**Run and confirm.**

> **What just happened?** Every place that previously knew the *shape* of the task list (`x[0]`, `x[1]`, `x[2]`) now uses named methods and attributes. Adding a fourth field to `Task` (say, a `created_at` timestamp) would not require changing any code outside `Task`. That is the payoff of introducing the type.

### Step 3.3: Extract a repository, retire the global

**Goal:** Replace the module-level `tasks` list with a proper repository class. The global goes away; storage lives in a class with a clear interface.

Add this class to `work.py`:

```python
class InMemoryTaskRepository:
    def __init__(self):
        self._storage = {}
        self._next_id = 1

    def add(self, title, priority):
        task = Task(id=self._next_id, title=title, priority=priority)
        self._storage[self._next_id] = task
        self._next_id += 1
        return task

    def list(self):
        return list(self._storage.values())

    def find_by_id(self, task_id):
        return self._storage.get(task_id)

    def mark_done(self, task_id):
        task = self._storage.get(task_id)
        if task is None:
            return False
        task.mark_done()
        return True

    def change_priority(self, task_id, new_priority):
        task = self._storage.get(task_id)
        if task is None:
            return False
        task.change_priority(new_priority)
        return True
```

Now update `run()`:

- Delete the global `tasks` list and the `next_id` counter at function scope. Replace them with `repo = InMemoryTaskRepository()` at the top of `run()`.
- The `a` branch becomes: `task = repo.add(title, Priority(priority_value))`.
- The `l` branch becomes: `for task in repo.list(): ...`.
- The `d` and `p` branches change *semantically*. Previously they took an index (0-based position in the list). Now they take an id (1-based, assigned by the repository). Update the user-visible prompt to say `<id>` instead of `<idx>`, and rewrite the handlers:

  ```python
  elif command == "d":
      args = line.split()[1:]
      if len(args) < 1:
          print("Usage: d <id>")
          continue
      try:
          task_id = int(args[0])
      except ValueError:
          print("Task id must be an integer.")
          continue
      if repo.mark_done(task_id):
          print("Marked done.")
      else:
          print("No such task id.")
  ```

  Do the equivalent for `p`. Note that the silent bare-`except:` is gone; you now catch only `ValueError`, and you tell the user what went wrong.

- **Update the list-output format** to show the id instead of a position counter. Drop the `i = 0; ... i += 1` index-tracking; just use `task.id`.

**Run and confirm.** The behaviour is the same as before, except that ids are 1-based and the `d`/`p` commands take an id rather than an index.

> **The smell that just died.** No more global state. The `repo` is created in one place, owned by `run()`, and shut down (implicitly) when `run()` returns. If you wrote tests for the program, each test would get its own repository and they would never interfere with each other.

### Step 3.4: Extract a service and split into modules

**Goal:** Stop having the CLI call the repository directly. Put a thin service layer between them, then split the four kinds of code into four files.

First, add a `TaskService` class to `work.py`:

```python
class TaskService:
    def __init__(self, repository):
        self._repo = repository

    def create_task(self, title, priority_value):
        priority = Priority(priority_value)
        return self._repo.add(title, priority)

    def list_tasks(self):
        return self._repo.list()

    def complete_task(self, task_id):
        return self._repo.mark_done(task_id)

    def set_priority(self, task_id, priority_value):
        priority = Priority(priority_value)
        return self._repo.change_priority(task_id, priority)
```

Update `run()` to use the service instead of the repository directly: `service = TaskService(repo)` and then replace every `repo.method(...)` with the corresponding `service.method(...)`. The CLI no longer needs to import `Priority` (the service does the int-to-`Priority` conversion).

**Run and confirm.**

Now split the single file into the four-module package layout. Create:

```
clean_task/
    __init__.py
    models.py
    repo.py
    service.py
    cli.py
```

Put a docstring in `__init__.py` (the file can otherwise be empty, or you can write one line of overview).

Move:
- `Priority` and `Task` into `models.py`.
- `InMemoryTaskRepository` into `repo.py`. Add `from .models import Priority, Task` at the top.
- `TaskService` into `service.py`. Add `from .models import Priority, Task` and `from .repo import TaskRepository` at the top (or just `InMemoryTaskRepository` if you have not yet introduced a `TaskRepository` protocol; see the bonus step below).
- `run()` and any helper functions into `cli.py`. Add the appropriate imports.

Make sure `cli.py` ends with:

```python
if __name__ == "__main__":
    run()
```

**Run with the new entry point:**

```bash
python3 -m clean_task.cli
```

> **A bonus you can do or skip.** A purist would define a `TaskRepository` protocol (in `repo.py`) that `InMemoryTaskRepository` implements, and have `TaskService` accept the protocol type rather than the concrete class. This lets you swap in a different repository (file-backed, SQLite, REST) without touching the service. The reference solution does this with `typing.Protocol`. If you have time, do it; if not, the lab works fine without it.

### Step 3.5: Break the long function into small handlers

**Goal:** The remaining `run()` is still long, with a big `if/elif` chain where each branch does several things. Split each command into its own handler function.

In `cli.py`, define one function per command:

```python
def handle_add(service):
    title = input("title: ")
    priority_text = input("priority (1..3): ").strip()
    try:
        priority_value = int(priority_text)
    except ValueError:
        print("Error: priority must be an integer 1, 2, or 3")
        return
    try:
        task = service.create_task(title, priority_value)
    except ValueError as exc:
        print(f"Error: {exc}")
        return
    print(f"Added #{task.id}: {task.title} (p{int(task.priority)})")


def handle_list(service):
    tasks = service.list_tasks()
    if not tasks:
        print("(no tasks)")
        return
    for task in tasks:
        print(format_task(task))


def handle_done(service, args):
    if len(args) < 1:
        print("Usage: d <id>")
        return
    try:
        task_id = int(args[0])
    except ValueError:
        print("Task id must be an integer.")
        return
    if service.complete_task(task_id):
        print("Marked done.")
    else:
        print("No such task id.")


def handle_priority(service, args):
    if len(args) < 2:
        print("Usage: p <id> <1-3>")
        return
    try:
        task_id = int(args[0])
        priority_value = int(args[1])
    except ValueError:
        print("Both id and priority must be integers.")
        return
    try:
        ok = service.set_priority(task_id, priority_value)
    except ValueError as exc:
        print(f"Error: {exc}")
        return
    if ok:
        print("Priority updated.")
    else:
        print("No such task id.")
```

Add a small formatter so the list output and the add confirmation can share their format:

```python
def format_task(task):
    box = "x" if task.done else " "
    return f"{task.id}: [{box}] {task.title} (p{int(task.priority)})"
```

Then `run()` becomes short and obvious:

```python
def run():
    service = TaskService(InMemoryTaskRepository())
    print("Task Tracker (cleaned up)")
    while True:
        line = input("[a]dd [l]ist [d]one <id> [p]rio <id> <1-3> [q]uit: ").strip()
        if not line:
            continue
        command, *args = line.split()
        if command == "a":
            handle_add(service)
        elif command == "l":
            handle_list(service)
        elif command == "d":
            handle_done(service, args)
        elif command == "p":
            handle_priority(service, args)
        elif command == "q":
            break
        else:
            print("Unknown command.")
```

**Build and run.** Try the full set of inputs to confirm everything still works:

```
a / Buy bread / 2
a / Finish report / 1
l
d 1
l
p 2 3
l
d 99            (should print "No such task id.")
d xyz           (should print "Task id must be an integer.")
p 1 9           (should print "Error: ...")
a / / 1         (empty title, should print "Error: ...")
huh             (should print "Unknown command.")
q
```

If every one of these produces a helpful, predictable message, your cleanup is done.

---

## Part 4: Reason About What You Built

### Question 4.1: Naming as documentation

Compare the variable names in `bad.py` to the names in your cleaned-up version. Pick five renames you made. For each one, explain what knowledge the bad name required the reader to keep in their head, and how the good name puts that knowledge where the reader needs it.

### Question 4.2: Why a dataclass instead of a dictionary?

The bad version stored tasks as nested lists. An obvious first improvement would have been to use a dictionary: `{"title": "...", "done": False, "priority": 1}`. Why is the `Task` dataclass a better choice than a dictionary in this case? Name at least three concrete advantages.

(Hint: think about typos, validation, autocomplete, refactoring, and the difference between "this thing has fields" and "this thing has behaviour.")

### Question 4.3: The bare except is the worst smell. Why?

Of all the smells in `bad.py`, the bare `except:` blocks are arguably the most dangerous. Why? What kinds of errors can a bare `except:` swallow that a real programmer would *want* to crash on?

### Question 4.4: Where would you add a feature?

The cleaned-up version makes it cheap to add features. For each of these, list which file(s) you would change and which would not need to change:

- **Feature A:** Persist tasks to a JSON file so they survive program restart.
- **Feature B:** Add a "delete task by id" command (`x <id>`).
- **Feature C:** Add a due-date field to each task.
- **Feature D:** Replace the CLI with a web UI using Flask.

Compare each of these to what you would have had to do in `bad.py`.

### Question 4.5: Comments

In Part 2 you identified that comments like `# Process if the option is a` were noise. Now look at your cleaned-up version. Where, if anywhere, do you still have comments? What do they say? Do they explain *why* or *what*?

A well-written program has comments that the code itself cannot express: the reason behind a non-obvious decision, a link to an external specification, a warning about a subtle constraint. If your cleaned-up version has comments that just restate the code, delete them.

---

## Part 5: Verify Behaviour Preservation

### Step 5.1: Run the same session as the baseline

Recall the session you captured in Step 1.3:

```
a / Make Bed / 1
l
d 1                    (was "d 0" in the bad version)
p 1 3                  (was "p 0 3" in the bad version)
l
q
```

Run this against your cleaned-up version with `python3 -m clean_task.cli` and compare the output to your Step 1.3 baseline.

The differences should be exactly:

1. **Banner text** changed from "Task Trkr v0" to "Task Tracker (cleaned up)" (or whatever you chose).
2. **Ids are 1-based** instead of 0-based indexes. The `d` and `p` commands take an id, and the list output shows the id.
3. **Confirmation messages** are more informative ("Added #1: Make Bed (p1)" instead of just "ok").

If any *other* behaviour is different, that is a regression. Go find it.

### Step 5.2: Try an extension

Add **Feature B from Question 4.4 (delete by id)** to your cleaned-up version. You should need to touch exactly three files:

- **`repo.py`:** add a `remove(self, task_id)` method to `InMemoryTaskRepository` (and to the `TaskRepository` protocol if you defined one).
- **`service.py`:** add a `delete_task(self, task_id)` method.
- **`cli.py`:** add a `handle_delete` function and an `elif command == "x"` branch in `run()`.

Build, run, test. **Notice that `models.py` does not need to change at all.** That is the architectural payoff.

Compare to what the same feature would have required in `bad.py`. In the bad version you would have had to add another `elif cmd.startswith("x"):` branch alongside the `d` and `p` branches, with its own copy of the split/parse/range-check pattern. Every addition makes the function longer and harder to read. In the clean version, each addition is a small focused unit.

---

## Part 6: Reflection

Answer in your notebook. These are open-ended.

1. **Layered architecture vs line-level clean code.** Lab 3-1 (Java) emphasized the layers. This lab emphasized line-level clean code. Did one feel more impactful than the other? Why? Could you imagine a codebase where one matters and the other does not?

2. **The order of the cleanup.** The lab cleaned things up in a specific order: names first, dataclass second, repository third, service fourth, function split fifth. Why this order? What goes wrong if you try to split the function first, before introducing the dataclass?

3. **Choices the lab did not specify.** Look back at your notebook from Part 3. What decisions did you have to make that the instructions did not pin down? Variable names, where to put a helper, how to phrase an error message? How did you decide?

4. **The strongest smell.** Of all the smells you found in Part 2, which one was the most painful to read in the original? Which one was the most painful to fix? Are they the same smell?

5. **When to stop cleaning up.** Could this code be improved further? List three things you could still do (add type hints everywhere, write tests, use `match` statements for command dispatch, factor out the validation, add logging). For each one, decide whether it would be worth doing in a real project.

6. **What you would do differently.** If you were starting again, what would you change about the order or the choices?

---


## Reference: Clean Code Smells, in Brief

| Smell | What it looks like | What to do |
|------|------|------|
| **Vague names** | `T`, `x`, `p`, `tmp`, `data` | Rename to what the value *is* in the domain. Short names are fine for short scopes; never use short names for module-level globals. |
| **Magic numbers/strings** | A literal whose meaning depends on knowledge outside the file | Replace with a named constant or an enum. |
| **Long function with mixed abstractions** | One function that does I/O, validation, business logic, and output | Break into small single-purpose helpers, one per responsibility. |
| **"What" comments** | `# Increment the counter` above `counter += 1` | Delete. Comments should explain *why*, not *what*. |
| **Bare except** | `except:` with no exception type | Catch the specific exception you expect. Let the rest crash. |
| **Duplication** | Two near-identical blocks differing only in details | Extract into a function parameterized over the differences. |
| **Coupling to data shape** | Code that knows `x[0]` is the name and `x[1]` is the age | Replace the list/tuple with a dataclass or named tuple. |
| **Global mutable state** | A module-level list or dict that functions read and write | Encapsulate in a class. |
| **Mixed layers** | UI, validation, business logic, and storage all in one function | Separate into modules: domain, repository, service, CLI. |

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'clean_task'`.**
Run the program from the *parent* directory of `clean_task/`, not from inside it. Use `python3 -m clean_task.cli`, not `python3 clean_task/cli.py`.

**`ImportError: attempted relative import with no known parent package`.**
You ran the file directly (e.g., `python3 cli.py` inside `clean_task/`). Use `python3 -m clean_task.cli` from the parent directory instead. The `-m` flag is what makes `clean_task` register as a package.

**`SyntaxError` on `list[Task]` or `Task | None`.**
You are on Python 3.9 or earlier. The lab requires 3.10+. Either upgrade, or replace `list[Task]` with `List[Task]` (importing `List` from `typing`) and `Task | None` with `Optional[Task]`.

**The `a` command still crashes on an empty title.**
You probably did not catch the `ValueError` from `Task.__post_init__`. Look at the try/except around `service.create_task(...)` in your `handle_add` function.

**Priority `Priority(99)` raises a different error than expected.**
`IntEnum(99)` raises `ValueError` with the message `99 is not a valid Priority`. If you want a custom message ("Priority must be 1, 2, or 3") you need a `from_int` classmethod on the enum that re-raises with your message, like the reference solution does.

**Circular import between `repo.py` and `service.py`.**
This usually means you imported `TaskService` from `repo.py` for type annotation purposes. The right direction is `service.py` imports from `repo.py`, never the reverse. If you only need the import for type hints, use `from __future__ import annotations` at the top of the file and the strings-as-types behaviour will let you skip the import entirely.

---

## Further Reading

- **Clean Code** (Robert C. Martin), chapters on Naming, Functions, and Comments.
- **Refactoring** (Martin Fowler), 2nd edition, especially the "Bad Smells in Code" chapter.
- **Fluent Python** (Luciano Ramalho), 2nd edition, for the Pythonic idioms (dataclasses, enums, Protocols).
- **Architecture Patterns with Python** (Percival and Gregory), free online at <https://www.cosmicpython.com/>, for the layered-architecture style you applied here.
- **PEP 8** (style guide) and **PEP 257** (docstring conventions): <https://peps.python.org/pep-0008/> and <https://peps.python.org/pep-0257/>.
