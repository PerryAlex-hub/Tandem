from pycrdt import Doc, Text

from app.core.redis_client import redis_client

REDIS_KEY_PREFIX = "doc:editor:"


class DocumentManager:
    def __init__(self) -> None:
        self.documents: dict[str, Doc] = {}

    async def get_or_create(self, room_code: str) -> Doc:
        if room_code in self.documents:
            return self.documents[room_code]

        doc = Doc()
        doc.get("content", type=Text)

        snapshot = await redis_client.get(f"{REDIS_KEY_PREFIX}{room_code}")
        if snapshot is not None:
            doc.apply_update(snapshot)

        self.documents[room_code] = doc
        return doc

    async def save(self, room_code: str) -> None:
        doc = self.documents[room_code]
        await redis_client.set(f"{REDIS_KEY_PREFIX}{room_code}", doc.get_update())


document_manager = DocumentManager()
