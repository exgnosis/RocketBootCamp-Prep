# Lab 1-1: Structured Programming 

## Overview

Structured programming is the discipline of building programs out of three basic control structures (sequence, selection, iteration) combined with functional decomposition (each function does one job and is named for what it does). The ideas are old; they were articulated in the 1960s and 1970s as a reaction to spaghetti code built around `GOTO` statements. The ideas are also durable: every modern language is designed around them, every healthy codebase uses them, and they remain the bedrock that more advanced techniques (object-oriented design, functional programming, refactoring) build on top of.

This lab gives you a small, well-decomposed program that processes a batch of banking transactions against a list of accounts. The program demonstrates every concept the module covers: a clear top-down structure, pure utility functions that pass data in and out without touching globals, sequence-selection-iteration at the right levels of the design, and an explicit "data dictionary" plus "decision table" written as comments. Most of the code is already written for you. Three small holes in the implementation are marked `TODO` for you to fill in.

The lab is therefore part **reading exercise** (understand the structure before you change it) and part **implementation exercise** (fill in the operative pieces while preserving the structure). When you are done, you will run the program and compare its output against the expected output for verification.

**This lab is hands-on.** You write the code yourself; no AI assistance is needed or expected. The point is to feel where the design decisions are and to practice making them yourself.

---

## Learning Objectives

By the end of this lab, you will be able to:

1. Identify the three control structures (sequence, selection, iteration) in a piece of working code.
2. Read a function signature and infer the function's responsibility from its types and name alone.
3. Translate a "data dictionary" (a textual description of record shapes) and a "decision table" (a textual description of rules) into Python.
4. Pass state explicitly through function parameters and return values instead of using global variables.
5. Use named status codes (`"OK"`, `"INSUFFICIENT_FUNDS"`, `"UNKNOWN_ACCOUNT"`) instead of generic booleans to give callers useful information.
6. Verify your implementation against an expected output.

---

## Part 1: Set Up the Workspace

### Step 1.1: Create the lab directory

In a terminal:

```bash
mkdir -p ~/structured-lab
cd ~/structured-lab
```

### Step 1.2: Create the starter file

Create a file called `starter.py` and paste in the following code. Do not modify anything yet; in Part 2 you will read it before changing anything.

