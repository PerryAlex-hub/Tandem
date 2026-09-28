from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.room import RoomOut
from app.schemas.participant import ParticipantJoin, ParticipantOut
from app.services.room_service import create_room, get_room_by_code
from app.services.participant_service import create_participant

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.post("/", response_model=RoomOut)
async def create_room_endpoint(db: AsyncSession = Depends(get_db)):
    room = await create_room(db)
    return room


@router.get("/{code}", response_model=RoomOut)
async def get_room_endpoint(code: str, db: AsyncSession = Depends(get_db)):
    room = await get_room_by_code(db, code)
    if room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    return room


@router.post("/{code}/join", response_model=ParticipantOut)
async def join_room_endpoint(
    code: str,
    payload: ParticipantJoin,
    db: AsyncSession = Depends(get_db),
):
    room = await get_room_by_code(db, code)
    if room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

    participant = await create_participant(db, room.id, payload.display_name)
    return participant
