import base64
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.board_manager import board_manager
from app.core.connection_manager import manager
from app.core.document_manager import document_manager
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

    doc = await document_manager.get_or_create(room_code, db)
    await websocket.send_json({
        "type": "editor_sync",
        "payload": {"update": base64.b64encode(doc.get_update()).decode("ascii")},
    })

    board = await board_manager.get_or_create(room_code, db)
    await websocket.send_json({
        "type": "whiteboard_sync",
        "payload": {"update": base64.b64encode(board.get_update()).decode("ascii")},
    })

    await manager.broadcast(room_code, {
        "type": "presence",
        "payload": {"event": "join", "display_name": participant.display_name},
    })

    try:
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")

            if message_type == "editor_update":
                try:
                    update_bytes = base64.b64decode(data["payload"]["update"])
                except (KeyError, ValueError) as exc:
                    await websocket.send_json({"type": "error", "payload": {"detail": str(exc)}})
                    continue

                doc = await document_manager.get_or_create(room_code)
                doc.apply_update(update_bytes)
                await document_manager.save(room_code)

                await manager.broadcast(room_code, {
                    "type": "editor_update",
                    "payload": {"update": data["payload"]["update"]},
                })

            elif message_type == "whiteboard_update":
                try:
                    update_bytes = base64.b64decode(data["payload"]["update"])
                except (KeyError, ValueError) as exc:
                    await websocket.send_json({"type": "error", "payload": {"detail": str(exc)}})
                    continue

                board = await board_manager.get_or_create(room_code)
                board.apply_update(update_bytes)
                await board_manager.save(room_code)

                await manager.broadcast(room_code, {
                    "type": "whiteboard_update",
                    "payload": {"update": data["payload"]["update"]},
                })

            else:
                await manager.broadcast(room_code, data)
    except WebSocketDisconnect:
        manager.disconnect(room_code, websocket)
        await manager.broadcast(room_code, {
            "type": "presence",
            "payload": {"event": "leave", "display_name": participant.display_name},
        })
