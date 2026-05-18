# Lab 2-1 Structured  Programming

## Overview

In this lab you will:
- Use top-down design and functional decomposition.
- Keep state explicit (pass data in/out of functions, avoid global variables).
- Implement control flow using sequence → selection → iteration.
- Translate a simple “data dictionary” and “decision table” into code.
- Produce a tiny batch report from input records.

## Procedure

- Rather than write all the code from scratch a started template has been provided. 
- You are just required to fill in the missing code
- The starter code is also in the file `Starter.py` and is shown here

```python
# =========================================
# Structured Programming Lab — Starter
# =========================================

from typing import List, Dict, Tuple

# ---- "Data Dictionary" (informal) ----
# Account record: {"acct_id": str, "balance": float}
# Transaction record: {"acct_id": str, "type": "DEP"|"WDR", "amount": float}
# Report row: (acct_id: str, opening: float, delta: float, closing: float, status: str)

# ---- "Decision Table" for withdrawal rules ----
# If WDR and amount <= balance           -> approve
# If WDR and amount > balance            -> decline
# DEP always approved (> 0)

# ---- Sample input (you can edit or replace with file reads later) ----
ACCOUNTS_SEED: List[Dict] = [
    {"acct_id": "A100", "balance": 100.0},
    {"acct_id": "B200", "balance": 50.0},
]

TX_BATCH: List[Dict] = [
    {"acct_id": "A100", "type": "DEP", "amount": 25.0},
    {"acct_id": "A100", "type": "WDR", "amount": 120.0},
    {"acct_id": "B200", "type": "WDR", "amount": 45.0},
    {"acct_id": "B200", "type": "WDR", "amount": 20.0},  # should decline (insufficient after first WDR)
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

## Take note of:

- **Encapsulation**: _balance is not modified directly—only through messages (deposit, withdraw, balance).
- **Abstraction**: Account declares what must exist; concrete accounts decide how.
- **Inheritance**: SavingsAccount and CheckingAccount extend a base.
- **Polymorphism**: Bank.run_month_end() calls monthly_process() without caring which account type it is, each responds differently.
- **Identity vs. state**: Two accounts can have the same balance (state) but are still distinct (identity via different owners/objects).