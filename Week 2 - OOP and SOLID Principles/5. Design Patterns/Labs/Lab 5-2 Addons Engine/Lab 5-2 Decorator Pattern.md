# Lab 5-2: The Decorator Pattern

## Overview

The **Decorator** pattern is one of the most useful entries in the 1994 Gang of Four catalogue of design patterns. It solves a specific problem that comes up over and over in object-oriented design: you have a basic thing, and you want to attach optional features to it at runtime, in any combination, without writing a separate class for every possible combination.

The motivating example is an online store. A customer places an order. The order might be gift-wrapped, might use priority shipping, might be insured, might use a coupon, or might use any combination of those. With inheritance, that's a combinatorial explosion: `GiftWrappedOrder`, `PriorityOrder`, `GiftWrappedPriorityOrder`, `InsuredGiftWrappedPriorityOrder`, and so on, growing as 2^n in the number of options. With the Decorator pattern, each option is a small wrapper class, and you stack them at runtime by wrapping each order inside the next: `Insurance(PriorityShipping(GiftWrap(order)))`. Three wrapper classes give you eight possible combinations; ten wrapper classes give you a thousand and twenty-four. The pattern scales by composition, not by inheritance.

In this lab you will work with an order-and-add-ons system. The `Order` interface is defined for you. So is the `BaseOrder` class that represents the cart, and the `OrderDecorator` base class that handles the wrapping mechanics. Your job is to implement three concrete decorators: `GiftWrap` (flat \$5), `PriorityShipping` (flat \$10), and `Insurance` (5% of whatever is being wrapped). After that you will stack them and watch the costs compose.

The reflection at the end of the lab is, like Lab 5-1, where the real intellectual content lives. The pattern is small; the design decisions it embodies are larger than the code. Composition over inheritance, the Open/Closed Principle, the question of *order-of-operations* (does insurance cover shipping?), and the relationship to Python's `@decorator` syntax (which is something different) all come up in the reflection.

**This lab is hands-on.** You write the code yourself; no AI assistance is needed or expected.

---

## Learning Objectives

By the end of this lab, you will be able to:

1. Recognize the Decorator pattern when you see it and explain what problem it solves.
2. Implement a decorator class in Python that wraps another object of the same interface, delegating most calls and modifying a few.
3. Stack multiple decorators on a single base object and predict the result.
4. Articulate the "composition over inheritance" principle and identify a place in code where it is, or is not, being followed.
5. Distinguish the OOP Decorator pattern (this lab) from Python's `@decorator` function-syntax (a different thing with a confusing shared name).

---

## Part 1: Set Up the Workspace

### Step 1.1: Confirm you have Python installed

In a terminal:

```bash
python3 --version
```

Python 3.8 or later is fine. The lab uses no f-string edge cases, structural pattern matching, or other newer-only features.

### Step 1.2: Create the lab directory

```bash
mkdir -p ~/decorator-lab
cd ~/decorator-lab
```

### Step 1.3: Create the starter file

Create a file called `starter.py` and paste in the following code exactly. Do not modify anything yet; in Part 2 you will read it before changing anything.

