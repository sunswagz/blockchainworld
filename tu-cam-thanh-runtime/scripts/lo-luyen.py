"""LÒ LUYỆN — học liên thanh trên tiền ảo, giá thật, nhiều chợ, nhiều quãng.

    python scripts/lo-luyen.py --cho BTCUSDT:1d,ETHUSDT:1d --bien 12
    python scripts/lo-luyen.py --cho <48 chợ> --bien 24 --lat 4 --ghi

VÌ SAO KHÔNG PHẢI "CHẠY THẬT NHANH HƠN"

Vòng chạy thật vào ~1,4 lệnh/ngày. Muốn 400 lệnh thì mất chín tháng, mà cấu
hình sẽ đổi trước lúc đó. Nút thắt của việc học KHÔNG phải tốc độ máy — nó là
số BẰNG CHỨNG ĐỘC LẬP. Chạy lại cùng một đoạn dữ liệu mười lần không thêm một
chữ nào; đo trên một chợ chưa từng nhìn thì có.

Nên lò này không tăng tốc đồng hồ. Nó tăng số chỗ để sai:

    48 chợ × 4 lát thời gian × N biến thể tham số

Tiền ảo, sàn giấy, nhưng GIÁ THẬT: cùng `RiskEngine`, cùng mô hình phí và trượt
giá mà bản chạy thật dùng. Chạy lại khớp đúng giá đặt và không nhảy giá qua
stop, nên nó nói ĐÚNG về cấu trúc và nói QUÁ ĐẸP về độ lớn — mọi con số ở đây
phải đọc kèm ghi chú đó.

VÌ SAO NHANH ĐƯỢC

Chuỗi tín hiệu (`sinh_luan_diem`) chỉ phụ thuộc NẾN, không phụ thuộc tham số
chiến lược. Nên tính một lần cho mỗi chợ — phần đắt nhất — rồi thử hàng chục
biến thể trên cùng chuỗi ấy gần như miễn phí. Đó là chỗ "liên thanh" thật sự.

LUẬT NHẬN: DƯƠNG Ở ĐA SỐ LÁT, KHÔNG PHẢI DƯƠNG KHI GỘP

Ba lần trong hệ này, một bộ luật dương ở chỗ nó được tìm ra rồi chết ở chỗ lạ.
Gộp mọi lát lại thành một con số là cách chắc chắn nhất để lặp lần thứ tư: một
lát rất tốt kéo được cả bảng. Nên điểm của một biến thể là

    (số lát dương) trước, rồi mới tới (kỳ vọng gộp)

và biến thể nào không dương ở quá nửa số lát thì không được đề xuất, dù gộp lại
đẹp tới đâu.

VÀ ĐẾM SỐ LẦN THỬ

Thử 24 biến thể rồi lấy cái tốt nhất thì cái tốt nhất ấy đẹp lên chỉ vì đã thử
24 lần. Lò ghi `soLanThu` vào kết quả để người đọc sau trừ hao — thiếu con số
đó thì "biến thể tốt nhất +0,3R" là một câu vô nghĩa.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from trader import huanluyen  # noqa: E402
from trader.brain import THAM_MAC_DINH  # noqa: E402
from trader.config import CONFIG, DATA_DIR, ROOT  # noqa: E402

GHI = "--ghi" in sys.argv
NL = chr(10)

# Khung ngữ cảnh cho mỗi khung chính — luôn dài hơn một bậc.
NGU_CANH = {"5m": "30m", "15m": "1h", "30m": "4h", "1h": "4h", "4h": "1d", "1d": "1d"}

# Lưới rộng hơn `LUOI_MAC_DINH` của huanluyen: lò lấy MẪU ngẫu nhiên từ đây chứ
# không quét hết, nên rộng không làm nó chậm — nhưng làm nó với tới được những
# chỗ mà lưới thưa bỏ qua.
LUOI: dict[str, list] = {
    "stopAtr": [1.0, 1.25, 1.5, 2.0, 2.5, 3.0],
    "demTp": [1.0, 1.05, 1.2, 1.4, 1.8, 2.2],
    "boiTp2": [1.3, 1.6, 2.0],
    "adxToiThieu": [0, 22, 25, 28, 32],
    "chanBienDongCao": [False, True],
    "chanXungDot": [True, False],
}


def _co(ten: str, mac_dinh):
    if ten not in sys.argv:
        return mac_dinh
    return sys.argv[sys.argv.index(ten) + 1]


def _cho_ds() -> list[str]:
    x = _co("--cho", None)
    if x:
        return [c.strip() for c in x.split(",") if c.strip()]
    return [f"{CONFIG['symbol']}:{CONFIG['timeframes']['primary']}"]


def _nap(sym: str, tf: str):
    """Nạp nến cho một chợ. Trả None khi thiếu file hoặc chợ đã CHẾT.

    Chợ chết: đủ nến nhưng nến cuối đã cũ (MKRUSDT ngừng 15/09/2025, đổi tên
    sang SKY). Nó qua mọi phép đếm rồi đóng góp một cửa sổ kết thúc từ một năm
    trước vào bảng gộp.
    """
    ctx = NGU_CANH.get(tf, "1d")
    nen = {}
    for k in (tf, ctx):
        f = ROOT / "data" / "lich-su" / f"{sym}-{k}.json"
        if not f.exists():
            return None
        nen[k] = json.loads(f.read_text(encoding="utf-8"))
    cuoi = max(x.get("t") or 0 for x in nen[tf])
    cu = (_dt.datetime.now(_dt.timezone.utc).timestamp() * 1000 - cuoi) / 86_400_000
    if cu > 30:
        print(f"    bỏ qua {sym}:{tf} — nến cuối cách đây {cu:.0f} ngày (chợ chết)")
        return None
    CONFIG["timeframes"]["primary"] = tf
    CONFIG["timeframes"]["context"] = ctx
    return nen


def bien_the(n: int, hat: int) -> list[dict]:
    """Champion trước, rồi n biến thể lấy mẫu ngẫu nhiên nhưng CÓ HẠT GIỐNG.

    Hạt giống cố định để lượt sau dựng lại đúng tập biến thể ấy. Không lặp lại
    được thì không ai kiểm chứng được kết quả, và "chạy lại thấy khác" sẽ được
    đổ cho nhiễu thay vì cho một lỗi.
    """
    r = random.Random(hat)
    ra = [dict(THAM_MAC_DINH)]
    thay = set()
    canh = 1
    while len(ra) < n + 1 and canh < n * 200:
        canh += 1
        t = {k: r.choice(v) for k, v in LUOI.items()}
        khoa = json.dumps(t, sort_keys=True)
        if khoa in thay:
            continue
        thay.add(khoa)
        ra.append({**THAM_MAC_DINH, **t})
    return ra


def chia_lat(tong: int, so: int) -> list[tuple[int, int]]:
    """Chia dãy nến thành `so` lát LIÊN TIẾP, không chồng nhau.

    Không xáo trộn: thị trường có trí nhớ, và trộn lát là cho phép một biến thể
    nhìn thấy tương lai của chính đoạn đang chấm nó.
    """
    b = tong // so
    return [(i * b, (i + 1) * b if i < so - 1 else tong) for i in range(so)]


def cham(bien: list[dict], diem: list[list[list]], so_lat: int) -> list[dict]:
    """Gộp điểm rồi xếp hạng. Hàm THUẦN — kiểm được bằng số bịa."""
    bang = []
    for i, tham in enumerate(bien):
        theo_lat, tong_n, tong_r = [], 0, 0.0
        for j in range(so_lat):
            ds = diem[i][j]
            n = sum(x[1] for x in ds)
            if not n:
                theo_lat.append(None)
                continue
            kv = sum(r * c for r, c in ds) / n
            theo_lat.append(round(kv, 3))
            tong_n += n
            tong_r += kv * n
        co = [x for x in theo_lat if x is not None]
        bang.append({
            "i": i, "tham": {k: tham[k] for k in LUOI if k in tham},
            "theoLat": theo_lat, "soLatDuong": sum(1 for x in co if x > 0),
            "soLatCo": len(co), "soLenh": tong_n,
            "kyVongGop": round(tong_r / tong_n, 4) if tong_n else None,
        })
    # Số lát dương TRƯỚC, kỳ vọng gộp SAU. Đảo thứ tự này là quay lại đúng cách
    # đã hỏng ba lần — chọn theo một con số gộp mà một lát tốt kéo lên.
    bang.sort(key=lambda x: (-(x["soLatDuong"]), -(x["kyVongGop"] if x["kyVongGop"] is not None else -9)))
    return bang


def main() -> int:
    cho_ds = _cho_ds()
    so_bien = int(_co("--bien", 12))
    so_lat = int(_co("--lat", 4))
    hat = int(_co("--hat", 20260829))
    bien = bien_the(so_bien, hat)
    t0 = time.time()

    print(f"LÒ LUYỆN · {len(cho_ds)} chợ × {so_lat} lát × {len(bien)} biến thể "
          f"(1 champion + {len(bien) - 1} thử) · hạt {hat}")
    print("tiền ảo, sàn giấy, GIÁ THẬT — cùng RiskEngine và mô hình chi phí của "
          "bản chạy thật" + NL)

    diem: list[list[list]] = [[[] for _ in range(so_lat)] for _ in bien]
    so_cho_that = 0

    for ten in cho_ds:
        sym, _, tf = ten.partition(":")
        tf = tf or CONFIG["timeframes"]["primary"]
        nen = _nap(sym, tf)
        if not nen:
            continue
        nc = nen[tf]
        if len(nc) < 400:
            print(f"    bỏ qua {ten} — chỉ {len(nc)} nến")
            continue
        so_cho_that += 1
        chuoi = huanluyen.lay_chuoi(nen, sym)[0]
        lats = chia_lat(len(nc), so_lat)
        print(f"  {ten} · {len(nc)} nến · chuỗi {len(chuoi)} điểm "
              f"({time.time() - t0:.0f}s)")

        for i, tham in enumerate(bien):
            for j, (a, b) in enumerate(lats):
                kq = huanluyen.chay_lai(nen, symbol=sym, chuoi=chuoi, tham=tham,
                                        tu_nen=a, den_nen=b, bo_qua_kill=True)
                tk = kq["thongKe"]
                if tk["so"] and tk["kyVongR"] is not None:
                    diem[i][j].append((tk["kyVongR"], tk["so"]))

    if not so_cho_that:
        print("Không chợ nào dùng được.")
        return 1

    bang = cham(bien, diem, so_lat)

    print(NL + f"{'biến thể':>9}  {'lát dương':>10} {'kỳ vọng gộp':>13} "
          f"{'lệnh':>6}   theo từng lát")
    print("─" * 92)
    for r in bang[:12]:
        ten = "CHAMPION" if r["i"] == 0 else f"#{r['i']}"
        lat = " ".join(f"{x:+.2f}" if x is not None else "  —  " for x in r["theoLat"])
        print(f"{ten:>9}  {r['soLatDuong']:>4}/{r['soLatCo']:<5} "
              f"{(r['kyVongGop'] or 0):+13.4f} {r['soLenh']:>6}   {lat}")

    cha = next(r for r in bang if r["i"] == 0)
    can = so_lat // 2 + 1
    tot = [r for r in bang if r["i"] != 0 and r["soLatDuong"] >= can
           and (r["kyVongGop"] if r["kyVongGop"] is not None else -9)
           > (cha["kyVongGop"] if cha["kyVongGop"] is not None else -9)]

    print(NL + f"champion: {cha['soLatDuong']}/{cha['soLatCo']} lát dương · "
          f"gộp {(cha['kyVongGop'] or 0):+.4f}R qua {cha['soLenh']} lệnh "
          f"trên {so_cho_that} chợ")
    print(f"{len(tot)}/{len(bien) - 1} biến thể vượt champion VÀ dương "
          f"≥{can}/{so_lat} lát.")
    if tot:
        t = tot[0]
        print(f"  dẫn đầu #{t['i']}: {json.dumps(t['tham'], ensure_ascii=False)}")
        print(f"  ĐÃ THỬ {len(bien) - 1} BIẾN THỂ — cái 'tốt nhất' trong ngần ấy lần "
              f"thử đẹp lên một phần chỉ vì đã thử ngần ấy lần. Trước khi tin: khai "
              f"giả thuyết rồi đo lại trên chợ CHƯA dùng ở lượt này.")
    else:
        print("  Không biến thể nào qua cả hai cửa. Đó là một kết quả, "
              "không phải một thất bại.")

    if GHI:
        f = DATA_DIR / "lo-luyen.json"
        tam = f.with_suffix(f".{os.getpid()}.tmp")
        tam.write_text(json.dumps({
            "luc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
            "cho": cho_ds, "soCho": so_cho_that, "soLat": so_lat,
            "soLanThu": len(bien) - 1, "hat": hat,
            "giay": round(time.time() - t0, 1),
            "bang": bang[:20],
        }, ensure_ascii=False, indent=1), encoding="utf-8")
        os.replace(tam, f)
        print(NL + f"đã ghi {f.name} ({time.time() - t0:.0f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
