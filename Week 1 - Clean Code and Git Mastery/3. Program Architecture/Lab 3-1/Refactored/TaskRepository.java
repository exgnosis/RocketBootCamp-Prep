import java.util.List;
import java.util.Optional;

public interface TaskRepository {
    Task add(String title, Priority priority);
    List<Task> list();
    Optional<Task> findById(int id);
    boolean markDone(int id);
}