```python
# =========================================
# Structured Programming Lab — Starter
# (No classes; functions only)
# =========================================

from typing import List, Dict, Tuple

# ---- "Data Dictionary" (informal) ----
# Account record:     {"acct_id": str, "balance": float}
# Transaction record: {"acct_id": str, "type": "DEP"|"WDR", "amount": float}
# Report row:         (acct_id: str, opening: float, delta: float, closing: float, status: str)

# ---- "Decision Table" for withdrawal rules ----
# If WDR and amount <= balance           -> approve
# If WDR and amount > balance            -> decline
# DEP always approved (> 0)

# ---- Sample input ----
ACCOUNTS_SEED: List[Dict] = [
    {"acct_id": "A100", "balance": 100.0},
    {"acct_id": "B200", "balance": 50.0},
]

TX_BATCH: List[Dict] = [
    {"acct_id": "A100", "type": "DEP", "amount": 25.0},
    {"acct_id": "A100", "type": "WDR", "amount": 120.0},
    {"acct_id": "B200", "type": "WDR", "amount": 45.0},
    {"acct_id": "B200", "type": "WDR", "amount": 20.0},  # decline (insufficient after first WDR)
    {"acct_id": "Z999", "type": "DEP", "amount": 10.0},  # invalid account
    {"acct_id": "A100", "type": "DEP", "amount": -5.0},  # invalid amount
]

# ---------- Utilities (pure functions) ----------

def find_account(accounts: List[Dict], acct_id: str) -> int:
    """Return index of account in list, or -1 if not found."""
    for i in range(len(accounts)):
        if accounts[i]["acct_id"] == acct_id:
            return i
    return -1


def validate_transaction(tx: Dict) -> Tuple[bool, str]:
    """Basic schema & domain checks for a transaction record."""
    # TODO: Check required keys: acct_id, type, amount
    # TODO: type must be 'DEP' or 'WDR'; amount must be > 0
    # Return (True, "") if valid; else (False, reason)
    return False, "NOT_IMPLEMENTED"


def apply_transaction(accounts: List[Dict], tx: Dict) -> Tuple[bool, str]:
    """
    Apply a single transaction using the decision table.
    Returns (True, 'OK') if applied; (False, reason) otherwise.
    """
    idx = find_account(accounts, tx["acct_id"])
    if idx == -1:
        return False, "UNKNOWN_ACCOUNT"

    acct = accounts[idx]
    ttype = tx["type"]
    amt = tx["amount"]

    if ttype == "DEP":
        # TODO: add amount to balance (sequence)
        # TODO: return (True, "OK")
        return False, "NOT_IMPLEMENTED"

    elif ttype == "WDR":
        # SELECTION: approve only if amount <= balance
        # TODO: if ok: subtract and return True; else: return False with "INSUFFICIENT_FUNDS"
        return False, "NOT_IMPLEMENTED"

    else:
        return False, "UNKNOWN_TYPE"


def process_batch(accounts_seed: List[Dict], tx_batch: List[Dict]) -> Tuple[List[Tuple], List[Dict]]:
    """
    ITERATION over transactions.
    Builds a report [(acct_id, opening, delta, closing, status), ...]
    and returns (report_rows, final_accounts).
    """
    # Make a *working* copy so we don't mutate the seed (structured transparency)
    accounts = [{"acct_id": a["acct_id"], "balance": float(a["balance"])} for a in accounts_seed]

    # Keep track of opening balances and deltas
    openings = {a["acct_id"]: a["balance"] for a in accounts}
    deltas = {a["acct_id"]: 0.0 for a in accounts}

    report_rows: List[Tuple] = []

    for tx in tx_batch:
        ok, reason = validate_transaction(tx)
        if not ok:
            report_rows.append((tx.get("acct_id", "?"), openings.get(tx.get("acct_id", "?"), 0.0),
                                0.0, openings.get(tx.get("acct_id", "?"), 0.0), f"REJECT:{reason}"))
            continue

        applied, reason = apply_transaction(accounts, tx)
        acct_id = tx["acct_id"]
        if applied:
            # update delta for that acct
            if tx["type"] == "DEP":
                deltas[acct_id] = deltas.get(acct_id, 0.0) + tx["amount"]
            else:  # WDR
                deltas[acct_id] = deltas.get(acct_id, 0.0) - tx["amount"]
            # status is recorded per-transaction for traceability
            idx = find_account(accounts, acct_id)
            closing = accounts[idx]["balance"]
            report_rows.append((acct_id, openings.get(acct_id, 0.0), deltas[acct_id], closing, "APPLIED"))
        else:
            closing = openings.get(acct_id, 0.0) + deltas.get(acct_id, 0.0)
            report_rows.append((acct_id, openings.get(acct_id, 0.0), deltas.get(acct_id, 0.0), closing, f"REJECT:{reason}"))

    return report_rows, accounts


def render_report(rows: List[Tuple]) -> None:
    """Pretty-print the report."""
    print("\n=== BATCH REPORT ===")
    print(f"{'Acct':<6} {'Opening':>10} {'Delta':>10} {'Closing':>10}  Status")
    for acct, opening, delta, closing, status in rows:
        print(f"{acct:<6} {opening:>10.2f} {delta:>10.2f} {closing:>10.2f}  {status}")


def main() -> None:
    # SEQUENCE: process then report
    rows, final_accounts = process_batch(ACCOUNTS_SEED, TX_BATCH)
    render_report(rows)

    print("\nFinal account balances:")
    for a in final_accounts:
        print(f" - {a['acct_id']}: {a['balance']:.2f}")


# Run
if __name__ == "__main__":
    main()
```

Save the file.

### Step 1.3: Run the starter to see the baseline

Before changing anything, run the starter to see what happens:

```bash
python3 starter.py
```

Output:

