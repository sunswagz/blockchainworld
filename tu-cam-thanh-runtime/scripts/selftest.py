"""Tự kiểm: chạy đúng một vòng kín, không gọi API, không mở cổng.

    python scripts/selftest.py

Kiểm những thứ chỉ lộ ra khi các tầng ghép vào nhau: căn chỉnh chỉ báo, hình
học lệnh, số học của Risk Engine, và kế toán của sàn giấy. Chạy cái này trước
khi tin bất cứ con số nào trên dashboard.

**Ghi vào sổ RIÊNG, không đụng sổ thật.** Phép kiểm này cố tình dựng những lệnh
thắng để soát phần kế toán; để chúng rơi vào `data/trades.jsonl` là bơm hàng giả
vào chính thứ dùng để đánh giá bot. Đã xảy ra thật: 14 trong 17 lệnh của sổ là
hàng của selftest, toàn TAKE_PROFIT cùng một giá vào, và bảng điều khiển khoe
"thắng 82,4% · kỳ vọng +1,135R" trong khi bot chưa từng tự vào lệnh nào.
"""
from __future__ import annotations

import asyncio
import json as _json

NL = chr(10)
import json
import os
import sys
import tempfile
import datetime as _dt
import time as _tg
from pathlib import Path

# PHẢI đặt trước khi import trader.* — `config.py` đọc biến này lúc nạp module,
# đặt sau thì DATA_DIR đã trỏ vào thư mục thật rồi.
#
# GHI ĐÈ, không `setdefault`. Bản cũ dùng `setdefault` nên hễ môi trường ĐÃ có
# `TCT_DATA_DIR` là phép kiểm chạy thẳng vào SỔ THẬT. Chuyện đó đã xảy ra hai
# lần: một dòng `export TCT_DATA_DIR=.../data` trong shell là đủ, và phép kiểm
# ghi 3 lệnh giả vào sổ giao dịch, đè kho chạy lại 86 → 40 bản, đè kho phát
# hiện 28 → 2.
#
# Mục [9] có bắt được — nhưng nó chỉ BÁO, và lúc báo thì các mục trước đã ghi
# xong rồi. Một phép kiểm phát hiện ô nhiễm sau khi ô nhiễm đã xảy ra thì chỉ
# là bản cáo phó. Chỗ đúng để chặn là ở đây, trước mọi import.
#
# Muốn chạy trên một sổ cụ thể thì sửa dòng này một cách có chủ ý, đừng để nó
# phụ thuộc vào một biến môi trường mà bất kỳ ai cũng có thể đã đặt vì việc khác.
os.environ["TCT_DATA_DIR"] = tempfile.mkdtemp(prefix="tct-selftest-")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx  # noqa: E402

from trader.brain import mock_thesis  # noqa: E402
from trader.broker import PaperBroker  # noqa: E402
from trader.config import CONFIG  # noqa: E402
from trader.data import get_market_data  # noqa: E402
from trader.features import build_market_state  # noqa: E402
from trader.regime import classify  # noqa: E402
from trader.risk import RiskEngine  # noqa: E402
from trader import store  # noqa: E402

FAILS: list[str] = []


def check(cond: bool, label: str) -> None:
    print(("  OK   " if cond else "  SAI  ") + label)
    if not cond:
        FAILS.append(label)


