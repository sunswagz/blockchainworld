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

    def add_provider_payload(self, *, source: str, entity_id: str, fetched_at: str,
                             payload_json: str, payload_hash: str) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                """INSERT INTO provider_payloads
                (source, entity_id, fetched_at, payload_json, payload_hash)
                VALUES (?, ?, ?, ?, ?)""",
                (source, entity_id, fetched_at, payload_json, payload_hash))
            return int(cur.lastrowid)

    def add_pool_snapshot(self, item: PoolSnapshot) -> int:
        item.validate()
        data = to_dict(item)
        columns = list(data)
        with self._connect() as conn:
            cur = conn.execute(
                f"INSERT INTO pool_snapshots ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
                [data[k] for k in columns])
            return int(cur.lastrowid)

    def add_pool_activity_snapshot(self, item: dict) -> int:
        columns = [
            "pool_id", "block_number", "block_hash", "block_timestamp", "window",
            "from_block", "to_block", "swap_count", "volume_usd_estimated",
            "fees_usd_estimated", "fee_token0_raw_estimated", "fee_token1_raw_estimated",
            "volume_token0_raw", "volume_token1_raw", "method", "data_status", "raw_ref",
        ]
        with self._connect() as conn:
            cur = conn.execute(
                f"INSERT INTO pool_activity_snapshots ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
                [item.get(k) for k in columns])
            return int(cur.lastrowid)

    def list_pool_activity(self, pool_id: str | None = None, limit: int = 100) -> list[dict]:
        query = "SELECT * FROM pool_activity_snapshots"
        params: list = []
        if pool_id:
            query += " WHERE pool_id = ?"
            params.append(pool_id)
        query += " ORDER BY block_timestamp DESC, id DESC LIMIT ?"
        params.append(limit)
        with self._connect() as conn:
            return [dict(row) for row in conn.execute(query, params).fetchall()]

    def add_position_snapshot(self, item: PositionSnapshot) -> int:
        item.validate()
        data = to_dict(item)
        data["in_range"] = None if data["in_range"] is None else int(data["in_range"])
        columns = list(data)
        with self._connect() as conn:
            cur = conn.execute(
                f"INSERT INTO position_snapshots ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
                [data[k] for k in columns])
            return int(cur.lastrowid)

    def add_position_fee_snapshot(self, item: dict) -> int:
        columns = [
            "position_id", "token_id", "wallet_address", "block_number", "block_hash",
            "block_timestamp", "pool_address", "token0_address", "token1_address",
            "token0_symbol", "token1_symbol", "token0_decimals", "token1_decimals",
            "tokens_owed0_raw", "tokens_owed1_raw", "tokens_owed0_human",
            "tokens_owed1_human", "current_tick", "tick_lower", "tick_upper",
            "liquidity_raw", "fee_tier", "data_status", "raw_ref",
        ]
        with self._connect() as conn:
            cur = conn.execute(
                f"INSERT INTO position_fee_snapshots ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
                [item.get(k) for k in columns])
            return int(cur.lastrowid)

    def list_position_fees(self, wallet: str | None = None, limit: int = 100) -> list[dict]:
        query = """SELECT f.* FROM position_fee_snapshots f
            JOIN (SELECT position_id, MAX(id) AS latest_id FROM position_fee_snapshots GROUP BY position_id) x
            ON f.id = x.latest_id"""
        params: list = []
        if wallet:
            query += " WHERE lower(f.wallet_address) = lower(?)"
            params.append(wallet)
        query += " ORDER BY f.block_number DESC, f.id DESC LIMIT ?"
        params.append(limit)
        with self._connect() as conn:
            return [dict(row) for row in conn.execute(query, params).fetchall()]

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
                 json.dumps(data["recommended_checks"], ensure_ascii=False)))
            return int(cur.lastrowid)

    def list_pools(self, limit: int = 100) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """SELECT p.* FROM pool_snapshots p
                JOIN (SELECT pool_id, MAX(id) AS latest_id FROM pool_snapshots GROUP BY pool_id) x
                ON p.id = x.latest_id ORDER BY p.observed_at DESC LIMIT ?""",
                (limit,)).fetchall()
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
                (limit,)).fetchall()
            out = []
            for row in rows:
                item = dict(row)
                item["evidence"] = json.loads(item.pop("evidence_json"))
                item["recommended_checks"] = json.loads(item.pop("recommended_checks_json"))
                out.append(item)
            return out
