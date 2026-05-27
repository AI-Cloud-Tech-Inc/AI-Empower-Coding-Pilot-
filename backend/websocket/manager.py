"""WebSocket connection manager for real-time updates."""

from __future__ import annotations

import asyncio
import json
from enum import StrEnum

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

ws_router = APIRouter()


class EventType(StrEnum):
    AGENT_STATUS = "agent_status"
    PIPELINE_PROGRESS = "pipeline_progress"
    PIPELINE_COMPLETE = "pipeline_complete"
    COST_UPDATE = "cost_update"
    AUDIT_EVENT = "audit_event"
    APPROVAL_UPDATE = "approval_update"
    SYSTEM_ALERT = "system_alert"


class ConnectionManager:
    """Manages WebSocket connections and broadcasts events."""

    def __init__(self) -> None:
        self._connections: dict[str, list[WebSocket]] = {}
        self._accepted: set[WebSocket] = set()
        self._ws_channels: dict[int, set[str]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, channel: str = "default") -> None:
        if websocket not in self._accepted:
            await websocket.accept()
            self._accepted.add(websocket)
        await self.subscribe(websocket, channel)

    async def subscribe(self, websocket: WebSocket, channel: str) -> None:
        async with self._lock:
            if channel not in self._connections:
                self._connections[channel] = []
            if websocket not in self._connections[channel]:
                self._connections[channel].append(websocket)
            ws_id = id(websocket)
            if ws_id not in self._ws_channels:
                self._ws_channels[ws_id] = set()
            self._ws_channels[ws_id].add(channel)

    async def disconnect(self, websocket: WebSocket) -> None:
        ws_id = id(websocket)
        async with self._lock:
            channels = self._ws_channels.pop(ws_id, set())
            for channel in channels:
                if channel in self._connections:
                    self._connections[channel] = [
                        ws for ws in self._connections[channel] if ws != websocket
                    ]
                    if not self._connections[channel]:
                        del self._connections[channel]
            self._accepted.discard(websocket)

    async def broadcast(self, event_type: str, data: dict, channel: str = "default") -> None:
        message = json.dumps({"type": event_type, "data": data})
        async with self._lock:
            connections = list(self._connections.get(channel, []))
        for ws in connections:
            try:
                await ws.send_text(message)
            except Exception:
                await self.disconnect(ws)

    async def send_to(self, websocket: WebSocket, event_type: str, data: dict) -> None:
        message = json.dumps({"type": event_type, "data": data})
        await websocket.send_text(message)

    @property
    def active_connections(self) -> int:
        return len(self._accepted)


manager = ConnectionManager()


@ws_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("type") == "subscribe":
                    channel = msg.get("channel", "default")
                    await manager.subscribe(websocket, channel)
                elif msg.get("type") == "ping":
                    await manager.send_to(websocket, "pong", {})
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        await manager.disconnect(websocket)


@ws_router.websocket("/ws/{channel}")
async def websocket_channel(websocket: WebSocket, channel: str) -> None:
    await manager.connect(websocket, channel)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("type") == "ping":
                    await manager.send_to(websocket, "pong", {})
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
