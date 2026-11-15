"""Self-test offline cho hợp đồng Market Intelligence."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from thi_bac_ty.market_intelligence.models import (  # noqa: E402
    Forecast, MarketObservation, Scenario,
)

NOW = "2026-11-16T00:00:00Z"
LATER = "2026-11-16T01:00:00Z"


def scenario(name: str) -> Scenario:
    return Scenario(
        name=name,
        thesis=f"Điều kiện {name}",
        triggers=("trigger-a",),
        invalidation_conditions=("invalidation-a",),
    )


def main() -> int:
    passed = 0

    def check(label: str, fn) -> None:
        nonlocal passed
        try:
            fn()
            passed += 1
            print(f"  OK  {label}")
        except Exception as exc:  # noqa: BLE001
            print(f"  FAIL {label}: {exc}")
            raise

    check("observation có provenance", lambda: MarketObservation(
        metric="BTCUSDT.close", value=65000.0, unit="USD",
        source="fixture", observed_at=NOW, fetched_at=LATER,
    ).validate())

    check("missing không được biến thành zero", lambda: MarketObservation(
        metric="TOTAL2", value=None, unit="USD",
        source="fixture", observed_at=NOW, fetched_at=LATER,
        status="missing", reason="fixture intentionally missing",
    ).validate())

    check("forecast có ba kịch bản", lambda: Forecast(
        forecast_id="fixture-001", model_version="0.1.0",
        created_at=LATER, as_of=NOW, valid_until="2026-11-17T00:00:00Z",
        asset_or_index="BTCUSDT", horizon="1D", timeframe_basis=("4h", "1d"),
        regime="transition", directional_bias="mixed",
        scenarios=(scenario("bullish"), scenario("base"), scenario("bearish")),
        evidence_ids=("obs-001",), status="active",
    ).validate())

    def reject_naive_timestamp() -> None:
        MarketObservation(
            metric="BTC", value=1.0, unit="USD", source="fixture",
            observed_at="2026-11-16T00:00:00", fetched_at=LATER,
        ).validate()

    def reject_bad_probabilities() -> None:
        Forecast(
            forecast_id="fixture-002", model_version="0.1.0",
            created_at=LATER, as_of=NOW, valid_until="2026-11-17T00:00:00Z",
            asset_or_index="BTCUSDT", horizon="1D", timeframe_basis=("1d",),
            regime="unknown", directional_bias="unknown",
            scenarios=(scenario("bullish"), scenario("base"), scenario("bearish")),
            evidence_ids=("obs-001",), probabilities={
                "bullish": 0.5, "base": 0.5, "bearish": 0.5,
            },
        ).validate()

    for label, fn in (
        ("reject timestamp without timezone", reject_naive_timestamp),
        ("reject probabilities not summing to one", reject_bad_probabilities),
    ):
        try:
            fn()
        except ValueError:
            passed += 1
            print(f"  OK  {label}")
        else:
            print(f"  FAIL {label}")
            return 1

    print(f"Market Intelligence checks passed: {passed}/5")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
