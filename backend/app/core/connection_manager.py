from fastapi import WebSocket

class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, room_code: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.setdefault(room_code, []).append(websocket)
    
    def disconnect(self, room_code: str, websocket: WebSocket) -> None:
        connections = self.active_connections.get(room_code)
        if connections and websocket in connections:
            connections.remove(websocket)

            if not connections:
                del self.active_connections[room_code]

    async def broadcast(self, room_code: str, message: dict) -> None:
        for connection in self.active_connections.get(room_code,[]):
            await connection.send_json(message)
        
manager = ConnectionManager()