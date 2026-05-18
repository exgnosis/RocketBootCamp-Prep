"""Command-line front end for the task tracker.

Reads commands from stdin, parses them, and delegates to TaskService.
Knows nothing about how tasks are stored or how Priority is implemented
beyond the integer that the user types.
"""

from .repo import InMemoryTaskRepository
from .service import TaskService
from .models import Task

PROMPT = "[a]dd [l]ist [d]one <id> [p]rio <id> <1-3> [q]uit: "
BANNER = "Task Tracker (cleaned up)"


def format_task(task: Task) -> str:
    box = "x" if task.done else " "
    return f"{task.id}: [{box}] {task.title} (p{int(task.priority)})"


def handle_add(service: TaskService) -> None:
    title = input("title: ")
    priority_text = input("priority (1..3): ").strip()
    try:
        priority_value = int(priority_text)
    except ValueError:
        print("Error: priority must be an integer 1, 2, or 3")
        return
    try:
        task = service.create_task(title, priority_value)
    except ValueError as exc:
        print(f"Error: {exc}")
        return
    print(f"Added #{task.id}: {task.title} (p{int(task.priority)})")


def handle_list(service: TaskService) -> None:
    tasks = service.list_tasks()
    if not tasks:
        print("(no tasks)")
        return
    for task in tasks:
        print(format_task(task))


def handle_done(service: TaskService, args: list[str]) -> None:
    if len(args) < 1:
        print("Usage: d <id>")
        return
    try:
        task_id = int(args[0])
    except ValueError:
        print("Task id must be an integer.")
        return
    if service.complete_task(task_id):
        print("Marked done.")
    else:
        print("No such task id.")


def handle_priority(service: TaskService, args: list[str]) -> None:
    if len(args) < 2:
        print("Usage: p <id> <1-3>")
        return
    try:
        task_id = int(args[0])
        priority_value = int(args[1])
    except ValueError:
        print("Both id and priority must be integers.")
        return
    try:
        ok = service.set_priority(task_id, priority_value)
    except ValueError as exc:
        print(f"Error: {exc}")
        return
    if ok:
        print("Priority updated.")
    else:
        print("No such task id.")


def run() -> None:
    service = TaskService(InMemoryTaskRepository())
    print(BANNER)
    while True:
        line = input(PROMPT).strip()
        if not line:
            continue
        command, *args = line.split()
        if command == "a":
            handle_add(service)
        elif command == "l":
            handle_list(service)
        elif command == "d":
            handle_done(service, args)
        elif command == "p":
            handle_priority(service, args)
        elif command == "q":
            break
        else:
            print("Unknown command.")


if __name__ == "__main__":
    run()
