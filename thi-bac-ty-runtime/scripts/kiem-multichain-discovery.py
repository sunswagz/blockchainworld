#!/usr/bin/env python3
"""Offline checks for multi-chain candidate discovery."""
from pathlib import Path
import sys
import runpy

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lp_intelligence.chain_registry import CHAINS, validate_registry
from lp_intelligence.providers.geckoterminal import parse_pool_candidate

validate_registry()
assert len(CHAINS) >= 55
assert len({c.chain_index for c in CHAINS if c.family == "evm"}) == len([c for c in CHAINS if c.family == "evm"])
module = runpy.run_path(str(Path(__file__).with_name("kham-pha-dex-da-chuoi.py")))
mapping = module["GECKO_NETWORKS"]
assert {"ethereum", "base", "bnb", "xlayer"}.issubset(mapping)
assert "solana" not in mapping
assert mapping["base"] == "base" and mapping["xlayer"] == "x-layer"
payload = {"data": [{"id": "base_0x" + "1"*40, "attributes": {"address": "0x" + "1"*40, "name": "WETH / USDC", "reserve_in_usd": "123.4", "volume_usd": {"h24": "9.5"}}, "relationships": {"base_token": {"data": {"id": "token_0x" + "2"*40}}, "quote_token": {"data": {"id": "token_0x" + "3"*40}}, "dex": {"data": {"id": "dex_test"}}}}], "included": [{"id": "token_0x" + "2"*40, "attributes": {"address": "0x" + "2"*40}}, {"id": "token_0x" + "3"*40, "attributes": {"address": "0x" + "3"*40}}, {"id": "dex_test", "attributes": {"identifier": "test-dex"}}]}
candidate = parse_pool_candidate(payload["data"][0], {x["id"]: x for x in payload["included"]}, "https://example.test/pool")
assert candidate.address == "0x" + "1"*40 and candidate.dex_id == "test-dex" and candidate.reserve_in_usd == 123.4
print("OK: chain registry, curated GeckoTerminal mapping and pool parser fixtures")
