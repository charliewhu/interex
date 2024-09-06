import json
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from domain import exceptions, models
from service_layer import services


def create_app(
    order_book: models.OrderBook = models.OrderBook(),
):
    app = FastAPI()

    origins = [
        "http://0.0.0.0",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    logger = logging.getLogger("__name__")
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())

    class ConnectionManager:
        def __init__(self):
            self.active_connections: list[WebSocket] = []

        async def connect(self, websocket: WebSocket):
            await websocket.accept()
            self.active_connections.append(websocket)

        def disconnect(self, websocket: WebSocket):
            self.active_connections.remove(websocket)

        async def send_personal_message(self, message: str, websocket: WebSocket):
            await websocket.send_text(message)

        async def broadcast(self, message: str):
            for connection in self.active_connections:
                await connection.send_text(message)

    order_manager = ConnectionManager()
    chat_manager = ConnectionManager()

    @app.websocket("/api/ws/orders")
    async def submit_order(websocket: WebSocket):
        """
        On connect: send order_book data
        On action: broadcast data
        On disconnect: disconnect from exchange
        """
        # data = await exchange.connect(websocket)

        # try:
        #     while True:
        #         data = await websocket.receive_json()

        #         response = exchange.order(data)
        #         await websocket.send_json(response_data)

        # except WebSocketDisconnect:
        #     order_manager.disconnect(websocket)

        ###############################################################
        await order_manager.connect(websocket)

        prices = order_book.prices()
        response_data = {"price": order_book.last_price, "prices": prices}
        await websocket.send_json(response_data)

        try:
            while True:
                data = await websocket.receive_json()
                try:
                    logger.info(f"{order_book=}")
                    logger.info(f'{data['price'], data['quantity']}')
                    logger.info(f"pre service: {order_book.prices()}")
                    # order = models.Order(
                    #     price=int(data["price"]),
                    #     quantity=int(data["quantity"]),
                    # )
                    # order_book.place_order(order)
                    services.order(
                        order_book=order_book,
                        price=data["price"],
                        quantity=data["quantity"],
                    )
                    logger.info(f"post service: {order_book.prices()}")
                    response_data = {
                        "price": order_book.last_price,
                        "prices": order_book.prices(),
                    }

                    await order_manager.broadcast(json.dumps(response_data))
                except exceptions.InvalidOrder:
                    response_data["error"] = "Invalid Order"
                    await websocket.send_json(response_data)
                except exceptions.NoOrdersAvailable:
                    response_data["error"] = "No Limit Orders Available"
                    await websocket.send_json(response_data)

        except WebSocketDisconnect:
            order_manager.disconnect(websocket)

    @app.websocket("/api/ws/chat/{client_id}")
    async def websocket_endpoint(websocket: WebSocket, client_id: int):
        await chat_manager.connect(websocket)
        await chat_manager.broadcast(
            f"There are {len(chat_manager.active_connections)} clients connected"
        )
        try:
            while True:
                data = await websocket.receive_text()
                await chat_manager.send_personal_message(
                    f"You wrote: {data}", websocket
                )
                await chat_manager.broadcast(f"{client_id} says: {data}")
        except WebSocketDisconnect:
            chat_manager.disconnect(websocket)
            await chat_manager.broadcast(f"{client_id} left the chat")
            await chat_manager.broadcast(
                f"There are {len(chat_manager.active_connections)} clients connected"
            )

    html = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Chat</title>
        </head>
        <body>
            <h1>WebSocket Chat</h1>
            <h2>Your ID: <span id="ws-id"></span></h2>
            <form action="" onsubmit="sendMessage(event)">
                <input type="text" id="messageText" autocomplete="off"/>
                <button>Send</button>
            </form>
            <ul id='messages'>
            </ul>
            <script>
                var client_id = Date.now()
                document.querySelector("#ws-id").textContent = client_id;
                var ws = new WebSocket(`ws://localhost:8080/api/ws/chat/${client_id}`);
                ws.onmessage = function(event) {
                    var messages = document.getElementById('messages')
                    var message = document.createElement('li')
                    var content = document.createTextNode(event.data)
                    message.appendChild(content)
                    messages.appendChild(message)
                };
                function sendMessage(event) {
                    var input = document.getElementById("messageText")
                    ws.send(input.value)
                    input.value = ''
                    event.preventDefault()
                }
            </script>
        </body>
    </html>
    """

    @app.get("/")
    async def get():
        return HTMLResponse(html)

    return app


app = create_app()
