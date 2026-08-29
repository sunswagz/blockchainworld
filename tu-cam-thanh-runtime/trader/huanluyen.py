"""HUẤN LUYỆN — chạy lại lịch sử để đo, rồi dò tham số để cải thiện.

Backtest là thứ dễ nói dối nhất trong cả hệ thống, vì nó luôn cho ra một con số
đẹp nếu mình không chặn. Bốn đường nói dối, và cách chặn từng đường:

1. **Nhìn trộm tương lai.** Feature ở nến `i` chỉ được đọc `candles[:i+1]`, và
   khung ngữ cảnh chỉ được lấy những nến đã ĐÓNG trước thời điểm đó. Cắt lát
   sai một nến là win rate đẹp lên mà không ai thấy vì sao.

2. **Nhập nhằng trong lòng nến.** Một nến chạm cả SL lẫn TP thì OHLC không cho
   biết cái nào tới trước. Ở đây luôn tính **SL trước** — chọn kiểu lạc quan là
   cách nhanh nhất để có một chiến lược trên giấy không bao giờ tồn tại thật.

3. **Quên chi phí.** Phí và trượt giá tính ở CẢ hai đầu, đúng công thức của
   `risk.py`. Bỏ chi phí ra thì mọi chiến lược tần suất cao đều thắng.

4. **Dò tham số rồi khoe chính con số đã dò.** Đây là đường tệ nhất vì nó
   trông giống hệt tiến bộ thật. Nên mọi lượt dò đều cắt đôi dữ liệu: chọn trên
   phần TRONG MẪU, rồi báo cáo trên phần NGOÀI MẪU chưa từng đụng tới. Chênh
   lệch giữa hai con số chính là mức khớp trội, và nó được hiện thẳng ra.

Bộ não dùng ở đây là bộ luật xác định (`mock_thesis`) chứ không gọi model: chạy
lại 2000 nến mà mỗi nến một lượt gọi thì vừa hết tiền vừa mất tính lặp lại — và
thứ cần dò ở đây là NGƯỠNG của luật, không phải văn phong của model.
"""
from __future__ import annotations

import bisect
import statistics
import time
from typing import Any, Callable

from .brain import suy_luan
from .bus import bus
from .config import CONFIG, ROOT
from .features import features_for
from .regime import classify
from .risk import RiskEngine

# Số nến tối thiểu trước khi được phép ra quyết định đầu tiên. EMA200 cần 200
# nến mới có giá trị; quyết định khi nó còn None là quyết định trên một feature
# rỗng, và regime sẽ luôn ra UNKNOWN theo một kiểu vô nghĩa.
KHOI_DONG = 210

# Phiên bản HÌNH DẠNG chuỗi tín hiệu. Nằm trong vân tay cache, nên đổi số này là
# mọi cache cũ tự bị bỏ và sinh lại.
#
# Bắt buộc phải có: cache gắn vân tay theo dữ liệu và khung thời gian, KHÔNG
# theo tập feature. Thêm một trường vào `feat` mà quên bỏ cache thì chiến lược
# mới đọc trường đó ra None ở mọi điểm — nó không lỗi, chỉ lặng lẽ không bao giờ
# vào lệnh, và bảng kết quả hiện "0 lệnh" trông y như chiến lược tồi.
#   v1 — price, adx, rsi14, emaStack, atr
#   v2 — thêm feature cho chiến lược biên, và GIỮ LẠI cả chế độ RANGE
# v3: thêm atrRatioVsMedian, swingHighs/Lows và _raw.ema20 cho hai bộ luật mới.
# Nâng số này là BẮT BUỘC khi đổi hình dạng `feat` — cache cũ không có trường mới
# nên nó trả None lặng lẽ, và bộ luật sẽ NO_TRADE 100% mà không ai biết vì sao.
PHIEN_BAN_CHUOI = 3


def _trang_thai(nen_chinh: list[dict], nen_ngu_canh: list[dict], moc_ctx: list[int],
                i: int, tf_chinh: str, tf_ngu_canh: str, symbol: str,
                cua_so: int) -> dict | None:
    """Dựng market state ĐÚNG như lúc chạy thật, tại nến thứ `i`.

    Cửa sổ bị chặn ở `cua_so` = `data.candleLimit`, đúng bằng số nến mà vòng
    chạy thật xin về. Lần viết đầu tôi cho lát nến lớn dần tới hết lịch sử —
    tới nến thứ 3800 thì chỉ báo được nhìn 3800 nến trong khi bản chạy thật
    không bao giờ thấy quá 400. Sai đó không làm gì đổ; nó chỉ khiến kết quả
    backtest thuộc về một hệ thống khác với hệ thống sắp chạy bằng tiền thật.
    Chặn đúng cửa sổ vừa trung thực hơn vừa biến O(n²) thành tuyến tính.
    """
    dau = max(0, i + 1 - cua_so)
    lat_chinh = nen_chinh[dau: i + 1]
    if i + 1 < KHOI_DONG:
        return None
    # Khung ngữ cảnh: chỉ những nến đã đóng tính tới thời điểm này. Tìm bằng
    # nhị phân trên mốc thời gian — quét tuyến tính ở đây là thêm một vòng O(n)
    # nữa vào một vòng lặp vốn đã chạy vài nghìn lượt.
    j = bisect.bisect_right(moc_ctx, lat_chinh[-1]["t"])
    lat_ctx = nen_ngu_canh[max(0, j - cua_so): j]
    if len(lat_ctx) < 60:
        return None
    return {
        "symbol": symbol,
        "price": lat_chinh[-1]["c"],
        "source": {"name": "chạy lại", "live": False},
        "timeframes": {tf_chinh: features_for(lat_chinh), tf_ngu_canh: features_for(lat_ctx)},
    }


def _thoat(nen: list[dict], tu: int, side: int, entry: float, sl: float,
           tp: float, toi_da_nen: int, cost_bps: float) -> tuple[str, float, int]:
    """Đi tới trong tương lai tìm điểm thoát. Trả (lý do, giá thoát, số nến giữ).

    Luật quan trọng nhất nằm ở đây: nến nào chạm CẢ SL lẫn TP thì tính SL.
    """
    for k in range(tu + 1, min(tu + 1 + toi_da_nen, len(nen))):
        n = nen[k]
        cham_sl = (n["l"] <= sl) if side == 1 else (n["h"] >= sl)
        cham_tp = (n["h"] >= tp) if side == 1 else (n["l"] <= tp)
        if cham_sl:
            # Bi quan có chủ đích: cùng một nến chạm cả hai thì coi như SL trước.
            gia = sl * (1 - cost_bps) if side == 1 else sl * (1 + cost_bps)
            return ("SL", gia, k - tu)
        if cham_tp:
            gia = tp * (1 - cost_bps) if side == 1 else tp * (1 + cost_bps)
            return ("TP", gia, k - tu)
    # Hết hạn giữ: thoát ở giá đóng cửa nến cuối cùng nhìn được.
    cuoi = min(tu + toi_da_nen, len(nen) - 1)
    gia = nen[cuoi]["c"]
    gia = gia * (1 - cost_bps) if side == 1 else gia * (1 + cost_bps)
    return ("HET_HAN", gia, cuoi - tu)


