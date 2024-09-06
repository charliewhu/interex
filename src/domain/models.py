import typing as t
import uuid
from collections import defaultdict, deque
from attrs import define, field, Factory


from . import exceptions


# @define(kw_only=True, slots=True)
# class User:
#     id: int  # unique identifier for each user
#     cash_balance: float = 10000.0  # assuming each user starts with some cash balance

#     def __repr__(self):
#         return f"User({self.id})"


@define(kw_only=True, slots=True)
class Order:
    id: str = Factory(lambda: str(uuid.uuid4()))
    quantity: int
    price: t.Optional[int] = None


@define(kw_only=True, slots=True)
class Price:
    orders: deque[Order] = field()
    quantity: int = field(default=0)


class OrderBook:
    def __init__(self, price: int = 100) -> None:
        self.bids: dict[int, Price] = defaultdict(
            lambda: Price(orders=deque([]), quantity=0)
        )
        self.offers: dict[int, Price] = defaultdict(
            lambda: Price(orders=deque([]), quantity=0)
        )
        self.last_price = price

    def place_order(self, order: Order):
        if not order.quantity:
            raise exceptions.InvalidOrder

        if order.price is None:
            self._match_market_order(order)
        else:
            if (
                order.price > self.last_price
                and order.quantity > 0
                or (order.price < self.last_price and order.quantity < 0)
            ):
                raise exceptions.InvalidOrder
            elif order.quantity > 0:
                if not self.bids[order.price]:
                    self.bids[order.price] = Price(
                        orders=deque([order]),
                        quantity=order.quantity,
                    )
                else:
                    self.bids[order.price].orders.append(order)
                    self.bids[order.price].quantity += order.quantity
            else:
                if not self.offers[order.price]:
                    self.offers[order.price] = Price(
                        orders=deque([order]),
                        quantity=order.quantity,
                    )
                else:
                    self.offers[order.price].orders.append(order)
                    self.offers[order.price].quantity += order.quantity

    def _match_market_order(self, order: Order):
        if order.quantity > 0:
            orders = self.offers
        else:
            orders = self.bids

        if all(orders[price].quantity == 0 for price in orders):
            raise exceptions.NoOrdersAvailable

        for price in sorted(orders.keys(), reverse=(order.quantity < 0)):
            print(f"{price=}")
            while abs(order.quantity) > 0 and orders[price].orders:
                # while orders exist at this price
                current_order = orders[price].orders[0]
                if abs(current_order.quantity) <= abs(order.quantity):
                    # if limit doesnt contain enough orders
                    orders[price].quantity -= current_order.quantity
                    orders[price].orders.popleft()
                else:
                    # partially take from current limit order
                    orders[price].quantity += order.quantity
                    current_order.quantity += order.quantity
                    order.quantity = 0  # market order is filled
