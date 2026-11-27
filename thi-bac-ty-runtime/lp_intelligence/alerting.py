"""Rule-based LP alerts. Only emits alerts from explicit, verified range states.

The evaluator is intentionally conservative: it never infers a USD loss or suggests
an automated rebalance from a tick-range transition.
"""
from __future__ import annotations

from .contracts import AlertEvent, utc_now
from .storage import SQLiteStore


def evaluate_position_alerts(store: SQLiteStore, wallet: str | None = None) -> dict:
    created: list[int] = []
    suppressed = 0
    checked = 0

    # Base position snapshots carry an explicit boolean in_range field.
    for position in store.list_positions(wallet=wallet, limit=500):
        checked += 1
        if position.get("in_range") is None or bool(position.get("in_range")):
            continue
        position_id = str(position.get("position_id") or "unknown")
        chain_id = str(position.get("chain_id") or "unknown")
        tick = position.get("current_tick")
        lower = position.get("tick_lower")
        upper = position.get("tick_upper")
        event = AlertEvent(
            dedupe_key=f"lp-out-of-range:{chain_id}:{position_id}",
            severity="warning",
            title="LP position is out of range",
            message=(
                f"Position {position_id} on chain {chain_id} is currently outside its configured tick range. "
                "The position may no longer be earning swap fees while it remains out of range."
            ),
            observed_at=utc_now(),
            evidence=({
                "position_id": position_id, "chain_id": chain_id,
                "current_tick": tick, "tick_lower": lower, "tick_upper": upper,
                "data_status": position.get("data_status"),
                "source": position.get("source"), "source_url": position.get("source_url"),
            },),
            recommended_checks=(
                "Verify the latest block and position state in the source explorer.",
                "Review the current token exposure and range; this alert does not recommend or execute a transaction.",
            ),
        )
        alert_id = store.add_alert_if_not_recent(event, cooldown_minutes=360)
        if alert_id is None:
            suppressed += 1
        else:
            created.append(alert_id)

    # X Layer collector records explicit range_status strings, not USD fee/PnL.
    if wallet:
        for position in store.list_xlayer_positions(wallet=wallet, limit=500):
            checked += 1
            status = str(position.get("range_status") or "").lower()
            if status not in {"below", "above", "below_range", "above_range", "out_of_range"}:
                continue
            token_id = str(position.get("token_id") or "unknown")
            event = AlertEvent(
                dedupe_key=f"lp-out-of-range:196:{token_id}",
                severity="warning",
                title="X Layer LP position is out of range",
                message=(
                    f"X Layer Uniswap V3 position NFT {token_id} is marked {status}. "
                    "Fee/PnL accounting for X Layer is incomplete."
                ),
                observed_at=utc_now(),
                evidence=({
                    "token_id": token_id, "chain_id": "196", "range_status": status,
                    "current_tick": position.get("current_tick"),
                    "tick_lower": position.get("tick_lower"),
                    "tick_upper": position.get("tick_upper"),
                    "block_number": position.get("block_number"),
                },),
                recommended_checks=(
                    "Verify the position state at the recorded block.",
                    "Do not interpret this alert as a USD loss or a trade instruction.",
                ),
            )
            alert_id = store.add_alert_if_not_recent(event, cooldown_minutes=360)
            if alert_id is None:
                suppressed += 1
            else:
                created.append(alert_id)

    return {"checked_positions": checked, "created_alert_ids": created,
            "created_count": len(created), "suppressed_count": suppressed}
