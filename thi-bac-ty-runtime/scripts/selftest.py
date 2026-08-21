"""Phép kiểm số học — chạy được KHÔNG CẦN MẠNG.

    python scripts/selftest.py

Kiểm đúng những chỗ hỏng IM LẶNG: số vẫn ra, bảng vẫn xanh, chỉ có kết quả là
sai. Trọng tâm là hai chỗ mà bản v0.1 (`capital-hunter-bot`) làm sai và không
có gì báo:

  1. **Funding nhân theo giờ thay vì đếm theo mốc.** Giữ 4 giờ trên sàn kết
     toán 8 giờ ra 0,005% theo công thức cũ, và 0,000% trong thực tế.
  2. **So funding thô giữa hai sàn khác chu kỳ.** 0,08%/8h nhỏ hơn 0,015%/1h,
     nhưng nhìn con số thô thì ngược lại.

Không phép kiểm nào ở đây gọi mạng, và không phép kiểm nào ghi vào sổ thật —
`TBT_DATA_DIR` được trỏ sang thư mục tạm TRƯỚC khi import.
"""
from __future__ import annotations

import gzip
import os
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ["TBT_DATA_DIR"] = tempfile.mkdtemp(prefix="tbt-selftest-")

from bac.can_loi import (lech_mark_bps, net_apr_pct,            # noqa: E402
                         phi_khu_hoi_bps, tim_co_hoi)
from bac.config import CONFIG, DATA_DIR, che_hieu_luc, ly_do_khong_that  # noqa: E402
from bac.dongho import dem_moc, moi_gio, moi_ngay, thu_cap, thu_thuc     # noqa: E402
from bac.models import BaoGia                                    # noqa: E402
from bac.rui_ro import NHAN, CongRuiRo                           # noqa: E402
from bac.san.base import moc_tron_gio_ke, nguyen_hoac_none, so_hoac_none  # noqa: E402
from bac.san.binance import _doi_chung                           # noqa: E402
from bac.san.okx import _chu_ky                                  # noqa: E402
from bac.so import So                                            # noqa: E402
from bac.bang import (XA_MOI_GIAY, MayGhi, _thu_muc,              # noqa: E402
                      dem_bang, doc_bang,
                      doc_bang_day_du as doc_bang_day_du_bang)
from bac.chay_lai import (KetQua, ThamSo, TraCuu, doi_chieu,      # noqa: E402
                          dung_bao_gia,
                          mot_luot as chay_lai_mot_luot)
from bac.chan_doan import TOI_THIEU_MAU, chan_doan                # noqa: E402
from bac.tien_hoa import (BIEN_VUOT, CUA_AN_TOAN, NUT_VAN,        # noqa: E402
                          dat_nut, de_xuat_tat_dinh)

_loi: list[str] = []
_dat = 0

GIO = 3_600_000.0


def kiem(nhan: str, dieu_kien: bool, chi_tiet: str = "") -> None:
    global _dat
    if dieu_kien:
        _dat += 1
        print(f"  ✓ {nhan}")
    else:
        _loi.append(nhan + (f" — {chi_tiet}" if chi_tiet else ""))
        print(f"  ✗ {nhan}" + (f"  ({chi_tiet})" if chi_tiet else ""))


def gan(a: float, b: float, sai: float = 1e-9) -> bool:
    return abs(a - b) <= sai


# ══════════════════════════════════════════════════════════════════════════
def kiem_chuan_hoa() -> None:
    print("\n── Chuẩn hoá: chỗ mọi scanner sơ sài chết ────────────────────")

    # Đúng ví dụ trong đề bài: nhìn thô thì Binance to hơn, chuẩn hoá thì không.
    binance = moi_gio(0.0008, 8.0)      # 0,08% / 8 giờ
    hyper = moi_gio(0.00015, 1.0)       # 0,015% / 1 giờ
    kiem("0,08%/8h = 0,010%/giờ", gan(binance, 0.0001))
    kiem("0,015%/1h = 0,015%/giờ", gan(hyper, 0.00015))
    kiem("chuẩn hoá LẬT NGƯỢC thứ hạng so với nhìn số thô",
         0.0008 > 0.00015 and hyper > binance,
         "đây chính là lỗi mà cả module dongho.py tồn tại để chặn")

    kiem("mỗi ngày = mỗi giờ × 24", gan(moi_ngay(0.0008, 8.0), 0.0001 * 24))

    nem = False
    try:
        moi_gio(0.001, 0.0)
    except ValueError:
        nem = True
    kiem("chu kỳ 0 thì NÉM, không trả về inf", nem,
         "một inf lọt vào bảng xếp hạng sẽ đứng đầu mọi cơ hội mãi mãi")


