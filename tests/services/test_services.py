from service_layer import services


def test_add_buy_limit(order_book):
    """Check if the order was placed correctly"""

    services.order(order_book, 90, 1)
    assert len(order_book._bids) == 1
    assert order_book._bids[90]


def test_market_order(order_book):
    """
    A buy market order should be excecuted
    if there is a sell limit in the order book
    """
    limit_price = 110
    # limit order in book
    services.order(order_book, limit_price, -2)

    # hit market
    services.order(order_book, None, 1)

    # limit order should be taken with 1 offer remaining
    assert len(order_book._offers[limit_price].orders) == 1
    assert order_book._offers[limit_price].quantity == -1
