from domain import models


def add_order(
    order_book: models.OrderBook, user_id: str, price: int | None, quantity: int
):
    # order_book.place_order()
    # convert from dict of list[Order]
    # to list of dicts {price, bids, offers}
    # ordered descending

    # TODO: wrap in transaction / uow
    order = models.Order(user_id=user_id, quantity=quantity, price=price)
    order_book.place_order(order)

    prices = order_book.get_prices()

    return prices
