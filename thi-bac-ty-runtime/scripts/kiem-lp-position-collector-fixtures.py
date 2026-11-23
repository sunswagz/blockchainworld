"""Offline integration fixtures for the read-only Uniswap V3/Base NFT collector."""
from __future__ import annotations
import sys
import tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from lp_intelligence.collectors.uniswap_v3_positions_base import (
    POSITION_MANAGER, TRANSFER_TOPIC, collect_uniswap_v3_base_positions,
    decode_abi_string, discover_wallet_token_ids, format_units,
)
from lp_intelligence.storage import SQLiteStore

WALLET = "0x" + "aa" * 20
TOKEN0 = "0x" + "11" * 20
TOKEN1 = "0x" + "22" * 20
POOL = "0x" + "33" * 20
FACTORY = "0x33128a8fc17869897dce68ed026d694621f6fdfd"
def w(v: int) -> str: return format(v, "064x")
def address_word(a: str) -> str: return w(int(a, 16))
def abi_string(s: str) -> str:
    raw=s.encode().hex()
    return "0x"+w(32)+w(len(s))+raw.ljust(((len(raw)+63)//64)*64,"0")
def transfer_log(token_id: int) -> dict:
    return {"topics":[TRANSFER_TOPIC,"0x"+"00"*32,"0x"+("00"*12)+WALLET[2:], "0x"+w(token_id)]}

class FakeRpc:
    def __init__(self): self.calls=[]; self.log_calls=[]
    def get_block_number(self): return 123456
    def get_block(self, block_number):
        assert block_number==123456
        return {"hash":"0x"+"ab"*32,"timestamp":hex(1770000000)}
    def get_logs(self, *, address, from_block, to_block, topics):
        self.log_calls.append((address,from_block,to_block,topics))
        assert address.lower()==POSITION_MANAGER.lower()
        if topics[1] is None: return [transfer_log(7)]
        return []
    def eth_call(self,to,data,block_tag="latest"):
        self.calls.append((to.lower(),data,block_tag))
        assert block_tag==hex(123456),"all contract reads must use one block tag"
        selector=data[:10]
        if to.lower()==POSITION_MANAGER.lower():
            if selector=="0x6352211e": return "0x"+address_word(WALLET)
            if selector=="0x99fbab88":
                vals=(0,0,int(TOKEN0,16),int(TOKEN1,16),500,(1<<24)-100,100,10**18,0,0,5,6)
                return "0x"+"".join(w(v) for v in vals)
        if to.lower()==FACTORY: return "0x"+w(int(POOL,16))
        if to.lower()==POOL.lower():
            if selector=="0x0dfe1681": return "0x"+address_word(TOKEN0)
            if selector=="0xd21220a7": return "0x"+address_word(TOKEN1)
            if selector=="0xddca3f43": return "0x"+w(500)
            if selector=="0x3850c7bd": return "0x"+w(1<<96)+w(0)+w(0)+w(0)+w(0)+w(0)+w(1)
            if selector=="0xf3058399": return "0x"+w(2*(1<<128))
            if selector=="0x46141319": return "0x"+w(3*(1<<128))
            if selector=="0xf30dba93": return "0x"+"".join(w(v) for v in (1,0,0,0,0,0,0,1))
        if to.lower()==TOKEN0.lower():
            if selector=="0x313ce567": return "0x"+w(18)
            if selector=="0x95d89b41": return abi_string("AAA")
        if to.lower()==TOKEN1.lower():
            if selector=="0x313ce567": return "0x"+w(6)
            if selector=="0x95d89b41": return abi_string("BBB")
        raise AssertionError(f"unexpected eth_call {to} {data}")

def main() -> int:
    checks=0
    def check(label, condition):
        nonlocal checks
        if not condition: raise AssertionError(label)
        checks+=1
        print("  ✓",label)
    check("dynamic ERC20 symbol decoding",decode_abi_string(abi_string("USDC"))=="USDC")
    check("raw token units retain decimal precision",format_units(1234567,6)=="1.234567")
    rpc=FakeRpc()
    ids=discover_wallet_token_ids(rpc,WALLET,from_block=100,to_block=123456,chunk_size=2000)
    check("wallet NFT discovery uses Transfer logs in/out filters",ids==[7] and len(rpc.log_calls)>2)
    with tempfile.TemporaryDirectory() as tmp:
        store=SQLiteStore(Path(tmp)/"lp.sqlite")
        result=collect_uniswap_v3_base_positions(WALLET,from_block=100,rpc=rpc,store=store)
        check("collector verifies current ownerOf after log discovery",result["position_count"]==1 and result["positions"][0]["token_id"]=="7")
        check("all on-chain calls use one pinned block",bool(rpc.calls) and all(x[2]=="0x1e240" for x in rpc.calls))
        check("factory, pool identity and fee tier reconcile",result["positions"][0]["pool_address"]==POOL and result["positions"][0]["fee_tier"]==500)
        check("in-range status uses lower-inclusive upper-exclusive ticks",result["positions"][0]["in_range"] is True)
        check("unclaimed token fees are calculated",result["positions"][0]["unclaimed_fee0"]=="2.000000000000000005 AAA" and result["positions"][0]["unclaimed_fee1"]=="3000000000000.000006 BBB")
        check("position and fee snapshots are persisted",len(store.list_positions(WALLET))==1 and len(store.list_position_fees(WALLET))==1)
        fee=store.list_position_fees(WALLET)[0]
        check("fee snapshot stores block hash and raw token amounts",fee["block_hash"]=="0x"+"ab"*32 and fee["tokens_owed0_raw"]==str(2*10**18+5))
        check("fee USD and APR remain unknown",store.list_positions(WALLET)[0]["unclaimed_fees_usd"] is None)
    print(f"LP NFT collector fixtures passed: {checks}/{checks}")
    return 0
if __name__=="__main__": raise SystemExit(main())