```python
from abc import ABC, abstractmethod

# ----- Component -----
class Order(ABC):
    @abstractmethod
    def cost(self) -> float: ...
    @abstractmethod
    def description(self) -> str: ...

# ----- Concrete Component -----
class BaseOrder(Order):
    def __init__(self, items):
        """
        items: list of (name, price) tuples
        """
        self.items = items

    def cost(self) -> float:
        return sum(price for _, price in self.items)

    def description(self) -> str:
        names = ", ".join(name for name, _ in self.items)
        return f"BaseOrder({names})"

# ----- Decorator Base -----
class OrderDecorator(Order):
    def __init__(self, inner: Order):
        self.inner = inner

    def cost(self) -> float:
        return self.inner.cost()

    def description(self) -> str:
        return self.inner.description()

# ----- Concrete Decorators (TODOs) -----
class GiftWrap(OrderDecorator):
    # TODO(1): add a flat $5 and append " + GiftWrap" to description
    def cost(self) -> float:
        pass
    def description(self) -> str:
        pass

class PriorityShipping(OrderDecorator):
    # TODO(2): add a flat $10 and append " + PriorityShipping"
    def cost(self) -> float:
        pass
    def description(self) -> str:
        pass

class Insurance(OrderDecorator):
    # TODO(3): add 5% of the wrapped order's current cost
    # and append " + Insurance(5%)"
    def cost(self) -> float:
        pass
    def description(self) -> str:
        pass

# ----- Demo / Quick Tests -----
if __name__ == "__main__":
    cart = [("Tee", 20.0), ("Mug", 12.5)]  # subtotal = 32.5

    base = BaseOrder(cart)
    print(base.description(), "=>", base.cost())           # expect BaseOrder(Tee, Mug) => 32.5

    # Single decorator
    wrapped = GiftWrap(base)
    print(wrapped.description(), "=>", wrapped.cost())     # expect +$5

    # Chain multiple decorators
    fast_and_safe = Insurance(PriorityShipping(GiftWrap(base)))
    print(fast_and_safe.description(), "=>", fast_and_safe.cost())
    # Expected breakdown: 32.5 + 5 (wrap) + 10 (priority) = 47.5, then +5% insurance on 47.5 = 49.875
    # So expect 49.875
```

Save the file.

### Step 1.4: Run the starter to see the baseline

```bash
python3 starter.py
```

Output:

```
BaseOrder(Tee, Mug) => 32.5
None => None
None => None
```

Read this carefully. The first line works correctly: the `BaseOrder` has no TODOs, so its `description()` returns the expected string and its `cost()` returns 32.5.

