import pytest


WEBSOCKET_URL = "/ws/orders"


def test_shows_price_levels(client):
    """
    API should return current prices on connection to WebSocket
    """

    with client.websocket_connect(WEBSOCKET_URL) as ws:
        data = ws.receive_json()

        expected_data = [
            {"price": 102, "bids": 0, "offers": 0},
            {"price": 101, "bids": 0, "offers": 0},
            {"price": 100, "bids": 0, "offers": 0},
            {"price": 99, "bids": 0, "offers": 0},
            {"price": 98, "bids": 0, "offers": 0},
        ]

        assert data["prices"] == expected_data


def test_limit_order_submission(client):
    """
    API accepts limit orders and returns updated price information
    to all connected devices
    """

    with client.websocket_connect(WEBSOCKET_URL) as ws:
        data = ws.receive_json()

        ws.send_json({"price": 101, "quantity": -10})

        data = ws.receive_json()

        expected_data = [
            {"price": 102, "bids": 0, "offers": 0},
            {"price": 101, "bids": 0, "offers": 10},
            {"price": 100, "bids": 0, "offers": 0},
            {"price": 99, "bids": 0, "offers": 0},
            {"price": 98, "bids": 0, "offers": 0},
        ]

        assert data["prices"] == expected_data


def test_market_order_submission(client):
    """
    API accepts market orders and returns updated price information
    to all connected devices
    """

    with client.websocket_connect(WEBSOCKET_URL) as ws:
        ws.receive_json()
        ws.send_json({"price": 101, "quantity": -5})

    with client.websocket_connect(WEBSOCKET_URL) as ws:
        ws.receive_json()

        # buy 2 at market
        ws.send_json({"price": None, "quantity": 2})

        data = ws.receive_json()

        # expect offers at price 101 to be reduced to 3
        expected_data = [
            {"price": 103, "bids": 0, "offers": 0},
            {"price": 102, "bids": 0, "offers": 0},
            {"price": 101, "bids": 0, "offers": 3},
            {"price": 100, "bids": 0, "offers": 0},
            {"price": 99, "bids": 0, "offers": 0},
        ]

        assert data["prices"] == expected_data


@pytest.mark.xfail
def test_error_handling():
    raise NotImplementedError