def kiem_dem_moc() -> None:
    print("\n── Đếm mốc: funding trả theo MỐC, không chảy liên tục ────────")

    now = 1_000_000_000_000.0

    # Vào lúc 00:05, mốc kế 08:00, giữ 4 giờ → KHÔNG mốc nào.
    moc_8h = now + 7.9 * GIO
    l = dem_moc(now, 4.0, int(moc_8h), 8.0)
    kiem("giữ 4h mà mốc còn 7,9h nữa → 0 mốc", l.soMoc == 0, f"đếm {l.soMoc}")
    kiem("và nói rõ còn bao lâu tới mốc đầu",
         l.choMocDauGiay is not None and gan(l.choMocDauGiay, 7.9 * 3600, 1.0))

    # Công thức CŨ sẽ nói có thu; công thức mới nói không.
    cu = moi_gio(0.0001, 8.0) * 4.0
    moi, _ = thu_thuc(now, 4.0, 0.0001, int(moc_8h), 8.0)
    kiem("công thức cũ báo có thu, thực tế bằng 0",
         cu > 0 and gan(moi, 0.0),
         f"cũ={cu:.6f} mới={moi:.6f}")

    # Vào 07:55, giữ 10 phút → thu TRỌN một chu kỳ.
    moc_gan = now + 5.0 * 60_000.0
    m2, _ = thu_thuc(now, 10.0 / 60.0, 0.0001, int(moc_gan), 8.0)
    kiem("giữ 10 PHÚT ngay trước mốc → thu trọn một chu kỳ", gan(m2, 0.0001))
    kiem("giữ 10 phút thu nhiều hơn giữ 4 giờ (cùng cặp số)", m2 > moi,
         "thời gian giữ dài hơn KHÔNG đồng nghĩa thu nhiều hơn")

    # Nhiều mốc.
    l3 = dem_moc(now, 24.0, int(now + 1 * GIO), 8.0)
    kiem("giữ 24h, chu kỳ 8h, mốc đầu sau 1h → 3 mốc", l3.soMoc == 3, f"đếm {l3.soMoc}")

    # Mốc rơi đúng biên cuối vẫn tính (lựa chọn lạc quan, có chủ ý).
    l4 = dem_moc(now, 2.0, int(now + 2 * GIO), 8.0)
    kiem("mốc rơi ĐÚNG biên cuối cửa sổ vẫn được tính", l4.soMoc == 1)

    # Mốc sàn trả về đã trôi qua → kéo về phía trước, không đếm âm.
    l5 = dem_moc(now, 8.0, int(now - 3 * GIO), 8.0)
    kiem("mốc đã trôi qua thì kéo tới mốc kế, không đếm âm",
         l5.soMoc >= 1 and l5.mocDauMs is not None and l5.mocDauMs >= now,
         f"đếm {l5.soMoc}")

    # Thiếu mốc → phải KHAI là ước lượng.
    l6 = dem_moc(now, 8.0, None, 8.0)
    kiem("thiếu mốc kế thì bật cờ ước lượng", l6.uocLuong)
    kiem("có mốc kế thì KHÔNG bật cờ ước lượng", not l3.uocLuong)

    nem = False
    try:
        dem_moc(now, -1.0, int(moc_8h), 8.0)
    except ValueError:
        nem = True
    kiem("giữ âm thì NÉM", nem)


def kiem_dau_funding() -> None:
    print("\n── Quy ước dấu: đúng cho CẢ nhánh âm ─────────────────────────")

    now = 1_000_000_000_000.0
    moc = int(now + 0.5 * GIO)

    # Cả hai dương: short nhận nhiều, long trả ít → lãi.
    a = thu_cap(now, 8.0, 0.00002, moc, 1.0, 0.00010, moc, 1.0)
    kiem("hai rate dương: thu = (nhận short) − (trả long) > 0", a["thu"] > 0)
    kiem("và đúng bằng chênh lệch × số mốc",
         gan(a["thu"], (0.00010 - 0.00002) * 8), f"{a['thu']}")

    # CẢ HAI ÂM — nhánh mà mọi bản `abs()` đều làm hỏng.
    b = thu_cap(now, 8.0, -0.00010, moc, 1.0, -0.00002, moc, 1.0)
    kiem("hai rate ÂM: vẫn lãi khi short ở sàn ÍT âm hơn", b["thu"] > 0,
         f"thu={b['thu']}")
    kiem("giá trị bằng đúng nhánh dương tương ứng", gan(b["thu"], a["thu"]))

    # Trái dấu — biên độ lớn nhất.
    c = thu_cap(now, 8.0, -0.00005, moc, 1.0, 0.00005, moc, 1.0)
    kiem("trái dấu: long NHẬN và short cũng NHẬN → thu lớn nhất",
         c["thu"] > a["thu"], f"{c['thu']} vs {a['thu']}")

    # Chu kỳ khác nhau giữa hai chân.
    d = thu_cap(now, 8.0, 0.0, moc, 8.0, 0.00001, moc, 1.0)
    kiem("hai chân hai chu kỳ: đếm mốc RIÊNG cho từng chân",
         d["soMocShort"] == 8 and d["soMocLong"] == 1,
         f"short={d['soMocShort']} long={d['soMocLong']}")


def kiem_can_loi() -> None:
    print("\n── Cân lợi: phí phải nhân BỐN lần khớp ───────────────────────")

    phi = {"a": {"phiTakerBps": 5.0, "truotGiaBps": 2.0},
           "b": {"phiTakerBps": 5.0, "truotGiaBps": 2.0}}
    kiem("phí khứ hồi = (5+2)×2 chân ×2 lượt = 28 bps",
         gan(phi_khu_hoi_bps("a", "b", phi), 28.0))
    kiem("sàn chưa khai phí thì tính 0, không nổ",
         gan(phi_khu_hoi_bps("a", "la", phi), 14.0))

    kiem("lệch mark 100 trên 10.000 = 100 bps",
         gan(lech_mark_bps(10_000.0, 10_100.0), 99.5024875621890, 1e-6))
    kiem("thiếu một mark → None, KHÔNG phải 0", lech_mark_bps(100.0, None) is None,
         "0 đọc thành 'không lệch', mà sự thật là 'không biết'")
    kiem("giá 0 cũng là không biết", lech_mark_bps(0.0, 100.0) is None)

    kiem("APR ngoại suy đúng hệ số", gan(net_apr_pct(10.0, 24.0), 0.001 * 365 * 100))
    kiem("cửa sổ giữ quá ngắn → None chứ không phải số khổng lồ",
         net_apr_pct(10.0, 0.1) is None)


#: `None` là một GIÁ TRỊ hợp lệ cho `moc` (sàn không công bố mốc), nên không
#: dùng được nó làm "chưa truyền". Bản đầu của phép kiểm dùng `moc=None` làm
#: mặc định, và ca "thiếu mốc" lặng lẽ nhận mốc mặc định — phép kiểm xanh
#: trong khi nó chưa bao giờ chạm tới nhánh đang định kiểm.
TU_LO = object()


def _bg(san, rate, gio, px=100.0, moc=TU_LO, ts=TU_LO, suy=False):
    now = int(time.time() * 1000)
    return BaoGia(san=san, ma="BTC", rate=rate, intervalGio=gio, markPx=px,
                  mocKeMs=(now + 60_000) if moc is TU_LO else moc,
                  nguonTsMs=now if ts is TU_LO else ts,
                  nhanTsMs=now, intervalSuyRa=suy)


