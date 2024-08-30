from domain.models import Order, OrderBook, User


def test_limit_order_placement():
    """Test placing a limit order."""
    # Create User
    user = User(id=1)

    # Create Order
    order = Order(
        id=1,
        user_id=user.id,
        quantity=1,
        price=100,
    )

    order_book = OrderBook()

    # Place a limit order
    placed_order = order_book.place_order(order)

    # Check if the order was placed correctly
    assert len(order_book.orders) == 1

    order = order_book.get_order(id=placed_order.id)
    assert order is not None
    assert order.price == 100
    assert order.quantity == 1