async def main() -> int:
    pri = CONFIG["timeframes"]["primary"]
    ctx = CONFIG["timeframes"]["context"]

    print("\n[1] MARKET DATA")
    async with httpx.AsyncClient() as c:
        m = await get_market_data(c)
    check(len(m["timeframes"][pri]) > 200, f"nến {pri}: {len(m['timeframes'][pri])}")
    check(m["price"] > 0, f"giá: {m['price']:,.2f}")
    print(f"       nguồn: {m['source']['name']} (thật: {m['source']['live']})")
    if not m["source"]["live"]:
        print("       ⚠ đang dùng nến TỔNG HỢP — số liệu dưới đây không phản ánh thị trường thật")

    print("\n[2] FEATURES")
    st = build_market_state(m)
    f = st["timeframes"][pri]
    check(f["rsi14"] is not None and 0 <= f["rsi14"] <= 100, f"RSI(14) = {f['rsi14']}")
    check(f["atr"] is not None and f["atr"] > 0, f"ATR = {f['atr']}")
    check(f["adx"] is not None, f"ADX = {f['adx']}  (+DI {f['plusDI']} / -DI {f['minusDI']})")
    check(f["emaStack"] in ("BULLISH_ALIGNED", "BEARISH_ALIGNED", "MIXED", "UNKNOWN"), f"EMA stack = {f['emaStack']}")
    check(f["structure"] in ("UPTREND", "DOWNTREND", "TRANSITION", "UNCLEAR"), f"cấu trúc = {f['structure']}")
    check(len(f["support"]) + len(f["resistance"]) > 0, f"vùng S/R: {len(f['support'])} hỗ trợ, {len(f['resistance'])} kháng cự")

    print("\n[3] REGIME")
    rg = classify(st, pri, ctx)
    check(rg["primary"] != "", f"{rg['primary']} · chất lượng {rg['quality']} · cờ {rg['flags'] or 'không'}")
    for r in rg["reasons"]:
        print(f"       • {r}")

    print("\n[4] BRAIN (mock)")
    th = mock_thesis(st, rg, pri)
    th["symbol"] = st["symbol"]
    check(th["action"] in ("LONG", "SHORT", "NO_TRADE"), f"hành động = {th['action']} (tin cậy {th['confidence']})")
    check(abs(sum(s["probability"] for s in th["scenarios"]) - 1.0) < 0.05, "tổng xác suất kịch bản ≈ 1.0")

    print("\n[5] RISK ENGINE")
    broker = PaperBroker(CONFIG["risk"])
    broker.reset()
    risk = RiskEngine(CONFIG["risk"])
    atr = f["_raw"]["atr"]
    d = risk.evaluate(th, st, broker.snapshot(st["price"]), atr)
    print(f"       phán quyết: {'CHO QUA' if d['approved'] else 'CHẶN/NO_TRADE'} — {d.get('note') or d.get('rejections')}")

    # Từng luật kiểm RIÊNG. Gộp nhiều vi phạm vào một luận điểm thì chỉ cần một
    # luật bắt được là test xanh — ba luật kia hỏng vẫn không ai biết.
    price = st["price"]

    def variant(**kw) -> dict:
        v = dict(th)
        v.update({"action": "LONG", "confidence": 0.8,
                  "entry_zone": [price * 0.999, price * 1.001], "suggested_risk_pct": 0.5})
        v.update(kw)
        return v

    def blocked_by(v: dict, code: str, label: str) -> None:
        d = risk.evaluate(v, st, broker.snapshot(price), atr)
        hit = (not d["approved"]) and any(code in r for r in d["rejections"])
        check(hit, label)
        if not hit:
            print(f"       → thực tế: {'CHO QUA' if d['approved'] else d['rejections']}")

    blocked_by(variant(invalidation=price - 1.5 * atr, targets=[price + 1.5 * atr]),
               "RR_THẤP", "chặn RR 1.0 (dưới ngưỡng 2.0)")
    blocked_by(variant(invalidation=price - 0.05 * atr, targets=[price + 5 * atr]),
               "SL_QUÁ_HẸP", "chặn SL 0.05×ATR (sẽ chết vì nhiễu)")
    blocked_by(variant(invalidation=price - 6 * atr, targets=[price + 20 * atr]),
               "SL_QUÁ_RỘNG", "chặn SL 6×ATR (một lệnh nuốt cả tuần)")
    blocked_by(variant(invalidation=price + 1.5 * atr, targets=[price + 3 * atr]),
               "SL_SAI_PHÍA", "chặn long mà SL đặt TRÊN giá vào")

    # Cùng luật, nhưng ở khoảng cách mà CHI PHÍ LỚN HƠN — đây là điều kiện đã
    # làm luật trên chết một lần. Hôm ATR nhỏ (0,094% giá), phí+trượt 0,15% đẩy
    # giá khớp vượt qua cả SL, nên phép so với giá khớp ra False và lệnh vô
    # nghĩa được duyệt — kèm khoảng stop teo lại còn 5,66 nên size phình to.
    # Dùng bội số ATR rất nhỏ để tái hiện điều kiện đó bất kể ATR hôm nay.
    blocked_by(variant(invalidation=price + 0.05 * atr, targets=[price + 3 * atr]),
               "SL_SAI_PHÍA", "chặn SL sai phía KỂ CẢ khi phí lớn hơn khoảng cách đó")

    # Chốt quan trọng nhất của cả nhóm này: SL sai phía KHÔNG ĐƯỢC làm size
    # phình lên. Đó mới là thứ gây hại — lệnh bị chặn thì thôi, nhưng nếu lọt
    # thì khoảng stop teo lại, RR trông đẹp, và vị thế to bất thường.
    for boi in (0.02, 0.05, 0.5, 1.5):
        d = risk.evaluate(variant(invalidation=price + boi * atr,
                                  targets=[price + 5 * atr]),
                          st, broker.snapshot(price), atr)
        check(not d["approved"],
              f"SL đặt TRÊN giá vào {boi}×ATR vẫn bị chặn "
              f"(chi phí {abs(price * (CONFIG['risk']['feeBps'] + CONFIG['risk']['slippageBps']) / 10_000):.0f} "
              f"so với {boi * atr:.0f})")
    blocked_by(variant(confidence=0.2, invalidation=price - 1.5 * atr, targets=[price + 3 * atr]),
               "CONFIDENCE_THẤP", "chặn tin cậy 0.2 (dưới 0.55)")

    # RR danh nghĩa 2.0 trên giá yêu cầu PHẢI bị chặn, vì sau phí+trượt nó không
    # còn là 2.0. Đây là phép kiểm chống lại chính cái bẫy vừa tìm ra.
    blocked_by(variant(invalidation=price - 1.5 * atr, targets=[price + 3.0 * atr]),
               "RR_THẤP", "chặn RR 2.0 trên giấy nhưng < 2.0 sau phí+trượt giá")

    # TP1 phải đặt ở bao nhiêu ×ATR mới giữ nổi RR tối thiểu sau chi phí?
    #
    # KHÔNG phải một hằng số. Chi phí (phí + trượt) tính theo % GIÁ, còn stop tính
    # theo ATR — nên khi biến động thấp, cùng 15bps ấy ăn phần lớn hơn trong RR.
    # Bản đầu của test này ghi cứng 4.8 và xanh; hôm sau ATR% tụt từ 0.377% xuống
    # 0.239% là nó đỏ, mà code thì không đổi dòng nào. Suy ra thay vì ghi cứng:
    #
    #     (k·ATR − drag) / (1.5·ATR + drag) ≥ minRR
    #   ⇒ k ≥ [ minRR·(1.5·ATR + drag) + drag ] / ATR
    rr_cfg = CONFIG["risk"]
    drag = price * (rr_cfg["feeBps"] + rr_cfg["slippageBps"]) / 10_000
    stop_that = 1.5 * atr + drag
    GOOD_TP = (rr_cfg["minRR"] * stop_that + drag) / atr
    print(f"       ATR {atr:.2f} ({atr / price * 100:.3f}% giá) · chi phí ${drag:.2f} "
          f"⇒ TP1 phải ở {GOOD_TP:.2f}×ATR mới đủ RR {rr_cfg['minRR']}")

    # Tin cậy cao KHÔNG được mua thêm rủi ro — đây là lời hứa trung tâm của cả hệ thống.
    greedy = variant(confidence=0.99, invalidation=price - 1.5 * atr,
                     targets=[price + GOOD_TP * atr], suggested_risk_pct=25.0)
    gd = risk.evaluate(greedy, st, broker.snapshot(price), atr)
    check(gd["approved"] and gd["position"]["riskPct"] <= CONFIG["risk"]["maxRiskPerTradePct"],
          f"tin cậy 0.99 xin 25% vốn → bị cắt còn {gd['position']['riskPct'] if gd['approved'] else '?'}%")

    ok_th = variant(invalidation=price - 1.5 * atr,
                    targets=[price + GOOD_TP * atr, price + 8.0 * atr],
                    suggested_risk_pct=25.0)
    od = risk.evaluate(ok_th, st, broker.snapshot(price), atr)
    check(od["approved"], "cho qua lệnh hợp lệ (RR đúng 2.0, SL 1.5×ATR)")
    if not od["approved"]:
        print(f"       → bị chặn bởi: {od['rejections']}")
    if od["approved"]:
        p = od["position"]
        cap = CONFIG["risk"]["maxRiskPerTradePct"]
        eq = broker.state["equity"]
        target = eq * cap / 100
        check(p["riskPct"] <= cap, f"…nhưng risk bị cắt {ok_th['suggested_risk_pct']}% → {p['riskPct']}% (trần {cap}%)")
        # Rủi ro thực tế có thể THẤP hơn trần khi trần notional ràng buộc trước:
        # spot không đòn bẩy + stop hẹp thì không thể đặt đủ vốn để mất 0.5%.
        # Lệch về phía an toàn thì đúng; lệch lên trên trần thì không bao giờ được.
        check(p["riskAmount"] <= target + 0.01,
              f"số tiền rủi ro ${p['riskAmount']} ≤ trần ${target:,.2f} ({cap}% của ${eq:,.0f})")
        if p["notionalCapped"]:
            print(f"       ↳ trần notional {CONFIG['risk']['maxNotionalPctOfEquity']}% ràng buộc trước: "
                  f"stop {p['stopDistance']} ({p['stopDistance'] / st['price'] * 100:.3f}% giá) quá hẹp để dùng hết {cap}% rủi ro")
        check(abs(p["rr"] - 2.0) < 0.15, f"RR tính trên TP1 SAU chi phí = {p['rr']}")
        check(p["expectedFill"] > p["entry"],
              f"thẩm định trên giá khớp dự kiến {p['expectedFill']:,.2f}, không phải giá yêu cầu "
              f"{p['entry']:,.2f} (chênh ${p['costDragOnEntry']})")

    # Tài khoản giữ cả coin lẫn tiền: vốn lớn, tiền mua được nhỏ. Sizing phải
    # theo tiền mua được, nếu không sàn từ chối sau khi đã tốn một lượt gọi model.
    print("\n[5b] TRẦN THEO SỐ DƯ MUA ĐƯỢC")
    acct = broker.snapshot(price)
    acct_giu_coin = {**acct, "equity": 73000.0, "availableQuote": 10000.0}
    dv = risk.evaluate(ok_th, st, acct_giu_coin, atr)
    check(dv["approved"], "vẫn cho qua khi vốn 73.000 nhưng chỉ 10.000 mua được")
    if dv["approved"]:
        v = dv["position"]
        check(v["notional"] <= 10000.0,
              f"notional {v['notional']:,.0f} ≤ tiền mua được 10.000 (vốn 73.000)")
        # Mẫu số phải là TIỀN MUA ĐƯỢC, không phải vốn ghi trên giấy.
        check(abs(v["riskAmount"] - 10000.0 * 0.005) < 0.01,
              f"rủi ro ${v['riskAmount']} = 0,5% của 10.000 mua được, không phải của 73.000")
        check(v["riskBaseIsCash"] and abs(v["riskBase"] - 10000.0) < 0.01,
              f"có khai rõ mẫu số đã dùng: {v['riskBase']:,.0f}")

    # — Bất biến quan trọng nhất của cả tầng này —
    # Cùng một tín hiệu, stop rộng hẹp khác nhau ⇒ RỦI RO PHẢI BẰNG NHAU, chỉ
    # khối lượng thay đổi. Công thức cũ làm ngược lại: khối lượng đứng im ở trần
    # tiền mặt còn rủi ro trôi 42 → 79 → 158 theo độ rộng stop. Chính chỗ trôi đó
    # đã biến kỳ vọng +0,282R thành khoản lỗ −$95,69 trên 8 lệnh thật.
    rr_theo_stop, qty_theo_stop = [], []
    for boi in (0.8, 1.5, 3.0):
        th_i = {**ok_th, "invalidation": price - atr * boi,
                "targets": [price + atr * boi * 4.0]}
        d_i = risk.evaluate(th_i, st, acct_giu_coin, atr * boi)
        if d_i["approved"]:
            rr_theo_stop.append(d_i["position"]["riskAmount"])
            qty_theo_stop.append(d_i["position"]["qty"])
    if len(rr_theo_stop) >= 2:
        check(max(rr_theo_stop) - min(rr_theo_stop) < 0.01,
              f"stop rộng hẹp khác nhau, rủi ro vẫn bằng nhau: "
              f"{' · '.join(f'{x:.2f}' for x in rr_theo_stop)}")
        check(max(qty_theo_stop) > min(qty_theo_stop) * 1.5,
              f"…và khối lượng mới là thứ thay đổi: "
              f"{' · '.join(f'{x:.5f}' for x in qty_theo_stop)}")
    else:
        check(False, f"chỉ có {len(rr_theo_stop)} lệnh qua cửa — không đo được bất biến")

    # Trần tiền mặt vẫn phải CÒN SỐNG, chỉ là từ nay hiếm khi chạm.
    #
    # Ở mức rủi ro 0,5% nó gần như không bao giờ chạm nữa — muốn chạm thì stop
    # phải hẹp dưới 0,5% giá, mà sàn stop tối thiểu 0,3×ATR đã chặn trước rồi.
    # Nên phải dựng một cỗ máy rủi ro CAO để gọi đúng nhánh đó ra; nếu không,
    # lưới an toàn nằm trong mã nguồn mà không phép kiểm nào đi qua, và ngày nó
    # hỏng thì không ai biết.
    from trader.risk import RiskEngine as _RE

    risk_cao = _RE({**risk.cfg, "maxRiskPerTradePct": 8.0})
    d_cao = risk_cao.evaluate({**ok_th, "suggested_risk_pct": 8.0}, st, acct_giu_coin, atr)
    if d_cao["approved"]:
        check(d_cao["position"]["notionalCapped"],
              "rủi ro 8%: lưới an toàn tiền mặt vẫn bắt được")
        check(d_cao["position"]["notional"] <= 10000.0,
              f"…và giữ notional {d_cao['position']['notional']:,.0f} trong tiền mua được")
        check(d_cao["position"]["riskAmount"] < 10000.0 * 0.08,
              f"…rủi ro thật ${d_cao['position']['riskAmount']:,.2f} thấp hơn mục tiêu 800 "
              f"vì bị cắt trần — cắt trần chỉ được làm rủi ro GIẢM")
    else:
        check(False, f"không gọi được nhánh cắt trần: {d_cao['note'][:70]}")

    print("\n[6] EXECUTION + JOURNAL")
    if od["approved"]:
        t = broker.open(od["position"], ok_th, rg)
        # Sau khi Risk Engine thẩm định trên giá khớp dự kiến, KẾ HOẠCH VÀ THỰC TẾ
        # PHẢI KHỚP NHAU. Lệch ở đây nghĩa là hai tầng đang mô hình hoá chi phí
        # khác nhau — và cái lệch đó sẽ âm thầm bò vào mọi R-multiple về sau.
        check(abs(t["riskAmount"] - t["plannedRiskAmount"]) < 0.02,
              f"rủi ro thật ${t['riskAmount']} == kế hoạch ${t['plannedRiskAmount']} (không còn trôi ngầm)")
        check(abs(t["rr"] - t["plannedRr"]) < 0.02,
              f"RR thật {t['rr']} == RR kế hoạch {t['plannedRr']}")

        eq0 = broker.state["equity"]
        broker.close(t, t["targets"][0], "TAKE_PROFIT")
        snap = broker.snapshot()
        check(snap["closedCount"] == 1, "giao dịch được ghi vào nhật ký")
        check(snap["equity"] > eq0, f"vốn {eq0:,.2f} → {snap['equity']:,.2f} sau khi chốt lãi")
        check(t["rMultiple"] < t["rr"], f"R thu được {t['rMultiple']} < RR thật {t['rr']} (phí hai đầu)")

    print("\n[7] NGẮT MẠCH")
    broker.state["equity"] = broker.state["peakEquity"] * 0.85   # drawdown 15%
    brk = risk.circuit_breakers(broker.snapshot())
    check(any("KILL_SWITCH" in b for b in brk), f"drawdown 15% kích kill switch: {brk[0] if brk else 'KHÔNG!'}")
    dd = risk.evaluate(ok_th, st, broker.snapshot(price), atr)
    check(not dd["approved"], "sau kill switch, lệnh hợp lệ vẫn bị chặn")

    print("\n[8] CHƯA ĐỌC ĐƯỢC SỐ DƯ ≠ MẤT SẠCH VỐN")
    # Lỗi thật đã xảy ra: lúc khởi động, peakEquity nạp từ đĩa còn số dư sàn
    # chưa về nên equity = 0 ⇒ ngắt mạch tính drawdown 100% rồi CHỐT CỨNG kill
    # switch. Số dư về sau vài giây, drawdown thật 0%, nhưng chốt không tự mở —
    # bot đứng im vĩnh viễn với dòng chữ không khớp con số nào trên màn hình.
    # Từ khi chạy nền tự khởi động, nó lặp lại mỗi lần bật máy.
    r2 = RiskEngine(CONFIG["risk"])
    chua_doc = {"equity": 0.0, "peakEquity": 73029.87, "equityKnown": False,
                "positions": [], "dailyPnl": {}, "dailyStartEquity": {}}
    brk2 = r2.circuit_breakers(chua_doc)
    check(any("CHUA_DOC_DUOC_SO_DU" in b for b in brk2),
          f"chưa đọc được số dư thì bị chặn: {brk2[0] if brk2 else 'KHÔNG CHẶN!'}")
    check(not any("KILL_SWITCH" in b for b in brk2),
          "…nhưng KHÔNG kích kill switch")
    check(r2.halted_reason is None,
          "…và không chốt cứng — lượt sau đọc được là chạy tiếp")

    # Đọc được rồi thì hàng rào thật phải hoạt động lại bình thường.
    da_doc = {**chua_doc, "equity": 73029.87, "equityKnown": True}
    check(not r2.circuit_breakers(da_doc), "đọc được số dư, vốn nguyên vẹn → không chặn gì")
    mat_that = {**chua_doc, "equity": 60000.0, "equityKnown": True}
    check(any("KILL_SWITCH" in b for b in r2.circuit_breakers(mat_that)),
          "vốn tụt thật 17.8% → kill switch vẫn kích như cũ")

    print("\n[9] PHÉP KIỂM KHÔNG ĐƯỢC GHI VÀO SỔ THẬT")
    from trader.config import DATA_DIR, ROOT

    that = ROOT / "data"
    if DATA_DIR.resolve() != that.resolve():
        check(True, f"sổ của phép kiểm nằm riêng: {DATA_DIR}")
    else:
        check(False, f"ĐANG GHI VÀO SỔ THẬT {that} — lệnh giả của phép kiểm sẽ "
                     f"trộn vào thống kê mà không ai phân biệt được")

    print("\n[10] ĐẾM KỸ NĂNG PHẢI ĐÚNG SỐ FILE")
    from trader.brain import load_skills
    from trader.config import SKILLS_DIR

    _, dem = load_skills()
    tren_dia = len([d for d in SKILLS_DIR.iterdir()
                    if (d / "SKILL.md").exists() or d.suffix == ".md"]) if SKILLS_DIR.exists() else 0
    check(dem == tren_dia, f"đếm được {dem} kỹ năng, trên đĩa có {tren_dia}")

    print("\n[11] HẬU KIỂM PHẢI PHÂN BIỆT ĐƯỢC LỆNH, VÀ CHỈ ĐÒI ĐỔI CHIẾN LƯỢC KHI CÓ LẶP LẠI")
    from trader.brain import mock_postmortem

    # Sổ giả dựng đúng hình dạng đã đo được trên 8 lệnh thật: ba lệnh thắng cược
    # NHỎ, hai lệnh thua cược LỚN. Đây là hình dạng đã biến kỳ vọng +0,282R thành
    # khoản lỗ −$95,69, nên nó là thứ phép kiểm phải bắt được.
    so_gia = [
        {"id": "a", "status": "CLOSED", "pnl": 60.0, "riskAmount": 37.0, "exitReason": "TAKE_PROFIT", "regimeKey": "K"},
        {"id": "b", "status": "CLOSED", "pnl": 40.0, "riskAmount": 45.0, "exitReason": "TAKE_PROFIT", "regimeKey": "K"},
        {"id": "c", "status": "CLOSED", "pnl": -45.0, "riskAmount": 45.0, "exitReason": "STOP_LOSS", "regimeKey": "K"},
        {"id": "d", "status": "CLOSED", "pnl": -53.0, "riskAmount": 53.0, "exitReason": "STOP_LOSS", "regimeKey": "K"},
        {"id": "e", "status": "CLOSED", "pnl": 58.0, "riskAmount": 58.0, "exitReason": "TAKE_PROFIT", "regimeKey": "K"},
        {"id": "f", "status": "CLOSED", "pnl": -63.0, "riskAmount": 63.0, "exitReason": "STOP_LOSS", "regimeKey": "K"},
        {"id": "g", "status": "CLOSED", "pnl": -104.0, "riskAmount": 104.0, "exitReason": "STOP_LOSS", "regimeKey": "K"},
        {"id": "h", "status": "CLOSED", "pnl": -112.0, "riskAmount": 112.0, "exitReason": "STOP_LOSS", "regimeKey": "K"},
    ]
    ket = [mock_postmortem(t, so_gia) for t in so_gia]
    cau = {k["lesson"] for k in ket}
    check(len(cau) >= 4, f"8 lệnh khác nhau ra {len(cau)} câu bài học khác nhau "
                         f"(bản dán nhãn cũ chỉ ra 2)")

    # Lệnh THẮNG mà cược lệch phải bị gọi là quyết định tồi — loại nguy hiểm nhất,
    # vì phần thưởng đến ngay và dạy đúng thứ không được lặp lại.
    thang_lech = next(k for k, t in zip(ket, so_gia) if t["id"] == "a")
    check(thang_lech["classification"] == "BAD_TRADE_GOOD_OUTCOME",
          f'lệnh thắng nhưng cược lệch 0,5× → {thang_lech["classification"]}')

    doi = sum(1 for k in ket if k["change_strategy"])
    check(doi >= 3, f"{doi} bài đòi đổi chiến lược khi tật lặp lại trên 3/8 lệnh")

    # Và cửa ngược lại: sổ mà mọi lệnh cược ĐỀU thì KHÔNG được đòi đổi chiến lược,
    # dù có thua. Thiếu cửa này thì mỗi lệnh thua lại đòi đổi một lần, và bài học
    # đắt nhất trong kho biến thành tiếng ồn.
    so_deu = [{"id": str(i), "status": "CLOSED", "pnl": (50.0 if i % 3 else -50.0),
               "riskAmount": 50.0, "exitReason": ("TAKE_PROFIT" if i % 3 else "STOP_LOSS"),
               "barsHeld": 20, "regimeKey": f"K{i}"} for i in range(8)]
    doi_deu = sum(1 for t in so_deu if mock_postmortem(t, so_deu)["change_strategy"])
    check(doi_deu == 0, f"sổ cược đều: {doi_deu} bài đòi đổi chiến lược (phải là 0)")

    print("\n[12] LÒ CHƯNG CẤT — ĐO ĐƯỢC PHẢI NHỚ ĐƯỢC, VÀ PHẢI ĐỔI ĐƯỢC HÀNH VI")
    from trader import chung_cat

    # Kho chạy lại giả: một chế độ lỗ sâu và đủ mẫu, một chế độ lỗ nhẹ thiếu mẫu.
    # `khung` bắt buộc: từ khi cầu dao đòi khung khớp, bài học không ghi khung
    # thì không bao giờ ngắt — xem mục [17]. Fixture phải giống hàng thật.
    _tf12 = CONFIG["timeframes"]["primary"]
    store.write_all(store.LESSONS_CHAY_LAI, [
        {"regimeKey": "XAU|none", "regime": "XAU", "rMultiple": -0.5, "khung": _tf12, "at": "x"}
        for _ in range(36)
    ] + [
        {"regimeKey": "IT|none", "regime": "IT", "rMultiple": -0.4, "khung": _tf12, "at": "x"}
        for _ in range(4)
    ])
    kq = chung_cat.chung_cat()
    ds = {p["ma"]: p for p in store.read_all(store.PHAT_HIEN)}

    check(f"che-do:{_tf12}:XAU|none" in ds, "chế độ đủ mẫu ra được phát hiện")
    check(f"che-do:{_tf12}:IT|none" not in ds, "chế độ 4 lệnh KHÔNG ra phát hiện (dưới ngưỡng 10)")

    # Từ chối phải ĐẾM ĐƯỢC. Bỏ im lặng thì "không phát hiện nào" trông y hệt
    # "chưa đo lần nào", và hai chuyện đó cần phân biệt được từ bên ngoài.
    check(any(b["ma"] == f"che-do:{_tf12}:IT|none" for b in kq["daBo"]),
          f"cái bị bỏ có ghi lý do ({kq['soDaBo']} mục trong daBo)")

    if f"che-do:{_tf12}:XAU|none" in ds:
        cau = ds[f"che-do:{_tf12}:XAU|none"]["cau"]
        check("36" in cau, "cỡ mẫu nằm TRONG câu, không chỉ ở trường bên cạnh")
        check("CHẠY LẠI" in cau, "câu tự khai nguồn là lệnh mô phỏng")

    # — Cầu dao: chỉ ngắt chế độ đã đo đủ sâu và đủ nhiều —
    check(chung_cat.cau_dao("XAU|none", "XAU") is not None,
          "cầu dao NGẮT chế độ lỗ -0,5R qua 36 lệnh")
    check(chung_cat.cau_dao("IT|none", "IT") is None,
          "cầu dao KHÔNG ngắt chế độ chỉ 4 lệnh")

    # Cửa ngược lại: lỗ nông thì dù đủ mẫu cũng không được ngắt. Thiếu phép kiểm
    # này thì ngưỡng sẽ trôi dần cho tới khi mọi chế độ đều bị khai tử — mà chế
    # độ bị khai tử thì không bao giờ thu thêm dữ liệu để cãi lại.
    store.write_all(store.LESSONS_CHAY_LAI, [
        {"regimeKey": "NONG|none", "regime": "NONG", "rMultiple": -0.15, "khung": _tf12, "at": "x"}
        for _ in range(40)
    ])
    chung_cat.chung_cat()
    check(chung_cat.cau_dao("NONG|none", "NONG") is None,
          "cầu dao KHÔNG ngắt chế độ lỗ nông -0,15R dù có 40 lệnh")

    # Xếp theo bằng chứng: câu mẫu lớn phải sống sót khi bị cắt bớt.
    store.write_all(store.PHAT_HIEN, [
        {"ma": "nho", "nguon": "dai-quan-sat", "cheDo": None, "cau": "x",
         "mau": 2, "doTin": "THẤP", "so": {}, "luc": "x"},
        {"ma": "lon", "nguon": "chien-luoc", "cheDo": None, "cau": "y",
         "mau": 44, "doTin": "CAO", "so": {}, "luc": "x"},
    ])
    dau = chung_cat.doc(None, None, gioi_han=1)
    check(dau and dau[0]["ma"] == "lon",
          f"cắt bớt thì giữ câu bằng chứng mạnh: giữ '{dau[0]['ma'] if dau else '—'}'")

    print("\n[13] MẪU GIÁ — CHỈ TÍNH KHI ĐÃ XÁC NHẬN, VÀ KHÔNG ĐƯỢC NHÌN TƯƠNG LAI")
    from trader import mau_gia

    def _nen(o, h, l, c, t=0):
        return {"t": t, "o": o, "h": h, "l": l, "c": c, "v": 100.0, "closed": True}

    # Hai đỉnh dựng tay: lên 100→120, về 110, lên lại 120, rồi thủng 110.
    # Xây bằng số bịa chứ không lấy từ lịch sử — phép kiểm phải kiểm ĐỊNH NGHĨA,
    # còn dữ liệu thật thì đo ở scripts/do-mau-gia.py.
    def _dung_hai_dinh(pha_co_ao: bool):
        # Đường giá zigzag rõ ràng, mỗi bước một nến. Không chèn nến đi ngang ở
        # đỉnh: `swings()` đòi hai bên THẤP HẲN, nên hai nến bằng nhau ở đỉnh là
        # đủ để không đỉnh nào được xác nhận — và cả mẫu biến mất mà không báo gì.
        duong = [100.0]
        def _toi(muc, buoc=0.5):
            b = buoc if muc > duong[-1] else -buoc
            while abs(duong[-1] - muc) > buoc:
                duong.append(duong[-1] + b)
            duong.append(muc)
        _toi(120.0)                       # đỉnh 1
        _toi(110.0)                       # cổ áo
        _toi(119.5)                       # đỉnh 2 — lệch 0,4% so với đỉnh 1
        _toi(108.0 if pha_co_ao else 112.0)
        # Râu nến ở ĐÚNG điểm quay đầu. Không có nó thì nến trước và nến sau
        # đỉnh cùng có đúng một giá cao nhất, và `swings()` — vốn đòi hai bên
        # THẤP HẲN — không xác nhận đỉnh nào cả. Đây chính là bẫy đã làm phép
        # kiểm này đỏ ở lần dựng đầu.
        ds = []
        for k in range(1, len(duong)):
            a, b = duong[k - 1], duong[k]
            h, l = max(a, b), min(a, b)
            truoc = duong[k - 1]
            sau = duong[k + 1] if k + 1 < len(duong) else b
            if b > truoc and b > sau:      # đỉnh
                h = b + 0.3
            elif b < truoc and b < sau:    # đáy
                l = b - 0.3
            ds.append(_nen(a, h, l, b, k))
        return ds

    chua = mau_gia.nhan_dien(_dung_hai_dinh(False))
    da = mau_gia.nhan_dien(_dung_hai_dinh(True))
    ten_chua = {m["ten"] for m in chua}
    ten_da = {m["ten"] for m in da}

    # Cửa quan trọng nhất của cả module: chưa phá cổ áo thì CHƯA phải mẫu.
    # Thiếu nó là đang chấm điểm cho chính cái hình mình vừa vẽ, và tỉ lệ thắng
    # sẽ đẹp một cách vô nghĩa.
    check("HAI_ĐỈNH" not in ten_chua,
          f"chưa phá cổ áo → chưa tính là mẫu (thấy: {sorted(ten_chua) or 'không có'})")
    check("HAI_ĐỈNH" in ten_da,
          f"đã phá cổ áo → nhận ra HAI_ĐỈNH (thấy: {sorted(ten_da) or 'không có'})")

    if "HAI_ĐỈNH" in ten_da:
        m = next(x for x in da if x["ten"] == "HAI_ĐỈNH")
        # Ba con số này là điều kiện để ĐO ĐƯỢC. Thiếu một cái thì "mẫu này đúng
        # 70%" là câu rỗng: đúng tới đâu, sai thì mất bao nhiêu, không ai biết.
        check(m["vao"] and m["stop"] and m["mucTieu"],
              f"mẫu tự khai đủ vào/stop/mục tiêu: {m['vao']}/{m['stop']}/{m['mucTieu']}")
        check(m["huong"] == "SHORT" and m["stop"] > m["vao"] > m["mucTieu"],
              f"hình học đúng phía cho SHORT: stop {m['stop']} > vào {m['vao']} > đích {m['mucTieu']}")

    # Không nhìn tương lai: cắt bớt nến ở CUỐI phải đổi kết quả, thêm nến vào
    # ĐẦU thì không. Nếu thêm nến quá khứ mà mẫu tại nến cuối đổi, nghĩa là cửa
    # sổ đang rò — và mọi số đo sẽ pha lẫn thông tin không có thật lúc đó.
    goc = _dung_hai_dinh(True)
    dem_them = [_nen(100.0, 100.2, 99.8, 100.0, -i) for i in range(5, 0, -1)] + goc
    a = {m["ten"] for m in mau_gia.nhan_dien(goc)}
    b = {m["ten"] for m in mau_gia.nhan_dien(dem_them)}
    check(a == b, f"thêm nến quá khứ không đổi mẫu tại nến cuối ({sorted(a)} vs {sorted(b)})")

    # Hai mẫu ngược hướng cùng xác nhận là MÂU THUẪN, không phải trung tính.
    tt = mau_gia.tom_tat([{"ten": "A", "loai": "x", "huong": "LONG", "rr": 2, "doTin": .5},
                          {"ten": "B", "loai": "x", "huong": "SHORT", "rr": 2, "doTin": .5}])
    check(tt["mauThuan"], "hai mẫu ngược hướng → cờ mâu thuẫn, không lấy trung bình")
    check(mau_gia.tom_tat([])["co"] is False, "không mẫu nào → co=False, không phải rỗng lặng lẽ")

    print("\n[14] NHIỀU CHỢ · NGHI THỨC · HÌNH HỌC KHUNG")
    from trader import chung_cat as CC, nghi_thuc as NT

    # — Nguồn «nhiều chợ»: dương ở một chợ KHÔNG được nói như dương ở mọi chợ —
    (DATA_DIR / "dau-nhieu-cho.json").write_text(json.dumps({
        "cho": ["A:4h", "B:4h"],
        "ket": {"MOT_CHO": {"A:4h": {"kyVongR": 0.4, "so": 30},
                            "B:4h": {"kyVongR": -0.3, "so": 30}},
                "MOI_CHO": {"A:4h": {"kyVongR": 0.2, "so": 30},
                            "B:4h": {"kyVongR": 0.1, "so": 30}},
                "THIEU_MAU": {"A:4h": {"kyVongR": 0.9, "so": 3},
                              "B:4h": {"kyVongR": 0.8, "so": 3}}},
    }, ensure_ascii=False), encoding="utf-8")
    bo = []
    ds = {p["ma"]: p for p in CC._tu_nhieu_cho(bo)}

    check("cho:MOT_CHO" in ds and "may rủi" in ds["cho:MOT_CHO"]["cau"],
          "dương 1/2 chợ → nói rõ chưa phân biệt được lợi thế với may rủi")
    check("cho:MOI_CHO" in ds and "MỌI chợ" in ds["cho:MOI_CHO"]["cau"],
          "dương 2/2 chợ → nói rõ đây là dấu hiệu lợi thế thật")
    # Cửa ngược lại: kỳ vọng đẹp mà mẫu bé thì KHÔNG được thành phát hiện.
    check("cho:THIEU_MAU" not in ds,
          f"+0,9R mà chỉ 3 lệnh/chợ → bị bỏ (bỏ {len(bo)} mục, có ghi lý do)")
    check(any(b["ma"] == "cho:THIEU_MAU" for b in bo),
          "…và cái bị bỏ có ghi lý do, không biến mất im lặng")

    # — Nghi thức: hạn phải chặn được, và ép phải vượt được —
    (DATA_DIR / "nghi-thuc.json").write_text(json.dumps(
        {"luc": "x", "mocGiay": _tg.time(), "ketQua": {}}, ensure_ascii=False),
        encoding="utf-8")
    check(NT.den_han() is False, "vừa chạy xong → chưa tới hạn, không chạy lại")
    (DATA_DIR / "nghi-thuc.json").write_text(json.dumps(
        {"luc": "x", "mocGiay": _tg.time() - NT.MOI_GIAY - 10, "ketQua": {}},
        ensure_ascii=False), encoding="utf-8")
    check(NT.den_han() is True, f"quá {NT.MOI_GIAY // 3600} tiếng → tới hạn")
    # Thứ tự không được đổi: đo → chưng cất → bàn giao. Bàn giao chạy trước thì
    # bản tóm tắt mô tả trạng thái CHƯA có kết quả đo mới, và nó xanh, và nó sai.
    check(NT.VIEC_CUOI[0][0] == "bàn giao" and
          all(v[0] != "bàn giao" for v in NT.VIEC),
          "bàn giao nằm ở nhóm chạy CUỐI, sau chưng cất")

    # — Hình học khung: khung ngắn phải kém hơn khung dài, và bảng phải nói ra —
    (DATA_DIR / "do-khung.json").write_text(json.dumps({
        "ket": {"X": {"5m": {"soDiem": 900, "muc": {"2.0": {"tyLeCham": 10.0,
                                                            "hoaVonCanTyLe": 33.3}}},
                      "1d": {"soDiem": 900, "muc": {"2.0": {"tyLeCham": 32.0,
                                                            "hoaVonCanTyLe": 33.3}}}}},
    }, ensure_ascii=False), encoding="utf-8")
    bo2 = []
    ds2 = {p["ma"]: p for p in CC._tu_do_khung(bo2)}
    check("khung-nao-do-noi" in ds2, "đo khung ra được phát hiện xếp hạng")
    if "khung-nao-do-noi" in ds2:
        so = ds2["khung-nao-do-noi"]["so"]
        check(so["totNhat"] == "1d" and so["teNhat"] == "5m",
              f"xếp đúng: tốt nhất {so['totNhat']}, tệ nhất {so['teNhat']}")
    check("khung-ngan-chet-vi-phi" in ds2,
          "khung 5m kém quá 15 điểm → có câu riêng về chi phí")

    print("\n[15] SỔ GIẢ THUYẾT — KHÔNG DỜI ĐƯỢC CỘT MỐC")
    from trader import so_gia_thuyet as G

    NG = {"truong": "kyVongR", "toanTu": ">", "giaTri": 0.0, "mauToiThieu": 20}
    r1 = G.khai("gt-thu", "câu hỏi", "dự đoán", "cách đo", NG)
    check(r1["ok"], "khai được một giả thuyết mới")

    # Khai trùng mã là cách êm nhất để ghi đè dự đoán cũ sau khi đã thấy số.
    check(G.khai("gt-thu", "khác", "khác", "khác", NG)["ok"] is False,
          "khai TRÙNG MÃ bị chặn — nếu không thì dự đoán cũ bị đè")

    # Chốt cái chưa khai: khi đó mọi kết quả đều 'đúng như dự đoán'.
    check(G.chot("chua-khai-bao-gio", {"kyVongR": 9.9, "mau": 999})["ok"] is False,
          "chốt cái CHƯA KHAI bị chặn")

    r2 = G.chot("gt-thu", {"kyVongR": -0.3, "mau": 50})
    check(r2["ok"] and r2["phanQuyet"] == "BÁC_BỎ",
          f"đo −0,3R với ngưỡng >0 → {r2.get('phanQuyet')}")
    check(G.chot("gt-thu", {"kyVongR": 9.9, "mau": 999})["ok"] is False,
          "chốt LẠI bị chặn — đây chính là dời cột mốc")

    # Mẫu bé phải ra KHÔNG_KẾT_LUẬN, không phải BÁC_BỎ. «Chưa đo đủ» và «đo ra
    # sai» là hai chuyện, gộp lại là khai tử oan một hướng còn có thể đúng.
    G.khai("gt-be", "c", "d", "e", NG)
    r3 = G.chot("gt-be", {"kyVongR": -0.9, "mau": 3})
    check(r3["phanQuyet"] == "KHÔNG_KẾT_LUẬN",
          f"mẫu 3 < ngưỡng 20 → {r3['phanQuyet']}, không phải BÁC_BỎ")

    # Sổ append-only: ghi đè phải bị chặn ở tầng store.
    try:
        store.write_all(store.GIA_THUYET, [])
        check(False, "GHI ĐÈ ĐƯỢC sổ giả thuyết — mất khả năng chứng minh đã dự đoán trước")
    except ValueError:
        check(True, "store từ chối ghi đè sổ giả thuyết")

    # Phán quyết là hàm THUẦN — kiểm được bằng số bịa, không cần chạy cả cỗ máy.
    check(G._phan_quyet(NG, {"kyVongR": 0.1, "mau": 20})[0] == "XÁC_NHẬN",
          "hàm phán quyết thuần: 0,1R với mẫu 20 → XÁC_NHẬN")
    check(G._phan_quyet(NG, {"kyVongR": 0.1, "mau": 19})[0] == "KHÔNG_KẾT_LUẬN",
          "…mẫu 19 → KHÔNG_KẾT_LUẬN, ngưỡng không nhân nhượng một đơn vị")

    # Tra ra được cái đã hỏng — công cụ đáng gọi nhất trong module.
    check(any(g["ma"] == "gt-thu" for g in G.tra("gt-thu")),
          "tra ra được giả thuyết đã bác bỏ")

    print("\n[16] BÀN GIAO — PHẢI BIẾT BOT ĐANG TẮT, VÀ KHÔNG ĐƯỢC TỰ ĂN MẤT PHẦN SO SÁNH")
    import importlib.util as _il
    _sp = _il.spec_from_file_location("bg", str(ROOT / "scripts" / "ban-giao.py"))
    BG = _il.module_from_spec(_sp)
    _sp.loader.exec_module(BG)

    # — Chọn mốc so sánh: ảnh chụp vừa ghi 2 phút trước KHÔNG được che mất
    #   ảnh chụp của hôm qua. Đây là lỗi đã đo được: nghi thức tự chạy lúc
    #   13:59, mở bàn giao lúc 14:01, và nó báo "không có gì đổi" trong khi số
    #   lệnh thật vừa nhảy 17 → 38.
    _now = _dt.datetime.now(_dt.timezone.utc)

    def _anh(gio_truoc, so_lenh):
        return {"luc": (_now - _dt.timedelta(hours=gio_truoc)).isoformat(timespec="seconds"),
                "soLenhThat": so_lenh, "phatHien": {}, "soKyNang": 1, "soBoLuat": 1}

    BG.LICH_SU.write_text(
        json.dumps(_anh(30, 17), ensure_ascii=False) + "\n"
        + json.dumps(_anh(0.03, 38), ensure_ascii=False) + "\n", encoding="utf-8")
    cu, gio = BG._doc_truoc()
    check(cu.get("soLenhThat") == 17 and gio and gio > 6,
          f"có ảnh 30h và ảnh 2 phút → chọn ảnh {gio:.0f}h ({cu.get('soLenhThat')} lệnh), "
          f"không để ảnh mới che mất")

    # Chỉ có ảnh quá mới thì vẫn phải so, NHƯNG phải khai ra là mốc quá gần.
    BG.LICH_SU.write_text(json.dumps(_anh(0.03, 38), ensure_ascii=False) + "\n",
                          encoding="utf-8")
    cu2, gio2 = BG._doc_truoc()
    check(cu2.get("soLenhThat") == 38 and gio2 is not None and gio2 < 1,
          f"chỉ có ảnh 2 phút → vẫn dùng, và trả về tuổi {gio2:.2f}h để báo cáo nói rõ")

    # — Sống hay chết: không có nhật ký phải kêu lên, không được im —
    BG.LICH_SU.unlink(missing_ok=True)
    # Ép cổng "đang trả lời" để phép kiểm chỉ đo phần NHẬT KÝ. Không ép thì kết
    # quả đổi theo việc runtime có tình cờ chạy hay không, và nó đã đỏ một lần
    # vì thế trong khi mã đúng.
    BG._cong_tra_loi = lambda cong: True
    canh = BG._con_song()
    check(any("KHÔNG CÓ NHẬT KÝ" in x or "IM" in x for x in canh),
          f"không có nhật ký runtime → có cảnh báo ({len(canh)} dòng)")

    # Nhật ký cũ 3 ngày phải bị bắt. Đây là cái đã im suốt 5 ngày rưỡi.
    _nk = DATA_DIR / "nhat-ky"
    _nk.mkdir(parents=True, exist_ok=True)
    _f = _nk / "runtime.log"
    _f.write_text("x", encoding="utf-8")
    _cu = _tg.time() - 3 * 86400
    os.utime(_f, (_cu, _cu))
    canh2 = BG._con_song()
    check(any("IM" in x and "ngày" in x for x in canh2),
          f"nhật ký cũ 3 ngày → báo im lặng kèm số ngày")

    # Và cửa ngược lại: nhật ký vừa ghi xong thì KHÔNG được kêu.
    os.utime(_f, None)
    check(not any("IM" in x for x in BG._con_song()),
          "nhật ký vừa ghi → không kêu (nếu không thì cảnh báo thành tiếng ồn)")

    BG._cong_tra_loi = lambda cong: False
    check(any("KHÔNG TRẢ LỜI" in x for x in BG._con_song()),
          "cổng câm → báo bot đang TẮT, kể cả khi nhật ký vừa ghi")

    print("\n[17] CẦU DAO KHÔNG ĐƯỢC CHẶN KHUNG NÀY BẰNG BẰNG CHỨNG CỦA KHUNG KHÁC")
    from trader import chung_cat as CC2
    from trader.config import CONFIG as CFG2

    # «TREND_UP|none» trên 1h và trên 4h là hai thị trường khác hẳn nhau mang
    # cùng một cái tên. Bản đầu gom bài học chạy lại theo mình chế độ, nên khi
    # bản chạy thật đổi sang 4h thì cầu dao lấy bằng chứng 1h ra chặn — bot đứng
    # im ở đúng chế độ mà bằng chứng 4h nói là được, và không có gì báo sai.
    _tf_cu = CFG2["timeframes"]["primary"]
    try:
        store.write_all(store.LESSONS_CHAY_LAI,
                        [{"regimeKey": "K|none", "regime": "K", "rMultiple": -0.6,
                          "khung": "1h", "at": "x"} for _ in range(40)])
        CC2.chung_cat()

        CFG2["timeframes"]["primary"] = "1h"
        check(CC2.cau_dao("K|none", "K") is not None,
              "đang chạy 1h + bằng chứng 1h → cầu dao NGẮT")

        CFG2["timeframes"]["primary"] = "4h"
        check(CC2.cau_dao("K|none", "K") is None,
              "đang chạy 4h + bằng chứng 1h → KHÔNG ngắt (đây là lỗi đã sập một lần)")

        # Bài học cũ chưa có trường `khung` cũng không được cho cầu dao dùng:
        # thà không chặn còn hơn chặn nhầm — cầu dao là thứ DUY NHẤT tự ý ngăn
        # bot giao dịch, nên nó phải chắc chắn hơn mọi thứ khác trong hệ.
        store.write_all(store.LESSONS_CHAY_LAI,
                        [{"regimeKey": "K|none", "regime": "K", "rMultiple": -0.6,
                          "at": "x"} for _ in range(40)])
        CC2.chung_cat()
        CFG2["timeframes"]["primary"] = "1h"
        check(CC2.cau_dao("K|none", "K") is None,
              "bài học KHÔNG ghi khung → không bao giờ ngắt")

        # Nhưng nó vẫn phải VÀO prompt làm bối cảnh, kèm nhãn khung.
        ds17 = CC2.doc("K|none", "K")
        co = [p for p in ds17 if p.get("cheDo") == "K|none"]
        check(bool(co), f"vẫn đưa vào prompt làm bối cảnh ({len(co)} phát hiện)")
        if co:
            check("khung" in co[0]["cau"].lower(),
                  "…và câu tự khai khung nó được đo trên")
    finally:
        CFG2["timeframes"]["primary"] = _tf_cu

    print("\n[18] BỘ NÃO QUA CLI — QUOTA GÓI, VÀ BỐN CHỐT AN TOÀN")
    from trader import cli_claude as CLI
    from trader import config as CFG3

    # — Bóc JSON: CLI hay trả kèm rào ```json —
    check(CLI._boc_json('```json\n{"a":1}\n```') == {"a": 1},
          "bóc được JSON nằm trong rào ```json")
    check(CLI._boc_json('{"a":2}') == {"a": 2}, "bóc được JSON trần")
    check(CLI._boc_json('Đây là kết quả: {"a":3} — hết.') == {"a": 3},
          "bóc được JSON lẫn trong câu chữ")
    try:
        CLI._boc_json("không có json ở đây")
        check(False, "chuỗi rác phải NÉM, không được trả dict rỗng")
    except ValueError:
        # Nuốt im ở đây là để bộ não chạy trên một dict rỗng và ra quyết định
        # trên số 0 — tệ hơn nhiều so với rơi về mock.
        check(True, "chuỗi rác thì NÉM, không im lặng trả rỗng")

    # — Chốt an toàn: phải TẮT công cụ —
    # Bộ não giao dịch chỉ cần suy luận trên dữ liệu được đưa vào. Cho nó quyền
    # chạy Bash/Write trên máy là mở một cửa không ai xin.
    for cong_cu in ("Bash", "Write", "Edit", "WebFetch"):
        check(cong_cu in CLI.TAT_CONG_CU, f"{cong_cu} nằm trong danh sách tắt")
    # Trần thời gian phải NHỎ HƠN giãn cách giữa hai luận điểm. Đó mới là bất
    # biến thật: một lượt gọi treo không được kéo dài quá lượt kế tiếp, nếu không
    # hai lượt chồng nhau và tiêu quota gấp đôi cho cùng một cây nến.
    #
    # Ngưỡng cũ "≤300s" dựa trên tiền đề SAI là vòng lặp sẽ đứng chờ. Nó không:
    # `asyncio.to_thread` giữ vòng lặp sống, và `tick()` được await tuần tự nên
    # không có lượt thứ hai nào bắt đầu. Canh nhầm bất biến thì phép kiểm sẽ đỏ
    # đúng lúc mã đang đúng — và lần này nó đã đỏ như thế.
    _gian = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))["brain"]
    _gian = (_gian.get("cli") or {}).get("minSecondsBetweenTheses") or _gian["minSecondsBetweenTheses"]
    check(0 < CLI.HET_GIAY < _gian,
          f"trần {CLI.HET_GIAY}s < giãn cách {_gian}s — lượt treo không chồng lượt sau")

    # — Chọn chế độ: đúng thứ tự ưu tiên —
    _bo = {k: os.environ.get(k) for k in ("BRAIN", "ANTHROPIC_API_KEY")}
    try:
        os.environ["BRAIN"] = "mock"
        check(CFG3.brain_mode() == "mock", "BRAIN=mock luôn thắng, kể cả khi có CLI")

        os.environ["BRAIN"] = "auto"
        os.environ["ANTHROPIC_API_KEY"] = "sk-thu-nghiem"
        check(CFG3.brain_mode() == "claude",
              "auto + có khoá API → claude (người đã chọn trả tiền thì đừng đổi hộ)")

        os.environ.pop("ANTHROPIC_API_KEY", None)
        mong = "cli" if CLI.co_the() else "mock"
        check(CFG3.brain_mode() == mong,
              f"auto + không khoá → {mong} (CLI trên máy này: {CLI.co_the()})")
    finally:
        for k, v in _bo.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    # — Đường CLI không ép được kiểu, nên tầng nhận phải tự dọn —
    from trader.brain import _ma_hop_le, _don_dep_cli
    check(_ma_hop_le("MOCK_RULES_V1") and not _ma_hop_le("Chiến lược dài dòng"),
          "phân biệt được MÃ chiến lược với câu văn")
    _d = {"strategy": "NO_TRADE — bốn lý do cộng hưởng đo được: (1) expectancy âm"}
    _don_dep_cli(_d, "thu")
    check(_d["strategy"] == "CLI_V1",
          "câu văn lọt vào `strategy` bị đổi thành mã, không làm vỡ bảng byStrategy")
    # `strategy` hỏi BỘ LUẬT nào, không hỏi lần này làm gì. Đo được trong sổ:
    # NO_TRADE, NO_TRADE_MTF_CONFLICT, NO_TRADE_STAT_GATE — qua được phép kiểm
    # ký tự (HOA + gạch dưới) nhưng trả lời sai câu hỏi.
    for _hd in ("NO_TRADE", "NO_TRADE_MTF_CONFLICT", "LONG_BREAKOUT"):
        _x = {"strategy": _hd}
        _don_dep_cli(_x, "thu")
        check(_x["strategy"] == "CLI_V1", f"«{_hd}» là hành động → đổi thành mã bộ luật")

    _g = {"strategy": "MOCK_RULES_V1"}
    _don_dep_cli(_g, "thu")
    check(_g["strategy"] == "MOCK_RULES_V1", "…và mã hợp lệ thì KHÔNG bị đụng vào")

    # `source` phải nói THẬT ai đã nghĩ. Bản cũ chỉ nhận mode "claude", nên mọi
    # quyết định của bộ não thật ở chế độ cli bị ghi là "mock" — sổ luận điểm
    # khi đó nói rằng bộ não chưa từng chạy, và không có gì mâu thuẫn với nó.
    import inspect as _ins18
    import trader.brain as _B18
    _src18 = _ins18.getsource(_B18.Brain)
    check('out["source"] = ("mock"' in _src18,
          "source tính theo mode thật, không chỉ nhận «claude»")
    check('else self.mode)' in _src18,
          "…và ghi thẳng tên chế độ, nên thêm đường thứ tư không phải sửa lại")

    # — Trần quota riêng của CLI phải CHẶT HƠN đường API —
    goc = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))["brain"]
    rieng = goc.get("cli") or {}
    check(bool(rieng), "config có khối brain.cli riêng")
    if rieng:
        check(rieng["maxCallsPerDay"] < goc["maxCallsPerDay"],
              f"trần lượt/ngày chặt hơn: {rieng['maxCallsPerDay']} < {goc['maxCallsPerDay']}")
        check(rieng["minSecondsBetweenTheses"] > goc["minSecondsBetweenTheses"],
              f"giãn cách rộng hơn: {rieng['minSecondsBetweenTheses']}s > "
              f"{goc['minSecondsBetweenTheses']}s")
        # Mỗi lượt nạp ~14k token. Trần phải giữ mức tiêu quota trong ngày ở chỗ
        # người dùng gói tháng chịu được, không phải chỗ vừa đủ chạy.
        # 40k token mỗi lượt — ĐO ĐƯỢC với lời nhắc hệ thống đầy đủ, không phải
        # ước. Lần ước đầu ra 29k và thiếu 38%; hằng số ở đây phải là số đo, nếu
        # không thì phép kiểm này canh một cái trần tưởng tượng.
        check(rieng["maxCallsPerDay"] * 40 <= 350,
              f"tiêu tối đa ~{rieng['maxCallsPerDay'] * 40}k token/ngày "
              f"({rieng['maxCallsPerDay']} lượt × 40k đo được)")

    print("\n[19] BẰNG CHỨNG TỪ LỆNH THẬT PHẢI TỚI ĐƯỢC CẦU DAO")
    from trader import chung_cat as CC4
    from trader.config import CONFIG as CFG4

    # 18 bài học từ lệnh thật đòi đổi chiến lược ở một chế độ, mà cầu dao chỉ
    # đọc nguồn `chay-lai` nên không có đường nào tới. Bằng chứng ĐẮT NHẤT trong
    # hệ không nối được vào cơ chế DUY NHẤT đổi được hành vi.
    _tf19 = CFG4["timeframes"]["primary"]

    def _dat(n, tien, doi, khung=_tf19):
        store.write_all(store.PHAT_HIEN, [{
            "ma": "that:R", "nguon": "so-that", "cheDo": "R", "khung": khung,
            "cau": "x", "mau": n, "doTin": "VỪA", "luc": "x",
            "so": {"tongTien": tien, "soDoiChienLuoc": doi}}])

    _dat(12, -300.0, 9)
    check(CC4.cau_dao("R|none", "R") is not None,
          "12 lệnh thật · tiền âm · 9/12 đòi đổi → NGẮT")

    # Ba cửa ngược lại. Thiếu bất kỳ cửa nào thì cầu dao sẽ ngắt vì lý do sai.
    _dat(6, -300.0, 6)
    check(CC4.cau_dao("R|none", "R") is None,
          "6 lệnh < ngưỡng 10 → không ngắt (chưa đủ mẫu)")
    _dat(12, +300.0, 12)
    check(CC4.cau_dao("R|none", "R") is None,
          "tiền DƯƠNG → không ngắt, dù hậu kiểm có càu nhàu")
    _dat(12, -300.0, 3)
    check(CC4.cau_dao("R|none", "R") is None,
          "chỉ 3/12 đòi đổi → không ngắt (một chuỗi xui không phải tật)")

    # Và khung vẫn phải khớp — lệnh của khung cũ không được chặn khung mới.
    _dat(12, -300.0, 9, khung="khung-khac")
    check(CC4.cau_dao("R|none", "R") is None,
          "bằng chứng của khung KHÁC → không ngắt")
    print("\n[22] KHO KỸ NĂNG KHÔNG CÒN LÀ CHỖ CHỨA MIỄN PHÍ")
    from trader.brain import load_skills as _ls22
    import importlib.util as _il22
    _sp22 = _il22.spec_from_file_location("bg22", str(ROOT / "scripts" / "ban-giao.py"))
    BG22 = _il22.module_from_spec(_sp22)
    _sp22.loader.exec_module(BG22)

    # Trước khi bộ não chạy thật, thêm kỹ năng là miễn phí. Từ khi nối CLI,
    # TOÀN BỘ kho đi vào lời nhắc hệ thống của MỌI lượt gọi. Ngưỡng này không
    # cấm thêm — nó bắt người thêm phải nhìn thấy cái giá.
    _sk22, _n22 = _ls22()
    check(len(_sk22) <= BG22.NGAN_SACH_KY_NANG,
          f"kho {len(_sk22):,} ký tự ≤ ngân sách {BG22.NGAN_SACH_KY_NANG:,} "
          f"(~{len(_sk22) / 3.2:,.0f} token mỗi lượt gọi, {_n22} kỹ năng)")

    print("\n[21] BÀN GIAO PHẢI ĐO TUỔI KHO ĐO, KHÔNG TIN LỜI BÁO CÁO")
    import datetime as _dt21
    import importlib.util as _il21
    _sp21 = _il21.spec_from_file_location("bg21", str(ROOT / "scripts" / "ban-giao.py"))
    BG21 = _il21.module_from_spec(_sp21)
    _sp21.loader.exec_module(BG21)

    # Nghi thức báo "đã khởi động ở luồng nền" là THÀNH CÔNG, nhưng luồng nền
    # chết cùng tiến trình mỗi lần runtime dựng lại. Đài quan sát đứng im 12
    # ngày trong khi nghi thức vẫn xanh. Nên đo TUỔI FILE, không tin báo cáo.
    _ten, _nhan, _ng = BG21.KHO_DO[0]
    _f21 = DATA_DIR / _ten
    _f21.parent.mkdir(parents=True, exist_ok=True)
    _f21.write_text("{}", encoding="utf-8")
    check(not any(_ten in x for x in BG21._kho_cu()),
          f"{_ten} vừa ghi → không báo cũ")
    _gia = _tg.time() - (_ng + 5) * 3600
    os.utime(_f21, (_gia, _gia))
    check(any(_ten in x for x in BG21._kho_cu()),
          f"{_ten} quá ngưỡng {_ng}h → báo cũ")

    # ── mtime tươi + dấu `luc` CŨ: đúng thế cờ mtime không thấy được ──
    #
    # Một lượt đo hỏng nửa chừng vẫn ghi file. mtime thành mới, số bên trong là
    # của hôm kia, và bàn giao báo "kho tươi". Đây là chỗ duy nhất hai thước
    # cho hai câu trả lời khác nhau — nên phải kiểm bằng chính thế cờ đó.
    _f21.write_text(json.dumps({
        "luc": (_dt21.datetime.now(_dt21.timezone.utc)
                - _dt21.timedelta(hours=_ng + 5)).isoformat(timespec="seconds")
    }), encoding="utf-8")   # mtime = BÂY GIỜ
    check(any(_ten in x for x in BG21._kho_cu()),
          "mtime tươi nhưng dấu `luc` quá ngưỡng → VẪN báo cũ")

    _f21.write_text(json.dumps({
        "luc": _dt21.datetime.now(_dt21.timezone.utc).isoformat(timespec="seconds")
    }), encoding="utf-8")
    _gia2 = _tg.time() - (_ng + 5) * 3600
    os.utime(_f21, (_gia2, _gia2))   # mtime CŨ, dấu mới
    check(not any(_ten in x for x in BG21._kho_cu()),
          "dấu `luc` mới thắng mtime cũ — cửa ngược lại")

    # Và phải NÓI RA khi rơi về mtime, chứ không lặng lẽ đo bằng thước yếu hơn.
    _f21.write_text("{}", encoding="utf-8")
    os.utime(_f21, (_gia2, _gia2))
    check(any("không đóng dấu" in x for x in BG21._kho_cu()),
          "kho không đóng dấu → báo cũ KÈM lời khai đang đo bằng mtime")
    _f21.unlink()
    check(any("CHƯA CÓ" in x and _ten in x for x in BG21._kho_cu()),
          f"{_ten} không tồn tại → báo CHƯA CÓ, khác với «cũ»")


    # ── Hai danh sách rời nhau phải khớp ──
    #
    # Nghi thức có bảng việc; bàn giao có bảng kho-phải-canh. Chúng viết tay,
    # rời nhau, và không gì nối. Thêm một việc mà quên khai bên kia thì kho ấy
    # đứng im vô hạn và KHÔNG AI KÊU — đã xảy ra với soát-lại-bài-học, 9 ngày.
    #
    # Không hợp nhất hai bảng: chúng trả lời hai câu hỏi khác nhau (chạy cái gì
    # / kho nào cũ). Nhưng bảng canh phải PHỦ bảng việc, và đó là phép kiểm.
    from trader import nghi_thuc as _NT19
    _canh = {t for t, _, _ in BG21.KHO_DO}
    _sinh = {x[3] for x in _NT19.VIEC if x[3]}
    _sot = sorted(_sinh - _canh)
    check(not _sot,
          "mọi kho nghi thức sinh ra đều được bàn giao canh tuổi"
          + (f" — KHÔNG AI CANH: {_sot}" if _sot else ""))
    check(bool({"kho-khong-ai-canh.json"} - _canh),
          "phép so BẮT ĐƯỢC một kho lạ — không tự chấm mù")

    # ── Kho phải tự đóng dấu LÚC ĐO ──
    #
    # Bàn giao đo tuổi kho bằng mtime. mtime nói "file bị chạm", không nói "số
    # bên trong được đo lại": một lượt hỏng nửa chừng vẫn chạm file, và kho
    # trông tươi trong khi nội dung là của hôm kia. Bốn trong sáu kho không có
    # trường nào nói lúc đo — do-khung, bo-pha, dau-nhieu-cho, chien-luoc.
    #
    # Canh ở tầng MÃ NGUỒN vì kho trong DATA_DIR tạm thì rỗng: mỗi script ghi
    # kho phải nhắc "luc" ngay trong câu lệnh ghi.
    _phai_dau = {
        "scripts/do-khung.py": "do-khung.json",
        "scripts/bo-pha.py": "bo-pha.json",
        "scripts/dau-chien-luoc.py": "dau-nhieu-cho.json",
        "trader/chien_luoc.py": "chien-luoc.json",
        "scripts/do-mau-gia.py": "mau-gia.json",
    }
    _khong = [f for f in _phai_dau
              if chr(34) + "luc" + chr(34) not in (ROOT / f).read_text(encoding="utf-8")]
    check(not _khong,
          "mọi script sinh kho đo đều đóng dấu lúc đo"
          + (f" — KHÔNG ĐÓNG DẤU: {_khong}" if _khong else ""))

    # Và khoá có mặt KHÔNG đủ. `do-mau-gia.py` từng ghi `"luc": None` cứng: phép
    # canh trên tìm thấy chữ "luc" nên báo xanh, mà giá trị thì vô dụng — bàn
    # giao rơi về mtime mà vẫn nghĩ mình đang đọc dấu. Khai một trường rồi để
    # trống còn tệ hơn không khai, vì nó làm cái canh im.
    _rong = [f for f in _phai_dau
             if chr(34) + "luc" + chr(34) + ": None"
             in (ROOT / f).read_text(encoding="utf-8")]
    check(not _rong,
          "không script nào ghi `luc: None` cứng"
          + (f" — DẤU RỖNG: {_rong}" if _rong else ""))

    # ── Đổi tên mã KHÔNG được báo là mất phép đo ──
    #
    # `that:TREND_UP` thành `that:khung?:TREND_UP` trong một commit, và bản bàn
    # giao báo 5 phát hiện BIẾN MẤT kèm câu "nguồn không còn đủ mẫu, hoặc vừa
    # hỏng" — lời giải thích sai về chuyện không xảy ra. Báo động sai dạy người
    # ta bỏ qua báo động, nên nó không rẻ hơn im lặng.
    _r = BG21._so({"phatHien": {"that:khung?:X": {}, "that-su-moi": {}}},
                  {"phatHien": {"that:X": {}, "mat-that": {}}})
    _t = " ".join(_r)
    check("ĐỔI TÊN MÃ" in _t, "trùng đuôi mã → ngờ là đổi tên, không kêu mất")
    check("that:X" in _t and "mat-that" in _t,
          "vẫn liệt kê ĐỦ cả hai — ngờ đổi tên không được nuốt mất cái thật")

    # Cửa ngược lại: mất thật thì KHÔNG được ngờ là đổi tên.
    _r2 = BG21._so({"phatHien": {"hoan-toan-khac": {}}},
                   {"phatHien": {"that:X": {}}})
    check("ĐỔI TÊN MÃ" not in " ".join(_r2),
          "không trùng đuôi nào → báo mất thẳng, không ngờ vẩn vơ")
    print("\n[20] HẬU KIỂM PHẢI NHƯỜNG TRẦN CHO LUẬN ĐIỂM")
    import trader.brain as _B20

    # Hai loại lượt gọi dùng CHUNG một trần. Một ngày nhiều lệnh đóng có thể
    # tiêu hết trần vào hậu kiểm, và bộ não không còn lượt nào để NGHĨ trước khi
    # vào lệnh tiếp theo. Hậu kiểm trễ một ngày vẫn nguyên giá trị (lệnh đã
    # đóng); luận điểm trễ thì mất hẳn cơ hội.
    _lop = next((getattr(_B20, n) for n in dir(_B20)
                 if isinstance(getattr(_B20, n), type)
                 and hasattr(getattr(_B20, n), "PHAN_CHO_HAU_KIEM")), None)
    check(_lop is not None, "tìm được lớp đồng hồ có PHAN_CHO_HAU_KIEM")
    if _lop:
        _o = _lop.__new__(_lop)
        _o.cfg = {"dailyBudgetUsd": 999.0, "maxCallsPerDay": 8}
        _o._day = lambda: _o._d

        _o._d = {"usd": 0.0, "calls": 3}
        check(_o.blocked("thesis") is None and _o.blocked("postmortem") is None,
              "3/8 lượt: cả hai loại đều được gọi")

        _o._d = {"usd": 0.0, "calls": 4}
        check(_o.blocked("thesis") is None and _o.blocked("postmortem") is not None,
              "4/8 lượt (nửa trần): hậu kiểm nhường, luận điểm vẫn chạy")

        _o._d = {"usd": 0.0, "calls": 8}
        check(_o.blocked("thesis") is not None,
              "8/8 lượt: luận điểm cũng dừng — trần cứng vẫn là trần cứng")
    print("\n[30] THIẾU KHOÁ LÀ LỖI NGƯỜI GỌI, KHÔNG PHẢI PHÁN QUYẾT")
    from trader import so_gia_thuyet as _G30

    # `_phan_quyet` biến mọi thứ không phải số thành KHÔNG_KẾT_LUẬN. Nên một
    # lời gọi gõ nhầm tên khoá cho ra "mẫu None < ngưỡng 30 — chưa đủ để nói
    # gì" — đọc y hệt một phép đo thật sự thiếu mẫu. Và vì sổ append-only từ
    # chối chốt lại, bản ghi sai ấy nằm lại VĨNH VIỄN.
    #
    # Đã xảy ra với `bung-nen-giu-duoc-o-cho-moi`: số đo có thật (−0,236R qua
    # 32 lệnh, đủ ngưỡng) nhưng ghi dưới tên khoá sai, và sổ ghi KHÔNG_KẾT_LUẬN.
    _ng30 = {"truong": "x", "toanTu": ">", "giaTri": 0, "mauToiThieu": 30}
    _G30.khai("t30a", "h", "d", "c", dict(_ng30))
    _r30 = _G30.chot("t30a", {"x": -0.2, "mauToiThieu": 32})
    check(_r30.get("ok") is False, "thiếu khoá «mau» → TỪ CHỐI, không phán quyết")
    check("mauToiThieu" in (_r30.get("viSao") or ""),
          "và kể ra những khoá ĐÃ nhận, để thấy ngay mình gõ nhầm gì")

    # Cửa ngược lại 1: có «mau» mà nhỏ vẫn phải là KHÔNG_KẾT_LUẬN — đó là kết
    # quả thật, không phải lỗi gọi.
    check(_G30.chot("t30a", {"x": -0.2, "mau": 5})["phanQuyet"] == "KHÔNG_KẾT_LUẬN",
          "có «mau» nhưng nhỏ → KHÔNG_KẾT_LUẬN như cũ")

    # Cửa ngược lại 2: đủ mẫu thì vẫn phán quyết bình thường, cả hai chiều.
    _G30.khai("t30b", "h", "d", "c", dict(_ng30))
    check(_G30.chot("t30b", {"x": -0.2, "mau": 32})["phanQuyet"] == "BÁC_BỎ",
          "đủ mẫu, không đạt ngưỡng → BÁC_BỎ")
    _G30.khai("t30c", "h", "d", "c", dict(_ng30))
    check(_G30.chot("t30c", {"x": 0.4, "mau": 32})["phanQuyet"] == "XÁC_NHẬN",
          "đủ mẫu, đạt ngưỡng → XÁC_NHẬN")
    print("\n[29] IMPORT TRONG HÀM KHÔNG CHE CHO HÀM KHÁC")
    import ast as _ast29

    # `dau-chien-luoc.py` có `import datetime as _dt` bên trong `_nap_cho`. Một
    # bản vá thêm chỗ dùng `_dt` trong `dau_nhieu_cho` — hàm khác, không thấy
    # cái import kia. Python biên dịch sạch, và NameError chỉ nổ ở dòng CUỐI
    # của một lượt đo 40 phút, sau khi mọi con số đã tính xong và trước khi kịp
    # ghi ra đĩa. Cả lượt đo mất trắng.
    #
    # Chỉ soi bí danh dạng `import X as _y` — quy ước ở đây cho import cục bộ.
    # Đủ hẹp để không báo bừa, và đúng chỗ đã cắn.
    def _khai_trong(node):
        return {a.asname for n in _ast29.walk(node)
                if isinstance(n, (_ast29.Import, _ast29.ImportFrom))
                for a in n.names if a.asname and a.asname.startswith("_")}

    _thieu = []
    for _f29 in sorted(list((ROOT / "trader").glob("*.py"))
                       + list((ROOT / "scripts").glob("*.py"))):
        try:
            _cay29 = _ast29.parse(_f29.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        _mod = _khai_trong(_ast29.Module(body=[n for n in _cay29.body
                                               if isinstance(n, (_ast29.Import,
                                                                 _ast29.ImportFrom))],
                                         type_ignores=[]))
        # Bí danh nào từng được khai CỤC BỘ ở file này thì mới đáng soi: nó là
        # thứ dễ tưởng đã có mà thật ra chỉ có trong một hàm.
        _cuc_bo = set()
        _ham = [n for n in _ast29.walk(_cay29)
                if isinstance(n, (_ast29.FunctionDef, _ast29.AsyncFunctionDef))]
        for _h in _ham:
            _cuc_bo |= _khai_trong(_h)
        # Hàm LỒNG thấy được import của hàm bao ngoài qua bao đóng. Bỏ qua chuyện
        # đó là báo nhầm ngay lần chạy đầu — và một phép canh hay báo nhầm sẽ bị
        # tắt, rồi lỗi thật đi qua cửa đang mở.
        _cha = {}
        for _n29 in _ast29.walk(_cay29):
            for _con in _ast29.iter_child_nodes(_n29):
                _cha[_con] = _n29

        def _khai_ke_thua(h):
            ra, cur = _khai_trong(h), _cha.get(h)
            while cur is not None:
                if isinstance(cur, (_ast29.FunctionDef, _ast29.AsyncFunctionDef)):
                    ra = ra | _khai_trong(cur)
                cur = _cha.get(cur)
            return ra

        for _h in _ham:
            _co = _khai_ke_thua(_h) | _mod
            _dung = {n.id for n in _ast29.walk(_h) if isinstance(n, _ast29.Name)}
            for _t in sorted((_dung & _cuc_bo) - _co):
                _thieu.append(f"{_f29.name}:{_h.name} dùng {_t}")
    check(not _thieu,
          f"không hàm nào dùng bí danh import của hàm KHÁC ({len(_ham)} hàm ở file cuối)"
          + (f" — THIẾU: {_thieu}" if _thieu else ""))

    # Cửa ngược lại: phép quét phải BẮT được một file dựng sẵn có đúng lỗi đó.
    _gia29 = _ast29.parse(NL.join([
        "def a():",
        "    import datetime as _dt",
        "    return _dt.datetime.now()",
        "def b():",
        "    return _dt.datetime.now()",
    ]))
    _hs = [n for n in _ast29.walk(_gia29) if isinstance(n, _ast29.FunctionDef)]
    _cb = set().union(*[_khai_trong(h) for h in _hs])
    _bat29 = [h.name for h in _hs
              if ({n.id for n in _ast29.walk(h) if isinstance(n, _ast29.Name)}
                  & _cb) - _khai_trong(h)]
    check(_bat29 == ["b"], f"quét BẮT được hàm b() dùng _dt của a() — được {_bat29}")
    print("\n[28] LỆCH CŨ KHÁC LỆCH ĐANG XẢY RA")
    from trader import chung_cat as C28

    # cv 0,357 trên 40 lệnh — nhưng gần hết nằm ở 3 lệnh ngày 19/08 có cùng
    # riskPct 0,5 mà số tiền gấp 2,5×: đúng lỗi MẪU SỐ đã sửa từ lâu. 20 lệnh
    # gần nhất có cv 0,03. Câu cũ nói y hệt cho cả hai trường hợp, mà việc phải
    # làm thì ngược nhau: lệch CŨ ⇒ R vẫn đọc được cho phần gần đây; lệch ĐANG
    # XẢY RA ⇒ có một chỗ hỏng phải tìm ngay.
    def _lam28(cu_lech, gan_lech):
        ds = []
        for i in range(20):
            ds.append({"id": f"c{i}", "openedAt": f"2026-08-0{i % 9 + 1}T00:00:00",
                       "closedAt": "x", "status": "CLOSED",
                       "regimeAtEntry": "Z", "khung": "4h",
                       "riskAmount": (200.0 if (cu_lech and i < 5) else 50.0),
                       "pnl": -1.0, "rMultiple": -1.0, "riskPct": 0.5})
        for i in range(20):
            ds.append({"id": f"g{i}", "openedAt": f"2026-08-2{i % 9}T00:00:00",
                       "closedAt": "x", "status": "CLOSED",
                       "regimeAtEntry": "Z", "khung": "4h",
                       "riskAmount": (200.0 if (gan_lech and i % 2) else 50.0),
                       "pnl": -1.0, "rMultiple": -1.0, "riskPct": 0.5})
        (DATA_DIR / store.TRADES).write_text(
            "".join(_json.dumps(x) + NL for x in ds), encoding="utf-8")
        return next((x["cau"] for x in C28._tu_so_that([]) if x["ma"] == "rui-ro-deu"), "")

    _c = _lam28(cu_lech=True, gan_lech=False)
    check("phần CŨ của sổ" in _c, "lệch dồn ở phần cũ → nói rõ là CŨ")
    check("ĐANG XẢY RA" not in _c, "và KHÔNG kêu là đang xảy ra")

    _c = _lam28(cu_lech=True, gan_lech=True)
    check("ĐANG XẢY RA" in _c, "lệch cả ở phần gần nhất → kêu ĐANG XẢY RA")
    check("phần CŨ của sổ" not in _c, "và KHÔNG trấn an bằng câu «lệch cũ»")

    # Rủi ro đều thì cả hai câu đều phải im.
    _c = _lam28(cu_lech=False, gan_lech=False)
    check("KHÔNG đều" not in _c, "rủi ro đều → không câu cảnh báo nào")


    # ── Cắt danh sách phải giữ cái MỚI, không phải cái đầu sổ ──
    #
    # `bac[:3]` giữ ba bác-bỏ CŨ NHẤT và vứt cái vừa đo xong. Càng học nhiều
    # thì bài học mới càng không tới được bộ não — một cửa tự đóng lại theo
    # thời gian, và không có gì báo vì phát hiện vẫn đủ số.
    from trader import so_gia_thuyet as _Gc
    for _i in range(5):
        _Gc.khai(f"bb{_i}", "h", "d", "c",
                 {"truong": "x", "toanTu": ">", "giaTri": 0, "mauToiThieu": 1})
        _Gc.chot(f"bb{_i}", {"x": -1, "mau": 9})
    _ma = [x["ma"] for x in C28._tu_gia_thuyet([]) if x["ma"].startswith("bac-bo:")]
    check("bac-bo:bb4" in _ma, f"bác bỏ MỚI NHẤT vào được prompt — có {_ma}")
    check("bac-bo:bb0" not in _ma, "và cái cũ nhất nhường chỗ, không chiếm mãi")
    # ── Mẫu giá: số CHỢ phải vào câu ──
    #
    # "45.000 nến khung 4h" và "45.000 nến khung 4h trên 15 chợ độc lập" là hai
    # mức bằng chứng khác hẳn: một chợ dài chỉ là một quan sát kéo dài, còn 15
    # chợ độc lập là thứ khớp trội khó bịa. Thiếu con số ấy thì đúng cái làm
    # phép đo đáng tin lại là thứ không được nói. Và kho đo CŨ chưa có trường
    # `cho` thì phải khai "KHÔNG RÕ", không được im.
    def _mg28(cho):
        d = {"khung": "4h", "nen": 100, "toiThieu": 15,
             "mau": [{"ten": "M", "so": 20, "kyVongR": -0.1, "duMau": True,
                      "tyLeThang": 40, "mfeTrungVi": 0.5, "rrTrungBinh": 1.2,
                      "chamDich": 30, "dinhStop": 50, "nenTrungBinh": 5,
                      "coDinh": {}, "loai": "x"}]}
        if cho is not None:
            d["cho"] = cho
        (DATA_DIR / "mau-gia.json").write_text(_json.dumps(d), encoding="utf-8")
        return next(x["cau"] for x in C28._tu_mau_gia([]) if x["ma"] == "mau-gia-tong")

    check("3 chợ độc lập" in _mg28(["A:4h", "B:4h", "C:4h"]),
          "nhiều chợ → nói rõ mấy chợ ĐỘC LẬP")
    check("của A:4h" in _mg28(["A:4h"]),
          "một chợ → nêu đích danh chợ đó, không nói «độc lập»")
    check("KHÔNG RÕ" in _mg28(None),
          "kho đo cũ chưa khai chợ → nói KHÔNG RÕ, không im lặng")
    print("\n[27] CON SỐ ĐẸP CỦA MỘT CHỢ KHÔNG ĐƯỢC ĐỨNG MỘT MÌNH")
    import importlib.util as _il27
    _sp27 = _il27.spec_from_file_location("bg27", str(ROOT / "scripts" / "ban-giao.py"))
    BG27 = _il27.module_from_spec(_sp27); _sp27.loader.exec_module(BG27)

    # Dòng tiêu đề ghi "champion MOCK_RULES_V1 (0.032R ngoài mẫu)" — con số của
    # MỘT chợ, đúng cái chợ mọi thứ ở đây từng được đo lên. Gộp 8 chợ thì cùng
    # bộ luật ấy −0,047R qua 193 lệnh. Và không có đường nào gỡ champion xuống:
    # `phan_quyet` là cửa DUYỆT, chặn kẻ thách đấu kém chứ không chặn kẻ đang ngồi.
    def _dat27(kv_mot, kv_gop):
        (DATA_DIR / "chien-luoc.json").write_text(_json.dumps(
            {"champion": {"ma": "X", "ketQua": {"kyVongR": kv_mot, "cho": "C:4h"}}}
        ), encoding="utf-8")
        store.write_all(store.PHAT_HIEN, [] if kv_gop is None else [
            {"ma": "cho:X", "nguon": "nhieu-cho", "cau": "c", "mau": 193,
             "doTin": "CAO", "so": {"kyVongR": kv_gop, "duong": 2, "soCho": 8},
             "cheDo": None, "khung": None, "luc": "x"}])

    _dat27(0.032, -0.047)
    _t27 = " ".join(BG27._champion_bi_bac_bo())
    check("-0.047" in _t27 and "193" in _t27,
          "champion dương ở chợ nhà, âm khi gộp → NÓI RA con số gộp")
    check("gỡ champion xuống" in _t27,
          "và nói rõ không có đường gỡ xuống — cửa duyệt chỉ chặn kẻ vào")

    # Cửa ngược lại 1: gộp lại vẫn dương thì im. Kêu khi không có gì để kêu là
    # dạy người đọc bỏ qua mục này.
    _dat27(0.032, 0.05)
    check(not BG27._champion_bi_bac_bo(), "gộp lại vẫn dương → mục IM")

    # Cửa ngược lại 2: chưa có phép đo nhiều chợ thì không được đoán bừa.
    _dat27(0.032, None)
    check(not BG27._champion_bi_bac_bo(),
          "chưa có phát hiện nhiều chợ → im, không suy diễn")

    # Champion âm ở CẢ HAI thước vẫn phải kêu — đó là ca nặng nhất.
    _dat27(-0.2, -0.3)
    check(bool(BG27._champion_bi_bac_bo()), "âm ở cả hai thước → vẫn kêu")
    print("\n[26] SETUP THƯA: GỘP CHỢ THAY VÌ VỨT THẦM")
    from trader import chung_cat as C26

    # Cổng cũ đòi MỖI chợ ≥20 lệnh ngoài mẫu. Với một setup hiếm điều đó không
    # bao giờ xảy ra dù dữ liệu về bao nhiêu: MOCK_BUNG_NEN_V1 có 45 lệnh trải
    # 8 chợ, nhiều nhất một chợ là 8 — nên nó nằm mãi ở "chưa đủ dữ liệu", và
    # dòng đó đọc giống hệt lúc thật sự chưa có gì. Bộ máy vứt bằng chứng tốt
    # nhất của chính nó, một cách im lặng.
    _mt, _sn, _gp = (C26.MAU_TOI_THIEU["nhieu-cho"],
                     C26.MAU_TOI_THIEU["nhieu-cho-san"],
                     C26.MAU_TOI_THIEU["nhieu-cho-gop"])

    def _dat26(ds):
        (DATA_DIR / "dau-nhieu-cho.json").write_text(_json.dumps({
            "cho": [f"C{i}:4h" for i in range(len(ds))],
            "ket": {"X": {f"C{i}:4h": {"kyVongR": r, "so": n}
                          for i, (r, n) in enumerate(ds)}},
        }), encoding="utf-8")

    # Thưa nhưng cộng lại đủ → PHẢI nói được, dưới mã cho-gop.
    _dat26([(0.2, _gp // 4 + 1)] * 5)
    _r26 = C26._tu_nhieu_cho([])
    check(any(x["ma"] == "cho-gop:X" for x in _r26),
          f"5 chợ nhỏ cộng lại > {_gp} lệnh → có phát hiện GỘP")
    check(all(x["ma"] != "cho:X" for x in _r26),
          "và KHÔNG giả vờ là phát hiện theo-chợ — hai loại câu khác nhau")

    # Cửa ngược lại 1: cộng lại vẫn không đủ → vẫn phải im, và phải NÓI vì sao.
    _bo26 = []
    _dat26([(0.2, _sn)] * 2)
    check(not C26._tu_nhieu_cho(_bo26), "gộp lại vẫn dưới ngưỡng → không phát hiện")
    check(any("gộp lại cũng chỉ" in x["viSao"] for x in _bo26),
          "và nói rõ đã thử gộp rồi mới bỏ, không im lặng")

    # Cửa ngược lại 2: chợ quá nhỏ không được kéo vào cho đủ số.
    _dat26([(9.0, _sn - 1)] * 50)
    check(not C26._tu_nhieu_cho([]),
          f"50 chợ mỗi chợ {_sn - 1} lệnh → vẫn im; gộp nhiễu vẫn là nhiễu")

    # Cửa ngược lại 3: có chợ đủ mẫu riêng thì đi đường CŨ, không đổi mã.
    _dat26([(0.1, _mt), (0.1, _mt)])
    _r26b = C26._tu_nhieu_cho([])
    check(any(x["ma"] == "cho:X" for x in _r26b) and
          all(x["ma"] != "cho-gop:X" for x in _r26b),
          "chợ đủ mẫu riêng → giữ mã cũ `cho:`, nhánh gộp không cướp việc")

    # Kỳ vọng GỘP phải theo TRỌNG SỐ số lệnh, không phải trung bình đầu chợ:
    # một chợ 3 lệnh không được nặng bằng một chợ 26 lệnh.
    _dat26([(1.0, _mt), (-1.0, _mt * 3)])
    _kv = next(x["so"]["kyVongR"] for x in C26._tu_nhieu_cho([]) if x["ma"] == "cho:X")
    check(abs(_kv - (-0.5)) < 1e-9,
          f"gộp theo trọng số lệnh: (+1×n, -1×3n) → -0.5R, được {_kv}")
    print("\n[25] LẶP LẠI KHÔNG ĐƯỢC ĐỌC NHƯ BẰNG CHỨNG CHỒNG CHẤT")
    from trader.journal import _gop_trung as _gt25, _gon as _gn25

    # `lessonsForThisRegime` đưa cho bộ não 9 mục mà chỉ là 3 câu. Sáu mục kia
    # không thêm chữ nào — cùng một câu đúc lại ở những lệnh khác nhau của cùng
    # chế độ. Hại nặng hơn chuyện tốn token: thấy một câu 9 lần thì nó NẶNG hơn
    # thấy một lần, dù vẫn là một quan sát. Cân sai, và sai theo hướng làm bộ
    # não tự tin hơn mức dữ liệu cho phép.
    _ds25 = ([{"lesson": "A", "rMultiple": -1}] * 4
             + [{"lesson": "B", "rMultiple": 2}] * 2
             + [{"lesson": "C", "rMultiple": 0}])
    _ra25 = _gt25(_ds25)
    check(len(_ra25) == 3, f"7 mục · 3 câu → còn {len(_ra25)} mục")
    check(sorted(x["_lan"] for x in _ra25) == [1, 2, 4],
          "số lần được ĐẾM chứ không bị vứt (1·2·4)")

    # Cửa ngược lại: câu khác nhau thì KHÔNG được gộp. Thiếu phép này thì một
    # lỗi gộp quá tay sẽ nuốt mất bài học thật mà bảng vẫn gọn đẹp.
    _kh25 = _gt25([{"lesson": f"câu {i}"} for i in range(5)])
    check(len(_kh25) == 5, "5 câu KHÁC nhau → giữ nguyên 5, không gộp nhầm")

    # Và bài học không có câu thì không được gộp vào nhau thành một.
    _rong = _gt25([{"lesson": "", "rMultiple": 1}, {"lesson": None, "rMultiple": 2}])
    check(len(_rong) == 2, "hai bài học RỖNG câu vẫn là hai, không nhập một")

    check(_gn25({"lesson": "A", "_lan": 1}).get("gapMayLan") is None,
          "gặp đúng 1 lần → KHÔNG hiện gapMayLan, tránh nhiễu lời nhắc")
    check(_gn25({"lesson": "A", "_lan": 4}).get("gapMayLan") == 4,
          "gặp 4 lần → hiện gapMayLan=4")
    print("\n[24] ĐỨNG NGOÀI LÂU PHẢI KÊU LÊN — CẢ CỬA NGƯỢC LẠI")
    import importlib.util as _il24
    _sp24 = _il24.spec_from_file_location("bg24", str(ROOT / "scripts" / "ban-giao.py"))
    BG24 = _il24.module_from_spec(_sp24)
    _sp24.loader.exec_module(BG24)

    # Bộ não ra NO_TRADE vì "chế độ này kỳ vọng âm" là quyết định ĐÚNG. Nhưng
    # đúng mãi thì hệ đứng ở một trạng thái vô sinh: không vào lệnh ⇒ không có
    # dữ liệu mới ⇒ bằng chứng âm đứng nguyên ⇒ không vào lệnh. Bàn giao phải
    # phân biệt "đang chờ thời" với "đã kẹt".
    #
    # Canh CẢ HAI cửa. Một luật có ngưỡng mà chỉ kiểm cửa thuận thì nó có thể
    # đang kêu SUỐT (vô dụng) hoặc CHẲNG BAO GIỜ kêu (chết lặng) — và cả hai
    # đều đọc giống "chưa từng thấy vấn đề".
    _lm = BG24.DUNG_IM_LIEN_TIEP
    _nt = lambda: {"action": "NO_TRADE", "reason_codes": ["X"]}

    # `store.write_all` TỪ CHỐI sổ luận điểm — nó append-only, và chốt đó đúng.
    # Ở đây phải dựng từng thế cờ nên ghi thẳng file. An toàn vì DATA_DIR của
    # phép kiểm là thư mục tạm (đặt ở đầu file, GHI ĐÈ chứ không setdefault —
    # chính chỗ đó từng cho phép kiểm ghi vào sổ THẬT hai lần).
    def _dat24(ds):
        f = DATA_DIR / store.THESES
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("".join(_json.dumps(x) + NL for x in ds), encoding="utf-8")

    _dat24([_nt() for _ in range(_lm - 1)])
    check(not BG24._dung_im(), f"{_lm - 1} lượt (dưới ngưỡng {_lm}) → IM")

    _dat24([_nt() for _ in range(_lm)])
    check(bool(BG24._dung_im()), f"{_lm} lượt (chạm ngưỡng) → KÊU")

    # Một lệnh thật xen vào là chuỗi đứt — bot vẫn đang giao dịch, không kẹt.
    _dat24([_nt() for _ in range(_lm)] + [{"action": "LONG"}]
            + [_nt() for _ in range(3)])
    check(not BG24._dung_im(),
          "một lệnh LONG xen vào → chuỗi đứt, không báo kẹt")

    _dat24([])
    check(not BG24._dung_im(), "sổ rỗng → im, không chia cho không")

    # ── Giả thuyết kẹt cùng bot: cùng thế bí, nhìn từ sổ giả thuyết ──
    #
    # Hai giả thuyết đang mở đo trên LỆNH THẬT. Bot đứng ngoài ⇒ không lệnh mới
    # ⇒ không chốt được. Không cần biết giả thuyết đo GÌ để nói điều đó: đếm
    # lệnh thật mở sau lúc khai là đủ, nên không phải đoán.
    from trader import so_gia_thuyet as _G24
    # Kiểm giá trị TRẢ VỀ của khai(), đừng chỉ nhìn đầu ra cuối. Bản đầu gọi sai
    # tên khoá ngưỡng («mau» thay vì «mauToiThieu»); khai() từ chối đúng, trả
    # {"ok": false}, và phép kiểm không thấy — nó chỉ thấy "không báo kẹt", đọc
    # y hệt "luật hỏng". Một lời gọi hỏng phải làm phép kiểm ĐỎ ngay tại chỗ gọi.
    _k24 = _G24.khai("gt-ket", "hỏi", "đoán", "cách đo",
                     {"truong": "kyVongR", "toanTu": ">", "giaTri": 0,
                      "mauToiThieu": 10})
    check(_k24.get("ok"), f"khai() nhận bản khai: {_k24.get('viSao') or 'ok'}")
    check(any("gt-ket" in x for x in BG24._gia_thuyet_ket()),
          "giả thuyết mở, 0 lệnh thật kể từ lúc khai → báo kẹt")

    # Cửa ngược lại: có lệnh thật mở SAU lúc khai thì không kẹt vì lý do này.
    _sau = _dt21.datetime.now(_dt21.timezone.utc) + _dt21.timedelta(hours=1)
    (DATA_DIR / store.TRADES).write_text(
        _json.dumps({"openedAt": _sau.isoformat(timespec="seconds")}) + NL,
        encoding="utf-8")
    check(not any("gt-ket" in x for x in BG24._gia_thuyet_ket()),
          "có lệnh thật mở sau lúc khai → KHÔNG báo kẹt")
    (DATA_DIR / store.TRADES).write_text("", encoding="utf-8")

    # Và giả thuyết ĐÃ CHỐT không được đếm là kẹt.
    _c24 = _G24.chot("gt-ket", {"kyVongR": 1, "mauToiThieu": 10})
    check(_c24.get("ok"), f"chot() nhận bản chốt: {_c24.get('viSao') or 'ok'}")
    check(not any("gt-ket" in x for x in BG24._gia_thuyet_ket()),
          "giả thuyết đã chốt → không còn là chỗ kẹt")

    # ── Ba chỗ cùng nói một ngưỡng phải cùng một số ──
    #
    # `web/app.js`, `Runtime` và `ban-giao` đều quyết định "bao nhiêu lượt đứng
    # ngoài thì gọi là kẹt". Ba bản sao viết tay ở ba ngôn ngữ; lệch nhau thì
    # buồng lái nói "bình thường" trong khi bản bàn giao nói "kẹt", và người
    # đọc tin cái nào tuỳ chỗ họ nhìn.
    import re as _re24
    _lay = lambda f, pat: int(_re24.search(pat, (ROOT / f).read_text(encoding="utf-8")).group(1))
    _nguong = {
        "web/app.js": _lay("web/app.js", r"const DUNG_IM = (\d+)"),
        "trader/loop.py": _lay("trader/loop.py", r"DUNG_IM_LIEN_TIEP = (\d+)"),
        "scripts/ban-giao.py": _lay("scripts/ban-giao.py", r"DUNG_IM_LIEN_TIEP = (\d+)"),
    }
    check(len(set(_nguong.values())) == 1,
          f"ngưỡng đứng-im khớp ở cả ba chỗ: {_nguong}")
    print("\n[23] MỌI PHÉP ĐO PHẢI TỰ KHAI CHỢ CỦA NÓ")
    from trader import chung_cat as CC23

    # Bốn lần cùng một lỗi trong hệ này: cầu dao chặn khung 4h bằng bằng chứng
    # 1h · bài học chạy lại không ghi khung · bảng mẫu giá ghi cứng "1h" · sổ
    # chiến lược ghi "+0,032R qua 26 lệnh" mà không nói của chợ nào.
    #
    # Mỗi lần đều sửa riêng một chỗ. Phép kiểm này là chỗ CHUNG: phát hiện nào
    # gắn với một chế độ thị trường thì phải khai khung nó được đo trên, nếu
    # không nó sẽ được đọc như thể đúng cho mọi khung.
    store.write_all(store.PHAT_HIEN, [
        {"ma": "co-khung", "nguon": "chay-lai", "cheDo": "R",
         "khung": CONFIG["timeframes"]["primary"],
         "cau": "x", "mau": 30, "doTin": "CAO", "so": {"kyVongR": -0.5}, "luc": "x"},
        {"ma": "thieu-khung", "nguon": "chay-lai", "cheDo": "R",
         "cau": "y", "mau": 30, "doTin": "CAO", "so": {}, "luc": "x"},
        {"ma": "khong-che-do", "nguon": "so-that", "cheDo": None,
         "cau": "z", "mau": 30, "doTin": "CAO", "so": {}, "luc": "x"},
    ])
    _ds23 = CC23.doc("R", "R", gioi_han=20)
    _theo = {p["ma"]: p for p in _ds23}

    check("thieu-khung" in _theo,
          "phát hiện thiếu khung vẫn VÀO prompt — bỏ hẳn là mất bối cảnh")
    check(CC23.cau_dao("R", "R") is not None,
          "phát hiện CÓ khung khớp → cầu dao ngắt được")

    # Và cửa quan trọng nhất: bỏ cái có khung đi thì cầu dao phải im, chứ không
    # được rơi sang dùng cái thiếu khung.
    store.write_all(store.PHAT_HIEN, [p for p in store.read_all(store.PHAT_HIEN)
                                      if p["ma"] != "co-khung"])
    check(CC23.cau_dao("R", "R") is None,
          "chỉ còn phát hiện THIẾU khung → cầu dao KHÔNG ngắt")

    # Kho đo trên đĩa: cái nào gắn chế độ thì phải có khung.
    CC23.chung_cat()
    # Không ép PHẢI có khung: bài học cũ chưa ghi khung vẫn đáng giữ làm bối
    # cảnh. Bất biến THẬT là — không rõ thì phải NÓI RA, chứ không im lặng trôi
    # qua như thể đã biết. Mã định danh mang "khung?" chính là chỗ nói ra đó.
    _im = [p["ma"] for p in store.read_all(store.PHAT_HIEN)
           if p.get("cheDo") and not p.get("khung") and "khung?" not in p["ma"]]
    check(not _im,
          "phát hiện không rõ khung đều tự khai trong mã định danh"
          + (f" — IM LẶNG: {_im}" if _im else ""))

    # ── Và cửa mà phép kiểm trên KHÔNG canh được ──
    #
    # Bốn dòng vừa rồi chạy trên DATA_DIR tạm, nơi không nguồn nào đủ mẫu để
    # sinh ra phát hiện gắn chế độ. Nên `_im` rỗng, và nó xanh vì luật CHƯA
    # TỪNG CHẠY chứ không vì luật đúng. Kho THẬT lúc đó đang có 5 vi phạm:
    # that:TREND_UP và bốn chuyen-gia:*. Đúng dạng đã ghi trong sổ — "ngưỡng đo
    # trên tập trôi nên luật không bao giờ kích hoạt, và «chưa từng thấy vấn
    # đề» đọc giống hệt «không có vấn đề»".
    #
    # Nên canh thêm ở tầng MÃ NGUỒN, nơi không phụ thuộc dữ liệu: hễ một phát
    # hiện khai `che_do=` thì mã định danh của nó phải nhắc tới khung. Cách này
    # bắt được cả nguồn CHƯA AI VIẾT, ngay lúc nó được viết.
    import ast as _ast23
    _src = (ROOT / "trader" / "chung_cat.py").read_text(encoding="utf-8")
    _cay = _ast23.parse(_src)
    _hong = []
    for _n in _ast23.walk(_cay):
        if not (isinstance(_n, _ast23.Call)
                and getattr(_n.func, "id", "") == "_pd"
                and any(k.arg == "che_do" for k in _n.keywords)
                and _n.args):
            continue
        if "khung" not in _ast23.get_source_segment(_src, _n.args[0]):
            _hong.append(f"dòng {_n.lineno}")

    # ── Sổ TRỘN: lệnh cũ không khai khung + lệnh mới có khai ──
    #
    # Thế cờ này chưa xảy ra nhưng sắp: hai bên môi giới đã ghi `khung` lúc mở
    # lệnh, còn 40 lệnh trong sổ thật thì không có trường đó. Lệnh thật KẾ TIẾP
    # là đủ để tập khung còn đúng {"4h"} — nếu chỗ đọc lọc bỏ lệnh thiếu khung.
    # Khi ấy câu vẫn đọc "41 lệnh" mà nhãn là 4h, và 40 trong số đó không ai
    # biết đo trên khung nào.
    _tr23 = [
        {"regimeAtEntry": "Z", "closedAt": "x"},          # cũ, không khung
        {"regimeAtEntry": "Z", "closedAt": "x"},
        {"regimeAtEntry": "Z", "closedAt": "x", "khung": "4h"},   # mới
    ]
    _g23 = lambda ds: (lambda k: next(iter(k)) if len(k) == 1 and None not in k
                       else None)({t.get("khung") for t in ds})
    check(_g23(_tr23) is None,
          "sổ trộn (2 lệnh không khung + 1 lệnh 4h) → khung KHÔNG rõ, không dán 4h")
    check(_g23([t for t in _tr23 if t.get("khung")]) == "4h",
          "sổ chỉ toàn lệnh 4h → khai đúng 4h (cửa ngược lại)")

    # Và chỗ đọc THẬT phải dùng đúng phép ấy, không phải một bản sao trong test.
    _seg = (ROOT / "trader" / "chung_cat.py").read_text(encoding="utf-8")
    check("None not in khung_ds" in _seg,
          "chung_cat dùng phép «None trong tập ⇒ không rõ», không lọc bỏ lệnh")
    check(not _hong,
          "mọi _pd(che_do=…) dựng mã có nhắc khung"
          + (f" — THIẾU: {_hong}" if _hong else ""))

    # Cửa ngược lại: phép kiểm trên phải BẮT ĐƯỢC một nguồn hỏng. Không có nó
    # thì một lỗi đánh máy trong chính đoạn quét cũng đọc là "sạch".
    _gia = _ast23.parse('_pd(f"x:{che_do}", "n", "c", 1, che_do=che_do)')
    _bat = [n for n in _ast23.walk(_gia)
            if isinstance(n, _ast23.Call) and getattr(n.func, "id", "") == "_pd"
            and any(k.arg == "che_do" for k in n.keywords)]
    check(bool(_bat) and "khung" not in _ast23.dump(_bat[0].args[0]),
          "phép quét BẮT ĐƯỢC nguồn hỏng dựng sẵn — không tự chấm mù")
    broker.reset()
    print("\n" + "=" * 62)
    if FAILS:
        print(f"  {len(FAILS)} PHÉP KIỂM SAI:")
        for x in FAILS:
            print("   - " + x)
        return 1
    print("  TẤT CẢ ĐỀU ĐÚNG — vòng chạy kín từ nến tới bài học.")
    print("=" * 62)
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