def kiem_ghep_cap() -> None:
    print("\n── Ghép cặp: LONG nơi thấp, SHORT nơi cao ────────────────────")

    now = time.time() * 1000.0
    phi = {"a": {"phiTakerBps": 0, "truotGiaBps": 0},
           "b": {"phiTakerBps": 0, "truotGiaBps": 0}}
    mo = lambda co: (True, [])          # noqa: E731 — cổng mở, để kiểm phần ghép

    # a: 0,01%/8h = 0,00125%/giờ · b: 0,001%/1h = 0,001%/giờ → LONG b
    ds = tim_co_hoi([_bg("a", 0.0001, 8.0), _bg("b", 0.00001, 1.0)],
                    now, 8.0, phi, mo)
    kiem("ghép ra đúng một cặp từ hai báo giá", len(ds) == 1)
    c = ds[0]
    kiem("LONG đặt ở sàn funding/GIỜ thấp hơn", c.sanLong == "b", f"đang là {c.sanLong}")
    kiem("SHORT đặt ở sàn funding/giờ cao hơn", c.sanShort == "a")
    kiem("so bằng moiGio chứ KHÔNG bằng rate thô",
         0.0001 > 0.00001 and c.sanShort == "a",
         "nếu so rate thô thì cũng ra 'a', nên phải kiểm thêm cặp lật ngược")

    # Cặp LẬT NGƯỢC: rate thô của a nhỏ hơn, nhưng moiGio lớn hơn.
    ds2 = tim_co_hoi([_bg("a", 0.00015, 1.0), _bg("b", 0.0008, 8.0)],
                     now, 8.0, phi, mo)
    c2 = ds2[0]
    kiem("rate thô a < b nhưng a/giờ > b/giờ → SHORT phải là a",
         0.00015 < 0.0008 and c2.sanShort == "a",
         f"đang SHORT {c2.sanShort} — nếu so rate thô sẽ ra 'b', và đó là lỗi")

    kiem("ba báo giá → ba cặp", len(tim_co_hoi(
        [_bg("a", 0.0001, 8.0), _bg("b", 0.00001, 1.0), _bg("c", 0.0, 8.0)],
        now, 8.0, {}, mo)) == 3)

    # Xếp hạng theo NET, không theo APR.
    phi2 = {"a": {"phiTakerBps": 50, "truotGiaBps": 0},
            "b": {"phiTakerBps": 0, "truotGiaBps": 0},
            "c": {"phiTakerBps": 0, "truotGiaBps": 0},
            "d": {"phiTakerBps": 0, "truotGiaBps": 0}}
    ds3 = tim_co_hoi([_bg("a", 0.0, 1.0), _bg("b", 0.001, 1.0),
                      _bg("c", 0.0, 1.0), _bg("d", 0.0002, 1.0)],
                     now, 8.0, phi2, mo)
    kiem("xếp hạng giảm dần theo NET",
         all(ds3[i].netBps >= ds3[i + 1].netBps for i in range(len(ds3) - 1)))


