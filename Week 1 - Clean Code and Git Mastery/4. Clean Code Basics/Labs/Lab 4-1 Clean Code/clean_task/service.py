from typing import List
from .models import Task
from .repo import TaskRepository


class TaskService:
    def __init__(self, repo: TaskRepository):
        self.repo = repo


    def list(self) -> List[Task]:
        return self.repo.list()


    def add(self, title: str, priority: int = 2) -> Task:
        title = (title or "").strip()
        if not title:
            raise ValueError("Title required")
        if priority not in (1, 2, 3):
            raise ValueError("Priority must be 1, 2, or 3")
        task = Task(title=title, priority=priority)
        self.repo.add(task)
        return task


    def mark_done(self, index: int) -> Task:
        tasks = self.repo.list()
        if index < 0 or index >= len(tasks):
            raise IndexError("Task index out of range")
        task = tasks[index]
        task.mark_done()
        self.repo.update(index, task)
        return task


    def set_priority(self, index: int, priority: int) -> Task:
        if priority not in (1, 2, 3):
            raise ValueError("Priority must be 1, 2, or 3")
        tasks = self.repo.list()
        if index < 0 or index >= len(tasks):
            raise IndexError("Task index out of range")
        task = tasks[index]
        task.priority = priority
        self.repo.update(index, task)
        return task