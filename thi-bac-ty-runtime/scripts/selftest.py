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
from bac.config import (CONFIG, DATA_DIR, MA_CHIEN_LUOC,          # noqa: E402
                        che_hieu_luc, ly_do_khong_that)
from bac.dongho import dem_moc, moi_gio, moi_ngay, thu_cap, thu_thuc     # noqa: E402
from bac.models import BaoGia                                    # noqa: E402
from bac.rui_ro import NHAN, CongRuiRo                           # noqa: E402
from bac.san.base import moc_tron_gio_ke, nguyen_hoac_none, so_hoac_none  # noqa: E402
from bac.san.binance import _doi_chung                           # noqa: E402
from bac.san.okx import _chu_ky                                  # noqa: E402
from bac.so import So                                            # noqa: E402
from thi_bac_ty.to_trinh import (HO, MAT_RUI_RO, Chan,           # noqa: E402
                                 RuiRo, ToTrinh)
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


def kiem_cua_that() -> None:
    print("\n── Cửa phải THẬT: khai một cửa mà quên nối là bày cửa giả ─────")

    from bac.rui_ro import CUA, MAC_DINH

    kiem("CUA và MAC_DINH khai cùng một bộ khoá",
         set(CUA) == set(MAC_DINH),
         f"lệch: {set(CUA) ^ set(MAC_DINH)}")

    # Dict do thám: ghi lại MỌI khoá mà `xet()` thật sự đọc. Chạy qua nhiều
    # tình huống để chạm đủ các nhánh — một lời gọi chỉ đi qua vài nhánh.
    class _Thap(dict):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            self.daDoc = set()

        def __getitem__(self, k):
            self.daDoc.add(k)
            return super().__getitem__(k)

    now = time.time() * 1000.0
    phi = {"a": {"phiTakerBps": 0, "truotGiaBps": 0},
           "b": {"phiTakerBps": 0, "truotGiaBps": 0}}
    thap = _Thap(MAC_DINH)
    cong = CongRuiRo({})
    cong.c = thap

    GIO = 3_600_000.0
    canh = [
        # (báo giá A, báo giá B, giữ giờ) — mỗi dòng chạm một nhánh khác
        (_bg("a", 0.0, 1.0), _bg("b", 0.0001, 1.0), 8.0),          # lành
        (_bg("a", 0.0, 1.0), _bg("b", 0.0, 1.0), 8.0),             # gross mỏng
        (_bg("a", 0.0, 1.0, px=None), _bg("b", 0.0001, 1.0), 8.0),  # thiếu mark
        (_bg("a", 0.0, 1.0, px=100.0), _bg("b", 0.0001, 1.0, px=140.0), 8.0),
        (_bg("a", 0.0, 1.0, ts=int(now - 900_000)),
         _bg("b", 0.0001, 1.0), 8.0),                              # dữ liệu cũ
        (_bg("a", 0.0, 1.0, ts=int(now + 900_000)),
         _bg("b", 0.0001, 1.0), 8.0),                              # lệch đồng hồ
        (_bg("a", 0.0, 1.0, moc=None), _bg("b", 0.0001, 1.0), 8.0),  # mốc đoán
        (_bg("a", 0.0, 8.0, moc=int(now + 20 * GIO)),
         _bg("b", 0.001, 8.0, moc=int(now + 20 * GIO)), 4.0),      # không mốc
    ]
    for a, b, giu in canh:
        tim_co_hoi([a, b], now, giu, phi, cong)

    kiem("mọi cửa KHAI ra đều được xet() đọc thật",
         set(CUA) <= thap.daDoc,
         f"khai mà không ai đọc: {sorted(set(CUA) - thap.daDoc)} — "
         f"đây chính là 'cửa giả' mà buồng lái sẽ bày như đang có hiệu lực")
    kiem("xet() KHÔNG đọc khoá nào ngoài CUA",
         thap.daDoc <= set(CUA),
         f"đọc lén: {sorted(thap.daDoc - set(CUA))}")

    # tom_tat chỉ nói về cửa thật
    cong2 = CongRuiRo({"grossToiThieuBpsNgay": 3.0, "khoaLa": 999})
    kiem("tom_tat() lọc bỏ khoá lạ, không bày nó như cửa",
         "khoaLa" not in cong2.tom_tat(),
         "dict(self.c) trần sẽ bày mọi thứ người dùng nhét vào config.json")
    kiem("tom_tat() vẫn trả đủ cửa thật",
         set(cong2.tom_tat()) == set(CUA))


def kiem_von_chua_hieu_luc() -> None:
    print("\n── Trần vốn: khai rõ CHƯA có hiệu lực, và ở khối RIÊNG ────────")

    from bac.rui_ro import CUA

    kiem("ba núm vốn KHÔNG còn nằm trong khối ruiRo",
         all(k not in CONFIG["ruiRo"]
             for k in ("vonMoiCoHoiUsd", "vonToiDaUsd", "donBayToiDa")),
         "nằm trong ruiRo là hiện lên bảng 'Cửa rủi ro đang có hiệu lực'")
    kiem("chúng nằm ở khối `von` riêng", "von" in CONFIG)
    kiem("và khai thẳng là CHƯA có hiệu lực",
         CONFIG["von"]["coHieuLuc"] is False,
         "không có lớp đặt lệnh thì không có vị thế nào để giới hạn")
    kiem("không núm vốn nào lọt vào danh sách CỬA",
         not any("von" in c.lower() or "donBay" in c for c in CUA),
         str(CUA))
    kiem("giá trị vẫn giữ, không bịa lại",
         gan(CONFIG["von"]["moiCoHoiUsd"], 100.0)
         and gan(CONFIG["von"]["toiDaUsd"], 300.0))


def kiem_khai_phi_thieu() -> None:
    print("\n── Cơ hội phải KHAI mô hình phí còn thiếu gì ──────────────────")

    from bac.models import PHI_CON_THIEU

    kiem("có đúng bốn khoản chưa trừ", len(PHI_CON_THIEU) == 4, str(PHI_CON_THIEU))
    kiem("bốn khoản khớp docstring can_loi.py",
         set(PHI_CON_THIEU) == {"vay-coin", "chuyen-von",
                                "basis-luc-thoat", "von-bi-khoa"})

    now = time.time() * 1000.0
    phi = {"a": {"phiTakerBps": 0, "truotGiaBps": 0},
           "b": {"phiTakerBps": 0, "truotGiaBps": 0}}
    ds = tim_co_hoi([_bg("a", 0.0, 1.0), _bg("b", 0.0001, 1.0)],
                    now, 8.0, phi, CongRuiRo({}))
    kiem("mọi cơ hội đều mang cờ mô hình phí",
         all(not c.moHinhPhiDuChua for c in ds),
         "một trường mặc định 'đã đủ' mà quên đặt lại là cách con số bắt "
         "đầu nói dối")
    kiem("và mang theo danh sách khoản thiếu",
         all(set(c.phiConThieu) == set(PHI_CON_THIEU) for c in ds))
    t = ds[0].tom_tat()
    kiem("lát cắt mang cả hai trường ra ngoài",
         t["moHinhPhiDuChua"] is False and len(t["phiConThieu"]) == 4)

    # Soi bằng chính KHUÔN của hợp đồng, không bằng chuỗi chép tay. Bản đầu
    # neo vào tiền tố "perp." và gãy ngay khi mã đổi thành "perpetual." —
    # một phép kiểm chép lại hằng số thì nó canh bản chép, không canh luật.
    from thi_bac_ty.to_trinh import KHUON_CHIEN_LUOC
    kiem("mã chiến lược khớp KHUÔN của hợp đồng",
         bool(KHUON_CHIEN_LUOC.match(MA_CHIEN_LUOC)), MA_CHIEN_LUOC)


def _tt(**kw):
    """Một tờ trình hợp lệ tối thiểu; `kw` để bẻ từng chỗ một."""
    goc = dict(
        chienLuoc="perpetual.funding_spread.v1", ho="phai-sinh", taiSan="BTC",
        chan=(Chan("LONG", "hyperliquid", "BTC", 100.0),
              Chan("SHORT", "binance", "BTC", 100.0)),
        vonCanUsd=100.0, sucChuaToiDaUsd=5000.0,
        grossBps=10.0, phiUocBps=27.0, netUocBps=-17.0, giuGio=8.0,
        moHinhPhiDuChua=False, phiConThieu=("vay-coin",),
        moHinhSucChuaDuChua=False, sucChuaConThieu=("do-sau-so-lenh",),
    )
    goc.update(kw)
    return ToTrinh(**goc)


def kiem_hop_dong() -> None:
    print("\n── Tờ trình: hợp đồng tự soát mình ───────────────────────────")

    t = _tt()
    kiem("tờ trình đủ khuôn thì hợp lệ", t.hop_le, str(t.kiem()))
    kiem("có mã sinh tự động", len(t.ma) == 16)
    kiem("có dấu thời gian", t.luc.endswith("Z"))

    kiem("mã chiến lược sai khuôn → bắt",
         not _tt(chienLuoc="funding").hop_le)
    kiem("mã chiến lược thiếu phiên bản → bắt",
         not _tt(chienLuoc="perpetual.funding_spread").hop_le)
    kiem("họ lạ → bắt", not _tt(ho="ho-tu-bia").hop_le)
    kiem("bảy họ đúng bằng bảng phân loại lại", len(HO) == 7, str(HO))

    kiem("không chân nào → bắt", not _tt(chan=()).hop_le,
         "một cơ hội phải nói rõ nó vào đâu")
    kiem("bên lạ ở một chân → bắt",
         not _tt(chan=(Chan("MUA_MANH", "binance", "BTC"),)).hop_le)
    kiem("chân thiếu cảng → bắt",
         not _tt(chan=(Chan("LONG", "", "BTC"),)).hop_le)

    kiem("vốn xin ≤ 0 → bắt", not _tt(vonCanUsd=0.0).hop_le)
    kiem("xin nhiều hơn sức chứa → bắt",
         not _tt(vonCanUsd=9999.0, sucChuaToiDaUsd=100.0).hop_le,
         "rót quá sức chứa là tự giết chính cơ hội ấy")
    kiem("sức chứa None thì KHÔNG bắt (chưa đo được ≠ sai)",
         _tt(sucChuaToiDaUsd=None).hop_le)

    # Luật 2: khai nửa vời cũng là sai khuôn.
    kiem("phí chưa đủ mà không kê thiếu gì → bắt",
         not _tt(moHinhPhiDuChua=False, phiConThieu=()).hop_le,
         "người đọc biết nó thiếu mà không biết thiếu gì thì không cân được")
    kiem("khai đủ phí mà vẫn kê thiếu → bắt",
         not _tt(moHinhPhiDuChua=True, phiConThieu=("vay-coin",)).hop_le)
    kiem("sức chứa chưa đủ mà không kê thiếu gì → bắt",
         not _tt(moHinhSucChuaDuChua=False, sucChuaConThieu=()).hop_le)

    kiem("rủi ro ngoài thang [0,1] → bắt",
         not _tt(ruiRo=RuiRo(thiTruong=1.7)).hop_le)
    kiem("tin cậy ngoài thang → bắt", not _tt(tinCay=2.0).hop_le)

    # Gom hết lỗi, không dừng ở cái đầu.
    xau = _tt(chienLuoc="x", ho="y", vonCanUsd=-1.0)
    kiem("gom ĐỦ lỗi khuôn, không dừng ở cái đầu", len(xau.kiem()) >= 3,
         str(xau.kiem()))