```
=== BATCH REPORT ===
Acct      Opening      Delta    Closing  Status
A100       100.00       0.00     100.00  REJECT:NOT_IMPLEMENTED
A100       100.00       0.00     100.00  REJECT:NOT_IMPLEMENTED
B200        50.00       0.00      50.00  REJECT:NOT_IMPLEMENTED
B200        50.00       0.00      50.00  REJECT:NOT_IMPLEMENTED
Z999         0.00       0.00       0.00  REJECT:NOT_IMPLEMENTED
A100       100.00       0.00     100.00  REJECT:NOT_IMPLEMENTED
```

Every transaction was rejected with `NOT_IMPLEMENTED` because the validator returns `False` unconditionally. The skeleton of the program works (it reads the inputs, walks the batch, and prints the report), but the operative pieces in the middle have not been written yet. Your job in Part 3 is to write them.

### Step 1.4: Create a lab notebook

Create a file `notebook.md` in the workspace. You will record your analyses, decisions, and observations as you go:

```markdown
# Structured Programming Lab Notebook

## Part 2: Reading the starter

## Part 3: Implementation decisions

## Part 4: Verification

## Part 5: Reflection
```

---

## Part 2: Read the Starter Before You Change It

This is a small program, but it has more structure than a casual reader sees on first pass. Before you implement the TODOs, you should be able to answer the questions below from the source alone. Spend at least 15 minutes on this section; do not skip it to get to the coding.

### Question 2.1: The data dictionary

The comment block at the top says:

```
Account record:     {"acct_id": str, "balance": float}
Transaction record: {"acct_id": str, "type": "DEP"|"WDR", "amount": float}
Report row:         (acct_id: str, opening: float, delta: float, closing: float, status: str)
```

This is a **data dictionary**: a plain-language description of the shapes of the data the program manipulates. Read it carefully and answer in your notebook:

1. Which two records are dictionaries? Which one is a tuple? Why might the author have chosen a tuple for one and dictionaries for the others?
2. Are any of the dictionary fields optional? Are any of the tuple fields optional? How can you tell?
3. The transaction's `type` field has only two allowed values: `"DEP"` and `"WDR"`. What does the program do if a transaction has a different type? (Look at `apply_transaction` for the answer.)

### Question 2.2: The decision table

Below the data dictionary:

```
If WDR and amount <= balance           -> approve
If WDR and amount > balance            -> decline
DEP always approved (> 0)
```

This is a **decision table**: a plain-language statement of the rules the program enforces. Three rules, expressed in three lines. Answer:

1. Where in the code does each of these three rules become Python? (Look in `apply_transaction`; two of them are TODOs you have not written yet.)
2. The third rule says "DEP always approved (> 0)". The "> 0" is the validation step (positive amount). Why is the "> 0" check done in `validate_transaction` and not in `apply_transaction`? What is the design principle?

### Question 2.3: The function decomposition

The program has five functions. List them in your notebook with a one-sentence description of what each one does, **based on the function signature and docstring alone** (do not read the body yet):

- `find_account(accounts, acct_id) -> int`
- `validate_transaction(tx) -> (bool, str)`
- `apply_transaction(accounts, tx) -> (bool, str)`
- `process_batch(accounts_seed, tx_batch) -> (rows, accounts)`
- `render_report(rows) -> None`

Now draw the call graph: which function calls which other function? `main()` is the root. Trace the arrows.

> If this exercise feels familiar, it is the same top-down reading technique from the C-reading lab. The reason it works for any unfamiliar program is the same: a function's *contract* (its name, parameters, return type, docstring) is supposed to tell you what it does without forcing you to read the body. When you find a function whose contract does not tell you that, you have found a code smell.

### Question 2.4: Where does state live?

A key principle of structured programming is **explicit state**: data is passed in and out of functions through parameters and return values, not stored in global variables that any function can secretly read or write.

Answer in your notebook:

1. Where is the *list of accounts* stored while the program is running? Is it a module-level global, a local variable in `main()`, or something else?
2. The `process_batch` function makes a **working copy** of the accounts (`accounts = [{...} for a in accounts_seed]`). Why? What would go wrong if it just used the original `accounts_seed` list?
3. Inside `process_batch`, there are also two dictionaries called `openings` and `deltas`. What are they for? Why are they local to `process_batch` rather than being defined at the module level?

