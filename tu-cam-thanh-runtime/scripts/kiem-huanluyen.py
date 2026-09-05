"""Kiểm cỗ máy chạy lại lịch sử.

    python scripts/kiem-huanluyen.py

Backtest là thứ dễ nói dối nhất trong hệ thống, và nó nói dối theo một kiểu đặc
biệt khó chịu: **không bao giờ đổ, chỉ trả về một con số đẹp hơn sự thật**. Mỗi
phép kiểm dưới đây gác đúng một đường nói dối, và tất cả đều là đường đã có
người đi qua chứ không phải giả thuyết.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))

# KHÔNG BAO GIỜ chạm sổ thật. GHI ĐÈ, không `setdefault`: một dòng
# `export TCT_DATA_DIR=` trong shell là đủ để setdefault không làm gì, và
# chuyện đó đã sập BA lần ở repo này — lần nặng nhất là bộ kiểm cửa duyệt đưa
# một champion GIẢ lên ngôi trong sổ chiến lược thật.
import os
from _tam_tu_don import tam_moi

os.environ["TCT_DATA_DIR"] = tam_moi("tct-kiem-")

from trader import huanluyen as HL  # noqa: E402
from trader.config import CONFIG  # noqa: E402

sai = 0


def ok(m: str) -> None:
    print(f"  OK   {m}")


def bao(m: str) -> None:
    global sai
    sai += 1
    print(f"  SAI  {m}")


def n(t, o, h, l, c, v=100.0):  # noqa: E741
    return {"t": t, "o": o, "h": h, "l": l, "c": c, "v": v,
            "closeTime": t + 3_599_999, "closed": True}


# ── 1. nến chạm CẢ SL lẫn TP thì phải tính SL ─────────────────────────────
print("\n[1] nhập nhằng trong lòng nến — phải chọn phía BẤT LỢI")
# LONG: entry 100, SL 95, TP 110. Nến kế mở 100, quét xuống 94, lên 111.
# OHLC không cho biết cái nào chạm trước. Đoán TP là cách dựng một chiến lược
# đẹp trên giấy mà không tồn tại thật.
nen = [n(0, 100, 100, 100, 100), n(1, 100, 111, 94, 105)]
ly_do, gia, so = HL._thoat(nen, 0, 1, 100.0, 95.0, 110.0, 10, 0.0)
if ly_do == "SL":
    ok("nến chạm cả hai → tính SL (bi quan)")
else:
    bao(f"nến chạm cả hai mà tính {ly_do} — backtest sẽ thổi phồng tỉ lệ thắng")

# SHORT phải đối xứng: SL ở TRÊN, TP ở dưới.
nen = [n(0, 100, 100, 100, 100), n(1, 100, 106, 89, 95)]
ly_do, _, _ = HL._thoat(nen, 0, -1, 100.0, 105.0, 90.0, 10, 0.0)
if ly_do == "SL":
    ok("short: nến chạm cả hai → tính SL")
else:
    bao(f"short chạm cả hai mà tính {ly_do}")

# Chỉ chạm TP thì phải là TP — nếu không thì luật bi quan đang nuốt cả lệnh thắng.
nen = [n(0, 100, 100, 100, 100), n(1, 100, 111, 99, 110)]
ly_do, _, _ = HL._thoat(nen, 0, 1, 100.0, 95.0, 110.0, 10, 0.0)
ok("chỉ chạm TP → tính TP") if ly_do == "TP" else bao(f"chỉ chạm TP mà tính {ly_do}")

# Không chạm gì trong hạn giữ → HET_HAN, và phải thoát ở giá đóng cửa.
nen = [n(0, 100, 100, 100, 100)] + [n(i, 100, 101, 99, 100.5) for i in range(1, 6)]
ly_do, gia, so = HL._thoat(nen, 0, 1, 100.0, 95.0, 110.0, 3, 0.0)
if ly_do == "HET_HAN" and so == 3:
    ok(f"không chạm gì → HET_HAN sau đúng {so} nến")
else:
    bao(f"hết hạn giữ ra {ly_do} sau {so} nến (mong HET_HAN sau 3)")


# ── 2. chi phí phải trừ ở CẢ hai đầu ──────────────────────────────────────
print("\n[2] phí và trượt giá")
nen = [n(0, 100, 100, 100, 100), n(1, 100, 111, 99, 110)]
_, gia_sach, _ = HL._thoat(nen, 0, 1, 100.0, 95.0, 110.0, 10, 0.0)
_, gia_phi, _ = HL._thoat(nen, 0, 1, 100.0, 95.0, 110.0, 10, 0.0015)
if gia_phi < gia_sach:
    ok(f"long thoát ở giá thấp hơn khi có phí ({gia_phi:.3f} < {gia_sach:.3f})")
else:
    bao("phí không được trừ khi thoát lệnh long")
_, gia_s2, _ = HL._thoat([n(0, 100, 100, 100, 100), n(1, 100, 101, 89, 90)],
                         0, -1, 100.0, 105.0, 90.0, 10, 0.0)
_, gia_p2, _ = HL._thoat([n(0, 100, 100, 100, 100), n(1, 100, 101, 89, 90)],
                         0, -1, 100.0, 105.0, 90.0, 10, 0.0015)
if gia_p2 > gia_s2:
    ok(f"short thoát ở giá cao hơn khi có phí ({gia_p2:.3f} > {gia_s2:.3f})")
else:
    bao("phí không được trừ khi thoát lệnh short")


# ── 3. KHÔNG ĐƯỢC NHÌN TƯƠNG LAI ──────────────────────────────────────────
print("\n[3] nhìn trộm tương lai")
nen_that = HL.nap_nen()
if not nen_that:
    print("  —    bỏ qua: chưa có dữ liệu, chạy scripts/tai-lich-su.py trước")
else:
    tf = CONFIG["timeframes"]["primary"]
    ctx = CONFIG["timeframes"]["context"]
    # Cắt ngắn đầu vào rồi chạy lại: những điểm tín hiệu nằm TRƯỚC chỗ cắt phải
    # giống hệt nhau. Lệch một chữ số nghĩa là feature ở nến i đã đọc dữ liệu
    # của nến sau i — sai lầm này làm mọi kết quả đẹp lên và không báo gì cả.
    N = 900
    ngan = {tf: nen_that[tf][:N], ctx: nen_that[ctx]}
    dai = {tf: nen_that[tf][:N + 120], ctx: nen_that[ctx]}
    a = HL.sinh_luan_diem(ngan)
    b = HL.sinh_luan_diem(dai)
    b_map = {x["i"]: x for x in b}
    lech = []
    for x in a:
        y = b_map.get(x["i"])
        if y is None:
            lech.append((x["i"], "mất điểm"))
        elif (abs((x["price"] or 0) - (y["price"] or 0)) > 1e-9
              or x["regime"]["primary"] != y["regime"]["primary"]
              or abs((x["atr"] or 0) - (y["atr"] or 0)) > 1e-9):
            lech.append((x["i"], f'{x["regime"]["primary"]}≠{y["regime"]["primary"]}'))
    if not a:
        bao("không sinh được điểm tín hiệu nào để so")
    elif lech:
        bao(f"{len(lech)}/{len(a)} điểm đổi khi thêm nến TƯƠNG LAI — có nhìn trộm: {lech[:3]}")
    else:
        ok(f"{len(a)} điểm tín hiệu không đổi khi thêm 120 nến tương lai")


# ── 4. cửa sổ chỉ báo phải khớp bản chạy thật ─────────────────────────────
print("\n[4] cửa sổ chỉ báo")
if nen_that:
    import inspect

    src = inspect.getsource(HL._trang_thai)
    if "cua_so" in src and "i + 1 - cua_so" in src:
        ok(f'lát nến bị chặn ở candleLimit = {CONFIG["data"]["candleLimit"]} như bản chạy thật')
    else:
        bao("lát nến không bị chặn — chạy lại đang cho chỉ báo nhìn nhiều lịch sử "
            "hơn bản chạy thật bao giờ thấy")


# ── 5. kill switch phải được báo, không được im lặng cắt ngắn ─────────────
print("\n[5] trung thực khi dừng sớm")
if nen_that:
    chuoi, _ = HL.lay_chuoi(nen_that, CONFIG["symbol"])
    kq = HL.chay_lai(nen_that, chuoi=chuoi)
    d = kq["dungSom"]
    if d:
        if kq["soNenXet"] < kq["soNenTrongDoan"]:
            ok(f'dừng sớm được báo: {d["lyDo"]} — đã xét {kq["soNenXet"]}/'
               f'{kq["soNenTrongDoan"]} nến, không nhận vơ cả đoạn')
        else:
            bao("dừng sớm mà vẫn báo đã xét hết đoạn")
    else:
        ok("không dừng sớm trong đoạn này")

    # Chế độ gỡ chốt phải THỰC SỰ chạy xa hơn. Chỉ xoá `halted_reason` là không
    # đủ: ngắt mạch tính lại sụt giảm mỗi lượt nên nó bật lại ngay — và hai chế
    # độ ra kết quả y hệt, trông như trùng hợp chứ không như một lỗi.
    kq2 = HL.chay_lai(nen_that, chuoi=chuoi, bo_qua_kill=True)
    if kq2["thongKe"]["so"] > kq["thongKe"]["so"]:
        ok(f'chế độ gỡ chốt chạy xa hơn thật: {kq2["thongKe"]["so"]} lệnh so với '
           f'{kq["thongKe"]["so"]}')
    elif not d:
        ok("không có chốt nào để gỡ")
    else:
        bao("gỡ chốt mà số lệnh không đổi — ngắt mạch vẫn đang chặn")


# ── 6. tham số chiến lược phải ĐỔI ĐƯỢC kết quả ───────────────────────────
print("\n[6] tham số dò phải có tác dụng")
if nen_that:
    a = HL.chay_lai(nen_that, chuoi=chuoi, bo_qua_kill=True,
                    tham={"stopAtr": 1.0})["thongKe"]
    b = HL.chay_lai(nen_that, chuoi=chuoi, bo_qua_kill=True,
                    tham={"stopAtr": 2.5})["thongKe"]
    if (a["so"], a["kyVongR"]) != (b["so"], b["kyVongR"]):
        ok(f'stopAtr đổi kết quả: 1.0→{a["kyVongR"]}R/{a["so"]} lệnh · '
           f'2.5→{b["kyVongR"]}R/{b["so"]} lệnh')
    else:
        bao("đổi stopAtr mà kết quả y nguyên — đang dò một tham số không có tác dụng")

    c = HL.chay_lai(nen_that, chuoi=chuoi, bo_qua_kill=True,
                    tham={"adxToiThieu": 35})["thongKe"]
    if c["so"] < a["so"]:
        ok(f'lọc ADX≥35 giảm số lệnh {a["so"]} → {c["so"]}')
    else:
        bao("lọc ADX không giảm số lệnh")


# ── 7. R-bội phải khớp định nghĩa ─────────────────────────────────────────
print("\n[7] R-bội = lãi ÷ tiền đã đặt cược")
if nen_that:
    kq = HL.chay_lai(nen_that, chuoi=chuoi, bo_qua_kill=True)
    sl = [t for t in kq["lenh"] if t["lyDo"] == "SL"]

    # Lệnh dính SL phải lỗ HƠN 1R, không phải đúng 1R: còn một lần phí nữa khi
    # thoát. Phần vượt = phí ÷ khoảng cách stop, nên stop càng hẹp càng vượt
    # nhiều — đo được từ −1,05R tới −1,42R trên dữ liệu thật. Ban đầu tôi kẹp
    # phép kiểm này ở −1,35 và nó báo đỏ hai lệnh stop hẹp; mã đúng, ngưỡng
    # kiểm sai. Gác đúng bất biến thay vì gác một khoảng đoán chừng.
    tot_hon = [t for t in sl if t["R"] > -1.0]
    if tot_hon:
        bao(f"{len(tot_hon)} lệnh chạm SL mà lỗ ÍT hơn 1R: {[t['R'] for t in tot_hon[:4]]} "
            f"— không thể xảy ra khi thoát ở đúng giá stop và còn trả phí")
    else:
        xa = [t["R"] for t in sl if t["R"] < -2.0]
        if xa:
            bao(f"{len(xa)} lệnh chạm SL lỗ quá 2R: {xa[:4]}")
        else:
            r = [t["R"] for t in sl]
            ok(f"{len(sl)} lệnh chạm SL đều lỗ hơn 1R vì phí lần thoát "
               f"({min(r):.2f}R … {max(r):.2f}R)")

    tp = [t for t in kq["lenh"] if t["lyDo"] == "TP" and t["R"] <= 0]
    ok("mọi lệnh chạm TP đều có R dương") if not tp else bao(f"{len(tp)} lệnh chạm TP mà R ≤ 0")

    # GIỚI HẠN ĐÃ BIẾT, ghi ở đây để không ai quên: mô hình này cho stop khớp
    # ĐÚNG giá stop cộng trượt cố định. Thật thì stop bị nhảy giá — tin ra lúc
    # 2h sáng, stop 95 khớp 90. Nghĩa là mọi con số ở đây vẫn còn LẠC QUAN hơn
    # thực tế một chút, kể cả sau khi đã bi quan hoá trong lòng nến.
    print("       (đã biết: chưa mô phỏng nhảy giá qua stop — số thật sẽ xấu hơn)")


# ── 8. một vị thế một lúc ─────────────────────────────────────────────────
print("\n[8] không chồng lệnh")
if nen_that:
    lenh = HL.chay_lai(nen_that, chuoi=chuoi, bo_qua_kill=True)["lenh"]
    chong = [(lenh[k - 1]["i"], lenh[k]["i"]) for k in range(1, len(lenh))
             if lenh[k]["i"] <= lenh[k - 1]["i"] + lenh[k - 1]["soNenGiu"]]
    if chong:
        bao(f"{len(chong)} cặp lệnh chồng nhau: {chong[:3]}")
    else:
        ok(f"{len(lenh)} lệnh, không cặp nào chồng lên nhau")


# ── 9. cắt trong/ngoài mẫu phải tách thật ─────────────────────────────────
print("\n[9] trong mẫu và ngoài mẫu không được dẫm lên nhau")
if nen_that:
    q = HL.quet(nen_that, chuoi=chuoi, luoi={"stopAtr": [1.5, 2.5], "demTp": [1.05, 1.3]})
    moc = q["mocCat"]
    tr = HL.chay_lai(nen_that, chuoi=chuoi, den_nen=moc, bo_qua_kill=True)["lenh"]
    ng = HL.chay_lai(nen_that, chuoi=chuoi, tu_nen=moc, bo_qua_kill=True)["lenh"]
    trung = {t["i"] for t in tr} & {t["i"] for t in ng}
    if trung:
        bao(f"{len(trung)} lệnh nằm ở CẢ hai phần — phép kiểm ngoài mẫu vô nghĩa")
    else:
        ok(f"trong mẫu {len(tr)} lệnh · ngoài mẫu {len(ng)} lệnh · không giao nhau")
    if "khopTroi" in q.get("totNhat", {}):
        ok(f'có báo mức khớp trội: {q["totNhat"]["khopTroi"]}')
    else:
        ok("chưa đủ mẫu để tính khớp trội — và điều đó được nói rõ")


# ── 10. thống kê rỗng không được ra số ─────────────────────────────────────
print("\n[10] không có lệnh thì không được bịa số")
tk = HL.thong_ke([], 10_000, 10_000)
if tk["tyLeThang"] is None and tk["kyVongR"] is None and tk["so"] == 0:
    ok("không lệnh nào → tỉ lệ thắng và kỳ vọng để None, không phải 0")
else:
    bao(f"thống kê rỗng trả về {tk['tyLeThang']} / {tk['kyVongR']} thay vì None")

tk2 = HL.thong_ke([{"R": 1.0, "von": 10_100, "soNenGiu": 3, "lyDo": "TP"}], 10_000, 10_100)
if tk2["heSoLoiNhuan"] is None:
    ok("không có lệnh thua → hệ số lợi nhuận để None chứ không phải vô cực")
else:
    bao(f"hệ số lợi nhuận ra {tk2['heSoLoiNhuan']} khi chưa có lệnh thua nào")

# ── 11. bồi thêm chuỗi phải ra ĐÚNG chuỗi tính lại từ đầu ──────────────────
print("\n[11] bồi thêm chuỗi = tính lại từ đầu, từng chữ một")
# Phép kiểm nhanh trong `selftest.py` [47] canh ĐIỀU KIỆN dùng lại; cái này
# canh KẾT QUẢ, trên nến thật, và vì thế nó chậm. Hai phép không thay nhau
# được: điều kiện đúng mà `_trang_thai` đọc thêm một trường nào đó ngoài hai
# lát cắt thì chỉ phép này bắt được.
_n11 = HL.nap_nen()
if not _n11:
    print("  —    bỏ qua: chưa có dữ liệu, chạy scripts/tai-lich-su.py trước")
else:
    _tf11 = CONFIG["timeframes"]["primary"]
    _ctx11 = CONFIG["timeframes"]["context"]
    # Cắt ngắn để chạy trong vài phút chứ không vài chục.
    _N11 = min(len(_n11[_tf11]), HL.KHOI_DONG + CONFIG["data"]["candleLimit"] + 60)
    _cu11 = {_tf11: _n11[_tf11][:_N11 - 2], _ctx11: _n11[_ctx11]}
    _moi11 = {_tf11: _n11[_tf11][3:_N11], _ctx11: _n11[_ctx11]}
    if _tf11 == _ctx11:
        _cu11 = {_tf11: _n11[_tf11][:_N11 - 2]}
        _moi11 = {_tf11: _n11[_tf11][3:_N11]}
    HL._bo_nho.clear()
    HL.lay_chuoi(_cu11, "BTCUSDT")                       # dựng gói cũ
    HL._bo_nho.clear()
    _boi11, _ng11 = HL.lay_chuoi(_moi11, "BTCUSDT")      # bồi thêm
    HL._bo_nho.clear()
    _het11 = HL.sinh_luan_diem(_moi11, symbol="BTCUSDT")  # chuẩn
    if json.dumps(_boi11, sort_keys=True) == json.dumps(_het11, sort_keys=True):
        ok(f"bồi thêm ra chuỗi y hệt tính lại từ đầu ({len(_boi11)} điểm · {_ng11})")
    else:
        bao(f"chuỗi bồi thêm KHÁC chuỗi tính lại: "
            f"{len(_boi11)} điểm so với {len(_het11)}")
    if "đĩa+" not in _ng11:
        bao(f"lượt hai không đi đường bồi thêm mà đi «{_ng11}» — cache vô dụng")
    else:
        ok("lượt hai đi đúng đường bồi thêm, không dựng lại cả chuỗi")


print("\n" + "=" * 60)
if sai:
    print(f"  {sai} phép kiểm hỏng.")
    sys.exit(1)
print("  CỖ MÁY CHẠY LẠI KHÔNG NÓI DỐI.")
print("=" * 60)