def kiem_cong_rui_ro() -> None:
    print("\n── Cổng rủi ro: bảy cửa, mỗi cửa một cách mất tiền ───────────")

    now = time.time() * 1000.0
    phi = {"a": {"phiTakerBps": 0, "truotGiaBps": 0},
           "b": {"phiTakerBps": 0, "truotGiaBps": 0}}
    cong = CongRuiRo({"grossToiThieuBpsNgay": 3.0, "netToiThieuBps": 0.5,
                      "lechMarkToiDaBps": 40.0, "tuoiToiDaGiay": 90.0})

    # Cơ hội tốt, mốc dày → qua.
    tot = tim_co_hoi([_bg("a", 0.0, 1.0), _bg("b", 0.0001, 1.0)],
                     now, 8.0, phi, cong)[0]
    kiem("cơ hội lành thì QUA cửa", tot.duyet, str(tot.lyDo))

    # Chênh lệch quá mỏng.
    mong = tim_co_hoi([_bg("a", 0.0, 1.0), _bg("b", 0.00000001, 1.0)],
                      now, 8.0, phi, cong)[0]
    kiem("chênh lệch quá mỏng thì bị chặn", not mong.duyet)

    # Phí ăn hết.
    phi_to = {"a": {"phiTakerBps": 100, "truotGiaBps": 0},
              "b": {"phiTakerBps": 100, "truotGiaBps": 0}}
    lo = tim_co_hoi([_bg("a", 0.0, 1.0), _bg("b", 0.0001, 1.0)],
                    now, 8.0, phi_to, cong)[0]
    kiem("phí ăn hết biên → NET âm → chặn", lo.netBps < 0 and not lo.duyet)

    # KHÔNG mốc nào rơi vào cửa sổ — cửa mà v0.1 không hề có.
    xa = int(now + 20 * GIO)
    khong_moc = tim_co_hoi([_bg("a", 0.0, 8.0, moc=xa), _bg("b", 0.001, 8.0, moc=xa)],
                           now, 4.0, phi, cong)[0]
    kiem("không mốc nào rơi vào cửa sổ giữ → chặn", not khong_moc.duyet)
    kiem("và nói đúng lý do",
         any("mốc kết toán" in l for l in khong_moc.lyDo), str(khong_moc.lyDo))
    kiem("gross vẫn to nhưng thu THỰC bằng 0",
         khong_moc.grossBpsNgay > 3.0 and gan(khong_moc.thuBps, 0.0),
         "đây là cơ hội mà bản v0.1 sẽ duyệt")

    # Lệch mark.
    lech = tim_co_hoi([_bg("a", 0.0, 1.0, px=100.0), _bg("b", 0.0001, 1.0, px=101.0)],
                      now, 8.0, phi, cong)[0]
    kiem("lệch mark quá trần → chặn", not lech.duyet)

    # Thiếu mark.
    thieu = tim_co_hoi([_bg("a", 0.0, 1.0, px=None), _bg("b", 0.0001, 1.0)],
                       now, 8.0, phi, cong)[0]
    kiem("thiếu mark một bên → chặn, không coi là lệch 0", not thieu.duyet)

    # Dữ liệu cũ.
    cu = tim_co_hoi([_bg("a", 0.0, 1.0, ts=int(now - 500_000)),
                     _bg("b", 0.0001, 1.0)], now, 8.0, phi, cong)[0]
    kiem("dữ liệu cũ hơn trần → chặn", not cu.duyet)

    # Mốc phải đoán.
    doan = tim_co_hoi([_bg("a", 0.0, 1.0, moc=None), _bg("b", 0.0001, 1.0)],
                      now, 8.0, phi, cong)[0]
    kiem("mốc phải ĐOÁN → chặn (mặc định)", not doan.duyet)
    cong_nhan = CongRuiRo({"grossToiThieuBpsNgay": 3.0, "netToiThieuBps": 0.5,
                           "nhanUocLuongMoc": True})
    doan2 = tim_co_hoi([_bg("a", 0.0, 1.0, moc=None), _bg("b", 0.0001, 1.0)],
                       now, 8.0, phi, cong_nhan)[0]
    kiem("bật nhanUocLuongMoc thì cho qua", doan2.duyet, str(doan2.lyDo))

    # Gom đủ lý do, không dừng ở cái đầu.
    te = tim_co_hoi([_bg("a", 0.0, 1.0, px=None, ts=int(now - 500_000)),
                     _bg("b", 0.0, 1.0)], now, 8.0, phi, cong)[0]
    kiem("gom ĐỦ lý do từ chối, không dừng ở cái đầu tiên", len(te.lyDo) >= 3,
         f"{len(te.lyDo)} lý do: {te.lyDo}")

    # ── mã lý do: thứ đem đi GỘP ────────────────────────────────────────
    #   Bản đầu chỉ có câu, và buồng lái cắt chuỗi để gộp. Câu mang con số
    #   nên "NET sau phí -29.00" và "-28.00" thành hai khoá khác nhau: bảng
    #   "vì sao bị chặn" vỡ thành sáu dòng nói cùng một chuyện.
    kiem("mỗi lý do có một mã đi kèm", len(te.lyDoMa) == len(te.lyDo),
         f"{len(te.lyDoMa)} mã / {len(te.lyDo)} câu")
    kiem("mọi mã đều có nhãn trong bảng NHAN",
         all(m in NHAN for m in te.lyDoMa),
         f"mã lạ: {[m for m in te.lyDoMa if m not in NHAN]}")

    #   Hai cơ hội cùng hỏng một kiểu, khác con số → PHẢI cùng mã.
    a1 = tim_co_hoi([_bg("a", 0.0, 1.0), _bg("b", 0.0001, 1.0)],
                    now, 8.0, {"a": {"phiTakerBps": 100}, "b": {}}, cong)[0]
    a2 = tim_co_hoi([_bg("a", 0.0, 1.0), _bg("b", 0.0002, 1.0)],
                    now, 8.0, {"a": {"phiTakerBps": 90}, "b": {}}, cong)[0]
    kiem("hai cặp NET âm khác nhau vẫn cùng MỘT mã",
         "net-am" in a1.lyDoMa and "net-am" in a2.lyDoMa,
         f"{a1.lyDoMa} vs {a2.lyDoMa}")
    kiem("...trong khi CÂU thì khác nhau (nên câu không gộp được)",
         a1.lyDo != a2.lyDo,
         "câu giống nhau thì phép kiểm trên không chứng minh được gì")

    #   Và đây là phép bắt đúng lỗi cũ: gộp theo mã ra 1 dòng, gộp theo câu
    #   ra 2 dòng.
    theo_ma, theo_cau = set(), set()
    for x in (a1, a2):
        theo_ma.update(m for m in x.lyDoMa if m == "net-am")
        theo_cau.update(c for c in x.lyDo if c.startswith("NET"))
    kiem("gộp theo mã → 1 nhóm; gộp theo câu → 2 nhóm",
         len(theo_ma) == 1 and len(theo_cau) == 2,
         f"mã={len(theo_ma)} câu={len(theo_cau)}")


def kiem_dong_ho() -> None:
    print("\n── Đồng hồ: máy chậm 6,94 phút và KHÔNG gì báo ────────────────")

    from bac.dong_ho import NGUONG_KEU_MS, DongHo

    d = DongHo()
    kiem("chưa có mẫu thì lệch là None, KHÔNG phải 0",
         d.lech_ms() is None,
         "0 nghĩa là 'đã đo, khớp'; None nghĩa là 'chưa biết' — khác hẳn nhau")
    kiem("chưa đo thì bay_gio_ms rơi về giờ máy",
         abs(d.bay_gio_ms() - time.time() * 1000.0) < 50)

    # Ba sàn cùng nói máy chậm 416 giây — đúng số đo thật 21/08/2026.
    t = time.time() * 1000.0
    for san in ("binance", "okx", "bybit"):
        d.ghi_mau(san, t + 416_200, t, t)
    kiem("ba mẫu khớp → lệch đúng bằng mẫu",
         gan(d.lech_ms(), 416_200, 1.0), f"{d.lech_ms()}")
    kiem("bay_gio_ms bù đúng phần lệch",
         abs(d.bay_gio_ms() - (time.time() * 1000.0 + 416_200)) < 50)
    kiem("lệch quá ngưỡng thì KÊU", d.tom_tat()["dangKeu"])

    # Bù nửa vòng khứ hồi: dấu sàn đóng ở đâu đó giữa lúc gửi và lúc nhận.
    d3 = DongHo()
    d3.ghi_mau("a", t + 1000, t, t + 200)     # khứ hồi 200ms, trung điểm t+100
    kiem("bù nửa vòng khứ hồi", gan(d3.lech_ms(), 900.0, 1.0), f"{d3.lech_ms()}")

    # Một sàn trả dấu thời gian hỏng KHÔNG được kéo cả ước lượng đi.
    d.ghi_mau("hong", t + 99_999_999, t, t)
    kiem("trung vị chịu được MỘT sàn trả dấu hỏng",
         gan(d.lech_ms(), 416_200, 1.0),
         f"{d.lech_ms()} — trung bình sẽ bị kéo lệch, trung vị thì không")

    d2 = DongHo()
    d2.ghi_mau("a", t, t, t)
    kiem("máy khớp sàn thì không kêu",
         not d2.tom_tat()["dangKeu"] and gan(d2.lech_ms(), 0.0, 1.0))
    kiem("ngưỡng kêu là 5 giây", gan(NGUONG_KEU_MS, 5000.0))


