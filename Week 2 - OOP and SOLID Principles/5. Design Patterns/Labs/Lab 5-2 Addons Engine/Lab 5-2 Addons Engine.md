# Lab 5-2 Addons using Decorator Pattern

## Learning Objectives

- Add optional features (gift wrap, priority shipping, insurance) to an order without modifying the base class. Students will chain decorators at runtime.
- Uses the Decorator pattern (class-based, OO; not Python’s @func syntax).
- Uses Composition over inheritance for sxtending behavior without changing existing code.

## Introduction

- This lab simulates an online store checkout where customers can add optional services (gift wrap, faster shipping, insurance). 
- The goal is to add these “extras” without changing the base Order class.

### Component Interface – Order

- Defines what every order must do:
  - cost() → returns the price of the order.
  - description() → describes what’s included.
- It’s an abstract base class (like a contract): every subclass must implement these methods.

```python
class Order(ABC):
    @abstractmethod
    def cost(self) -> float: ...
    @abstractmethod
    def description(self) -> str: ...

```

### Concrete Component – BaseOrder

-Represents the basic order without add-ons.
Example: If your cart is [("Tee", 20), ("Mug", 12.5)], then:
-   cost() → 32.5
  - description() → "BaseOrder(Tee, Mug)"

```python
class BaseOrder(Order):
    def __init__(self, items):
        self.items = items  # list of (name, price) pairs

    def cost(self) -> float:
        return sum(price for _, price in self.items)

    def description(self) -> str:
        names = ", ".join(name for name, _ in self.items)
        return f"BaseOrder({names})"
```

### Decorator Base Class – OrderDecorator

- This is the wrapper for add-ons.
- It holds another order inside it (inner) and delegates calls to that order.
- By default, it just passes through the cost and description.
- Subclasses (like GiftWrap) will override these methods to add their own behavior.

```python
class OrderDecorator(Order):
    def __init__(self, inner: Order):
        self.inner = inner

    def cost(self) -> float:
        return self.inner.cost()

    def description(self) -> str:
        return self.inner.description()

```

### Empty Add-Ons (TODOs)

- These are what you will do in the lab.
- These are the concrete decorators.
- Each one will add its own cost and append text to the description.



```python
class GiftWrap(OrderDecorator):
    # TODO: add +$5 and label in description
    def cost(self): pass
    def description(self): pass

class PriorityShipping(OrderDecorator):
    # TODO: add +$10
    def cost(self): pass
    def description(self): pass

class Insurance(OrderDecorator):
    # TODO: add +5% of current total
    def cost(self): pass
    def description(self): pass

```

- The full started code is in the file `starter.py`
- Complete and test your completed code
- A solution is in the file `solution.py`

### Demo Section (__main__)

- This code tests the pattern:
- First prints a plain order (32.5).
- Then applies one decorator (GiftWrap) and shows +$5.
- Finally chains multiple decorators: gift wrap, priority shipping, and insurance (5% of subtotal so far).

```python
if __name__ == "__main__":
    cart = [("Tee", 20.0), ("Mug", 12.5)]  # subtotal = 32.5

    base = BaseOrder(cart)
    print(base.description(), "=>", base.cost())  
    # BaseOrder(Tee, Mug) => 32.5

    wrapped = GiftWrap(base)
    print(wrapped.description(), "=>", wrapped.cost())  
    # BaseOrder(Tee, Mug) + GiftWrap => 37.5

    fast_and_safe = Insurance(PriorityShipping(GiftWrap(base)))
    print(fast_and_safe.description(), "=>", fast_and_safe.cost())

```

## End  