"""Domain models for the task tracker.

Contains the Priority enum and the Task entity. No I/O, no storage,
no framework dependencies live in this module.
"""

from dataclasses import dataclass, field
from enum import IntEnum


class Priority(IntEnum):
    """Task priority. Lower numbers are more urgent (1 = HIGH)."""

    HIGH = 1
    MEDIUM = 2
    LOW = 3

    @classmethod
    def from_int(cls, value: int) -> "Priority":
        """Return the Priority for an integer 1..3, or raise ValueError."""
        try:
            return cls(value)
        except ValueError as exc:
            raise ValueError("Priority must be 1, 2, or 3") from exc


@dataclass
class Task:
    """A single to-do item.

    A Task owns its own invariants: the title is non-empty after stripping,
    the priority is a valid Priority value, and `done` starts as False.
    Callers mutate state through methods (mark_done, rename, change_priority)
    rather than by writing fields directly.
    """

    id: int
    title: str
    priority: Priority
    done: bool = field(default=False)

    def __post_init__(self) -> None:
        self.title = self.title.strip()
        if not self.title:
            raise ValueError("Title cannot be empty")
        if not isinstance(self.priority, Priority):
            raise TypeError("priority must be a Priority value")

    def mark_done(self) -> None:
        self.done = True

    def rename(self, new_title: str) -> None:
        stripped = new_title.strip()
        if not stripped:
            raise ValueError("Title cannot be empty")
        self.title = stripped

    def change_priority(self, new_priority: Priority) -> None:
        if not isinstance(new_priority, Priority):
            raise TypeError("priority must be a Priority value")
        self.priority = new_priority