def sinh_luan_diem(nen: dict[str, list[dict]], *, symbol: str = "BTCUSDT",
                   bao_tien_do: Callable[[int, int], None] | None = None,
                   chi_muc: list[int] | None = None) -> list[dict]:
    """Chạy feature → regime trên từng nến, trả về chuỗi TÍN HIỆU thô.

    Ranh giới ở đây là điều quan trọng nhất của cả module. Chuỗi này chứa
    **những gì đo được từ thị trường** — feature và chế độ — và tuyệt đối
    không chứa quyết định nào. Quyết định (vào hay không, SL đặt đâu, TP bao
    xa) là việc của chiến lược, và chiến lược chính là thứ đang được đem ra dò.

    Chia vậy vì phần đo là toàn bộ chi phí: chỉ báo phải tính lại trên cửa sổ
    400 nến ở mỗi bước, ~340 giây cho sáu tháng. Còn phần quyết định thì rẻ.
    Cache phần đắt, chạy lại phần rẻ ⇒ dò hàng trăm tổ hợp trong vài giây, mà
    mọi tổ hợp chắc chắn nhìn cùng một thị trường.

    Lần đầu tôi nhét luôn cả luận điểm vào chuỗi này. Hậu quả: 108 tổ hợp cho
    ra kết quả y hệt nhau, vì cái duy nhất còn được phép đổi là mấy ngưỡng mà
    bộ luật vốn đã tự dựng mục tiêu để vừa khít.
    """
    tf_chinh = CONFIG["timeframes"]["primary"]
    tf_ctx = CONFIG["timeframes"]["context"]
    nc, nx = nen[tf_chinh], nen[tf_ctx]
    moc_ctx = [x["t"] for x in nx]
    cua_so = CONFIG["data"]["candleLimit"]

    chuoi: list[dict] = []
    cuoi = len(nc) - 1
    # `chi_muc` cho phép tính LẺ vài nến thay vì cả chuỗi — đường dùng lại cache
    # sau khi có nến mới. None nghĩa là tính hết, đúng như trước.
    can = list(range(KHOI_DONG, cuoi)) if chi_muc is None else         [i for i in chi_muc if KHOI_DONG <= i < cuoi]
    for _k, i in enumerate(can):
        if bao_tien_do and _k % 50 == 0:
            bao_tien_do(_k, len(can))
        st = _trang_thai(nc, nx, moc_ctx, i, tf_chinh, tf_ctx, symbol, cua_so)
        if st is None:
            continue
        rg = classify(st, tf_chinh, tf_ctx)
        # Chế độ hoàn toàn không đọc được thì bỏ. RANGE thì GIỮ — trước đây nó
        # bị loại cùng nhóm, và hậu quả là không thể đo nổi một chiến lược biên
        # trên chính đoạn dữ liệu mà thị trường đi ngang phần lớn thời gian.
        if rg["primary"] == "UNKNOWN":
            continue
        p = st["timeframes"][tf_chinh]
        chuoi.append({
            "i": i, "t": nc[i]["t"], "price": st["price"], "atr": p["_raw"]["atr"],
            "regime": rg,
            # Đúng những trường mà các bộ luật đọc, không hơn. Chuỗi này bị ghi
            # ra đĩa; giữ cả bảng feature làm nó nặng gấp mấy chục lần mà không
            # thêm thông tin nào dùng được. Thêm trường ở đây phải nâng
            # PHIEN_BAN_CHUOI, nếu không cache cũ sẽ trả None lặng lẽ.
            "feat": {
                "price": p["price"], "adx": p.get("adx"), "rsi14": p.get("rsi14"),
                "emaStack": p.get("emaStack"), "_raw": {"atr": p["_raw"]["atr"],
                                         "ema20": p["_raw"].get("ema20")},
                # cho chiến lược biên
                "bbPosition": p.get("bbPosition"), "bbWidthPct": p.get("bbWidthPct"),
                "range20High": p.get("range20High"), "range20Low": p.get("range20Low"),
                "distToRange20LowPct": p.get("distToRange20LowPct"),
                "distToRange20HighPct": p.get("distToRange20HighPct"),
                "volumeRatio": p.get("volumeRatio"), "atrPct": p.get("atrPct"),
                "structure": p.get("structure"),
                # cho chiến lược kéo lùi và bung nén
                "atrRatioVsMedian": p.get("atrRatioVsMedian"),
                "swingHighs": p.get("swingHighs"), "swingLows": p.get("swingLows"),
            },
        })
    if bao_tien_do:
        bao_tien_do(len(can), len(can))
    return chuoi


