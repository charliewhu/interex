import typing as t

from domain import models


class IRepository[T](t.Protocol):
    def add(self, item: T) -> T: ...

    def get(self, id) -> T: ...

    def list(self) -> list[T]: ...


class InMemoryRepository:
    def __init__(self, orders: list[models.Order]) -> None:
        self._orders = set(orders)

    def add(self, item: models.Order):
        return item