def kiem_tuoi_am() -> None:
    print("\n── Tuổi ÂM: cửa 'dữ liệu cũ' từng chết trong im lặng ──────────")

    now = time.time() * 1000.0
    b_cu = _bg("a", 0.0, 1.0, ts=int(now - 600_000))
    b_tuong_lai = _bg("a", 0.0, 1.0, ts=int(now + 416_200))

    kiem("báo giá cũ 600s → tuổi +600", gan(b_cu.tuoi_giay(now), 600.0, 1.0))
    kiem("dấu thời gian ở TƯƠNG LAI → tuổi ÂM, không bị kẹp về 0",
         b_tuong_lai.tuoi_giay(now) < -400,
         f"đang là {b_tuong_lai.tuoi_giay(now):.0f} — kẹp về 0 là cách cửa "
         f"tuoiToiDaGiay bị vô hiệu suốt mà vẫn hiện trong bảng cấu hình")

    phi = {"a": {"phiTakerBps": 0, "truotGiaBps": 0},
           "b": {"phiTakerBps": 0, "truotGiaBps": 0}}
    cong = CongRuiRo({"grossToiThieuBpsNgay": 3.0, "netToiThieuBps": 0.5,
                      "lechDongHoToiDaGiay": 10.0})

    lech = tim_co_hoi([_bg("a", 0.0, 1.0, ts=int(now + 416_200)),
                       _bg("b", 0.0001, 1.0)], now, 8.0, phi, cong)[0]
    kiem("lệch đồng hồ → cơ hội bị CHẶN", not lech.duyet)
    kiem("và mã lý do đúng là lech-dong-ho", "lech-dong-ho" in lech.lyDoMa,
         str(lech.lyDoMa))

    # Chân này lệch −416s, chân kia mới +0,4s. `max()` trần sẽ lấy +0,4 và
    # che mất chỗ hỏng; phải lấy giá trị xa 0 nhất, giữ nguyên dấu.
    kiem("'tuổi xấu nhất' lấy giá trị xa 0 nhất, giữ dấu",
         lech.tuoiXauNhatGiay is not None and lech.tuoiXauNhatGiay < -400,
         f"đang là {lech.tuoiXauNhatGiay}")

    # Bù đúng lệch thì mọi thứ về bình thường.
    ok = tim_co_hoi([_bg("a", 0.0, 1.0, ts=int(now + 416_200)),
                     _bg("b", 0.0001, 1.0, ts=int(now + 416_200))],
                    now + 416_200, 8.0, phi, cong)[0]
    kiem("bù lệch rồi thì cơ hội qua cửa bình thường", ok.duyet, str(ok.lyDo))


def kiem_adapter() -> None:
    print("\n── Adapter: đơn vị và suy luận chu kỳ ────────────────────────")

    kiem("so_hoac_none loại chuỗi rỗng", so_hoac_none("") is None)
    kiem("so_hoac_none loại NaN", so_hoac_none(float("nan")) is None)
    kiem("so_hoac_none loại inf", so_hoac_none(float("inf")) is None)
    kiem("so_hoac_none đọc được chuỗi số", gan(so_hoac_none("1.5"), 1.5))
    kiem("nguyen_hoac_none đọc mốc ms", nguyen_hoac_none("1700000000000") == 1700000000000)

    m = moc_tron_gio_ke(1_000_000_000_000.0)
    kiem("mốc tròn giờ kế luôn ở phía trước", m > 1_000_000_000_000)
    kiem("và chia hết cho một giờ", m % 3_600_000 == 0)

    # OKX suy chu kỳ từ hai mốc sàn công bố.
    g, suy = _chu_ky(0, int(4 * GIO))
    kiem("OKX: hai mốc cách 4h → chu kỳ 4h, KHÔNG phải đoán", gan(g, 4.0) and not suy)
    g2, suy2 = _chu_ky(0, int(6.97 * GIO))
    kiem("OKX: khoảng vô lý → rơi về mặc định và KHAI là đoán",
         gan(g2, 8.0) and suy2)
    g3, suy3 = _chu_ky(None, None)
    kiem("OKX: thiếu mốc → mặc định + khai đoán", gan(g3, 8.0) and suy3)

    # Binance đối chứng chu kỳ.
    kiem("Binance: còn 3h tới mốc → chu kỳ ít nhất 4h",
         gan(_doi_chung(int(3 * GIO), 0), 4.0))
    kiem("Binance: còn 7h tới mốc → 8h", gan(_doi_chung(int(7 * GIO), 0), 8.0))
    kiem("Binance: còn 30h → không chu kỳ nào chứa nổi → None",
         _doi_chung(int(30 * GIO), 0) is None)
    kiem("Binance: mốc đã qua → None", _doi_chung(0, int(GIO)) is None)