def chay_lai(nen: dict[str, list[dict]], *, symbol: str = "BTCUSDT",
             chuoi: list[dict] | None = None,
             rieng: dict | None = None, tham: dict | None = None,
             bo_luat: str = "MOCK_RULES_V1",
             tu_nen: int = 0, den_nen: int | None = None,
             toi_da_nen_giu: int = 48, bo_qua_kill: bool = False,
             bao_tien_do: Callable[[int, int], None] | None = None) -> dict:
    """Chạy lại một đoạn nến, trả về từng lệnh và thống kê.

    `tham` xoay CHIẾN LƯỢC (SL mấy ATR, TP bao xa, vào ở chế độ nào).
    `rieng`  xoay NGƯỠNG RỦI RO (minRR, minConfidence…).
    `chuoi`  là tín hiệu dựng sẵn từ `sinh_luan_diem`; không truyền thì tự tính.

    Hai nhóm tham số tách bạch vì chúng thuộc về hai người khác nhau: chiến
    lược là thứ được phép sai và được phép sửa, còn ngưỡng rủi ro là hàng rào.
    Gộp một chỗ thì rồi sẽ có lúc "tối ưu" bằng cách hạ hàng rào.
    """
    tf_chinh = CONFIG["timeframes"]["primary"]
    nc = nen[tf_chinh]
    if chuoi is None:
        chuoi = sinh_luan_diem(nen, symbol=symbol, bao_tien_do=bao_tien_do)

    c = {**CONFIG["risk"], **(rieng or {})}
    if bo_qua_kill:
        # Chế độ ĐO LỢI THẾ THÔ: tắt hẳn ngắt mạch để chạy hết đoạn dữ liệu.
        # Chỉ gỡ chốt `halted_reason` là không đủ — `circuit_breakers` tính lại
        # sụt giảm từ vốn so với đỉnh ở mỗi lượt, mà vốn đã sụt thì nó sụt mãi,
        # nên chốt bật lại ngay lượt sau. Lần đầu tôi làm vậy và hai chế độ ra
        # kết quả y hệt nhau, trông như trùng hợp chứ không như một lỗi.
        c = {**c, "maxDrawdownPct": 1e9, "maxDailyLossPct": 1e9}
    engine = RiskEngine(c)
    cost_bps = (c["feeBps"] + c["slippageBps"]) / 10_000

    von_dau = c.get("startingEquity", 10_000.0)
    von = von_dau
    dinh = von_dau

    lenh: list[dict] = []
    tu_choi: dict[str, int] = {}
    theo_regime: dict[str, dict] = {}
    dang_giu_toi = -1        # chỉ số nến mà vị thế đang mở còn chiếm
    kill: dict | None = None

    dau = max(tu_nen, KHOI_DONG)
    cuoi = min(den_nen if den_nen is not None else len(nc) - 1, len(nc) - 1)
    xet = [d for d in chuoi if dau <= d["i"] < cuoi]

    for d in xet:
        i = d["i"]
        # Một vị thế tại một thời điểm — giống luật thật (maxOpenPositions=1).
        # Bỏ luật này là backtest vào hàng trăm lệnh chồng lên nhau, và con số
        # ra không thuộc về hệ thống nào cả.
        if i <= dang_giu_toi:
            continue

        # Dựng luận điểm TẠI ĐÂY, từ tín hiệu đã cache — chính hàm mà bản chạy
        # thật dùng, chỉ khác bộ tham số.
        st = {"symbol": symbol, "price": d["price"],
              "timeframes": {tf_chinh: d["feat"]}}
        ld = suy_luan(bo_luat, st, d["regime"], tf_chinh, tham)
        if ld["action"] == "NO_TRADE":
            ma = (ld.get("reason_codes") or ["NO_TRADE"])[-1]
            tu_choi[f"CHIẾN_LƯỢC_{ma}"] = tu_choi.get(f"CHIẾN_LƯỢC_{ma}", 0) + 1
            continue

        tk = {"equity": von, "peakEquity": dinh, "positions": [], "dailyPnl": {},
              "dailyStartEquity": {}, "availableQuote": von}
        pq = engine.evaluate(ld, st, tk, d["atr"])

        if not pq["approved"]:
            for r in pq["rejections"]:
                ma = r.split(":")[0]
                tu_choi[ma] = tu_choi.get(ma, 0) + 1
            # Kill switch là CHỐT CỨNG, không tự mở lại — đúng như bản chạy
            # thật. Nghĩa là từ đây trở đi mọi điểm còn lại đều bị chặn, nên cứ
            # lặp tiếp là đếm hàng trăm lần "bị chặn" rồi báo cáo như thể đã đo
            # hết đoạn dữ liệu. Lần chạy đầu tôi để vậy: bảng ghi "3789 nến"
            # trong khi thực tế chỉ đo được một phần ba. Dừng hẳn và nói rõ.
            if engine.halted_reason:
                kill = {"luc": nc[i]["t"], "i": i, "lyDo": engine.halted_reason,
                        "soNenBoDo": cuoi - i,
                        "phanTramDaXet": round((i - dau) / max(1, cuoi - dau) * 100, 1)}
                break
            continue

        v = pq["position"]
        side = 1 if v["side"] == "LONG" else -1
        entry = v["expectedFill"]
        sl, tp = v["stopLoss"], v["targets"][0]
        ly_do, gia_ra, so_nen = _thoat(nc, i, side, entry, sl, tp, toi_da_nen_giu, cost_bps)

        rui_ro = abs(entry - sl) * v["qty"]
        lai = (gia_ra - entry) * side * v["qty"]
        r_boi = lai / rui_ro if rui_ro else 0.0
        von += lai
        dinh = max(dinh, von)

        k = d["regime"]["key"]
        g = theo_regime.setdefault(k, {"so": 0, "thang": 0, "tongR": 0.0})
        g["so"] += 1
        g["thang"] += 1 if lai > 0 else 0
        g["tongR"] += r_boi

        lenh.append({
            "i": i, "t": d["t"], "side": v["side"],
            "entry": round(entry, 2), "sl": round(sl, 2), "tp": round(tp, 2),
            "exit": round(gia_ra, 2), "lyDo": ly_do, "soNenGiu": so_nen,
            "pnl": round(lai, 2), "R": round(r_boi, 3),
            "regime": d["regime"]["primary"], "regimeKey": k,
            "rr": round(pq["rr"], 2) if pq["rr"] else None,
            "von": round(von, 2),
        })
        dang_giu_toi = i + so_nen

    da_xet = (kill["i"] - dau) if kill else (cuoi - dau)
    return {
        "lenh": lenh,
        "tuChoi": dict(sorted(tu_choi.items(), key=lambda x: -x[1])),
        "theoRegime": {k: {**v, "tyLeThang": round(v["thang"] / v["so"] * 100, 1),
                           "trungBinhR": round(v["tongR"] / v["so"], 3)}
                       for k, v in theo_regime.items()},
        "thongKe": thong_ke(lenh, von_dau, von),
        "soNenXet": da_xet, "soNenTrongDoan": cuoi - dau,
        "soDiemVao": len(xet),
        "dungSom": kill,
        "nguong": {k: c[k] for k in ("minRR", "minConfidence", "minStopAtr", "maxStopAtr",
                                     "maxRiskPerTradePct", "feeBps", "slippageBps") if k in c},
    }


