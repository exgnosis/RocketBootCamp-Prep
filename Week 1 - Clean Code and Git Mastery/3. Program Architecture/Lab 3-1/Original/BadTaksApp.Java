import java.util.*;

class Task {
    //  Public instance variables (no encapsulation)
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
                // ❌ UI directly mutates data structure by index
                String[] parts = cmd.split("\\s+");
                if (parts.length > 1) {
                    int idx = Integer.parseInt(parts[1]);
                    if (idx >= 0 && idx < BadTaskStore.tasks.size()) {
                        BadTaskStore.tasks.get(idx).done = true; //  direct field write
                    }
                }
            } else if (cmd.equals("q")) {
                break;
            }
        }
        sc.close();
    }
}