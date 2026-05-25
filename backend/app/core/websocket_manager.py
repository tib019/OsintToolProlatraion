from __future__ import annotations

import json
from collections import defaultdict

from fastapi import WebSocket


class WebSocketManager:
    """Manages active WebSocket connections grouped by case_id."""

    def __init__(self) -> None:
        self.connections: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(self, case_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections[case_id].append(websocket)

    def disconnect(self, case_id: str, websocket: WebSocket) -> None:
        try:
            self.connections[case_id].remove(websocket)
        except ValueError:
            pass
        # Clean up empty lists
        if not self.connections[case_id]:
            del self.connections[case_id]

    async def broadcast(self, case_id: str, event_type: str, payload: dict) -> None:
        """Send a JSON message to all connections subscribed to case_id."""
        message = json.dumps({"type": event_type, "payload": payload})
        dead: list[WebSocket] = []
        for ws in self.connections.get(case_id, []):
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            try:
                self.connections[case_id].remove(ws)
            except (ValueError, KeyError):
                pass


ws_manager = WebSocketManager()