### Question 2.5: The three control structures

Structured programming is built on three control structures:

- **Sequence**: do A, then B, then C.
- **Selection**: if some condition, do A; otherwise do B. Also includes `if/elif/else` chains and switch-style dispatch.
- **Iteration**: do A repeatedly while some condition holds, or for each item in some collection.

Find at least one example of each in the starter code and note the line numbers (or function name plus a one-line quote) in your notebook. Some examples are obvious; some are nested inside others.

### Reference: Things you should have noticed

After you write your own answers, check against this list. You should have noticed at least:

**Data dictionary (Q2.1):** Accounts and transactions are dictionaries (mutable, named fields); report rows are tuples (immutable, positional fields). The choice of tuple for report rows signals that a row is a snapshot, not something to be mutated. None of the fields are explicitly marked optional, but `tx.get("acct_id", "?")` in `process_batch` suggests the author has imagined a transaction where `acct_id` might be missing. The validator handles such defensive cases. An unknown transaction `type` is handled by the final `else` branch of `apply_transaction` returning `"UNKNOWN_TYPE"`.

**Decision table (Q2.2):** The three rules map to:
- `DEP` branch in `apply_transaction` (which you will fill in).
- `WDR amount <= balance` branch in `apply_transaction` (which you will fill in).
- `WDR amount > balance` branch in `apply_transaction` (also yours to fill in).
- The "> 0" check is in `validate_transaction` because amount-positivity is a property of a transaction, independent of any account. Whether the transaction is valid at all should be decided before the program tries to apply it. This is the **separation of validation from execution**, a recurring pattern in well-structured code.

**Function decomposition (Q2.3):** `main()` calls `process_batch()` and `render_report()`. `process_batch()` calls `validate_transaction()` and `apply_transaction()`. `apply_transaction()` calls `find_account()`. The call graph is a tree with no cycles. Each function is named for what it does. Each function takes its data as parameters and returns its result.

**Explicit state (Q2.4):** The accounts list starts as a module-level `ACCOUNTS_SEED` constant, but `process_batch` immediately copies it so the original is not mutated. This is the structured-programming version of "do not have side effects on inputs." `openings` and `deltas` are local to `process_batch` because they are bookkeeping state for the duration of a single batch; making them globals would make the function impossible to call twice in the same program without resetting state.

**Three control structures (Q2.5):**
- **Sequence**: in `main()`, "process then report": `rows, final_accounts = process_batch(...)` followed by `render_report(rows)` followed by the balance printout. Also the linear setup of `accounts`, `openings`, and `deltas` at the top of `process_batch`.
- **Selection**: `if ttype == "DEP" / elif ttype == "WDR" / else` in `apply_transaction`; `if not ok` and `if applied` in `process_batch`; `if accounts[i]["acct_id"] == acct_id` in `find_account`.
- **Iteration**: `for i in range(len(accounts))` in `find_account`; `for tx in tx_batch` in `process_batch`; `for acct, opening, delta, closing, status in rows` in `render_report`; `for a in final_accounts` in `main`.

---

## Part 3: Implement the TODOs

You will implement three pieces of code, one in `validate_transaction` and two in `apply_transaction`. Run the program after each one to confirm progress.

Make a copy of the starter so you can compare:

```bash
cp starter.py work.py
```

Edit `work.py` from now on; leave `starter.py` as a reference.

### Step 3.1: Implement `validate_transaction`

Open `work.py` and find the `validate_transaction` function. Replace its body with an implementation that:

1. Checks that the transaction dict contains the three required keys: `"acct_id"`, `"type"`, and `"amount"`. If any are missing, return `(False, "MISSING_FIELDS")`.
2. Checks that the `"type"` value is either `"DEP"` or `"WDR"`. If not, return `(False, "INVALID_TYPE")`.
3. Checks that the `"amount"` value is a number (it might be a string or other non-numeric type) and that it is greater than zero. If it cannot be converted to a number, return `(False, "INVALID_AMOUNT")`. If it is zero or negative, return `(False, "NONPOSITIVE_AMOUNT")`.
4. If all checks pass, return `(True, "")`.

