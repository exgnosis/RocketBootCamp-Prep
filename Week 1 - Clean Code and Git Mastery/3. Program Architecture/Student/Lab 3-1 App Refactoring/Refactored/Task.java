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
