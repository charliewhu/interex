from fastapi.testclient import TestClient

from api.app import create_app
from domain import models


WEBSOCKET_URL = "/api/ws/orders"


def test_shows_price_levels(client):
    """
    API should return current prices on connection to WebSocket
    """
    # client = TestClient(app)

    with client.websocket_connect(WEBSOCKET_URL) as websocket:
        data = websocket.receive_json()

        expected_data = [
            {"price": 102, "bids": 0, "offers": 0},
            {"price": 101, "bids": 0, "offers": 0},
            {"price": 100, "bids": 0, "offers": 0},
            {"price": 99, "bids": 0, "offers": 0},
            {"price": 98, "bids": 0, "offers": 0},
            {"price": 97, "bids": 0, "offers": 0},
        ]

        assert data["prices"] == expected_data


def test_limit_order_submission(client):
    """
    API accepts limit orders and returns updated price information
    to all connected devices
    """
    # client = TestClient(app)

    with client.websocket_connect(WEBSOCKET_URL) as websocket:
        data = websocket.receive_json()

        websocket.send_json({"price": 101, "quantity": -10})

        data = websocket.receive_json()

        expected_data = [
            {"price": 102, "bids": 0, "offers": 0},
            {"price": 101, "bids": 0, "offers": 10},
            {"price": 100, "bids": 0, "offers": 0},
            {"price": 99, "bids": 0, "offers": 0},
            {"price": 98, "bids": 0, "offers": 0},
            {"price": 97, "bids": 0, "offers": 0},
        ]

        assert data["prices"] == expected_data


def test_market_order_submission():
    """
    API accepts market orders and returns updated price information
    to all connected devices
    """
    order_book = models.OrderBook()
    existing_order = models.Order(
        user_id="chad",
        quantity=-5,
        price=101,
    )
    order_book.place_order(existing_order)

    client = TestClient(create_app(order_book=order_book))

    with client.websocket_connect(WEBSOCKET_URL) as websocket:
        data = websocket.receive_json()

        print(f"{data=}")

        # buy 2 at market
        websocket.send_json({"price": None, "quantity": 2})

        data = websocket.receive_json()

        # expect offers at price 101 to be reduced to 3
        expected_data = [
            {"price": 103, "bids": 0, "offers": 0},
            {"price": 102, "bids": 0, "offers": 0},
            {"price": 101, "bids": 0, "offers": 3},
            {"price": 100, "bids": 0, "offers": 0},
            {"price": 99, "bids": 0, "offers": 0},
            {"price": 98, "bids": 0, "offers": 0},
        ]

        assert data["prices"] == expected_data
