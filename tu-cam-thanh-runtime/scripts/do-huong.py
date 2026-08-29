"""ĐO HƯỚNG — nửa LONG và nửa SHORT của chiến lược đáng bao nhiêu, tách riêng.

    python scripts/do-huong.py --cho BTCUSDT:1d,ETHUSDT:1d --ghi

VÌ SAO CẦN MỘT PHÉP ĐO RIÊNG CHO CHUYỆN NÀY

Sổ lệnh THẬT: 41 LONG, 0 SHORT. Trong 154 luận điểm, bộ não chưa từng đề xuất
SHORT một lần. Nhưng bản CHẠY LẠI thì có — 41 LONG và 11 SHORT chỉ riêng BTC.

Nghĩa là phép đo và bản chạy thật đang là HAI CHIẾN LƯỢC KHÁC NHAU. Sàn spot
chỉ bán được thứ đang giữ, nên `risk.py` chặn SHORT khi `spot_only` — chặn
đúng. Cái sai là không ai đối chiếu con số đo với thứ thật sự chạy được, nên
mọi kết luận về champion đều nói về một chiến lược mà bot không chạy nổi.

Đo lần đầu trên 12 chợ khung 1d:

    cả hai chiều   558 lệnh   +0,0063R
    chỉ LONG       344 lệnh   −0,0168R
    riêng SHORT    214 lệnh   +0,0435R

Nửa SHORT là nửa có lãi. Bot đang chạy đúng nửa lỗ.

ĐÂY KHÔNG PHẢI LỜI KHUYÊN BẬT SHORT

Nó là một con số, và con số ấy đến từ chạy lại — khớp đúng giá đặt, không nhảy
giá qua stop. Short trong thực tế còn có phí vay và rủi ro bị ép đóng, những
thứ chạy lại không mô phỏng. Việc của script này là làm cho khoảng cách giữa
"đo được" và "chạy được" NHÌN THẤY ĐƯỢC, chứ không phải đóng nó lại.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from trader import huanluyen  # noqa: E402
from trader.config import CONFIG, DATA_DIR, ROOT  # noqa: E402

GHI = "--ghi" in sys.argv
NL = chr(10)
NGU_CANH = {"5m": "30m", "15m": "1h", "30m": "4h", "1h": "4h", "4h": "1d", "1d": "1d"}


def _co(ten: str, mac_dinh):
    return sys.argv[sys.argv.index(ten) + 1] if ten in sys.argv else mac_dinh


def _nap(sym: str, tf: str):
    ctx = NGU_CANH.get(tf, "1d")
    nen = {}
    for k in (tf, ctx):
        f = ROOT / "data" / "lich-su" / f"{sym}-{k}.json"
        if not f.exists():
            return None
        nen[k] = json.loads(f.read_text(encoding="utf-8"))
    cuoi = max(x.get("t") or 0 for x in nen[tf])
    if (_dt.datetime.now(_dt.timezone.utc).timestamp() * 1000 - cuoi) / 86_400_000 > 30:
        return None
    CONFIG["timeframes"]["primary"] = tf
    CONFIG["timeframes"]["context"] = ctx
    return nen


def gop(ds: list[tuple[float, int]]) -> tuple[float | None, int]:
    """Kỳ vọng gộp theo TRỌNG SỐ số lệnh. Hàm thuần."""
    n = sum(c for _, c in ds)
    if not n:
        return None, 0
    return sum(r * c for r, c in ds) / n, n


def main() -> int:
    cho = [x.strip() for x in str(_co("--cho", "")).split(",") if x.strip()]
    if not cho:
        cho = [f"{CONFIG['symbol']}:{CONFIG['timeframes']['primary']}"]

    ca_hai: list[tuple[float, int]] = []
    chi_long: list[tuple[float, int]] = []
    lenh_long: list[float] = []
    lenh_short: list[float] = []
    theo_cho: dict[str, dict] = {}
    quang: list[tuple[int, int]] = []

    for ten in cho:
        sym, _, tf = ten.partition(":")
        tf = tf or CONFIG["timeframes"]["primary"]
        nen = _nap(sym, tf)
        if not nen or len(nen[tf]) < 400:
            print(f"  bỏ qua {ten}")
            continue
        t = [x.get("t") for x in nen[tf] if x.get("t")]
        quang.append((min(t), max(t)))
        chuoi = huanluyen.lay_chuoi(nen, sym)[0]

        kq = huanluyen.chay_lai(nen, symbol=sym, chuoi=chuoi, bo_qua_kill=True)
        tk = kq["thongKe"]
        if tk["so"] and tk["kyVongR"] is not None:
            ca_hai.append((tk["kyVongR"], tk["so"]))
        for l in kq["lenh"]:
            (lenh_long if l["side"] == "LONG" else lenh_short).append(l["R"])

        kq_l = huanluyen.chay_lai(nen, symbol=sym, chuoi=chuoi,
                                  tham={"cheDoVao": ["TREND_UP"]}, bo_qua_kill=True)
        tl = kq_l["thongKe"]
        if tl["so"] and tl["kyVongR"] is not None:
            chi_long.append((tl["kyVongR"], tl["so"]))

        theo_cho[ten] = {"caHai": tk["kyVongR"], "soCaHai": tk["so"],
                         "chiLong": tl["kyVongR"], "soChiLong": tl["so"]}
        # Chợ không sinh lệnh nào trả `kyVongR` là None — chuyện bình thường với
        # coin ít biến động hoặc bộ lọc chặt. In thẳng None thì nổ format.
        _f = lambda v: f"{v:+.4f}" if v is not None else "   —   "
        print(f"  {ten:16} cả hai {_f(tk['kyVongR'])}/{tk['so']:<4} · "
              f"chỉ LONG {_f(tl['kyVongR'])}/{tl['so']}")

    if not theo_cho:
        print("Không chợ nào dùng được.")
        return 1

    r_hai, n_hai = gop(ca_hai)
    r_long, n_long = gop(chi_long)
    kv_l = sum(lenh_long) / len(lenh_long) if lenh_long else None
    kv_s = sum(lenh_short) / len(lenh_short) if lenh_short else None

    print(NL + f"{len(theo_cho)} chợ:")
    _g = lambda v: f"{v:+.4f}" if v is not None else "   —   "
    print(f"  cả hai chiều  {n_hai:5} lệnh · kỳ vọng GỘP {_g(r_hai)}R")
    print(f"  chỉ LONG      {n_long:5} lệnh · kỳ vọng GỘP {_g(r_long)}R")
    if kv_l is not None:
        print(f"  riêng LONG    {len(lenh_long):5} lệnh · {kv_l:+.4f}R")
    if kv_s is not None:
        print(f"  riêng SHORT   {len(lenh_short):5} lệnh · {kv_s:+.4f}R")

    chenh = (r_hai - r_long) if (r_hai is not None and r_long is not None) else None
    if chenh is not None:
        print(NL + f"Nửa SHORT đóng góp {chenh:+.4f}R vào kỳ vọng mỗi lệnh.")
        print("Bot chạy thật trên sàn SPOT không đánh được nửa đó — "
              "mọi con số «cả hai chiều» nói về một chiến lược nó không chạy nổi.")

    if GHI:
        f = DATA_DIR / "do-huong.json"
        tam = f.with_suffix(f".{os.getpid()}.tmp")
        tam.write_text(json.dumps({
            "luc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
            "cho": list(theo_cho), "soCho": len(theo_cho),
            "quang": ({"tu": _dt.datetime.fromtimestamp(
                           min(a for a, _ in quang) / 1000,
                           _dt.timezone.utc).strftime("%Y-%m-%d"),
                       "den": _dt.datetime.fromtimestamp(
                           max(b for _, b in quang) / 1000,
                           _dt.timezone.utc).strftime("%Y-%m-%d")} if quang else None),
            "caHai": {"kyVongR": r_hai, "so": n_hai},
            "chiLong": {"kyVongR": r_long, "so": n_long},
            "riengLong": {"kyVongR": kv_l, "so": len(lenh_long)},
            "riengShort": {"kyVongR": kv_s, "so": len(lenh_short)},
            "chenhDoShort": chenh,
            "theoCho": theo_cho,
        }, ensure_ascii=False, indent=1), encoding="utf-8")
        os.replace(tam, f)
        print(NL + f"đã ghi {f.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
