from domain import models


def order(
    order_book: models.OrderBook,
    price: int | None,
    quantity: int,
):
    # order_book.place_order()
    # convert from dict of list[Order]
    # to list of dicts {price, bids, offers}
    # ordered descending

    # TODO: wrap in transaction / uow
    order = models.Order(quantity=quantity, price=price)
    order_book.place_order(order)
