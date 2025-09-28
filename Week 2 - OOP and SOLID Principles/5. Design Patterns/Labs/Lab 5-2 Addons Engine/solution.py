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

# ----- Concrete Decorators -----
class GiftWrap(OrderDecorator):
    # Adds a flat $5
    def cost(self) -> float:
        return self.inner.cost() + 5.0

    def description(self) -> str:
        return self.inner.description() + " + GiftWrap"

class PriorityShipping(OrderDecorator):
    # Adds a flat $10
    def cost(self) -> float:
        return self.inner.cost() + 10.0

    def description(self) -> str:
        return self.inner.description() + " + PriorityShipping"

class Insurance(OrderDecorator):
    # Adds 5% of the current (already-wrapped) cost
    def cost(self) -> float:
        base = self.inner.cost()
        return base * 1.05

    def description(self) -> str:
        return self.inner.description() + " + Insurance(5%)"

# (Optional) Example extra decorator
class Coupon(OrderDecorator):
    """Subtract a fixed amount, not below $0."""
    def __init__(self, inner: Order, amount_off: float):
        super().__init__(inner)
        self.amount_off = max(0.0, amount_off)

    def cost(self) -> float:
        return max(self.inner.cost() - self.amount_off, 0.0)

    def description(self) -> str:
        return self.inner.description() + f" + Coupon(${self.amount_off:.2f})"

# ----- Demo / Quick Tests -----
if __name__ == "__main__":
    cart = [("Tee", 20.0), ("Mug", 12.5)]  # subtotal = 32.5

    base = BaseOrder(cart)
    print(base.description(), "=>", base.cost())           # BaseOrder(Tee, Mug) => 32.5

    wrapped = GiftWrap(base)
    print(wrapped.description(), "=>", wrapped.cost())     # BaseOrder(Tee, Mug) + GiftWrap => 37.5

    fast_and_safe = Insurance(PriorityShipping(GiftWrap(base)))
    print(fast_and_safe.description(), "=>", fast_and_safe.cost())
    # Expected: 32.5 + 5 + 10 = 47.5; 5% insurance => 49.875

    # Optional: apply a $5 coupon after all add-ons
    discounted = Coupon(fast_and_safe, 5.0)
    print(discounted.description(), "=>", round(discounted.cost(), 2))
    # Expected: 49.875 - 5 = 44.875 -> 44.88 (rounded)
