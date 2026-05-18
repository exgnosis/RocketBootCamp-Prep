# lab 4-1: Clean Code Refactoring

## Modularization

- The first thing is to some basic modularization just like we did with the Java example
- Large blobs of code are both inefficient from an engineering perspective and difficult to understand
- A wall of course code that isn't modularized is not modularized is too complicated and disorganized for developers to understand without a lot of difficulty
  - One symptom of this is when someone reading the code has to draw some sort of structural diagram to understand it.
- In Python, we modularize by creating separating modules into separate file.

### Module Structure

```text
clean_task/
models.py
repo.py
service.py
cli.py
```

## Refactoring
1. Introduce a **domain model** (`Task`).
2. Create a **repository** abstraction; start with in‑memory.
3. Create an **application service** to hold use cases: add, list, done, set_priority.
4. Keep a **thin CLI** that parses commands and delegates to the service.

## Exercise

- Run the cleaned up version from the directory above the `clean_task` directory

```bash
python  -m  clean_task.clo
```

- Confirm the same functionality

- Discuss what sort of clean code refactorings you can see that have been done between the two versions.

## End
