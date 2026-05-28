"""Tests for WebSocket connection manager."""

from __future__ import annotations

import pytest

from backend.websocket.manager import ConnectionManager, EventType


class TestEventType:
    def test_event_types_exist(self) -> None:
        assert EventType.AGENT_STATUS == "agent_status"
        assert EventType.PIPELINE_PROGRESS == "pipeline_progress"
        assert EventType.PIPELINE_COMPLETE == "pipeline_complete"
        assert EventType.COST_UPDATE == "cost_update"
        assert EventType.AUDIT_EVENT == "audit_event"


class TestConnectionManager:
    def test_initial_state(self) -> None:
        mgr = ConnectionManager()
        assert mgr.active_connections == 0

    @pytest.mark.asyncio
    async def test_broadcast_no_connections(self) -> None:
        mgr = ConnectionManager()
        await mgr.broadcast("test", {"key": "value"})