def kiem_rui_ro_chua_do() -> None:
    print("\n── Rủi ro: KHÔNG BIẾT phải khác KHÔNG ────────────────────────")

    r = RuiRo(thiTruong=0.2, thanhKhoan=0.5)
    kiem("bốn mặt chưa đo được liệt kê ra", len(r.chua_do()) == 4, str(r.chua_do()))
    kiem("mặt nặng nhất lấy MAX của những mặt ĐÃ đo",
         gan(r.cao_nhat(), 0.5),
         "trung bình sẽ làm một cơ hội chết ở một mặt trông êm")
    kiem("chưa đo mặt nào → cao nhất là None, không phải 0",
         RuiRo().cao_nhat() is None,
         "0 nghĩa là 'đã xét, không có rủi ro' — Rủi Ro Tổng sẽ cộng những "
         "số 0 ấy thành một danh mục an toàn giả")
    kiem("sáu mặt đúng bằng bảng", len(MAT_RUI_RO) == 6)

    t = _tt(ruiRo=r).tom_tat()
    kiem("tóm tắt mang theo danh sách chưa đo",
         len(t["ruiRo"]["chuaDo"]) == 4)


def kiem_so_sanh_lien_ty() -> None:
    print("\n── NET mỗi giờ: thước SO SÁNH giữa các ty ────────────────────")

    ngan = _tt(netUocBps=6.0, giuGio=2.0)
    dai = _tt(netUocBps=20.0, giuGio=24.0)
    kiem("20 bps giữ 24h THUA 6 bps giữ 2h",
         ngan.net_moi_gio_bps > dai.net_moi_gio_bps,
         f"{ngan.net_moi_gio_bps:.3f} vs {dai.net_moi_gio_bps:.3f} — "
         f"vốn quay được mười hai lượt")
    kiem("net mỗi giờ tính đúng", gan(ngan.net_moi_gio_bps, 3.0))


def kiem_suc_chua() -> None:
    print("\n── Sức chứa: MIN hai chân, và thà None còn hơn bịa ───────────")

    from bac.suc_chua import PHAN_OI, SAN_USD, TRAN_USD, uoc_luong

    s, thieu = uoc_luong(1_000_000.0, 4_000_000.0)
    kiem("lấy MIN của hai chân, không lấy trung bình",
         gan(s, 1_000_000.0 * PHAN_OI),
         "chân mỏng hơn quyết — vị thế phải vào được CẢ HAI")
    kiem("luôn khai là mô hình chưa đủ", "do-sau-so-lenh" in thieu)

    s2, t2 = uoc_luong(1e12, 1e12)
    kiem("có trần tuyệt đối, chặn OI sai đơn vị", gan(s2, TRAN_USD),
         "đã thấy sàn trả OI bằng số COIN thay vì USD")

    s3, t3 = uoc_luong(1000.0, 1000.0)
    kiem("dưới sàn thì trả None, không trả số bé vô nghĩa", s3 is None)
    kiem("và nói rõ vì sao", "suc-chua-duoi-san" in t3)

    s4, t4 = uoc_luong(None, None)
    kiem("không cảng nào báo OI → None", s4 is None)
    kiem("và khai không cảng nào báo", "khong-cang-nao-bao-oi" in t4)

    s5, t5 = uoc_luong(2_000_000.0, None)
    kiem("một cảng báo thì vẫn suy được", s5 is not None)
    kiem("nhưng khai rõ là suy từ MỘT phía", "chi-mot-cang-bao-oi" in t5)


def kiem_adapter_ty() -> None:
    print("\n── Adapter: dịch, KHÔNG bịa số ───────────────────────────────")

    from bac.xuat_to_trinh import CHIEN_LUOC, xuat_to_trinh

    now = time.time() * 1000.0
    phi = {"a": {"phiTakerBps": 0, "truotGiaBps": 0},
           "b": {"phiTakerBps": 0, "truotGiaBps": 0}}
    co = tim_co_hoi([_bg("a", 0.0, 1.0), _bg("b", 0.0001, 1.0)],
                    now, 8.0, phi, CongRuiRo({}))[0]

    t = xuat_to_trinh(co, vonXinUsd=100.0,
                      oiLongUsd=2_000_000.0, oiShortUsd=3_000_000.0)
    kiem("tờ trình xuất ra hợp lệ", t.hop_le, str(t.kiem()))
    kiem("mang đúng mã chiến lược", t.chienLuoc == CHIEN_LUOC)
    kiem("mã chiến lược trong tờ trình KHỚP mã trong lát cắt",
         CHIEN_LUOC == MA_CHIEN_LUOC,
         "đã lệch thật một lần: lát cắt ghi perp.… còn tờ trình ghi "
         "perpetual.… — sổ đăng ký sẽ gộp thành hai dòng cho một chiến lược")
    kiem("thuộc họ phái sinh", t.ho == "phai-sinh")
    kiem("hai chân, LONG trước SHORT sau",
         len(t.chan) == 2 and t.chan[0].ben == "LONG"
         and t.chan[1].ben == "SHORT")
    kiem("chân trỏ đúng cảng của cơ hội",
         t.chan[0].cang == co.sanLong and t.chan[1].cang == co.sanShort)

    kiem("rủi ro giao thức là None, KHÔNG phải 0",
         t.ruiRo.giaoThuc is None,
         "ty Phái Sinh không chạm hợp đồng thông minh — ghi 0 là nói 'đã "
         "xét, không có rủi ro'")
    kiem("rủi ro cầu nối là None, KHÔNG phải 0", t.ruiRo.cauNoi is None)
    kiem("rủi ro cảng là None (chưa có mô hình xếp hạng sàn)",
         t.ruiRo.cang is None)
    kiem("rủi ro thị trường suy được từ lệch mark",
         t.ruiRo.thiTruong is not None)

    kiem("chép nguyên lời khai phí của CoHoi, không dựng lại",
         tuple(t.phiConThieu) == tuple(co.phiConThieu))
    kiem("sức chứa luôn khai là chưa đủ mô hình", not t.moHinhSucChuaDuChua)
    kiem("có bằng chứng đi kèm", len(t.bangChung) >= 4)

    # Thiếu mark → không biết lệch → rủi ro thị trường None, và tin cậy tụt.
    co2 = tim_co_hoi([_bg("a", 0.0, 1.0, px=None), _bg("b", 0.0001, 1.0)],
                     now, 8.0, phi, CongRuiRo({"doiHoiHaiMark": False}))[0]
    t2 = xuat_to_trinh(co2, 100.0, 2e6, 3e6)
    kiem("thiếu mark → rủi ro thị trường None, không phải 0",
         t2.ruiRo.thiTruong is None)
    kiem("và độ tin TỤT so với tờ trình đủ dữ liệu",
         t2.tinCay < t.tinCay, f"{t2.tinCay} vs {t.tinCay}")

    kiem("không OI cảng nào → sức chứa None nhưng tờ trình VẪN hợp lệ",
         xuat_to_trinh(co, 100.0, None, None).hop_le)


def kiem_chieu_phu_thuoc() -> None:
    print("\n── Kiến trúc: trung ương KHÔNG được biết ty nào tồn tại ───────")

    import pathlib
    goc = pathlib.Path(__file__).resolve().parent.parent / "thi_bac_ty"
    xau = []
    for p in goc.glob("*.py"):
        s = p.read_text(encoding="utf-8")
        for d in s.splitlines():
            d = d.strip()
            if d.startswith(("import bac", "from bac")):
                xau.append(f"{p.name}: {d}")
    kiem("không file nào trong thi_bac_ty/ import bac/", not xau,
         f"{xau} — ngày trung ương phải import một ty để xử một trường hợp "
         f"riêng là ngày hợp đồng đã hỏng")

    # Và chiều ngược lại PHẢI có: ty biết trung ương.
    ad = (pathlib.Path(__file__).resolve().parent.parent
          / "bac" / "xuat_to_trinh.py").read_text(encoding="utf-8")
    kiem("ty import trung ương (chiều đúng)", "from thi_bac_ty" in ad)

    # Trung ương không được nhắc tới thuật ngữ của một ty cụ thể.
    tu_cam = ("funding", "perp", "mocKe", "intervalGio")
    lo = []
    for p in goc.glob("*.py"):
        s = p.read_text(encoding="utf-8").lower()
        for t in tu_cam:
            # `to_trinh.py` được phép nêu ví dụ trong docstring, nên chỉ soi
            # phần MÃ: bỏ mọi dòng bắt đầu bằng # hoặc nằm trong docstring
            # thì phức tạp; ở đây chỉ cấm trong tên định danh.
            if f"def {t}" in s or f"{t} =" in s:
                lo.append(f"{p.name}: {t}")
    kiem("trung ương không có định danh nào mang thuật ngữ một ty", not lo,
         str(lo))


