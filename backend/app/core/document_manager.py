from pycrdt import Doc, Text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis_client import redis_client
from app.services.snapshot_service import load_snapshot

REDIS_KEY_PREFIX = "doc:editor:"
DOC_TYPE = "editor"


class DocumentManager:
    def __init__(self) -> None:
        self.documents: dict[str, Doc] = {}

    async def get_or_create(self, room_code: str, db: AsyncSession | None = None) -> Doc:
        if room_code in self.documents:
            return self.documents[room_code]

        doc = Doc()
        doc.get("content", type=Text)

        snapshot = await redis_client.get(f"{REDIS_KEY_PREFIX}{room_code}")

        if snapshot is None and db is not None:
            snapshot = await load_snapshot(db, room_code, DOC_TYPE)
            if snapshot is not None:
                # repopulate the hot cache so we don't hit Postgres again next time
                await redis_client.set(f"{REDIS_KEY_PREFIX}{room_code}", snapshot)

        if snapshot is not None:
            doc.apply_update(snapshot)

        self.documents[room_code] = doc
        return doc

    async def save(self, room_code: str) -> None:
        doc = self.documents[room_code]
        await redis_client.set(f"{REDIS_KEY_PREFIX}{room_code}", doc.get_update())


document_manager = DocumentManager()