def thong_ke(lenh: list[dict], von_dau: float, von_cuoi: float) -> dict:
    """Thống kê. **Kỳ vọng R là con số quan trọng nhất, không phải tỉ lệ thắng.**

    Tỉ lệ thắng một mình thì vô nghĩa và dễ đánh lừa: chốt lãi thật non là đẩy
    được tỉ lệ thắng lên 90% trong khi vẫn cháy tài khoản. Kỳ vọng R trả lời
    đúng câu cần hỏi — mỗi lệnh trung bình kiếm được bao nhiêu lần số tiền đã
    đặt cược. Dương thì có cửa, âm thì thắng nhiều đến mấy cũng chỉ là chết chậm.
    """
    if not lenh:
        return {"so": 0, "tyLeThang": None, "kyVongR": None, "tongR": 0.0,
                "heSoLoiNhuan": None, "sutGiamToiDaPct": 0.0, "chuoiThuaDaiNhat": 0,
                "vonDau": von_dau, "vonCuoi": von_dau, "loiNhuanPct": 0.0,
                "trungBinhNenGiu": None, "ghiChu": "không có lệnh nào qua được Risk Engine"}

    rs = [t["R"] for t in lenh]
    thang = [r for r in rs if r > 0]
    thua = [r for r in rs if r <= 0]

    dinh, sut = von_dau, 0.0
    for t in lenh:
        dinh = max(dinh, t["von"])
        sut = max(sut, (dinh - t["von"]) / dinh * 100)

    chuoi = dai_nhat = 0
    for r in rs:
        chuoi = chuoi + 1 if r <= 0 else 0
        dai_nhat = max(dai_nhat, chuoi)

    tong_thang = sum(thang)
    tong_thua = abs(sum(thua))

    return {
        "so": len(lenh),
        "soThang": len(thang), "soThua": len(thua),
        "tyLeThang": round(len(thang) / len(rs) * 100, 1),
        "kyVongR": round(statistics.fmean(rs), 3),
        "tongR": round(sum(rs), 2),
        "trungBinhThangR": round(statistics.fmean(thang), 3) if thang else None,
        "trungBinhThuaR": round(statistics.fmean(thua), 3) if thua else None,
        # Hệ số lợi nhuận = tổng lãi / tổng lỗ. Không có lệnh thua thì để None
        # chứ không để vô cực: "∞" trên bảng chỉ có nghĩa là mẫu quá nhỏ.
        "heSoLoiNhuan": round(tong_thang / tong_thua, 2) if tong_thua > 0 else None,
        "sutGiamToiDaPct": round(sut, 2),
        "chuoiThuaDaiNhat": dai_nhat,
        "vonDau": round(von_dau, 2), "vonCuoi": round(von_cuoi, 2),
        "loiNhuanPct": round((von_cuoi - von_dau) / von_dau * 100, 2),
        "trungBinhNenGiu": round(statistics.fmean([t["soNenGiu"] for t in lenh]), 1),
        "theoLyDoThoat": {ly: sum(1 for t in lenh if t["lyDo"] == ly)
                          for ly in ("TP", "SL", "HET_HAN")},
    }


# ── dò tham số, có cắt trong/ngoài mẫu ────────────────────────────────────
# Lưới dò CHIẾN LƯỢC, không phải ngưỡng rủi ro.
#
# Lưới đầu tiên tôi dựng toàn ngưỡng rủi ro (minRR, minStopAtr, minConfidence)
# và cả 108 tổ hợp cho ra một kết quả duy nhất. Lý do đáng nhớ: bộ luật TỰ suy
# mục tiêu từ `minRR` để luôn vừa đủ qua cửa, còn SL thì luôn đúng 1.5×ATR và
# độ tin cậy luôn đúng 0.6 — nên mấy cái ngưỡng ấy không bao giờ chạm tới cái
# gì. Dò một tham số mà chiến lược đã tự chiều theo thì chỉ đo được chính nó.
#
# Những số dưới đây thì đổi thật: chúng đổi lệnh nào được vào và lãi lỗ ra sao.
LUOI_MAC_DINH: dict[str, list] = {
    "stopAtr": [1.0, 1.5, 2.0, 2.5],
    "demTp": [1.05, 1.3, 1.8],
    "adxToiThieu": [0, 25, 30],
    "chanBienDongCao": [False, True],
}


def _to_hop(luoi: dict[str, list]) -> list[dict]:
    ra: list[dict] = [{}]
    for k, vs in luoi.items():
        ra = [{**c, k: v} for c in ra for v in vs]
    return ra


def quet(nen: dict[str, list[dict]], *, symbol: str = "BTCUSDT",
         chuoi: list[dict] | None = None,
         luoi: dict[str, list] | None = None, ty_le_trong_mau: float = 0.7,
         toi_thieu_lenh: int = 8, bo_qua_kill: bool = True,
         bao_tien_do: Callable[[int, int, dict], None] | None = None) -> dict:
    """Dò lưới tham số, chọn TRONG mẫu, chấm điểm NGOÀI mẫu.

    Không có bước cắt này thì việc dò tham số chỉ là tìm bộ số vừa khít với quá
    khứ. Con số trong mẫu luôn đẹp lên khi lưới rộng ra — nó phải đẹp lên, kể cả
    khi chiến lược hoàn toàn vô dụng. Chỉ con số ngoài mẫu mới nói được điều gì.
    """
    luoi = luoi or LUOI_MAC_DINH
    tf = CONFIG["timeframes"]["primary"]
    tong = len(nen[tf])
    moc = int(tong * ty_le_trong_mau)
    if chuoi is None:
        chuoi = sinh_luan_diem(nen, symbol=symbol)

    to_hops = _to_hop(luoi)
    kq: list[dict] = []
    t0 = time.time()

    for idx, bo in enumerate(to_hops):
        trong = chay_lai(nen, symbol=symbol, chuoi=chuoi, tham=bo,
                         tu_nen=0, den_nen=moc, bo_qua_kill=bo_qua_kill)
        tk = trong["thongKe"]
        kq.append({"bo": bo, "trongMau": tk, "duMau": tk["so"] >= toi_thieu_lenh})
        if bao_tien_do:
            bao_tien_do(idx + 1, len(to_hops), bo)

    # Chọn theo KỲ VỌNG R, và chỉ trong số bộ có đủ mẫu. Chọn theo lợi nhuận %
    # thì luôn thắng bởi bộ nào vào ít lệnh mà may — một lệnh +8R là đủ.
    hop_le = [k for k in kq if k["duMau"] and k["trongMau"]["kyVongR"] is not None]
    hop_le.sort(key=lambda k: k["trongMau"]["kyVongR"], reverse=True)

    goc = chay_lai(nen, symbol=symbol, chuoi=chuoi, tu_nen=moc, bo_qua_kill=bo_qua_kill)
    ra: dict[str, Any] = {
        "soToHop": len(to_hops), "mocCat": moc, "tongNen": tong,
        "giay": round(time.time() - t0, 1), "boQuaKill": bo_qua_kill,
        "bang": [{"bo": k["bo"], **{x: k["trongMau"][x] for x in
                                    ("so", "tyLeThang", "kyVongR", "tongR", "sutGiamToiDaPct")},
                  "duMau": k["duMau"]} for k in kq],
        "hienHanhNgoaiMau": goc["thongKe"],
        "toiThieuLenh": toi_thieu_lenh,
    }

    if not hop_le:
        ra["ketLuan"] = (f"không bộ nào vào đủ {toi_thieu_lenh} lệnh trong mẫu — "
                         f"đoạn dữ liệu quá ngắn để kết luận bất cứ điều gì")
        return ra

    tot = hop_le[0]
    ngoai = chay_lai(nen, symbol=symbol, chuoi=chuoi, tham=tot["bo"],
                     tu_nen=moc, bo_qua_kill=bo_qua_kill)
    tm, nm = tot["trongMau"], ngoai["thongKe"]
    ra["totNhat"] = {
        "bo": tot["bo"], "trongMau": tm, "ngoaiMau": nm,
        # Khớp trội = phần kỳ vọng bốc hơi khi ra khỏi dữ liệu đã dùng để chọn.
        "khopTroi": (round(tm["kyVongR"] - nm["kyVongR"], 3)
                     if nm["kyVongR"] is not None else None),
    }
    ra["ketLuan"] = _ket_luan(tm, nm, goc["thongKe"], toi_thieu_lenh)
    return ra


