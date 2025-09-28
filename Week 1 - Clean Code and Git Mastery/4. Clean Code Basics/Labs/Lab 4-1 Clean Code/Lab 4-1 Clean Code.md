# lab 4-1: Clean Code

## Objective

- This lab will use the same example as the previous lab, but this time written in Python to demonstrate some clean code ideas
- Note that there is a lot of overlap in the concepts we saw in previous modules and labs.
- This is because we see similar design and construction motifs based on similar ideas about design and composition

## The Bad Version

- The following is the unclean Python code.

```Python
# bad_task_app.py
# Intentional anti-patterns: globals, magic values, long function, mixed I/O & logic,
# vague names, duplication, no tests, no error handling, comments that explain "what".
T = []  # tasks: [ [title, done, prio] ]

def run():
    print("Task Trkr v0")
    while True:
        cmd = input("[a]dd [l]ist [d]one <idx> [p]rio <idx> <1-3> [q]uit: ").strip()
        if cmd == "a":
        # Process if the option is a
            t = input("title: ")
            p = input("priority (1..3): ")
            if p == "": p = "2"  # default medium
            try:
                p = int(p)
            except:
                p = 2
            if p < 1 or p > 3: p = 2
            T.append([t, False, p])
            print("ok")
        elif cmd == "l":
          # Process if the option is l
            i = 0
            for x in T:
                box = "x" if x[1] else " "
                pr = x[2]
                # Duplicate formatting logic scattered
                print(str(i) + ": [" + box + "] " + x[0] + " (p" + str(pr) + ")")
                i += 1
        elif cmd.startswith("d"):
            parts = cmd.split()
            if len(parts) > 1:
                try:
                    idx = int(parts[1])
                    if idx >= 0 and idx < len(T):
                        T[idx][1] = True
                        print("done")
                except:
                    print("bad idx")
        elif cmd.startswith("p"):
          # Process if the option is p
            parts = cmd.split()
            if len(parts) > 2:
                try:
                    idx = int(parts[1]); pr = int(parts[2])
                    if idx >= 0 and idx < len(T):
                        if pr < 1 or pr > 3: pr = 2
                        T[idx][2] = pr
                        print("prio ok")
                except:
                    print("bad args")
        elif cmd == "q":
          # Process if the option is q
            break
        else:
            print("???")

if __name__ == "__main__":
    run()

```

### Run the code. 
- Open an terminal window and locate to the directory with the `Bad.py` file
- Run the code and ensure it's the same functionality as the previous Java version.

```bash
~/working$ python Bad.py
Task Trkr v0
[a]dd [l]ist [d]one <idx> [p]rio <idx> <1-3> [q]uit: a
title: Make Bed
priority (1..3): 1
ok
[a]dd [l]ist [d]one <idx> [p]rio <idx> <1-3> [q]uit: l
0: [ ] Make Bed (p1)
[a]dd [l]ist [d]one <idx> [p]rio <idx> <1-3> [q]uit: d 0
done
[a]dd [l]ist [d]one <idx> [p]rio <idx> <1-3> [q]uit: l
0: [x] Make Bed (p1)
[a]dd [l]ist [d]one <idx> [p]rio <idx> <1-3> [q]uit: q
(base) rod@exgnosis:~/working$ 

```
## The Code Smells 

- Vague names (T, x, t, p) and “mental mapping” for readers to decode intent
- One long, mixed-abstraction loop doing many things; functions should be small and “do one thing”
- Mixing UI, business logic, and storage (tight coupling, hard to test/extend) — a common “boundaries” and “systems” concern

### Task.
- In the resources folder, there is an article on code smells in Python.
- Using that as a starting point, see what other code smells you can find.
- If you feel comfortable enough programming in Python, refactor this code.
- If not, just copy and implement the solution provide

## End