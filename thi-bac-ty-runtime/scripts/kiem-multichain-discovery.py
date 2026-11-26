from lp_intelligence.chain_registry import CHAINS, validate_registry
from lp_intelligence.providers.geckoterminal import GeckoTerminalClient, parse_pool_candidate
from pathlib import Path
import runpy

validate_registry()
assert len(CHAINS) >= 55
assert len({c.chain_index for c in CHAINS if c.family=="evm"}) == len([c for c in CHAINS if c.family=="evm"])
module=runpy.run_path(str(Path(__file__).with_name("kham-pha-dex-da-chuoi.py")))
mapping=module["GECKO_NETWORKS"]
assert {"ethereum","base","bnb","xlayer","solana"}.isdisjoint(mapping.keys()) is False
assert "solana" not in mapping  # not an EVM GeckoTerminal slug in this scanner
assert mapping["base"]=="base" and mapping["xlayer"]=="x-layer"
payload={"data":[{"id":"base_0x"+"1"*40,"attributes":{"address":"0x"+"1"*40,"name":"WETH / USDC","reserve_in_usd":"123.4","volume_usd":{"h24":"9.5"}},"relationships":{"base_token":{"data":{"id":"token_0x"+"2"*40}},"quote_token":{"data":{"id":"token_0x"+"3"*40}},"dex":{"data":{"id":"dex_test"}}}}],"included":[{"id":"token_0x"+"2"*40,"attributes":{"address":"0x"+"2"*40}},{"id":"token_0x"+"3"*40,"attributes":{"address":"0x"+"3"*40}},{"id":"dex_test","attributes":{"identifier":"test-dex"}}]}
p=parse_pool_candidate(payload["data"][0],{x["id"]:x for x in payload["included"]},"https://example.test/pool")
assert p.address=="0x"+"1"*40 and p.dex_id=="test-dex" and p.reserve_in_usd==123.4
print("OK: chain registry, curated GeckoTerminal mapping and pool parser fixtures")
