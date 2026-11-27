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


    def get_wallet_baseline(self, wallet: str, chain_id: str) -> dict | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM wallet_chain_baselines WHERE lower(wallet_address)=lower(?) AND chain_id=?",
                (wallet, str(chain_id)),
            ).fetchone()
            return None if row is None else dict(row)

    def add_wallet_baseline(self, item: dict) -> None:
        columns = ["wallet_address", "chain_id", "chain_name", "baseline_block",
                   "baseline_hash", "baseline_timestamp", "scan_from_block", "created_at"]
        with self._connect() as conn:
            conn.execute(
                f"INSERT OR IGNORE INTO wallet_chain_baselines ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
                [item.get(k) for k in columns],
            )

    def list_wallet_baselines(self, wallet: str) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM wallet_chain_baselines WHERE lower(wallet_address)=lower(?) ORDER BY CAST(chain_id AS INTEGER)",
                (wallet,),
            ).fetchall()
            return [dict(row) for row in rows]

    def add_wallet_monitor_run(self, wallet: str, observed_at: str, status: str, result: dict) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO wallet_monitor_runs(wallet_address,observed_at,status,result_json) VALUES(?,?,?,?)",
                (wallet.lower(), observed_at, status, json.dumps(result, ensure_ascii=False, sort_keys=True)),
            )
            return int(cur.lastrowid)

    def list_wallet_monitor_runs(self, wallet: str, limit: int = 20) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM wallet_monitor_runs WHERE lower(wallet_address)=lower(?) ORDER BY observed_at DESC,id DESC LIMIT ?",
                (wallet, limit),
            ).fetchall()
            out = []
            for row in rows:
                item = dict(row)
                item["result"] = json.loads(item.pop("result_json"))
                out.append(item)
            return out

    def add_xlayer_position_snapshot(self, wallet: str, block: dict, position: dict) -> int:
        payload = json.dumps(position, ensure_ascii=False, sort_keys=True)
        columns = ["wallet_address", "token_id", "block_number", "block_hash", "block_timestamp",
                   "pool_address", "token0", "token1", "fee_tier", "tick_lower", "tick_upper",
                   "current_tick", "liquidity_raw", "tokens_owed0_raw", "tokens_owed1_raw",
                   "range_status", "verification", "payload_json"]
        values = [
            wallet.lower(), str(position["token_id"]), block["number"], block["hash"],
            block["timestamp"], position.get("pool_address"), position.get("token0"),
            position.get("token1"), position.get("fee_tier"), position.get("tick_lower"),
            position.get("tick_upper"), position.get("current_tick"), position.get("liquidity_raw"),
            position.get("tokens_owed0_raw"), position.get("tokens_owed1_raw"),
            position.get("range_status"), position.get("verification", "unknown"), payload,
        ]
        with self._connect() as conn:
            cur = conn.execute(
                f"INSERT INTO xlayer_position_snapshots ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
                values,
            )
            return int(cur.lastrowid)

    def list_xlayer_positions(self, wallet: str, limit: int = 100) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """SELECT p.* FROM xlayer_position_snapshots p
                JOIN (SELECT token_id, MAX(id) AS latest_id FROM xlayer_position_snapshots
                WHERE lower(wallet_address)=lower(?) GROUP BY token_id) x ON p.id=x.latest_id
                ORDER BY p.block_number DESC LIMIT ?""",
                (wallet, limit),
            ).fetchall()
            out = []
            for row in rows:
                item = dict(row)
                item["payload"] = json.loads(item.pop("payload_json"))
                out.append(item)
            return out


    def add_token_price_observation(self, item: dict) -> int:
        columns = ["chain_id", "token_address", "price_usd", "observed_at",
                   "fetched_at", "source", "source_url", "data_status", "raw_ref"]
        with self._connect() as conn:
            cur = conn.execute(
                f"INSERT INTO token_price_observations ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
                [item.get(k) for k in columns],
            )
            return int(cur.lastrowid)

    def latest_token_price(self, chain_id: str, token_address: str) -> dict | None:
        with self._connect() as conn:
            row = conn.execute(
                """SELECT * FROM token_price_observations
                WHERE chain_id=? AND lower(token_address)=lower(?)
                ORDER BY observed_at DESC,id DESC LIMIT 1""",
                (str(chain_id), token_address),
            ).fetchone()
            return None if row is None else dict(row)

    def get_provider_payload(self, payload_id: int) -> dict | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM provider_payloads WHERE id=?", (payload_id,)
            ).fetchone()
            if row is None:
                return None
            item = dict(row)
            item["payload"] = json.loads(item.pop("payload_json"))
            return item

    def list_position_fee_history(self, position_id: str) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM position_fee_snapshots WHERE position_id=? ORDER BY block_timestamp,id",
                (position_id,),
            ).fetchall()
            return [dict(row) for row in rows]

    def add_position_performance_snapshot(self, item: dict) -> int:
        columns = [
            "position_id", "wallet_address", "chain_id", "block_number", "block_hash",
            "observed_at", "fetched_at", "token0_address", "token1_address",
            "token0_symbol", "token1_symbol", "amount0", "amount1", "fees0", "fees1",
            "price0_usd", "price1_usd", "principal_usd", "unclaimed_fees_usd",
            "position_value_usd", "initial_capital_usd", "hodl_value_usd",
            "il_vs_hodl_usd", "il_vs_hodl_pct", "fee_adjusted_vs_hodl_usd",
            "pnl_before_claimed_fees_and_costs_usd", "fee_apr_24h_pct",
            "fee_apr_7d_pct", "fee_apr_30d_pct", "claimed_fees_usd", "gas_cost_usd",
            "rebalance_cost_usd", "data_status", "methodology_json",
        ]
        with self._connect() as conn:
            cur = conn.execute(
                f"INSERT INTO position_performance_snapshots ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
                [item.get(k) for k in columns],
            )
            return int(cur.lastrowid)

    def list_position_performance(self, wallet: str | None = None,
                                  position_id: str | None = None, limit: int = 100) -> list[dict]:
        query = "SELECT * FROM position_performance_snapshots WHERE 1=1"
        params: list = []
        if wallet:
            query += " AND lower(wallet_address)=lower(?)"
            params.append(wallet)
        if position_id:
            query += " AND position_id=?"
            params.append(position_id)
        query += " ORDER BY observed_at DESC,id DESC LIMIT ?"
        params.append(limit)
        with self._connect() as conn:
            return [dict(row) for row in conn.execute(query, params).fetchall()]


    def add_lp_position_event(self, item: dict) -> int:
        columns = [
            "chain_id", "manager_address", "position_id", "token_id", "wallet_address",
            "tx_hash", "block_number", "block_hash", "transaction_index", "log_index",
            "event_type", "recipient", "amount0_raw", "amount1_raw", "liquidity_raw",
            "raw_log_json",
        ]
        with self._connect() as conn:
            conn.execute(
                f"INSERT OR IGNORE INTO lp_position_events ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
                [item.get(k) for k in columns],
            )
            row = conn.execute(
                "SELECT id FROM lp_position_events WHERE chain_id=? AND tx_hash=? AND log_index=?",
                (item["chain_id"], item["tx_hash"], item["log_index"]),
            ).fetchone()
            return int(row["id"])

    def list_lp_position_events(self, position_id: str | None = None,
                                wallet: str | None = None, limit: int = 20000) -> list[dict]:
        query = "SELECT * FROM lp_position_events WHERE 1=1"
        params: list = []
        if position_id:
            query += " AND position_id=?"
            params.append(position_id)
        if wallet:
            query += " AND lower(wallet_address)=lower(?)"
            params.append(wallet)
        query += " ORDER BY block_number, transaction_index, log_index LIMIT ?"
        params.append(limit)
        with self._connect() as conn:
            return [dict(row) for row in conn.execute(query, params).fetchall()]

    def add_lp_transaction_cost(self, item: dict) -> int:
        columns = [
            "chain_id", "tx_hash", "wallet_address", "tx_from", "tx_to",
            "block_number", "block_hash", "block_timestamp", "receipt_status",
            "gas_used", "effective_gas_price_wei", "l1_fee_wei", "total_fee_wei",
            "native_symbol", "position_ids_json", "allocation_method", "data_status",
            "raw_receipt_json",
        ]
        with self._connect() as conn:
            conn.execute(
                f"INSERT OR IGNORE INTO lp_transaction_costs ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
                [item.get(k) for k in columns],
            )
            row = conn.execute(
                "SELECT id FROM lp_transaction_costs WHERE chain_id=? AND tx_hash=?",
                (item["chain_id"], item["tx_hash"]),
            ).fetchone()
            return int(row["id"])

    def list_lp_transaction_costs(self, wallet: str, limit: int = 5000) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM lp_transaction_costs WHERE lower(wallet_address)=lower(?) ORDER BY block_number,tx_hash LIMIT ?",
                (wallet, limit),
            ).fetchall()
            return [dict(row) for row in rows]

    def add_lp_position_accounting_snapshot(self, item: dict) -> int:
        columns = [
            "position_id", "wallet_address", "chain_id", "block_number", "block_hash",
            "observed_at", "token0_address", "token1_address", "token0_symbol",
            "token1_symbol", "liquidity_contributed0_raw", "liquidity_contributed1_raw",
            "principal_owed0_raw", "principal_owed1_raw", "principal_recovered0_raw",
            "principal_recovered1_raw", "realized_fees0_raw", "realized_fees1_raw",
            "realized_fees_usd", "principal_recovered_usd", "gas_cost_native_wei",
            "gas_cost_usd", "net_pnl_usd", "accounting_status", "methodology_json",
        ]
        with self._connect() as conn:
            cur = conn.execute(
                f"INSERT INTO lp_position_accounting_snapshots ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
                [item.get(k) for k in columns],
            )
            return int(cur.lastrowid)

    def list_lp_position_accounting(self, wallet: str | None = None,
                                    position_id: str | None = None, limit: int = 500) -> list[dict]:
        query = "SELECT * FROM lp_position_accounting_snapshots WHERE 1=1"
        params: list = []
        if wallet:
            query += " AND lower(wallet_address)=lower(?)"
            params.append(wallet)
        if position_id:
            query += " AND position_id=?"
            params.append(position_id)
        query += " ORDER BY observed_at DESC,id DESC LIMIT ?"
        params.append(limit)
        with self._connect() as conn:
            return [dict(row) for row in conn.execute(query, params).fetchall()]

    def token_price_near(self, chain_id: str, token_address: str,
                         observed_at: str, max_skew_seconds: int = 300) -> dict | None:
        with self._connect() as conn:
            rows = conn.execute(
                """SELECT * FROM token_price_observations
                WHERE chain_id=? AND lower(token_address)=lower(?)""",
                (str(chain_id), token_address),
            ).fetchall()
            if not rows:
                return None
            from datetime import datetime
            target = datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
            candidates = []
            for row in rows:
                item = dict(row)
                stamp = datetime.fromisoformat(item["observed_at"].replace("Z", "+00:00"))
                skew = abs((stamp - target).total_seconds())
                if skew <= max_skew_seconds:
                    candidates.append((skew, item))
            return None if not candidates else min(candidates, key=lambda x: x[0])[1]


    def add_lp_position_event(self, item: dict) -> int:
        columns = [
            "chain_id", "manager_address", "position_id", "token_id", "wallet_address",
            "tx_hash", "block_number", "block_hash", "transaction_index", "log_index",
            "event_type", "from_address", "recipient", "amount0_raw", "amount1_raw",
            "liquidity_raw", "raw_log_json",
        ]
        with self._connect() as conn:
            conn.execute(
                f"INSERT OR IGNORE INTO lp_position_events ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
                [item.get(k) for k in columns],
            )
            row = conn.execute(
                "SELECT id FROM lp_position_events WHERE chain_id=? AND tx_hash=? AND log_index=?",
                (item["chain_id"], item["tx_hash"], item["log_index"]),
            ).fetchone()
            return int(row["id"])

    def list_lp_position_events(self, position_id: str | None = None,
                                wallet: str | None = None, limit: int = 20000) -> list[dict]:
        query = "SELECT * FROM lp_position_events WHERE 1=1"
        params: list = []
        if position_id:
            query += " AND position_id=?"
            params.append(position_id)
        if wallet:
            query += " AND lower(wallet_address)=lower(?)"
            params.append(wallet)
        query += " ORDER BY block_number, transaction_index, log_index LIMIT ?"
        params.append(limit)
        with self._connect() as conn:
            return [dict(row) for row in conn.execute(query, params).fetchall()]

    def add_lp_transaction_cost(self, item: dict) -> int:
        columns = [
            "chain_id", "tx_hash", "wallet_address", "tx_from", "tx_to",
            "block_number", "block_hash", "block_timestamp", "receipt_status",
            "gas_used", "effective_gas_price_wei", "l1_fee_wei", "total_fee_wei",
            "native_symbol", "position_ids_json", "allocation_method", "data_status",
            "raw_receipt_json",
        ]
        with self._connect() as conn:
            conn.execute(
                f"INSERT OR IGNORE INTO lp_transaction_costs ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
                [item.get(k) for k in columns],
            )
            row = conn.execute(
                "SELECT id FROM lp_transaction_costs WHERE chain_id=? AND tx_hash=?",
                (item["chain_id"], item["tx_hash"]),
            ).fetchone()
            return int(row["id"])

    def list_lp_transaction_costs(self, wallet: str, limit: int = 5000) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM lp_transaction_costs WHERE lower(wallet_address)=lower(?) ORDER BY block_number,tx_hash LIMIT ?",
                (wallet, limit),
            ).fetchall()
            return [dict(row) for row in rows]

    def add_lp_position_accounting_snapshot(self, item: dict) -> int:
        columns = [
            "position_id", "wallet_address", "chain_id", "block_number", "block_hash",
            "observed_at", "token0_address", "token1_address", "token0_symbol",
            "token1_symbol", "liquidity_contributed0_raw", "liquidity_contributed1_raw",
            "principal_owed0_raw", "principal_owed1_raw", "principal_recovered0_raw",
            "principal_recovered1_raw", "realized_fees0_raw", "realized_fees1_raw",
            "realized_fees_usd", "principal_recovered_usd", "gas_cost_native_wei",
            "gas_cost_usd", "net_pnl_usd", "accounting_status", "methodology_json",
        ]
        with self._connect() as conn:
            cur = conn.execute(
                f"INSERT INTO lp_position_accounting_snapshots ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
                [item.get(k) for k in columns],
            )
            return int(cur.lastrowid)

    def list_lp_position_accounting(self, wallet: str | None = None,
                                    position_id: str | None = None, limit: int = 500) -> list[dict]:
        query = "SELECT * FROM lp_position_accounting_snapshots WHERE 1=1"
        params: list = []
        if wallet:
            query += " AND lower(wallet_address)=lower(?)"
            params.append(wallet)
        if position_id:
            query += " AND position_id=?"
            params.append(position_id)
        query += " ORDER BY observed_at DESC,id DESC LIMIT ?"
        params.append(limit)
        with self._connect() as conn:
            return [dict(row) for row in conn.execute(query, params).fetchall()]

    def token_price_near(self, chain_id: str, token_address: str,
                         observed_at: str, max_skew_seconds: int = 300) -> dict | None:
        from datetime import datetime
        target = datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM token_price_observations WHERE chain_id=? AND lower(token_address)=lower(?)",
                (str(chain_id), token_address),
            ).fetchall()
        candidates = []
        for row in rows:
            item = dict(row)
            stamp = datetime.fromisoformat(item["observed_at"].replace("Z", "+00:00"))
            skew = abs((stamp - target).total_seconds())
            if skew <= max_skew_seconds:
                candidates.append((skew, item))
        return None if not candidates else min(candidates, key=lambda x: x[0])[1]

    def add_alert_if_not_recent(self, item: AlertEvent, cooldown_minutes: int = 360) -> int | None:
        """Insert once per dedupe key during a cooldown; return None when suppressed."""
        from datetime import datetime, timedelta, timezone
        item.validate()
        cutoff = (datetime.now(timezone.utc) - timedelta(minutes=cooldown_minutes)).isoformat().replace("+00:00", "Z")
        data = to_dict(item)
        with self._connect() as conn:
            exists = conn.execute(
                "SELECT id FROM alert_events WHERE dedupe_key=? AND observed_at>=? ORDER BY id DESC LIMIT 1",
                (data["dedupe_key"], cutoff),
            ).fetchone()
            if exists:
                return None
            cur = conn.execute(
                """INSERT INTO alert_events
                (dedupe_key,severity,title,message,observed_at,evidence_json,recommended_checks_json,delivery_status)
                VALUES (?,?,?,?,?,?,?,'pending')""",
                (data["dedupe_key"], data["severity"], data["title"], data["message"],
                 data["observed_at"], json.dumps(data["evidence"], ensure_ascii=False),
                 json.dumps(data["recommended_checks"], ensure_ascii=False)),
            )
            return int(cur.lastrowid)

    def list_pending_alerts(self, limit: int = 100) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM alert_events WHERE delivery_status='pending' ORDER BY observed_at,id LIMIT ?",
                (limit,),
            ).fetchall()
            result = []
            for row in rows:
                item = dict(row)
                item["evidence"] = json.loads(item.pop("evidence_json"))
                item["recommended_checks"] = json.loads(item.pop("recommended_checks_json"))
                result.append(item)
            return result

    def set_alert_delivery_status(self, alert_id: int, status: str) -> None:
        if status not in {"sent", "pending"} and not status.startswith("failed:"):
            raise ValueError("invalid alert delivery status")
        with self._connect() as conn:
            conn.execute("UPDATE alert_events SET delivery_status=? WHERE id=?", (status[:240], alert_id))

    def list_xlayer_positions(self, wallet: str, limit: int = 100) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """SELECT p.* FROM xlayer_position_snapshots p
                JOIN (SELECT token_id, MAX(id) AS latest_id FROM xlayer_position_snapshots
                     WHERE lower(wallet_address)=lower(?) GROUP BY token_id) x
                ON p.id=x.latest_id ORDER BY p.block_number DESC LIMIT ?""",
                (wallet, limit),
            ).fetchall()
            return [dict(row) for row in rows]

