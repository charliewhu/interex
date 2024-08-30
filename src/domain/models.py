from dataclasses import dataclass


@dataclass
class User:
    id: int  # unique identifier for each user
    cash_balance: float = 10000.0  # assuming each user starts with some cash balance

    def __repr__(self):
        return f"User({self.id})"


@dataclass(frozen=True)
class Order:
    id: int
    user_id: int
    price: int
    quantity: int


class OrderBook:
    def __init__(self) -> None:
        self.orders: set[Order] = set()

    def place_order(self, order: Order):
        self.orders.add(order)
        return order

    def get_order(self, id: int):
        return next(o for o in self.orders if o.id == id)