# ══════════════════════════════════════════════════════════════════════════
#  TRUNG ƯƠNG — chín tầng, và câu hỏi cuối: hai ty khác ngành sống chung được?
# ══════════════════════════════════════════════════════════════════════════

def _mau(ma="perpetual.funding_spread.v1", ho="phai-sinh", taiSan="BTC",
        von=100.0, chua=1000.0, net=8.0, giu=8.0, chan=None, tin=0.9,
        rr=None, **kw):
    """Một tờ trình hợp lệ, đủ để đi hết đường ống. Sửa gì thì truyền vào."""
    from thi_bac_ty.to_trinh import Chan as _C, RuiRo as _R
    if chan is None:
        chan = (_C("LONG", "hyperliquid", taiSan, loai="perp"),
                _C("SHORT", "binance", taiSan, loai="perp"))
    return ToTrinh(
        chienLuoc=ma, ho=ho, taiSan=taiSan, chan=tuple(chan),
        vonCanUsd=von, sucChuaToiDaUsd=chua,
        grossBps=net + 2.0, phiUocBps=2.0, netUocBps=net, giuGio=giu,
        ruiRo=rr if rr is not None else _R(0.2, 0.2, 0.1, 0.2, 0.2, 0.0),
        tinCay=tin, moHinhPhiDuChua=True,
        moHinhSucChuaDuChua=False, sucChuaConThieu=("do-sau-so-lenh",),
        cang=tuple(c.cang for c in chan), **kw)


def _tam(ten: str):
    import tempfile as _tf
    from pathlib import Path as _P
    return _P(_tf.mkdtemp(prefix=f"tbt-{ten}-"))


def kiem_so_cai() -> None:
    print("\n── Sổ Cái: chỉ thêm, không sửa; sai thì ĐẢO chứ không xoá ────")
    from thi_bac_ty.so_cai import ButToan, SoCai

    sc = SoCai(_tam("socai") / "so.sqlite3")

    kiem("loại tự bịa bị chặn ngay lúc ghi",
         not sc.ghi(ButToan("LOAI_BIA", "gì đó", 1.0)))
    kiem("bút toán không lý do bị chặn",
         not sc.ghi(ButToan("PHI", "   ", -1.0)),
         "sổ cái tồn tại để trả lời 'vì sao'")
    kiem("hai lần ghi hỏng thì đếm được", sc.soLoiGhi == 2)

    ok = sc.ghi(ButToan("FUNDING", "mốc 08:00", 12.5, "a.b.v1", "TT1"))
    kiem("bút toán hợp lệ ghi được", ok)

    dong = sc.gan_day(10)
    idg = dong[0]["id"]
    kiem("đảo một bút toán thì thành công", sc.dao(idg, "ghi nhầm gấp đôi"))
    sau = {d["id"]: d for d in sc.gan_day(10)}
    kiem("bản gốc KHÔNG bị sửa", sau[idg]["soTienUsd"] == 12.5,
         "sổ chỉ-thêm mà UPDATE được thì lịch sử không còn là lịch sử")
    dao = [d for d in sau.values() if d["loai"] == "DIEU_CHINH"]
    kiem("bút toán đảo mang dấu ngược",
         len(dao) == 1 and dao[0]["soTienUsd"] == -12.5)
    kiem("đảo hai lần cùng một bút toán bị chặn",
         not sc.dao(idg, "đảo lần hai"),
         "không thì một dòng sai đảo ba lần thành lãi")

    # Cấp vốn KHÔNG phải lãi lỗ — gộp nhầm là mỗi lần cấp $100 thành lỗ $100.
    sc.ghi(ButToan("CAP_VON", "cấp cho TT2", 500.0, "a.b.v1", "TT2"))
    sc.ghi(ButToan("PHI", "phí vào lệnh", -3.0, "a.b.v1", "TT2"))
    ll = sc.lai_lo_theo_chien_luoc()["a.b.v1"]["laiLoUsd"]
    kiem("lãi lỗ không tính CAP_VON", gan(ll, 12.5 - 12.5 - 3.0),
         f"đang là {ll}")


def kiem_danh_muc() -> None:
    print("\n── Danh Mục: ba thước phơi nhiễm, ba câu hỏi khác nhau ───────")
    from thi_bac_ty.danh_muc import DanhMuc, ViThe

    dm = DanhMuc(1000.0)
    kiem("cờ trung thực mặc định là MÔ PHỎNG", dm.nguonThat is False)
    kiem("bảng tóm tắt nói rõ đang mô phỏng",
         dm.tom_tat()["loiNhac"] is not None)

    chan = [ViThe("TT1", "a.b.v1", "LONG", "hyperliquid", "BTC", 200.0),
            ViThe("TT1", "a.b.v1", "SHORT", "binance", "BTC", 200.0)]
    kiem("cam kết delta-neutral thành công", dm.cam_ket("TT1", chan))
    kiem("cấp hai lần cùng một tờ trình bị chặn",
         not dm.cam_ket("TT1", chan))

    kiem("phơi nhiễm RÒNG của cặp delta-neutral = 0",
         gan(dm.phoi_nhiem_rong()["BTC"], 0.0),
         "đây là câu 'giá BTC chạy thì ta thiệt bao nhiêu'")
    kiem("phơi nhiễm THÔ = 400", gan(dm.phoi_nhiem_tho()["BTC"], 400.0),
         "đây là câu 'muốn thoát thì phải bán bao nhiêu'")
    kiem("phơi nhiễm CẢNG tách theo từng sàn",
         gan(dm.phoi_nhiem_cang()["binance"], 200.0)
         and gan(dm.phoi_nhiem_cang()["hyperliquid"], 200.0),
         "một sàn sập thì kẹt CẢ HAI chân, nên đây không phải thước ròng")

    kiem("tiền mặt đã trừ đúng", gan(dm.tienMatUsd, 600.0))
    kiem("NAV không đổi khi chỉ chuyển vốn", gan(dm.navUsd, 1000.0))

    to = [ViThe("TT2", "a.b.v1", "LONG", "okx", "ETH", 700.0)]
    kiem("Danh Mục tự chặn khi không đủ tiền mặt",
         not dm.cam_ket("TT2", to),
         "tầng cuối phải tự kiểm, không tin tầng trên đã kiểm")

    dm.dong("TT1", laiLoUsd=7.5)
    kiem("đóng vị thế thì hoàn vốn kèm lãi lỗ", gan(dm.tienMatUsd, 1007.5))
    kiem("lãi lỗ đã thực hiện được cộng dồn",
         gan(dm.laiLoDaThucHienUsd, 7.5))

    # DI_VAY là −1: vay BTC ra bán là đang short nó.
    dm2 = DanhMuc(1000.0)
    dm2.cam_ket("TTV", [ViThe("TTV", "c.d.v1", "DI_VAY", "aave", "BTC", 100.0),
                        ViThe("TTV", "c.d.v1", "CHO_VAY", "compound", "BTC",
                              100.0)])
    kiem("CHO_VAY (+1) và DI_VAY (−1) triệt tiêu nhau",
         gan(dm2.phoi_nhiem_rong()["BTC"], 0.0),
         "cho vay BTC thì vẫn GIỮ BTC; vay BTC ra bán là đang short")


def kiem_rui_ro_tong() -> None:
    print("\n── Rủi Ro Tổng: trả về một TRẦN, không phải một chữ có/không ──")
    from thi_bac_ty.danh_muc import DanhMuc, ViThe
    from thi_bac_ty.rui_ro_tong import PHAT_CHUA_DO, RuiRoTong
    from thi_bac_ty.to_trinh import Chan, RuiRo

    rrt = RuiRoTong()
    dm = DanhMuc(1000.0)

    pq = rrt.xet(_mau(von=100.0), dm)
    kiem("tờ trình lành được duyệt", pq.duyet)
    kiem("phán quyết mang một con số USD", isinstance(pq.choToiDaUsd, float))

    # Trần một cơ hội = 15% NAV → xin 500 chỉ được 150.
    pq2 = rrt.xet(_mau(von=500.0, chua=5000.0), dm)
    kiem("xin nhiều hơn trần thì bị CẮT chứ không bị từ chối",
         pq2.duyet and pq2.biCat and gan(pq2.choToiDaUsd, 150.0),
         f"đang cho {pq2.choToiDaUsd}")
    kiem("bị cắt thì phải nói cắt ở đâu", bool(pq2.lyDoCat))

    # Mặt rủi ro chưa đo KHÔNG được coi là 0.
    d_do, chua = rrt.diem(_mau(rr=RuiRo(0.1, 0.1, 0.1, 0.1, 0.1, 0.1)))
    d_chua, chua2 = rrt.diem(_mau(rr=RuiRo(0.1, 0.1, 0.1, 0.1, 0.1, None)))
    kiem("đo đủ sáu mặt thì điểm = mặt cao nhất", gan(d_do, 0.1))
    kiem("một mặt CHƯA ĐO thì bị phạt, không phải cho 0",
         gan(d_chua, PHAT_CHUA_DO) and chua2 == ("cauNoi",),
         "None ≠ 0; không đo được rủi ro cầu nối không có nghĩa là không có")

    # Điểm lấy MAX chứ không trung bình.
    d_max, _ = rrt.diem(_mau(rr=RuiRo(0.0, 0.0, 0.0, 0.0, 0.0, 0.9)))
    kiem("điểm rủi ro lấy MAX, không lấy trung bình", gan(d_max, 0.9),
         "an toàn năm mặt và chết ở mặt thứ sáu vẫn là một cơ hội chết")

    # Không đo được sức chứa thì không rót.
    pq3 = rrt.xet(_mau(chua=None), dm)
    kiem("chưa đo sức chứa thì bị từ chối", not pq3.duyet)
    kiem("và nói rõ vì sao",
         any("sức chứa" in l for l in pq3.lyDo))

    # Tờ trình sai khuôn chết ngay, không được xét tiếp.
    from dataclasses import replace as _rep
    xau = _rep(_mau(), chienLuoc="PERP.Funding.V1")
    pq4 = rrt.xet(xau, dm)
    kiem("tờ trình sai khuôn bị loại thẳng",
         not pq4.duyet and pq4.diemRuiRo is None)

    # Cặp delta-neutral KHÔNG bị trần phơi nhiễm RÒNG chặn…
    dm3 = DanhMuc(1000.0)
    pq5 = rrt.xet(_mau(von=100.0), dm3)
    kiem("cặp delta-neutral không chạm trần phơi nhiễm ròng",
         pq5.duyet and not any("ròng" in l for l in pq5.lyDoCat),
         "hai chân ngược nhau thì không làm lệch danh mục thêm chút nào")

    # …nhưng vị thế MỘT CHIỀU thì có.
    mot_chieu = _mau(von=100.0, chua=1000.0,
                    chan=(Chan("LONG", "binance", "BTC"),))
    dm4 = DanhMuc(1000.0)
    # Đã LONG 200 BTC; trần ròng là 25% NAV = 250, nên chỉ còn 50.
    dm4.cam_ket("CU", [ViThe("CU", "x.y.v1", "LONG", "okx", "BTC", 200.0)])
    pq6 = rrt.xet(mot_chieu, dm4)
    kiem("vị thế một chiều BỊ trần phơi nhiễm ròng chặn",
         gan(pq6.choToiDaUsd, 50.0)
         and any("ròng" in l for l in pq6.lyDoCat),
         f"cho {pq6.choToiDaUsd}, lyDoCat={pq6.lyDoCat}")

    # Trần tính theo NAV, không theo tiền mặt: cấp bớt tiền mặt đi mà NAV
    # không đổi thì trần một cơ hội phải không đổi.
    dm5 = DanhMuc(1000.0)
    dm5.cam_ket("K", [ViThe("K", "x.y.v1", "LONG", "kraken", "SOL", 400.0)])
    pq7 = rrt.xet(_mau(taiSan="AVAX", von=500.0, chua=5000.0,
                      chan=(Chan("LONG", "okx", "AVAX"),
                            Chan("SHORT", "bybit", "AVAX"))), dm5)
    kiem("trần một cơ hội tính trên NAV chứ không trên tiền mặt",
         gan(pq7.choToiDaUsd, 150.0),
         f"NAV vẫn 1000 nên trần vẫn 150; đang cho {pq7.choToiDaUsd}")


