"""Application service for the task tracker.

Sits between the CLI and the repository. Translates raw input types
(such as a plain int priority) into domain types, calls the repository,
and returns results the CLI can render directly.
"""

from .models import Priority, Task
from .repo import TaskRepository


class TaskService:
    def __init__(self, repository: TaskRepository) -> None:
        self._repo = repository

    def create_task(self, title: str, priority_value: int) -> Task:
        priority = Priority.from_int(priority_value)
        return self._repo.add(title, priority)

    def list_tasks(self) -> list[Task]:
        return self._repo.list()

    def complete_task(self, task_id: int) -> bool:
        return self._repo.mark_done(task_id)

    def set_priority(self, task_id: int, priority_value: int) -> bool:
        priority = Priority.from_int(priority_value)
        return self._repo.change_priority(task_id, priority)
