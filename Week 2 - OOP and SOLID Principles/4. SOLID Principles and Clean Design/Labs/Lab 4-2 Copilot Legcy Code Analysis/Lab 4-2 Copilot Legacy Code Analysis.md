# Lab 4-2: Analyzing Legacy Code with GitHub Copilot (Claude Sonnet)

## Overview

Legacy code is one of the highest-value use cases for an AI coding assistant. The code is often unfamiliar (a different era, a different language, conventions that have fallen out of use), the original authors are unavailable, and the cost of a wrong assumption is high. Copilot with a strong reasoning model like Claude Sonnet 4.6 can read code in any language it has seen during training, explain its intent in plain English, identify problems, and suggest modernizations.

In this lab you will analyze three legacy files using GitHub Copilot in Ask mode:

1. **PAYROLL.CBL**: A COBOL payroll program from the 1980s. Most students will not have read COBOL before.
2. **user_registry.c**: A small C program from the late 1990s with several classic memory-safety and security issues.
3. **OrderProcessor.java**: A Java 8 class from 2014 that works correctly but uses idioms that are out of date in modern Java.

For each file you will ask Copilot a structured series of questions, capture its findings, and form a judgement about what to do with the code.

**Estimated time:** 45 to 60 minutes
**Difficulty:** Beginner to intermediate

**Prerequisites:**

- A paid GitHub Copilot plan (Pro, Pro+, Business, or Enterprise) with Claude models available in the picker.
- VS Code with the **GitHub Copilot Chat** extension installed and authenticated.
- Claude Sonnet 4.6 selected in the chat model picker.
- Completion of Lab 6-1 (or equivalent familiarity with Copilot Chat modes).

---

## Learning Objectives

By the end of this lab, you will be able to:

1. Use Copilot in **Ask mode** to perform structured analysis of unfamiliar code without modifying it.
2. Frame prompts that produce useful, comparable analyses across different languages.
3. Identify common categories of legacy-code problems: correctness, security, maintainability, idiom drift.
4. Distinguish between "this code is broken" and "this code is dated but correct."
5. Decide which legacy issues are worth fixing now versus deferring or rewriting wholesale.

---

## Part 1: Set Up the Workspace

### Step 1.1: Create the lab directory

In a terminal:

```bash
mkdir -p ~/legacy-lab
cd ~/legacy-lab
code .
```

VS Code opens the empty directory as a workspace. When prompted, click **Yes, I trust the authors**.

### Step 1.2: Create the three legacy files

You will create three files in this workspace. Copy each block below into a new file with the matching name, then save.

> Do not edit the contents. The whole point is to analyze the code exactly as a maintenance programmer would inherit it.

**File 1: `PAYROLL.CBL`**

