from typing import Tuple
from .repo import InMemoryTaskRepository
from .service import TaskService


PROMPT = "[a]dd [l]ist [d]one <idx> [p]rio <idx> <1-3> [q]uit: "


class CLI:
    def __init__(self, service: TaskService):
        self.svc = service


    def format_row(self, i: int) -> str:
        t = self.svc.list()[i]
        box = "x" if t.done else " "
        return f"{i}: [{box}] {t.title} (p{t.priority})"


    def handle(self, line: str) -> Tuple[bool, str]:
        parts = (line or "").strip().split()
        if not parts:
            return True, ""
        cmd = parts[0]
        try:
            if cmd == "a":
                title = input("title: ")
                pr_raw = input("priority (1..3): ") or "2"
                pr = int(pr_raw)
                self.svc.add(title, pr)
                return True, "ok"
            elif cmd == "l":
                rows = [self.format_row(i) for i, _ in enumerate(self.svc.list())]
                return True, "\n".join(rows)
            elif cmd == "d":
                idx = int(parts[1])
                self.svc.mark_done(idx)
                return True, "done"
            elif cmd == "p":
                idx = int(parts[1]); pr = int(parts[2])
                self.svc.set_priority(idx, pr)
                return True, "prio ok"
            elif cmd == "q":
                return False, "bye"
            else:
                return True, "???"
        except (IndexError, ValueError) as e:
            return True, str(e)




def main() -> int:
    repo = InMemoryTaskRepository()
    svc = TaskService(repo)
    cli = CLI(svc)
    print("Task Trkr v1 (clean)")
    running = True
    while running:
        line = input(PROMPT)
        running, out = cli.handle(line)
        if out:
            print(out)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())