def kiem_phan_bo() -> None:
    print("\n── Phân Bổ: cấp TUẦN TỰ, vì cấp song song thì trần vô nghĩa ───")
    from thi_bac_ty.danh_muc import DanhMuc
    from thi_bac_ty.phan_bo import PhanBo
    from thi_bac_ty.rui_ro_tong import RuiRoTong
    from thi_bac_ty.to_trinh import Chan

    pb, rrt = PhanBo(), RuiRoTong()

    # NET ≤ 0 bị loại thẳng, dù mọi thứ khác đều đẹp.
    kiem("NET ≤ 0 xếp hạng −∞", PhanBo.diem(_mau(net=0.0), 0.1) == float("-inf"),
         "lỗ ít vẫn là lỗ")

    # Điểm = net/giờ × tin cậy × (1 − rủi ro)
    d = PhanBo.diem(_mau(net=8.0, giu=8.0, tin=0.5), 0.5)
    kiem("điểm nhân đủ ba thừa số", gan(d, 1.0 * 0.5 * 0.5), f"đang là {d}")
    kiem("không tự chấm được độ tin thì coi như 1.0",
         gan(PhanBo.diem(_mau(net=8.0, giu=8.0, tin=None), 0.0), 1.0))
    kiem("chưa đo được rủi ro thì coi như 0.5",
         gan(PhanBo.diem(_mau(net=8.0, giu=8.0, tin=1.0), None), 0.5),
         "không phải 0 — chưa biết không phải là an toàn")

    # ── chỗ quan trọng nhất: cấp tuần tự ──────────────────────────────────
    dm = DanhMuc(1000.0)
    nam = [_mau(taiSan=t, von=200.0, chua=5000.0,
                chan=(Chan("LONG", "hyperliquid", t),
                      Chan("SHORT", "binance", t)))
           for t in ("BTC", "ETH", "SOL", "AVAX", "DOT")]
    lat = pb.chia(nam, rrt, dm, luc="T")

    # Cấp SONG SONG thì cả năm đều 'lọt' (mỗi tờ 150, tổng 750) vì tờ nào
    # cũng được xét trên danh mục RỖNG. Cấp tuần tự thì tờ thứ tư chỉ còn
    # 50 và tờ thứ năm hết chỗ — trần một ty (50% NAV) mới thật sự chặn.
    pn_ty = dm.phoi_nhiem_ty()["perpetual.funding_spread.v1"]
    kiem("trần MỘT TY chặn được, vì danh mục cập nhật sau mỗi lần cấp",
         pn_ty <= 1000.0 * 0.50 + 1e-6,
         f"ty đang ôm {pn_ty} — cấp song song thì cộng lại mới vượt")
    kiem("tờ cuối bị từ chối vì hết chỗ", len(lat.tuChoi) >= 1,
         str(lat.tom_tat()))
    kiem("mọi lần từ chối đều kèm lý do",
         all(x.get("lyDo") for x in lat.tuChoi),
         "một phán quyết 0 đồng mà ô lý do trống thì không ai đọc thành "
         "'trần đã hết chỗ'")
    kiem("phần cấp về sau nhỏ dần, không bằng nhau",
         [x["capUsd"] for x in lat.daCap]
         == sorted((x["capUsd"] for x in lat.daCap), reverse=True),
         str([x["capUsd"] for x in lat.daCap]))
    kiem("tổng cấp không vượt trần tổng dùng vốn",
         lat.tongCapUsd <= 1000.0 * 0.80 + 1e-6, f"{lat.tongCapUsd}")

    # Dự trữ: không bao giờ rót hết tiền mặt.
    kiem("giữ lại đúng 20% NAV làm dự trữ", gan(lat.duTruUsd, 200.0))
    kiem("tiền mặt còn lại không thấp hơn dự trữ",
         dm.tienMatUsd >= lat.duTruUsd - 1e-6,
         f"còn {dm.tienMatUsd}, dự trữ {lat.duTruUsd}")

    # Sàn tối thiểu: rót vụn thì phí cố định ăn hết.
    dm2 = DanhMuc(1000.0)
    dm2.cam_ket("X", [__import__("thi_bac_ty.danh_muc", fromlist=["ViThe"])
                      .ViThe("X", "x.y.v1", "LONG", "kraken", "SOL", 785.0)])
    lat2 = pb.chia([_mau(taiSan="DOT", von=100.0, chua=1000.0,
                        chan=(Chan("LONG", "okx", "DOT"),
                              Chan("SHORT", "bybit", "DOT")))],
                   rrt, dm2, luc="T")
    kiem("cấp dưới sàn tối thiểu thì thà không cấp",
         len(lat2.daCap) == 0
         and any("sàn" in str(x.get("lyDo")) for x in lat2.tuChoi),
         f"daCap={lat2.daCap} tuChoi={lat2.tuChoi}")


def kiem_so_dang_ky() -> None:
    print("\n── Sổ Đăng Ký: một chiều, một bước, và cái PHỄU ───────────────")
    from thi_bac_ty.so_dang_ky import SoDangKy, _hop_le

    kiem("PHAT_HIEN → DUYET_TY: một bước tới, hợp lệ",
         _hop_le("PHAT_HIEN", "DUYET_TY"))
    kiem("DUYET_TY → PHAT_HIEN: đi lùi, KHÔNG hợp lệ",
         not _hop_le("DUYET_TY", "PHAT_HIEN"))
    kiem("PHAT_HIEN → DA_CAP_VON: NHẢY CÓC, không hợp lệ",
         not _hop_le("PHAT_HIEN", "DA_CAP_VON"),
         "đây đúng là hình dạng của 'một tầng bỏ qua tầng trên nó'")
    kiem("TU_CHOI → DA_CAP_VON: từ trạng thái kết thúc, không đi đâu được",
         not _hop_le("TU_CHOI", "DA_CAP_VON"))
    kiem("mọi bước trên đường đi đều rẽ được vào TU_CHOI",
         all(_hop_le(t, "TU_CHOI")
             for t in ("PHAT_HIEN", "DUYET_TY", "DUYET_RUI_RO",
                       "DA_CAP_VON", "DA_MO")))

    sdk = SoDangKy(_tam("sdk") / "sdk.sqlite3")
    kiem("phễu rỗng: tỉ lệ là None, KHÔNG phải 0%",
         sdk.pheu()["tiLe"]["DA_CAP_VON"] is None,
         "'chưa có tờ nào' khác hẳn 'không tờ nào qua'")

    t1 = _mau()
    kiem("ghi nhận một tờ trình", sdk.ghi_nhan(t1))
    kiem("ghi nhận hai lần cùng mã thì bị chặn", not sdk.ghi_nhan(t1))
    kiem("chuyển hợp lệ thì được", sdk.chuyen(t1.ma, "DUYET_TY", "qua cổng ty"))
    kiem("nhảy cóc thì bị chặn",
         not sdk.chuyen(t1.ma, "DA_CAP_VON", "đi tắt"))
    kiem("và lần đi tắt ấy được ĐẾM ra", sdk.soChuyenSai == 1,
         "chặn im lặng thì không ai biết có tầng đang đi tắt")
    kiem("chuyển sai không làm hỏng trạng thái đang có",
         sdk.phieu(t1.ma)["trangThai"] == "DUYET_TY")

    sdk.chuyen(t1.ma, "DUYET_RUI_RO", "qua rủi ro tổng")
    sdk.chuyen(t1.ma, "DA_CAP_VON", "cấp 100")
    p = sdk.pheu()
    kiem("phễu đếm đúng từng nấc",
         p["PHAT_HIEN"] == 1 and p["DUYET_RUI_RO"] == 1
         and p["DA_CAP_VON"] == 1)
    kiem("đường đi của một tờ trình đọc lại được đủ",
         len(sdk.phieu(t1.ma)["duongDi"]) == 4)


