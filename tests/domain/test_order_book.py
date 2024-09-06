import pytest
from domain import models, exceptions


def test_limit_order_placement():
    """Test placing a limit order."""
    # Create User

    # Create Order
    order = models.Order(
        quantity=1,
        price=90,
    )

    order_book = models.OrderBook()

    order_book.place_order(order)

    # Check if the order was placed correctly
    assert len(order_book.bids) == 1
    assert order.price is not None
    assert order_book.bids[order.price]


def test_buy_order_above_market():
    """
    Test placing buy order above market price
    (this should be a stop order later on)
    """

    # Create Order
    order = models.Order(
        quantity=1,
        price=100,
    )

    order_book = models.OrderBook(price=90)

    with pytest.raises(exceptions.InvalidOrder):
        # Place invalid order
        order_book.place_order(order)


def test_sell_order_below_market():
    # Create Order
    order = models.Order(
        quantity=-1,
        price=80,
    )

    order_book = models.OrderBook(price=90)

    with pytest.raises(exceptions.InvalidOrder):
        # Place invalid order
        order_book.place_order(order)


def test_zero_order():
    # Create Order
    order = models.Order(
        quantity=0,
        price=80,
    )

    order_book = models.OrderBook(price=90)

    with pytest.raises(exceptions.InvalidOrder):
        # Place invalid order
        order_book.place_order(order)


def test_market_order():
    """
    A buy market order should be excecuted
    if there is a sell limit in the order book
    """
    order_book = models.OrderBook()

    # Create sell limit order
    limit_order = models.Order(
        quantity=-2,
        price=110,
    )
    order_book.place_order(limit_order)

    # create market order
    market_order = models.Order(
        quantity=1,
    )

    assert limit_order.price is not None
    assert len(order_book.offers[limit_order.price].orders) == 1

    order_book.place_order(market_order)

    # limit order should be taken with 1 offer remaining
    assert len(order_book.offers[limit_order.price].orders) == 1
    assert order_book.offers[limit_order.price].quantity == -1


def test_market_order_across_prices():
    """
    A buy market order should be excecuted
    if there is a sell limit in the order book
    """
    # Create sell limit order
    first_limit_order = models.Order(
        quantity=-1,
        price=110,
    )
    order_book = models.OrderBook()
    order_book.place_order(first_limit_order)

    # Create sell limit order
    second_limit_order = models.Order(
        quantity=-1,
        price=111,
    )
    order_book.place_order(second_limit_order)

    # create buy market order
    market_order = models.Order(
        quantity=2,
    )

    assert first_limit_order.price is not None
    assert second_limit_order.price is not None

    assert order_book.offers[first_limit_order.price].quantity == -1
    assert order_book.offers[second_limit_order.price].quantity == -1

    order_book.place_order(market_order)

    # limit orders should be taken
    assert order_book.offers[first_limit_order.price].quantity == 0
    assert len(order_book.offers[first_limit_order.price].orders) == 0

    assert order_book.offers[second_limit_order.price].quantity == 0
    assert len(order_book.offers[second_limit_order.price].orders) == 0


def test_market_order_at_last_price():
    """
    A buy market order should be excecuted
    if there is a sell limit in the order book
    """
    order_book = models.OrderBook(price=100)

    # Create sell limit order
    limit_order = models.Order(
        quantity=-2,
        price=100,
    )
    order_book.place_order(limit_order)

    # create market order
    market_order = models.Order(
        quantity=1,
    )

    assert limit_order.price is not None
    assert order_book.offers[limit_order.price].quantity == -2

    order_book.place_order(market_order)

    # limit order should be taken with 1 offer remaining
    assert order_book.offers[limit_order.price].quantity == -1
    assert len(order_book.offers[limit_order.price].orders) == 1
    assert order_book.offers[limit_order.price].orders[0].quantity == -1


def test_short_market_order_across_prices():
    """
    A buy market order should be excecuted
    if there is a sell limit in the order book
    """

    # Create buy limit order
    first_limit_order = models.Order(
        quantity=1,
        price=90,
    )
    order_book = models.OrderBook()
    order_book.place_order(first_limit_order)

    # Create by limit order
    second_limit_order = models.Order(
        quantity=1,
        price=89,
    )
    order_book.place_order(second_limit_order)

    # create sell market order
    market_order = models.Order(
        quantity=-2,
    )

    assert first_limit_order.price is not None
    assert second_limit_order.price is not None

    assert order_book.bids[first_limit_order.price].quantity == 1
    assert len(order_book.bids[second_limit_order.price].orders) == 1

    order_book.place_order(market_order)

    # limit orders should be taken
    assert order_book.bids[first_limit_order.price].quantity == 0
    assert len(order_book.bids[first_limit_order.price].orders) == 0

    assert order_book.bids[second_limit_order.price].quantity == 0
    assert len(order_book.bids[second_limit_order.price].orders) == 0


def test_sell_limit_filled_if_buy_limits_exist():
    """
    If there are both sell and buy limits in the orderbook
    ensure the correct side is filled
    """
    order_book = models.OrderBook()

    # Create sell limit order
    sell_limit_order = models.Order(
        quantity=-1,
        price=110,
    )
    order_book.place_order(sell_limit_order)

    # Create buy limit order
    buy_limit_order = models.Order(
        quantity=1,
        price=90,
    )
    order_book.place_order(buy_limit_order)

    # create sell market order
    market_order = models.Order(
        quantity=-1,
    )
    order_book.place_order(market_order)

    # assert sell limit still there
    assert sell_limit_order.price is not None
    assert order_book.offers[sell_limit_order.price].orders[0].quantity == -1

    # assert buy limit is gone
    assert buy_limit_order.price is not None
    assert len(order_book.offers[buy_limit_order.price].orders) == 0


def test_market_order_no_execution_if_no_limit_orders(order_book):
    """
    Raise an exception if a market order is sent
    but no limit orders are in the orderbook
    """

    # create sell market order
    market_order = models.Order(
        quantity=-1,
    )

    with pytest.raises(exceptions.NoOrdersAvailable):
        order_book.place_order(market_order)


def test_cannot_place_bids_and_offers_at_same_price(order_book):
    buy_limit = models.Order(quantity=1, price=order_book.last_price)

    sell_limit = models.Order(quantity=1, price=order_book.last_price)

    order_book.place_order(buy_limit)

    with pytest.raises(exceptions.InvalidOrder):
        order_book.place_order(sell_limit)
