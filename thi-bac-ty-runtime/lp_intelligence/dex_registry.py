"""DEX protocol catalogue. Unknown deployments are never guessed."""
from __future__ import annotations
from dataclasses import asdict, dataclass

@dataclass(frozen=True)
class DexProtocol:
    key: str
    name: str
    chain_key: str
    family: str
    lp_model: str
    discovery_status: str
    adapter_key: str | None = None
    deployment_verified: bool = False
    notes: str = ""

# Only deployments already represented by the existing collectors are marked
# adapter_available/verified. Other entries are protocol families to discover,
# not fabricated contract addresses or claims of live support.
DEX_PROTOCOLS: tuple[DexProtocol, ...] = (
    DexProtocol("uniswap-v3-base","Uniswap V3","base","uniswap_v3","concentrated","adapter_available","uniswap_v3_evm",True,"Existing Base pool/NFT/fee collectors."),
    DexProtocol("uniswap-v3-xlayer","Uniswap V3","xlayer","uniswap_v3","concentrated","partial","uniswap_v3_evm",True,"Existing X Layer discovery/position scanner; fee accounting parity remains incomplete."),
    DexProtocol("evm-v2-family","V2-style AMMs","*","amm_v2","fungible_lp_token","discovery_required",None,False,"Factory/pair adapters require per-chain deployment registry."),
    DexProtocol("evm-v3-family","V3-style AMMs","*","concentrated","nft_or_manager_position","discovery_required",None,False,"Factory/position-manager deployments require verification."),
    DexProtocol("evm-stableswap-family","Stable-swap AMMs","*","stableswap","protocol_specific","discovery_required",None,False,"Pool and LP-token semantics vary by protocol."),
    DexProtocol("solana-amm-family","Solana AMMs","solana","solana_amm","token_account_or_position","discovery_required",None,False,"Requires program-specific account decoders."),
    DexProtocol("solana-clmm-family","Solana CLMMs","solana","solana_clmm","concentrated","discovery_required",None,False,"Requires program-specific position and fee adapters."),
    DexProtocol("sui-clmm-family","Sui AMMs/CLMMs","sui","sui_clmm","object_position","discovery_required",None,False,"Requires Move object and event adapters."),
)

def validate_registry() -> None:
    keys = [p.key for p in DEX_PROTOCOLS]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate DEX protocol key")
    allowed = {"adapter_available","partial","discovery_required","disabled"}
    if any(p.discovery_status not in allowed for p in DEX_PROTOCOLS):
        raise ValueError("invalid DEX discovery status")
    if any(p.deployment_verified and not p.adapter_key for p in DEX_PROTOCOLS):
        raise ValueError("verified deployment requires an adapter key")

def list_protocols(*, chain_key: str | None = None, status: str | None = None) -> list[dict]:
    rows = [p for p in DEX_PROTOCOLS if (chain_key is None or p.chain_key in {chain_key,"*"})
            and (status is None or p.discovery_status == status)]
    return [asdict(p) for p in rows]