The order of the checks matters. Check for missing fields first; you cannot check the type or amount of a field that does not exist.

**Design hint:** The function returns a `(bool, str)` tuple. The boolean tells the caller whether the transaction is valid; the string gives a machine-readable reason when it is not. This is the same pattern `apply_transaction` uses for the same reason: callers need to know *why* a check failed so they can report it.

**Implementation hint:** To check for required keys, use `all(k in tx for k in ("acct_id", "type", "amount"))`. To safely convert amount to float, wrap it in `try / except (TypeError, ValueError)`.

After implementing, run:

```bash
python3 work.py
```

You should still see "NOT_IMPLEMENTED" on some rows because `apply_transaction` is still not done. But now you should see specific rejection reasons on the *invalid* transactions:

- The `Z999` row will probably still say `REJECT:NOT_IMPLEMENTED` (the validator passes; the rejection comes from `apply_transaction`'s `UNKNOWN_ACCOUNT` branch, which is already implemented). Or it may say something else depending on your exact implementation; we will check this in Part 4.
- The negative-amount row should now say `REJECT:NONPOSITIVE_AMOUNT`.

If you do not see the negative-amount rejection, your validator is not catching it. Debug before moving on.

### Step 3.2: Implement the DEP branch of `apply_transaction`

Still in `work.py`, find the `apply_transaction` function and the `if ttype == "DEP":` branch. Replace the two TODO comments with the actual implementation:

1. Add `amt` to `acct["balance"]`. Recall that `acct` is a *reference* to a dictionary inside the `accounts` list, so mutating it in place updates the original.
2. Return `(True, "OK")`.

That's two lines of code, possibly one if you like it terse.

**Run:**

```bash
python3 work.py
```

You should now see the first deposit row succeed:

```
A100       100.00      25.00     125.00  APPLIED
```

The first row of A100 is the `DEP $25` transaction. Opening 100.00, delta +25.00, closing 125.00, status APPLIED. If your output shows that, the deposit branch is working.

### Step 3.3: Implement the WDR branch of `apply_transaction`

Find the `elif ttype == "WDR":` branch and implement it:

1. If `amt` is less than or equal to `acct["balance"]`: subtract `amt` from the balance and return `(True, "OK")`.
2. Otherwise: return `(False, "INSUFFICIENT_FUNDS")`.

This is the **selection** the comment was hinting at. The decision table from Part 2 told you exactly when to approve and when to decline; your code implements that table directly.

**Run:**

```bash
python3 work.py
```

Now every operative branch is implemented. Compare your output to the expected output in Part 4.

---

## Part 4: Verify Against the Expected Output

Run the finished program:

```bash
python3 work.py
```

Your output should match this exactly:

```
=== BATCH REPORT ===
Acct      Opening      Delta    Closing  Status
A100       100.00      25.00     125.00  APPLIED
A100       100.00     -95.00       5.00  APPLIED
B200        50.00     -45.00       5.00  APPLIED
B200        50.00     -45.00       5.00  REJECT:INSUFFICIENT_FUNDS
Z999         0.00       0.00       0.00  REJECT:UNKNOWN_ACCOUNT
A100       100.00     -95.00       5.00  REJECT:NONPOSITIVE_AMOUNT

Final account balances:
 - A100: 5.00
 - B200: 5.00
```

Walk through it row by row before you congratulate yourself; verifying that the output is right is the same skill as writing the code.

### Row-by-row trace

| Row | Transaction | Result |
|----|----|----|
| 1 | A100 DEP $25 | Balance 100 + 25 = 125. APPLIED. |
| 2 | A100 WDR $120 | Balance 125 - 120 = 5 (≤ balance, so approved). APPLIED. Delta is the *cumulative* delta for the account: +25 - 120 = -95. |
| 3 | B200 WDR $45 | Balance 50 - 45 = 5. APPLIED. Delta -45. |
| 4 | B200 WDR $20 | Balance is 5, requested 20. 20 > 5, so REJECT:INSUFFICIENT_FUNDS. The reported delta stays at -45 (the previous delta), and the closing balance shown is the opening 50 plus that delta, which is 5. The withdrawal that failed does not change the balance. |
| 5 | Z999 DEP $10 | Account Z999 does not exist. REJECT:UNKNOWN_ACCOUNT. |
| 6 | A100 DEP $-5 | Amount is negative; the validator rejects with REJECT:NONPOSITIVE_AMOUNT. Note the delta and closing on the row are A100's *current* delta (-95) and closing (5), which is sensible: the rejection does not change A100's state. |

Final balances are A100 = 5.00 and B200 = 5.00. Both ended up at the same number by coincidence.

### If your output differs

The most common ways for the output to differ:

1. **Validation order matters.** If your validator checks the amount *before* checking that the keys exist, a transaction with a missing key will throw `KeyError` instead of returning a clean rejection. Fix the order.
2. **Mutating the input by accident.** If your `apply_transaction` for DEP looks like `acct = acct.copy(); acct["balance"] += amt; return ...`, you mutated a copy, not the original. The accounts list will not be updated and the next transaction for the same account will see the old balance.
3. **Using `>` instead of `<=` for WDR.** The decision table says "approve if amount <= balance." A wallet with exactly enough money should be allowed to spend all of it, but a wallet with strictly less than the amount should not. Off-by-one with the comparison operator changes the boundary case.
4. **Returning `(False, "OK")` or `(True, "INSUFFICIENT_FUNDS")` by mistake.** The boolean and the reason must match: True means it worked, False means it did not.

Diff the outputs character by character if you have to. If you cannot find the bug from reading your code, add `print(f"DEBUG: tx={tx} acct={acct}")` lines at the top of `apply_transaction` and trace what is happening.

---

## Part 5: Reflection

Answer in your notebook. These are open-ended; spend at least 10 minutes.

1. **Sequence, selection, iteration.** Now that you have written code for two of these (the DEP branch is sequence, the WDR branch is selection), reflect on how natural each one felt. Was the selection harder than the sequence? Why? Imagine you had to implement the iteration (the loop in `process_batch`) yourself instead of having it provided. Which would have been hardest?

2. **The cost of pure functions.** `find_account`, `validate_transaction`, and `apply_transaction` are *almost* pure functions: their behaviour is determined entirely by their inputs, with `apply_transaction` being the one exception (it mutates the accounts list). Why does `apply_transaction` mutate while the others do not? What would change if `apply_transaction` were also pure, returning a new accounts list instead of modifying the existing one?

3. **Named status codes vs booleans.** The functions return `(bool, str)` tuples where the string is a status code like `"INSUFFICIENT_FUNDS"` or `"UNKNOWN_ACCOUNT"`. The alternative would be to return just a boolean and have the caller try to guess why. Why is the status code so much more useful? Where do those strings end up in the program's output?

4. **The data dictionary as documentation.** The comments at the top of the file describe the shape of the data. Modern Python has type hints, dataclasses, and TypedDict that can express the same information formally. Why might the author have chosen plain-comment data dictionary instead? When might a typed alternative be worth the extra ceremony?

5. **The decision table as documentation.** Like the data dictionary, the three-line decision table is informal. Some teams use formal decision tables with multi-column grids, especially for complex business rules. When would you reach for the formal version? At what number of rules does the informal style become unmanageable?

6. **What is missing?** This program is a good example of structured programming, but it is not production code. Three things are missing that you would want before deploying it. Name them. (Hint: think about persistence, error handling for malformed input, and testability.)

---

## Reference: The Three Control Structures

Structured programming claims that every algorithm can be expressed using only these three control structures (and their nesting). The claim is theoretical and is taught because it forces a mental model in which control flow is predictable: you can always trace a program by reading it from top to bottom, with no surprises.

| Structure | Looks like | Used for |
|-----------|------------|----------|
| **Sequence** | One statement after another | "Do these things in order." |
| **Selection** | `if`, `elif`, `else`, `match` | "Pick which path to take." |
| **Iteration** | `for`, `while` | "Do something repeatedly." |

Each can be nested inside another. Real code is usually a tree of these three patterns.

The structures Dijkstra and others *opposed* were `goto`, computed jumps, and self-modifying code: control flow that could land anywhere from anywhere, making program behaviour impossible to predict by reading. Python has no `goto` (deliberately; the famous "April Fools" `goto` proposal in 2004 was a joke). The three structures are the only tools you have, and that is the point.

---

## Reference: Functional Decomposition Checklist

When you decompose a program into functions, check each function against these properties:

| Property | Question |
|----------|----------|
| **Single responsibility** | Can you describe what this function does in one sentence without using "and"? |
| **Clear contract** | Do the parameter types and return type tell a caller what to pass and what to expect? |
| **No surprises** | Does the function do exactly what its name suggests, and nothing else (no hidden side effects)? |
| **Pure if possible** | If the function does not need to mutate state, does it avoid mutating state? |
| **Small** | Is the function short enough to read in one screen? |

`find_account` is the best example in this lab: takes a list and an id, returns an index, does nothing else. If you cannot describe a function this cleanly, consider splitting it.

---

## Reference: Data Dictionaries and Decision Tables

These two techniques come from the structured analysis tradition of the 1970s and 1980s. They are simple, language-independent, and surprisingly durable.

A **data dictionary** is a description of the shape of each kind of record in a program, written as text. Examples:

```
Customer:   {customer_id: int, name: str, email: str, registered: date}
Order:      {order_id: int, customer_id: int, items: list, total: float}
Order Item: {sku: str, quantity: int, unit_price: float}
```

A data dictionary is most useful when it lives near the code that uses it (in a comment block, in a README, in a docstring at the top of a module). It is least useful when it lives in a separate document that nobody updates.

A **decision table** is a description of business rules written as a small grid or list. Examples:

```
If customer is a member and order total >= $50  -> free shipping
If customer is a member and order total <  $50  -> $5 flat shipping
If customer is not a member                     -> $10 flat shipping
```

A decision table is most useful when the rules would otherwise be buried in nested `if/else` statements. Writing the table first, then translating it to code, often surfaces missing cases.

---

## Troubleshooting

**`KeyError: 'acct_id'` from inside `apply_transaction`.**
Your validator did not check for missing fields before declaring the transaction valid. Fix the order of checks in `validate_transaction`: required-keys first, then type, then amount.

**`TypeError: unsupported operand type(s) for +: 'float' and 'str'`.**
You did not convert the amount to a float in `validate_transaction`. The amount might come in as a string, and `balance + "25.0"` is a type error. Use `float(tx["amount"])` after validating that the conversion succeeds.

**All rows say `REJECT:UNKNOWN_ACCOUNT` even for valid accounts.**
You probably broke `find_account` while editing nearby code, or the account list was mutated in a way that lost the records. Restore `find_account` from the starter and try again.

**The deposit row succeeds but the balance is wrong.**
You probably wrote `acct["balance"] + amt` instead of `acct["balance"] = acct["balance"] + amt` (or `acct["balance"] += amt`). The first expression computes the new balance and throws it away; only the second writes it back.

**The output has the right rows but in a different order.**
Check that you did not accidentally sort the report rows. The lab expects them in transaction order.

**My program crashes on the negative-amount row before it can be rejected.**
Your validator returned True for the negative-amount case. Re-check that you compare amount to zero with `<=`, not just `<`, and that the comparison happens after the float conversion succeeds.

---

## Further Reading

- **Dijkstra, E. W., "Go To Statement Considered Harmful"** (CACM, 1968). The article that started the structured programming movement. Short, opinionated, and still readable.
- **Wirth, N., "Program Development by Stepwise Refinement"** (CACM, 1971). The original statement of top-down design: write a program at a high level using made-up function names, then refine each function down to working code.
- **The Pragmatic Programmer** (Hunt and Thomas), 20th anniversary edition. Chapters on orthogonality and tracer code revisit the same ideas with modern examples.
- **Refactoring** (Martin Fowler), 2nd edition. The "Smells" chapter catalogs what badly-structured code looks like, which is the inverse of what you wrote in this lab.
