import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.board_manager import board_manager
from app.core.connection_manager import manager
from app.core.document_manager import document_manager
from app.crdt.objects import ObjectOp
from app.db.session import get_db
from app.models.participant import Participant
from app.ot.operations import parse_operation

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

    doc = document_manager.get_or_create(room_code)
    await websocket.send_json({
        "type": "editor_state",
        "payload": {"content": doc.content, "revision": doc.revision},
    })

    board = board_manager.get_or_create(room_code)
    await websocket.send_json({
        "type": "whiteboard_state",
        "payload": {"objects": board.get_all()},
    })

    await manager.broadcast(room_code, {
        "type": "presence",
        "payload": {"event": "join", "display_name": participant.display_name},
    })

    try:
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")

            if message_type == "editor_op":
                try:
                    op = parse_operation(data["payload"]["op"])
                    base_revision = data["payload"]["base_revision"]
                except (KeyError, ValidationError) as exc:
                    await websocket.send_json({"type": "error", "payload": {"detail": str(exc)}})
                    continue

                doc = document_manager.get_or_create(room_code)
                transformed_op, new_revision = doc.receive_op(base_revision, op)

                await manager.broadcast(room_code, {
                    "type": "editor_op",
                    "payload": {"op": transformed_op.model_dump(), "revision": new_revision},
                })

            elif message_type == "whiteboard_op":
                try:
                    op = ObjectOp(**data["payload"])
                except (KeyError, ValidationError) as exc:
                    await websocket.send_json({"type": "error", "payload": {"detail": str(exc)}})
                    continue

                board = board_manager.get_or_create(room_code)
                resolved = board.apply_op(op)

                await manager.broadcast(room_code, {
                    "type": "whiteboard_op",
                    "payload": resolved.model_dump(),
                })

            else:
                await manager.broadcast(room_code, data)
    except WebSocketDisconnect:
        manager.disconnect(room_code, websocket)
        await manager.broadcast(room_code, {
            "type": "presence",
            "payload": {"event": "leave", "display_name": participant.display_name},
        })
