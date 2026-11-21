"""Minimal read-only JSON-RPC helpers for EVM calls; no signing support."""
from __future__ import annotations
import itertools
from typing import Any
import httpx

_counter = itertools.count(1)

class JsonRpcError(RuntimeError):
    pass

class JsonRpcClient:
    def __init__(self, url: str, timeout: float = 15.0, client: httpx.Client | None = None):
        if not url.startswith("https://") and not url.startswith("http://127.0.0.1"):
            raise ValueError("RPC URL must use HTTPS (or loopback for local testing)")
        self.url = url
        self._client = client or httpx.Client(timeout=timeout)
        self._owns_client = client is None

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def call(self, method: str, params: list[Any]) -> Any:
        response = self._client.post(
            self.url,
            json={"jsonrpc": "2.0", "id": next(_counter), "method": method, "params": params},
        )
        response.raise_for_status()
        payload = response.json()
        if payload.get("error"):
            raise JsonRpcError(str(payload["error"]))
        if "result" not in payload:
            raise JsonRpcError("JSON-RPC response is missing result")
        return payload["result"]

    def eth_call(self, to: str, data: str, block_tag: str = "latest") -> str:
        result = self.call("eth_call", [{"to": to, "data": data}, block_tag])
        if not isinstance(result, str) or not result.startswith("0x"):
            raise JsonRpcError("eth_call returned malformed data")
        return result

    def get_block_number(self) -> int:
        result = self.call("eth_blockNumber", [])
        if not isinstance(result, str) or not result.startswith("0x"):
            raise JsonRpcError("eth_blockNumber returned malformed data")
        return int(result, 16)

    def get_block(self, block_number: int) -> dict[str, Any]:
        result = self.call("eth_getBlockByNumber", [hex(block_number), False])
        if not isinstance(result, dict) or not result.get("hash") or not result.get("timestamp"):
            raise JsonRpcError("eth_getBlockByNumber returned incomplete block")
        return result

    def get_logs(self, *, address: str, from_block: int, to_block: int, topics: list[Any]) -> list[dict[str, Any]]:
        result = self.call("eth_getLogs", [{
            "address": address, "fromBlock": hex(from_block),
            "toBlock": hex(to_block), "topics": topics,
        }])
        if not isinstance(result, list):
            raise JsonRpcError("eth_getLogs returned malformed data")
        return result


def _word_address(address: str) -> str:
    raw = address.lower().removeprefix("0x")
    if len(raw) != 40 or any(c not in "0123456789abcdef" for c in raw):
        raise ValueError("invalid EVM address")
    return raw.rjust(64, "0")

def factory_get_pool_calldata(token_a: str, token_b: str, fee: int) -> str:
    if not 0 <= fee < 2**24:
        raise ValueError("fee tier must fit uint24")
    token0, token1 = sorted((token_a.lower(), token_b.lower()))
    return "0x1698ee82" + _word_address(token0) + _word_address(token1) + format(fee, "064x")

def decode_uint(result: str, word_index: int = 0) -> int:
    raw = result.removeprefix("0x")
    start = word_index * 64
    word = raw[start:start + 64]
    if len(word) != 64:
        raise ValueError("eth_call result does not contain requested ABI word")
    return int(word, 16)

def decode_int24_word(result: str, word_index: int = 0) -> int:
    value = decode_uint(result, word_index) & ((1 << 24) - 1)
    return value - (1 << 24) if value & (1 << 23) else value

def encode_selector_call(selector: str) -> str:
    if len(selector) != 10 or not selector.startswith("0x"):
        raise ValueError("selector must be 4-byte hex")
    return selector

def verify_uniswap_v3_pool(
    rpc: JsonRpcClient, factory: str, pool_address: str, token0: str, token1: str,
    fee_tiers: tuple[int, ...] = (100, 500, 3000, 10000), block_tag: str = "latest",
) -> int | None:
    for fee in fee_tiers:
        calldata = factory_get_pool_calldata(token0, token1, fee)
        result = rpc.eth_call(factory, calldata) if block_tag == "latest" else rpc.eth_call(factory, calldata, block_tag)
        found = "0x" + result[-40:].lower()
        if int(found, 16) != 0 and found == pool_address.lower():
            return fee
    return None
