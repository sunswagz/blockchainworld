"""Versioned registry of chains exposed by OKX Wallet; no RPC secrets or tx methods."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Iterable

@dataclass(frozen=True)
class Chain:
    key: str
    name: str
    family: str
    chain_index: int
    wallet_support: str = "documented"
    scan_status: str = "registry_only"
    native_asset: str | None = None

# Snapshot of OKX's published Supported Networks table. This is metadata, not
# a promise that every network exposes DEX LP data or that all wallet accounts
# use the same address on every chain.
CHAINS: tuple[Chain, ...] = (
    Chain("ethereum","Ethereum","evm",1,native_asset="ETH"),
    Chain("arbitrum","Arbitrum One","evm",42161,native_asset="ETH"),
    Chain("avalanche","Avalanche C-Chain","evm",43114,native_asset="AVAX"),
    Chain("base","Base","evm",8453,scan_status="adapter_available",native_asset="ETH"),
    Chain("bnb","BNB Chain","evm",56,native_asset="BNB"),
    Chain("blast","Blast","evm",81457,native_asset="ETH"),
    Chain("linea","Linea","evm",59144,native_asset="ETH"),
    Chain("mantle","Mantle","evm",5000,native_asset="MNT"),
    Chain("optimism","Optimism","evm",10,native_asset="ETH"),
    Chain("polygon","Polygon","evm",137,native_asset="POL"),
    Chain("scroll","Scroll","evm",534352,native_asset="ETH"),
    Chain("sonic","Sonic","evm",146,native_asset="S"),
    Chain("unichain","Unichain","evm",130,native_asset="ETH"),
    Chain("xlayer","X Layer","evm",196,scan_status="adapter_available",native_asset="OKB"),
    Chain("zksync","zkSync Era","evm",324,native_asset="ETH"),
    Chain("mantapacific","Manta Pacific","evm",169,native_asset="ETH"),
    Chain("conflux","Conflux eSpace","evm",1030,native_asset="CFX"),
    Chain("cronos","Cronos","evm",25,native_asset="CRO"),
    Chain("fantom","Fantom","evm",250,native_asset="FTM"),
    Chain("gnosis","Gnosis","evm",100,native_asset="xDAI"),
    Chain("metis","Metis","evm",1088,native_asset="METIS"),
    Chain("mode","Mode Network","evm",34443,native_asset="ETH"),
    Chain("opbnb","opBNB","evm",204,native_asset="BNB"),
    Chain("zora","Zora","evm",7777777,native_asset="ETH"),
    Chain("berachain","Berachain","evm",80094,native_asset="BERA"),
    Chain("ink","Ink","evm",57073,native_asset="ETH"),
    Chain("hyperEVM","HyperEVM","evm",999,native_asset="HYPE"),
    Chain("katana","Katana","evm",747474,native_asset="ETH"),
    Chain("monad","Monad","evm",143,native_asset="MON"),
    Chain("plasma","Plasma","evm",9745,native_asset="XPL"),
    Chain("sei","Sei EVM","evm",1329,native_asset="SEI"),
    Chain("sui","Sui","sui",784,native_asset="SUI"),
    Chain("solana","Solana","solana",501,native_asset="SOL"),
    Chain("bitcoin","Bitcoin","utxo",0,native_asset="BTC"),
    Chain("ton","TON","ton",607,native_asset="TON"),
    Chain("tron","TRON","tron",195,native_asset="TRX"),
)

def validate_registry(chains: Iterable[Chain] = CHAINS) -> None:
    rows = tuple(chains)
    keys = [c.key for c in rows]
    indexes = [(c.family, c.chain_index) for c in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate chain key")
    if len(indexes) != len(set(indexes)):
        raise ValueError("duplicate family/chain index")
    if any(c.family not in {"evm","solana","sui","utxo","ton","tron","other"} for c in rows):
        raise ValueError("unknown chain family")
    if any(c.scan_status not in {"registry_only","adapter_available","disabled"} for c in rows):
        raise ValueError("unknown scan status")

def get_chain(key: str) -> Chain:
    for chain in CHAINS:
        if chain.key.lower() == key.lower():
            return chain
    raise KeyError(key)

def list_chains(*, family: str | None = None, scan_status: str | None = None) -> list[dict]:
    rows = [c for c in CHAINS if (family is None or c.family == family)
            and (scan_status is None or c.scan_status == scan_status)]
    return [asdict(c) for c in rows]
