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