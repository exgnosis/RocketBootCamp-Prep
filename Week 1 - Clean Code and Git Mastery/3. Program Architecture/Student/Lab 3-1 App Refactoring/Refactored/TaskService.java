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
