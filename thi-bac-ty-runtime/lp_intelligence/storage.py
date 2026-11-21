"""Append-only SQLite storage for LP snapshots, provider payloads and alerts."""
from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path

from .contracts import AlertEvent, PoolSnapshot, PositionSnapshot, to_dict

DEFAULT_DB = Path(os.getenv("LP_INTELLIGENCE_DB", "data/lp-intelligence.sqlite"))
SCHEMA = Path(__file__).with_name("schema.sql")


class SQLiteStore:
    def __init__(self, path: str | Path = DEFAULT_DB):
        self.path = Path(path)

    def _connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def initialize(self) -> None:
        with self._connect() as conn:
            conn.executescript(SCHEMA.read_text(encoding="utf-8"))

    def add_provider_payload(
        self, *, source: str, entity_id: str, fetched_at: str,
        payload_json: str, payload_hash: str,
    ) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                """INSERT INTO provider_payloads
                (source, entity_id, fetched_at, payload_json, payload_hash)
                VALUES (?, ?, ?, ?, ?)""",
                (source, entity_id, fetched_at, payload_json, payload_hash),
            )
            return int(cur.lastrowid)

    def add_pool_snapshot(self, item: PoolSnapshot) -> int:
        item.validate()
        data = to_dict(item)
        columns = list(data)
        with self._connect() as conn:
            cur = conn.execute(
                f"INSERT INTO pool_snapshots ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
                [data[k] for k in columns],
            )
            return int(cur.lastrowid)

    def add_position_snapshot(self, item: PositionSnapshot) -> int:
        item.validate()
        data = to_dict(item)
        data["in_range"] = None if data["in_range"] is None else int(data["in_range"])
        columns = list(data)
        with self._connect() as conn:
            cur = conn.execute(
                f"INSERT INTO position_snapshots ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
                [data[k] for k in columns],
            )
            return int(cur.lastrowid)

    def add_alert(self, item: AlertEvent) -> int:
        item.validate()
        data = to_dict(item)
        with self._connect() as conn:
            cur = conn.execute(
                """INSERT INTO alert_events
                (dedupe_key, severity, title, message, observed_at, evidence_json, recommended_checks_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (data["dedupe_key"], data["severity"], data["title"], data["message"],
                 data["observed_at"], json.dumps(data["evidence"], ensure_ascii=False),
                 json.dumps(data["recommended_checks"], ensure_ascii=False)),
            )
            return int(cur.lastrowid)

    def list_pools(self, limit: int = 100) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """SELECT p.* FROM pool_snapshots p
                JOIN (SELECT pool_id, MAX(id) AS latest_id FROM pool_snapshots GROUP BY pool_id) x
                ON p.id = x.latest_id ORDER BY p.observed_at DESC LIMIT ?""",
                (limit,),
            ).fetchall()
            return [dict(row) for row in rows]

    def list_positions(self, wallet: str | None = None, limit: int = 100) -> list[dict]:
        query = """SELECT p.* FROM position_snapshots p
            JOIN (SELECT position_id, MAX(id) AS latest_id FROM position_snapshots GROUP BY position_id) x
            ON p.id = x.latest_id"""
        params: list = []
        if wallet:
            query += " WHERE lower(p.wallet_address) = lower(?)"
            params.append(wallet)
        query += " ORDER BY p.observed_at DESC LIMIT ?"
        params.append(limit)
        with self._connect() as conn:
            return [dict(row) for row in conn.execute(query, params).fetchall()]

    def list_alerts(self, limit: int = 100) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM alert_events ORDER BY observed_at DESC, id DESC LIMIT ?",
                (limit,),
            ).fetchall()
            out = []
            for row in rows:
                item = dict(row)
                item["evidence"] = json.loads(item.pop("evidence_json"))
                item["recommended_checks"] = json.loads(item.pop("recommended_checks_json"))
                out.append(item)
            return out