The next two lines say `None => None` because the decorator methods `cost()` and `description()` have bodies of just `pass`. In Python, a function whose body is `pass` (or any function that doesn't explicitly `return`) returns `None` implicitly. So `wrapped.description()` returns `None`, `wrapped.cost()` returns `None`, and the `print` call dutifully prints `None => None`.

This is the expected "before" state. The program runs without crashing, but the decorator methods produce nothing. Your job in Part 3 is to make those methods actually do something. After all three TODOs are done, the second line should show the cost with gift wrap (+$5) and the third should show the full chained total (49.875).

### Step 1.5: Create a lab notebook

Create a file `notebook.md` in the workspace. You will record your analyses and observations as you go:

```markdown
# Decorator Pattern Lab Notebook

## Part 2: Reading the starter

## Part 3: The implementation

## Part 4: Verification

## Part 5: Stretch (Coupon)

## Part 6: Reflection
```

---

## Part 2: Read the Starter Before You Change It

The Decorator pattern is short to write but has more moving parts than the Factory pattern from Lab 5-1. Make sure you understand the structure before you start typing. Spend at least 15 minutes on this section.

### Question 2.1: The three roles

The starter defines four classes that play three distinct roles:

| Class | Role |
|-------|------|
| `Order` | ? |
| `BaseOrder` | ? |
| `OrderDecorator` | ? |
| `GiftWrap`, `PriorityShipping`, `Insurance` | ? |

Fill in the roles from memory or from the source. Then check against this list:

- `Order` is the **Component interface**: a contract that says "anything that calls itself an order has `cost()` and `description()` methods."
- `BaseOrder` is the **Concrete Component**: the actual thing being decorated. Without any wrappers, this is what an order is.
- `OrderDecorator` is the **Decorator base class**: a wrapper that itself implements `Order`, and that holds an inner `Order` it delegates to.
- `GiftWrap`, `PriorityShipping`, `Insurance` are the **Concrete Decorators**: specific add-ons that override some methods to add behaviour while still delegating to the inner order.

Answer in your notebook:

1. Why does `OrderDecorator` itself inherit from `Order`? What does the codebase gain from that choice?
2. Why is `OrderDecorator` declared but its `cost()` and `description()` just delegate (return `self.inner.cost()` and `self.inner.description()`)? If you never instantiated `OrderDecorator` directly, could you skip these methods entirely?

### Question 2.2: Composition, not inheritance

Look at `OrderDecorator.__init__`:

```python
def __init__(self, inner: Order):
    self.inner = inner
```

The decorator does not *inherit* from the thing it decorates. It *contains* a reference to it. This is the central design decision of the pattern, and it deserves a careful answer:

1. Suppose you tried to do this with inheritance instead. `GiftWrap` would `extends BaseOrder`, `PriorityShipping` would `extends BaseOrder`, `Insurance` would `extends BaseOrder`. How would you express "a gift-wrapped order with priority shipping" in that scheme? Could you?
2. The decorator pattern stores the inner order as a *plain attribute* (`self.inner`). What is the type of `self.inner` *at compile time*? What might it be at runtime? (Hint: it could be a `BaseOrder`. It could also be another decorator.)
3. The recursive nature of decorator chains is the source of their power. `Insurance(PriorityShipping(GiftWrap(base)))` is a `Insurance` whose `.inner` is a `PriorityShipping` whose `.inner` is a `GiftWrap` whose `.inner` is the `BaseOrder`. When you call `.cost()` on the outermost, what happens?

### Question 2.3: The `Order` abstract base class

The starter uses `from abc import ABC, abstractmethod` and declares `Order(ABC)` with two `@abstractmethod` methods. Answer:

1. What happens if you try to write `o = Order()` somewhere in the program? Why?
2. The method bodies use `...` (the Ellipsis literal). Could you have written `pass` instead? Could you have written `raise NotImplementedError`? Which would you prefer in your own code?
3. The decorator base class `OrderDecorator` *also* inherits from `Order(ABC)`. But `OrderDecorator` provides concrete implementations of both methods (delegate to `self.inner`). Does that mean `OrderDecorator` is *not* abstract? Could you write `od = OrderDecorator(base)` and have it work?

### Question 2.4: The TODOs

Look at the three TODO classes (`GiftWrap`, `PriorityShipping`, `Insurance`). Each has `cost()` and `description()` methods whose bodies are `pass`.

1. The first two TODOs (`GiftWrap`, `PriorityShipping`) ask you to add a *flat* amount. The third (`Insurance`) asks you to add a *percentage*. What is the practical difference for the math when you stack decorators?
2. Specifically: if you wrap a $100 order in `Insurance` and then in `PriorityShipping`, you get `($100 * 1.05) + $10 = $115`. If you wrap it in `PriorityShipping` and then in `Insurance`, you get `($100 + $10) * 1.05 = $115.50`. The order of wrapping changes the answer by 50 cents. Is that a bug or a feature? (The lab demo wraps `Insurance` outermost, so insurance covers the shipping. That is a deliberate business choice. The reflection at the end revisits this.)
3. Each `description()` method *appends* text rather than replacing it. Why? What would happen if `GiftWrap.description()` returned `"GiftWrap"` instead of `self.inner.description() + " + GiftWrap"`?

### Reference: Things you should have noticed

After you write your own answers, check against this list.

**Three roles (Q2.1):** `OrderDecorator` inherits from `Order` so the rest of the program can treat a decorated order *exactly* like an undecorated one. A function that accepts an `Order` will accept a `BaseOrder` or a `GiftWrap(BaseOrder)` interchangeably. That is what gives the pattern its substitutability. You could technically skip the delegating methods in `OrderDecorator` and put them in each concrete decorator, but the base class is convenient because most concrete decorators only override one method and inherit the delegation for the rest.

**Composition (Q2.2):** With inheritance, "gift wrap + priority" requires a class `GiftWrappedPriorityOrder` (or multiple inheritance, which has its own complications). With composition, you express it at construction time: `PriorityShipping(GiftWrap(base))`. `self.inner`'s type at runtime can be any `Order`: a `BaseOrder`, another decorator, anything that follows the contract. The recursive call structure means `outer.cost()` delegates to `inner.cost()`, which delegates further, all the way down to `BaseOrder.cost()`, which actually does the sum. Each layer adds its own contribution on the way back up.

**ABC (Q2.3):** Instantiating an `ABC` with unimplemented abstract methods raises `TypeError: Can't instantiate abstract class Order with abstract methods cost, description`. You could write `pass` or `raise NotImplementedError` instead of `...`, but `...` is the modern idiom and matches type stubs. `OrderDecorator` provides concrete implementations of both abstract methods (delegation counts as a concrete implementation), so it is no longer abstract; you *could* instantiate it directly. There would be no good reason to, but Python wouldn't stop you. This is different from Java, where you would typically mark the decorator base class `abstract` even though it has concrete methods, to communicate intent.

**TODOs (Q2.4):** Flat decorators add a constant; percentage decorators multiply. Stacking flat decorators is commutative (order doesn't matter); stacking percentage decorators on top of flat ones is not. Inner-to-outer order is the actual mathematical order: `Insurance(PriorityShipping(base))` means "first compute PriorityShipping's cost, then apply insurance." For descriptions, the *appending* pattern means each decorator extends the previous description rather than replacing it, so the final string reads like a recipe of what was applied.

---

## Part 3: Implement the Three Decorators

You will implement three TODOs. They are short, and the second is a near-exact copy of the first. Run the program after each one to confirm progress.

Make a copy of the starter so you can compare:

```bash
cp starter.py work.py
```

Edit `work.py` from now on; leave `starter.py` as a reference.

### Step 3.1: TODO 1 - Implement `GiftWrap`

Find the `GiftWrap` class. Replace both method bodies:

```python
class GiftWrap(OrderDecorator):
    def cost(self) -> float:
        return self.inner.cost() + 5.0

    def description(self) -> str:
        return self.inner.description() + " + GiftWrap"
```

Two design notes worth pausing on:

1. **`self.inner.cost()`, not `self.cost()`.** Calling `self.cost()` from inside `cost()` is infinite recursion. The decorator is supposed to call the *inner* order's cost, then add its own contribution.

2. **String concatenation, not formatting.** `self.inner.description() + " + GiftWrap"` is the simplest possible thing. You could use an f-string (`f"{self.inner.description()} + GiftWrap"`) and it would work identically. Either is fine.

Run the program:

```bash
python3 work.py
```

Output should now show:

```
BaseOrder(Tee, Mug) => 32.5
BaseOrder(Tee, Mug) + GiftWrap => 37.5
None => None
```

The second line is now correct: 32.5 + 5 = 37.5. The third line still says `None` because TODOs 2 and 3 are not done yet.

### Step 3.2: TODO 2 - Implement `PriorityShipping`

Find the `PriorityShipping` class. Replace both method bodies:

```python
class PriorityShipping(OrderDecorator):
    def cost(self) -> float:
        return self.inner.cost() + 10.0

    def description(self) -> str:
        return self.inner.description() + " + PriorityShipping"
```

This is identical to TODO 1 except for the amount and the label. There's nothing new to learn here; the point is that *adding a new add-on* is now a five-line operation, which is the Decorator pattern's whole pitch.

Run again. The third line will still say `None` because TODO 3 wraps `Insurance` outside `PriorityShipping`, and `Insurance` is still not implemented.

### Step 3.3: TODO 3 - Implement `Insurance`

Find the `Insurance` class. Replace both method bodies:

```python
class Insurance(OrderDecorator):
    def cost(self) -> float:
        return self.inner.cost() * 1.05

    def description(self) -> str:
        return self.inner.description() + " + Insurance(5%)"
```

This one is different from the first two: it *multiplies* rather than *adds*. The line `self.inner.cost() * 1.05` is shorthand for "take the current cost and add 5% of it" (the same as `cost + cost * 0.05`).

Notice the design implication: this multiplication happens on whatever the inner cost happens to be at the moment Insurance is applied. If Insurance wraps a `PriorityShipping(GiftWrap(base))`, then the 5% is applied to the cost *including* gift wrap and priority shipping. That is: insurance covers the full order, including its add-ons. The math is `(32.5 + 5 + 10) * 1.05 = 47.5 * 1.05 = 49.875`.

That is a *deliberate* business choice. The lab assumes a real online store would want insurance to cover the full bill, including extras. If you wanted insurance to cover only the items (not the shipping), you would wrap things in a different order. Reflection question 5 returns to this.

### Step 3.4: Run the full demo

```bash
python3 work.py
```

Output should be:

```
BaseOrder(Tee, Mug) => 32.5
BaseOrder(Tee, Mug) + GiftWrap => 37.5
BaseOrder(Tee, Mug) + GiftWrap + PriorityShipping + Insurance(5%) => 49.875
```

Three lines, all correct. The Decorator pattern in three classes.

---

## Part 4: Verify Against the Expected Output

Compare your output to:

```
BaseOrder(Tee, Mug) => 32.5
BaseOrder(Tee, Mug) + GiftWrap => 37.5
BaseOrder(Tee, Mug) + GiftWrap + PriorityShipping + Insurance(5%) => 49.875
```

### Step-by-step trace of the chained order

| Step | Operation | Cost so far | Description so far |
|------|-----------|-------------|--------------------|
| 1 | `BaseOrder([Tee=20, Mug=12.5])` | 32.5 | `BaseOrder(Tee, Mug)` |
| 2 | `GiftWrap(...)` | 32.5 + 5 = 37.5 | `... + GiftWrap` |
| 3 | `PriorityShipping(...)` | 37.5 + 10 = 47.5 | `... + PriorityShipping` |
| 4 | `Insurance(...)` | 47.5 * 1.05 = 49.875 | `... + Insurance(5%)` |

Each line of the table represents one layer of wrapping. Notice that the cost computation happens *outward*: the innermost layer (`BaseOrder`) computes first, then `GiftWrap` adds its $5, then `PriorityShipping` adds its $10, then `Insurance` applies its 5% to everything below it.

### If your output differs

1. **You see `None` somewhere.** A TODO method has `pass` in its body instead of a proper `return` statement. Check each decorator class.

2. **You see `RecursionError: maximum recursion depth exceeded`.** You wrote `self.cost()` instead of `self.inner.cost()` inside a decorator's `cost` method (or similarly for `description`). The decorator calls itself instead of delegating, and recursion never reaches `BaseOrder`. Re-read Step 3.1.

3. **The chained line shows `49.875000000000004` or similar float artifact.** Possible but rare. The standard IEEE 754 representation of `47.5 * 1.05` is exactly 49.875 in Python's default print, but very close arithmetic can produce trailing-9 noise. If you see it, the math is still right; the printout would be cleaned up in production with `round(cost, 2)`.

4. **Cost is 49.875 but description is wrong** (missing parts, in the wrong order, or duplicated). Each decorator's `description()` should call `self.inner.description()` and *append* to it. If you return just the label (`"+ GiftWrap"` etc.), you lose the inner description. If you wrote `self.description()` instead of `self.inner.description()`, the program would have crashed before this point.

5. **The cost is 47.5 instead of 49.875.** Your `Insurance.cost()` adds 5% wrong, or maybe adds a flat amount. Re-read Step 3.3. The math is `self.inner.cost() * 1.05`, not `self.inner.cost() + 5`.

6. **The cost is something like 51.125 instead of 49.875.** You probably wrote `self.inner.cost() + self.inner.cost() * 0.05` (which is mathematically identical to `* 1.05`) but then added an extra `+ 0.05` somewhere by accident, or you wrote `* 1.5` (50%) instead of `* 1.05` (5%).

---

## Part 5: Stretch - Add a `Coupon` Decorator

Predict in your notebook before you code:

- How many existing methods or classes will you need to modify?
- How many new lines of code will you write?
- Where in the chain does it make sense to apply a coupon, before or after insurance?

Then add a `Coupon` decorator that subtracts a fixed amount, but never lets the total go below zero.

### Step 5.1: Add the `Coupon` class

Add after the `Insurance` class:

```python
class Coupon(OrderDecorator):
    """Subtract a fixed amount; never go below $0."""
    def __init__(self, inner: Order, amount_off: float):
        super().__init__(inner)
        self.amount_off = max(0.0, amount_off)

    def cost(self) -> float:
        return max(self.inner.cost() - self.amount_off, 0.0)

    def description(self) -> str:
        return self.inner.description() + f" + Coupon(${self.amount_off:.2f})"
```

Three things worth noticing:

1. **The constructor takes a second argument.** `OrderDecorator.__init__` takes one argument (`inner`). `Coupon` overrides `__init__` to take *two*: the inner order and the amount off. It uses `super().__init__(inner)` to set `self.inner` the normal way, then sets `self.amount_off` itself.

2. **The `max(0.0, amount_off)` guards against negative coupons.** A user who passes `-10` should not get an extra $10 added to their bill. Defensive code in the constructor catches this once, instead of every time `cost()` is called.

3. **The `max(..., 0.0)` in `cost()` guards against the coupon being larger than the order.** A $50 coupon on a $30 order should result in $0, not -$20. The store does not pay the customer to take the items.

### Step 5.2: Add a usage example

Append to the `__main__` block:

```python
    discounted = Coupon(fast_and_safe, 5.0)
    print(discounted.description(), "=>", round(discounted.cost(), 2))
    # Expected: 49.875 - 5 = 44.875 -> 44.88 (rounded)
```

The `round(cost, 2)` is what production currency code looks like; most retail systems show money to two decimal places, not the full float.

Run:

```bash
python3 work.py
```

Output should now include a fourth line:

```
BaseOrder(Tee, Mug) => 32.5
BaseOrder(Tee, Mug) + GiftWrap => 37.5
BaseOrder(Tee, Mug) + GiftWrap + PriorityShipping + Insurance(5%) => 49.875
BaseOrder(Tee, Mug) + GiftWrap + PriorityShipping + Insurance(5%) + Coupon($5.00) => 44.88
```

### Step 5.3: Count the cost

The full cost of adding a new add-on type was:

| Where | Lines |
|-------|-------|
| New `Coupon` class (constructor + cost + description) | 9 |
| New call in `__main__` | 2 |
| **Total** | **11** |

And critically: no existing decorator, no `BaseOrder`, no `OrderDecorator`, no `Order` interface needed to change. The Open/Closed Principle in practice.

---

## Part 6: Reflection

Answer in your notebook. These are open-ended; spend at least 15 minutes.

1. **Composition over inheritance.** This lab has zero classes with multiple-inheritance, even though the domain ("orders that are both gift-wrapped *and* express-shipped *and* insured") looks like it might want it. Why does composition win here? Sketch what the inheritance-based design would look like with three add-ons. How many classes does it need? With five add-ons? With ten?

2. **The order of wrapping matters.** The lab wraps `Insurance` outermost so that insurance covers shipping. A different store might wrap `Coupon` outermost so the discount applies to the full bill including taxes and shipping. Yet another might wrap `Coupon` innermost so the discount applies only to the items. For your own design choice, write out what the chain `Coupon(Insurance(PriorityShipping(GiftWrap(base))), 5)` computes, and what `Insurance(Coupon(PriorityShipping(GiftWrap(base)), 5))` computes. Are these the same?

3. **The "+" in `description()`.** Each decorator appends ` + DecoratorName` to the description. The final description reads like a build recipe: `BaseOrder(...) + GiftWrap + PriorityShipping + Insurance(5%)`. What if a store wanted this in a different format, like a JSON object or a list? Would you have to change every decorator? Is that a weakness of the pattern as written?

4. **What if the decorator wants to refuse?** Imagine a hypothetical `RestrictedShipping` decorator that refuses to ship hazardous items. It needs to inspect the inner order to decide. Can a decorator in this pattern do that? What information does it have access to? (Hint: it has `self.inner`, but that's just an `Order`; it can't ask the inner order what *items* are in it, only the total cost and description.)

5. **Python's `@decorator` syntax.** Python has a syntactic feature called "decorators" written with `@`, used like `@staticmethod` or `@property` above a function or method. That is *not* the same as the OOP Decorator pattern in this lab. What is the relationship between the two? When you see `@some_decorator`, what is happening, and how does it differ from `SomeDecorator(thing)`? (The next reference section unpacks this.)

6. **What is missing?** This is a teaching example, not production code. Three things you would want before deploying it. Name them. (Hints: configuration, currency arithmetic, idempotence of decorators.)

---

## Reference: The Decorator Pattern in One Picture

```
          +----------+   programs to   +----------------+
          |  Client  | --------------> |   <interface>  |
          +----------+                 |     Order      |
                                       +----------------+
                                       | cost()         |
                                       | description()  |
                                       +----------------+
                                            ^      ^
                                            |      |
                  +-------------------------+      +------------------------+
                  |                                                         |
        +-------------------+                            +-----------------------+
        |   BaseOrder       |                            |   OrderDecorator      |
        |   (the cart)      |                            |   inner: Order        |
        +-------------------+                            +-----------------------+
                                                                  ^
                                              +-------------------+----------------+
                                              |                   |                |
                                       +-----------+      +---------------+   +-----------+
                                       | GiftWrap  |      | PriorityShip. |   | Insurance |
                                       +-----------+      +---------------+   +-----------+
```

The decorator class hierarchy parallels the concrete component hierarchy: both implement `Order`. But where `BaseOrder` is a leaf (it has no `inner`), each decorator holds a reference to an `Order` and delegates to it. That `Order` can be another decorator, which delegates to *its* inner, and so on, until you reach a `BaseOrder` at the bottom of the chain.

---

## Reference: The OOP Decorator Pattern vs Python `@decorator` Syntax

This is one of the most confusing naming overlaps in Python and worth straightening out explicitly.

**The OOP Decorator pattern (this lab):**

```python
order = Insurance(PriorityShipping(GiftWrap(base)))
order.cost()  # 49.875
```

A wrapper *object* contains an inner object and adds behaviour to its methods. Each wrapper is a *class*. Stacking is by passing one object into another's constructor.

**Python `@decorator` syntax:**

```python
@cached
@log_calls
def fetch_user(id):
    ...
```

A wrapper *function* (or class) modifies a function or method. The `@` is syntactic sugar: `@cached def f(): ...` is exactly equivalent to `def f(): ...; f = cached(f)`. Each decorator is a *function* (usually) that takes a function and returns a function.

The two share the name "decorator" because they share the same underlying intuition: wrap an existing thing to add behaviour without modifying it. But the *mechanism* is different:

| | OOP Decorator (this lab) | Python `@decorator` |
|--|--|--|
| What gets wrapped | An object | A function or class |
| What's the wrapper | A class instance | A function (usually) |
| When is wrapping applied | Runtime | At definition time |
| How is wrapping expressed | `Insurance(order)` | `@cached` above the def |
| Can you stack multiples? | Yes | Yes |
| Can you unstack at runtime? | Yes (re-construct the chain) | No (it's baked in at definition) |
| Common use cases | Add-ons, middleware, optional features | Caching, logging, access control, type-checking |

If you're new to both, the simple rule: **OOP decorator pattern is for varying *what an object does*; Python `@decorator` is for varying *what a function does*.** They solve different problems with similar-feeling syntax.

---

## Reference: Composition vs Inheritance

The Decorator pattern is one of the clearest demonstrations of the "favour composition over inheritance" guideline. The full hierarchy of approaches:

| Approach | What it looks like | When it works well |
|----------|-------------------|--------------------|
| **Pure inheritance** | `GiftWrappedPriorityInsuredOrder extends BaseOrder` | One fixed combination, never any others. |
| **Inheritance with mixins** | `class FancyOrder(BaseOrder, GiftWrappable, Priority, Insurable)` | Small fixed set of orthogonal traits. |
| **Decorator pattern** | `Insurance(PriorityShipping(GiftWrap(base)))` | Many independent optional features that combine in any combination. |
| **Strategy pattern** | `order.pricing_policy = GiftWrappedPricing()` | One varying behaviour at a time; not stacking. |
| **Configuration / data** | `order.add_ons = ["gift_wrap", "priority", "insurance"]` | Add-ons are pure data with no logic. |

The decorator pattern is what you reach for when the variation is **composable and runtime-determined**: composable because different customers want different combinations, runtime-determined because the customer picks the combination at checkout, not at compile time.

---

## Reference: When the Decorator Pattern Is the Wrong Tool

Like every pattern, this one is over-applied. Warning signs:

1. **There is only one decorator, and only ever will be.** A single-decorator hierarchy is a class doing extra work. Just inline the behaviour into `BaseOrder`.

2. **Decorators need to know about each other.** If `Insurance` has to behave differently when stacked under `PriorityShipping`, the pattern is breaking down. The whole point of the pattern is that decorators are independent of each other; if yours aren't, you may need a different abstraction (like a pipeline with explicit stages, or a builder).

3. **Decorators need to access private state of the inner.** The inner is just an `Order` interface; decorators only see `cost()` and `description()`. If you find yourself wanting to inspect the inner's `items` list, the abstraction is too narrow, and you either need a wider interface or a different pattern.

4. **The chain is built once and never varies.** If every customer in your system has the exact same combination of add-ons, you don't need runtime composition; you can just write one class.

---

## Troubleshooting

**`RecursionError: maximum recursion depth exceeded`.**
A decorator method calls itself (`self.cost()` or `self.description()`) instead of delegating to the inner (`self.inner.cost()` / `self.inner.description()`). Each call goes back to the same method on the same object, forever.

**`AttributeError: 'GiftWrap' object has no attribute 'inner'`.**
You wrote a constructor on `GiftWrap` (or another decorator) that didn't call `super().__init__(inner)`. The base class `OrderDecorator.__init__` sets `self.inner`, and if you override the constructor without calling super, that assignment never happens.

**`TypeError: Can't instantiate abstract class GiftWrap with abstract methods cost, description`.**
Your TODO methods are missing or named wrong. Python sees that `GiftWrap` inherits `cost` and `description` as abstract from `Order` (via `OrderDecorator`'s ABC ancestry), and if you don't provide concrete implementations with those exact names, Python refuses to construct the object.

**`None => None` in the output.**
A decorator's method body is still `pass` and returns `None`. Replace `pass` with the proper `return` statement.

**The cost looks right but `description()` shows nothing or just the inner part.**
Your `description()` method probably doesn't append the decorator's own label. Check that each `description()` returns `self.inner.description() + " + SomeLabel"`.

**A float comes out as `49.875000000000004`.**
This is normal IEEE 754 floating-point behaviour. Currency code in production uses `decimal.Decimal` to avoid this. For this lab, `round(cost, 2)` (as shown in the `Coupon` example) is enough.

---

## Further Reading

- **Design Patterns: Elements of Reusable Object-Oriented Software** (Gamma, Helm, Johnson, Vlissides, 1994). The original Gang of Four book. The Decorator chapter is short, with the canonical example of a window-with-scrollbars-and-borders.
- **Head First Design Patterns, 2nd edition** (Freeman et al.). The Decorator chapter uses a coffee-shop example (a coffee, plus milk, plus mocha, plus whip) that is almost identical to this lab. Friendly introduction.
- **Refactoring Guru: Decorator** at <https://refactoring.guru/design-patterns/decorator>. Free online walkthrough with diagrams and code in many languages.
- **PEP 318: Decorators for Functions and Methods** at <https://peps.python.org/pep-0318/>. The original proposal for Python's `@decorator` syntax. Useful for understanding the *Python* sense of "decorator," which is related to but distinct from this lab's sense.
- **Fluent Python, 2nd edition** (Luciano Ramalho). Chapter 9, "Decorators and Closures," covers Python's function-decorator system in depth. The class-based decorator pattern from this lab appears in the chapter on design patterns.
