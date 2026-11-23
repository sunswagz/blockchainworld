"""Offline tests for Base Uniswap V3 realized fee and cost accounting."""
from __future__ import annotations
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from lp_intelligence.accounting import (
    COLLECT_TOPIC, DECREASE_LIQUIDITY_TOPIC, INCREASE_LIQUIDITY_TOPIC,
    TRANSFER_TOPIC, decode_position_manager_event, attribute_position_cashflows,
    allocate_transaction_gas,
)
from lp_intelligence.storage import SQLiteStore

WALLET = "0x" + "aa" * 20
MANAGER = "0x" + "bb" * 20
TX = "0x" + "cc" * 32
BLOCK_HASH = "0x" + "dd" * 32

def w(value: int) -> str:
    return format(value, "064x")

def log(topic: str, token_id: int, data: str, index: int) -> dict:
    return {
        "address": MANAGER, "topics": [topic, "0x" + w(token_id)],
        "data": "0x" + data, "transactionHash": TX,
        "blockNumber": hex(100), "transactionIndex": "0x0",
        "logIndex": hex(index), "blockHash": BLOCK_HASH,
    }

def main() -> int:
    checks = 0
    def check(label, condition):
        nonlocal checks
        if not condition:
            raise AssertionError(label)
        checks += 1
        print("  ✓", label)

    collect = decode_position_manager_event(
        log(COLLECT_TOPIC, 7, w(int(WALLET, 16)) + w(130) + w(240), 3), WALLET
    )
    check("Collect decodes indexed tokenId, recipient and raw token amounts",
          collect["event_type"] == "Collect" and collect["token_id"] == "7"
          and collect["recipient"] == WALLET and collect["amount0_raw"] == "130"
          and collect["amount1_raw"] == "240")

    decrease = decode_position_manager_event(
        log(DECREASE_LIQUIDITY_TOPIC, 7, w(999) + w(100) + w(200), 2), WALLET
    )
    check("DecreaseLiquidity decodes liquidity and principal amounts",
          decrease["liquidity_raw"] == "999" and decrease["amount0_raw"] == "100"
          and decrease["amount1_raw"] == "200")

    increase = decode_position_manager_event(
        log(INCREASE_LIQUIDITY_TOPIC, 7, w(500) + w(1000) + w(2000), 1), WALLET
    )
    check("IncreaseLiquidity decodes capital contribution amounts",
          increase["amount0_raw"] == "1000" and increase["amount1_raw"] == "2000")

    transfer_log = {
        "address": MANAGER,
        "topics": [TRANSFER_TOPIC, "0x" + w(0), "0x" + w(int(WALLET, 16)), "0x" + w(7)],
        "data": "0x", "transactionHash": TX, "blockNumber": hex(100),
        "transactionIndex": "0x0", "logIndex": hex(0), "blockHash": BLOCK_HASH,
    }
    transfer = decode_position_manager_event(transfer_log, WALLET)
    check("ERC721 Transfer decodes tokenId and ownership transition",
          transfer["token_id"] == "7" and transfer["from_address"] == "0x" + "0"*40
          and transfer["recipient"] == WALLET)

    cash = attribute_position_cashflows([
        {"event_type": "IncreaseLiquidity", "block_number": 1, "log_index": 0,
         "amount0_raw": "1000", "amount1_raw": "2000"},
        {"event_type": "DecreaseLiquidity", "block_number": 2, "log_index": 0,
         "amount0_raw": "100", "amount1_raw": "200"},
        {"event_type": "Collect", "block_number": 2, "log_index": 1,
         "amount0_raw": "130", "amount1_raw": "240"},
    ])
    check("Collect attributes withdrawn principal first and residual as realized fees",
          cash["principal_recovered0_raw"] == "100"
          and cash["principal_recovered1_raw"] == "200"
          and cash["realized_fees0_raw"] == "30"
          and cash["realized_fees1_raw"] == "40")

    ownership, basis = owned_events([
        {"event_type": "Transfer", "block_number": 1, "log_index": 0,
         "from_address": "0x" + "0"*40, "recipient": WALLET},
        {"event_type": "IncreaseLiquidity", "block_number": 1, "log_index": 1,
         "amount0_raw": "10", "amount1_raw": "20"},
        {"event_type": "Transfer", "block_number": 2, "log_index": 0,
         "from_address": WALLET, "recipient": "0x" + "ee"*20},
        {"event_type": "Collect", "block_number": 3, "log_index": 0,
         "amount0_raw": "999", "amount1_raw": "999"},
    ], WALLET)
    check("ownership intervals exclude events after transfer-out and recognize mint-to-wallet",
          len(ownership) == 3 and basis == "position_no_longer_held")

    _, transferred_basis = owned_events([
        {"event_type": "Transfer", "block_number": 1, "log_index": 0,
         "from_address": "0x" + "ee"*20, "recipient": WALLET},
        {"event_type": "IncreaseLiquidity", "block_number": 1, "log_index": 1,
         "amount0_raw": "10", "amount1_raw": "20"},
    ], WALLET)
    check("transferred-in NFT keeps acquisition basis unknown",
          transferred_basis == "acquired_by_transfer_or_reacquired")

    gas = allocate_transaction_gas(101, ["p1", "p2", "p1"])
    check("transaction gas is split across distinct positions without loss",
          gas == {"p1": 51, "p2": 50} and sum(gas.values()) == 101)

    try:
        allocate_transaction_gas(-1, ["p1"])
        raised = False
    except ValueError:
        raised = True
    check("negative transaction gas is rejected", raised)

    with tempfile.TemporaryDirectory() as tmp:
        store = SQLiteStore(Path(tmp) / "accounting.sqlite")
        store.initialize()
        event = {
            "chain_id": "8453", "manager_address": MANAGER,
            "position_id": "8453:uniswap-v3:nft:7", "token_id": "7",
            "wallet_address": WALLET, "tx_hash": TX, "block_number": 100,
            "block_hash": BLOCK_HASH, "transaction_index": 0, "log_index": 0,
            "event_type": "Transfer", "from_address": "0x" + "0"*40,
            "recipient": WALLET, "amount0_raw": "0", "amount1_raw": "0",
            "liquidity_raw": "0", "raw_log_json": "{}",
        }
        first = store.add_lp_position_event(event)
        second = store.add_lp_position_event(event)
        check("event ledger is idempotent by chain, transaction and log index", first == second
              and len(store.list_lp_position_events(wallet=WALLET)) == 1)

    print(f"LP realized accounting fixtures passed: {checks}/{checks}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
