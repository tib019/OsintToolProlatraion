from __future__ import annotations

import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.websocket_manager import ws_manager

router = APIRouter()


@router.websocket("/ws/{case_id}")
async def websocket_endpoint(websocket: WebSocket, case_id: str) -> None:
    """WebSocket endpoint for real-time case graph updates."""
    await ws_manager.connect(case_id, websocket)
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                message = json.loads(raw)
            except json.JSONDecodeError:
                message = {"type": raw}

            msg_type = message.get("type", "").upper()

            if msg_type == "PING":
                await websocket.send_text(json.dumps({"type": "PONG"}))
            # Other client-initiated message types can be handled here
    except WebSocketDisconnect:
        ws_manager.disconnect(case_id, websocket)