```cobol
      ******************************************************************
      * PAYROLL.CBL
      * Original author: J. Henderson
      * Last modified:   1987-03-12
      *
      * Reads an employee record from a fixed-format input file,
      * computes weekly gross pay, applies a flat-rate tax deduction,
      * and writes a payslip line to PAYSLIP.OUT.
      *
      * NOTE FROM IT (2003): The Payroll Modernization Project will
      * replace this program. Do not extend. Maintenance only.
      ******************************************************************
       IDENTIFICATION DIVISION.
       PROGRAM-ID. PAYROLL.

       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT EMP-FILE ASSIGN TO "EMP.DAT"
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT PAY-FILE ASSIGN TO "PAYSLIP.OUT"
               ORGANIZATION IS LINE SEQUENTIAL.

       DATA DIVISION.
       FILE SECTION.
       FD  EMP-FILE.
       01  EMP-RECORD.
           05  EMP-ID        PIC 9(5).
           05  EMP-NAME      PIC X(20).
           05  EMP-RATE      PIC 9(3)V99.
           05  EMP-HOURS     PIC 9(3)V99.
           05  EMP-DEPT      PIC X(3).

       FD  PAY-FILE.
       01  PAY-LINE          PIC X(80).

       WORKING-STORAGE SECTION.
       01  WS-EOF            PIC X VALUE "N".
           88  END-OF-FILE   VALUE "Y".

       01  WS-CALC.
           05  WS-GROSS      PIC 9(5)V99 VALUE 0.
           05  WS-TAX        PIC 9(5)V99 VALUE 0.
           05  WS-NET        PIC 9(5)V99 VALUE 0.
           05  WS-OT-HOURS   PIC 9(3)V99 VALUE 0.
           05  WS-REG-HOURS  PIC 9(3)V99 VALUE 0.

       01  WS-CONSTANTS.
           05  WS-STD-WEEK   PIC 9(3)V99 VALUE 40.00.
           05  WS-OT-MULT    PIC 9V99    VALUE 1.50.
           05  WS-TAX-RATE   PIC 9V99    VALUE 0.22.

       01  WS-OUTPUT.
           05  FILLER        PIC X(8)  VALUE "PAYSLIP ".
           05  OUT-ID        PIC 9(5).
           05  FILLER        PIC X(2)  VALUE "  ".
           05  OUT-NAME      PIC X(20).
           05  FILLER        PIC X(2)  VALUE "  ".
           05  OUT-GROSS     PIC $$$,$$9.99.
           05  FILLER        PIC X(2)  VALUE "  ".
           05  OUT-NET       PIC $$$,$$9.99.

       PROCEDURE DIVISION.
       MAIN-PARA.
           OPEN INPUT EMP-FILE
                OUTPUT PAY-FILE.
           PERFORM READ-PARA.
           PERFORM PROCESS-PARA UNTIL END-OF-FILE.
           CLOSE EMP-FILE
                 PAY-FILE.
           STOP RUN.

       READ-PARA.
           READ EMP-FILE
               AT END MOVE "Y" TO WS-EOF
           END-READ.

       PROCESS-PARA.
           IF EMP-HOURS > WS-STD-WEEK
               COMPUTE WS-OT-HOURS = EMP-HOURS - WS-STD-WEEK
               MOVE WS-STD-WEEK TO WS-REG-HOURS
               COMPUTE WS-GROSS =
                   (WS-REG-HOURS * EMP-RATE) +
                   (WS-OT-HOURS * EMP-RATE * WS-OT-MULT)
           ELSE
               MOVE EMP-HOURS TO WS-REG-HOURS
               MOVE 0 TO WS-OT-HOURS
               COMPUTE WS-GROSS = WS-REG-HOURS * EMP-RATE
           END-IF.

           COMPUTE WS-TAX = WS-GROSS * WS-TAX-RATE.
           COMPUTE WS-NET = WS-GROSS - WS-TAX.

           MOVE EMP-ID    TO OUT-ID.
           MOVE EMP-NAME  TO OUT-NAME.
           MOVE WS-GROSS  TO OUT-GROSS.
           MOVE WS-NET    TO OUT-NET.

           WRITE PAY-LINE FROM WS-OUTPUT.
           PERFORM READ-PARA.

       END PROGRAM PAYROLL.
```

**File 2: `user_registry.c`**

