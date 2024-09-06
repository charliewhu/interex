import random
import string
import pytest
from fastapi.testclient import TestClient
from api.app import create_app
from domain.models import OrderBook


@pytest.fixture
def order_book():
    yield OrderBook()


@pytest.fixture(scope="function")
def app(order_book):
    yield create_app(order_book)


@pytest.fixture(scope="function")
def client(app):
    return TestClient(
        app,
        base_url=f'http://{''.join(random.choice(string.ascii_letters) for _ in range(10))}',
    )
