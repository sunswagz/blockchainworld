"""Kiểm kết nối Binance Spot Testnet.

    python scripts/kiem-testnet.py

Chạy được cả khi CHƯA có khoá: phần công khai (ping, đồng hồ, bộ lọc, giá, làm
tròn) kiểm hết, phần cần khoá thì báo rõ là bỏ qua chứ không giả vờ xanh.

KHÔNG đặt lệnh nào. Muốn thử đặt lệnh thật thì thêm cờ:

    python scripts/kiem-testnet.py --dat-lenh-that

Cờ đó mua một lượng nhỏ nhất hợp lệ rồi bán ngay bằng MARKET — vẫn là tiền giả,
nhưng nó chạm thật vào sổ lệnh nên phải gõ tay mới chạy.
"""
from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# KHÔNG BAO GIỜ chạm sổ thật. GHI ĐÈ, không `setdefault`: một dòng
# `export TCT_DATA_DIR=` trong shell là đủ để setdefault không làm gì, và
# chuyện đó đã sập BA lần ở repo này — lần nặng nhất là bộ kiểm cửa duyệt đưa
# một champion GIẢ lên ngôi trong sổ chiến lược thật.
import os
from _tam_tu_don import tam_moi

os.environ["TCT_DATA_DIR"] = tam_moi("tct-kiem-")

from trader.config import CONFIG  # noqa: E402
from trader.exchange import BinanceError, TestnetClient  # noqa: E402

FAILS: list[str] = []
SYMBOL = CONFIG["symbol"]


def check(cond: bool, label: str) -> bool:
    print(("  OK   " if cond else "  SAI  ") + label)
    if not cond:
        FAILS.append(label)
    return cond