```c
/*
 * user_registry.c
 *
 * Maintains an in-memory list of registered users. Reads commands from
 * stdin: "add <name> <age>", "find <name>", "list", "quit".
 *
 * Original author: M. Petrov, 1998
 * Last touched:    2004, prior to the Y2.038K audit
 *
 * Builds with: gcc -o registry user_registry.c
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_USERS 100

struct user {
    char name[32];
    int  age;
};

struct user *users[MAX_USERS];
int user_count = 0;

void add_user(char *name, int age) {
    struct user *u = malloc(sizeof(struct user));
    strcpy(u->name, name);
    u->age = age;
    users[user_count] = u;
    user_count = user_count + 1;
}

struct user *find_user(char *name) {
    int i;
    for (i = 0; i <= user_count; i++) {
        if (strcmp(users[i]->name, name) == 0) {
            return users[i];
        }
    }
    return NULL;
}

void list_users() {
    int i;
    printf("--- Registered Users (%d) ---\n", user_count);
    for (i = 0; i < user_count; i++) {
        printf("%s (age %d)\n", users[i]->name, users[i]->age);
    }
}

int main(int argc, char *argv[]) {
    char command[16];
    char name[64];
    int  age;
    char line[256];

    printf("Registry ready. Commands: add, find, list, quit.\n");

    while (1) {
        printf("> ");
        gets(line);

        if (strncmp(line, "quit", 4) == 0) {
            break;
        } else if (strncmp(line, "add", 3) == 0) {
            sscanf(line, "%s %s %d", command, name, &age);
            add_user(name, age);
            printf("Added %s.\n", name);
        } else if (strncmp(line, "find", 4) == 0) {
            sscanf(line, "%s %s", command, name);
            struct user *u = find_user(name);
            if (u != NULL) {
                printf("Found %s (age %d).\n", u->name, u->age);
            } else {
                printf("Not found.\n");
            }
        } else if (strncmp(line, "list", 4) == 0) {
            list_users();
        } else {
            printf("Unknown command.\n");
        }
    }

    printf("Goodbye.\n");
    return 0;
}
```

**File 3: `OrderProcessor.java`**

```java
package com.example.orders;

import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.Date;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;

/**
 * OrderProcessor
 *
 * Reads an orders CSV from disk, filters out cancelled rows, computes
 * a per-customer total, and prints the top spenders.
 *
 * Original implementation: 2014. Target runtime: Java 8.
 * Has not been touched since the Spring 4 -> Spring 5 migration.
 */
public class OrderProcessor {

    private static final SimpleDateFormat DATE_FMT =
        new SimpleDateFormat("yyyy-MM-dd");

    public static class Order {
        public String customerId;
        public String status;
        public double amount;
        public Date   placedOn;

        public Order(String customerId, String status, double amount, Date placedOn) {
            this.customerId = customerId;
            this.status = status;
            this.amount = amount;
            this.placedOn = placedOn;
        }
    }

    public List<Order> loadOrders(String path) throws IOException {
        List<Order> result = new ArrayList<Order>();
        BufferedReader reader = null;
        try {
            reader = new BufferedReader(new FileReader(path));
            String line = reader.readLine();
            while (line != null) {
                String[] parts = line.split(",");
                Date placed = null;
                try {
                    placed = DATE_FMT.parse(parts[3]);
                } catch (Exception e) {
                    placed = new Date();
                }
                Order o = new Order(parts[0], parts[1],
                                    Double.parseDouble(parts[2]), placed);
                result.add(o);
                line = reader.readLine();
            }
        } finally {
            if (reader != null) {
                try {
                    reader.close();
                } catch (IOException e) {
                    // ignore
                }
            }
        }
        return result;
    }

    public Map<String, Double> totalsByCustomer(List<Order> orders) {
        Map<String, Double> totals = new HashMap<String, Double>();
        Iterator<Order> it = orders.iterator();
        while (it.hasNext()) {
            Order o = it.next();
            if (o.status.equals("CANCELLED")) {
                continue;
            }
            Double current = totals.get(o.customerId);
            if (current == null) {
                totals.put(o.customerId, o.amount);
            } else {
                totals.put(o.customerId, current + o.amount);
            }
        }
        return totals;
    }

    public void printTopSpenders(Map<String, Double> totals, int n) {
        List<Map.Entry<String, Double>> entries =
            new ArrayList<Map.Entry<String, Double>>(totals.entrySet());

        Collections.sort(entries, new Comparator<Map.Entry<String, Double>>() {
            public int compare(Map.Entry<String, Double> a,
                               Map.Entry<String, Double> b) {
                return b.getValue().compareTo(a.getValue());
            }
        });

        for (int i = 0; i < n && i < entries.size(); i++) {
            Map.Entry<String, Double> e = entries.get(i);
            System.out.println(e.getKey() + ": $" + e.getValue());
        }
    }

    public static void main(String[] args) throws IOException {
        OrderProcessor p = new OrderProcessor();
        List<Order> orders = p.loadOrders(args[0]);
        Map<String, Double> totals = p.totalsByCustomer(orders);
        p.printTopSpenders(totals, 10);
    }
}
```

