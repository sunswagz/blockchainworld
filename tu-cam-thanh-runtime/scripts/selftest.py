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
import json
import os
import sys
import tempfile
from pathlib import Path

# PHẢI đặt trước khi import trader.* — `config.py` đọc biến này lúc nạp module,
# đặt sau thì DATA_DIR đã trỏ vào thư mục thật rồi.
os.environ.setdefault("TCT_DATA_DIR", tempfile.mkdtemp(prefix="tct-selftest-"))

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx  # noqa: E402

from trader.brain import mock_thesis  # noqa: E402
from trader.broker import PaperBroker  # noqa: E402
from trader.config import CONFIG  # noqa: E402
from trader.data import get_market_data  # noqa: E402
from trader.features import build_market_state  # noqa: E402
from trader.regime import classify  # noqa: E402
from trader.risk import RiskEngine  # noqa: E402

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
        n = dv["position"]["notional"]
        check(n <= 10000.0, f"notional {n:,.0f} ≤ tiền mua được 10.000 (vốn 73.000)")
        check(dv["position"]["notionalCapped"], "có đánh dấu là đã bị cắt trần")
        check(dv["position"]["riskAmount"] < 73000.0 * 0.005,
              f"rủi ro thật ${dv['position']['riskAmount']} < 0,5% vốn — cắt trần thì rủi ro giảm theo")

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
