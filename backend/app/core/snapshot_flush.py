import asyncio

from app.core.board_manager import board_manager
from app.core.document_manager import document_manager
from app.db.session import AsyncSessionLocal
from app.services.snapshot_service import upsert_snapshot

FLUSH_INTERVAL_SECONDS = 30


async def flush_once() -> None:
    async with AsyncSessionLocal() as db:
        for room_code, doc in list(document_manager.documents.items()):
            await upsert_snapshot(db, room_code, "editor", doc.get_update())

        for room_code, doc in list(board_manager.boards.items()):
            await upsert_snapshot(db, room_code, "board", doc.get_update())


async def flush_loop() -> None:
    while True:
        await asyncio.sleep(FLUSH_INTERVAL_SECONDS)
        try:
            await flush_once()
        except Exception:
            # a failed flush shouldn't kill the background loop; Redis still
            # holds the hot copy, so we just try again next interval
            pass
