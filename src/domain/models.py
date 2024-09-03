from collections import defaultdict
import typing as t
from dataclasses import dataclass, field
import uuid

from domain import exceptions


@dataclass
class User:
    id: int  # unique identifier for each user
    cash_balance: float = 10000.0  # assuming each user starts with some cash balance

    def __repr__(self):
        return f"User({self.id})"


@dataclass
class Order:
    user_id: str
    quantity: int
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    price: t.Optional[int] = None


class OrderBook:
    def __init__(self, price: int = 100) -> None:
        self.orders: dict[int, list[Order]] = defaultdict(list)
        self.last_price = price

    def place_order(self, order: Order):
        if order.quantity == 0:
            raise exceptions.InvalidOrder

        if order.price is not None:  # limit orders
            p = order.price
            # cant add limit bid/offer above/below the last market price
            invalid_long = order.price > self.last_price and order.quantity > 0
            invalid_short = order.price < self.last_price and order.quantity < 0

            # if there are resting bids then we cant add limit offers at the last traded price
            # as this is the equivalent of a market order
            invalid_last_price_long = (
                order.price == self.last_price
                and order.quantity > 0
                and sum(order.quantity for order in self.orders[self.last_price]) < 0
            )
            invalid_last_price_short = (
                order.price == self.last_price
                and order.quantity < 0
                and sum(order.quantity for order in self.orders[self.last_price]) > 0
            )

            if (
                invalid_long
                or invalid_short
                or invalid_last_price_long
                or invalid_last_price_short
            ):
                raise exceptions.InvalidOrder

            self.orders[p].append(order)

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

        while abs(quantity) > 0:
            self.last_price = self.min_max(
                [
                    key
                    for key, value in self.orders.items()
                    if quantity * key > quantity * self.last_price and len(value) > 0
                    # for market longs we want closest price above last price
                    # for shorts flip the sign and get prices below
                ],
                quantity,
            )  # nearest limit price that has Orders

            # quantity available at nearest price
            available_quantity = sum(o.quantity for o in self.orders[self.last_price])

            # if the available quantity at the price is less than the market order
            # clear all orders at that price
            if abs(available_quantity) <= abs(quantity):
                del self.orders[self.last_price]
                quantity += available_quantity

            else:
                # loop through Orders at price and decrement their quantity
                while abs(quantity) > 0:
                    try:
                        available_in_order = self.orders[self.last_price][0].quantity
                        if abs(available_in_order) <= abs(quantity):
                            del self.orders[self.last_price][0]
                            quantity += available_in_order
                        else:
                            self.orders[self.last_price][0].quantity += quantity
                            quantity = 0

                    except IndexError:
                        break

    def get_prices(self, quantity: int = 6) -> list[dict[str, int]]:
        """Return 'quantity' of prices surrounding the current market price

        Args:
            quantity (_type_): the number of prices required

        Returns:
            _type_: list of prices with orders
        """
        min = self.last_price - int(quantity / 2)
        max = self.last_price + int(quantity / 2)
        prices = {price: self.orders[price] for price in range(min, max, 1)}

        result = []
        for price, orders in prices.items():
            bids_sum = 0
            offers_sum = 0

            for order in orders:
                quantity = order.quantity
                if quantity > 0:
                    bids_sum += quantity
                else:
                    offers_sum -= (
                        quantity  # Convert negative quantity to positive by subtracting
                    )

            result.append({"price": price, "bids": bids_sum, "offers": offers_sum})

            # Sort the result by 'price' in descending order
            result.sort(key=lambda x: x["price"], reverse=True)

        return result

    @staticmethod
    def min_max(iterable: t.Iterable, find_max: int):
        """
        Return the max if find_max is negative, minimum otherwise
        """
        return max(iterable) if find_max < 0 else min(iterable)
