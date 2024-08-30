from collections import defaultdict
import typing as t
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
    # price: t.Optional[int]
    quantity: int


@dataclass(frozen=True)
class LimitOrder(Order):
    price: int


class OrderBook:
    def __init__(self, price: int = 100) -> None:
        self.orders: dict[int, list[LimitOrder]] = defaultdict(list)
        self.price = price

    def place_order(self, order: Order):
        if order.quantity == 0:
            raise exceptions.InvalidOrder

        if isinstance(order, LimitOrder):
            invalid_long = order.price >= self.price and order.quantity > 0
            invalid_short = order.price <= self.price and order.quantity < 0
            if invalid_long or invalid_short:
                raise exceptions.InvalidOrder

            self.orders[order.price].append(order)
        else:  # market order
            self.match_order(order)

        return order

    def match_order(self, order: Order):
        if self.orders:
            self.matcher(order.quantity)
        else:
            raise exceptions.NoOrdersAvailable

    def matcher(
        self,
        quantity: int,
    ):
        """
        Find the nearest price above or below market and decrement
        the number of orders contained within it
        """
        quantity_unfilled = abs(quantity)
        while quantity_unfilled > 0:
            price = self.min_max(
                [
                    key
                    for key, value in self.orders.items()
                    if quantity * key > quantity * self.price and len(value) > 0
                    # for market longs we want prices above last price
                    # for shorts flip the sign and get prices below
                ],
                quantity,
            )  # nearest limit price
            available_quantity = sum(abs(o.quantity) for o in self.orders[price])
            del self.orders[price][:quantity_unfilled]
            quantity_unfilled -= available_quantity
            self.price = price

    @staticmethod
    def min_max(iterable: t.Iterable, find_max: int):
        """
        Return the max if find_max is negative, minimum otherwise
        """
        return max(iterable) if find_max < 0 else min(iterable)
