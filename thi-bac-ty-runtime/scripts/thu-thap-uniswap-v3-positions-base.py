"""Collect all current Uniswap V3/Base NFT positions for a public wallet address."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from lp_intelligence.collectors.uniswap_v3_positions_base import collect_uniswap_v3_base_positions

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wallet", required=True, help="Public EVM wallet address; no connection/signature")
    parser.add_argument("--max-positions", type=int, default=100)
    args = parser.parse_args()
    result = collect_uniswap_v3_base_positions(args.wallet, max_positions=args.max_positions)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