def kiem_cau_dao() -> None:
    print("\n── Cầu Dao: ngắt TỰ ĐỘNG, đóng lại PHẢI CÓ NGƯỜI ─────────────")
    import inspect
    from thi_bac_ty.cau_dao import CauDao

    NG = {"lechDongHoToiDaGiay": 60.0, "soCangChetToiDa": 0,
          "tuoiToiDaGiay": 300.0, "sutVonToiDaPct": 10.0}
    cd = CauDao()

    cd.tu_soat(lechDongHoGiay=None, cangChet=[], tuoiXauNhatGiay=1.0,
               sutVonPct=0.0, nguong=NG)
    kiem("CHƯA đo được đồng hồ đã là lý do ngắt", cd.dang_ngat,
         "chạy phép đếm mốc trên giờ máy là chạy mù")

    cd.tu_soat(lechDongHoGiay=2.0, cangChet=[], tuoiXauNhatGiay=1.0,
               sutVonPct=0.0, nguong=NG)
    kiem("đo được rồi thì lý do ấy tự gỡ", not cd.dang_ngat)

    cd.tu_soat(lechDongHoGiay=416.0, cangChet=[], tuoiXauNhatGiay=1.0,
               sutVonPct=0.0, nguong=NG)
    duoc, ly = cd.cho_phep()
    kiem("đồng hồ lệch 416s thì NGẮT", not duoc)
    kiem("và nói rõ lệch bao nhiêu", any("416" in l for l in ly))

    cd.tu_soat(lechDongHoGiay=1.0, cangChet=[], tuoiXauNhatGiay=1.0,
               sutVonPct=0.0, nguong=NG)
    kiem("đồng hồ khớp lại thì tự đóng lại", cd.cho_phep()[0],
         "đo trực tiếp và không mơ hồ thì mới được tự mở")

    # Sụt vốn thì KHÔNG tự mở lại.
    cd.tu_soat(lechDongHoGiay=1.0, cangChet=[], tuoiXauNhatGiay=1.0,
               sutVonPct=25.0, nguong=NG)
    kiem("sụt vốn 25% thì ngắt", not cd.cho_phep()[0])
    cd.tu_soat(lechDongHoGiay=1.0, cangChet=[], tuoiXauNhatGiay=1.0,
               sutVonPct=0.0, nguong=NG)
    kiem("sụt vốn hết thì VẪN ngắt", not cd.cho_phep()[0],
         "sụt vốn là hậu quả, không phải tín hiệu — nó 'hết' không có nghĩa "
         "là nguyên nhân đã hết")
    kiem("het_ly_do() không gỡ được lý do không tự mở",
         not cd.het_ly_do("sut-von"))
    kiem("phải có người mới đóng lại được",
         cd.dong_lai("sut-von", "nguoi-van-hanh") and cd.cho_phep()[0])

    sig = inspect.signature(CauDao.dong_lai)
    kiem("tham số `nguoi` KHÔNG có mặc định",
         sig.parameters["nguoi"].default is inspect.Parameter.empty,
         "đóng cầu dao là hành động có trách nhiệm; sổ phải ghi được ai làm")
    kiem("lịch sử ghi lại ai đóng",
         any(x.get("nguoi") == "nguoi-van-hanh" for x in cd.lichSu))


def kiem_thuc_thi() -> None:
    print("\n── Thực Thi: máy trạng thái hai chân, và legging risk ─────────")
    from thi_bac_ty.so_cai import SoCai
    from thi_bac_ty.thuc_thi import (DUONG, TRAN_CHUA_PHONG_HO_GIAY,
                                     DieuPhoiThucThi, PhienThucThi,
                                     YChiThucThi)
    from thi_bac_ty.to_trinh import Chan

    kiem("mọi trạng thái trong DUONG đều khai được đường ra",
         set(DUONG) >= {"CHO", "CHUA_PHONG_HO", "GIU", "PHANG"})
    kiem("trạng thái kết thúc thì không có đường ra",
         DUONG["DA_DOI_SOAT"] == () and DUONG["HONG"] == ()
         and DUONG["HOAN_VON"] == ())

    dp = DieuPhoiThucThi(moPhong=False)
    kiem("mô phỏng là CỨNG, cấu hình không tắt được", dp.moPhong is True,
         "lớp ký lệnh chưa tồn tại; một cờ tắt được là một lời hứa suông")

    sc = SoCai(_tam("tt") / "so.sqlite3")
    chan = (Chan("LONG", "hyperliquid", "BTC"), Chan("SHORT", "binance", "BTC"))
    y = YChiThucThi("TT1", "a.b.v1", chan, 200.0, "thử")
    p = dp.chay(y, sc)
    kiem("hai chân khớp thì về GIU", p.trangThai == "GIU")
    kiem("và đi đúng đường, không nhảy bước nào",
         [b["den"] for b in p.lichSu]
         == ["GIU_VON", "MO_CHAN_A", "MO_CHAN_B", "DA_PHONG_HO", "GIU"])

    # ── nhánh đáng giá nhất: chân B trượt ────────────────────────────────
    p2 = dp.chay(YChiThucThi("TT2", "a.b.v1", chan, 200.0), sc, chanBHong=True)
    duong = [b["den"] for b in p2.lichSu]
    kiem("chân B trượt thì vào CHUA_PHONG_HO", "CHUA_PHONG_HO" in duong)
    kiem("và ĐÓNG GẤP chứ không chờ",
         duong[-3:] == ["DANG_DONG", "PHANG", "DA_DOI_SOAT"],
         "một vị thế chưa phòng hộ để lâu là một cược một chiều không ai "
         "cố ý đặt")
    kiem("số lần đóng gấp đếm được", dp.soPhangGap == 1)
    kiem("sổ cái ghi lại lúc nguy hiểm",
         any(d["chiTiet"].get("nguyHiem") for d in sc.gan_day(50)))

    # Đồng hồ đếm ngược có thật.
    p3 = PhienThucThi(y)
    p3.chuyen("GIU_VON"); p3.chuyen("MO_CHAN_A"); p3.chuyen("MO_CHAN_B")
    p3.chuyen("CHUA_PHONG_HO", "chân B trượt")
    kiem("vừa vào CHUA_PHONG_HO thì chưa quá hạn",
         not p3.qua_han_phong_ho())
    kiem("quá trần thì phải đóng gấp",
         p3.qua_han_phong_ho(p3.vaoChuaPhongHoLuc
                             + TRAN_CHUA_PHONG_HO_GIAY + 1.0))
    kiem("trần chưa-phòng-hộ nhỏ có chủ ý",
         TRAN_CHUA_PHONG_HO_GIAY <= 60.0,
         f"đang là {TRAN_CHUA_PHONG_HO_GIAY}s")

    # Đường chuyển ngoài bảng bị chặn VÀ ghi lại.
    p4 = PhienThucThi(y)
    kiem("chuyển ngoài bảng DUONG bị chặn", not p4.chuyen("GIU", "đi tắt"))
    kiem("và lần đi tắt ấy vẫn vào lịch sử",
         p4.lichSu and p4.lichSu[-1]["chan"] is True,
         "chặn im lặng thì không ai biết có ai đó đang đi tắt")

    # Ý chí sai khuôn chết trước khi chạm sàn.
    p5 = dp.chay(YChiThucThi("TT3", "a.b.v1",
                             (Chan("LONG", "okx", "BTC"),
                              Chan("LONG", "bybit", "BTC")), 100.0), sc)
    kiem("hai chân CÙNG một bên bị chặn — đó không phải delta-neutral",
         p5.trangThai == "HONG")
    kiem("vốn ≤ 0 bị chặn",
         dp.chay(YChiThucThi("TT4", "a.b.v1", chan, 0.0), sc).trangThai
         == "HONG")


def kiem_khuon_ty() -> None:
    print("\n── Khuôn Ty: khai sai thì chết Ở CỬA, không chết sau ba tháng ─")
    from thi_bac_ty.khuon_ty import Ty
    from thi_bac_ty.thong_chinh import ThongChinh

    class TyTot(Ty):
        ma, ho, moTa = "perpetual.funding_spread.v1", "phai-sinh", "chênh funding"
        def quet(self): return [1, 2]
        def xet(self, co): return (co == 1), [("thu", "chỉ nhận số 1")]
        def trinh(self, co): return _mau()

    class TyMaSai(TyTot):
        ma = "Perp Funding V1"

    class TyHoLa(TyTot):
        ho = "phai-sinh-moi"

    class TyKhongMoTa(TyTot):
        moTa = "  "

    kiem("ty khai đúng thì qua", TyTot.kiem_khai() == [])
    kiem("mã sai khuôn bị bắt", any("sai khuôn" in l for l in TyMaSai.kiem_khai()))
    kiem("họ lạ bị bắt", any("không có trong" in l for l in TyHoLa.kiem_khai()))
    kiem("thiếu mô tả bị bắt", any("mô tả" in l for l in TyKhongMoTa.kiem_khai()))

    tc = ThongChinh()
    t = TyTot()
    ra = t.mot_luot(tc)
    kiem("mot_luot đi đủ quét → xét → trình",
         t.soLuotQuet == 1 and t.soCoHoi == 2 and t.soQuaCongTy == 1
         and len(ra) == 1)

    class TyNo(TyTot):
        ma = "perpetual.no_tung.v1"
        def quet(self): raise RuntimeError("sàn trả 502")

    tn = TyNo()
    kiem("ty nổ thì KHÔNG kéo theo cả hệ", tn.mot_luot(tc) == [])
    kiem("và lỗi của nó hiện ra chứ không im", "502" in (tn.loiCuoi or ""))

    class TyTrinhBay(TyTot):
        ma = "perpetual.bay.v1"
        def quet(self): return [1]
        def trinh(self, co):
            from dataclasses import replace
            return replace(_mau(), chienLuoc="BAY")

    tb = TyTrinhBay()
    tb.mot_luot(tc)
    kiem("tờ trình sai khuôn bị Thông Chính chặn ở cửa",
         tb.soTrinh == 0 and tb.soTrinhSaiKhuon == 1)
    kiem("và Thông Chính đếm được ty nào gửi sai",
         tc.tom_tat()["saiKhuonTheoTy"].get("BAY") == 1)


