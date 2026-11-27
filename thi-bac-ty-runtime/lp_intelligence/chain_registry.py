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
    # Additional EVM networks listed in the current OKX Supported Networks page.
    Chain("arc","Arc","evm",5042,native_asset="USDC"),
    Chain("apechain","ApeChain","evm",33139,native_asset="APE"),
    Chain("bitlayer","Bitlayer","evm",200901,native_asset="BTC"),
    Chain("bob","BOB","evm",60808,native_asset="ETH"),
    Chain("boba","Boba","evm",288,native_asset="ETH"),
    Chain("celo","Celo","evm",42220,native_asset="CELO"),
    Chain("chiliz","Chiliz","evm",88888,native_asset="CHZ"),
    Chain("core","Core","evm",1116,native_asset="CORE"),
    Chain("endurance","Endurance","evm",648,native_asset="ACE"),
    Chain("ethereum_pow","EthereumPoW","evm",10001,native_asset="ETHW"),
    Chain("filecoin","Filecoin","evm",314,native_asset="FIL"),
    Chain("flare","Flare","evm",14,native_asset="FLR"),
    Chain("gravity","Gravity Alpha","evm",1625,native_asset="G"),
    Chain("haqq","Haqq Network","evm",11235,native_asset="ISLM"),
    Chain("kaia","Kaia","evm",8217,native_asset="KAIA"),
    Chain("kava","Kava EVM","evm",2222,native_asset="KAVA"),
    Chain("megaeth","MegaETH","evm",4326,native_asset="ETH"),
    Chain("merlin","Merlin","evm",4200,native_asset="BTC"),
    Chain("pulsechain","PulseChain","evm",369,native_asset="PLS"),
    Chain("robinhood","Robinhood Chain","evm",4663,native_asset="ETH"),
    Chain("ronin","Ronin","evm",2020,native_asset="RON"),
    Chain("stable","Stable","evm",988,native_asset="USDT"),
    Chain("taiko","Taiko","evm",167000,native_asset="ETH"),
    Chain("tempo","Tempo","evm",4217,native_asset="USD"),
    Chain("xdc","XDC Network","evm",50,native_asset="XDC"),
    Chain("zetachain","ZetaChain","evm",7000,native_asset="ZETA"),
    Chain("zero_g","0G","evm",16661,native_asset="0G"),
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