def _ket_luan(trong: dict, ngoai: dict, hien_hanh: dict, toi_thieu: int) -> str:
    """Đọc kết quả hộ người dùng — và nói thẳng khi kết quả không đủ để kết luận."""
    if ngoai["so"] < toi_thieu:
        return (f"ngoài mẫu chỉ có {ngoai['so']} lệnh (cần ≥{toi_thieu}) — "
                f"chưa đủ để nói bộ tham số này tốt hơn hay tệ hơn")
    if ngoai["kyVongR"] is None:
        return "ngoài mẫu không có lệnh nào — không kết luận được"

    dau = "" if hien_hanh["kyVongR"] is None else \
        f" (bộ đang dùng: {hien_hanh['kyVongR']:+.3f}R trên {hien_hanh['so']} lệnh)"
    if ngoai["kyVongR"] <= 0:
        return (f"bộ tốt nhất trong mẫu ({trong['kyVongR']:+.3f}R) rơi xuống "
                f"{ngoai['kyVongR']:+.3f}R khi ra ngoài mẫu — ĐỪNG áp dụng{dau}")
    sut = trong["kyVongR"] - ngoai["kyVongR"]
    if sut > trong["kyVongR"] * 0.5:
        return (f"ngoài mẫu vẫn dương ({ngoai['kyVongR']:+.3f}R) nhưng mất hơn nửa "
                f"kỳ vọng so với trong mẫu ({trong['kyVongR']:+.3f}R) — dấu hiệu khớp trội, "
                f"cần thêm dữ liệu trước khi tin{dau}")
    return (f"giữ được {ngoai['kyVongR']:+.3f}R ngoài mẫu trên {ngoai['so']} lệnh, "
            f"sát mức trong mẫu {trong['kyVongR']:+.3f}R — bộ này đáng thử tiếp{dau}")


# ── nạp dữ liệu và cache chuỗi luận điểm ──────────────────────────────────
def nap_nen(symbol: str | None = None) -> dict[str, list[dict]] | None:
    """Nạp nến lịch sử đã tải sẵn. None nếu chưa chạy `scripts/tai-lich-su.py`."""
    import json

    symbol = symbol or CONFIG["symbol"]
    kho = ROOT / "data" / "lich-su"
    tfs = [CONFIG["timeframes"]["primary"], CONFIG["timeframes"]["context"]]
    ra = {}
    for tf in tfs:
        f = kho / f"{symbol}-{tf}.json"
        if not f.exists():
            return None
        ra[tf] = json.loads(f.read_text(encoding="utf-8"))
    return ra


# Vân tay của MÃ sinh ra chuỗi. Tính một lần lúc nạp module.
#
# `PHIEN_BAN_CHUOI` là một con số phải TỰ TAY tăng khi sửa mã sinh chuỗi — và
# nó vừa không được tăng: bản vá làm tròn giá theo chữ số có nghĩa đổi hẳn nội
# dung chuỗi, nhưng vân tay không đổi nên cache cũ (chứa giá đã bị làm tròn về
# 0) vẫn được dùng, và lượt đo tiếp theo nổ y hệt lượt trước bản vá.
#
# Một con số phải nhớ tăng thì sớm muộn sẽ quên. Nên băm luôn NỘI DUNG những
# file thật sự quyết định chuỗi: sửa bất kỳ file nào trong số đó là vân tay đổi
# và cache tự hết hạn, không ai phải nhớ gì.
#
# Giá: mỗi lần sửa một trong các file này là mọi chuỗi phải tính lại. Đó đúng
# là điều cần xảy ra — chuỗi cũ được sinh bởi mã cũ.
def _van_tay_ma() -> str:
    import hashlib

    h = hashlib.sha256()
    # CHỈ những file thật sự quyết định NỘI DUNG chuỗi.
    #
    # `sinh_luan_diem` dựng chuỗi từ nến → `features_for` → `classify`. Nó KHÔNG
    # gọi bộ luật nào: `suy_luan` chỉ xuất hiện ở `chay_lai`, tức tầng dùng chuỗi
    # chứ không phải tầng sinh ra nó.
    #
    # Bản đầu băm cả `brain.py`, nên MỖI lần sửa bộ não là toàn bộ chuỗi hết hạn
    # — 48 file, 35 MB, hàng giờ dựng lại, cho một thay đổi không đụng tới một
    # con số nào trong chuỗi. Rộng quá thì cache thành vô dụng theo cách khác:
    # không sai, chỉ là không bao giờ trúng.
    for ten in ("features.py", "indicators.py", "regime.py", "mau_gia.py",
                "huanluyen.py"):
        f = ROOT / "trader" / ten
        if f.exists():
            h.update(f.read_bytes())
    return h.hexdigest()[:12]


VAN_TAY_MA = _van_tay_ma()

