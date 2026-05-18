from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List
from .models import Task


class TaskRepository(ABC):
    @abstractmethod
    def list(self) -> List[Task]: ...


    @abstractmethod
    def add(self, task: Task) -> None: ...


    @abstractmethod
    def update(self, index: int, task: Task) -> None: ...


class InMemoryTaskRepository(TaskRepository):
    def __init__(self, initial=None):
        self._tasks: List[Task] = list(initial or [])


    def list(self) -> List[Task]:
        return list(self._tasks)


    def add(self, task: Task) -> None:
        self._tasks.append(task)


    def update(self, index: int, task: Task) -> None:
        if index < 0 or index >= len(self._tasks):
            raise IndexError("Task index out of range")
        self._tasks[index] = task