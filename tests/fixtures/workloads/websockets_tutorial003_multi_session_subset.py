"""Independent ASGI workload for FastAPI 0.141.1 WebSocket tutorial 003.

The workflow supplies one sequential session and one deterministic, scheduled
two-client conversation. Workload behavior is defined here independently of
the upstream test; the input recipe controls client events and captures output.
"""

HTML = """
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
            var ws = new WebSocket(`ws://localhost:8000/ws/${client_id}`);
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


def create_app(factory_input=None, event_trace=None):
    """Build the app surface selected by input-only fixture data."""
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse

    app = FastAPI()

    @app.get("/")
    async def get():
        return HTMLResponse(HTML)

    if (factory_input or {}).get("websocket", False):
        from fastapi import WebSocket, WebSocketDisconnect

        class ConnectionManager:
            def __init__(self) -> None:
                self.active_connections: list[WebSocket] = []

            async def connect(self, websocket: WebSocket) -> None:
                await websocket.accept()
                self.active_connections.append(websocket)

            def disconnect(self, websocket: WebSocket) -> None:
                self.active_connections.remove(websocket)

            async def send_personal_message(self, message: str, websocket: WebSocket) -> None:
                await websocket.send_text(message)

            async def broadcast(self, message: str) -> None:
                for connection in self.active_connections:
                    await connection.send_text(message)

        manager = ConnectionManager()

        @app.websocket("/ws/{client_id}")
        async def websocket_endpoint(websocket: WebSocket, client_id: int) -> None:
            await manager.connect(websocket)
            try:
                while True:
                    data = await websocket.receive_text()
                    await manager.send_personal_message(f"You wrote: {data}", websocket)
                    await manager.broadcast(f"Client #{client_id} says: {data}")
            except WebSocketDisconnect:
                manager.disconnect(websocket)
                await manager.broadcast(f"Client #{client_id} left the chat")

    return app