def _van_tay(nen: dict[str, list[dict]], symbol: str) -> str:
    """Vân tay của bộ dữ liệu + những cấu hình ẢNH HƯỞNG tới chuỗi luận điểm.

    Cache chuỗi luận điểm mà không gắn vân tay là cái bẫy tệ nhất ở đây: đổi
    khung thời gian hay `candleLimit` rồi bấm chạy, kết quả trả về trong một
    giây và trông rất hợp lý — nhưng nó là chuỗi của cấu hình CŨ. Không có gì
    báo sai cả.
    """
    import hashlib

    tf = CONFIG["timeframes"]
    m = [symbol, tf["primary"], tf["context"], str(CONFIG["data"]["candleLimit"]),
         str(KHOI_DONG), f"v{PHIEN_BAN_CHUOI}", VAN_TAY_MA]
    for k in sorted(nen):
        v = nen[k]
        m += [k, str(len(v)), str(v[0]["t"]), str(v[-1]["t"])]
    return hashlib.sha256("|".join(m).encode()).hexdigest()[:16]


def _van_tay_hinh(symbol: str) -> str:
    """Vân tay của MÃ + CẤU HÌNH — cố ý KHÔNG gồm quãng nến.

    `_van_tay` gộp cả hai, nên chỉ cần một nến mới về là cả chuỗi 9000 điểm
    thành rác. Đo được: nghi thức 4h phải dựng lại 15 chuỗi mỗi lượt, mà lượt
    trước 8 chợ đã mất 75 phút — tức việc ấy quá hạn 5400s trước khi bắt đầu.

    Tách ra thì quãng nến trở thành thứ ĐỐI CHIẾU chứ không phải thứ khoá: điểm
    nào tính trên cùng cửa sổ dữ liệu thì dùng lại, phần còn lại tính thêm.
    """
    import hashlib

    tf = CONFIG["timeframes"]
    m = [symbol, tf["primary"], tf["context"], str(CONFIG["data"]["candleLimit"]),
         str(KHOI_DONG), f"v{PHIEN_BAN_CHUOI}", VAN_TAY_MA]
    return hashlib.sha256("|".join(m).encode()).hexdigest()[:16]


def _quang(nen: dict[str, list[dict]]) -> dict:
    """Quãng nến của từng khung: bao nhiêu nến, từ mốc nào tới mốc nào."""
    return {k: {"n": len(v), "dau": v[0]["t"], "cuoi": v[-1]["t"]}
            for k, v in nen.items()}


def _moc_day(nen: dict[str, list[dict]]) -> list[int]:
    """Mốc thời gian của những nến ĐÃ ĐƯỢC XÉT ở lượt dựng chuỗi này.

    Cần vì "không có trong cache" và "đã xét rồi, không ra điểm nào" là hai
    chuyện khác hẳn — chế độ UNKNOWN bị bỏ qua ở `sinh_luan_diem`, nên phân nửa
    chỉ mục vốn không sinh điểm. Lẫn hai thứ ấy thì lượt bồi thêm tính lại 587
    chỉ mục để ra 110 điểm; đo được đúng con số đó ở lượt thử đầu.
    """
    tf = CONFIG["timeframes"]["primary"]
    nc = nen[tf]
    return [nc[i]["t"] for i in range(KHOI_DONG, len(nc) - 1)]


def _cung_lat(dau_cu: int, dau_moi: int, day: bool) -> bool:
    """Lát cắt tại một mốc có TRÙNG tập nến giữa bộ cũ và bộ mới không?

    Lát cắt là `arr[max(0, k - cua_so) : k]` với `k` chỉ phụ thuộc vào mốc thời
    gian. Ba ca, và ca giữa là chỗ dễ sai nhất:

      • đầu mảng KHÔNG đổi   → `k` như nhau ⇒ lát trùng, đầy hay chưa cũng vậy;
      • mảng cuốn VỀ TRƯỚC   → `k_cũ > k_mới`, hai lát chỉ trùng khi lát MỚI đã
                               đầy (cùng đếm ngược `cua_so` nến từ cùng một mốc);
      • bộ mới có THÊM lịch sử ở đầu → `k_cũ < k_mới`, không suy ra được gì từ
                               những số đang có ⇒ từ chối.

    Bản đầu đòi "lát phải đầy" ở MỌI ca. Không sai kết quả, nhưng ở đoạn đầu
    lịch sử — nơi khung ngữ cảnh chưa đủ `cua_so` nến — thì không điểm nào dùng
    lại được, và cache im lặng thành vô dụng. Phép kiểm [11] bắt đúng chỗ đó.
    """
    if dau_cu == dau_moi:
        return True
    if dau_cu < dau_moi:
        return day
    return False


def _diem_dung_lai(cu: list[dict], quang_cu: dict, xet_cu: list[int],
                   nen: dict[str, list[dict]]) -> tuple[list[dict], list[int]]:
    """Chọn điểm cache CÒN ĐÚNG với bộ nến mới. Trả (điểm dùng lại, chỉ mục thiếu).

    Một điểm tại mốc `t` được quyết định bởi ĐÚNG hai lát cắt: `cua_so` nến
    chính kết thúc ở `t`, và `cua_so` nến ngữ cảnh đã mở trước `t`. Nến đã đóng
    thì không đổi giá, nên cùng hai lát ấy ⇒ cùng kết quả. Ba điều kiện:

      1. mốc `t` có mặt trong bộ mới, và lát nến CHÍNH tại đó trùng bộ cũ;
      2. lát nến NGỮ CẢNH tại đó cũng trùng;
      3. `t` nằm trước nến ngữ cảnh cuối của bộ CŨ ít nhất một nhịp — nến cuối
         lúc ấy có thể CHƯA ĐÓNG, và giá của nó sẽ đổi ở lần nạp sau.

    Điều 3 là chỗ dễ bỏ sót nhất: hai điều đầu nhìn có vẻ đủ, nhưng phần đuôi
    chuỗi lại đúng là phần được dùng nhiều nhất trong cửa sổ ngoài mẫu.
    """
    from .data import TF_MS

    tf, ctx = CONFIG["timeframes"]["primary"], CONFIG["timeframes"]["context"]
    if tf not in quang_cu or ctx not in quang_cu:
        return [], []
    nc, nx = nen[tf], nen[ctx]
    cua_so = CONFIG["data"]["candleLimit"]
    moc_ctx = [x["t"] for x in nx]
    vi_tri = {x["t"]: i for i, x in enumerate(nc)}
    han_duoi = quang_cu[ctx]["cuoi"] - (TF_MS.get(ctx) or TF_MS["1d"])
    d_tf = (quang_cu[tf]["dau"], nc[0]["t"])
    d_ctx = (quang_cu[ctx]["dau"], nx[0]["t"])
    xet = set(xet_cu)

    def dung_duoc(t: int, i: int) -> bool:
        if t not in xet or t >= han_duoi or i < KHOI_DONG:
            return False
        if not _cung_lat(d_tf[0], d_tf[1], i + 1 >= cua_so):
            return False
        return _cung_lat(d_ctx[0], d_ctx[1],
                         bisect.bisect_right(moc_ctx, t) >= cua_so)

    giu = [{**d, "i": vi_tri[d["t"]]}      # chỉ số phải theo bộ nến MỚI
           for d in cu
           if d.get("t") in vi_tri and dung_duoc(d["t"], vi_tri[d["t"]])]
    # THIẾU = chỉ mục mà bộ cũ chưa từng xét với cửa sổ dùng lại được. Chỗ đã
    # xét mà không có điểm là chỗ ĐÃ BIẾT không ra gì — tính lại chỉ tốn giờ.
    thieu = [i for i in range(KHOI_DONG, len(nc) - 1)
             if not dung_duoc(nc[i]["t"], i)]
    return giu, thieu


