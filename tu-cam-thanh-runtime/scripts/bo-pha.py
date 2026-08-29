"""BỘ PHÁ — việc duy nhất của nó là tìm chỗ chiến lược CHẾT.

    python scripts/bo-pha.py                          champion, khung trong config
    python scripts/bo-pha.py --cho BTCUSDT:4h --ma MOCK_RULES_V1
    python scripts/bo-pha.py --ghi

Cửa duyệt hiện tại hỏi "bộ này có dương ngoài mẫu không". Câu đó chưa đủ. Một
chiến lược dương ngoài mẫu vẫn có thể chết ngay khi phí nhích lên, hoặc chỉ sống
được vì đoạn ngoài mẫu tình cờ là một đoạn thị trường dễ.

Bộ phá hỏi ngược lại: **cần điều kiện tệ tới đâu thì bộ này mới thua?** Nếu câu
trả lời là "chỉ cần phí gấp đôi", thì con số dương kia không phải lợi thế — nó
là biên độ nằm gọn trong sai số của giả định chi phí.

BỐN ĐÒN

    phí gấp đôi     15bps → 30bps mỗi đầu. Sàn kém thanh khoản, lệnh to, giờ
                    xấu — mọi thứ đều đẩy chi phí thật lên trên giả định.
    phí gấp ba      45bps. Ngưỡng này không phải để đạt, mà để biết mình cách
                    vực bao xa.
    đoạn xấu nhất   K cửa sổ mà mua-và-giữ lỗ nặng nhất. Một chiến lược thuận
                    xu hướng dương trên toàn kỳ có thể chỉ dương nhờ thị trường
                    tăng, và chết sạch ở đúng chỗ cần nó nhất.
    biến động cao   K cửa sổ ATR% cao nhất. Chỗ stop bị quét nhiều nhất.

MỘT CHỖ PHẢI ĐỌC CẨN THẬN

Cửa sổ xấu nhất được chọn BẰNG CÁCH NHÌN TOÀN BỘ LỊCH SỬ — tức là có nhìn trước.
Cố ý: đây không phải phép đo lợi thế, nó là **bài kiểm tra chịu đựng**. Con số
ra không so được với kỳ vọng ngoài mẫu, và không được đem đi khoe như một kết
quả backtest.
"""
from __future__ import annotations

import datetime as _dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from trader import huanluyen as HL  # noqa: E402
from trader import data as DATA  # noqa: E402
from trader.config import CONFIG, DATA_DIR, ROOT  # noqa: E402

GHI = "--ghi" in sys.argv
CUA_SO = 200      # độ dài mỗi cửa sổ căng thẳng, tính bằng nến
SO_CUA_SO = 5     # lấy mấy cửa sổ tệ nhất
NGU_CANH = {"5m": "30m", "15m": "1h", "30m": "4h", "1h": "4h", "4h": "1d", "1d": "1d"}


def _co(ten: str, mac_dinh=None):
    return sys.argv[sys.argv.index(ten) + 1] if ten in sys.argv else mac_dinh


def _nap(sym: str, chinh: str, ctx: str):
    kho = ROOT / "data" / "lich-su"
    nen = {}
    for tf in (chinh, ctx):
        f = kho / f"{sym}-{tf}.json"
        if not f.exists():
            return None
        nen[tf] = json.loads(f.read_text(encoding="utf-8"))
    cu = DATA.qua_cu(nen[chinh], chinh)
    if cu is not None:
        print(f"  bỏ qua {sym}:{chinh} — nến cuối cách đây {cu:.0f} ngày (chợ chết)")
        return None
    CONFIG["timeframes"]["primary"] = chinh
    CONFIG["timeframes"]["context"] = ctx
    return nen


def _cua_so_xau(nc: list[dict], theo: str) -> list[tuple[int, int, float]]:
    """K cửa sổ tệ nhất, không chồng lấn nhau.

    Không chặn chồng lấn thì năm cửa sổ "tệ nhất" hoá ra là năm lát cắt của cùng
    một cú sập, và bài kiểm tra chịu đựng chỉ kiểm đúng một sự kiện.
    """
    ds = []
    for i in range(HL.KHOI_DONG, len(nc) - CUA_SO, 10):
        w = nc[i:i + CUA_SO]
        if theo == "lo":
            diem = (w[-1]["c"] - w[0]["c"]) / w[0]["c"]        # càng âm càng tệ
        else:
            diem = -sum((c["h"] - c["l"]) / c["c"] for c in w) / len(w)  # ATR% càng cao
        ds.append((i, diem))
    ds.sort(key=lambda x: x[1])
    ra: list[tuple[int, int, float]] = []
    for i, diem in ds:
        if all(abs(i - j) >= CUA_SO for j, _, _ in ra):
            ra.append((i, i + CUA_SO, diem))
        if len(ra) >= SO_CUA_SO:
            break
    return ra


def _tk(nen, chuoi, sym, ma, rieng=None, tu=0, den=None) -> dict:
    return HL.chay_lai(nen, symbol=sym, chuoi=chuoi, bo_luat=ma, rieng=rieng,
                       tu_nen=tu, den_nen=den, bo_qua_kill=True)["thongKe"]


