from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db 
from app.schemas.room import RoomOut
from app.services.room_service import create_room
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/rooms", tags=["rooms"])

@router.post("/", response_model=RoomOut)
async def create_room_endpoint(db: AsyncSession = Depends(get_db)):
    room = await create_room(db)
    return room