# Lab 2-1: Object-Oriented Programming

## Overview

Object-oriented programming is the discipline of building programs out of **objects**: bundles of data and the behaviour that operates on that data, packaged so that the inside of the bundle is hidden and the outside is a small, deliberate set of operations. The ideas were articulated in the 1960s by Nygaard and Dahl in Simula, refined by Kay in Smalltalk in the 1970s, and made mainstream by C++, Python, and Java from the 1990s onward. They remain the default way most production systems are built today.

In the previous lab you wrote a banking program using only functions and plain dictionaries. The data and the logic were separate: an account was a dict, and a function in another part of the file knew how to read and write its fields. Anybody with access to the dict could change the balance to anything they liked, and there was nothing stopping a careless caller from setting `account["balance"] = -9999` and breaking every invariant the program depended on.

This lab rebuilds banking using classes. A balance now lives inside an `Account` object and can only be changed by calling `deposit` or `withdraw`, which enforce the rules. We define an abstract `Account` type that declares *what* every account can do without specifying *how*, then two concrete subclasses that differ in their withdrawal rules: a `SavingsAccount` that refuses to go negative and a `CheckingAccount` that allows a bounded overdraft for a fee. Finally a `Bank` object collaborates with those accounts polymorphically: it sends each account the same `monthly_process()` message, and each account responds in its own way.

Most of the code is already written for you. Four small holes in the implementation are marked `TODO` for you to fill in.

The lab is therefore part **reading exercise** (understand the structure before you change it) and part **implementation exercise** (fill in the operative pieces while preserving the structure). When you are done, you will run the program and compare its output against the expected output for verification.

**This lab is hands-on.** You write the code yourself; no AI assistance is needed or expected. The point is to feel the difference between "data and code in separate places" and "data and code packaged together" by writing the code yourself.

---

## Learning Objectives

By the end of this lab, you will be able to:

1. Identify the four pillars of OOP (encapsulation, abstraction, inheritance, polymorphism) in a piece of working code.
2. Define a Python class with private (by convention) state and a public method interface.
3. Use an abstract base class (`ABC`) and `@abstractmethod` to declare an interface that subclasses must implement.
4. Override a method in a subclass and use `super()` to extend a parent's behaviour.
5. Explain "message passing" in the OOP sense: objects collaborate by calling each other's methods, not by reading each other's fields.
6. Verify your implementation against an expected output.

---

## Part 1: Set Up the Workspace

### Step 1.1: Create the lab directory

In a terminal:

```bash
mkdir -p ~/oop-lab
cd ~/oop-lab
```

### Step 1.2: Create the starter file

Create a file called `starter.py` and paste in the following code. Do not modify anything yet; in Part 2 you will read it before changing anything.

```python
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

    # TODO: Try a few withdrawals:
    # - withdraw 120 from savings (should succeed; 150 - 120 = 30)
    # - withdraw 70 from checking (should overdraft; 50 - 70 - 5 fee = -25)
    # Print both accounts after each step to observe the difference.
    print("Savings withdraw 120 ->", s.withdraw(120), s)
    print("Checking withdraw 70 ->", c.withdraw(70), c)

    bank = Bank([s, c])
    print("\nRunning month end...")
    bank.run_month_end()
    print("After month end:", s, c)

    print("\nTotal deposits in bank:", bank.total_deposits())
```

Save the file.

### Step 1.3: Run the starter to see the baseline

Before changing anything, run the starter to see what happens:

```bash
python3 starter.py
```

Output:

```
Before withdrawals: SavingsAccount(owner='Ava', balance=150.00) CheckingAccount(owner='Ben', balance=50.00)
Savings withdraw 120 -> None SavingsAccount(owner='Ava', balance=150.00)
Checking withdraw 70 -> None CheckingAccount(owner='Ben', balance=50.00)

Running month end...
After month end: SavingsAccount(owner='Ava', balance=150.00) CheckingAccount(owner='Ben', balance=50.00)

Total deposits in bank: 200.0
```

