"""Canonical provenance-aware contracts for LP Intelligence.

Unknown is represented by None, never by zero. Timestamps must carry
an explicit timezone and are normalized to UTC for storage.
"""
from __future__ import annotations

import datetime as dt
import math
from dataclasses import asdict, dataclass, field
from typing import Literal

DataStatus = Literal["fresh", "stale", "missing", "invalid", "provisional"]
Severity = Literal["info", "warning", "high", "critical"]


def parse_utc(value: str) -> dt.datetime:
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include timezone")
    return parsed.astimezone(dt.timezone.utc)


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _finite_or_none(value: float | None, field_name: str) -> None:
    if value is not None and not math.isfinite(value):
        raise ValueError(f"{field_name} must be finite or None")


@dataclass(frozen=True)
class Observation:
    metric: str
    value: float | None
    unit: str
    source: str
    source_url: str
    observed_at: str
    fetched_at: str
    status: DataStatus = "fresh"
    reason: str | None = None
    metadata: dict = field(default_factory=dict)

    def validate(self) -> None:
        if not self.metric.strip() or not self.unit.strip() or not self.source.strip():
            raise ValueError("metric, unit and source are required")
        observed, fetched = parse_utc(self.observed_at), parse_utc(self.fetched_at)
        if fetched < observed:
            raise ValueError("fetched_at cannot precede observed_at")
        _finite_or_none(self.value, "value")
        if self.status == "missing" and self.value is not None:
            raise ValueError("missing observation must have value=None")
        if self.status in ("missing", "invalid") and not self.reason:
            raise ValueError("missing/invalid observations require a reason")


@dataclass(frozen=True)
class PoolSnapshot:
    pool_id: str
    chain_id: str
    chain_name: str
    protocol: str
    version: str
    pool_address: str
    token0_address: str
    token0_symbol: str
    token1_address: str
    token1_symbol: str
    observed_at: str
    fetched_at: str
    source: str
    source_url: str
    data_status: DataStatus = "fresh"
    tvl_usd: float | None = None
    volume_24h_usd: float | None = None
    fees_24h_usd: float | None = None
    fee_apr_pct: float | None = None
    incentive_apr_pct: float | None = None
    spot_price: float | None = None
    current_tick: int | None = None
    fee_tier_bps: float | None = None
    raw_ref: str | None = None

    def validate(self) -> None:
        required = (self.pool_id, self.chain_id, self.chain_name, self.protocol,
                    self.version, self.pool_address, self.token0_address,
                    self.token0_symbol, self.token1_address, self.token1_symbol,
                    self.source, self.source_url)
        if any(not str(v).strip() for v in required):
            raise ValueError("pool identity and provenance fields are required")
        if parse_utc(self.fetched_at) < parse_utc(self.observed_at):
            raise ValueError("fetched_at cannot precede observed_at")
        for name in ("tvl_usd", "volume_24h_usd", "fees_24h_usd",
                     "fee_apr_pct", "incentive_apr_pct", "spot_price", "fee_tier_bps"):
            _finite_or_none(getattr(self, name), name)
        for name in ("tvl_usd", "volume_24h_usd", "fees_24h_usd"):
            value = getattr(self, name)
            if value is not None and value < 0:
                raise ValueError(f"{name} cannot be negative")


@dataclass(frozen=True)
class PositionSnapshot:
    position_id: str
    wallet_address: str
    chain_id: str
    protocol: str
    version: str
    pool_id: str
    observed_at: str
    fetched_at: str
    source: str
    source_url: str
    data_status: DataStatus = "fresh"
    liquidity_raw: str | None = None
    tick_lower: int | None = None
    tick_upper: int | None = None
    current_tick: int | None = None
    principal_usd: float | None = None
    unclaimed_fees_usd: float | None = None
    claimed_fees_usd: float | None = None
    in_range: bool | None = None
    raw_ref: str | None = None

    def validate(self) -> None:
        required = (self.position_id, self.wallet_address, self.chain_id,
                    self.protocol, self.version, self.pool_id, self.source, self.source_url)
        if any(not str(v).strip() for v in required):
            raise ValueError("position identity and provenance fields are required")
        if self.tick_lower is not None and self.tick_upper is not None:
            if self.tick_lower >= self.tick_upper:
                raise ValueError("tick_lower must be less than tick_upper")
        if parse_utc(self.fetched_at) < parse_utc(self.observed_at):
            raise ValueError("fetched_at cannot precede observed_at")
        for name in ("principal_usd", "unclaimed_fees_usd", "claimed_fees_usd"):
            _finite_or_none(getattr(self, name), name)


@dataclass(frozen=True)
class AlertEvent:
    dedupe_key: str
    severity: Severity
    title: str
    message: str
    observed_at: str
    evidence: tuple[dict, ...] = ()
    recommended_checks: tuple[str, ...] = ()

    def validate(self) -> None:
        if not self.dedupe_key.strip() or not self.title.strip() or not self.message.strip():
            raise ValueError("alert key, title and message are required")
        parse_utc(self.observed_at)
        if self.severity not in ("info", "warning", "high", "critical"):
            raise ValueError("unknown severity")


def to_dict(value) -> dict:
    return asdict(value)