def kiem_trung_uong_vong() -> None:
    print("\n── Trung Ương: cả vòng, và cầu dao đứng trên tất cả ───────────")
    from thi_bac_ty.khuon_ty import Ty
    from thi_bac_ty.trung_uong import TrungUong

    class TyThu(Ty):
        ma, ho, moTa = "perpetual.funding_spread.v1", "phai-sinh", "thử"
        def __init__(self, ts): super().__init__(); self.ts = ts
        def quet(self): return list(self.ts)
        def xet(self, co): return True, []
        def trinh(self, co): return _mau(taiSan=co, von=100.0, chua=5000.0)

    tu = TrungUong(_tam("tu"), {"vonBanDauUsd": 1000.0})
    kiem("đăng ký ty khai đúng thì nhận", tu.dang_ky(TyThu(["BTC"])))

    class TyBia(TyThu):
        ma = "khong-dung-khuon"
    kiem("đăng ký ty khai sai thì TỪ CHỐI", not tu.dang_ky(TyBia(["BTC"])))
    kiem("và lần từ chối ấy vào sổ cái",
         any(d["chiTiet"].get("khaiSai") for d in tu.so_cai.gan_day(50)),
         "chết ở cửa, có ghi biên bản")

    lat = tu.mot_vong(lechDongHoGiay=1.0, cangChet=[], tuoiXauNhatGiay=5.0)
    kiem("một vòng chạy trọn", lat.soTyChay == 1 and lat.soToTrinhNhan == 1)
    kiem("cầu dao không ngắt khi mọi thứ lành", not lat.cauDaoNgat)
    kiem("vốn đã được cấp", lat.phanBo["soCap"] == 1)
    kiem("và vị thế đã mở", lat.soThucThi == 1)

    p = tu.so_dang_ky.pheu()
    kiem("phễu đi đủ năm nấc",
         p["PHAT_HIEN"] == 1 and p["DUYET_TY"] == 1 and p["DUYET_RUI_RO"] == 1
         and p["DA_CAP_VON"] == 1 and p["DA_MO"] == 1)
    kiem("KHÔNG có lần đi tắt nào", tu.so_dang_ky.soChuyenSai == 0,
         "mọi tầng đi đúng thứ tự, không tầng nào gọi vượt cấp")

    # ── cầu dao ngắt: vẫn quan sát, KHÔNG cam kết vốn ────────────────────
    tien_truoc = tu.danh_muc.tienMatUsd
    tu.ty["perpetual.funding_spread.v1"].ts = ["ETH"]
    lat2 = tu.mot_vong(lechDongHoGiay=999.0, cangChet=["okx"],
                       tuoiXauNhatGiay=5.0)
    kiem("đồng hồ lệch + cảng chết → cầu dao NGẮT", lat2.cauDaoNgat)
    kiem("ngắt rồi thì KHÔNG cấp đồng nào",
         gan(tu.danh_muc.tienMatUsd, tien_truoc) and lat2.phanBo is None)
    kiem("nhưng VẪN quét và VẪN ghi nhận", lat2.soGhiNhan == 1,
         "dừng quan sát là tự làm mình mù đúng lúc cần nhìn nhất")
    kiem("tờ trình bị từ chối có ghi rõ là do cầu dao",
         any("CẦU DAO" in b["lyDo"]
             for b in tu.so_dang_ky.phieu(
                 tu.so_dang_ky.theo_trang_thai("TU_CHOI")[0]["ma"])["duongDi"]))

    anh = tu.anh_chup()
    kiem("ảnh chụp đủ chín tầng",
         all(k in anh for k in ("ty", "thongChinh", "soDangKy", "danhMuc",
                                "ruiRoTong", "phanBo", "cauDao", "thucThi",
                                "soCai")))


def kiem_hai_ty_khac_nganh() -> None:
    print("\n── Câu hỏi cuối: hai ty KHÁC NGÀNH sống chung được không? ─────")
    from thi_bac_ty.khuon_ty import Ty
    from thi_bac_ty.to_trinh import Chan, RuiRo
    from thi_bac_ty.trung_uong import TrungUong

    # Ty thứ hai KHÔNG phải phái sinh, không có funding, không có mốc kết
    # toán, không có hai chân trên hai sàn perp. Nếu Trung Ương chỉ chạy
    # được với ty đầu tiên thì lớp trừu tượng này là giả.
    class TyChoVay(Ty):
        ma = "lending.rate_spread.v1"
        ho = "tin-dung"
        moTa = "vay chỗ rẻ, cho vay chỗ đắt — không mốc, không funding"

        def quet(self):
            return [{"taiSan": "USDC", "vay": "aave", "choVay": "compound",
                     "chenhBps": 14.0}]

        def xet(self, co):
            if co["chenhBps"] < 5.0:
                return False, [("chenh-mong", "chênh lãi suất quá mỏng")]
            return True, []

        def trinh(self, co):
            return ToTrinh(
                chienLuoc=self.ma, ho=self.ho, taiSan=co["taiSan"],
                chan=(Chan("DI_VAY", co["vay"], co["taiSan"],
                           loai="lending", chuoi="ethereum"),
                      Chan("CHO_VAY", co["choVay"], co["taiSan"],
                           loai="lending", chuoi="ethereum")),
                vonCanUsd=150.0, sucChuaToiDaUsd=8000.0,
                grossBps=co["chenhBps"], phiUocBps=3.0,
                netUocBps=co["chenhBps"] - 3.0, giuGio=24.0,
                ruiRo=RuiRo(thiTruong=0.05, thanhKhoan=0.15, giaoThuc=0.30,
                            cang=0.20, thucThi=0.10, cauNoi=0.0),
                tinCay=0.75, moHinhPhiDuChua=True,
                moHinhSucChuaDuChua=False,
                sucChuaConThieu=("do-sau-pool",),
                cang=(co["vay"], co["choVay"]), chuoi=("ethereum",),
                bangChung=(f"chênh {co['chenhBps']} bps",))

    class TyPerp(Ty):
        ma, ho = "perpetual.funding_spread.v1", "phai-sinh"
        moTa = "chênh funding giữa hai sàn perp"
        def quet(self): return ["BTC"]
        def xet(self, co): return True, []
        def trinh(self, co): return _mau(taiSan=co, von=150.0, chua=8000.0)

    tu = TrungUong(_tam("hai-ty"), {"vonBanDauUsd": 2000.0})
    kiem("ty phái sinh đăng ký được", tu.dang_ky(TyPerp()))
    kiem("ty tín dụng — ngành khác hẳn — cũng đăng ký được",
         tu.dang_ky(TyChoVay()),
         "không sửa một dòng nào trong trung ương")

    lat = tu.mot_vong(lechDongHoGiay=1.0, cangChet=[], tuoiXauNhatGiay=5.0)
    kiem("cả hai ty cùng quét trong một vòng", lat.soTyChay == 2)
    kiem("cả hai tờ trình cùng vào sổ đăng ký", lat.soGhiNhan == 2)
    kiem("cả hai cùng được cấp vốn", lat.phanBo["soCap"] == 2,
         str(lat.phanBo["tuChoi"]))

    theo_ty = tu.so_dang_ky.tom_tat()["theoTy"]
    kiem("sổ đăng ký tách được hai ty",
         theo_ty.get("perpetual.funding_spread.v1") == 1
         and theo_ty.get("lending.rate_spread.v1") == 1)

    pn_ty = tu.danh_muc.phoi_nhiem_ty()
    kiem("danh mục biết mỗi ty đang giữ bao nhiêu", len(pn_ty) == 2,
         str(pn_ty))

    # Đây là chỗ chứng minh lớp trừu tượng KHÔNG giả: một thước duy nhất so
    # được cơ hội của hai ngành hoàn toàn khác nhau.
    cap = {x["chienLuoc"]: x for x in lat.phanBo["daCap"]}
    perp = cap["perpetual.funding_spread.v1"]["netMoiGioBps"]
    vay = cap["lending.rate_spread.v1"]["netMoiGioBps"]
    kiem("NET mỗi giờ so được perp với cho vay",
         gan(perp, 8.0 / 8.0) and gan(vay, 11.0 / 24.0),
         f"perp={perp} vay={vay}")
    kiem("và xếp hạng đặt perp trên cho vay",
         cap["perpetual.funding_spread.v1"]["diemXep"]
         > cap["lending.rate_spread.v1"]["diemXep"],
         "6 bps giữ 2 giờ hơn 20 bps giữ 24 giờ — giuGio không phải số trang trí")

    # Phơi nhiễm cộng chéo hai ngành: USDC ở tầng cho vay và BTC ở tầng perp
    # đều là chân, đều vào cùng một bảng.
    kiem("phơi nhiễm chuỗi chỉ đếm chân có chuỗi",
         gan(tu.danh_muc.phoi_nhiem_chuoi().get("ethereum", 0.0),
             cap["lending.rate_spread.v1"]["capUsd"]),
         "chân sàn tập trung không có chuỗi, không được cộng nhầm vào")

    ll = tu.so_cai.tom_tat()["laiLoTheoTy"]
    kiem("sổ cái tách lãi lỗ theo từng ty", isinstance(ll, dict))

    # Và cuối cùng: trung ương vẫn không biết ty nào tồn tại.
    kiem("trung ương chỉ giữ ty qua khuôn, không qua tên cụ thể",
         set(tu.ty) == {"perpetual.funding_spread.v1",
                        "lending.rate_spread.v1"},
         "hai ty, một cỗ máy, không một dòng đặc thù nào trong trung ương")