The deposits work (the savings account starts at 100, plus a deposit of 50, ends at 150; the checking starts at 25, plus 25, ends at 50). But the two withdraw calls return `None` instead of `True` or `False`, and the balances did not change. The month-end run also did nothing. That is because three of the four TODO methods have an empty body (`pass`), which in Python implicitly returns `None` and performs no side effects. The skeleton of the program works (it constructs the objects, prints them, asks the bank to do month-end), but the operative pieces have not been written yet. Your job in Part 3 is to write them.

### Step 1.4: Create a lab notebook

Create a file `notebook.md` in the workspace. You will record your analyses, decisions, and observations as you go:

```markdown
# OOP Lab Notebook

## Part 2: Reading the starter

## Part 3: Implementation decisions

## Part 4: Verification

## Part 5: Reflection
```

---

## Part 2: Read the Starter Before You Change It

This is a small program, but it has more structure than a casual reader sees on first pass. Before you implement the TODOs, you should be able to answer the questions below from the source alone. Spend at least 15 minutes on this section; do not skip it to get to the coding.

### Question 2.1: The abstract base class

The file opens with an `Account(ABC)` class containing three methods marked `@abstractmethod`. Read it carefully and answer in your notebook:

1. What is the role of an abstract method? What happens if a subclass forgets to implement one and you try to construct it?
2. The three abstract methods (`deposit`, `withdraw`, `balance`) define the *interface* of an account. Why is it useful to declare this interface separately, given that `BaseAccount` will implement all three immediately below?
3. The body of each abstract method is `...` (literal three dots, the Ellipsis literal). Why is the body irrelevant for an abstract method? Could it have been `pass` instead? Would `raise NotImplementedError` have been better?

### Question 2.2: Encapsulation

Look at `BaseAccount.__init__`:

```python
def __init__(self, owner: str, opening_balance: float = 0.0):
    self._balance = float(opening_balance)
    self.owner = owner
```

Answer:

1. The balance field is named `_balance` with a leading underscore. The owner field is named `owner` with no underscore. What is the convention difference, and why does it matter?
2. Python does not actually prevent outside code from writing `acct._balance = -9999`. So in what sense is `_balance` "encapsulated"? What does the convention buy you if the language does not enforce it?
3. There is a `balance()` method that returns `self._balance` but no `set_balance()` method. Why not? If a caller wants to change the balance, what must they do instead?

### Question 2.3: The class hierarchy

The starter declares four classes. Draw the inheritance hierarchy in your notebook:

```
Account (abstract)
  |
  +-- BaseAccount
        |
        +-- SavingsAccount
        |
        +-- CheckingAccount
```

Answer:

1. Why is the hierarchy a chain (`Account -> BaseAccount -> SavingsAccount`) rather than each subclass inheriting directly from `Account`?
2. `SavingsAccount` does not define `withdraw`. Where does its `withdraw` method come from?
3. `CheckingAccount` *does* define `withdraw`. What happens to the `withdraw` it inherited from `BaseAccount`? Is the inherited version still callable from anywhere, and if so, how?

### Question 2.4: Polymorphism in `Bank.run_month_end`

Look at this loop in `Bank.run_month_end`:

```python
for acct in self.accounts:
    if hasattr(acct, "monthly_process"):
        getattr(acct, "monthly_process")()
```

Answer:

1. What does this loop actually do? Walk through it for a list `[savings, checking]`.
2. The same method name (`monthly_process`) calls different code for savings and checking accounts. This is the textbook definition of **polymorphism**. Why is this more flexible than writing `if isinstance(acct, SavingsAccount): ... elif isinstance(acct, CheckingAccount): ...`?
3. The `hasattr` check is a safeguard: not every `Account` subclass is required to have `monthly_process`. Why is that the right design choice here, given that the abstract `Account` class lists only `deposit`, `withdraw`, and `balance` as required?

### Question 2.5: Where state lives

A key principle of OOP is that each object carries its own state, hidden from the others. Answer in your notebook:

1. If you create two `SavingsAccount` instances `a = SavingsAccount("Ava", 100)` and `b = SavingsAccount("Bob", 100)` and call `a.deposit(50)`, what happens to `b._balance`?
2. The bank has a `self.accounts` list. If you mutate that list from outside (`bank.accounts.append(some_acct)`), does the bank know? Should it?
3. Compare this to the structured-programming lab, where the list of accounts was a module-level `ACCOUNTS_SEED` constant. What would change in this program if you wanted to run two independent banks (test and production) at the same time?

### Reference: Things you should have noticed

After you write your own answers, check against this list. You should have noticed at least:

**Abstract base class (Q2.1):** An `@abstractmethod` declares that any concrete subclass *must* override the method. Trying to instantiate a subclass that has not overridden all abstract methods raises `TypeError: Can't instantiate abstract class ...`. The interface is declared separately so a caller (like `Bank`) can program against the abstraction `Account` without depending on any particular concrete implementation; this lets you later add `MoneyMarketAccount` without changing the bank. The body of an abstract method is irrelevant because the body is never executed; `...`, `pass`, and `raise NotImplementedError` all work, but `...` is the modern idiom and matches type stubs.

**Encapsulation (Q2.2):** The leading underscore on `_balance` is a Python convention meaning "treat this as private; do not poke at it from outside the class." Python does not enforce this, but every Python tool (linters, IDEs, code reviews) treats it as a signal. The convention buys you a contract with future readers: anyone modifying balance through means other than `deposit`/`withdraw` is breaking the rules of the class and owns the resulting bugs. There is no `set_balance` because we never want callers to bypass the deposit and withdraw rules.

**Class hierarchy (Q2.3):** `BaseAccount` exists so the two concrete account types can share the deposit logic, the balance accessor, and the `__repr__`. Without it, both subclasses would duplicate that code. `SavingsAccount`'s `withdraw` comes from `BaseAccount` via inheritance: when you call `s.withdraw(amount)`, Python looks for `withdraw` on `SavingsAccount`, does not find it, walks up to `BaseAccount`, finds it there. `CheckingAccount.withdraw` *overrides* the inherited version: when you call `c.withdraw(amount)`, Python finds the `CheckingAccount` version first and stops looking. The `BaseAccount` version is still callable explicitly from `CheckingAccount.withdraw` via `super().withdraw(amount)`, though this implementation does not use that.

**Polymorphism (Q2.4):** The loop iterates over each account and, if it implements `monthly_process`, calls it. For `[savings, checking]`, the call dispatches first to `SavingsAccount.monthly_process` (which adds interest) and then to `CheckingAccount.monthly_process` (which deducts a fee). This is more flexible than `isinstance` chains because adding a new account type requires only adding a new class with a `monthly_process` method; the bank code does not change. With `isinstance` chains, the bank would have to be modified every time a new account type appeared, which is the classic "shotgun surgery" code smell.

**State (Q2.5):** Each object has its own `_balance`; modifying `a._balance` does not affect `b._balance` because they are separate instances. `bank.accounts` is a plain Python list, so external code that mutates it does affect the bank; if you wanted to prevent that you would copy on input and return copies from accessors. Two independent banks would simply be two `Bank` objects: `test_bank = Bank([...])` and `prod_bank = Bank([...])`. In the structured-programming lab, running two independent batches required resetting global state, which is fragile.

---

## Part 3: Implement the TODOs

You will implement four pieces of code: one in `BaseAccount`, one in `SavingsAccount`, and two in `CheckingAccount`. Run the program after each one to confirm progress.

Make a copy of the starter so you can compare:

```bash
cp starter.py work.py
```

Edit `work.py` from now on; leave `starter.py` as a reference.

### Step 3.1: Implement `BaseAccount.withdraw`

Open `work.py` and find the `withdraw` method in `BaseAccount`. Replace its body with an implementation that:

1. Returns `False` if `amount` is zero or negative (a withdrawal of zero is meaningless; a withdrawal of a negative number is a deposit in disguise and should not be allowed through this method).
2. If `self._balance >= amount`, subtract `amount` from `self._balance` and return `True`.
3. Otherwise, return `False`. Do not change `self._balance`.

