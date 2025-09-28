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