def kiem_chan_doan_he() -> None:
    print("\n── Chẩn đoán hệ: vặn tham số phân bổ, KHÔNG vặn đèn báo ───────")
    from thi_bac_ty.chan_doan_he import (BUOC_TOI_DA, CUA_AN_TOAN_HE,
                                         NUT_TRUNG_UONG, chan_doan_he,
                                         de_xuat)
    from thi_bac_ty.khuon_ty import Ty
    from thi_bac_ty.trung_uong import TrungUong

    trung = set(NUT_TRUNG_UONG) & set(CUA_AN_TOAN_HE)
    kiem("không cửa an toàn nào lọt vào danh sách núm vặn được", not trung,
         f"{trung} — đường ngắn nhất tới điểm cao là tắt đèn báo, và nó sẽ "
         f"tìm ra ngay")

    # Đi tắt là bệnh nặng nhất, và không chờ đủ mẫu.
    tr = chan_doan_he({"soDangKy": {"soChuyenSai": 3, "pheu": {"phatHien": 2}}})
    dt = [t for t in tr if t.ma == "di-tat"]
    kiem("một tầng đi tắt là triệu chứng NẶNG", dt and dt[0].nang == 3)
    kiem("và nó không đề xuất vặn núm nào",
         de_xuat(dt, {"ruiRoTong": {"tranMotCang": 0.4}}) == [],
         "đi tắt là lỗi kiến trúc, vặn tham số không chữa được")

    # Chưa đủ mẫu thì đứng yên.
    tr2 = chan_doan_he({"soDangKy": {"pheu": {"phatHien": 7}}})
    kiem("chưa đủ tờ trình thì chẩn đúng một câu: chạy thêm",
         len(tr2) == 1 and tr2[0].ma == "thieu-to-trinh")

    # Tiền nằm không mà vẫn từ chối = trần đặt sai chỗ.
    anh = {"soDangKy": {"pheu": {"phatHien": 200, "DUYET_TY": 120,
                                 "DUYET_RUI_RO": 90, "DA_CAP_VON": 20,
                                 "DA_MO": 20}},
           "danhMuc": {"tiLeDungVon": 0.05}}
    tr3 = chan_doan_he(anh)
    ma3 = {t.ma for t in tr3}
    kiem("dùng vốn 5% mà vẫn từ chối → 'trần đặt sai chỗ'",
         "tran-dat-sai-cho" in ma3, str(ma3))

    dx = de_xuat(tr3, {"ruiRoTong": {"tranMotCang": 0.40}})
    kiem("và đề xuất NỚI, không phải siết",
         dx and dx[0].den > dx[0].tu, str([d.tom_tat() for d in dx]))
    kiem("bước vặn có trần",
         dx and abs(dx[0].den - dx[0].tu) <= abs(dx[0].tu) * BUOC_TOI_DA + 1e-9)
    kiem("mỗi lượt đề xuất ĐÚNG MỘT núm", len(dx) == 1,
         "vặn hai núm rồi thấy khá lên thì không biết núm nào có công")

    # Legging có hệ thống thì SIẾT lại.
    tr4 = chan_doan_he({"soDangKy": {"pheu": {"phatHien": 100}},
                        "thucThi": {"soPhien": 20, "soPhangGap": 6}})
    dx4 = de_xuat(tr4, {"ruiRoTong": {"tranMotCoHoi": 0.15}})
    kiem("legging có hệ thống thì đề xuất SIẾT",
         dx4 and dx4[0].den < dx4[0].tu, str([d.tom_tat() for d in dx4]))

    # Núm đã chạm biên thì không đề xuất bừa.
    dx5 = de_xuat(tr3, {"ruiRoTong": {"tranMotCang": 0.60}})
    kiem("núm đã chạm biên trên thì bỏ qua, không đề xuất bừa",
         all(d.nut != "ruiRoTong.tranMotCang" for d in dx5))

    # Khoẻ là một kết luận hợp lệ.
    tr6 = chan_doan_he({"soDangKy": {"pheu": {"phatHien": 300, "DUYET_TY": 200,
                                              "DUYET_RUI_RO": 150,
                                              "DA_CAP_VON": 100, "DA_MO": 95}},
                        "danhMuc": {"tiLeDungVon": 0.55}})
    kiem("không bệnh nào vượt ngưỡng thì báo KHOẺ",
         [t.ma for t in tr6] == ["khoe"], str([t.ma for t in tr6]))

    # Và vòng học của Trung Ương chỉ ĐỀ XUẤT.
    class TyIm(Ty):
        ma, ho, moTa = "perpetual.funding_spread.v1", "phai-sinh", "im"
        def quet(self): return []
        def xet(self, co): return False, []
        def trinh(self, co): return None

    tu = TrungUong(_tam("hoc"), {"vonBanDauUsd": 1000.0})
    tu.dang_ky(TyIm())
    tu.mot_vong(lechDongHoGiay=1.0, cangChet=[], tuoiXauNhatGiay=1.0)
    h = tu.hoc()
    kiem("vòng học chạy được và không tự vặn", h["tuVan"] is False,
         "đổi tham số phân bổ thì KHÔNG chạy lại được — không A/B được thì "
         "không tự nhận được")
    kiem("tham số đọc từ tầng thật, không từ phần ghi đè",
         "tranMotCang" in tu.tham_so()["ruiRoTong"],
         "đọc self.c thì thấy {} và kết luận là không có núm nào")
    kiem("nhật ký xét tham số được ghi ra đĩa", tu._soXet.exists())


def kiem_chong_trung() -> None:
    print("\n── Chống trùng: cùng một cơ hội KHÔNG vào sổ 120 lần mỗi giờ ──")
    from thi_bac_ty.khuon_ty import Ty
    from thi_bac_ty.to_trinh import Chan
    from thi_bac_ty.trung_uong import TrungUong, _dau_van

    a = _mau(taiSan="BTC")
    b = _mau(taiSan="BTC", net=9.9)          # cùng cơ hội, NET nhúc nhích
    c = _mau(taiSan="ETH")
    kiem("vân tay KHÔNG đổi khi NET nhúc nhích", _dau_van(a) == _dau_van(b),
         "gộp giá vào vân tay là mỗi lượt quét lại ra một vân mới")
    kiem("khác tài sản thì khác vân", _dau_van(a) != _dau_van(c))
    kiem("khác cảng thì khác vân",
         _dau_van(a) != _dau_van(_mau(
             chan=(Chan("LONG", "okx", "BTC"), Chan("SHORT", "bybit", "BTC")))))
    kiem("đảo thứ tự chân KHÔNG đổi vân",
         _dau_van(_mau(chan=(Chan("LONG", "hyperliquid", "BTC"),
                             Chan("SHORT", "binance", "BTC"))))
         == _dau_van(_mau(chan=(Chan("SHORT", "binance", "BTC"),
                                Chan("LONG", "hyperliquid", "BTC")))),
         "cùng một cặp, chỉ khác thứ tự liệt kê")

    class TyLap(Ty):
        ma, ho, moTa = "perpetual.funding_spread.v1", "phai-sinh", "trình lặp"
        def quet(self): return ["BTC"]
        def xet(self, co): return True, []
        def trinh(self, co): return _mau(taiSan="BTC", von=100.0, chua=5000.0)

    tu = TrungUong(_tam("trung"), {"vonBanDauUsd": 1000.0})
    tu.dang_ky(TyLap())
    l1 = tu.mot_vong(lechDongHoGiay=1.0, cangChet=[], tuoiXauNhatGiay=1.0)
    l2 = tu.mot_vong(lechDongHoGiay=1.0, cangChet=[], tuoiXauNhatGiay=1.0)
    l3 = tu.mot_vong(lechDongHoGiay=1.0, cangChet=[], tuoiXauNhatGiay=1.0)

    kiem("vòng đầu ghi nhận", l1.soGhiNhan == 1 and l1.soBoTrung == 0)
    kiem("hai vòng sau BỎ vì cùng một cơ hội",
         l2.soGhiNhan == 0 and l2.soBoTrung == 1
         and l3.soGhiNhan == 0 and l3.soBoTrung == 1)
    kiem("nên sổ chỉ có MỘT tờ trình, không phải ba",
         tu.so_dang_ky.tom_tat()["soToTrinh"] == 1,
         "mẫu số của cái phễu phải là số cơ hội THẬT, không phải số lượt quét")
    kiem("và vốn chỉ cấp MỘT lần cho cơ hội ấy",
         len(tu.danh_muc.viThe) == 1,
         "bỏ cửa này là cấp vốn hai lần cho cùng một cơ hội")

    # Hết nhịp thì ghi lại — cửa này là CHỐNG TRÙNG, không phải chặn vĩnh viễn.
    tu2 = TrungUong(_tam("trung2"), {"vonBanDauUsd": 1000.0,
                                     "nhipGhiNhanGiay": 0.0})
    tu2.dang_ky(TyLap())
    tu2.mot_vong(lechDongHoGiay=1.0, cangChet=[], tuoiXauNhatGiay=1.0)
    l = tu2.mot_vong(lechDongHoGiay=1.0, cangChet=[], tuoiXauNhatGiay=1.0)
    kiem("hết nhịp thì cơ hội được ghi lại", l.soGhiNhan == 1,
         "chặn vĩnh viễn thì một cơ hội quay lại sau ba ngày sẽ vô hình")


