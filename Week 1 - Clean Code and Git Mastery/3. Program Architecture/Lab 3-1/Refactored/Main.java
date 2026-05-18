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