**Design hint:** Notice the asymmetry between `deposit` and `withdraw`. `deposit` raises `ValueError` for a bad amount; `withdraw` returns `False`. That is intentional: a programmer-error amount (negative deposit) should crash loudly because it almost certainly indicates a bug in the caller, but an insufficient-funds withdrawal is a normal business outcome that the caller wants to handle, not a bug. Different failure modes deserve different error styles.

After implementing, run:

```bash
python3 work.py
```

You should now see the savings withdrawal succeed:

```
Savings withdraw 120 -> True SavingsAccount(owner='Ava', balance=30.00)
```

The checking withdrawal will still print `False` (or `None` if you have not changed it) because its overriding method is still empty.

### Step 3.2: Implement `SavingsAccount.monthly_process`

Find the `monthly_process` method in `SavingsAccount`. Replace its body with an implementation that adds 0.2% of the current balance to the balance:

```
new_balance = old_balance + old_balance * 0.002
```

Equivalently `self._balance += self._balance * 0.002`. One line.

**Run** and check that the savings balance grows slightly after month-end. With a balance of 30.00 after the earlier withdrawal, 0.2% interest is 0.06, so the new balance should be 30.06.

### Step 3.3: Implement `CheckingAccount.withdraw`

Find the `withdraw` method in `CheckingAccount`. This is the most involved TODO. Implement it as follows:

1. Return `False` if `amount` is zero or negative.
2. Compute the *projected* balance after withdrawal: `projected = self._balance - amount`.
3. If `projected` is below `-self.overdraft_limit`, the overdraft limit would be exceeded. Return `False` and do not change `self._balance`.
4. Otherwise, set `self._balance = projected`.
5. If `self._balance` is now below zero, charge the fee: `self._balance -= self.fee`. (Note: the fee is charged *after* the withdrawal goes through, so the balance can dip below the overdraft limit by exactly the fee amount. This matches typical retail-banking behaviour.)
6. Return `True`.

**Design hint:** Notice that step 3 checks the projected balance against `-overdraft_limit`, not against 0. The whole point of an overdraft is that the balance is allowed to be negative; the limit defines how negative. Putting the check the wrong way around is the most common bug in this method, so think through the case `balance=50, amount=70, overdraft_limit=50` before you write the code: projected is `-20`, which is greater than `-50`, so it should be allowed.

**Run.** With Ben's checking starting at 50 and withdrawing 70: `projected = 50 - 70 = -20`, which is greater than `-50`, so allowed. Then since `-20 < 0`, charge the fee of 5, leaving `-25`:

```
Checking withdraw 70 -> True CheckingAccount(owner='Ben', balance=-25.00)
```

### Step 3.4: Implement `CheckingAccount.monthly_process`

Find the `monthly_process` method in `CheckingAccount`. Subtract `1.0` from `self._balance`:

```python
self._balance -= 1.0
```

One line.

**Run** the full program. Now every operative method is implemented. Compare your output to the expected output in Part 4.

---

## Part 4: Verify Against the Expected Output

Run the finished program:

```bash
python3 work.py
```

Your output should match this exactly:

```
Before withdrawals: SavingsAccount(owner='Ava', balance=150.00) CheckingAccount(owner='Ben', balance=50.00)
Savings withdraw 120 -> True SavingsAccount(owner='Ava', balance=30.00)
Checking withdraw 70 -> True CheckingAccount(owner='Ben', balance=-25.00)

Running month end...
After month end: SavingsAccount(owner='Ava', balance=30.06) CheckingAccount(owner='Ben', balance=-26.00)

Total deposits in bank: 4.059999999999999
```

Walk through it row by row before you congratulate yourself; verifying that the output is right is the same skill as writing the code.

### Step-by-step trace

