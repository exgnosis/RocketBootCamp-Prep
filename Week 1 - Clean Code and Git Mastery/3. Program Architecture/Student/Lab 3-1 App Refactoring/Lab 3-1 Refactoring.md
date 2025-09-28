# Lab 3-1:  Refactoring a Blob

## Objectives

- In this lab you will refactor a tightly coupled, spaghetti code blob into a modular, cohesive Java App
- This lab will cover some of the content from the section on engineering principles as well as the section on program design

## Project Description

- Below is a tiny “Task Tracker” app. 
- The starter code is intentionally bad: public fields, god-class behavior, data access + UI + domain logic all tangled together.
- The other important point is that this code is just a monolith of code, which is not how Java programs are intended to be architected.
- The code is below and is also in the file `BadTaskApp.java`


```java
import java.util.*;

class Task {
    // Public instance variables (no encapsulation)
    public String title;
    public boolean done;
    public int priority; // 1=high, 3=low
}

class BadTaskStore {
    //  Global mutable state, no abstraction boundary
    public static List<Task> tasks = new ArrayList<>();
}

public class BadTaskApp {
    //  Mixes UI, business logic, and data access in one place
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        System.out.println("Task Tracker (bad version)");
        while (true) {
            System.out.print("[a]dd, [l]ist, [d]one <idx>, [q]uit: ");
            String cmd = sc.nextLine().trim();

            if (cmd.equals("a")) {
                Task t = new Task();
                System.out.print("title: ");
                t.title = sc.nextLine();           //  direct field access
                System.out.print("priority (1..3): ");
                t.priority = Integer.parseInt(sc.nextLine());
                t.done = false;
                BadTaskStore.tasks.add(t);         //  store accessed directly
            } else if (cmd.equals("l")) {
                int i = 0;
                for (Task t : BadTaskStore.tasks) {
                    System.out.println(i + ": [" + (t.done ? "x" : " ") + "] "
                            + t.title + " (p" + t.priority + ")");
                    i++;
                }
            } else if (cmd.startsWith("d")) {
                //  UI directly mutates data structure by index
                String[] parts = cmd.split("\\s+");
                if (parts.length > 1) {
                    int idx = Integer.parseInt(parts[1]);
                    if (idx >= 0 && idx < BadTaskStore.tasks.size()) {
                        BadTaskStore.tasks.get(idx).done = true; // ❌ direct field write
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

- Compile and run the code
- From a Java functional perspective, the code compiles and executes.
- Experiment with creating task and marking it done.
- The code works, but it is a mess.

## Refactoring

The following are the steps for the refactoring:

1. Encapsulate the domain (Task)
   - Make fields private.
   - Replace raw int priority with an enum.
   - Provide behavior methods (e.g., markDone()), not just data.
2. Remove global mutable state 
   - Replace BadTaskStore.tasks with a TaskRepository interface.
   - Implement an InMemoryTaskRepository.
3. Introduce an application/service layer
   - TaskService mediates between UI and repository.
   - All validation and orchestration live here (not in UI).
4. Separate the UI
   - Keep Main (CLI) responsible only for I/O and command parsing.
   - UI never touches fields or the repository directly.
5. Tighten input handling
   - Validate priority, command formats, and indexes.
   - Make service/repo responsible for domain-safe operations.

The code also has to be modularized by splitting the classes into separate files which represent modules


## Options

- If you are comfortable writing Java code, you can try your own refactoring.
- If you are not comfortable with the scope of this project, just examine the solution and confirm that the refactoring solution is a better design.

## End