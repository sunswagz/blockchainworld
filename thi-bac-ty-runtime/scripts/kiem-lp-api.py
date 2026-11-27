#!/usr/bin/env python3
"""Offline HTTP smoke tests for the read-only LP Intelligence API."""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory(prefix="lp-api-test-") as tmp:
    os.environ["LP_INTELLIGENCE_DB"] = str(Path(tmp) / "api.sqlite")
    from fastapi.testclient import TestClient
    from lp_intelligence.api import app

    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

        for endpoint in (
            "/api/v1/pools",
            "/api/v1/positions",
            "/api/v1/position-fees",
            "/api/v1/alerts",
            "/api/v1/pool-activity",
            "/api/v1/position-performance",
            "/api/v1/position-accounting",
            "/api/v1/chains",
            "/api/v1/dex-protocols",
        ):
            result = client.get(endpoint)
            assert result.status_code == 200, (endpoint, result.text)
            assert "data" in result.json() and "count" in result.json(), endpoint

        chains = client.get("/api/v1/chains?family=evm").json()
        assert chains["count"] > 10
        assert all(item["family"] == "evm" for item in chains["data"])

        protocols = client.get("/api/v1/dex-protocols?chain_key=base").json()
        assert any(item["key"] == "uniswap-v3-base" for item in protocols["data"])

        wallet = "0x" + "1" * 40
        monitor = client.get(f"/api/v1/wallet-monitor/{wallet}")
        assert monitor.status_code == 200
        assert monitor.json()["wallet"] == wallet

print("LP Intelligence API smoke tests passed: health, read endpoints, filters and wallet monitor route.")
