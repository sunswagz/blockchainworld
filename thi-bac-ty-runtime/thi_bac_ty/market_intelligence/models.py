"""Hợp đồng dữ liệu Market Intelligence.

Nguyên tắc: không biết khác với bằng không; mọi số liệu phải có nguồn và thời
điểm; forecast là bản ghi có thời hạn và không bị ghi đè.
"""
from __future__ import annotations

import datetime as dt
import math
from dataclasses import dataclass, field
from typing import Literal


DataStatus = Literal["fresh", "stale", "missing", "invalid", "provisional"]
ForecastStatus = Literal["draft", "active", "expired", "invalidated", "evaluated"]
Bias = Literal["bullish", "bearish", "neutral", "mixed", "unknown"]
Regime = Literal[
    "accumulation", "expansion", "distribution", "contraction",
    "transition", "unknown",
]
Horizon = Literal["1D", "1W", "1M", "3M", "1Y"]


def _parse_time(value: str) -> dt.datetime:
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include timezone")
    return parsed.astimezone(dt.timezone.utc)


@dataclass(frozen=True)
class MarketObservation:
    """Một điểm dữ liệu có provenance; value=None nghĩa là chưa biết."""

    metric: str
    value: float | None
    unit: str
    source: str
    observed_at: str
    fetched_at: str
    status: DataStatus = "fresh"
    reason: str | None = None
    metadata: dict = field(default_factory=dict)

    def validate(self) -> None:
        if not self.metric.strip():
            raise ValueError("metric is required")
        if not self.unit.strip():
            raise ValueError("unit is required")
        if not self.source.strip():
            raise ValueError("source is required")
        observed = _parse_time(self.observed_at)
        fetched = _parse_time(self.fetched_at)
        if fetched < observed:
            raise ValueError("fetched_at cannot precede observed_at")
        if self.value is not None and not math.isfinite(self.value):
            raise ValueError("value must be finite or None")
        if self.status == "missing" and self.value is not None:
            raise ValueError("missing observation must have value=None")
        if self.status == "invalid" and not self.reason:
            raise ValueError("invalid observation requires a reason")
        if self.status == "missing" and not self.reason:
            raise ValueError("missing observation requires a reason")


@dataclass(frozen=True)
class Scenario:
    """Kịch bản phải có điều kiện kích hoạt và điều kiện vô hiệu hóa."""

    name: Literal["bullish", "base", "bearish"]
    thesis: str
    triggers: tuple[str, ...]
    invalidation_conditions: tuple[str, ...]
    target_zones: tuple[str, ...] = ()

    def validate(self) -> None:
        if not self.thesis.strip():
            raise ValueError("scenario thesis is required")
        if not self.triggers:
            raise ValueError("scenario requires at least one trigger")
        if not self.invalidation_conditions:
            raise ValueError("scenario requires invalidation conditions")


@dataclass(frozen=True)
class Forecast:
    """Forecast append-only; confidence/probabilities chỉ khi đã hiệu chỉnh."""

    forecast_id: str
    model_version: str
    created_at: str
    as_of: str
    valid_until: str
    asset_or_index: str
    horizon: Horizon
    timeframe_basis: tuple[str, ...]
    regime: Regime
    directional_bias: Bias
    scenarios: tuple[Scenario, ...]
    evidence_ids: tuple[str, ...]
    status: ForecastStatus = "draft"
    confidence: float | None = None
    probabilities: dict[str, float] | None = None
    supersedes: str | None = None

    def validate(self) -> None:
        if not self.forecast_id.strip() or not self.model_version.strip():
            raise ValueError("forecast_id and model_version are required")
        created = _parse_time(self.created_at)
        as_of = _parse_time(self.as_of)
        valid_until = _parse_time(self.valid_until)
        if as_of > created:
            raise ValueError("as_of cannot be after forecast creation")
        if valid_until <= as_of:
            raise ValueError("valid_until must be after as_of")
        if not self.asset_or_index.strip():
            raise ValueError("asset_or_index is required")
        if not self.timeframe_basis:
            raise ValueError("timeframe_basis is required")
        if self.confidence is not None and not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be in [0, 1]")
        if self.probabilities is not None:
            required = {"bullish", "base", "bearish"}
            if set(self.probabilities) != required:
                raise ValueError("probabilities must contain bullish, base, bearish")
            values = tuple(self.probabilities.values())
            if any(not math.isfinite(v) or v < 0 or v > 1 for v in values):
                raise ValueError("probabilities must be finite and in [0, 1]")
            if abs(sum(values) - 1.0) > 1e-6:
                raise ValueError("probabilities must sum to 1")
        names = {scenario.name for scenario in self.scenarios}
        if names != {"bullish", "base", "bearish"}:
            raise ValueError("forecast requires bullish, base and bearish scenarios")
        for scenario in self.scenarios:
            scenario.validate()
        if self.status in ("active", "evaluated") and not self.evidence_ids:
            raise ValueError("active/evaluated forecast requires evidence_ids")
