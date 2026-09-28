import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.participant import Participant


async def create_participant(db: AsyncSession, room_id: uuid.UUID, display_name: str) -> Participant:
    participant = Participant(room_id=room_id, display_name=display_name)
    db.add(participant)
    await db.commit()
    await db.refresh(participant)
    return participant
