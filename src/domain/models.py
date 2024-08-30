from dataclasses import dataclass

from domain import exceptions


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
    def __init__(self, price: int = 100) -> None:
        self.orders: set[Order] = set()
        self.price = price

    def place_order(self, order: Order):
        invalid_long = order.price >= self.price and order.quantity > 0
        invalid_short = order.price <= self.price and order.quantity < 0
        if order.quantity == 0 or invalid_long or invalid_short:
            raise exceptions.InvalidOrder

        self.orders.add(order)
        return order

    def get_order(self, id: int):
        return next(o for o in self.orders if o.id == id)
