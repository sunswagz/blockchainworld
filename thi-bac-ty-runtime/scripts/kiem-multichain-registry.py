#!/usr/bin/env python3
"""Offline checks for the multi-chain registry."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lp_intelligence.chain_registry import CHAINS, list_chains, validate_registry
from lp_intelligence.dex_registry import DEX_PROTOCOLS, list_protocols, validate_registry as validate_dex

validate_registry()
validate_dex()
assert len({c.chain_index for c in CHAINS if c.family == "evm"}) == len([c for c in CHAINS if c.family == "evm"])
assert {c.key for c in CHAINS if c.scan_status == "adapter_available"} == {"base", "xlayer"}
assert any(p.key == "uniswap-v3-base" and p.deployment_verified for p in DEX_PROTOCOLS)
assert any(p.discovery_status == "discovery_required" for p in DEX_PROTOCOLS)
assert len(list_chains(family="evm")) > 10
assert list_protocols(chain_key="base")
print(f"OK: {len(CHAINS)} chain records, {len(DEX_PROTOCOLS)} DEX protocol records; no unsupported deployment is marked live.")