def kiem_so() -> None:
    print("\n── Sổ: ghi cả lượt TRỐNG, và không ghi vào sổ thật ───────────")

    kiem("sổ nằm trong TBT_DATA_DIR, không phải sổ THẬT",
         str(DATA_DIR).startswith(os.environ["TBT_DATA_DIR"]), str(DATA_DIR))

    s = So(Path(os.environ["TBT_DATA_DIR"]) / "kiem.sqlite3")
    kiem("sổ mới thì thống kê nói CHƯA CÓ", s.thong_ke()["chuaCo"])

    s.ghi_luot([], soBaoGia=0, sanLoi=["binance"])
    tk = s.thong_ke()
    kiem("lượt TRỐNG vẫn được ghi", tk["soLuot"] == 1 and not tk["chuaCo"],
         "một tuần không cơ hội nào là một PHÁT HIỆN, không phải thiếu dữ liệu")

    now = time.time() * 1000.0
    phi = {"a": {"phiTakerBps": 0, "truotGiaBps": 0},
           "b": {"phiTakerBps": 0, "truotGiaBps": 0}}
    ds = tim_co_hoi([_bg("a", 0.0, 1.0), _bg("b", 0.0001, 1.0)],
                    now, 8.0, phi, CongRuiRo({}))
    for _ in range(3):
        s.ghi_luot(ds, soBaoGia=2, sanLoi=[])
    kiem("ghi cơ hội đếm đúng", s.thong_ke()["soCoHoi"] == 3)
    kiem("đọc lại được", len(s.gan_day(10)) == 3)

    d = s.do_dai("BTC", ds[0].sanLong, ds[0].sanShort, 24.0)
    kiem("độ dai đếm đúng số mẫu", d["soMau"] == 3)
    kiem("3 mẫu thì CHƯA đủ để kết luận", not d["duMau"])
    kiem("tỉ lệ dương tính đúng", d["tiLeDuong"] is not None and d["tiLeDuong"] > 0)

    trong = s.do_dai("KHONG-CO", "a", "b", 24.0)
    kiem("cặp chưa có mẫu: tỉ lệ là None, KHÔNG phải 0",
         trong["soMau"] == 0 and trong["tiLeDuong"] is None,
         "0 đọc thành 'chưa bao giờ dương' — một kết luận dữ liệu không hề nói")


def kiem_cua_dat_lenh() -> None:
    print("\n── Ba cửa: mặc định phải ĐÓNG ────────────────────────────────")

    kiem("chế độ khai mặc định là quan-sat", CONFIG["che"] == "quan-sat")
    kiem("chế độ hiệu lực KHÔNG BAO GIỜ là 'that' ở bản này",
         che_hieu_luc() != "that")
    ly = ly_do_khong_that()
    kiem("nói rõ có cửa đang đóng", len(ly) >= 1)
    kiem("và nói rõ lớp đặt lệnh CHƯA ĐƯỢC VIẾT",
         any("chưa được viết" in l for l in ly), str(ly))
    kiem("xác nhận rủi ro mặc định TẮT",
         not CONFIG["datLenh"]["toiXacNhanDaDocRuiRo"])


def kiem_gop_cau_hinh() -> None:
    print("\n── Gộp cấu hình: sửa một ngưỡng không được xoá sáu cửa kia ───")

    from bac.config import MAC_DINH, _gop
    ra = _gop(MAC_DINH, {"ruiRo": {"netToiThieuBps": 2.0}})
    kiem("ngưỡng sửa được", gan(ra["ruiRo"]["netToiThieuBps"], 2.0))
    kiem("các cửa KHÁC vẫn còn nguyên",
         "lechMarkToiDaBps" in ra["ruiRo"] and "tuoiToiDaGiay" in ra["ruiRo"],
         "gộp nông sẽ vứt sạch chúng, và cổng rủi ro mở toang trong im lặng")
    kiem("nhánh không đụng tới vẫn nguyên", ra["quet"]["giuGio"] == MAC_DINH["quet"]["giuGio"])


def _khung(lucMs, quotes):
    """Một khung băng: thời điểm + danh sách báo giá thô."""
    return {"luc": lucMs, "baoGia": [
        {"san": s, "ma": "BTC", "rate": r, "intervalGio": g,
         "markPx": 100.0, "mocKeMs": moc, "nguonTsMs": int(lucMs),
         "nhanTsMs": int(lucMs), "nguonTuSan": True}
        for s, r, g, moc in quotes]}


def kiem_bang() -> None:
    print("\n── Băng ghi: ký ức thô, và ba bài học chép sẵn ────────────────")

    tm = _thu_muc()
    kiem("thư mục băng nằm trong TBT_DATA_DIR, không phải băng THẬT",
         str(tm).startswith(os.environ["TBT_DATA_DIR"]), str(tm))

    m1 = MayGhi()
    for i in range(3):
        m1.ghi({"luc": 1000.0 + i, "vong": i, "baoGia": []})
    m1.dong()
    m2 = MayGhi()
    m2.ghi({"luc": 2000.0, "vong": 9, "baoGia": []})
    m2.dong()
    kiem("hai phiên ghi ra HAI file khác nhau", m1.duong != m2.duong,
         "nối thêm vào file cũ là cách sinh ra rác nằm giữa file")
    kiem("đọc lại thấy đủ khung của cả hai phiên", len(doc_bang()) == 4,
         f"đọc được {len(doc_bang())}")
    kiem("dem_bang đếm đúng bằng doc_bang",
         dem_bang().soKhung == len(doc_bang()))

    # ── xả theo THỜI GIAN, không theo số khung ──────────────────────────
    #   Đếm khung là sai theo nhịp: "mỗi 50 khung" ở nhịp 2 giây là 100
    #   giây, ở nhịp 30 giây là 25 PHÚT mất trắng mỗi lần tắt máy. Với cung
    #   cần hàng giờ băng mới có một mẫu, 25 phút là nhiều.
    kiem("xả theo giây, không theo số khung", gan(XA_MOI_GIAY, 60.0))
    truoc = dem_bang().soKhung
    m3 = MayGhi()
    m3.ghi({"luc": 9001.0, "baoGia": []})
    kiem("khung ĐẦU xuống đĩa ngay, không đợi đủ số",
         dem_bang().soKhung == truoc + 1,
         "không thì bảng trạng thái hiện 'phiên này 3 khung · trên đĩa 0'")
    for i in range(5):
        m3.ghi({"luc": 9002.0 + i, "baoGia": []})
    kiem("chưa tới hạn xả thì chưa xuống đĩa",
         dem_bang().soKhung == truoc + 1)
    m3.dong()
    kiem("đóng file thì xả nốt phần còn lại",
         dem_bang().soKhung == truoc + 6,
         f"{dem_bang().soKhung} vs {truoc + 6}")

    # Dựng lại đúng kiểu hỏng đã cắn ở cung kia: thành viên cụt + nối thêm.
    cu = gzip.compress(b'{"luc":1,"baoGia":[]}\n' * 40)
    moi_ = gzip.compress(b'{"luc":2,"baoGia":[]}\n' * 30)
    hong = tm / "bang-2999-01-01-000000-0.jsonl.gz"
    hong.write_bytes(cu[:len(cu) - 24] + moi_)

    nem = False
    try:
        with gzip.open(hong, "rt", encoding="utf-8") as f:
            for _ in f:
                pass
    except Exception:                              # noqa: BLE001
        nem = True
    kiem("(đối chứng) gzip.open TRẦN vẫn ném trên file kiểu này", nem)

    try:
        k, bao = doc_bang_day_du_bang("2999-01-01")
        da_nem = False
    except Exception:                              # noqa: BLE001
        k, bao, da_nem = [], None, True
    kiem("doc_bang KHÔNG ném trên băng hỏng", not da_nem)
    sau = sum(1 for x in k if x.get("luc") == 2)
    kiem("cứu được trọn phần sau chỗ đứt", sau == 30, f"chỉ thấy {sau}/30")
    kiem("khai ra là có file hỏng, không im lặng trả về thiếu",
         bao is not None and bao.soFileHong >= 1 and not bao.lanh_lan)
    hong.unlink(missing_ok=True)