### Step 1.3: Confirm Copilot is ready

1. Open the Chat view (`Ctrl+Alt+I`).
2. Confirm the model picker reads **Claude Sonnet 4.6**.
3. Switch the chat mode dropdown to **Ask**. You will stay in Ask mode for the entire lab. The goal is analysis, not modification.

### Step 1.4: Create a lab notebook file

Create a new file `findings.md` in the workspace. You will record your analyses here as you go. Start it with:

```markdown
# Legacy Code Analysis Findings

## PAYROLL.CBL

## user_registry.c

## OrderProcessor.java
```

Save it.

---

## Part 2: Analyze PAYROLL.CBL (COBOL)

Open `PAYROLL.CBL` in the editor so it becomes Copilot's active-file context.

You will work through five structured questions. For each one, copy Copilot's answer into the corresponding section of `findings.md`. Note: Copilot's exact wording will vary between runs (LLMs are non-deterministic), but the substance of the answers should match what is described below.

### Question 2.1: Plain-English explanation

In the Chat view, with `PAYROLL.CBL` active in the editor, type:

```
#file:PAYROLL.CBL Explain what this program does in plain English for someone
who has never read COBOL. Cover the input, the processing, and the output.
Two paragraphs maximum.
```

**Expected response:** Copilot should describe the program as reading an employee record file (`EMP.DAT`), computing weekly gross pay including overtime at 1.5x for hours over 40, applying a 22% flat tax, and writing one formatted payslip line per employee to `PAYSLIP.OUT`.

### Question 2.2: Data structure walkthrough

```
Walk me through the EMP-RECORD structure field by field. For each PIC clause,
explain what type and size it represents and give a realistic example value.
```

**Expected response:** Copilot should decode the PIC clauses, e.g. `EMP-ID PIC 9(5)` as a 5-digit unsigned integer, `EMP-RATE PIC 9(3)V99` as a fixed-point number with three digits before an implied decimal and two after (max $999.99), and so on.

### Question 2.3: Business rules embedded in the code

```
What business rules and policies are hardcoded into this program?
List them with the line or paragraph they appear in. For each one,
say whether it should be configurable instead, and why.
```

**Expected response:** Copilot should flag:
- The 40-hour standard work week (WS-STD-WEEK)
- The 1.5x overtime multiplier (WS-OT-MULT)
- The 22% flat tax rate (WS-TAX-RATE)
- The output file name `PAYSLIP.OUT`
- The fixed-width payslip format

And argue that tax rates change yearly, overtime rules vary by jurisdiction, and the standard week varies by employment contract, so all three numerical constants should come from a configuration file or table.

### Question 2.4: Defects and risks

```
What defects, risks, or missing safeguards do you see in this program?
Consider: error handling, edge cases (negative hours, zero rate, missing
fields), file I/O failures, and auditability. Be specific about line numbers
or paragraph names.
```

**Expected response:** Copilot should call out:
- No error handling on `OPEN` (program crashes silently on missing input file)
- No validation of input values (negative hours, zero or negative rate, malformed record)
- No audit log (you can compute a payslip but cannot prove later what inputs produced it)
- Silent truncation if gross pay exceeds `9(5)V99` (i.e., over $99,999.99)
- No handling of the EMP-DEPT field at all (it is read but never used)

### Question 2.5: Modernization recommendation

```
The comment at the top of the file says "Maintenance only, do not extend"
but it's clear this program is still in production. If you were asked to
modernize this for a 2026 codebase, would you (a) keep it in COBOL and
clean it up, (b) wrap it in a service interface, or (c) rewrite from scratch
in a modern language? Make the case for one recommendation and name the
key risks of that choice.
```

This is an open-ended judgement question. There is no single correct answer. Copilot should weigh:
- Cost and risk of rewrite (subtle business rules, decades of edge cases)
- Availability of COBOL developers
- The fact that the program runs once a week and works correctly
- Whether it integrates with other modern systems