| Step | Action | Result |
|----|----|----|
| 1 | `SavingsAccount("Ava", 100.0)` | Ava: balance 100.00 |
| 2 | `CheckingAccount("Ben", 25.0, overdraft_limit=50, fee=5)` | Ben: balance 25.00 |
| 3 | `s.deposit(50)` | Ava: 100 + 50 = 150.00 |
| 4 | `c.deposit(25)` | Ben: 25 + 25 = 50.00 |
| 5 | `s.withdraw(120)` | 150 >= 120, so deduct. Ava: 30.00. Returns True. |
| 6 | `c.withdraw(70)` | Projected 50 - 70 = -20, which is greater than -50 (allowed). Then -20 < 0 so charge fee 5: Ben: -25.00. Returns True. |
| 7 | `bank.run_month_end()` | For each account, call `monthly_process`. |
| 7a | `s.monthly_process()` | 30 + (30 * 0.002) = 30 + 0.06 = 30.06. |
| 7b | `c.monthly_process()` | -25 - 1 = -26.00. |
| 8 | `bank.total_deposits()` | 30.06 + (-26.00) = 4.06, displayed as `4.059999999999999` due to floating-point representation. |

The "total deposits" number ending in `...9999` rather than a clean `4.06` is the classic floating-point artifact: `0.06` and `-1.0` and `30.0` cannot all be represented exactly in binary, so the addition produces a number that is *almost* 4.06 but not quite. This is not a bug in your code; it is a property of IEEE 754 doubles. Production banking code uses fixed-point or decimal arithmetic (`decimal.Decimal` in Python) for exactly this reason.

### If your output differs

The most common ways for the output to differ:

1. **The savings withdrawal failed.** You probably wrote `if self._balance > amount` (strictly greater) instead of `>=`. A withdrawal of exactly the balance should be allowed.
2. **The checking withdrawal failed when it should have succeeded.** You probably compared `projected` against `0` instead of against `-self.overdraft_limit`. The whole point of an overdraft is that the balance is allowed to be negative.
3. **The fee was charged twice or not at all.** The fee is charged once, *after* the withdrawal goes through, only if the new balance is below zero. If you charge it before the balance update, or check the condition against `projected` rather than the updated `self._balance`, the math comes out wrong.
4. **You returned `True` from `withdraw` but did not actually change the balance.** Easy mistake: you computed `projected` but never assigned it to `self._balance`. The return value and the side effect must match.
5. **The interest amount is wrong.** 0.2% is `0.002`, not `0.02` or `0.2`. The most common typo here is `0.02`, which would give 30 + 0.6 = 30.60 instead of 30.06.

If you cannot find the bug from reading your code, add `print(f"DEBUG: balance={self._balance}, amount={amount}")` lines at the top of the offending method and trace what is happening.

---

## Part 5: Reflection

Answer in your notebook. These are open-ended; spend at least 10 minutes.

1. **Encapsulation in practice.** In the structured-programming lab, an account was a dictionary and any function could mutate its `balance` field freely. In this lab, the balance is `_balance` with a leading underscore, and the only sanctioned way to change it is through `deposit` and `withdraw`. Did that constraint help you, hurt you, or both? When in this lab would you have *wanted* to reach in and set `_balance` directly, and what would have gone wrong if you had?

2. **The cost of inheritance.** `SavingsAccount` and `CheckingAccount` both inherit from `BaseAccount`, which inherits from `Account`. That is a three-deep hierarchy for a 100-line program. What did you gain by the layering? What is the cost when the hierarchy grows to five or six levels deep? At what point would you stop adding layers and start composing instead?

3. **Polymorphism vs explicit dispatch.** `Bank.run_month_end` calls `acct.monthly_process()` polymorphically; it does not care which kind of account it has. The alternative would be `if isinstance(acct, SavingsAccount): add_interest(acct) elif isinstance(acct, CheckingAccount): charge_fee(acct)`. Both work for the current program. Which would you prefer if you were adding a third account type next week? Which would you prefer if you were trying to understand the program for the first time?

4. **Abstract base class as documentation.** The `Account` ABC declares three methods (`deposit`, `withdraw`, `balance`) but not `monthly_process`. Why? What does that say about which behaviours are considered "every account must have this" versus "some accounts happen to have this"? How might you have made `monthly_process` mandatory if you wanted to?

