# =========================================
# Object-Oriented Programming Lab - Starter
# =========================================

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

    # TODO: Implement withdraw with a simple guard (no overdraft).
    # Deduct only if there is enough balance; return True if it succeeded,
    # False otherwise. Reject non-positive amounts by returning False.
    def withdraw(self, amount: float) -> bool:
        # TODO: your code here
        pass

    # Expose read-only balance via a method (could also use @property)
    def balance(self) -> float:
        return self._balance

    def __repr__(self):
        return f"{self.__class__.__name__}(owner={self.owner!r}, balance={self._balance:.2f})"


# 3) Inheritance + Polymorphism:
#    SavingsAccount and CheckingAccount share BaseAccount behaviour,
#    but specialize withdrawal rules (same message -> different behaviour).

class SavingsAccount(BaseAccount):
    """No overdraft; earns a tiny monthly interest via monthly_process()."""

    # TODO: Implement monthly_process to add 0.2% interest to the balance.
    def monthly_process(self) -> None:
        # TODO: your code here
        pass


class CheckingAccount(BaseAccount):
    """Allows a small overdraft with a fee when overdrawn."""

    def __init__(self, owner: str, opening_balance: float = 0.0,
                 overdraft_limit: float = 50.0, fee: float = 5.0):
        super().__init__(owner, opening_balance)
        self.overdraft_limit = float(overdraft_limit)
        self.fee = float(fee)

    # TODO: Override withdraw.
    # - Permit going negative down to -overdraft_limit.
    # - If the balance ends up below 0 after the withdrawal, charge the fee.
    # - Return True on success, False if the overdraft limit would be exceeded
    #   or the amount is not positive.
    def withdraw(self, amount: float) -> bool:
        # TODO: your code here
        pass

    # TODO: Implement monthly_process to charge a $1 maintenance fee
    # (i.e., subtract 1.0 from the balance).
    def monthly_process(self) -> None:
        # TODO: your code here
        pass


# 4) Collaboration / "message passing": a simple Bank that sends messages to accounts
class Bank:
    def __init__(self, accounts: List[Account]):
        self.accounts = list(accounts)

    def total_deposits(self) -> float:
        return sum(acct.balance() for acct in self.accounts)

    def run_month_end(self) -> None:
        # Polymorphic call: each account responds with its own monthly behaviour.
        for acct in self.accounts:
            # Some accounts implement monthly_process; others might not.
            # We can "duck type" safely with hasattr.
            if hasattr(acct, "monthly_process"):
                getattr(acct, "monthly_process")()


# 5) Tiny test drive: run this file to see it work
if __name__ == "__main__":
    s = SavingsAccount("Ava", 100.0)
    c = CheckingAccount("Ben", 25.0, overdraft_limit=50.0, fee=5.0)

    s.deposit(50)
    c.deposit(25)

    print("Before withdrawals:", s, c)

    # The two withdrawal calls below exercise the methods you will implement.
    # Before you implement them, you will see "None" instead of True/False,
    # and balances will not change. After you implement them, the savings
    # withdrawal should succeed (150 - 120 = 30) and the checking withdrawal
    # should overdraft (50 - 70 - 5 fee = -25).
    print("Savings withdraw 120 ->", s.withdraw(120), s)
    print("Checking withdraw 70 ->", c.withdraw(70), c)

    bank = Bank([s, c])
    print("\nRunning month end...")
    bank.run_month_end()
    print("After month end:", s, c)

    print("\nTotal deposits in bank:", bank.total_deposits())
