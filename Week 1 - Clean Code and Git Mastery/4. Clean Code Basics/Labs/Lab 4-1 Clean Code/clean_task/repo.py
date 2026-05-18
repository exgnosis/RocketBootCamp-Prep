"""Task storage abstraction.

Defines the TaskRepository protocol that the application service depends
on, plus a default in-memory implementation. Swap the implementation to
change where tasks are stored (file, database, remote service) without
touching any other layer.
"""

from typing import Protocol

from .models import Priority, Task


class TaskRepository(Protocol):
    """The storage operations the application needs."""

    def add(self, title: str, priority: Priority) -> Task: ...
    def list(self) -> list[Task]: ...
    def find_by_id(self, task_id: int) -> Task | None: ...
    def mark_done(self, task_id: int) -> bool: ...
    def change_priority(self, task_id: int, new_priority: Priority) -> bool: ...


class InMemoryTaskRepository:
    """A simple dict-backed store. Preserves insertion order."""

    def __init__(self) -> None:
        self._storage: dict[int, Task] = {}
        self._next_id: int = 1

    def add(self, title: str, priority: Priority) -> Task:
        task = Task(id=self._next_id, title=title, priority=priority)
        self._storage[self._next_id] = task
        self._next_id += 1
        return task

    def list(self) -> list[Task]:
        return list(self._storage.values())

    def find_by_id(self, task_id: int) -> Task | None:
        return self._storage.get(task_id)

    def mark_done(self, task_id: int) -> bool:
        task = self._storage.get(task_id)
        if task is None:
            return False
        task.mark_done()
        return True

    def change_priority(self, task_id: int, new_priority: Priority) -> bool:
        task = self._storage.get(task_id)
        if task is None:
            return False
        task.change_priority(new_priority)
        return True