5. **The same domain, two designs.** Compare this lab's code to the structured-programming lab's. Roughly the same line count, roughly the same banking domain. What did you gain by switching to OOP? What did you lose? (Be honest; OOP is not strictly better than structured programming for every problem. Some problems, especially data pipelines, are clearer as functions over plain records.)

6. **What is missing?** This program is a good demonstration of OOP, but it is not production code. Three things are missing that you would want before deploying it. Name them. (Hints: persistence, concurrency, money arithmetic.)

---

## Reference: The Four Pillars of OOP

Most OOP textbooks list four "pillars". This lab touches on all four.

| Pillar | What it means | Where it appears in this lab |
|--------|---------------|------------------------------|
| **Encapsulation** | Hide internal state; expose a controlled interface. | `_balance` is hidden behind `deposit`, `withdraw`, `balance()`. |
| **Abstraction** | Expose *what* an object does, hide *how* it does it. | The `Account` ABC declares the interface; concrete classes decide the implementation. |
| **Inheritance** | One class extends another, reusing its behaviour. | `SavingsAccount` and `CheckingAccount` inherit from `BaseAccount`. |
| **Polymorphism** | The same method call on different objects produces different behaviour. | `Bank.run_month_end` calls `monthly_process` on each account; savings adds interest, checking charges a fee. |

A common rookie mistake is to assume all four are always good and to use them everywhere. They are *tools*, and each has costs:

- Encapsulation costs you discoverability: a caller cannot see what an object is doing internally and must trust the interface.
- Abstraction costs you concreteness: you have to read multiple files to understand what `acct.withdraw(50)` actually does.
- Inheritance costs you flexibility: a deep hierarchy makes it hard to mix and match behaviours, which is why modern OOP often prefers *composition* (an object that contains other objects) over inheritance.
- Polymorphism costs you traceability: when you read `acct.monthly_process()` you cannot tell, without context, which method will run.

The art is in knowing which tool fits which job.

---

## Reference: Abstract Base Classes in Python

Python's `abc` module gives you tools for declaring interfaces:

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...

    @abstractmethod
    def perimeter(self) -> float: ...
```

Rules:

1. A class that inherits from `ABC` and has any `@abstractmethod` cannot be instantiated. `Shape()` raises `TypeError`.
2. A subclass must override every abstract method to become instantiable. If `Circle(Shape)` defines `area` but not `perimeter`, `Circle()` still raises `TypeError`.
3. Abstract methods can have a body; the body is inherited and callable via `super().area()` from the subclass. This is useful when the abstract method has a default implementation that subclasses extend.

Python's ABCs are weaker than Java's interfaces or C++'s pure virtual classes because Python is duck-typed: a class that *does not* inherit from `Account` but has `deposit`, `withdraw`, and `balance` methods will still work everywhere an `Account` is expected. The ABC is more about *declaring intent* than enforcing structure. Some Python codebases skip ABCs entirely and rely on duck typing plus type hints; others use ABCs religiously for clarity. The choice is stylistic.

---

## Reference: Encapsulation Checklist

When you write a class, check each field against these questions:

| Question | If yes |
|----------|--------|
| Could outside code change this field directly and break an invariant? | Prefix with `_`; provide a method instead. |
| Should it never change after construction? | Treat as immutable; do not expose a setter. |
| Does outside code need to *read* it? | Provide a method or `@property`. |
| Does outside code need to *modify* it through a specific rule? | Provide a method named for the operation (`deposit`, not `set_balance`). |
| Does outside code need unrestricted modification? | Probably you have not thought hard enough; reconsider whether this is really part of the object's state or whether it belongs somewhere else. |

The smell to watch for is the `set_x` method for every field. If your class is just getters and setters with no real behaviour, you have written a data bag, not an object. Python `dataclasses` and `namedtuple` do data bags better and make the data-bag nature explicit.

---

## Reference: Inheritance vs Composition

Inheritance ("is a") and composition ("has a") are the two main ways to reuse behaviour between classes. Both have their place; modern OOP guidance generally favours composition.

**Inheritance**, as used in this lab:

```python
class SavingsAccount(BaseAccount):
    def monthly_process(self):
        self._balance += self._balance * 0.002
