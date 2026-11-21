#!/usr/bin/env python3
"""Offline fixtures for X Layer token/pool scanner pure helpers."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(filename))
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def main() -> int:
    token = load("token_scanner", "quet-token-xlayer.py")
    pool = load("pool_scanner", "kham-pha-pool-uniswap-v3-xlayer.py")
    bootstrap = load("wallet_bootstrap", "khoi-tao-vi-xlayer.py")
    positions = load("position_scanner", "quet-vi-the-uniswap-v3-xlayer.py")

    wallet = "0x" + "51f9d30f78239e53f14c1e248fd29e6966ce5287"
    assert bootstrap.normalize_address("XKO51f9d30f78239e53f14c1e248fd29e6966ce5287") == wallet
    assert bootstrap.normalize_address(wallet) == wallet
    assert token.address_word(wallet) == wallet[2:].rjust(64, "0")
    assert token.decode_string("0x" + "55534443".ljust(64, "0")) == "USDC"
    assert pool.address_from_result("0x" + "0" * 24 + "a" * 40) == "0x" + "a" * 40
    assert positions.signed24((1 << 24) - 1) == -1
    assert positions.topic_address(wallet) == "0x" + wallet[2:].rjust(64, "0")

    rejected = False
    try:
        token.address_word("0x1234")
    except ValueError:
        rejected = True
    assert rejected

    print("X Layer scanner fixtures passed: 8/8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
