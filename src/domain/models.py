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
        self._bids: dict[int, Price] = defaultdict(
            lambda: Price(orders=deque([]), quantity=0)
        )
        self._offers: dict[int, Price] = defaultdict(
            lambda: Price(orders=deque([]), quantity=0)
        )
        self.last_price = price
        # self.last_direction: t.Literal["buy", "sell"]

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
                if (
                    # prevent limit bids and offers at same price
                    order.price == self.last_price
                    and self._offers[order.price].quantity < 0
                ):
                    raise exceptions.InvalidOrder
                if not self._bids[order.price]:
                    self._bids[order.price] = Price(
                        orders=deque([order]),
                        quantity=order.quantity,
                    )
                else:
                    self._bids[order.price].orders.append(order)
                    self._bids[order.price].quantity += order.quantity
            else:
                if (
                    # prevent limit bids and offer at same price
                    order.price == self.last_price
                    and self._bids[order.price].quantity > 0
                ):
                    raise exceptions.InvalidOrder
                if not self._offers[order.price]:
                    self._offers[order.price] = Price(
                        orders=deque([order]),
                        quantity=order.quantity,
                    )
                else:
                    self._offers[order.price].orders.append(order)
                    self._offers[order.price].quantity += order.quantity

    def _match_market_order(self, order: Order):
        if order.quantity > 0:
            orders = self._offers
        else:
            orders = self._bids

        if all(orders[price].quantity == 0 for price in orders):
            raise exceptions.NoOrdersAvailable

        for price in sorted(orders.keys(), reverse=(order.quantity < 0)):
            while abs(order.quantity) > 0 and orders[price].orders:
                # while orders exist at this price
                current_order = orders[price].orders[0]

                if abs(current_order.quantity) <= abs(order.quantity):
                    # if limit doesnt contain enough orders
                    orders[price].quantity -= current_order.quantity
                    order.quantity += current_order.quantity
                    orders[price].orders.popleft()
                else:
                    # partially take from current limit order
                    orders[price].quantity += order.quantity
                    current_order.quantity += order.quantity
                    order.quantity = 0  # market order is filled

                self.last_price = price

    def prices(self, quantity: int = 2):
        """Return list[dict] for combined bids and offers centered around last_price"""
        min = self.last_price - quantity - 1
        max = self.last_price + quantity

        orders = [
            {
                "price": price,
                "bids": self._bids[price].quantity,
                "offers": abs(self._offers[price].quantity),
            }
            for price in range(max, min, -1)
        ]

        return orders
