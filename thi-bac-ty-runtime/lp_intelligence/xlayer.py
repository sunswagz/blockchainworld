"""X Layer mainnet deployment registry for LP Intelligence.

Addresses are sourced from the official Uniswap deployment documentation.
Do not reuse addresses from Base or another EVM chain.
"""

CHAIN_ID = 196
CHAIN_NAME = "X Layer"
NATIVE_SYMBOL = "OKB"
DEFAULT_RPC_URL = "https://rpc.xlayer.tech"
EXPLORER_BASE_URL = "https://www.okx.com/web3/explorer/xlayer"

UNISWAP_V3 = {
    "factory": "0x4B2ab38DBF28D31D467aA8993f6c2585981D6804",
    "nonfungible_position_manager": "0x315e413A11AB0df498eF83873012430ca36638Ae",
    "wrapped_native_token": "0xe538905cf8410324e03A5A23C1c177a474D59b2b",
    "multicall": "0xe2023f3fa515cf070e07fd9d51c1d236e07843f4",
    "tick_lens": "0x661e93cca42afacb172121ef892830ca3b70f08d",
    "quoter_v2": "0xd1b797d92d87b688193a2b976efc8d577d204343",
    "swap_router_02": "0x4f0c28f5926afda16bf2506d5d9e57ea190f9bca",
}
