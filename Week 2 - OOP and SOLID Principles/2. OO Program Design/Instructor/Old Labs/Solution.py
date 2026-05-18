from abc import ABC, abstractmethod
from typing import List


class Account(ABC):
    @abstractmethod
    def deposit(self, amount: float) -> None:
        ...

    @abstractmethod
    def withdraw(self, amount: float) -> bool:
        ...

    @abstractmethod
    def balance(self) -> float:
        ...


class BaseAccount(Account):
    def __init__(self, owner: str, opening_balance: float = 0.0):
        self._balance = float(opening_balance)
        self.owner = owner

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("amount must be positive")
        self._balance += amount

    def withdraw(self, amount: float) -> bool:
        if amount <= 0:
            return False
        if self._balance >= amount:
            self._balance -= amount
            return True
        return False

    def balance(self) -> float:
        return self._balance

    def __repr__(self):
        return f"{self.__class__.__name__}(owner={self.owner!r}, balance={self._balance:.2f})"


class SavingsAccount(BaseAccount):
    def monthly_process(self) -> None:
        # add 0.2% interest
        self._balance += self._balance * 0.002


class CheckingAccount(BaseAccount):
    def __init__(self, owner: str, opening_balance: float = 0.0, overdraft_limit: float = 50.0, fee: float = 5.0):
        super().__init__(owner, opening_balance)
        self.overdraft_limit = float(overdraft_limit)
        self.fee = float(fee)

    def withdraw(self, amount: float) -> bool:
        if amount <= 0:
            return False
        projected = self._balance - amount
        # allow down to -overdraft_limit
        if projected >= -self.overdraft_limit:
            self._balance = projected
            # charge fee if crossing below zero
            if self._balance < 0:
                self._balance -= self.fee
            return True
        return False

    def monthly_process(self) -> None:
        # small maintenance fee
        self._balance -= 1.0


class Bank:
    def __init__(self, accounts: List[Account]):
        self.accounts = list(accounts)

    def total_deposits(self) -> float:
        return sum(acct.balance() for acct in self.accounts)

    def run_month_end(self) -> None:
        for acct in self.accounts:
            if hasattr(acct, "monthly_process"):
                getattr(acct, "monthly_process")()


if __name__ == "__main__":
    s = SavingsAccount("Ava", 100.0)
    c = CheckingAccount("Ben", 25.0, overdraft_limit=50.0, fee=5.0)

    s.deposit(50)   # 150
    c.deposit(25)   # 50

    print("Before withdrawals:", s, c)

    # Savings: disallow overdraft
    print("Savings withdraw 120 ->", s.withdraw(120), s)  # True, new balance 30
    # Checking: can dip below 0 (fee if so)
    print("Checking withdraw 70 ->", c.withdraw(70), c)   # 50-70 = -20, fee 5 => -25

    bank = Bank([s, c])
    print("\nRunning month end...")
    bank.run_month_end()
    print("After month end:", s, c)  # Savings +0.2% interest; Checking -$1 fee

    print("\nTotal deposits in bank:", bank.total_deposits())
