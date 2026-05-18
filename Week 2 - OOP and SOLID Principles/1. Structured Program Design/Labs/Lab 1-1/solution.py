from typing import List, Dict, Tuple

ACCOUNTS_SEED: List[Dict] = [
    {"acct_id": "A100", "balance": 100.0},
    {"acct_id": "B200", "balance": 50.0},
]

TX_BATCH: List[Dict] = [
    {"acct_id": "A100", "type": "DEP", "amount": 25.0},
    {"acct_id": "A100", "type": "WDR", "amount": 120.0},
    {"acct_id": "B200", "type": "WDR", "amount": 45.0},
    {"acct_id": "B200", "type": "WDR", "amount": 20.0},
    {"acct_id": "Z999", "type": "DEP", "amount": 10.0},
    {"acct_id": "A100", "type": "DEP", "amount": -5.0},
]

def find_account(accounts: List[Dict], acct_id: str) -> int:
    for i in range(len(accounts)):
        if accounts[i]["acct_id"] == acct_id:
            return i
    return -1

def validate_transaction(tx: Dict) -> Tuple[bool, str]:
    # required keys
    if not all(k in tx for k in ("acct_id", "type", "amount")):
        return False, "MISSING_FIELDS"
    if tx["type"] not in ("DEP", "WDR"):
        return False, "INVALID_TYPE"
    try:
        amt = float(tx["amount"])
    except (TypeError, ValueError):
        return False, "INVALID_AMOUNT"
    if amt <= 0.0:
        return False, "NONPOSITIVE_AMOUNT"
    return True, ""

def apply_transaction(accounts: List[Dict], tx: Dict) -> Tuple[bool, str]:
    idx = find_account(accounts, tx["acct_id"])
    if idx == -1:
        return False, "UNKNOWN_ACCOUNT"

    acct = accounts[idx]
    amt = float(tx["amount"])

    if tx["type"] == "DEP":
        acct["balance"] = acct["balance"] + amt
        return True, "OK"
    elif tx["type"] == "WDR":
        if amt <= acct["balance"]:
            acct["balance"] = acct["balance"] - amt
            return True, "OK"
        else:
            return False, "INSUFFICIENT_FUNDS"
    else:
        return False, "UNKNOWN_TYPE"

def process_batch(accounts_seed: List[Dict], tx_batch: List[Dict]) -> Tuple[List[Tuple], List[Dict]]:
    accounts = [{"acct_id": a["acct_id"], "balance": float(a["balance"])} for a in accounts_seed]
    openings = {a["acct_id"]: a["balance"] for a in accounts}
    deltas = {a["acct_id"]: 0.0 for a in accounts}

    report_rows: List[Tuple] = []

    for tx in tx_batch:
        ok, reason = validate_transaction(tx)
        if not ok:
            acct_id = tx.get("acct_id", "?")
            opening = openings.get(acct_id, 0.0)
            delta = deltas.get(acct_id, 0.0)
            closing = opening + delta
            report_rows.append((acct_id, opening, delta, closing, f"REJECT:{reason}"))
            continue

        applied, reason = apply_transaction(accounts, tx)
        acct_id = tx["acct_id"]
        if applied:
            if tx["type"] == "DEP":
                deltas[acct_id] = deltas.get(acct_id, 0.0) + tx["amount"]
            else:
                deltas[acct_id] = deltas.get(acct_id, 0.0) - tx["amount"]
            idx = find_account(accounts, acct_id)
            closing = accounts[idx]["balance"]
            report_rows.append((acct_id, openings.get(acct_id, 0.0), deltas[acct_id], closing, "APPLIED"))
        else:
            closing = openings.get(acct_id, 0.0) + deltas.get(acct_id, 0.0)
            report_rows.append((acct_id, openings.get(acct_id, 0.0), deltas.get(acct_id, 0.0), closing, f"REJECT:{reason}"))

    return report_rows, accounts

def render_report(rows: List[Tuple]) -> None:
    print("\n=== BATCH REPORT ===")
    print(f"{'Acct':<6} {'Opening':>10} {'Delta':>10} {'Closing':>10}  Status")
    for acct, opening, delta, closing, status in rows:
        print(f"{acct:<6} {opening:>10.2f} {delta:>10.2f} {closing:>10.2f}  {status}")

def main() -> None:
    rows, final_accounts = process_batch(ACCOUNTS_SEED, TX_BATCH)
    render_report(rows)

    print("\nFinal account balances:")
    for a in final_accounts:
        print(f" - {a['acct_id']}: {a['balance']:.2f}")

if __name__ == "__main__":
    main()
