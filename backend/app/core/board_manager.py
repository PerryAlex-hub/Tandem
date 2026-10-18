from pycrdt import Doc, Map

from app.core.redis_client import redis_client

REDIS_KEY_PREFIX = "doc:board:"


class BoardManager:
    def __init__(self) -> None:
        self.boards: dict[str, Doc] = {}

    async def get_or_create(self, room_code: str) -> Doc:
        if room_code in self.boards:
            return self.boards[room_code]

        doc = Doc()
        doc.get("objects", type=Map)

        snapshot = await redis_client.get(f"{REDIS_KEY_PREFIX}{room_code}")
        if snapshot is not None:
            doc.apply_update(snapshot)

        self.boards[room_code] = doc
        return doc

    async def save(self, room_code: str) -> None:
        doc = self.boards[room_code]
        await redis_client.set(f"{REDIS_KEY_PREFIX}{room_code}", doc.get_update())


board_manager = BoardManager()
