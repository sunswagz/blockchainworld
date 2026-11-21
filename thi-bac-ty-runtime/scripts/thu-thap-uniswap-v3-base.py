"""Run one read-only Uniswap V3/Base market-data collection cycle."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lp_intelligence.collectors.uniswap_v3_base import collect_uniswap_v3_base


if __name__ == "__main__":
    try:
        result = collect_uniswap_v3_base()
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1)
    print(json.dumps(result, ensure_ascii=False, indent=2))
