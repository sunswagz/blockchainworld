"""Offline fixture tests for the Uniswap V3/Base collector.

Run from thi-bac-ty-runtime:
    python scripts/kiem-lp-collector-fixtures.py
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lp_intelligence.collectors.uniswap_v3_base import (
    FACTORY, POOL_SELECTORS, USDC, WETH, collect_uniswap_v3_base,
)
from lp_intelligence.evm import (
    decode_int24_word, decode_uint, factory_get_pool_calldata,
)
from lp_intelligence.providers.geckoterminal import PoolCandidate, parse_pool_candidate
from lp_intelligence.storage import SQLiteStore

POOL = "0x" + "a" * 40
NOW_CANDIDATE = PoolCandidate(
    address=POOL,
    name="WETH / USDC 0.05%",
    dex_id="uniswap-v3",
    base_token_address=WETH.lower(),
    quote_token_address=USDC.lower(),
    base_token_price_usd=3200.0,
    quote_token_price_usd=1.0,
    reserve_in_usd=12_000_000.0,
    volume_24h_usd=3_000_000.0,
    source_url="https://api.geckoterminal.com/api/v2/networks/base/tokens/example/pools",
)


def word(value: int) -> str:
    return format(value, "064x")


class FakeGecko:
    def token_pools(self, network: str, token_address: str):
        assert network == "base"
        assert token_address.lower() == WETH.lower()
        return [NOW_CANDIDATE], {"data": [{"id": "fixture"}], "included": []}


class FakeRpc:
    def eth_call(self, to: str, data: str, block_tag: str = "latest") -> str:
        if to.lower() == FACTORY.lower():
            # getPool() confirms this fixture pool for the 500 fee tier.
            if data.startswith("0x1698ee82") and data.endswith(word(500)):
                return "0x" + "0" * 24 + POOL[2:]
            return "0x" + "0" * 64
        if to.lower() == WETH.lower() and data == "0x313ce567":
            return "0x" + word(18)
        if to.lower() == USDC.lower() and data == "0x313ce567":
            return "0x" + word(6)
        if data == POOL_SELECTORS["token0"]:
            return "0x" + "0" * 24 + WETH[2:].lower()
        if data == POOL_SELECTORS["token1"]:
            return "0x" + "0" * 24 + USDC[2:].lower()
        if data == POOL_SELECTORS["slot0"]:
            return "0x" + word(2**96) + word(0) + word(0) + word(0) + word(0) + word(0) + word(0)
        if data == POOL_SELECTORS["liquidity"]:
            return "0x" + word(123456789)
        raise AssertionError(f"Unexpected eth_call: {to} {data}")

    def get_block_number(self):
        return 10

    def get_block(self, block_number):
        return {"hash": "0x" + "b" * 64, "timestamp": hex(100000 + block_number * 2)}

    def get_logs(self, *, address, from_block, to_block, topics):
        return []


def main() -> int:
    count = 0

    def check(label: str, condition: bool) -> None:
        nonlocal count
        if not condition:
            raise AssertionError(label)
        count += 1
        print("  ✓", label)

    call = factory_get_pool_calldata(USDC, WETH, 500)
    check("factory getPool calldata has canonical selector", call.startswith("0x1698ee82"))
    check("factory getPool calldata sorts token addresses", call[10:74] < call[74:138])
    check("signed int24 decoder handles negative ticks",
          decode_int24_word("0x" + word((1 << 24) - 7)) == -7)
    check("uint decoder reads ABI words", decode_uint("0x" + word(123) + word(456), 1) == 456)

    included = {
        "token_base_8453_" + WETH.lower(): {"attributes": {"address": WETH.lower()}},
        "token_base_8453_" + USDC.lower(): {"attributes": {"address": USDC.lower()}},
        "dex_uniswap-v3": {"attributes": {"identifier": "uniswap-v3"}},
    }
    item = {
        "id": "base_" + POOL,
        "attributes": {"address": POOL, "name": "WETH / USDC", "reserve_in_usd": "99",
                       "volume_usd": {"h24": "10"}},
        "relationships": {
            "base_token": {"data": {"id": "token_base_8453_" + WETH.lower()}},
            "quote_token": {"data": {"id": "token_base_8453_" + USDC.lower()}},
            "dex": {"data": {"id": "dex_uniswap-v3"}},
        },
    }
    parsed = parse_pool_candidate(item, included, "https://example.invalid")
    check("GeckoTerminal parser resolves pool and token addresses",
          parsed.address == POOL and parsed.base_token_address == WETH.lower()
          and parsed.quote_token_address == USDC.lower())

    with tempfile.TemporaryDirectory(prefix="lp-collector-fixture-") as tmp:
        store = SQLiteStore(Path(tmp) / "fixture.sqlite")
        store.initialize()
        result = collect_uniswap_v3_base(
            store=store, gecko=FakeGecko(), rpc=FakeRpc()
        )
        check("collector confirms factory pool and fee tier", result["fee_tier"] == 500)
        check("collector reads on-chain tick and liquidity",
              result["current_tick"] == 0 and result["liquidity_raw"] == "123456789")
        check("collector appends a verified pool snapshot", len(store.list_pools()) == 1)
        pool = store.list_pools()[0]
        check("collector leaves fees and APR unknown, not fabricated",
              pool["fees_24h_usd"] is None and pool["fee_apr_pct"] is None)
        check("collector archives raw payload provenance", pool["raw_ref"] == "1")

    print(f"LP collector fixture tests passed: {count}/{count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
