"""ĐO KHUNG — khung nào CHO PHÉP một cái stop sống được và một mục tiêu với tới?

    python scripts/do-khung.py
    python scripts/do-khung.py --ghi          ghi data/do-khung.json
    python scripts/do-khung.py --coin BTCUSDT --khung 1h,4h,1d

Đo được trên 1h: stop đủ rộng để sống qua nhiễu và mục tiêu đủ gần để với tới
LOẠI TRỪ NHAU ở minRR 2,0. Câu hỏi treo lại: đó là sự thật về **thị trường**, hay
chỉ là sự thật về **khung 1h**?

PHÉP ĐO NÀY KHÔNG CẦN CHIẾN LƯỢC NÀO

Cố ý. Nếu đo bằng cách chạy lại một bộ luật thì kết quả trộn hai thứ: khung có
hợp không, và bộ luật có chọn đúng điểm vào không. Tách ra bằng cách bỏ hẳn phần
chọn: vào lệnh ở MỌI nến, stop cố định `k×ATR`, rồi xem giá đi tới đâu.

Con số ra không phải một chiến lược — không ai vào lệnh ở mọi nến. Nó là **trần
trên của hình học**: nếu ngay cả khi vào ngẫu nhiên mà tỉ lệ chạm 2R trước stop
đã dưới mức hoà vốn, thì không điểm vào nào cứu được, và ngược lại nếu nó cao thì
chỗ đáng sửa là bộ chọn điểm vào chứ không phải khung.

HAI CHỖ PHẢI ĐỌC CẨN THẬN

Trong MỘT cây nến, không biết đỉnh hay đáy tới trước. Ở đây khi cả mục tiêu lẫn
stop cùng nằm trong biên độ một nến, phần thắng được tính cho MỤC TIÊU. Nghĩa là
mọi con số dưới đây là **trần trên lạc quan** — thực tế sẽ thấp hơn. Chọn thiên
vị theo hướng này có chủ ý: nếu ngay cả trần trên lạc quan đã âm thì kết luận
"khung này không đỡ nổi mức RR đó" là chắc chắn, không cần cãi.

Và

Các khung KHÔNG phủ cùng một đoạn lịch sử (xem `tai-lich-su.py`): 1d thấy cả chu
kỳ 2022, 5m chỉ thấy sáu tuần gần nhất. Nên chênh lệch giữa hai khung là chênh
lệch của **khung cộng với thời kỳ**, không phải của riêng khung.
"""
from __future__ import annotations

import datetime as _dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from trader.config import CONFIG, DATA_DIR, ROOT  # noqa: E402
from trader.indicators import atr as _atr  # noqa: E402

GHI = "--ghi" in sys.argv
GIU = 48          # nến giữ tối đa — cùng luật với bản chạy thật
STOP_ATR = 1.5    # đúng bội số champion đang dùng
MUC = (1.0, 1.5, 2.0, 3.0)
BUOC = 3          # xét mỗi 3 nến, đủ dày mà không đếm gần như trùng nhau


def _dsach(co: str, mac_dinh: list[str]) -> list[str]:
    if co not in sys.argv:
        return mac_dinh
    return [x.strip() for x in sys.argv[sys.argv.index(co) + 1].split(",") if x.strip()]


def _nap(sym: str, tf: str) -> list[dict]:
    f = ROOT / "data" / "lich-su" / f"{sym}-{tf}.json"
    if not f.exists():
        return []
    d = json.loads(f.read_text(encoding="utf-8"))
    return d if isinstance(d, list) else []


