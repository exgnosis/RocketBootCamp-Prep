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