def kiem_chay_lai() -> None:
    print("\n── Chạy lại: đo funding THỰC NHẬN, không phải dự đoán ─────────")

    kiem("dựng lại báo giá từ băng",
         dung_bao_gia({"san": "a", "ma": "BTC", "rate": 0.0001,
                       "intervalGio": 8.0}) is not None)
    kiem("thiếu chu kỳ → BỎ báo giá, không đoán bừa",
         dung_bao_gia({"san": "a", "ma": "BTC", "rate": 0.0001}) is None,
         "đoán bừa chu kỳ là đúng lỗi mà cả cung này tồn tại để chặn")
    kiem("chu kỳ 0 → bỏ",
         dung_bao_gia({"san": "a", "ma": "BTC", "rate": 0.0,
                       "intervalGio": 0}) is None)

    GIO = 3_600_000.0
    t0 = 1_000_000_000_000.0
    khung = []
    for i in range(30):
        t = t0 + i * 600_000.0                       # mỗi 10 phút, 5 giờ băng
        moc = t0 + (int(i * 600_000.0 // GIO) + 1) * GIO
        # Rate của "b" TỤT ngay sau khung đầu — mô phỏng funding decay.
        r_b = 0.0002 if i == 0 else 0.00001
        khung.append(_khung(t, [("a", 0.0, 1.0, moc), ("b", r_b, 1.0, moc)]))

    tra = TraCuu(khung)
    kiem("tra cứu lấy đúng rate tại một mốc",
         gan(tra.rate_tai("BTC", "b", t0), 0.0002))
    kiem("mốc ngoài tầm băng → None, KHÔNG phải 0",
         tra.rate_tai("BTC", "b", t0 - 10 * GIO) is None,
         "coi None là 0 là bịa ra một lần kết toán không trả gì")

    mo = {"grossToiThieuBpsNgay": 0.1, "netToiThieuBps": -999.0,
          "tuoiToiDaGiay": 1e9, "lechDongHoToiDaGiay": 1e9,
          "lechMarkToiDaBps": 1e9}
    ts = ThamSo(ten="thử", giuGio=2.0, ruiRo=dict(mo))
    kq = chay_lai_mot_luot(khung, ts, {"a": {}, "b": {}})
    kiem("chạy lại đi hết băng", kq.soKhung == 30, f"{kq.soKhung}")
    kiem("có cơ hội hậu kiểm được", kq.soDoDuoc > 0, f"{kq.soDoDuoc}")
    kiem("DỰ ĐOÁN cao hơn THỰC NHẬN vì funding tụt trước khi tới mốc",
         kq.sai_so_du_doan_bps is not None and kq.sai_so_du_doan_bps > 0,
         f"sai số {kq.sai_so_du_doan_bps} — đây là thứ chỉ băng mới đo được")

    kiem("chưa đo được cái nào thì kỳ vọng là None, không phải 0",
         KetQua("rỗng").ky_vong_bps is None)
    kiem("cờ đủ mẫu đúng bằng ngưỡng 30",
         kq.tom_tat()["duMau"] == (kq.soDoDuoc >= 30))

    so = doi_chieu(khung, ts, ThamSo("B", 4.0, dict(mo)), {"a": {}, "b": {}})
    kiem("đối chiếu chạy hai bộ trên CÙNG băng", "A" in so and "B" in so)
    kiem("thiếu mẫu thì nói thẳng, không kết luận",
         (so["duMau"] is True) or ("CHƯA đủ mẫu" in so["ghiChu"]))


def kiem_chan_doan_hoc() -> None:
    print("\n── Chẩn đoán: bệnh ĐO ĐƯỢC, không phải cảm giác ───────────────")

    it = KetQua("ít")
    it.soDoDuoc = 5
    it.soKhung = 100
    tc = chan_doan(it)
    kiem("ít mẫu → triệu chứng 'thiếu mẫu' và DỪNG hẳn",
         len(tc) == 1 and tc[0].ma == "thieu-mau",
         "chẩn tiếp trên 5 mẫu là học thuộc nhiễu")

    lo = KetQua("lỗ")
    lo.soDoDuoc = 50
    lo.soCoHoi = 50
    lo.soQuaCua = 50
    lo.tongNetThucBps = -100.0
    lo.soLai = 40
    lo.soLo = 10
    lo.tongThuDuDoanBps = 500.0
    lo.tongThuThucBps = 100.0
    ma = [t.ma for t in chan_doan(lo)]
    kiem("kỳ vọng âm → bắt được", "ky-vong-am" in ma, str(ma))
    kiem("dự đoán lạc quan có hệ thống → bắt được",
         "du-doan-lac-quan" in ma, str(ma))
    kiem("đuôi nặng → bắt được (thắng 80% mà vẫn lỗ)",
         "duoi-nang" in ma, str(ma))

    khoe = KetQua("khoẻ")
    khoe.soDoDuoc = 50
    khoe.soCoHoi = 50
    khoe.soQuaCua = 50
    khoe.tongNetThucBps = 100.0
    khoe.soLai = 45
    khoe.soLo = 5
    khoe.tongThuDuDoanBps = 100.0
    khoe.tongThuThucBps = 100.0
    kiem("không bệnh nào vượt ngưỡng → nói KHOẺ",
         [t.ma for t in chan_doan(khoe)] == ["khoe"])

    hut = KetQua("hụt")
    hut.soDoDuoc = 50
    hut.soCoHoi = 100
    hut.soQuaCua = 50
    hut.tongNetThucBps = 50.0
    hut.soLai = 30
    hut.soLo = 20
    hut.tongThuDuDoanBps = 50.0
    hut.tongThuThucBps = 50.0
    ma2 = [t.ma for t in chan_doan(hut, {"khong-moc": 80, "net-am": 20})]
    kiem("cửa sổ giữ hụt mốc → bắt được", "cua-so-hut-moc" in ma2, str(ma2))

    dh = [t for t in chan_doan(hut, {"lech-dong-ho": 5}) if t.ma == "dong-ho-lech"]
    kiem("đồng hồ lệch → nói rõ KHÔNG phải bệnh vặn tham số chữa được",
         len(dh) == 1 and dh[0].nutGoiY == [],
         "gợi ý núm cho nó là mời vòng tiến hoá đi vặn nhầm chỗ")


def kiem_tien_hoa_hoc() -> None:
    print("\n── Tiến hoá: bốn luật chặn bốn cách tự lừa ────────────────────")

    kiem("KHÔNG cửa an toàn nào nằm trong NUT_VAN",
         all(c not in NUT_VAN for c in CUA_AN_TOAN),
         "cho vòng tiến hoá nới cửa an toàn là dạy nó cách tắt đèn báo")
    kiem("phí KHÔNG phải núm vặn",
         "phiTakerBps" not in NUT_VAN and "truotGiaBps" not in NUT_VAN,
         "vặn phí xuống là đường dễ nhất tới điểm cao, nó sẽ tìm ra ngay")
    kiem("mọi núm đều có min/max",
         all("min" in v and "max" in v for v in NUT_VAN.values()))

    goc = ThamSo("gốc", 8.0, {"grossToiThieuBpsNgay": 3.0,
                              "netToiThieuBps": 0.5})

    class T:
        def __init__(self, ma, nut):
            self.ma, self.nutGoiY = ma, nut

    dx = de_xuat_tat_dinh([T("ky-vong-am", ["netToiThieuBps"])], goc)
    kiem("triệu chứng lỗ → đề xuất SIẾT ngưỡng NET",
         len(dx) == 1 and dx[0].den > dx[0].tu,
         str([d.tom_tat() for d in dx]))
    kiem("bước không vượt trần 25%",
         abs(dx[0].den - dx[0].tu) <= abs(dx[0].tu) * 0.2500001 + 1e-9)

    nhieu = de_xuat_tat_dinh(
        [T("ky-vong-am", ["netToiThieuBps"]),
         T("cua-qua-chat", ["grossToiThieuBpsNgay"])], goc)
    kiem("MỘT lượt chỉ vặn MỘT núm", len(nhieu) == 1,
         f"{len(nhieu)} — vặn hai núm rồi khá lên thì không biết núm nào có công")

    an = de_xuat_tat_dinh([T("dong-ho-lech", ["doiHoiHaiMark"])], goc)
    kiem("gợi ý chạm cửa an toàn thì BỎ QUA", an == [])

    bien = ThamSo("biên", 24.0, {"netToiThieuBps": 40.0})
    kiem("đã chạm biên thì không đề xuất nữa",
         de_xuat_tat_dinh([T("ky-vong-am", ["netToiThieuBps"])], bien) == [])

    moi = dat_nut(goc, "netToiThieuBps", 2.0, "thử")
    kiem("dat_nut đổi ĐÚNG một núm",
         moi.ruiRo["netToiThieuBps"] == 2.0
         and moi.ruiRo["grossToiThieuBpsNgay"] == 3.0
         and moi.giuGio == goc.giuGio)
    kiem("dat_nut KHÔNG sửa bản gốc", goc.ruiRo["netToiThieuBps"] == 0.5)
    kiem("dat_nut vặn được cả núm ở gốc (giuGio)",
         dat_nut(goc, "giuGio", 4.0, "t").giuGio == 4.0)

    kiem("biên vượt nhiễu là 0,15 bps", gan(BIEN_VUOT, 0.15))
    kiem("tối thiểu mẫu để chẩn là 30", TOI_THIEU_MAU == 30)


def main() -> int:
    print("=" * 70)
    print("  THỊ BẠC TY — phép kiểm số học (không cần mạng)")
    print("=" * 70)
    print(f"  cửa sổ giữ mặc định: {CONFIG['quet']['giuGio']:g} giờ")
    print("  NET sau phí mới là alpha. Funding thô thì không.")

    kiem_chuan_hoa()
    kiem_dem_moc()
    kiem_dau_funding()
    kiem_can_loi()
    kiem_ghep_cap()
    kiem_cong_rui_ro()
    kiem_dong_ho()
    kiem_tuoi_am()
    kiem_adapter()
    kiem_so()
    kiem_cua_dat_lenh()
    kiem_gop_cau_hinh()
    kiem_bang()
    kiem_chay_lai()
    kiem_chan_doan_hoc()
    kiem_tien_hoa_hoc()

    print("\n" + "=" * 70)
    if _loi:
        print(f"  {_dat} đạt · {len(_loi)} HỎNG")
        for l in _loi:
            print(f"    ✗ {l}")
        return 1
    print(f"  {_dat}/{_dat} đạt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
