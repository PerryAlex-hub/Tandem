from pycrdt import Doc, Map
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis_client import redis_client
from app.services.snapshot_service import load_snapshot

REDIS_KEY_PREFIX = "doc:board:"
DOC_TYPE = "board"


class BoardManager:
    def __init__(self) -> None:
        self.boards: dict[str, Doc] = {}

    async def get_or_create(self, room_code: str, db: AsyncSession | None = None) -> Doc:
        if room_code in self.boards:
            return self.boards[room_code]

        doc = Doc()
        doc.get("objects", type=Map)

        snapshot = await redis_client.get(f"{REDIS_KEY_PREFIX}{room_code}")

        if snapshot is None and db is not None:
            snapshot = await load_snapshot(db, room_code, DOC_TYPE)
            if snapshot is not None:
                await redis_client.set(f"{REDIS_KEY_PREFIX}{room_code}", snapshot)

        if snapshot is not None:
            doc.apply_update(snapshot)

        self.boards[room_code] = doc
        return doc

    async def save(self, room_code: str) -> None:
        doc = self.boards[room_code]
        await redis_client.set(f"{REDIS_KEY_PREFIX}{room_code}", doc.get_update())


board_manager = BoardManager()
