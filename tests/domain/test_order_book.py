import pytest
from domain import models, exceptions


def test_limit_order_placement():
    """Test placing a limit order."""
    # Create User
    user = models.User(id=1)

    # Create Order
    order = models.Order(
        id=1,
        user_id=user.id,
        quantity=1,
        price=90,
    )

    order_book = models.OrderBook()

    # Place a limit order
    placed_order = order_book.place_order(order)

    # Check if the order was placed correctly
    assert len(order_book.orders) == 1

    order = order_book.get_order(id=placed_order.id)
    assert order is not None
    assert order.price == 90
    assert order.quantity == 1


def test_buy_order_above_market():
    """
    Test placing buy order above market price
    (this should be a stop order later on)
    """
    # Create User
    user = models.User(id=1)

    # Create Order
    order = models.Order(
        id=1,
        user_id=user.id,
        quantity=1,
        price=100,
    )

    order_book = models.OrderBook(price=90)

    with pytest.raises(exceptions.InvalidOrder):
        # Place invalid order
        order_book.place_order(order)


def test_sell_order_below_market():
    """
    Test placing buy order above market price
    (this should be a stop order later on)
    """
    # Create User
    user = models.User(id=1)

    # Create Order
    order = models.Order(
        id=1,
        user_id=user.id,
        quantity=-1,
        price=80,
    )

    order_book = models.OrderBook(price=90)

    with pytest.raises(exceptions.InvalidOrder):
        # Place invalid order
        order_book.place_order(order)


def test_zero_order():
    """
    Test placing buy order above market price
    (this should be a stop order later on)
    """
    # Create User
    user = models.User(id=1)

    # Create Order
    order = models.Order(
        id=1,
        user_id=user.id,
        quantity=0,
        price=80,
    )

    order_book = models.OrderBook(price=90)

    with pytest.raises(exceptions.InvalidOrder):
        # Place invalid order
        order_book.place_order(order)