def kiem_chay_lai_he() -> None:
    print("\n── Chạy lại hệ: đo đề xuất, và chặn lối TỰ THÁO PHANH ────────")
    from thi_bac_ty.chay_lai_he import (BIEN_VUOT_BPS, TOI_THIEU_MAU,
                                        doi_chieu, dung_lai, mot_luot,
                                        thu_hoach)
    from thi_bac_ty.khuon_ty import Ty
    from thi_bac_ty.to_trinh import Chan
    from thi_bac_ty.trung_uong import TrungUong, _dat_nut

    # ── dựng lại phải KHÔNG mất trường nào ──────────────────────────────
    goc = _mau(taiSan="BTC", von=120.0, chua=4000.0, net=7.5, giu=6.0)
    lai = dung_lai(goc.tom_tat())
    kiem("dựng lại từ payload không mất trường nào",
         lai is not None and lai.ma == goc.ma
         and gan(lai.netUocBps, goc.netUocBps)
         and gan(lai.vonCanUsd, goc.vonCanUsd)
         and lai.chan[0].cang == goc.chan[0].cang
         and lai.ruiRo.tom_tat() == goc.ruiRo.tom_tat()
         and lai.phiConThieu == goc.phiConThieu,
         "sổ đăng ký lưu payload; mất một trường là chạy lại trên dữ liệu khác")
    kiem("payload hỏng trả None chứ không ném",
         dung_lai({"chienLuoc": "a.b.v1"}) is None,
         "một dòng hỏng không được giết cả lượt chạy lại")

    # ── NET/giờ bình quân phải theo VỐN, không theo đầu cơ hội ──────────
    # Hai cơ hội cùng được cấp ĐỦ số xin, nhưng cỡ vốn lệch hẳn nhau. Hai
    # cách tính cho hai con số khác xa — nên phép kiểm này phân biệt được.
    lo = [_mau(taiSan="AAA", von=500.0, chua=9000.0, net=12.0, giu=6.0,
               chan=(Chan("LONG", "hyperliquid", "AAA"),
                     Chan("SHORT", "binance", "AAA"))),
          _mau(taiSan="BBB", von=300.0, chua=9000.0, net=100.0, giu=1.0,
               chan=(Chan("LONG", "okx", "BBB"),
                     Chan("SHORT", "bybit", "BBB")))]
    kq = mot_luot(lo, {}, 10000.0, "thu")
    theo_von = (500.0 * 2.0 + 300.0 * 100.0) / 800.0      # 38,75
    theo_dau = (2.0 + 100.0) / 2                          # 51,00
    kiem("cả hai cơ hội đều được cấp đủ", kq.soCap == 2
         and gan(kq.tongCapUsd, 800.0), f"{kq.soCap} · {kq.tongCapUsd}")
    kiem("NET/giờ bình quân tính THEO VỐN, không theo đầu cơ hội",
         kq.netMoiGioBinhQuanBps is not None
         and gan(kq.netMoiGioBinhQuanBps, theo_von, 0.01),
         f"đang {kq.netMoiGioBinhQuanBps} · theo vốn {theo_von} · "
         f"theo đầu cơ hội {theo_dau} — rót $300 vào cơ hội 100 bps không "
         f"kéo cả danh mục lên ngang nó")

    kiem("kết quả khai thẳng là KHÔNG mô phỏng vòng đời",
         kq.tom_tat()["moPhongVongDoi"] is False)
    kiem("và khai thẳng hai thứ không đo được",
         "lãi lỗ" in kq.tom_tat()["khongDoDuoc"])

    # ── chưa đủ mẫu thì KHÔNG kết luận ──────────────────────────────────
    it = doi_chieu(lo, {}, {}, 10000.0)
    kiem("dưới ngưỡng mẫu thì từ chối kết luận",
         it["duDeKetLuan"] is False and str(TOI_THIEU_MAU) in it["vi"])

    # ── cùng tham số thì phải HOÀ ───────────────────────────────────────
    nhieu = [_mau(taiSan=f"T{i}", von=100.0, chua=9000.0, net=6.0 + i * 0.1,
                  giu=8.0,
                  chan=(Chan("LONG", "hyperliquid", f"T{i}"),
                        Chan("SHORT", "binance", f"T{i}")))
             for i in range(30)]
    hoa = doi_chieu(nhieu, {}, {}, 5000.0)
    kiem("cùng một bộ tham số thì kết luận HOÀ",
         hoa["duDeKetLuan"] and hoa["ketLuan"] == "hoa",
         str(hoa.get("ketLuan")) + " · " + str(hoa.get("vi"))[:70])

    # ── ĐÂY là phép kiểm quan trọng nhất của cả file ────────────────────
    # Nới hết mọi trần thì luôn rót được nhiều hơn. Nếu máy chấm đó là
    # "tốt hơn" thì vòng tiến hoá sẽ học đúng một bài: tự tháo phanh.
    # Năm cơ hội RẤT tốt dồn trên một cặp cảng, hai lăm cơ hội tầm thường
    # rải khắp nơi. Nới trần một cơ hội thì vốn dồn vào năm cái tốt: NET/giờ
    # bình quân TĂNG THẬT, và độ tập trung cũng tăng theo. Đây đúng là hình
    # dạng mà một vòng tiến hoá tham lam sẽ tưởng là "tiến bộ".
    dam = ([_mau(taiSan=f"TOT{i}", von=1500.0, chua=90000.0, net=160.0,
                 giu=8.0,
                 chan=(Chan("LONG", "hyperliquid", f"TOT{i}"),
                       Chan("SHORT", "binance", f"TOT{i}")))
            for i in range(5)]
           + [_mau(taiSan=f"THG{i}", von=1500.0, chua=90000.0, net=8.0,
                   giu=8.0,
                   chan=(Chan("LONG", f"okx{i}", f"THG{i}"),
                         Chan("SHORT", f"bybit{i}", f"THG{i}")))
              for i in range(25)])
    tp = doi_chieu(dam, {"ruiRoTong": {"tranMotCoHoi": 0.02}},
                   {"ruiRoTong": {"tranMotCoHoi": 0.30}}, 5000.0)
    kiem("nới trần khiến NET/giờ bình quân TĂNG THẬT",
         tp["lechNetMoiGioBps"] is not None and tp["lechNetMoiGioBps"] > 1.0,
         f"lệch {tp.get('lechNetMoiGioBps')}")
    kiem("và độ tập trung cũng tăng theo",
         tp["damHon"] is True,
         f"cảng {tp['A']['dayNhatCangUsd']} → {tp['B']['dayNhatCangUsd']}")
    kiem("nên KHÔNG được chấm là cải thiện",
         tp["ketLuan"] == "b-tot-hon-NHUNG-dam-hon",
         f"kết luận đang là {tp['ketLuan']} — chấm 'b-tot-hon' ở đây là dạy "
         f"vòng tiến hoá rằng đường lên điểm là tự tháo phanh")
    kiem("và nói rõ đây là ĐỔI rủi ro lấy lợi suất",
         "rủi ro lấy lợi suất" in tp["vi"], tp["vi"][:70])

    # Ngược lại: hơn mà KHÔNG tập trung hơn thì mới là cải thiện thật.
    deu = [_mau(taiSan=f"D{i}", von=200.0, chua=90000.0, net=8.0 + i, giu=8.0,
                chan=(Chan("LONG", f"okx{i}", f"D{i}"),
                      Chan("SHORT", f"bybit{i}", f"D{i}")))
           for i in range(30)]
    sach = doi_chieu(deu, {"phanBo": {"toiDaSoViThe": 4}},
                     {"phanBo": {"toiDaSoViThe": 30}}, 20000.0)
    kiem("hơn mà không tập trung hơn thì mới gọi là cải thiện",
         sach["ketLuan"] in ("b-tot-hon", "a-tot-hon", "hoa")
         and sach["damHon"] is False,
         f"{sach['ketLuan']} · đậm hơn={sach['damHon']}")

    # ── trần nào chặn nhiều nhất — câu trả lời cho 'nới cái nào' ────────
    chat = doi_chieu(nhieu, {"ruiRoTong": {"tranMotCang": 0.05}}, {}, 5000.0)
    kiem("đếm được trần nào chặn nhiều nhất",
         bool(chat["A"]["tranChanNhieuNhat"]),
         str(chat["A"]["tranChanNhieuNhat"])[:80])

    # ── _dat_nut phải trả BẢN SAO ──────────────────────────────────────
    g = {"ruiRoTong": {"tranMotCang": 0.35}}
    m = _dat_nut(g, "ruiRoTong.tranMotCang", 0.50)
    kiem("_dat_nut không sửa bản gốc",
         gan(g["ruiRoTong"]["tranMotCang"], 0.35)
         and gan(m["ruiRoTong"]["tranMotCang"], 0.50),
         "sửa tại chỗ thì A và B dùng chung một dict, và phép so luôn nói "
         "'có tiến bộ'")

    # ── thu hoạch từ sổ thật, và vòng học có ĐO ─────────────────────────
    class TyNhieu(Ty):
        ma, ho, moTa = "perpetual.funding_spread.v1", "phai-sinh", "nhiều"
        def __init__(self): super().__init__(); self.i = 0
        def quet(self): self.i += 1; return [f"T{self.i}"]
        def xet(self, co): return True, []
        def trinh(self, co):
            return _mau(taiSan=co, von=100.0, chua=9000.0, net=6.0,
                        chan=(Chan("LONG", "hyperliquid", co),
                              Chan("SHORT", "binance", co)))

    tu = TrungUong(_tam("clh"), {"vonBanDauUsd": 5000.0})
    tu.dang_ky(TyNhieu())
    for _ in range(25):
        tu.mot_vong(lechDongHoGiay=1.0, cangChet=[], tuoiXauNhatGiay=1.0)
    tt, hong = thu_hoach(tu.so_dang_ky)
    kiem("thu hoạch đọc lại được tờ trình từ sổ", len(tt) == 25 and hong == 0,
         f"{len(tt)} tờ, {hong} hỏng")
    kiem("và chúng dựng lại đủ để chạy lại",
         mot_luot(tt, {}, 5000.0, "x").soCap > 0)


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
    kiem_cua_that()
    kiem_von_chua_hieu_luc()
    kiem_khai_phi_thieu()
    kiem_hop_dong()
    kiem_rui_ro_chua_do()
    kiem_so_sanh_lien_ty()
    kiem_suc_chua()
    kiem_adapter_ty()
    kiem_chieu_phu_thuoc()
    kiem_so_cai()
    kiem_danh_muc()
    kiem_rui_ro_tong()
    kiem_phan_bo()
    kiem_so_dang_ky()
    kiem_cau_dao()
    kiem_thuc_thi()
    kiem_khuon_ty()
    kiem_trung_uong_vong()
    kiem_hai_ty_khac_nganh()
    kiem_chan_doan_he()
    kiem_chong_trung()
    kiem_chay_lai_he()

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
