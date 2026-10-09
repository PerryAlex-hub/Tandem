from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.room import RoomOut, SetProblemRequest
from app.schemas.participant import ParticipantJoin, ParticipantOut
from app.schemas.problem import ProblemOut
from app.services.room_service import create_room, get_room_by_code, set_current_problem
from app.services.participant_service import create_participant
from app.services.problem_service import get_problem
from app.core.connection_manager import manager

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


@router.post("/{code}/problem", response_model=ProblemOut)
async def set_room_problem_endpoint(
    code: str,
    payload: SetProblemRequest,
    db: AsyncSession = Depends(get_db),
):
    room = await get_room_by_code(db, code)
    if room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

    problem = await get_problem(db, payload.frontend_id)
    if problem is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")

    await set_current_problem(db, room, problem.frontend_id)

    problem_payload = ProblemOut.model_validate(problem).model_dump()
    await manager.broadcast(code, {"type": "set_problem", "payload": problem_payload})

    return problem
