#!/usr/bin/env python3
"""Evaluate LP position alerts and deliver pending Telegram notifications."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lp_intelligence.alerting import evaluate_position_alerts
from lp_intelligence.storage import SQLiteStore
from lp_intelligence.telegram import format_alert, send_message


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wallet", default=os.getenv("LP_WALLET_ADDRESS"))
    parser.add_argument("--dry-run", action="store_true", help="Evaluate and print alerts without Telegram delivery")
    args = parser.parse_args()

    store = SQLiteStore()
    store.initialize()
    evaluated = evaluate_position_alerts(store, wallet=args.wallet)
    print(f"Checked {evaluated['checked_positions']} positions; created {evaluated['created_count']} alerts.")

    pending = store.list_pending_alerts(limit=100)
    if args.dry_run:
        for alert in pending:
            print(format_alert(alert), "\n---")
        return 0

    if not pending:
        print("No pending alerts.")
        return 0
    if not os.getenv("TELEGRAM_BOT_TOKEN") or not os.getenv("TELEGRAM_CHAT_ID"):
        print(f"{len(pending)} pending alert(s); Telegram is not configured. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID.")
        return 0

    sent = failed = 0
    for alert in pending:
        try:
            send_message(format_alert(alert))
            store.set_alert_delivery_status(alert["id"], "sent")
            sent += 1
        except Exception as exc:
            store.set_alert_delivery_status(alert["id"], f"failed:{type(exc).__name__}")
            failed += 1
            print(f"Alert {alert['id']} delivery failed: {type(exc).__name__}", file=sys.stderr)
    print(f"Telegram delivery: {sent} sent, {failed} failed.")
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
