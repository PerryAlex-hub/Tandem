import asyncio
import json

from fastapi import WebSocket

from app.core.redis_client import redis_client


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict[str, list[WebSocket]] = {}
        self._listen_tasks: dict[str, asyncio.Task] = {}

    async def connect(self, room_code: str, websocket: WebSocket) -> None:
        await websocket.accept()
        is_new_room = room_code not in self.active_connections
        self.active_connections.setdefault(room_code, []).append(websocket)

        if is_new_room:
            self._listen_tasks[room_code] = asyncio.create_task(self._listen(room_code))

    def disconnect(self, room_code: str, websocket: WebSocket) -> None:
        connections = self.active_connections.get(room_code)
        if connections and websocket in connections:
            connections.remove(websocket)

            if not connections:
                del self.active_connections[room_code]
                task = self._listen_tasks.pop(room_code, None)
                if task:
                    task.cancel()

    async def broadcast(self, room_code: str, message: dict) -> None:
        await redis_client.publish(f"room:{room_code}:broadcast", json.dumps(message))

    async def _listen(self, room_code: str) -> None:
        channel = f"room:{room_code}:broadcast"
        pubsub = redis_client.pubsub()
        await pubsub.subscribe(channel)

        try:
            async for raw_message in pubsub.listen():
                if raw_message["type"] != "message":
                    continue

                message = json.loads(raw_message["data"])
                for connection in self.active_connections.get(room_code, []):
                    await connection.send_json(message)
        except asyncio.CancelledError:
            pass
        finally:
            await pubsub.unsubscribe(channel)
            await pubsub.close()


manager = ConnectionManager()
