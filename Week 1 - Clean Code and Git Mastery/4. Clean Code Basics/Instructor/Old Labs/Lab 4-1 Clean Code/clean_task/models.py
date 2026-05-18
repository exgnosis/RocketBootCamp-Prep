
from dataclasses import dataclass

@dataclass
class Task:
    title: str
    done: bool = False
    priority: int = 2  # 1=high, 3=low

    def mark_done(self) -> "Task":
        self.done = True
        return self
