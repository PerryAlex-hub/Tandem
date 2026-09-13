import random 
import string
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.room import Room

def _generate_code(length: int = 6 ) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(random.choices(alphabet, k=length))

async def create_room(db: AsyncSession) -> Room:
    while True:
        code = _generate_code()
        existing_room = await db.execute(select(Room).where(Room.code == code))
        if existing_room.scalar_one_or_none() is None:
            break
    new_room = Room(code=code)
    db.add(new_room)
    await db.commit()
    await db.refresh(new_room)
    return new_room