from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document_snapshot import DocumentSnapshot


async def load_snapshot(db: AsyncSession, room_code: str, doc_type: str) -> bytes | None:
    result = await db.execute(
        select(DocumentSnapshot.data).where(
            DocumentSnapshot.room_code == room_code,
            DocumentSnapshot.doc_type == doc_type,
        )
    )
    return result.scalar_one_or_none()


async def upsert_snapshot(db: AsyncSession, room_code: str, doc_type: str, data: bytes) -> None:
    stmt = pg_insert(DocumentSnapshot).values(room_code=room_code, doc_type=doc_type, data=data)
    stmt = stmt.on_conflict_do_update(
        index_elements=[DocumentSnapshot.room_code, DocumentSnapshot.doc_type],
        set_={"data": data, "updated_at": func.now()},
    )
    await db.execute(stmt)
    await db.commit()
