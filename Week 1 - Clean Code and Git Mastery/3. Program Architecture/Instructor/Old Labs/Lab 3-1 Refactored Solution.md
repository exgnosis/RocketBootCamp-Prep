# Lab 3-1 Refactoring


## Business Logic
- This is also called the domain layer because it contains the core business concepts of that domain, in this case, task management.

### Priority (enum)

```java
public enum Priority {
    HIGH(1), MEDIUM(2), LOW(3);

    private final int level;
    Priority(int level) { this.level = level; }
    public int level() { return level; }

    public static Priority fromInt(int n) {
        return switch (n) {
            case 1 -> HIGH;
            case 2 -> MEDIUM;
            case 3 -> LOW;
            default -> throw new IllegalArgumentException("Priority must be 1..3");
        };
    }
}

```
- Responsibility: Encodes valid priority values and their meaning (HIGH/MEDIUM/LOW, with levels 1–3).
- Rationale: Removes “magic numbers” and centralizes validation/translation (fromInt).
- Advantages: Pure domain concept—no I/O, no framework dependencies. Easy to test.

### Task (entity)

```java
import java.util.Objects;

public class Task {
    private final int id;
    private String title;
    private Priority priority;
    private boolean done;

    public Task(int id, String title, Priority priority) {
        this.id = id;
        this.title = Objects.requireNonNull(title).trim();
        if (this.title.isEmpty()) {
            throw new IllegalArgumentException("Title cannot be empty");
        }
        this.priority = Objects.requireNonNull(priority);
        this.done = false;
    }

    public int getId() { return id; }
    public String getTitle() { return title; }
    public Priority getPriority() { return priority; }
    public boolean isDone() { return done; }

    public void rename(String newTitle) {
        String t = Objects.requireNonNull(newTitle).trim();
        if (t.isEmpty()) throw new IllegalArgumentException("Title cannot be empty");
        this.title = t;
    }

    public void changePriority(Priority p) {
        this.priority = Objects.requireNonNull(p);
    }

    public void markDone() { this.done = true; }
}

```

- Responsibility: Represents a to-do item and guards its own invariants (non-empty title, valid priority). Exposes behavior (markDone, rename, changePriority) instead of raw field writes.
  Rationale: Enforces encapsulation and high cohesion; all rules about a task live here.
- Advantages: Pure domain model. Other layers call methods rather than mutating fields, reducing coupling.

## Data access (infrastructure / adapter)

- Order to increase suppleness and reduce the coupling of the data and code, we create a repository interface and an implementation

### TaskRepository (interface)

```java
import java.util.List;
import java.util.Optional;

public interface TaskRepository {
    Task add(String title, Priority priority);
    List<Task> list();
    Optional<Task> findById(int id);
    boolean markDone(int id);
}

```
- Responsibility: Defines the capabilities the app needs for persistence: add, list, findById, markDone.
- Rationale" Creates a stable boundary between the core app and storage details. Anything that can store tasks (memory, file, DB, HTTP API) can implement this.
- Advantages: The domain/app layers depend on this abstraction, not a concrete store.

### InMemoryTaskRepository (implementation)

```java
import java.util.*;

public class InMemoryTaskRepository implements TaskRepository {
    private final Map<Integer, Task> storage = new LinkedHashMap<>();
    private int nextId = 1;

    @Override
    public Task add(String title, Priority priority) {
        int id = nextId++;
        Task t = new Task(id, title, priority);
        storage.put(id, t);
        return t;
    }

    @Override
    public List<Task> list() {
        return new ArrayList<>(storage.values());
    }

    @Override
    public Optional<Task> findById(int id) {
        return Optional.ofNullable(storage.get(id));
    }

    @Override
    public boolean markDone(int id) {
        Task t = storage.get(id);
        if (t == null) return false;
        t.markDone();
        return true;
    }
}

```

- Responsibility: A concrete, in-process map-backed store for tasks.
- Rationale: Provides a simple, fast implementation of the repository interface
- Advantages: “Interface” that satisfies `TaskRepository`. Swappable with a DB-backed repo later without touching service/UI.

## Application layer (use cases / orchestration)

- This is a layer of functionality that various UIs can call to get the task management functionality. 
- It decouples the UX from the business processes
- This allows for multiple interfaces to be used without having to recode the rest of the application
- You can think of this as an interface to the underlying app functionality

### TaskService (use-case/application service)

```Java
import java.util.List;

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

- Responsibility: Orchestrates use cases and enforces application-level rules (e.g., mapping int to Priority, delegating to the repo, deciding success/failure of operations).
- Rationale: Keeps UI thin and persistence ignorant of business decisions. Concentrates workflows and validations that cross entities or require coordination.
- Advantages: Depends on the port (TaskRepository) and on domain (Task, Priority), but not on UI or concrete storage. -
- This layer is where you’d add transactions, logging, or policies.

## Presentation layer (UI)

### Main (CLI)

```Java
import java.util.List;
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        TaskRepository repo = new InMemoryTaskRepository();
        TaskService service = new TaskService(repo);

        Scanner sc = new Scanner(System.in);
        System.out.println("Tiny Task Tracker (refactored)");
        while (true) {
            System.out.print("[a]dd, [l]ist, [d]one <id>, [q]uit: ");
            String line = sc.nextLine().trim();

            if (line.equals("a")) {
                System.out.print("title: ");
                String title = sc.nextLine();
                System.out.print("priority (1..3): ");
                String pStr = sc.nextLine();
                try {
                    int p = Integer.parseInt(pStr);
                    Task t = service.createTask(title, p);
                    System.out.println("Added #" + t.getId() + ": " + t.getTitle() + " (p" + t.getPriority().level() + ")");
                } catch (Exception e) {
                    System.out.println("Error: " + e.getMessage());
                }

            } else if (line.equals("l")) {
                List<Task> tasks = service.listTasks();
                if (tasks.isEmpty()) {
                    System.out.println("(no tasks)");
                } else {
                    for (Task t : tasks) {
                        System.out.printf("%d: [%s] %s (p%d)%n",
                                t.getId(), (t.isDone() ? "x" : " "), t.getTitle(), t.getPriority().level());
                    }
                }

            } else if (line.startsWith("d")) {
                String[] parts = line.split("\\s+");
                if (parts.length < 2) {
                    System.out.println("Usage: d <id>");
                    continue;
                }
                try {
                    int id = Integer.parseInt(parts[1]);
                    boolean ok = service.completeTask(id);
                    System.out.println(ok ? "Marked done." : "No such task id.");
                } catch (NumberFormatException nfe) {
                    System.out.println("Task id must be an integer.");
                }

            } else if (line.equals("q")) {
                break;

            } else {
                System.out.println("Unknown command.");
            }
        }
        sc.close();
    }
}

```

- Responsibility: Handles I/O only—reads commands, prints results. Converts free-form user input into structured calls on TaskService.
- Rationale: Prevents UI from knowing about domain internals or storage details (no direct field writes, no List indexing into a global).
- Advantages:  Depends only on the service API; can be replaced by a GUI/web/REST layer without touching the domain or repository.

## Test
- Run this version and verify that it has all the functionality of the previous version.

## End