Capture Copilot's reasoning verbatim. You will compare it with the other two file analyses at the end of the lab.

---

## Part 3: Analyze user_registry.c (C)

Open `user_registry.c` in the editor.

### Question 3.1: Plain-English explanation

```
#file:user_registry.c Explain what this program does in plain English.
What is its intended use? Two paragraphs.
```

**Expected response:** A REPL-style command-line registry of users (name + age) with add/find/list/quit commands, maintaining the data in memory only (lost on exit).

### Question 3.2: Security and memory-safety audit

```
Perform a security and memory-safety audit of this code. List every issue
you find with the line number, an explanation of the risk, and a one-line
description of the fix. Order the list by severity, most severe first.
```

**Expected response:** Copilot should produce a numbered list including (in approximately this priority order):

1. **`gets(line)`** (around line 63): Removed from C11. Reads unbounded input into a 256-byte buffer; classic buffer overflow leading to arbitrary code execution. Fix: replace with `fgets(line, sizeof(line), stdin)`.
2. **`strcpy(u->name, name)`** (around line 29): No length check. If `name` is longer than 31 bytes, overflows the 32-byte struct field. Fix: use `strncpy` with explicit size, or `snprintf`.
3. **Off-by-one in `find_user`** (around line 37): `i <= user_count` reads `users[user_count]` which is past the last valid entry. Fix: use `<` instead of `<=`.
4. **`sscanf(line, "%s %s %d", ...)`** (around line 66): `%s` has no width specifier. Long input overflows `command` (16 bytes) or `name` (64 bytes). Fix: `%15s %63s %d` or use a safer parser.
5. **Unchecked `malloc`** (around line 28): If allocation fails, `u` is `NULL` and the next `strcpy` segfaults. Fix: check return, handle failure.
6. **No bounds check on `users[user_count]`** (around line 31): If `user_count` reaches `MAX_USERS`, writes past the array. Fix: check before adding.
7. **Memory leak**: `malloc`-allocated user records are never `free()`d. Fix: free on `quit`, or use a destructor pattern.

### Question 3.3: What would a modern C compiler say?

```
What warnings or errors would a modern C compiler (gcc 13 or clang 16)
emit if I built this with -Wall -Wextra -Wpedantic? Which of those would
become hard errors with -Werror?
```

**Expected response:** Copilot should mention:
- `gets` produces a deprecation warning in C99/C11 and is removed from C11 in some libc versions (compile may fail at link time).
- Implicit `int` return on `list_users` would warn.
- Unused parameters `argc`, `argv` would warn under `-Wunused-parameter`.
- Various `-Wformat` warnings on the `printf` calls if argument types do not match.

### Question 3.4: Modernization plan

```
Suppose this program is still in use as a small internal utility. Sketch
a modernization plan that brings it up to current standards without
changing the user-visible behaviour. Order the changes from "safe and
cheap" to "behavioural impact, needs testing".
```

This is a judgement question. Copilot should propose roughly:
- **Cheap and safe**: replace `gets` with `fgets`, add `malloc` checks, fix the off-by-one, add `%s` width specifiers.
- **Medium**: add `free()` cleanup on exit, bound user_count against `MAX_USERS`.
- **Higher impact, needs tests**: replace fixed-size arrays with dynamic allocation, switch to a hash table for lookup, persist state to disk.
- **Rewrite candidate**: if the program is more than a curiosity, port to a memory-safe language (Rust, Go, even Python).

---

## Part 4: Analyze OrderProcessor.java (Java 8)

Open `OrderProcessor.java` in the editor.

This file is qualitatively different from the previous two. It is correct in most ways, but it is written in idiomatic 2014 Java 8 and would look outdated to a current Java developer. The interesting question is not "what is broken" but "what would you change if you were modernizing."

### Question 4.1: Plain-English explanation

```
#file:OrderProcessor.java Explain what this class does. What is the input,
what is the output, what is the dependency footprint? Be specific.
```