def _doi_chieu(giu: list[dict], nen: dict[str, list[dict]], symbol: str,
               so_mau: int = 5) -> bool:
    """Tính LẠI vài điểm dùng lại và so từng chữ. Sai một điểm ⇒ vứt cả cache.

    Không có bước này thì mọi điều kiện ở trên chỉ là lập luận, và một lập luận
    sai ở đây không làm gì đổ — nó chỉ khiến mọi con số thuộc về một thị trường
    khác. Năm điểm rải đều là đủ: lỗi lệch cửa sổ không bao giờ chỉ sai một chỗ.
    """
    import json

    if not giu:
        return True
    b = max(1, len(giu) // so_mau)
    mau = giu[::b][:so_mau]
    moi = sinh_luan_diem(nen, symbol=symbol, chi_muc=[x["i"] for x in mau])
    theo_i = {x["i"]: x for x in moi}
    for x in mau:
        y = theo_i.get(x["i"])
        if y is None or json.dumps(y, sort_keys=True) != json.dumps(x, sort_keys=True):
            return False
    return True


_bo_nho: dict[str, list[dict]] = {}


def _ghi_goi(f, chuoi: list[dict], quang: dict, xet: list[int], symbol: str) -> None:
    """Ghi gói chuỗi ra đĩa, nguyên tử, rồi dọn gói cũ của CHÍNH chợ này.

    Ghi qua file tạm rồi ĐỔI TÊN. `write_text` không nguyên tử: hai tiến trình
    cùng sinh một chuỗi (nghi thức chạy nền + một lượt gõ tay) có thể để lại
    file cụt giữa chừng. Đường đọc nuốt mọi lỗi parse và tính lại, nên file cụt
    KHÔNG gây sập — nó gây chuyện khó thấy hơn: mỗi lượt đều "tính mới" một
    chuỗi vốn đã có sẵn, và một chuỗi 9000 nến mất hàng chục phút. Cache im
    lặng thành vô dụng, mà bảng nào cũng xanh.

    Dọn gói CŨ vì vân tay gồm cả mã nguồn: mỗi lần sửa `features.py` là toàn bộ
    cache thành rác không ai với tới — 74 file, 86 MB sau đúng một bản vá. Chỉ
    xoá file của chợ vừa ghi: tiến trình khác có thể đang dùng cache của chợ
    khác với vân tay khác.
    """
    import json
    import os

    f.parent.mkdir(parents=True, exist_ok=True)
    tam = f.with_suffix(f".{os.getpid()}.tmp")
    tam.write_text(json.dumps({"quang": quang, "xet": xet, "chuoi": chuoi}),
                   encoding="utf-8")
    os.replace(tam, f)
    for cu_f in f.parent.glob(f"{symbol}-*.json"):
        if cu_f.name != f.name:
            try:
                cu_f.unlink()
            except OSError:
                pass


def lay_chuoi(nen: dict[str, list[dict]], symbol: str,
              bao_tien_do: Callable[[int, int], None] | None = None,
              dung_dia: bool = True) -> tuple[list[dict], str]:
    """Chuỗi luận điểm, lấy từ RAM → đĩa → tính mới. Trả (chuỗi, nguồn)."""
    import json

    vt = _van_tay(nen, symbol)
    if vt in _bo_nho:
        return _bo_nho[vt], "bộ nhớ"

    # Tên file theo vân tay MÃ+CẤU HÌNH, không theo quãng nến: một chợ có đúng
    # một gói chuỗi, và gói ấy được BỒI THÊM mỗi lần nến mới về.
    f = ROOT / "data" / "chuoi" / f"{symbol}-{_van_tay_hinh(symbol)}-goi.json"
    quang_nay = _quang(nen)
    if dung_dia and f.exists():
        try:
            goi = json.loads(f.read_text(encoding="utf-8"))
            cu, quang_cu = goi.get("chuoi") or [], goi.get("quang") or {}
            if quang_cu == quang_nay:
                _bo_nho[vt] = cu
                return cu, "đĩa"
            giu, thieu = _diem_dung_lai(cu, quang_cu, goi.get("xet") or [], nen)
            if giu and _doi_chieu(giu, nen, symbol):
                t0 = time.time()
                them = sinh_luan_diem(nen, symbol=symbol, chi_muc=thieu,
                                      bao_tien_do=bao_tien_do)
                c = sorted(giu + them, key=lambda d: d["i"])
                _bo_nho[vt] = c
                if dung_dia:
                    _ghi_goi(f, c, quang_nay, _moc_day(nen), symbol)
                return c, (f"đĩa+{len(them)} điểm mới trong "
                           f"{time.time() - t0:.0f}s (dùng lại {len(giu)})")
            if giu:
                # Đối chiếu TRƯỢT: điều kiện dùng lại có chỗ sai. Không nuốt im —
                # tính lại thì chỉ chậm, còn im lặng thì mọi bảng số sau đó nói
                # về một thị trường khác.
                bus.log("hoc", "chuoi-doi-chieu-truot",
                        f"{symbol}: {len(giu)} điểm cache không khớp khi tính lại "
                        f"— dựng lại toàn bộ")
        except Exception:  # noqa: BLE001 — cache hỏng thì tính lại, không phải sự cố
            pass

    t0 = time.time()
    c = sinh_luan_diem(nen, symbol=symbol, bao_tien_do=bao_tien_do)
    _bo_nho[vt] = c
    if dung_dia:
        _ghi_goi(f, c, quang_nay, _moc_day(nen), symbol)
    bus.emit("hoc", "sinh-chuoi",
             f"sinh {len(c)} điểm vào lệnh từ lịch sử trong {time.time() - t0:.0f}s")
    return c, "tính mới"


# ── đúc bài học ───────────────────────────────────────────────────────────
def duc_bai_hoc(kq: dict) -> list[dict]:
    """Biến một lượt chạy lại thành các câu có thể hành động được.

    Cố ý KHÔNG gọi model: mỗi câu ở đây đều truy được ra con số sinh ra nó, nên
    sai thì cãi lại được. Một bài học không truy được nguồn thì không phải bài
    học, chỉ là một câu nghe hay.
    """
    tk, ra = kq["thongKe"], []

    if tk["so"] == 0:
        top = list(kq["tuChoi"].items())[:3]
        ra.append({
            "muc": "CHẶN_HẾT", "nang": "cao",
            "cau": "Không lệnh nào qua được Risk Engine trong cả đoạn dữ liệu.",
            "so": ", ".join(f"{k}×{v}" for k, v in top) or "không có luận điểm nào được sinh",
            "lam": "Xem ba lý do từ chối nhiều nhất — nếu toàn RR_THẤP thì minRR đang "
                   "cao hơn mức mà chiến lược này với tay tới được.",
        })
        return ra

    if tk["kyVongR"] is not None and tk["kyVongR"] <= 0:
        ra.append({
            "muc": "KỲ_VỌNG_ÂM", "nang": "cao",
            "cau": "Kỳ vọng âm — bộ luật hiện tại không có lợi thế trên đoạn này.",
            "so": f"{tk['kyVongR']:+.3f}R/lệnh trên {tk['so']} lệnh, tỉ lệ thắng {tk['tyLeThang']}%",
            "lam": "Đừng tăng size. Chạy dò tham số, và nếu ngoài mẫu vẫn âm thì "
                   "vấn đề nằm ở tín hiệu vào lệnh chứ không ở ngưỡng.",
        })

    # Thắng nhiều mà vẫn âm = đang chốt non. Đây là cái bẫy tỉ lệ thắng.
    if (tk["tyLeThang"] or 0) >= 55 and (tk["kyVongR"] or 0) <= 0:
        ra.append({
            "muc": "CHỐT_NON", "nang": "cao",
            "cau": f"Thắng {tk['tyLeThang']}% số lệnh mà kỳ vọng vẫn âm — lãi bị cắt "
                   f"ngắn hơn lỗ.",
            "so": f"thắng TB {tk['trungBinhThangR']}R · thua TB {tk['trungBinhThuaR']}R",
            "lam": "Đây là lý do không được lấy tỉ lệ thắng làm mục tiêu. Nới mục tiêu "
                   "hoặc siết stop, đừng vào nhiều lệnh hơn.",
        })

    ht = tk.get("theoLyDoThoat", {})
    if ht.get("HET_HAN", 0) > tk["so"] * 0.4:
        ra.append({
            "muc": "HẾT_HẠN_NHIỀU", "nang": "vua",
            "cau": f"{ht['HET_HAN']}/{tk['so']} lệnh thoát vì hết hạn giữ, không chạm SL lẫn TP.",
            "so": f"giữ trung bình {tk['trungBinhNenGiu']} nến",
            "lam": "Mục tiêu đang đặt xa hơn tầm với của biến động trong khoảng thời "
                   "gian đó. Hạ TP1 hoặc chỉ vào khi ADX cao hơn.",
        })

    # Regime nào ăn, regime nào không — dữ liệu để BỎ BỚT, không phải để thêm.
    tot = [(k, v) for k, v in kq["theoRegime"].items() if v["so"] >= 5]
    if tot:
        tot.sort(key=lambda x: x[1]["trungBinhR"])
        te, hay = tot[0], tot[-1]
        if te[1]["trungBinhR"] < 0:
            ra.append({
                "muc": "REGIME_LỖ", "nang": "vua",
                "cau": f"Chế độ {te[0]} lỗ đều — không vào lệnh ở đây là cải thiện rẻ nhất.",
                "so": f"{te[1]['so']} lệnh · {te[1]['trungBinhR']:+.3f}R · thắng {te[1]['tyLeThang']}%",
                "lam": f"Thêm {te[0].split('|')[0]} vào danh sách chế độ đứng ngoài, "
                       f"rồi chạy lại để xem kỳ vọng chung có lên không.",
            })
        if hay[1]["trungBinhR"] > 0 and hay[0] != te[0]:
            ra.append({
                "muc": "REGIME_ĂN", "nang": "thap",
                "cau": f"Chế độ {hay[0]} là nơi lợi thế nằm.",
                "so": f"{hay[1]['so']} lệnh · {hay[1]['trungBinhR']:+.3f}R · thắng {hay[1]['tyLeThang']}%",
                "lam": "Đừng vội tăng size — xác nhận trên dữ liệu ngoài mẫu trước.",
            })

    if tk["chuoiThuaDaiNhat"] >= 6:
        ra.append({
            "muc": "CHUỖI_THUA", "nang": "vua",
            "cau": f"Có lúc thua liền {tk['chuoiThuaDaiNhat']} lệnh.",
            "so": f"sụt giảm sâu nhất {tk['sutGiamToiDaPct']}%",
            "lam": "Con số này quyết định mức risk mỗi lệnh chịu được, không phải kỳ vọng. "
                   "Chuỗi thua như vậy ở mức risk hiện tại có chấp nhận được không?",
        })

    top_tu_choi = list(kq["tuChoi"].items())[:1]
    if top_tu_choi and top_tu_choi[0][1] >= tk["so"]:
        k, v = top_tu_choi[0]
        ra.append({
            "muc": "CỬA_HẸP", "nang": "thap",
            "cau": f"Risk Engine chặn nhiều hơn số lệnh cho qua — lý do đứng đầu là {k}.",
            "so": f"{v} lần chặn so với {tk['so']} lệnh được vào",
            "lam": "Không hẳn là xấu. Nhưng nếu kỳ vọng đang dương thì nới đúng ngưỡng "
                   "này là cách tăng số lệnh mà không đổi bản chất chiến lược.",
        })

    if not ra:
        ra.append({
            "muc": "ỔN", "nang": "thap",
            "cau": "Không thấy điểm hỏng rõ ràng nào trong đoạn này.",
            "so": f"{tk['so']} lệnh · {tk['kyVongR']:+.3f}R · thắng {tk['tyLeThang']}% · "
                  f"sụt sâu nhất {tk['sutGiamToiDaPct']}%",
            "lam": "Chạy trên đoạn dữ liệu khác trước khi kết luận. Một đoạn đẹp có thể "
                   "chỉ là một chế độ thị trường thuận.",
        })

    bus.emit("hoc", "duc-bai-hoc", f"đúc {len(ra)} bài học từ {tk['so']} lệnh chạy lại")
    return ra
