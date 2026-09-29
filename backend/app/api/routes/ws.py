import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.connection_manager import manager
from app.db.session import get_db
from app.models.participant import Participant

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/{room_code}")
async def room_websocket(
    websocket: WebSocket,
    room_code: str,
    participant_id: str,
    db: AsyncSession = Depends(get_db),
):
    try:
        participant_uuid = uuid.UUID(participant_id)
    except ValueError:
        await websocket.close(code=4400)
        return

    result = await db.execute(select(Participant).where(Participant.id == participant_uuid))
    participant = result.scalar_one_or_none()
    if participant is None:
        await websocket.close(code=4404)
        return

    await manager.connect(room_code, websocket)
    await manager.broadcast(room_code, {
        "type": "presence",
        "payload": {"event": "join", "display_name": participant.display_name},
    })

    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast(room_code, data)
    except WebSocketDisconnect:
        manager.disconnect(room_code, websocket)
        await manager.broadcast(room_code, {
            "type": "presence",
            "payload": {"event": "leave", "display_name": participant.display_name},
        })