**Expected response:** Reads a CSV of orders (customerId, status, amount, date), parses it line by line, filters out cancelled orders, sums per customer, and prints the top N spenders to stdout. No external dependencies beyond the JDK.

### Question 4.2: Correctness review

```
Are there any actual bugs or latent defects in this code? Set aside style
and modernity for now and focus on correctness. What can go wrong at
runtime?
```

**Expected response:** Copilot should identify:
- **`SimpleDateFormat` as a `static final` field is not thread-safe.** If two threads call `loadOrders` concurrently, the date parser can produce wrong results or throw `NumberFormatException`. This is the canonical Java 8 trap.
- **No header-row handling**: the first CSV line is parsed as data, which will throw `NumberFormatException` on the amount column.
- **`split(",")` does not handle quoted fields**: a customer name containing a comma will break parsing.
- **`catch (Exception e)` on date parsing silently substitutes today's date**, which silently corrupts data.
- **`args[0]` with no length check** will throw `ArrayIndexOutOfBoundsException` if run with no arguments.
- **No null/empty-line guard**: a trailing blank line in the CSV will throw on `parts[3]`.

### Question 4.3: Idiom modernization

```
Rewrite this class in modern Java (Java 17 or later) idioms. Do not change
the behaviour. Show the rewritten code in a single block and below it
list each idiom change you made with a one-line justification.
```

**Expected response:** Copilot should produce a rewrite that uses:
- `java.time.LocalDate` and `DateTimeFormatter` instead of `Date` and `SimpleDateFormat` (thread-safe, immutable).
- `record Order(...)` instead of the static inner class with public fields.
- `try-with-resources` on the `BufferedReader` instead of `try { } finally { }`.
- `Files.lines(Path.of(path))` and streams instead of a manual `while` loop.
- `Collectors.groupingBy(Order::customerId, Collectors.summingDouble(Order::amount))` instead of the manual HashMap accumulation.
- `Comparator.comparingDouble(...).reversed()` and `.limit(n)` instead of an anonymous Comparator class.
- Diamond operator (`new ArrayList<>()`) or `List.of(...)`.
- An explicit check on `args.length` before `args[0]`.

### Question 4.4: Trade-off question

```
The modernization in 4.3 is more concise but it changes the failure modes.
For example, streams short-circuit differently and try-with-resources
swallows secondary exceptions differently than the explicit version.
Walk me through three places where the rewritten code behaves
observably differently from the original, even though both are
"correct."
```

This question forces Copilot (and the student) to reason about *behaviour preservation*, which is the real challenge in legacy modernization. Capture the answer carefully.

### Question 4.5: Migration risk

```
If this class is part of a larger codebase that uses it as a library
(callers depend on the public method signatures), what is the safe
migration path? Should the public API change at all?
```

**Expected response:** Copilot should distinguish between *internal* modernization (safe, no caller impact) and *API* modernization (changing the public method signatures, which breaks callers). The safe path is to modernize the internals first while keeping the public surface stable, then deprecate and migrate callers separately.

---

## Part 5: Cross-File Comparison

You now have three analyses captured in `findings.md`. Review them side by side and answer the following synthesis questions in your lab notebook.

### Synthesis Question 5.1: Severity ranking

Rank the three files from "most urgent to fix" to "least urgent to fix." Justify your ranking. Pay attention to:

- Is the code actually broken, or just dated?
- Is it deployed in a context where a bug would matter?
- How costly would a fix be relative to its impact?

### Synthesis Question 5.2: Quality of Copilot's analysis

Across the three files, where did Copilot's analysis seem most reliable? Least reliable? Were there language-specific differences? For example:

- COBOL is a small share of Copilot's training data. Did its COBOL explanations feel as confident as its Java ones?
- C security audits are a well-trodden topic for LLMs. Did Copilot find all the issues, or did it miss any that you can spot manually?
- Java idiom modernization is heavily represented in training data. Was the modernized version actually idiomatic, or did it have its own anti-patterns?

### Synthesis Question 5.3: What did you do that Copilot did not?

Did you make judgement calls during the lab that Copilot could not have made for you? For example:

- Deciding that the COBOL program is fine to leave alone because it works and is being retired.
- Deciding that the C program's lack of persistence is acceptable for an internal utility but unacceptable for a customer-facing system.
- Deciding that the Java modernization is worth doing because the team is on Java 17 now and the old idioms are confusing new hires.

### Synthesis Question 5.4: Prompt engineering retrospective

Look back at the five questions you asked of the COBOL file in Part 2. Which question elicited the most useful response? Which gave the least value? If you were to design a reusable "legacy code intake" prompt template for new files, what would it contain?

---

## Part 6: Cleanup

You can keep the workspace for reference, or remove it:

```bash
rm -rf ~/legacy-lab
```

---

## Reference: Useful Patterns for Legacy Code Prompts

These patterns are reusable across languages and codebases.

| Pattern | Example wording | When to use |
|---------|-----------------|-------------|
| **Plain-English first** | "Explain what this code does in plain English. Two paragraphs maximum." | Always your first question. If Copilot's explanation is wrong, every later answer will be too. |
| **Structure walkthrough** | "Walk me through this type/struct/record field by field, explaining what each one is for." | When the data shape is unfamiliar (COBOL records, C structs, old-style Java beans). |
| **Embedded business rules** | "What business rules and policies are hardcoded into this code? Where could they have come from? Should they be configurable?" | The single most important question for legacy code. The rules are usually undocumented anywhere else. |
| **Defect and risk audit** | "What defects, risks, or missing safeguards do you see? Consider edge cases, error handling, concurrency, and auditability." | When you are deciding whether to ship a fix or rewrite. |
| **Compiler/linter what-if** | "What warnings would a modern compiler/linter emit on this code with strict flags?" | Quick way to surface dated patterns and unsafe constructs. |
| **Behaviour-preserving modernization** | "Rewrite this in modern idioms without changing the behaviour. Then list every change and justify it." | When the code works but is hard to read or maintain. The "list every change" half is what makes it usable. |
| **Migration risk** | "If callers depend on this code's public API, what is the safe migration path?" | Always ask this before changing anything in a library. |
| **Stay/wrap/rewrite trichotomy** | "Would you (a) keep this and clean it up, (b) wrap it in a modern interface, or (c) rewrite from scratch? Make the case for one." | Decision-making question for legacy systems. Forces a recommendation rather than a list of options. |

---

## Troubleshooting

**Copilot's COBOL explanation seems vague or wrong.**
COBOL is much less represented in training data than Java or C. Try giving it explicit structural hints in your prompt, e.g. "This is a COBOL-85 program with three DIVISIONs. Focus on the PROCEDURE DIVISION first." If you still get poor results, try Claude Sonnet 4.6 specifically (it tends to handle COBOL better than Haiku) or fall back to a web search for the syntax you do not recognize.

**Copilot's modernized Java code uses features your project does not allow.**
Be explicit about your constraints up front: "Rewrite this targeting Java 17, no third-party libraries, no preview features." Without that, Copilot will use whatever it thinks is most idiomatic, which may include features your team does not have.

**Copilot refuses to answer or gives a meta-response.**
Make sure you are in **Ask** mode, not Agent mode (Agent mode sometimes tries to *act* on legacy code rather than analyze it). If you see "I'll need to read the file first" without an actual analysis, click the file in the explorer to make it the active editor tab, then re-ask.

**The analyses for the same file differ noticeably between runs.**
This is expected. LLMs are non-deterministic. For high-stakes analysis, run the same prompt two or three times and reconcile the answers. The most reliable findings are the ones that appear in every run.

---

## Further Reading

- OWASP C/C++ secure coding guide: <https://owasp.org/www-community/Source_Code_Analysis_Tools>
- Java modernization (Java 8 to 17): <https://docs.oracle.com/en/java/javase/17/migrate/index.html>
- COBOL maintenance and modernization patterns: <https://www.gartner.com/en/documents/cobol-modernization>
- GitHub Copilot in VS Code: <https://code.visualstudio.com/docs/copilot/overview>