def do_mot(nen: list[dict], drag_bps: float) -> dict | None:
    """Với mọi điểm vào, đo mục tiêu nào tới trước stop — cho cả hai chiều."""
    if len(nen) < 220 + GIU:
        return None
    a = _atr(nen, 14)
    ra = {m: {"LONG": [0, 0], "SHORT": [0, 0]} for m in MUC}
    lui = []          # lùi ngược tối đa TRƯỚC lúc chạm 2R, ở những lệnh có chạm
    n = 0

    for i in range(210, len(nen) - GIU - 1, BUOC):
        atr = a[i]
        if not atr:
            continue
        vao = nen[i]["c"]
        rui = STOP_ATR * atr
        drag = vao * drag_bps / 10_000
        rui_that = rui + drag
        if rui_that <= 0:
            continue
        n += 1
        cua = nen[i + 1: i + 1 + GIU]

        for chieu in ("LONG", "SHORT"):
            dai = chieu == "LONG"
            stop = vao - rui if dai else vao + rui
            xa_nhat = 0.0
            lui_toi_da = 0.0
            da = set()
            cham_2r_lui = None
            for c in cua:
                if dai:
                    nguoc = (vao - c["l"]) / rui_that
                    thuan = (c["h"] - vao - drag) / rui_that
                    het = c["l"] <= stop
                else:
                    nguoc = (c["h"] - vao) / rui_that
                    thuan = (vao - c["l"] - drag) / rui_that
                    het = c["h"] >= stop
                if thuan < 2.0:
                    lui_toi_da = max(lui_toi_da, nguoc)
                xa_nhat = max(xa_nhat, thuan)
                for m in MUC:
                    if m in da:
                        continue
                    if xa_nhat >= m:
                        ra[m][chieu][0] += 1      # chạm mục tiêu trước
                        da.add(m)
                        if m == 2.0 and cham_2r_lui is None:
                            cham_2r_lui = lui_toi_da
                    elif het:
                        ra[m][chieu][1] += 1      # dính stop trước
                        da.add(m)
                if het or len(da) == len(MUC):
                    break
            for m in MUC:
                if m not in da:
                    ra[m][chieu][1] += 1          # hết cửa sổ, chưa chạm
            if cham_2r_lui is not None:
                lui.append(cham_2r_lui)

    if not n:
        return None
    out = {"soDiem": n, "muc": {}}
    for m in MUC:
        cham = ra[m]["LONG"][0] + ra[m]["SHORT"][0]
        tong = cham + ra[m]["LONG"][1] + ra[m]["SHORT"][1]
        ty = cham / tong if tong else 0
        # Kỳ vọng của cược máy móc: thắng thì +m, thua thì −1.
        out["muc"][str(m)] = {"tyLeCham": round(ty * 100, 1),
                              "kyVongR": round(ty * m - (1 - ty), 3),
                              "hoaVonCanTyLe": round(1 / (1 + m) * 100, 1)}
    lui.sort()
    out["luiTruocKhiCham2R"] = round(lui[len(lui) // 2], 2) if lui else None
    return out


def main() -> int:
    coins = _dsach("--coin", ["BTCUSDT", "ETHUSDT", "SOLUSDT"])
    tfs = _dsach("--khung", ["5m", "15m", "30m", "1h", "4h", "1d"])
    r = CONFIG["risk"]
    drag = r["feeBps"] + r["slippageBps"]
    print(f"stop {STOP_ATR}×ATR · giữ {GIU} nến · chi phí {drag}bps mỗi đầu · "
          f"vào ở mọi nến (bước {BUOC})\n")

    ra: dict = {}
    for sym in coins:
        print(f"── {sym}")
        print(f"   {'khung':7}{'điểm':>7}" + "".join(f"{('  ' + str(m) + 'R'):>16}" for m in MUC)
              + f"{'lùi trước 2R':>14}")
        for tf in tfs:
            nen = _nap(sym, tf)
            if not nen:
                print(f"   {tf:7}   (chưa tải)")
                continue
            k = do_mot(nen, drag)
            if not k:
                print(f"   {tf:7}   (không đủ nến)")
                continue
            # QUÃNG THỜI GIAN của chính khung này.
            #
            # Bảng này so các KHUNG với nhau, mà các khung phủ những quãng hoàn
            # toàn khác nhau: 5m có 41 ngày (07–08/2026) còn 1d có 1499 ngày
            # (2022–2026). Kết luận "khung càng dài càng gần hoà vốn" vì thế có
            # thể là kết luận về BỐN NĂM so với BỐN MƯƠI NGÀY, không phải về
            # khung — và chính bảng này đã dẫn tới quyết định đổi 1h sang 4h.
            #
            # Không sửa được bằng cách tải thêm: 5m phủ 1499 ngày là 431.000
            # nến. Cái sửa được là NÓI RA, để không ai đọc bảng như thể cùng kỳ.
            _t = [x.get("t") for x in nen if x.get("t")]
            if _t:
                import datetime as _d
                k["quang"] = {
                    "tu": _d.datetime.fromtimestamp(
                        min(_t) / 1000, _d.timezone.utc).strftime("%Y-%m-%d"),
                    "den": _d.datetime.fromtimestamp(
                        max(_t) / 1000, _d.timezone.utc).strftime("%Y-%m-%d"),
                    "soNgay": round((max(_t) - min(_t)) / 86_400_000),
                }
            ra.setdefault(sym, {})[tf] = k
            cot = ""
            for m in MUC:
                v = k["muc"][str(m)]
                cot += f"{v['tyLeCham']:>8.1f}%{v['kyVongR']:>+8.3f}"
            print(f"   {tf:7}{k['soDiem']:>7}{cot}{(k['luiTruocKhiCham2R'] or 0):>14.2f}R")
        print()

    print("Đọc: mỗi ô là «tỉ lệ chạm mục tiêu trước stop» và «kỳ vọng của cược máy móc».")
    print(f"Hoà vốn cần: 1R→50,0%  1.5R→40,0%  2R→33,3%  3R→25,0%")
    print("Kỳ vọng DƯƠNG ở đây KHÔNG phải một chiến lược — nó là trần trên của hình học:")
    print("nếu vào ngẫu nhiên đã dương thì chỗ đáng sửa là bộ chọn điểm vào, không phải khung.")

    if GHI:
        f = DATA_DIR / "do-khung.json"
        # `luc`: mtime chỉ nói "lần ghi cuối", không nói "đo trên dữ liệu tới lúc
        # nào" — một lượt hỏng nửa chừng vẫn chạm file và làm kho trông tươi.
        f.write_text(json.dumps({"luc": _dt.datetime.now(_dt.timezone.utc)
                                 .isoformat(timespec="seconds"),
                                 "stopAtr": STOP_ATR, "giu": GIU, "buoc": BUOC,
                                 "dragBps": drag, "ket": ra}, ensure_ascii=False, indent=1),
                     encoding="utf-8")
        print(f"\nđã ghi {f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
