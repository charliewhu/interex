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
        self._prices: dict[int, Price] = defaultdict(
            lambda: Price(orders=deque([]), quantity=0)
        )
        self.last_price = price

    def place_order(self, order: Order):
        if not order.quantity:
            raise exceptions.InvalidOrder

        if order.price is None:
            self._match_market_order(order)
        else:
            if (order.price > self.last_price and order.quantity > 0) or (
                order.price < self.last_price and order.quantity < 0
            ):
                raise exceptions.InvalidOrder

            # Get the existing price level (positive quantity for bids, negative for offers)
            price_level = self._prices.get(order.price)

            if price_level:
                # Prevent limit bids/offers at the same price
                if (
                    order.price == self.last_price
                    and price_level.quantity * order.quantity < 0
                ):
                    raise exceptions.InvalidOrder

                price_level.orders.append(order)
                price_level.quantity += order.quantity
            else:
                # Add new price level
                self._prices[order.price] = Price(
                    orders=deque([order]), quantity=order.quantity
                )

    def _match_market_order(self, order: Order):
        # filter self._prices for required only bids or offers
        orders = {
            price: value
            for price, value in self._prices.items()
            if value.quantity * order.quantity < 0
        }

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
                "bids": self._prices[price].quantity
                if self._prices[price].quantity > 0
                else 0,
                "offers": abs(self._prices[price].quantity)
                if self._prices[price].quantity < 0
                else 0,
            }
            for price in range(max, min, -1)
        ]

        return orders
