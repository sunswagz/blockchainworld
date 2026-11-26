"""Read-only cross-chain DEX pool discovery via GeckoTerminal trending pools."""
from __future__ import annotations
import argparse, json, time
from datetime import datetime, timezone
from pathlib import Path
from lp_intelligence.providers.geckoterminal import GeckoTerminalClient
from lp_intelligence.chain_registry import CHAINS

# Slugs are provider identifiers, not chain IDs. Keep only mappings that have
# been explicitly curated; unknown slugs are skipped rather than guessed.
GECKO_NETWORKS = {
    "ethereum":"eth", "arbitrum":"arbitrum", "avalanche":"avax",
    "base":"base", "bnb":"bsc", "blast":"blast", "linea":"linea",
    "mantle":"mantle", "optimism":"optimism", "polygon":"polygon_pos",
    "scroll":"scroll", "sonic":"sonic", "unichain":"unichain",
    "xlayer":"x-layer", "zksync":"zksync", "mantapacific":"manta-pacific",
    "conflux":"conflux-espace", "cronos":"cronos", "fantom":"fantom",
    "gnosis":"xdai", "metis":"metis", "mode":"mode", "opbnb":"op_bnb",
    "zora":"zora", "berachain":"berachain", "ink":"ink",
    "hyperEVM":"hyperevm", "katana":"katana", "monad":"monad",
    "plasma":"plasma", "sei":"sei",
}

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chains", default="all", help="comma-separated registry keys or all")
    parser.add_argument("--pages", type=int, default=1)
    parser.add_argument("--delay", type=float, default=0.35)
    parser.add_argument("--output", default="./data/multichain-dex-discovery.json")
    args=parser.parse_args()
    if not 1 <= args.pages <= 10 or args.delay < 0:
        parser.error("--pages must be 1..10 and --delay nonnegative")
    selected=set(GECKO_NETWORKS) if args.chains=="all" else set(args.chains.split(","))
    unknown=selected-set(GECKO_NETWORKS)
    if unknown:
        parser.error("No curated GeckoTerminal network slug for: "+", ".join(sorted(unknown)))
    registry={c.key:c for c in CHAINS}
    output={"generated_at":datetime.now(timezone.utc).isoformat(),"provider":"GeckoTerminal V2",
            "read_only":True,"chains":[],"errors":[]}
    client=GeckoTerminalClient()
    try:
        for key in sorted(selected):
            chain=registry[key]
            row={"chain_key":key,"chain_name":chain.name,"chain_index":chain.chain_index,
                 "provider_network":GECKO_NETWORKS[key],"pools":[],"pages_scanned":0}
            for page in range(1,args.pages+1):
                try:
                    pools,raw,url=client.trending_pools(GECKO_NETWORKS[key],page=page)
                    row["pages_scanned"]+=1
                    for p in pools:
                        row["pools"].append({
                            "address":p.address,"name":p.name,"dex_id":p.dex_id,
                            "token0_or_base":p.base_token_address,"token1_or_quote":p.quote_token_address,
                            "base_token_price_usd":p.base_token_price_usd,
                            "quote_token_price_usd":p.quote_token_price_usd,
                            "tvl_usd":p.reserve_in_usd,"volume_24h_usd":p.volume_24h_usd,
                            "source_url":url,"verification_status":"provider_candidate_unverified",
                        })
                    time.sleep(args.delay)
                except Exception as exc:
                    output["errors"].append({"chain_key":key,"page":page,
                                             "error_type":type(exc).__name__,"message":str(exc)[:500]})
                    break
            row["pools"].sort(key=lambda p:(p["tvl_usd"] or -1,p["volume_24h_usd"] or -1),reverse=True)
            output["chains"].append(row)
    finally:
        client.close()
    output["summary"]={"chains_requested":len(selected),
        "chains_with_results":sum(bool(c["pools"]) for c in output["chains"]),
        "candidate_pools":sum(len(c["pools"]) for c in output["chains"]),
        "provider_errors":len(output["errors"]),
        "note":"Provider candidates are not verified deployments, wallet positions, audited pools, or APR recommendations."}
    path=Path(args.output); path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(output,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps(output["summary"],ensure_ascii=False))
    return 0 if not output["errors"] else 2

if __name__=="__main__":
    raise SystemExit(main())