def main() -> int:
    cho = _co("--cho", f"{CONFIG['symbol']}:{CONFIG['timeframes']['primary']}")
    sym, _, chinh = cho.partition(":")
    chinh = chinh or CONFIG["timeframes"]["primary"]
    ctx = NGU_CANH.get(chinh, "4h")
    nen = _nap(sym, chinh, ctx)
    if nen is None:
        print(f"chưa tải nến {sym} {chinh}/{ctx}")
        return 1
    nc = nen[chinh]
    ma = _co("--ma", "MOCK_RULES_V1")
    chuoi, tu_dau = HL.lay_chuoi(nen, sym)
    r = CONFIG["risk"]
    print(f"BỘ PHÁ · {ma} trên {cho} (ngữ cảnh {ctx}) · {len(nc)} nến · chuỗi {len(chuoi)} ({tu_dau})\n")

    goc = _tk(nen, chuoi, sym, ma)
    print(f"{'đòn':30}{'lệnh':>7}{'kỳ vọng':>11}{'thắng':>9}{'sụt giảm':>11}")
    print("─" * 68)

    def _dong(nhan: str, tk: dict) -> None:
        kv = tk.get("kyVongR")
        n = tk.get("so") or 0
        c_kv = f"{kv:+.3f}" if kv is not None else "—"
        c_th = f"{tk.get('tyLeThang') or 0:.1f}%" if n else "—"
        c_sg = f"{tk.get('sutGiamToiDaPct') or 0:.1f}%"
        print(f"{nhan:30}{n:>7}{c_kv:>11}{c_th:>9}{c_sg:>11}")

    ket = {"goc": goc, "don": {}}
    _dong("gốc (toàn kỳ, phí thường)", goc)

    for boi in (2, 3):
        tk = _tk(nen, chuoi, sym, ma,
                 rieng={"feeBps": r["feeBps"] * boi, "slippageBps": r["slippageBps"] * boi})
        ket["don"][f"phi-x{boi}"] = tk
        _dong(f"phí ×{boi} ({(r['feeBps'] + r['slippageBps']) * boi}bps/đầu)", tk)

    for theo, nhan in (("lo", "đoạn mua-giữ lỗ nặng nhất"), ("bien", "đoạn biến động cao nhất")):
        cs = _cua_so_xau(nc, theo)
        gop = {"so": 0, "tongR": 0.0, "thang": 0, "sut": 0.0}
        for tu, den, _ in cs:
            tk = _tk(nen, chuoi, sym, ma, tu=tu, den=den)
            n = tk.get("so") or 0
            if not n:
                continue
            gop["so"] += n
            gop["tongR"] += (tk.get("kyVongR") or 0) * n
            gop["thang"] += round((tk.get("tyLeThang") or 0) / 100 * n)
            gop["sut"] = max(gop["sut"], tk.get("sutGiamToiDaPct") or 0)
        t = {"so": gop["so"],
             "kyVongR": round(gop["tongR"] / gop["so"], 3) if gop["so"] else None,
             "tyLeThang": round(gop["thang"] / gop["so"] * 100, 1) if gop["so"] else 0,
             "sutGiamToiDaPct": round(gop["sut"], 2)}
        ket["don"][theo] = t
        _dong(f"{nhan} ({len(cs)}×{CUA_SO} nến)", t)

    print()
    # HAI KIỂU CHẾT, và gộp chúng lại là nói nhầm:
    #
    #   TẮT TIẾNG   số lệnh sụt gần hết — không phải thua, mà là không còn lệnh
    #               nào qua nổi cửa `minRR`. Chiến lược im lặng, tài khoản đứng yên.
    #   THUA        vẫn vào lệnh bình thường nhưng kỳ vọng âm.
    #
    # Bản đầu tôi gộp cả hai vào "chết ở phí ×2" — đúng là nó không sống, nhưng
    # câu ấy khiến người đọc tưởng chiến lược mất tiền, trong khi thực tế nó
    # ngừng giao dịch. Hai chuyện cần hai cách sửa khác nhau.
    goc_n = goc.get("so") or 0
    goc_kv = goc.get("kyVongR")
    tat, thua, song = [], [], []
    for k, v in ket["don"].items():
        n = v.get("so") or 0
        if goc_n and n < goc_n * 0.2:
            tat.append(f"{k} (còn {n}/{goc_n} lệnh)")
        elif (v.get("kyVongR") or -9) > 0:
            song.append(k)
        else:
            thua.append(k)

    if goc_kv is None or goc_kv <= 0:
        print(f"Gốc đã âm ({goc_kv:+.3f}R qua {goc_n} lệnh) — bộ phá không có gì để phá. "
              f"Sửa chiến lược trước, đo chịu đựng sau.")
    elif not tat and not thua:
        print("Sống qua CẢ BỐN đòn. Hiếm, và đáng ghi vào sổ giả thuyết.")
    if tat:
        print(f"TẮT TIẾNG ở: {', '.join(tat)} — không phải thua, mà là cửa minRR "
              f"{r['minRR']} chặn hết vì chi phí đội lên. Chiến lược đứng im, không mất "
              f"tiền, và cũng không làm được gì.")
    if thua:
        print(f"THUA ở: {', '.join(thua)} — vẫn vào lệnh bình thường nhưng kỳ vọng âm.")
    print("\nCửa sổ căng thẳng được chọn bằng cách nhìn toàn bộ lịch sử (có nhìn trước).")
    print("Đây là bài kiểm tra CHỊU ĐỰNG, không phải phép đo lợi thế — đừng so với ngoài mẫu.")

    if GHI:
        f = DATA_DIR / "bo-pha.json"
        f.write_text(json.dumps({"luc": _dt.datetime.now(_dt.timezone.utc)
                                 .isoformat(timespec="seconds"),
                                 "cho": cho, "ma": ma, "cuaSo": CUA_SO,
                                 "soCuaSo": SO_CUA_SO, "ket": ket},
                                ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\nđã ghi {f.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
