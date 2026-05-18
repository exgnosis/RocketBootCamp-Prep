# Lab 2-1 OO Programming

## Overview

In this lab you will:
- Model a small domain with classes/objects (object model: state + behavior + identity).
- Apply encapsulation (hide internals behind an interface).
- Use abstraction via an abstract base class (what, not how).
- Demonstrate inheritance and polymorphism (same message, different response).
- Demonstrate “message passing”: objects collaborate by calling each other’s methods.

## Procedure

- Rather than write all the code from scratch a started template has been provided. 
- You are just required to fill in the missing code
- The starter code is also in the file `Starter.py` and is shown here

```python
# =========================
# Starter C0de
# =========================

from abc import ABC, abstractmethod
from typing import List


# 1) Abstraction (interface): what every account can do
class Account(ABC):
    """Abstract account type: defines the interface (messages) clients can send."""

    @abstractmethod
    def deposit(self, amount: float) -> None:
        ...

    @abstractmethod
    def withdraw(self, amount: float) -> bool:
        """Return True if withdrawal succeeds, else False."""
        ...

    @abstractmethod
    def balance(self) -> float:
        ...


# 2) Encapsulation: keep raw balance hidden; expose via methods/properties
class BaseAccount(Account):
    def __init__(self, owner: str, opening_balance: float = 0.0):
        # _balance is internal state (encapsulated)
        self._balance = float(opening_balance)
        self.owner = owner  # identity: who owns it

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("amount must be positive")
        self._balance += amount

    # TODO: Implement withdraw with simple guard (no overdraft)
    # Deduct only if there is enough balance; return True/False
    def withdraw(self, amount: float) -> bool:
        # TODO: your code here
        pass

    # Expose read-only balance via a method (could also use @property)
    def balance(self) -> float:
        return self._balance

    def __repr__(self):
        return f"{self.__class__.__name__}(owner={self.owner!r}, balance={self._balance:.2f})"


# 3) Inheritance + Polymorphism:
#    SavingsAccount and CheckingAccount share BaseAccount behavior,
#    but specialize withdrawal rules (same message -> different behavior).

class SavingsAccount(BaseAccount):
    """No overdraft; earns a tiny monthly interest via monthly_process()."""

    # TODO: Implement monthly_process to add interest (e.g., 0.2% of balance)
    def monthly_process(self) -> None:
        # TODO: your code here
        pass


class CheckingAccount(BaseAccount):
    """Allows small overdraft with a fee when overdrawn."""

    def __init__(self, owner: str, opening_balance: float = 0.0, overdraft_limit: float = 50.0, fee: float = 5.0):
        super().__init__(owner, opening_balance)
        self.overdraft_limit = float(overdraft_limit)
        self.fee = float(fee)

    # TODO: Override withdraw:
    # - permit going negative down to -overdraft_limit (charge fee if crosses below 0)
    # - return True/False
    def withdraw(self, amount: float) -> bool:
        # TODO: your code here
        pass

    # TODO: Implement monthly_process to charge a $1 maintenance fee
    def monthly_process(self) -> None:
        # TODO: your code here
        pass


# 4) Collaboration / “message passing”: a simple Bank that sends messages to accounts
class Bank:
    def __init__(self, accounts: List[Account]):
        self.accounts = list(accounts)

    def total_deposits(self) -> float:
        return sum(acct.balance() for acct in self.accounts)

    def run_month_end(self) -> None:
        # Polymorphic call: each account responds with its own monthly behavior
        for acct in self.accounts:
            # Some accounts implement monthly_process; others might not.
            # We can "duck type" safely with hasattr.
            if hasattr(acct, "monthly_process"):
                getattr(acct, "monthly_process")()


# 5) Tiny test drive — run this file to see it work
if __name__ == "__main__":
    s = SavingsAccount("Ava", 100.0)
    c = CheckingAccount("Ben", 25.0, overdraft_limit=50.0, fee=5.0)

    s.deposit(50)
    c.deposit(25)

    print("Before withdrawals:", s, c)

    # TODO: Try a few withdrawals:
    # - withdraw 120 from savings (should succeed if enough)
    # - withdraw 70 from checking (may go overdraft and charge fee)
    # Print both accounts after each step to observe differences.
    # TODO: your code here

    bank = Bank([s, c])
    print("\nRunning month end...")
    bank.run_month_end()
    print("After month end:", s, c)

    print("\nTotal deposits in bank:", bank.total_deposits())

```

## Take note of:

- **Encapsulation**: _balance is not modified directly—only through messages (deposit, withdraw, balance).
- **Abstraction**: Account declares what must exist; concrete accounts decide how.
- **Inheritance**: SavingsAccount and CheckingAccount extend a base.
- **Polymorphism**: Bank.run_month_end() calls monthly_process() without caring which account type it is, each responds differently.
- **Identity vs. state**: Two accounts can have the same balance (state) but are still distinct (identity via different owners/objects).