def main() -> int:
    dat_lenh = "--dat-lenh-that" in sys.argv
    c = TestnetClient()

    print("\n[1] CÔNG KHAI (không cần khoá)")
    try:
        c.ping()
        check(True, "ping tới testnet.binance.vision")
    except Exception as e:  # noqa: BLE001
        check(False, f"ping: {e}")
        return 1

    # Lệch THÔ của máy không phải phép kiểm — client bù offset vào mọi request đã
    # ký, nên máy lệch 7 phút vẫn gửi lệnh được. Thứ phải đúng là dấu thời gian
    # SAU KHI BÙ. Kiểm lệch thô là kiểm nhầm thứ, và nó đỏ trong khi hệ thống chạy tốt.
    lech = c.sync_time()
    huong = "chậm hơn sàn" if lech > 0 else "nhanh hơn sàn"
    print(f"       đồng hồ máy {huong} {abs(lech) / 1000:.1f}s — đã bù vào mọi request đã ký")
    if abs(lech) > 60_000:
        print("       ⚠ lệch hơn một phút: nên sửa đồng hồ máy (w32tm /resync), vì nó còn ảnh hưởng "
              "chứng chỉ TLS và dấu thời gian git")
    import time as _t
    sau_bu = abs((int(_t.time() * 1000) + c._offset_ms) - c._get("/api/v3/time")["serverTime"])
    check(sau_bu < 3000, f"dấu thời gian sau khi bù lệch {sau_bu}ms so với sàn (recvWindow 5000)")

    f = c.filters(SYMBOL)
    check(f["status"] == "TRADING", f"{SYMBOL} đang {f['status']}")
    check(f["stepSize"] is not None, f"bước khối lượng {f['stepSize']}")
    check(f["tickSize"] is not None, f"bước giá {f['tickSize']}")
    check(f["minNotional"] is not None, f"giá trị lệnh tối thiểu ${f['minNotional']}")
    check(f["ocoAllowed"], f"OCO được phép: {f['ocoAllowed']} — cần cho việc giao SL/TP cho sàn giữ")

    gia = c.price(SYMBOL)
    check(gia > 0, f"giá testnet {gia:,.2f}")

    print("\n[2] LÀM TRÒN THEO BỘ LỌC")
    tho = 0.123456789
    lam_tron = c.round_qty(SYMBOL, tho)
    check(lam_tron <= Decimal(str(tho)),
          f"khối lượng {tho} → {lam_tron} (làm tròn XUỐNG, không bao giờ lên)")
    check(lam_tron % f["stepSize"] == 0, f"{lam_tron} là bội của bước {f['stepSize']}")
    p_tho = 63000.987654
    check(c.round_price(SYMBOL, p_tho) % f["tickSize"] == 0,
          f"giá {p_tho} → {c.round_price(SYMBOL, p_tho)} khớp bước giá")

    nho = c.round_qty(SYMBOL, 0.00001)
    ly_do = c.check_order(SYMBOL, nho, gia)
    check(ly_do is not None,
          f"lệnh {nho} @ {gia:,.0f} bị chặn đúng lý do: {ly_do}")

    du = c.round_qty(SYMBOL, float(f["minNotional"]) / gia * 1.2)
    check(c.check_order(SYMBOL, du, gia) is None,
          f"lệnh {du} @ {gia:,.0f} (≈${float(du) * gia:.2f}) hợp lệ")

    print("\n[3] SO GIÁ TESTNET vs MAINNET")
    print("     Phân tích chạy trên nến mainnet (testnet chỉ có 60 nến 4H, không đủ EMA200),")
    print("     còn khớp lệnh ở testnet. Hai sổ lệch nhau nhiều thì cả hệ thống vô nghĩa.")
    try:
        import httpx
        m = httpx.get("https://data-api.binance.vision/api/v3/ticker/price",
                      params={"symbol": SYMBOL}, timeout=15).json()
        gia_main = float(m["price"])
        lech_pct = abs(gia - gia_main) / gia_main * 100
        print(f"     testnet {gia:,.2f} · mainnet {gia_main:,.2f}")
        check(lech_pct < 0.5, f"lệch {lech_pct:.3f}% (ngưỡng 0.5%)")
    except Exception as e:  # noqa: BLE001
        check(False, f"không so được với mainnet: {e}")

    print("\n[4] CẦN KHOÁ")
    if not c.has_keys:
        print("  BỎ QUA — chưa có BINANCE_TESTNET_KEY / BINANCE_TESTNET_SECRET trong .env")
        print("           lấy ở https://testnet.binance.vision (đăng nhập bằng GitHub)")
        print("           rồi đặt \"mode\": \"testnet\" trong config.json")
    else:
        try:
            bal = c.balances()
            check(True, "đọc được số dư tài khoản")
            for asset, v in list(bal.items())[:6]:
                print(f"       {asset:<6} rảnh {v['free']:.8f}  khoá {v['locked']:.8f}")
            quote = bal.get(f["quote"], {}).get("free", 0.0)
            check(quote >= float(f["minNotional"]),
                  f"{f['quote']} rảnh {quote:.2f} ≥ tối thiểu {f['minNotional']} — đủ vào một lệnh")

            treo = c.open_orders(SYMBOL)
            check(True, f"đọc được lệnh treo: {len(treo)} lệnh")
            for o in treo[:5]:
                print(f"       {o['side']} {o['type']} {o['origQty']} @ {o.get('price')} "
                      f"stop={o.get('stopPrice')} listId={o.get('orderListId')}")

            if dat_lenh:
                print("\n[5] ĐẶT LỆNH THẬT (mua tối thiểu rồi bán ngay)")
                qty = c.round_qty(SYMBOL, float(f["minNotional"]) / gia * 1.3)
                print(f"       mua MARKET {qty} {f['base']} (≈${float(qty) * gia:.2f})")
                mua = c.market_buy(SYMBOL, qty)
                fills = mua.get("fills") or []
                got = sum(Decimal(x["qty"]) for x in fills)
                gia_mua = (sum(Decimal(x["price"]) * Decimal(x["qty"]) for x in fills) / got) if got else 0
                check(mua.get("status") == "FILLED", f"khớp mua: {mua.get('status')} @ {gia_mua:,.2f}")
                ban_qty = c.round_qty(SYMBOL, float(got))
                ban = c.market_sell(SYMBOL, ban_qty)
                check(ban.get("status") == "FILLED", f"khớp bán: {ban.get('status')}")
                print("       (đã trả lại trạng thái ban đầu, trừ phí)")
            else:
                print("\n[5] ĐẶT LỆNH THẬT — bỏ qua (thêm --dat-lenh-that để chạy)")
        except BinanceError as e:
            check(False, f"lỗi có ký: {e}")

    print("\n" + "=" * 64)
    if FAILS:
        print(f"  {len(FAILS)} PHÉP KIỂM SAI:")
        for x in FAILS:
            print("   - " + x)
        return 1
    print("  TESTNET SẴN SÀNG." if c.has_keys else "  Phần công khai OK — còn thiếu khoá.")
    print("=" * 64)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