```

A `SavingsAccount` *is a* `BaseAccount`. It automatically inherits all its parent's methods.

**Composition**, an alternative design:

```python
class Account:
    def __init__(self, owner, balance, withdrawal_policy, monthly_policy):
        self.owner = owner
        self._balance = balance
        self._withdrawal_policy = withdrawal_policy
        self._monthly_policy = monthly_policy

    def withdraw(self, amount):
        return self._withdrawal_policy.apply(self, amount)

    def monthly_process(self):
        self._monthly_policy.apply(self)
```

Here a savings account is constructed by passing in a `NoOverdraftPolicy` and an `InterestPolicy`. A checking account passes in an `OverdraftPolicy` and a `MaintenanceFeePolicy`. The same `Account` class supports both, and new behaviours (a "premium account" that adds rewards) are new policies, not new subclasses.

Composition is more flexible (you can mix and match policies) but adds more moving parts. Inheritance is simpler for a fixed taxonomy. The famous design guideline is "favour composition over inheritance", attributed to the Gang of Four design-patterns book; it is a useful default but not an absolute rule.

---

## Troubleshooting

**`TypeError: Can't instantiate abstract class BaseAccount with abstract method withdraw`.**
You tried to construct an object whose class still has an unimplemented `@abstractmethod`. Check that `BaseAccount.withdraw` is no longer `pass`.

**`AttributeError: 'NoneType' object has no attribute '_balance'`.**
Somewhere you wrote `self._balance = self.deposit(amount)` (or similar) and `deposit` returns `None`. Methods that mutate should usually return `None`; methods that compute should return a value. Do not assign the return of a mutating method to anything.

**The savings interest is exactly $0.06 in your math but the displayed balance is `30.060000000000002` or similar.**
This is normal IEEE 754 floating-point behaviour. Real banking code uses `decimal.Decimal`. For this lab, the `:.2f` formatter in `__repr__` hides the artifact; only the raw `total_deposits()` call exposes it.

**Every call to `monthly_process` raises `AttributeError`.**
`Bank.run_month_end` uses `hasattr` and `getattr` to safely call the method only when it exists. If you see an `AttributeError` despite that, you probably misspelled the method (`monthy_process`? `monthly_proccess`?). The misspelled definition does not get found by `hasattr("monthly_process")`, so the bank silently skips it, but a direct call elsewhere would fail.

**Multiple withdrawals are being applied even when they should fail.**
You probably wrote the side effect *before* the guard, e.g. `self._balance -= amount; if self._balance >= 0: return True`. Check the order: validate first, mutate only if validation passed.

**`super().__init__()` raises something weird.**
Check the argument order. `CheckingAccount.__init__` calls `super().__init__(owner, opening_balance)`. If you reversed the arguments, the owner becomes a number and the opening balance becomes a string.

---

## Further Reading

- **The Python Tutorial, "Classes"** at docs.python.org. Authoritative reference for Python's class model, including the subtleties of `super()`, MRO, and `__init_subclass__`.
- **Fluent Python, 2nd edition** (Luciano Ramalho). The "Object-Oriented Idioms" chapters cover ABCs, protocols, and the design tradeoffs in idiomatic Python OOP.
- **Design Patterns: Elements of Reusable Object-Oriented Software** (Gamma, Helm, Johnson, Vlissides). The 1994 "Gang of Four" book. Its concrete patterns are sometimes dated, but the discussions of when to use inheritance versus composition remain the standard reference.
- **Object-Oriented Software Construction, 2nd edition** (Bertrand Meyer). The definitive 1300-page treatment of OOP from first principles. Long but worth it for anyone going deep on the subject.
- **"Goto Considered Harmful Considered Harmful"** (Frank Rubin, CACM 1987). A reply to Dijkstra's structured-programming classic, included here because the same kind of healthy disagreement applies to OOP: every methodology has both true believers and credible critics, and you should read both.
