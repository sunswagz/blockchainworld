#!/usr/bin/env python3
"""Offline tests for LP alert rules, cooldown and Telegram delivery formatting."""
from __future__ import annotations
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lp_intelligence.alerting import evaluate_position_alerts
from lp_intelligence.contracts import PositionSnapshot, utc_now
from lp_intelligence.storage import SQLiteStore
from lp_intelligence.telegram import format_alert, send_message, TelegramDeliveryError
import httpx

with tempfile.TemporaryDirectory() as tmp:
    store = SQLiteStore(Path(tmp) / "alerts.sqlite")
    store.initialize()
    snapshot = PositionSnapshot(
        position_id="base:123", wallet_address="0x" + "1"*40,
        chain_id="8453", protocol="uniswap-v3", version="v3",
        pool_id="base:pool", observed_at=utc_now(), fetched_at=utc_now(),
        source="fixture", source_url="https://example.test/position",
        in_range=False, current_tick=120, tick_lower=100, tick_upper=110,
    )
    store.add_position_snapshot(snapshot)
    first = evaluate_position_alerts(store, snapshot.wallet_address)
    assert first["created_count"] == 1
    second = evaluate_position_alerts(store, snapshot.wallet_address)
    assert second["created_count"] == 0 and second["suppressed_count"] == 1
    pending = store.list_pending_alerts()
    assert len(pending) == 1
    assert "LP position is out of range" in format_alert(pending[0])

    seen = {}
    def handler(request):
        seen["url"] = str(request.url)
        seen["payload"] = request.read().decode()
        return httpx.Response(200, json={"ok": True, "result": {"message_id": 9}})
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        result = send_message("test alert", token="123:secret", chat_id="42", client=client)
    assert result["message_id"] == 9
    assert "/sendMessage" in seen["url"] and "test alert" in seen["payload"]

print("LP alert fixtures passed: out-of-range rule, cooldown dedupe, pending queue and Telegram sender.")
