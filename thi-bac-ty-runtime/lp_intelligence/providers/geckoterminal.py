"""Small GeckoTerminal V2 client; public market data only."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

BASE_URL = "https://api.geckoterminal.com/api/v2"
ACCEPT = "application/json;version=20230203"


@dataclass(frozen=True)
class PoolCandidate:
    address: str
    name: str
    dex_id: str | None
    base_token_address: str | None
    quote_token_address: str | None
    base_token_price_usd: float | None
    quote_token_price_usd: float | None
    reserve_in_usd: float | None
    volume_24h_usd: float | None
    source_url: str


def _number(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if result == result and abs(result) != float("inf") else None


def _included_map(payload: dict) -> dict[str, dict]:
    return {
        item.get("id"): item
        for item in payload.get("included", [])
        if isinstance(item, dict) and item.get("id")
    }


def parse_pool_candidate(item: dict, included: dict[str, dict], source_url: str) -> PoolCandidate:
    attrs = item.get("attributes") or {}
    rels = item.get("relationships") or {}

    def related_address(name: str) -> str | None:
        rel = rels.get(name) or {}
        data = rel.get("data") or {}
        resource = included.get(data.get("id"), {})
        token_attrs = resource.get("attributes") or {}
        address = token_attrs.get("address")
        if address:
            return str(address).lower()
        # Some API versions include the address directly in the resource id.
        rid = data.get("id", "")
        if "_" in rid:
            possible = rid.rsplit("_", 1)[-1]
            if possible.startswith("0x") and len(possible) == 42:
                return possible.lower()
        return None

    dex_rel = (rels.get("dex") or {}).get("data") or {}
    dex_resource = included.get(dex_rel.get("id"), {})
    dex_attrs = dex_resource.get("attributes") or {}
    pool_address = attrs.get("address")
    if not pool_address:
        resource_id = item.get("id", "")
        pool_address = resource_id.rsplit("_", 1)[-1] if "_" in resource_id else None
    if not isinstance(pool_address, str) or not pool_address.startswith("0x") or len(pool_address) != 42:
        raise ValueError("GeckoTerminal pool response has no valid EVM pool address")

    volume = attrs.get("volume_usd") or {}
    return PoolCandidate(
        address=pool_address.lower(),
        name=str(attrs.get("name") or ""),
        dex_id=str(dex_attrs.get("identifier") or dex_attrs.get("name") or "") or None,
        base_token_address=related_address("base_token"),
        quote_token_address=related_address("quote_token"),
        base_token_price_usd=_number(attrs.get("base_token_price_usd")),
        quote_token_price_usd=_number(attrs.get("quote_token_price_usd")),
        reserve_in_usd=_number(attrs.get("reserve_in_usd")),
        volume_24h_usd=_number(volume.get("h24")) if isinstance(volume, dict) else None,
        source_url=source_url,
    )


class GeckoTerminalClient:
    def __init__(self, timeout: float = 15.0, client: httpx.Client | None = None):
        self._client = client or httpx.Client(
            timeout=timeout,
            headers={"Accept": ACCEPT, "User-Agent": "BlockchainWorld-LP-Intelligence/0.1"},
        )
        self._owns_client = client is None

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def _get(self, path: str, params: dict | None = None) -> dict:
        response = self._client.get(f"{BASE_URL}{path}", params=params)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError("Unexpected GeckoTerminal response")
        return payload

    def token_pools(self, network: str, token_address: str) -> tuple[list[PoolCandidate], dict]:
        path = f"/networks/{network}/tokens/{token_address}/pools"
        payload = self._get(path, params={"include": "base_token,quote_token,dex", "page": 1})
        url = f"{BASE_URL}{path}"
        included = _included_map(payload)
        candidates = [
            parse_pool_candidate(item, included, url)
            for item in payload.get("data", [])
            if isinstance(item, dict)
        ]
        return candidates, payload

    def pool_detail(self, network: str, pool_address: str) -> tuple[dict, str]:
        path = f"/networks/{network}/pools/{pool_address}"
        payload = self._get(path, params={"include": "base_token,quote_token,dex"})
        return payload, f"{BASE_URL}{path}"


    def trending_pools(self, network: str, *, page: int = 1) -> tuple[list[PoolCandidate], dict, str]:
        """Discover public trending pool candidates on a GeckoTerminal network slug."""
        if page < 1 or page > 10:
            raise ValueError("page must be between 1 and 10")
        path = f"/networks/{network}/trending_pools"
        payload = self._get(path, params={
            "include": "base_token,quote_token,dex",
            "page": page,
        })
        url = f"{BASE_URL}{path}?page={page}"
        included = _included_map(payload)
        candidates = [
            parse_pool_candidate(item, included, url)
            for item in payload.get("data", [])
            if isinstance(item, dict)
        ]
        return candidates, payload, url
