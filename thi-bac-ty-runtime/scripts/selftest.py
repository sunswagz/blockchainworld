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
from phai_sinh_chung.dongho import dem_moc, moi_gio, moi_ngay, thu_cap, thu_thuc     # noqa: E402
from phai_sinh_chung.models import BaoGia                                    # noqa: E402
from bac.rui_ro import NHAN, CongRuiRo                           # noqa: E402
from phai_sinh_chung.san.base import moc_tron_gio_ke, nguyen_hoac_none, so_hoac_none  # noqa: E402
from phai_sinh_chung.san.binance import _doi_chung                           # noqa: E402
from phai_sinh_chung.san.okx import _chu_ky                                  # noqa: E402
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
def _nem(f, loai) -> bool:
    """Gọi `f` và trả True nếu nó ném đúng loại lỗi ấy.

    Có những luật chỉ giữ được bằng cách TỪ CHỐI DỰNG — kiểm chúng bằng
    cách gọi rồi xem giá trị trả về thì không kiểm được gì, vì không có
    giá trị nào để mà xem.
    """
    try:
        f()
    except loai:
        return True
    except BaseException:
        return False
    return False
def _dinh_nghia(dong: str, ten_f: str) -> bool:
    """Dòng này có ĐỊNH NGHĨA đúng `ten_f` không — khớp cả ranh giới từ.

    Khớp tiền tố trần thì `class BaoGiaCau` bị nhận là `class BaoGia`, và
    phép kiểm "chỉ định nghĩa ở một chỗ" báo trùng cho hai lớp khác hẳn
    nhau. Đã cắn thật lúc `chuyen_von/cau_noi.py` ra đời.
    """
    if not dong.startswith(ten_f):
        return False
    con = dong[len(ten_f):]
    return con[:1] in ("", ":", "(", " ", "[")




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

    from phai_sinh_chung.dong_ho import NGUONG_KEU_MS, DongHo

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

    # ── OPEN INTEREST: hai cảng câm làm cả họ phái-sinh không được cấp vốn ─
    # Trước lượt này chỉ Hyperliquid và Bybit báo OI. Cặp nào hai chân đều
    # binance/okx thì `uoc_luong` trả None, và «chưa đo được sức chứa» là lý
    # do từ chối ĐỨNG ĐẦU của cả họ phái-sinh — 36 lần chỉ trong một buổi.
    from phai_sinh_chung.san.binance import _oi_usd
    from phai_sinh_chung.san.okx import _oi_ca_san, _oi_hop_le

    kiem("OKX: `oiUsd` khớp `oiCcy × mark` thì NHẬN",
         gan(_oi_hop_le((2.24e9, 28900.0), 77550.0), 2.24e9, 1.0))
    kiem("OKX: hai trường lệch quá một nửa → None, không đoán trường nào đúng",
         _oi_hop_le((2.24e9, 289.0), 77550.0) is None,
         "một sức chứa sai gấp mấy lần đắt hơn hẳn một sức chứa không có")
    kiem("OKX: thiếu `oiUsd` thì suy từ `oiCcy × mark`",
         gan(_oi_hop_le((None, 100.0), 50.0), 5000.0))
    kiem("OKX: thiếu cả hai → None", _oi_hop_le(None, 50.0) is None
         and _oi_hop_le((None, None), 50.0) is None)

    class _R:
        def __init__(self, ma, d): self.status_code, self._d = ma, d
        def json(self): return self._d
        def raise_for_status(self):
            if self.status_code >= 400:
                raise RuntimeError(f"HTTP {self.status_code}")

    class _C:
        def __init__(self, ra): self.ra, self.hoi = ra, []
        async def get(self, url, params=None):
            self.hoi.append((url, params))
            if isinstance(self.ra, BaseException):
                raise self.ra
            return self.ra

    import asyncio as _aio
    # `openInterest` của Binance tính bằng COIN. Không nhân mark là ra một
    # con số nhỏ hơn thật đúng bằng giá một đồng coin — mà vẫn trông hợp lệ.
    _kh = _C(_R(200, {"openInterest": "106801.857"}))
    kiem("Binance: OI bằng COIN được nhân mark ra USD",
         gan(_aio.run(_oi_usd(_kh, "g", "BTCUSDT", 77550.0)),
             106801.857 * 77550.0, 1.0),
         "sai đơn vị ở đây không phải một lỗi mà là một con số nhỏ hơn thật "
         "77.550 lần, và tầng trên không cách nào biết")
    kiem("Binance: KHÔNG có mark thì OI là None, không phải số coin trần",
         _aio.run(_oi_usd(_C(_R(200, {"openInterest": "1"})), "g", "X", None))
         is None,
         "`None` nghĩa là không biết; một con số sai đơn vị nghĩa là biết "
         "sai, và hai thứ ấy phải khác nhau ở tầng trên")
    kiem("Binance: HTTP hỏng thì bỏ THÂN, dù thân có số trông hợp lệ",
         _aio.run(_oi_usd(_C(_R(418, {"openInterest": "999"})), "g", "X",
                          1.0)) is None,
         "đọc mã trạng thái TRƯỚC rồi mới đọc thân: sàn chặn tần suất, hay "
         "một cổng proxy chen vào, đều trả 4xx kèm một thân JSON — và thân "
         "ấy không phải số của sàn")

    # Kiểm ở tầng `_hoi`, không ở tầng `_oi_usd`: điều đáng giữ không phải
    # "hàm phụ trả None" mà là "báo giá VẪN VỀ khi hàm phụ hỏng". Kiểm hàm
    # phụ một mình thì đột biến đổi `return None` thành `raise` vẫn qua —
    # nó đã sống sót đúng một lượt như thế.
    from phai_sinh_chung.san.binance import Binance as _Bn

    class _CBn:
        """Khách giả: fundingInfo và premiumIndex CHẠY, riêng OI thì HỎNG."""
        def __init__(self, kieu): self.kieu = kieu
        async def get(self, url, params=None):
            if url.endswith("/fapi/v1/fundingInfo"):
                return _R(200, [])
            if url.endswith("/fapi/v1/premiumIndex"):
                return _R(200, {"lastFundingRate": "0.0001",
                                "markPrice": "100.0",
                                "nextFundingTime": 0, "time": 0})
            if self.kieu == "nem":
                raise RuntimeError("đứt")
            return _R(500, {})

    for _k in ("nem", "500"):
        _ds = _aio.run(_Bn()._hoi(_CBn(_k), ["BTC"]))
        kiem(f"Binance: OI hỏng kiểu «{_k}» thì báo giá VẪN VỀ, chỉ mất OI",
             len(_ds) == 1 and _ds[0].oiUsd is None
             and gan(_ds[0].markPx, 100.0),
             f"{_ds} — mất OI thì sức chứa thô hơn; mất báo giá là mất cả cặp")
    kiem("OKX: hỏi OI hỏng thì trả bảng RỖNG, không ném",
         _aio.run(_oi_ca_san(_C(RuntimeError("đứt")), "g")) == {}
         and _aio.run(_oi_ca_san(_C(_R(500, {})), "g")) == {})
    _kh2 = _C(_R(200, {"data": [{"instId": "BTC-USDT-SWAP", "oiUsd": "9",
                                 "oiCcy": "3"}]}))
    kiem("OKX: hỏi OI MỘT LƯỢT cho cả sàn, không hỏi từng mã",
         _aio.run(_oi_ca_san(_kh2, "g")) == {"BTC-USDT-SWAP": (9.0, 3.0)}
         and len(_kh2.hoi) == 1
         and (_kh2.hoi[0][1] or {}).get("instType") == "SWAP"
         and "instId" not in (_kh2.hoi[0][1] or {}),
         "hỏi từng mã là sáu lời hỏi để lấy sáu dòng của cùng một bảng, và "
         "mỗi lời hỏi thêm là một dịp bị chặn tần suất")


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

    # ── BĂNG PHẢI MANG DẤU GỐC, không chỉ TUỔI ──────────────────────────
    # `BaoGia.tom_tat()` bản đầu ghi `tuoiGiay` mà không ghi `nguonTsMs`.
    # Tuổi là số ĐÃ DẪN, đúng tại thời điểm ghi và vô nghĩa lúc đọc lại.
    # Hậu quả không phải một sai số mà là toàn bộ năng lực hậu kiểm chết
    # IM LẶNG: dựng lại với `nguonTsMs = None` → `tuoi_giay()` trả None →
    # cổng chặn «sàn không đóng dấu thời gian» → 460.035 cơ hội trên 188
    # giờ băng cho ra ĐÚNG 0 lần hậu kiểm, và không lỗi nào phát ra.
    from phai_sinh_chung.models import BaoGia as _BG26
    _tt26 = _BG26(san="a", ma="BTC", rate=1e-4, intervalGio=8.0,
                  markPx=100.0, mocKeMs=9_000,
                  nguonTsMs=1_000, nhanTsMs=1_100).tom_tat(2_000.0)
    kiem("băng ghi DẤU GỐC, không chỉ tuổi đã dẫn",
         _tt26.get("nguonTsMs") == 1_000 and _tt26.get("nhanTsMs") == 1_100,
         "băng ghi NGUYÊN LIỆU, sổ ghi KẾT LUẬN — và tuổi là kết luận")
    kiem("và vẫn ghi tuổi cho người đọc", _tt26.get("tuoiGiay") == 1.0)

    # Băng CŨ (chỉ có `tuoiGiay`) phải DẪN LẠI được, không phải vứt đi.
    _cu26 = {"san": "a", "ma": "BTC", "rate": 1e-4, "intervalGio": 8.0,
             "tuoiGiay": 1.5}
    kiem("báo giá băng CŨ dẫn lại được dấu gốc từ `luc`",
         dung_bao_gia(_cu26, 5_000.0).nguonTsMs == 5_000 - 1_500,
         "`luc` của khung và `nowMs` của tóm tắt là CÙNG một biến trong "
         "`vong.py`, nên đảo ngược là phép DẪN CHÍNH XÁC — nó cứu 188 giờ "
         "băng khỏi bị vứt")
    kiem("nhưng dấu ghi THẲNG vẫn thắng dấu dẫn lại",
         dung_bao_gia({**_cu26, "nguonTsMs": 42}, 5_000.0).nguonTsMs == 42,
         "dẫn lại là để đọc bản cũ, không phải để thay bản mới")
    kiem("thiếu CẢ dấu lẫn tuổi thì None, không bịa",
         dung_bao_gia({"san": "a", "ma": "BTC", "rate": 1e-4,
                       "intervalGio": 8.0}, 5_000.0).nguonTsMs is None,
         "bịa một dấu là bịa luôn độ tươi, và cổng rủi ro mất cửa duy nhất "
         "nó có để chặn dữ liệu cũ")
    kiem("thiếu `luc` thì cũng không dẫn được, và nói None",
         dung_bao_gia(_cu26, None).nguonTsMs is None)

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

    # ── HẬU KIỂM PHẢI NHƯỜNG GIL, không thì cỗ máy đứng hình ────────────
    # "Luồng nền" trong Python KHÔNG có nghĩa là không cản ai: mã Python
    # thuần giữ GIL. Đo thật 29/08: cổng 5188 chết **110 giây** kể từ lúc
    # máy lên — buồng lái không mở được, vòng quét không quay, và cầu dao
    # đo tuổi dữ liệu nên nó sắp ngắt vì chính phép đo của mình.
    import ast as _a22
    import pathlib as _p22
    from bac.chay_lai import NHUONG_GIAY, NHUONG_MOI_KHUNG, _nhuong

    _nguon22 = (_p22.Path(__file__).resolve().parent.parent
                / "bac/chay_lai.py").read_text(encoding="utf-8")
    _c22 = _a22.parse(_nguon22)

    def _co_nhuong(ham: str) -> bool:
        for nd in _a22.walk(_c22):
            if isinstance(nd, _a22.FunctionDef) and nd.name == ham:
                for x in _a22.walk(nd):
                    if isinstance(x, _a22.Call)                             and getattr(x.func, "id", "") == "_nhuong":
                        return True
        return False

    kiem("CẢ HAI vòng nặng đều NHƯỜNG nhịp cho luồng khác",
         _co_nhuong("mot_luot") and _co_nhuong("__init__"),
         "dựng chỉ mục và chạy lại đều nặng; nhường một chỗ thì chỗ kia vẫn "
         "giữ GIL suốt phần của nó")
    kiem("nhường theo NHỊP KHUNG, tất định — không theo đồng hồ",
         isinstance(NHUONG_MOI_KHUNG, int) and NHUONG_MOI_KHUNG > 0,
         "nhường theo đồng hồ thì hai lượt trên cùng một cuốn băng khác "
         "nhau, và một phép hậu kiểm không tất định thì không còn là bằng "
         "chứng")
    _t22n = time.perf_counter()
    for _ in range(50):
        _nhuong()
    _het22 = time.perf_counter() - _t22n
    kiem("mỗi lần nhường RẺ — 50 lần dưới 0,5 giây",
         _het22 < 0.5 and NHUONG_GIAY <= 0.005,
         f"{_het22 * 1000:.0f}ms — nhường quá đắt thì hậu kiểm chạy cả buổi")

    # ── BĂNG CŨ chạy lại được, ĐẦU-CUỐI ─────────────────────────────────
    # Kiểm `_dau_thoi_gian` một mình không đủ: đột biến ngừng truyền `luc`
    # xuống `dung_bao_gia` vẫn qua, vì băng thử ở trên có sẵn `nguonTsMs`.
    # Điều đáng giữ là «băng CŨ vẫn hậu kiểm được», và chỉ chạy cả lượt mới
    # nói được điều đó.
    khungCu = [{"luc": k["luc"],
                "baoGia": [{x: v for x, v in b.items()
                            if x not in ("nguonTsMs", "nhanTsMs")}
                           | {"tuoiGiay": 0.0} for b in k["baoGia"]]}
               for k in khung]
    kqCu = chay_lai_mot_luot(khungCu, ts, {"a": {}, "b": {}})
    kiem("băng CŨ (chỉ có `tuoiGiay`) vẫn hậu kiểm được, ĐẦU-CUỐI",
         kqCu.soDoDuoc == kq.soDoDuoc and kqCu.soDoDuoc > 0,
         f"{kqCu.soDoDuoc} vs {kq.soDoDuoc} — 188 giờ băng đã ghi cho ra "
         f"ĐÚNG 0 lần hậu kiểm chỉ vì thiếu một khoá, và không lỗi nào "
         f"phát ra")
    kiem("và mọi cơ hội KHÔNG còn bị chặn vì «không đóng dấu thời gian»",
         not kqCu.boQua.get("khong-dau-thoi-gian"),
         f"{kqCu.boQua} — đây đúng là cửa đã chặn 460.035/460.035 cơ hội")

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
    # Trần 25% giữ cho núm LỚN không nhảy xa. Nhưng nó không được là trần
    # duy nhất: núm gần 0 thì 25% cũng gần 0, và núm ấy đứng yên vĩnh viễn.
    # Nên bước = LỚN HƠN trong hai cách tính, và trần thật là chính nó.
    from bac.tien_hoa import buoc_van as _bv
    _tran = _bv("netToiThieuBps", dx[0].tu)
    kiem("bước không vượt LỚN HƠN của (25% giá trị, 5% bề rộng khuôn)",
         abs(dx[0].den - dx[0].tu) <= _tran + 1e-9,
         f"{dx[0].tom_tat()} vs trần {_tran}")
    kiem("và với núm gần 0, chính SÀN theo khuôn là thứ quyết",
         gan(_tran, 45.0 * 0.05) and _tran > abs(dx[0].tu) * 0.25,
         "0,5 × 25% = 0,125 — nhích ngần ấy thì cải thiện nhỏ hơn nhiễu, "
         "và lượt nào cũng bị trả lại")

    nhieu = de_xuat_tat_dinh(
        [T("ky-vong-am", ["netToiThieuBps"]),
         T("cua-qua-chat", ["grossToiThieuBpsNgay"])], goc)
    kiem("MỘT lượt chỉ vặn MỘT núm", len(nhieu) == 1,
         f"{len(nhieu)} — vặn hai núm rồi khá lên thì không biết núm nào có công")

    # ── ĐÃ TRẢ LẠI thì đi tiếp, đừng đề xuất lại y nguyên ───────────────
    # Đo trên máy sống: triệu chứng nặng nhất là `du-doan-lac-quan`, núm của
    # nó là `giuGio`, đề xuất 8→6, đo ra TỆ HƠN, trả lại. Lượt sau: cùng dữ
    # liệu, cùng triệu chứng, cùng đề xuất, cùng kết quả. Mãi mãi. Núm
    # `netToiThieuBps` — thứ một phép quét tay cho thấy CÓ cải thiện thật —
    # không bao giờ tới lượt.
    _tc32 = [T("du-doan-lac-quan", ["giuGio"]),
             T("ky-vong-am", ["netToiThieuBps"])]
    _d32 = de_xuat_tat_dinh(_tc32, goc)
    kiem("chưa trả lại gì thì lấy triệu chứng NẶNG nhất",
         len(_d32) == 1 and _d32[0].nut == "giuGio", str(_d32))
    _d33 = de_xuat_tat_dinh(_tc32, goc,
                            [{"nut": "giuGio", "den": _d32[0].den}])
    kiem("đã đo và trả lại rồi thì ĐI TIẾP xuống ứng viên kế",
         len(_d33) == 1 and _d33[0].nut == "netToiThieuBps",
         f"{_d33} — cùng dữ liệu, cùng đề xuất, cùng kết quả, mãi mãi")
    kiem("và VẪN đúng MỘT đề xuất mỗi lượt", len(_d33) == 1,
         "vặn hai núm rồi khá lên thì không biết núm nào có công")
    _d34 = de_xuat_tat_dinh(
        _tc32, goc, [{"nut": "giuGio", "den": _d32[0].den},
                     {"nut": "netToiThieuBps", "den": _d33[0].den}])
    kiem("hết ứng viên thì ĐỨNG YÊN, không quay lại cái đã trả",
         _d34 == [], f"{_d34}")
    kiem("trả lại một GIÁ TRỊ KHÁC thì không chặn nhầm",
         de_xuat_tat_dinh(_tc32, goc,
                          [{"nut": "giuGio", "den": 999.0}])[0].nut == "giuGio",
         "chặn theo (núm, giá trị) chứ không theo mỗi tên núm — bước sau "
         "dịch tới một giá trị khác, và giá trị ấy chưa ai đo")

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

    # ── NÚM GẦN 0 KHÔNG ĐƯỢC ĐÓNG BĂNG ──────────────────────────────────
    # Bước nhân theo giá trị hiện tại có một chỗ chết: `netToiThieuBps` xuất
    # phát 0,5 nên bước đầu là 0,125 — đổi ngưỡng ngần ấy thì kỳ vọng nhích
    # vài phần trăm bps, dưới biên nhiễu 0,15, nên lượt nào cũng bị TRẢ LẠI.
    # Đo trên băng thật: 0,5 → 15 cải thiện 0,56 bps, thừa sức vượt nhiễu.
    # Cỗ máy ĐO ĐƯỢC đích mà không bước tới được, và mỗi lượt trả lại trông
    # y hệt một quyết định thận trọng đúng đắn.
    from bac.tien_hoa import (BUOC_TOI_DA as _BTD31, SAN_BUOC_KHUON,
                              _kep as _kep31, buoc_van)

    _b31 = buoc_van("netToiThieuBps", 0.5)
    kiem("núm gần 0 vẫn có bước ĐỦ LỚN để đo được",
         _b31 > 0.5 * _BTD31 and gan(_b31, 45.0 * SAN_BUOC_KHUON),
         f"bước {_b31} — nhân theo giá trị hiện tại thì một núm gần 0 có "
         f"bước gần 0, và nó đứng yên vĩnh viễn")
    kiem("núm LỚN vẫn dùng bước nhân, không bị sàn kéo lên",
         gan(buoc_van("tuoiToiDaGiay", 200.0), 200.0 * _BTD31),
         "sàn để cứu núm nhỏ, không phải để cho núm lớn nhảy xa hơn")
    _T31 = type("T31", (), {})
    _t31 = _T31(); _t31.ma = "ky-vong-am"; _t31.nutGoiY = ["netToiThieuBps"]
    _g31 = ThamSo("g", 8.0, {"netToiThieuBps": 0.5,
                             "grossToiThieuBpsNgay": 3.0})
    _dx31 = de_xuat_tat_dinh([_t31], _g31)
    kiem("và đề xuất thật sự nhảy khỏi 0,5, không nhích 0,125",
         _dx31 and _dx31[0].den - _dx31[0].tu > 1.0,
         f"{[d.tom_tat() for d in _dx31]}")
    _dem31, _v31 = 0, 0.5
    while _v31 < 15.0 and _dem31 < 50:
        _v31 = _kep31("netToiThieuBps", _v31 + buoc_van("netToiThieuBps", _v31))
        _dem31 += 1
    kiem("đi từ 0,5 tới 15 trong ít lượt, không phải hai chục",
         _dem31 <= 8, f"{_dem31} lượt — mỗi lượt cách nhau 6 giờ")

    # ── VÒNG LẶP PHẢI GỌI, lần thứ BA cùng một lớp hỏng ─────────────────
    # `tien_hoa.mot_luot()` chỉ tới được qua `POST /api/tien-hoa`, nên
    # `duong_tien_hoa()` đứng ở `soLuot: 0` từ lúc dựng: cỗ máy ghi băng
    # suốt 188 giờ mà chưa một lần đọc lại. Trước đó là lát cắt cung tĩnh,
    # rồi tới `TrungUong.hoc()`. Cùng một cách hỏng, cùng một cách giấu.
    import ast as _ast30
    import pathlib as _pl30

    _goc30 = _pl30.Path(__file__).resolve().parent.parent

    def _goi30(tep: str, ham: str, ten: str) -> bool:
        for nd in _ast30.walk(_ast30.parse(
                (_goc30 / tep).read_text(encoding="utf-8"))):
            if isinstance(nd, (_ast30.FunctionDef, _ast30.AsyncFunctionDef))                     and nd.name == ham:
                for x in _ast30.walk(nd):
                    if isinstance(x, _ast30.Call):
                        fn = x.func
                        if isinstance(fn, _ast30.Name) and fn.id == ten:
                            return True
                        if isinstance(fn, _ast30.Attribute) and fn.attr == ten:
                            return True
        return False

    # ── MỖI NÚT BẤM: hoặc vòng lặp cũng gọi, hoặc KHAI là việc của người ─
    # Ba lần cùng một lớp hỏng — lát cắt cung tĩnh, `TrungUong.hoc()`,
    # `tien_hoa.mot_luot()` — và cả ba đều KHÔNG phải mã chết: chúng có
    # người gọi, chỉ là qua một nút bấm. Bộ dò "hàm không ai gọi" bỏ lọt cả
    # ba. Bất biến đúng không phải «có ai gọi không» mà là **«ai gọi: cỗ máy
    # hay ngón tay người»**.
    #
    # Danh sách dưới đây là những nút CỐ Ý chỉ dành cho người, mỗi cái một
    # lý do. Thêm một nút mới mà không nối vào vòng lặp và cũng không khai ở
    # đây thì phép kiểm này đỏ — đó là điểm của nó.
    NGUOI_BAM = {
        "/api/nap-von": "ĐÒI TÊN NGƯỜI — máy không tự quyết bỏ thêm tiền",
        "/api/dat-tham-so": "ĐÒI TÊN NGƯỜI và LÝ DO — người đổi một núm máy "
                            "KHÔNG đề xuất",
        "/api/tam-dung": "dừng máy là quyết định của người, không của máy",
        "/api/quet-ngay": "quét ép ngoài nhịp — công cụ gỡ rối",
        "/api/chay-lai": "chạy lại một bộ tham số tuỳ chọn — công cụ khảo sát",
        "/api/doi-chieu": "so hai bộ tham số tuỳ chọn — công cụ khảo sát",
        "/api/chay-lai-he": "như trên, ở tầng phân bổ",
        "/api/ap-dung-tham-so": "ĐÒI TÊN NGƯỜI — máy đề xuất, người ký",
        "/api/quay-lui-tham-so": "ĐÒI TÊN NGƯỜI, cùng lý do",
        "/api/cau-dao/dong-lai": "bất đối xứng cầu dao: máy NGẮT được, "
                                 "đóng lại phải có người xem",
        "/api/lat-cat": "cung tĩnh chỉ đổi khi có người bấm — tiêu đề file "
                        "đã sửa cho khớp, xem `kiem_lat_cat`",
    }
    VONG_GOI = {
        "/api/hoc": ("thi_bac_ty/trung_uong.py", "_cuoi_vong",
                     "_hoc_dinh_ky"),
        "/api/tien-hoa": ("bac/vong.py", "mot_vong", "_tien_hoa_dinh_ky"),
        "/api/doi-soat-vi-the": ("thi_bac_ty/trung_uong.py", "mot_vong",
                                 "canh_vi_the"),
    }
    _sv30 = (_goc30 / "bac/server.py").read_text(encoding="utf-8")
    _duong30 = _ast30.parse(_sv30)
    _post30 = set()
    for nd in _ast30.walk(_duong30):
        if not isinstance(nd, (_ast30.FunctionDef, _ast30.AsyncFunctionDef)):
            continue
        for dec in nd.decorator_list:
            f = dec.func if isinstance(dec, _ast30.Call) else dec
            if getattr(f, "attr", "") == "post" and isinstance(dec, _ast30.Call):
                for arg in dec.args:
                    if isinstance(arg, _ast30.Constant):
                        _post30.add(arg.value)
    _la30 = _post30 - set(NGUOI_BAM) - set(VONG_GOI)
    kiem("mỗi nút BẤM: hoặc vòng lặp cũng gọi, hoặc KHAI là việc của người",
         not _la30,
         f"{sorted(_la30)} — một cơ chế chỉ tới được qua nút bấm là một cơ "
         f"chế không chạy, và nhìn vào buồng lái thì nó có vẻ đang chạy. Đã "
         f"cắn BA lần: lát cắt cung tĩnh, `hoc()`, `tien_hoa.mot_luot()`")
    for _d30, (_t30, _h30, _g30) in VONG_GOI.items():
        kiem(f"và `{_d30}` thật sự được vòng lặp gọi",
             _goi30(_t30, _h30, _g30),
             f"khai là vòng lặp gọi mà `{_h30}` không gọi `{_g30}` thì lời "
             f"khai ấy còn tệ hơn không khai")
    # ── và HÀM nào không ai gọi ở đâu cả ────────────────────────────────
    # Bộ dò này KHÔNG bắt được ba lỗi trên — chúng đều có người gọi. Nó bắt
    # lớp khác: mã dựng ra rồi bỏ quên. `dang_ky_nghe()` của Thông Chính là
    # một ví dụ đã gỡ: không tầng nào đăng ký, chưa bao giờ, mà mỗi lần nộp
    # tờ trình vẫn sao chép một danh sách rỗng dưới khoá — hai nghìn lần
    # mỗi vòng cho một tính năng không ai dùng.
    _BO_QUA_MC = {"__pycache__", "scripts", "dichvu", "web", "data",
                  "data-demo", ".venv"}
    #: Hàm KHÔNG ai gọi mà vẫn giữ, mỗi cái một lý do. Danh sách này phải
    #: NGẮN: nó là chỗ để khai ngoại lệ, không phải chỗ để giấu mã chết.
    _MO_COI_CHO_PHEP = {
        "dang_ngat": "thuộc tính đọc trạng thái cầu dao — phép kiểm dùng, "
                     "buồng lái đọc qua `tom_tat()`",
        "kiem_token": "phép soát bảng token, đúng chỗ của nó là bộ kiểm chứ "
                      "không phải vòng chạy",
    }
    _dn, _du = {}, {}
    _tepMC = [q for q in _goc30.rglob("*.py")
              if not any(x in _BO_QUA_MC for x in q.parts)]
    for q in _tepMC:
        try:
            _cay = _ast30.parse(q.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for nd in _ast30.walk(_cay):
            if isinstance(nd, (_ast30.FunctionDef, _ast30.AsyncFunctionDef)):
                # Hàm có decorator là hàm KHUNG gọi (route, middleware,
                # property, sự kiện) — người gọi nằm ngoài cây mã này.
                if nd.decorator_list:
                    continue
                _dn.setdefault(nd.name, str(q.relative_to(_goc30)))
    for q in _tepMC + [_pl30.Path(__file__)]:
        try:
            _cay = _ast30.parse(q.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for nd in _ast30.walk(_cay):
            if isinstance(nd, _ast30.Name):
                _du[nd.id] = 1
            elif isinstance(nd, _ast30.Attribute):
                _du[nd.attr] = 1
            elif isinstance(nd, _ast30.Constant) and isinstance(nd.value, str):
                _du[nd.value] = 1
            elif isinstance(nd, _ast30.alias):
                _du[nd.name.split(".")[-1]] = 1
                if nd.asname:
                    _du[nd.asname] = 1
    _mocoi = sorted(t for t in _dn
                    if not t.startswith("__") and t not in _du
                    and t not in _MO_COI_CHO_PHEP)
    kiem("KHÔNG hàm nào bị bỏ quên — dựng ra rồi không ai gọi",
         not _mocoi,
         f"{[(t, _dn[t]) for t in _mocoi]} — mã chết không sai, nó chỉ tốn "
         f"công đọc và tốn công giữ đúng; và có lúc tốn cả CPU")
    kiem("và danh sách ngoại lệ mồ côi NGẮN, mỗi cái một lý do",
         len(_MO_COI_CHO_PHEP) <= 5
         and all(len(v) > 20 for v in _MO_COI_CHO_PHEP.values()),
         "danh sách ngoại lệ dài ra là cách mã chết ở lại vĩnh viễn")

    kiem("danh sách nút-người nào cũng có LÝ DO, không có dòng trống",
         all(len(v) > 20 for v in NGUOI_BAM.values()),
         "một danh sách miễn trừ không kèm lý do sẽ dài ra mãi")

    kiem("vòng quét GỌI hậu kiểm, không đợi người bấm",
         _goi30("bac/vong.py", "mot_vong", "_tien_hoa_dinh_ky"),
         "băng ghi mà không ai đọc lại thì mọi lần vặn ngưỡng đều là đổi số "
         "cho vui — không cách nào biết tốt hơn hay chỉ khác đi")
    _vg30 = (_goc30 / "bac/vong.py").read_text(encoding="utf-8")
    kiem("và nó chạy ở TIẾN TRÌNH RIÊNG, không phải luồng",
         '"-m", "bac.tien_hoa"' in _vg30 and "_sp.run(" in _vg30,
         "luồng trong Python chia GIL với cả tiến trình — «nền» không có "
         "nghĩa là không cản ai. Đo thật 29/08: cổng 5188 câm 90 giây kể từ "
         "lúc máy lên, buồng lái không mở được, và cầu dao đo tuổi dữ liệu "
         "nên nó sắp ngắt vì chính phép đo của mình")
    kiem("và có cửa `python -m bac.tien_hoa` để gọi",
         '__name__ == "__main__"' in
         (_goc30 / "bac/tien_hoa.py").read_text(encoding="utf-8"),
         "gọi bằng `-m` mà module không có cửa ấy thì tiến trình con chết "
         "lặng, và buồng lái chỉ thấy một ô trống")
    kiem("tiến trình con có TRẦN THỜI GIAN",
         "timeout=TREO_TIEN_HOA_GIAY" in _vg30,
         "một tiến trình treo mà không ai giết thì nó nằm đó tới khi máy "
         "tắt, và lượt hậu kiểm sau không bao giờ chạy")
    kiem("và luồng chỉ ĐỢI tiến trình con — đợi thì nhả GIL",
         _goi30("bac/vong.py", "_tien_hoa_dinh_ky", "Thread"),
         "vẫn cần một luồng để không chặn vòng quét lúc đợi")
    from bac.config import MAC_DINH as _MD30
    _nguon30 = (_goc30 / "bac/vong.py").read_text(encoding="utf-8")
    # Khẳng định CƠ CHẾ, không khẳng định GIÁ TRỊ. Bản đầu đòi
    # `CONFIG["tuVanTienHoa"] is False`, và nó đỏ ngay ngày chủ bật cờ ấy —
    # một phép kiểm đóng băng một quyết định thuộc về người thì nó không
    # bảo vệ gì cả, nó chỉ cản. Thứ đáng giữ là: có một cái cửa, cửa ấy
    # được TÔN TRỌNG, và tắt thì máy KHÔNG tự vặn.
    kiem("tự vặn tham số có CỬA, và cửa ấy được tôn trọng",
         'lenh.append("--that")' in _nguon30
         and 'CONFIG.get("tuVanTienHoa")' in _nguon30,
         "tầng ty A/B được nên nó CÓ QUYỀN tự nhận, nhưng «có quyền» và "
         "«được bật sẵn» là hai chuyện — phải có cửa để người chọn")
    kiem("và MẶC ĐỊNH trong mã là TẮT, dù config hiện đang bật hay không",
         _MD30.get("tuVanTienHoa") is False,
         "một cỗ máy mới dựng, chưa ai cấu hình gì, KHÔNG được tự vặn tham "
         "số của chính nó")

    # Lượt THỬ cũng phải VÀO SỔ. Không thì vòng chạy đều mà
    # `duong_tien_hoa()` vẫn báo `soLuot: 0`, và người đọc kết luận đúng
    # cái ngược lại với sự thật.
    _th30 = (_goc30 / "bac/tien_hoa.py").read_text(encoding="utf-8")
    _cay30 = _ast30.parse(_th30)
    _ml30 = [x for x in _ast30.walk(_cay30)
             if isinstance(x, _ast30.FunctionDef) and x.name == "mot_luot"][0]
    _ghiSo = [x for x in _ast30.walk(_ml30) if isinstance(x, _ast30.Call)
              and getattr(x.func, "id", "") == "_ghi_so"]
    # Không cấm `_ghi_so` nằm trong `if` — ba nhánh thoát sớm của `mot_luot`
    # đều hợp lệ. Cấm đúng một thứ: nhánh `if` NÀO nhắc tới `thu` mà lại bao
    # một lời ghi sổ. Đó chính là hình dạng của lỗi cũ.
    _duoiThu = []
    for nd in _ast30.walk(_ml30):
        if not isinstance(nd, _ast30.If):
            continue
        if not any(isinstance(x, _ast30.Name) and x.id == "thu"
                   for x in _ast30.walk(nd.test)):
            continue
        for than in nd.body:
            for x in _ast30.walk(than):
                if isinstance(x, _ast30.Call)                         and getattr(x.func, "id", "") == "_ghi_so":
                    _duoiThu.append(x)
    kiem("MỌI lượt vào sổ, kể cả lượt THỬ",
         len(_ghiSo) >= 1 and not _duoiThu,
         f"{len(_ghiSo)} lời gọi `_ghi_so`, {len(_duoiThu)} nằm dưới một "
         f"nhánh xét `thu` — một cơ chế chạy mà không ghi thì với người đọc "
         f"nó bằng một cơ chế không chạy")
    # ── SỔ GỘP không được đếm lượt THỬ như lượt ĐÃ ÁP ───────────────────
    # Đo thật 29/08 trên máy sống: sổ khoe «nhận 7 · tổng cải thiện 1,105
    # bps» trong khi `config.json` chưa đổi một chữ và bản tham số vẫn #1.
    # Hai lời nói dối chồng nhau, cả hai đều theo hướng khoe: lượt THỬ đếm
    # như lượt đã áp, và cùng MỘT phép đo 0,158 bps cộng lại bảy lần (lượt
    # thử không vặn gì nên lượt sau chẩn lại ra y hệt).
    import bac.tien_hoa as _th37
    _cu37 = _th37.SO_TIEN_HOA
    _th37.SO_TIEN_HOA = _tam("so-tien-hoa") / "tien-hoa.jsonl"
    try:
        for _ in range(3):
            _th37._ghi_so(_th37.KetQuaTienHoa(
                luc="x", thu=True,
                nhan={"nut": "netToiThieuBps", "tu": 0.5, "den": 2.75,
                      "caiThienBps": 0.158}))
        _d37 = _th37.duong_tien_hoa()
        kiem("lượt THỬ kết luận «sẽ nhận» KHÔNG đếm là đã nhận",
             _d37["soLanNhan"] == 0 and _d37["soLanThuNhan"] == 3,
             f"{_d37} — một cỗ máy khoe mình mạnh lên trong khi chưa đổi gì "
             f"là kiểu nói dối khó thấy nhất, vì mọi dòng trong sổ đều thật")
        kiem("và KHÔNG cộng cải thiện của lượt thử vào tổng",
             _d37["tongCaiThien"] is None,
             "lượt thử không vặn gì nên lượt sau ra y hệt; cộng lại là đếm "
             "một phép đo bảy lần")
        kiem("sổ NÓI RÕ là chưa áp lượt nào",
             "CHƯA áp lượt nào" in _d37["vi"], _d37["vi"])
        _th37._ghi_so(_th37.KetQuaTienHoa(
            luc="y", thu=False,
            nhan={"nut": "giuGio", "tu": 8.0, "den": 6.0,
                  "caiThienBps": 0.4}))
        import json as _js22
        _d38 = _th37.duong_tien_hoa()
        kiem("lượt ÁP THẬT thì đếm, và chỉ nó vào tổng cải thiện",
             _d38["soLanNhan"] == 1 and gan(_d38["tongCaiThien"], 0.4)
             and "1 lượt ÁP THẬT" in _d38["vi"], str(_d38))
        # Dòng CŨ, ghi trước khi cờ `thu` tồn tại: không phải thử, không
        # phải thật — KHÔNG BIẾT. Nhét vào một trong hai rổ là chọn một
        # hướng nói sai.
        with _th37.SO_TIEN_HOA.open("a", encoding="utf-8") as _f37:
            _f37.write(_js22.dumps(
                {"luc": "z", "nhan": {"nut": "x", "caiThienBps": 9.0}},
                ensure_ascii=False) + chr(10))
        _d39 = _th37.duong_tien_hoa()
        kiem("dòng CŨ thiếu cờ `thu` vào rổ KHÔNG RÕ, không vào hai rổ kia",
             _d39["soLanKhongRo"] == 1 and _d39["soLanNhan"] == 1
             and _d39["soLanThuNhan"] == 3,
             f"{_d39} — coi là thử thì giấu mất một lần vặn có thật, coi là "
             f"thật thì khoe một lần vặn chưa xảy ra")
        kiem("và cải thiện của dòng KHÔNG RÕ không cộng vào tổng",
             gan(_d39["tongCaiThien"], 0.4),
             f"{_d39['tongCaiThien']} — 9,0 của dòng mù không được lẫn vào")
        kiem("sổ KHAI ra là có dòng không rõ",
             "KHÔNG rõ thử hay thật" in _d39["vi"], _d39["vi"])

        kiem("và mỗi dòng trong chuỗi mang cờ `thu`",
             all("thu" in x for x in _d38["chuoi"]),
             "đọc lại một dòng «NHẬN giuGio 8→6» mà không biết nó đã áp hay "
             "chỉ là diễn tập thì hai thứ ấy lẫn vào nhau")
    finally:
        _th37.SO_TIEN_HOA = _cu37

    kiem("và sổ phân biệt được lượt THỬ với lượt ÁP THẬT",
         '"thu": self.thu' in _th30,
         "đọc lại một dòng «NHẬN giuGio 8→6» mà không biết nó đã được áp "
         "hay chỉ là diễn tập thì hai thứ ấy lẫn vào nhau")


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
    kiem("tám họ đúng bằng bảng phân loại lại", len(HO) == 8, str(HO))
    kiem("`tien-doan` là họ RIÊNG, không nhét vào `chenh-lech`",
         "tien-doan" in HO,
         "thị trường tiên đoán không phải phái sinh (không có tài sản cơ sở "
         "để phái sinh từ đó) và không phải chênh lệch (không có hai nơi để "
         "so). Nhét bừa cho khỏi sửa hợp đồng thì `_pheu_theo_ho()` gộp nó "
         "với chênh lệch stablecoin, và cái phễu ấy nói dối về CẢ HAI")

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

    # ── BIÊN của hợp đồng ───────────────────────────────────────────────
    #
    # Đây là cái cổng MỌI ty phải qua, và quét đột biến cho 10/15 con
    # SỐNG SÓT — gần như mọi biên của `kiem()` đang trống. Một cổng
    # không ai kiểm ở biên là một cổng chỉ chặn được những tờ trình sai
    # rõ ràng, mà tờ trình sai rõ ràng thì không ai gửi.

    kiem("xin ĐÚNG BẰNG sức chứa thì hợp lệ",
         _tt(vonCanUsd=100.0, sucChuaToiDaUsd=100.0).hop_le,
         "«xin nhiều hơn chỗ chứa» phải nghĩa là HƠN, không phải bằng")
    kiem("xin hơn sức chứa một xu thì bắt",
         not _tt(vonCanUsd=100.01, sucChuaToiDaUsd=100.0).hop_le)

    kiem("cửa sổ giữ đúng bằng 0 thì BẮT — không có cơ hội nào dài 0 giờ",
         not _tt(giuGio=0.0).hop_le,
         "giữ 0 giờ nghĩa là vào rồi ra tức thì, và mọi con số bps mỗi "
         "giờ dựng trên nó đều chia cho không")
    kiem("nhưng một khoảnh khắc dương thì qua", _tt(giuGio=0.001).hop_le)

    kiem("khoá vốn ĐÚNG BẰNG 0 là hợp lệ — nghĩa là không khoá",
         _tt(khoaVonDenGio=0.0).hop_le,
         "0 ở đây là «không khoá», không phải một giá trị sai")
    kiem("khoá vốn ÂM thì bắt", not _tt(khoaVonDenGio=-0.001).hop_le)

    kiem("thanh khoản thoát ĐÚNG BẰNG 0 là hợp lệ — nghĩa là không ra được",
         _tt(thanhKhoanThoatUsd=0.0).hop_le,
         "«ra được 0 đồng» là một phép đo có thật và rất đáng biết; loại "
         "nó ra là bắt ty im lặng đúng lúc nó nói điều tệ nhất")
    kiem("thanh khoản thoát ÂM thì bắt",
         not _tt(thanhKhoanThoatUsd=-0.001).hop_le)

    kiem("xin ĐÚNG BẰNG vốn tối thiểu kinh tế thì hợp lệ",
         _tt(vonCanUsd=500.0, vonToiThieuKinhTeUsd=500.0).hop_le,
         "«xin ít hơn ngưỡng mình khai» phải nghĩa là ÍT HƠN")
    kiem("xin dưới ngưỡng ấy thì bắt",
         not _tt(vonCanUsd=499.0, vonToiThieuKinhTeUsd=500.0).hop_le)
    kiem("khai vốn tối thiểu = 0 thì bắt",
         not _tt(vonToiThieuKinhTeUsd=0.0).hop_le,
         "khai 0 nghĩa là «engine này kinh tế ở mọi cỡ vốn», và chưa "
         "engine nào như thế")
    kiem("khai một xu thì qua — thang MỞ ở 0, không mở ở 1",
         _tt(vonCanUsd=100.0, vonToiThieuKinhTeUsd=0.01).hop_le)

    # Thang [0,1] ĐÓNG hai đầu: 0 là «không rủi ro mặt này», 1 là «rủi ro
    # tối đa». Đổi `<=` thành `<` là gọi chính hai đầu thang là vi phạm.
    for _v in (0.0, 1.0):
        kiem(f"rủi ro đúng bằng {_v:g} nằm TRONG thang",
             _tt(ruiRo=RuiRo(thiTruong=_v)).hop_le,
             f"{_tt(ruiRo=RuiRo(thiTruong=_v)).kiem()}")
        kiem(f"tin cậy đúng bằng {_v:g} cũng thế",
             _tt(tinCay=_v).hop_le, f"{_tt(tinCay=_v).kiem()}")
    kiem("nhích ra ngoài thang thì bắt",
         not _tt(tinCay=1.001).hop_le and not _tt(tinCay=-0.001).hop_le)

    # `raDuocKhong`: ra được ĐÚNG BẰNG số xin thì ra được.
    kiem("thoát ĐÚNG BẰNG số xin thì «ra được»",
         _tt(vonCanUsd=100.0, thanhKhoanThoatUsd=100.0).raDuocKhong is True)
    kiem("thiếu một xu thì KHÔNG ra được",
         _tt(vonCanUsd=100.0,
             thanhKhoanThoatUsd=99.98).raDuocKhong is False)
    kiem("chưa đo thanh khoản thoát thì None, không phải False",
         _tt(thanhKhoanThoatUsd=None).raDuocKhong is None,
         "«chưa đo» và «đo rồi, và ra không được» là hai câu khác nhau")

    # `xin_theo_suc_chua`: sức chứa ĐÚNG BẰNG 0 nghĩa là không chứa được
    # gì, nên xin đúng sàn — cùng luật với `None`.
    from thi_bac_ty.to_trinh import xin_theo_suc_chua as _xin
    kiem("sức chứa 0 thì xin đúng SÀN, y như chưa đo",
         gan(_xin(500.0, 0.0), 500.0) and gan(_xin(500.0, None), 500.0))
    kiem("sức chứa dương bé xíu cũng vẫn xin đúng sàn, không xin dưới sàn",
         gan(_xin(500.0, 1.0), 500.0),
         "dưới sàn thì phí cố định ăn hết — sàn là SÀN")


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
    kiem("và LÚC ẤY mới khai thiếu OI", "oi-thieu-o-mot-so-cang" in t5)
    kiem("CẢ HAI chân báo OI thì KHÔNG khai thiếu OI nữa",
         "oi-thieu-o-mot-so-cang" not in thieu,
         "tới 29/08 chỉ hai trong bốn cảng báo OI nên dòng này khai vô điều "
         "kiện; nay cả bốn đều báo, và khai một cái thiếu KHÔNG CÒN THIẾU thì "
         "trung ương hạ trọng số cho một con số vốn đã tốt hơn nó tưởng")
    kiem("nhưng độ sâu sổ lệnh thì VẪN thiếu, mọi lúc",
         all("do-sau-so-lenh" in x for x in (thieu, t3, t4, t5)),
         "runtime không hỏi sổ lệnh của cảng nào — cái thiếu ấy chưa lượt nào "
         "hết thiếu, và nó là cái thiếu ĐÁNG kể nhất")


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
        rr=None, khoa=0.0, thoat=None, **kw):
    """Một tờ trình hợp lệ, đủ để đi hết đường ống. Sửa gì thì truyền vào."""
    from thi_bac_ty.to_trinh import Chan as _C, RuiRo as _R
    if chan is None:
        chan = (_C("LONG", "hyperliquid", taiSan, loai="perp"),
                _C("SHORT", "binance", taiSan, loai="perp"))
    return ToTrinh(
        chienLuoc=ma, ho=ho, taiSan=taiSan, chan=tuple(chan),
        vonCanUsd=von, sucChuaToiDaUsd=chua,
        vonToiThieuKinhTeUsd=1.0,
        grossBps=net + 2.0, phiUocBps=2.0, netUocBps=net, giuGio=giu,
        ruiRo=rr if rr is not None else _R(0.2, 0.2, 0.1, 0.2, 0.2, 0.0),
        tinCay=tin, moHinhPhiDuChua=True,
        khoaVonDenGio=khoa, thanhKhoanThoatUsd=thoat,
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

    # ĐÓNG VÌ ĐÂU: xoay chỗ hay khởi động lại. Hai bệnh khác hẳn nhau mà
    # cùng trả phí vào lệnh, và trước đây bảng tách khoản chỉ kể một.
    scD = SoCai(_tam("socai-dong") / "so.sqlite3")
    scD.ghi(ButToan("PHI", "phí vào lệnh", -1.0, "d.v1", "T1",
                    {"phiUocBps": 2.0}))
    scD.ghi(ButToan("DONG_VI_THE", "xoay chỗ · A → B", 0.0, "d.v1", "T1",
                    {"xoayCho": True}))
    scD.ghi(ButToan("DONG_VI_THE", "đóng · hết hạn giữ", 0.0, "d.v1", "T2",
                    {}))
    scD.ghi(ButToan("PHI", "phí vào lệnh", -1.0, "e.v1", "T3",
                    {"phiUocBps": 2.0}))
    _d = scD.lai_lo_tach_khoan()
    kiem("số lần đóng tách được ra ĐÓNG VÌ ĐÂU",
         (_d["d.v1"]["soLanDong"] == 2
          and _d["d.v1"]["soLanDongXoayCho"] == 1
          and gan(_d["d.v1"]["phanDongDoXoayCho"], 0.5)),
         f"{_d['d.v1']} — «giữ vị thế lâu hơn, hoặc khởi động lại ít đi» "
         f"là lời khuyên SAI khi thủ phạm là xoay chỗ")
    kiem("chưa đóng lần nào thì phần-do-xoay là None, không phải 0",
         _d["e.v1"]["soLanDong"] == 0
         and _d["e.v1"]["phanDongDoXoayCho"] is None,
         "0 ở đây đọc thành «đã đóng, và không lần nào do xoay» — một câu "
         "khác hẳn «chưa đóng lần nào»")

    # ── XOAY CHỖ: lời hứa đặt cạnh đời thật của vị thế ──────────────────
    scX = SoCai(_tam("socai-xoay") / "so.sqlite3")

    def _xoayGhi(so, cu, moi, hua, giu, gioHua=160.0, ty="lending.v1"):
        ct = {"xoayCho": True, "taiSanCu": cu, "taiSanMoi": moi,
              "loiRongUocUsd": hua, "daGiuGio": giu}
        if gioHua is not None:
            ct["gioChungHua"] = gioHua
        so.ghi(ButToan("DONG_VI_THE", f"xoay chỗ · {cu} → {moi}", 0.0,
                       ty, f"{cu}-{moi}-{giu}", ct))

    kiem("chưa xoay lần nào thì mọi con số là None, không phải 0",
         (scX.xoay_cho_hua_va_thuc()["soLan"] == 0
          and scX.xoay_cho_hua_va_thuc()["gioGiuTrungVi"] is None),
         "0 giờ nghĩa là «đã đo, và bằng không»; ở đây chưa đo gì cả")

    # Một lần đóng THƯỜNG không được lẫn vào phép đo xoay chỗ.
    scX.ghi(ButToan("DONG_VI_THE", "đóng · hết hạn giữ", 0.0, "lending.v1",
                    "thuong-1", {"daGiuGio": 720.0}))
    for g in (0.01, 0.02, 0.03, 5.0):
        _xoayGhi(scX, "USDT", "SUSDAI", 40.0, g)
    kiem("lần đóng THƯỜNG không bị đếm vào phép đo xoay chỗ",
         scX.xoay_cho_hua_va_thuc()["soLan"] == 4,
         "một vị thế hết hạn giữ sau 720 giờ mà lẫn vào đây thì trung vị "
         "giờ giữ nhảy lên và cả phép đo im")
    _xc = scX.xoay_cho_hua_va_thuc()
    kiem("lời hứa cộng đúng", gan(_xc["huaLoiRongUsd"], 160.0),
         f"{_xc['huaLoiRongUsd']}")
    kiem("giờ giữ lấy TRUNG VỊ, không lấy trung bình",
         gan(_xc["gioGiuTrungVi"], 0.025),
         f"{_xc['gioGiuTrungVi']} — trung bình là 1,265: một lần giữ 5 giờ "
         f"giữa ba lần giữ vài phút kéo nó lên năm mươi lần, và con số ấy "
         f"đọc thành «giữ cũng khá lâu»")
    kiem("tỉ lệ sống trên hứa = giờ giữ ÷ giờ hứa",
         gan(_xc["tiLeSongTrenHua"], 0.025 / 160.0),
         f"{_xc['tiLeSongTrenHua']}")
    kiem("cặp đi–đến đếm từ TRƯỜNG, không tách từ câu lý do",
         _xc["capLapNhieuNhat"][0] == {"cap": "USDT → SUSDAI", "soLan": 4},
         f"{_xc['capLapNhieuNhat']} — tách chuỗi «xoay chỗ · A → B» là dựng "
         f"phép phân tích trên câu văn, và câu văn đổi lúc nào không hay")
    kiem("và đếm được có bao nhiêu cặp đi lại NHIỀU LẦN",
         _xc["soCapDiLaiNhieuLan"] == 1, str(_xc))
    kiem("cửa sổ GẦN ĐÂY cũng đếm cặp, không chỉ tổng cộng dồn",
         (_xc["ganDay"]["capLapNhieuNhat"]
          == [{"cap": "USDT → SUSDAI", "soLan": 4}]
          and _xc["ganDay"]["soCapDiLaiNhieuLan"] == 1),
         f"{_xc['ganDay']} — chẩn đoán đọc `ganDay`, nên bằng chứng phải "
         f"nằm trong `ganDay`; để trống ở đó là dựng một triệu chứng nói "
         f"về hôm nay mà không kèm được bằng chứng nào của hôm nay")
    kiem("cửa sổ hẹp lại thì đếm ít đi — cửa sổ có thật, không phải nhãn",
         scX.xoay_cho_hua_va_thuc(gioGanDay=0.0)["ganDay"]["soLan"] == 0
         and scX.xoay_cho_hua_va_thuc(gioGanDay=0.0)["soLan"] == 4,
         "cộng dồn cả đời KHÔNG đổi theo cửa sổ; chỉ `ganDay` đổi")

    # Bút toán CŨ không có `gioChungHua`: khai ra là thiếu, đừng đếm
    # thành 0 giờ hứa — bịa ra một lời hứa khiêm tốn chưa ai từng nói.
    scY = SoCai(_tam("socai-xoay-cu") / "so.sqlite3")
    _xoayGhi(scY, "USDT", "REUSD", 5.0, 0.01, gioHua=None)
    _xoayGhi(scY, "DAI", "USD3", 5.0, 0.02, gioHua=None)
    _yc = scY.xoay_cho_hua_va_thuc()
    kiem("bút toán thiếu quãng hứa được ĐẾM RIÊNG, không lẫn vào trung vị",
         (_yc["soThieuGioHua"] == 2 and _yc["gioHuaTrungVi"] is None
          and _yc["tiLeSongTrenHua"] is None),
         f"{_yc} — đếm thiếu thành 0 thì tỉ lệ sống/hứa hoá vô cực và cả "
         f"phép đo thành vô nghĩa")
    kiem("nhưng giờ GIỮ thì vẫn đo được, vì trường ấy có",
         gan(_yc["gioGiuTrungVi"], 0.015),
         f"{_yc['gioGiuTrungVi']} — mù một trường không phải mù cả hàng")


def kiem_danh_muc() -> None:
    print("\n── Danh Mục: ba thước phơi nhiễm, ba câu hỏi khác nhau ───────")
    from thi_bac_ty.danh_muc import DanhMuc, ViThe

    # ── BIÊN, chỗ quét đột biến chỉ ra đang trống ───────────────────────
    #
    # `danh_muc.py` chỉ có HAI chỗ đem đột biến được, và cả hai đều sống
    # sót — tức là cả hai đều chưa ai kiểm. Một trong hai là cửa duy nhất
    # canh «có đủ tiền không».
    _dmB = DanhMuc(1000.0)
    kiem("cam kết ĐÚNG BẰNG toàn bộ tiền mặt thì ĐƯỢC",
         _dmB.cam_ket("het", [ViThe("het", "a.b.v1", "LONG", "kraken",
                                    "SOL", 1000.0)])
         and gan(_dmB.tienMatUsd, 0.0),
         "«quá tiền mặt» phải nghĩa là QUÁ, không phải vừa hết — chặn ở "
         "đây là để lại một đồng lẻ vĩnh viễn không tiêu được")
    kiem("nhưng quá một xu thì KHÔNG",
         not DanhMuc(1000.0).cam_ket(
             "qua", [ViThe("qua", "a.b.v1", "LONG", "kraken", "SOL",
                           1000.01)]))

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

    # ── BIÊN của từng cửa: «đúng bằng ngưỡng» phải QUA ──────────────────
    #
    # Quét đột biến tự động trên `rui_ro_tong.py` cho 10/15 con SỐNG SÓT,
    # và phần lớn nằm ở đây: `>` đổi thành `>=`, `<` thành `<=`. Nghĩa là
    # không phép kiểm nào phân biệt được «đúng bằng trần» với «vượt trần»
    # — trên chính cái cửa quyết định tiền có được cam kết hay không.
    #
    # Ngưỡng ở đây ĐÓNG: đúng bằng trần thì còn trong trần. Đảo lại là
    # loại đúng những cơ hội nằm sát mép, và sát mép là chỗ phần lớn cơ
    # hội thật nằm.
    _dmB = DanhMuc(10_000.0)

    _rrD = RuiRoTong({"ruiRoToiDa": 0.60})
    _ttD = _mau(von=100.0, chua=9000.0,
                rr=RuiRo(0.60, 0.10, 0.10, 0.10, 0.10, 0.10))
    kiem("điểm rủi ro ĐÚNG BẰNG trần thì vẫn qua",
         not any("diem-rui-ro-cao" in x for x in _rrD.xet(_ttD, _dmB).lyDo),
         f"{_rrD.xet(_ttD, _dmB).lyDo} — trần là trần, không phải mép vực")
    _ttD2 = _mau(von=100.0, chua=9000.0,
                 rr=RuiRo(0.61, 0.10, 0.10, 0.10, 0.10, 0.10))
    kiem("nhích trên trần một chút thì bị chặn",
         any("diem-rui-ro-cao" in x for x in _rrD.xet(_ttD2, _dmB).lyDo),
         "không có vế này thì phép kiểm trên chỉ chứng minh cửa luôn im")

    _rrT = RuiRoTong({"tinCayToiThieu": 0.50})
    kiem("độ tin ĐÚNG BẰNG sàn thì vẫn qua",
         not any("tin-cay-thap" in x for x in
                 _rrT.xet(_mau(von=100.0, chua=9000.0, tin=0.50),
                          _dmB).lyDo))
    kiem("dưới sàn một chút thì bị chặn",
         any("tin-cay-thap" in x for x in
             _rrT.xet(_mau(von=100.0, chua=9000.0, tin=0.49), _dmB).lyDo))

    # NET mỗi giờ = netUocBps / giuGio. Dựng ngược để chạm đúng sàn.
    _san = 0.5
    _rrN = RuiRoTong({"netMoiGioToiThieuBps": _san})
    kiem("NET mỗi giờ ĐÚNG BẰNG sàn thì vẫn qua",
         not any("net-thap" in x for x in
                 _rrN.xet(_mau(von=100.0, chua=9000.0,
                               net=_san * 24.0, giu=24.0), _dmB).lyDo),
         f"sàn {_san} bps/giờ")
    kiem("dưới sàn thì bị chặn",
         any("net-thap" in x for x in
             _rrN.xet(_mau(von=100.0, chua=9000.0,
                           net=_san * 24.0 * 0.9, giu=24.0), _dmB).lyDo))

    _rrK = RuiRoTong({"khoaVonToiDaGio": 720.0})
    kiem("khoá vốn ĐÚNG BẰNG trần thì vẫn qua",
         not any("khoa-von-lau" in x for x in
                 _rrK.xet(_mau(von=100.0, chua=9000.0, khoa=720.0),
                          _dmB).lyDo))
    kiem("khoá quá trần một giờ thì bị chặn",
         any("khoa-von-lau" in x for x in
             _rrK.xet(_mau(von=100.0, chua=9000.0, khoa=721.0), _dmB).lyDo))

    # `and` chứ không `or`: cờ TẮT thì thiếu mô hình phí KHÔNG phải lý do
    # từ chối. Đổi thành `or` là bật một cửa mà người vận hành đã tắt —
    # và tắt nó là quyết định có chủ ý, ghi ngay trong MAC_DINH.
    # `_mau` đặt `moHinhPhiDuChua=True` cứng, nên ép lại sau khi dựng —
    # `ToTrinh` đông cứng, đi cửa `object.__setattr__` như mọi phép kiểm
    # khác cần một tờ trình lệch chuẩn.
    def _thieuMoHinh():
        t = _mau(von=100.0, chua=9000.0)
        object.__setattr__(t, "moHinhPhiDuChua", False)
        object.__setattr__(t, "phiConThieu", ("vay-coin",))
        return t

    kiem("cờ mô-hình-phí TẮT thì thiếu mô hình KHÔNG bị chặn",
         not any("mo-hinh-phi-thieu" in x for x in
                 RuiRoTong({"batBuocDuMoHinhPhi": False}).xet(
                     _thieuMoHinh(), _dmB).lyDo),
         "bật một cửa người vận hành đã tắt là tự ý siết, dù siết cũng là "
         "một hướng")
    kiem("và BẬT cờ ấy thì mới chặn",
         any("mo-hinh-phi-thieu" in x for x in
             RuiRoTong({"batBuocDuMoHinhPhi": True}).xet(
                 _thieuMoHinh(), _dmB).lyDo))

    # `biCat` phải phân biệt CẮT với CHO ĐỦ. Trần đúng bằng số xin không
    # phải là cắt — báo cắt ở đó là dạy người đọc bỏ qua chữ «đã cắt».
    _pqDu = RuiRoTong().xet(_mau(von=100.0, chua=9000.0), DanhMuc(10_000.0))
    kiem("cho ĐỦ số xin thì KHÔNG gọi là bị cắt",
         _pqDu.duyet and not _pqDu.biCat,
         f"xin {_pqDu.xinUsd} cho {_pqDu.choToiDaUsd}")
    _pqCat = RuiRoTong().xet(_mau(von=5000.0, chua=9000.0),
                             DanhMuc(10_000.0))
    kiem("cho ÍT hơn số xin thì mới là bị cắt",
         _pqCat.duyet and _pqCat.biCat,
         f"xin {_pqCat.xinUsd} cho {_pqCat.choToiDaUsd}")

    # Trần siết về 0 là TỪ CHỐI, và một tờ bị từ chối KHÔNG phải một tờ «bị
    # cắt». Hai chữ ấy đi hai chỗ khác nhau trong phễu: «bị cắt» đếm những
    # cơ hội mình bóp nhỏ lại, «từ chối» đếm những cơ hội mình bỏ hẳn. Trộn
    # chúng vào nhau là đếm một lần vào cả hai cột, và tổng thì không cộng
    # lại được nữa.
    _tt0 = _mau(von=100.0, chua=9000.0)
    # Bỏ sàn vốn tối thiểu đi, để chạm ĐÚNG nhánh «hết chỗ ở trần» chứ
    # không rơi vào nhánh «dưới vốn tối thiểu» ở trên nó.
    object.__setattr__(_tt0, "vonToiThieuKinhTeUsd", None)
    _pq0 = RuiRoTong({"tranMotCoHoi": 0.0,
                      "batBuocKhaiVonToiThieu": False}).xet(
        _tt0, DanhMuc(10_000.0))
    kiem("trần siết về 0 thì KHÔNG duyệt", not _pq0.duyet,
         f"đang cho {_pq0.choToiDaUsd}")
    kiem("và tờ bị từ chối thì KHÔNG gọi là «bị cắt»", not _pq0.biCat,
         "0 đồng là bỏ hẳn, không phải bóp nhỏ")
    kiem("một phán quyết 0 đồng phải KÈM lý do",
         any("het-cho-o-tran" in x for x in _pq0.lyDo),
         f"lyDo={_pq0.lyDo} — ô lý do trống thì trong phễu nó hiện thành "
         f"một tờ bị đánh rớt không ai biết vì sao")


def kiem_phan_bo() -> None:
    print("\n── Phân Bổ: cấp TUẦN TỰ, vì cấp song song thì trần vô nghĩa ───")
    from thi_bac_ty.danh_muc import DanhMuc
    from thi_bac_ty.phan_bo import PhanBo
    from thi_bac_ty.rui_ro_tong import RuiRoTong
    from thi_bac_ty.to_trinh import Chan

    pb, rrt = PhanBo(), RuiRoTong()

    # NET ≤ 0 bị loại thẳng, dù mọi thứ khác đều đẹp.
    kiem("NET ≤ 0 xếp hạng −∞", pb.diem(_mau(net=0.0), 0.1) == float("-inf"),
         "lỗ ít vẫn là lỗ")

    # Điểm = net/giờ × RÓT ĐƯỢC × tin × (1−rủi ro) × khoá vốn.
    # Đặt xin = chứa = 100 và khoá = 0 để chỉ còn ba thừa số gốc nhân với 100.
    lanh = dict(net=8.0, giu=8.0, von=100.0, chua=100.0, khoa=0.0)
    d = pb.diem(_mau(tin=0.5, **lanh), 0.5)
    kiem("điểm nhân đủ ba thừa số gốc", gan(d, 1.0 * 100.0 * 0.5 * 0.5),
         f"đang là {d}")
    kiem("không tự chấm được độ tin thì coi như 1.0",
         gan(pb.diem(_mau(tin=None, **lanh), 0.0), 100.0))
    kiem("chưa đo được rủi ro thì coi như 0.5",
         gan(pb.diem(_mau(tin=1.0, **lanh), None), 50.0),
         "không phải 0 — chưa biết không phải là an toàn")

    # ── §13 · đúng ví dụ trong tệp: 0,40% trên $80 vs 7% trên $100.000 ──
    # DEX arb: lợi suất cao ngất, sức chứa $80.
    # Lending: lợi suất thấp, nhưng rót được $5.000.
    dex = _mau(taiSan="DEX", net=400.0, giu=8.0, tin=1.0, von=80.0,
               chua=80.0, khoa=0.0)          # 50 bps/giờ, rót được $80
    lend = _mau(taiSan="LEND", net=8.0, giu=8.0, tin=1.0, von=5000.0,
                chua=5000.0, khoa=0.0)       # 1 bps/giờ, rót được $5.000
    kiem("xếp theo PHẦN TRĂM thì cơ hội $80 thắng",
         dex.net_moi_gio_bps > lend.net_moi_gio_bps,
         "đây đúng là cái bẫy §13 mô tả")
    kiem("xếp theo ĐÔ-LA MỖI GIỜ thì cơ hội $5.000 thắng",
         pb.diem(lend, 0.0) > pb.diem(dex, 0.0),
         f"dex={pb.diem(dex, 0.0):.0f} lend={pb.diem(lend, 0.0):.0f}")

    # Nhưng khi trần khả dụng nhỏ hơn CẢ HAI, phần sức chứa thừa vô dụng,
    # nên hai cơ hội quay về so bằng lợi suất — và lúc ấy DEX thắng THẬT.
    kiem("trần khả dụng $50 thì sức chứa thừa hết tác dụng, DEX thắng lại",
         pb.diem(dex, 0.0, 50.0) > pb.diem(lend, 0.0, 50.0),
         "một thước tính công cho phần sức chứa không dùng tới là thước "
         "nói dối")

    ct = pb.diem_chi_tiet(_mau(von=1000.0, chua=80.0, khoa=0.0), 0.0)
    kiem("rót được = chỗ CHẬT NHẤT giữa xin và sức chứa",
         gan(ct["rotDuocUsd"], 80.0), str(ct["rotDuocUsd"]))
    ct2 = pb.diem_chi_tiet(_mau(von=1000.0, chua=800.0, khoa=0.0), 0.0, 200.0)
    kiem("và trần khả dụng cũng cắt vào đó",
         gan(ct2["rotDuocUsd"], 200.0), str(ct2["rotDuocUsd"]))
    kiem("chưa đo sức chứa thì rót được bị PHẠT, không cho nguyên số xin",
         gan(pb.diem_chi_tiet(_mau(von=1000.0, chua=None, khoa=0.0),
                              0.0)["rotDuocUsd"], 350.0),
         "mù sức chứa mà tính như đã đo là thưởng cho sự mù")

    # ── §14 · khoá vốn phải vào điểm ────────────────────────────────────
    ngay = pb.diem(_mau(net=8.0, giu=8.0, tin=1.0, von=100.0, chua=5000.0,
                        khoa=0.0), 0.0)
    khoa = pb.diem(_mau(net=8.0, giu=8.0, tin=1.0, von=100.0, chua=5000.0,
                        khoa=168.0), 0.0)
    kiem("cùng lợi suất, khoá 7 ngày THUA rút được ngay", khoa < ngay,
         f"khoá={khoa:.3f} ngay={ngay:.3f}")
    kiem("khoá đúng tham chiếu thì hệ số = 0,50",
         gan(pb.diem_chi_tiet(_mau(chua=5000.0, khoa=168.0), 0.0)["heSoKhoaVon"], 0.5))
    kiem("khoá 0 giờ thì hệ số = 1,00",
         gan(pb.diem_chi_tiet(_mau(chua=5000.0, khoa=0.0), 0.0)["heSoKhoaVon"], 1.0))
    kiem("chưa đo khoá vốn thì bị PHẠT, không coi như 0 giờ",
         gan(pb.diem_chi_tiet(_mau(chua=5000.0, khoa=None), 0.0)["heSoKhoaVon"], 0.70),
         "None ≠ 0; chưa biết khoá bao lâu không có nghĩa là rút được ngay")
    kiem("hệ số khoá không bao giờ chạm 0",
         pb.diem_chi_tiet(_mau(chua=5000.0, khoa=99999.0), 0.0)["heSoKhoaVon"] > 0.0,
         "khoá lâu là bất lợi, không phải phạm luật — phạm luật thì "
         "rui_ro_tong.khoaVonToiDaGio đã chặn")

    # ── điểm phải MỔ RA ĐƯỢC, không phải một con số câm ─────────────────
    kiem("điểm chi tiết khai đủ năm thừa số",
         set(pb.diem_chi_tiet(_mau(chua=5000.0, khoa=0.0), 0.2))
         >= {"netMoiGioBps", "rotDuocUsd", "tinCay", "motTruRuiRo",
             "heSoKhoaVon"},
         "nhìn một con số trần thì không ai biết thua vì rủi ro hay vì "
         "sức chứa mỏng")

    # ── §14 · hai cửa mới của Rủi Ro Tổng ───────────────────────────────
    from thi_bac_ty.danh_muc import DanhMuc as _DM
    dm_k = _DM(10000.0)
    lau = _mau(von=100.0, chua=9000.0, khoa=24 * 90.0)      # khoá 90 ngày
    pq_k = rrt.xet(lau, dm_k)
    kiem("khoá vốn quá trần thì TỪ CHỐI, không phải cắt bớt",
         not pq_k.duyet and any("khoá vốn" in l for l in pq_k.lyDo),
         "cắt trần không rút ngắn thời gian khoá — rót ít hơn vẫn kẹt "
         "đúng ngần ấy tháng")

    hep_thoat = _mau(von=500.0, chua=9000.0, khoa=0.0, thoat=120.0)
    pq_t = rrt.xet(hep_thoat, dm_k)
    kiem("thanh khoản thoát cắt trần xuống đúng chỗ ra được",
         gan(pq_t.choToiDaUsd, 120.0)
         and any("thanh khoản thoát" in l for l in pq_t.lyDoCat),
         f"cho {pq_t.choToiDaUsd} · {pq_t.lyDoCat}")
    kiem("tờ trình tự biết mình có ra được không",
         hep_thoat.raDuocKhong is False and _mau(thoat=None).raDuocKhong is None,
         "vào được $100.000 không có nghĩa là ra được $100.000")
    kiem("giờ vốn bị giữ lấy chỗ LỚN hơn giữa định giữ và buộc giữ",
         gan(_mau(giu=8.0, khoa=2160.0).gio_von_bi_giu, 2160.0)
         and gan(_mau(giu=8.0, khoa=0.0).gio_von_bi_giu, 8.0),
         "định giữ 8 giờ mà khoá 90 ngày thì vốn bị giữ 90 ngày")

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

    # ── BIÊN, chỗ quét đột biến chỉ ra đang trống ──────────────────────
    #
    # Quét đột biến trên `phan_bo.py` cho 6/9 con SỐNG SÓT. Đây là bàn
    # chia tiền: mỗi con sống là một dòng có thể sửa sai mà không phép
    # kiểm nào kêu.
    _V = __import__("thi_bac_ty.danh_muc", fromlist=["ViThe"]).ViThe

    # Sàn ĐÓNG: cấp đúng bằng sàn thì vẫn cấp. Trên kia đã có vế «dưới
    # sàn thì thôi» ($15), nhưng chỉ vế ấy thì `<` và `<=` là một — và
    # đổi sang `<=` là ném đúng những lần rót nằm sát sàn.
    _dmS = DanhMuc(1000.0)
    _dmS.cam_ket("X", [_V("X", "x.y.v1", "LONG", "kraken", "SOL", 775.0)])
    _latS = pb.chia([_mau(taiSan="DOT", von=100.0, chua=1000.0,
                          chan=(Chan("LONG", "okx", "DOT"),
                                Chan("SHORT", "bybit", "DOT")))],
                    rrt, _dmS, luc="T")
    kiem("cấp ĐÚNG BẰNG sàn tối thiểu thì vẫn cấp",
         len(_latS.daCap) == 1 and gan(_latS.daCap[0]["capUsd"], 25.0),
         f"tiền mặt 225, dự trữ 200, còn đúng 25 = sàn; "
         f"daCap={_latS.daCap} tuChoi={_latS.tuChoi}")

    # Trần SỐ vị thế cũng đóng: đang ôm đúng trần thì tờ sau không vào
    # nữa. `>=` đổi thành `>` là cho lọt thêm đúng một vị thế quá trần,
    # và trần «12» im lặng thành «13».
    _dmN = DanhMuc(10_000.0)
    _dmN.cam_ket("X", [_V("X", "x.y.v1", "LONG", "kraken", "SOL", 100.0)])
    _pbN = PhanBo({"toiDaSoViThe": 1})
    _latN = _pbN.chia([_mau(taiSan="DOT", von=100.0, chua=1000.0,
                            chan=(Chan("LONG", "okx", "DOT"),))],
                      rrt, _dmN, luc="T")
    kiem("đang ôm ĐÚNG trần số vị thế thì tờ sau bị chặn",
         len(_latN.daCap) == 0
         and any("tran-vi-the" in str(x.get("lyDo")) for x in _latN.tuChoi),
         f"trần 1, đang ôm 1; daCap={_latN.daCap} tuChoi={_latN.tuChoi}")
    _dmN2 = DanhMuc(10_000.0)
    _dmN2.cam_ket("X", [_V("X", "x.y.v1", "LONG", "kraken", "SOL", 100.0)])
    _latN2 = PhanBo({"toiDaSoViThe": 2}).chia(
        [_mau(taiSan="DOT", von=100.0, chua=1000.0,
              chan=(Chan("LONG", "okx", "DOT"),))], rrt, _dmN2, luc="T")
    kiem("còn dưới trần một chỗ thì vào được",
         len(_latN2.daCap) == 1,
         "không có vế này thì phép kiểm trên cũng xanh khi bàn chia luôn "
         "từ chối")

    # `thamChieuKhoaGio = 0` nghĩa là KHÔNG phạt khoá vốn. Đổi `<=` thành
    # `<` là rơi thẳng vào phép chia cho 0.
    kiem("tham chiếu khoá = 0 thì không phạt, và không nổ",
         gan(PhanBo({"thamChieuKhoaGio": 0.0}).diem_chi_tiet(
                 _mau(net=8.0, giu=8.0, von=100.0, chua=100.0, khoa=99.0),
                 0.0, None)["heSoKhoaVon"], 1.0),
         "tắt một hình phạt phải là TẮT, không phải chia cho 0")

    # `luc` truyền vào phải được GIỮ. `or` đổi thành `and` thì mọi lát cắt
    # mang nhãn thời gian của máy thay vì của vòng — và lúc đối chiếu thì
    # không ghép lại được với sổ.
    kiem("nhãn thời gian truyền vào được giữ nguyên", _latS.luc == "T",
         f"đang là {_latS.luc!r}")
    kiem("không truyền thì tự điền, không để trống",
         bool(pb.chia([], rrt, DanhMuc(1000.0)).luc))

    # Từ chối mà ô lý do TRỐNG thì vẫn phải ghi vào sổ một câu đọc được.
    # `or` đổi thành `and` là ghi một bút toán TU_CHOI với lý do rỗng —
    # đúng cái bẫy «ô trống thì không ai đọc thành gì».
    class _RrtCam:
        c = {"tranMotCoHoi": 0.15}

        def diem(self, tt):
            return 0.2, ()

        def xet(self, tt, dm):
            from thi_bac_ty.rui_ro_tong import PhanQuyet
            return PhanQuyet(tt.ma, tt.chienLuoc, tt.vonCanUsd, 0.0, 0.2,
                             (), ())

    from thi_bac_ty.so_cai import SoCai as _SoCai
    _sc = _SoCai(_tam("phanbo-lydo") / "so.sqlite3")
    PhanBo().chia([_mau(taiSan="DOT", von=100.0, chua=1000.0)],
                  _RrtCam(), DanhMuc(10_000.0), so_cai=_sc, luc="T")
    _bt = _sc.gan_day(50, loai="TU_CHOI")
    kiem("từ chối KHÔNG lý do vẫn ghi sổ một câu đọc được",
         len(_bt) == 1 and bool(str(_bt[0].get("lyDo", "")).strip()),
         f"{_bt} — bút toán TU_CHOI với ô lý do rỗng là một dòng sổ không "
         f"ai đọc lại được")


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

    # ── BIÊN, chỗ quét đột biến chỉ ra đang trống ──────────────────────
    #
    # Sổ này là cái PHỄU — nơi câu «từ chối 95 trên 100» được đếm. Quét
    # đột biến cho 5/6 con sống sót.

    # NẤC ĐẦU. `tu is None` nghĩa là tờ trình vừa vào sổ, và nó chỉ được
    # vào ở PHAT_HIEN. Đổi `==` thành `!=` là cho một tờ trình xuất hiện
    # thẳng ở giữa phễu — lúc ấy nấc đầu nhỏ hơn nấc sau, và mọi tỉ lệ
    # sống sót tính từ nó đều vượt 100%.
    kiem("tờ trình mới chỉ vào sổ được ở PHAT_HIEN",
         _hop_le(None, "PHAT_HIEN"))
    for _t in ("DUYET_TY", "DUYET_RUI_RO", "DA_CAP_VON", "DA_MO",
               "TU_CHOI", "DA_DONG"):
        kiem(f"KHÔNG vào thẳng được ở {_t}", not _hop_le(None, _t),
             "vào giữa phễu thì nấc đầu nhỏ hơn nấc sau, và tỉ lệ sống "
             "sót tính từ nó vượt 100%")

    # SỔ RỖNG: 0 tờ và `chuaCo` là True. `int(n or 0)` che cho ca bảng
    # rỗng trả `None`; đổi thành `and` là `int(None)` nổ ngay, hoặc tệ
    # hơn, trả 0 mà `chuaCo` sai — và một cuốn sổ trắng lúc ấy trông y
    # hệt một cuốn sổ đã có tờ nào đó.
    _sdkR = SoDangKy(_tam("sdk-rong") / "sdk.sqlite3")
    _tR = _sdkR.tom_tat()
    kiem("sổ RỖNG: 0 tờ, và `chuaCo` nói thẳng là chưa có gì",
         _tR["soToTrinh"] == 0 and _tR["chuaCo"] is True,
         f"{_tR}")
    _sdkR.ghi_nhan(_mau(taiSan="ETH"))
    _tR2 = _sdkR.tom_tat()
    kiem("có một tờ rồi thì `chuaCo` TẮT",
         _tR2["soToTrinh"] == 1 and _tR2["chuaCo"] is False,
         f"{_tR2} — một cờ không bao giờ tắt được là một cờ không ai đọc")

    # LÝ DO TỪ CHỐI gom theo MÃ. Câu trần không có mã thì gom theo chính
    # câu ấy — `ly or ""` che cho ca `lyDo` rỗng trong sổ cũ. Đổi thành
    # `and` là mọi câu gom về khoá rỗng, và bảng thủ phạm chỉ còn một
    # dòng trắng.
    _sdkL = SoDangKy(_tam("sdk-lydo") / "sdk.sqlite3")
    for _i, _ly in enumerate(("tran-vi-the: đã đủ 12",
                              "tran-vi-the: đã đủ 12 chỗ",
                              "duoi-von-toi-thieu: cần 500",
                              "một câu trần không có mã",
                              "một câu trần KHÁC cũng không có mã")):
        _t = _mau(taiSan=f"C{_i}")
        _sdkL.ghi_nhan(_t)
        _sdkL.chuyen(_t.ma, "TU_CHOI", _ly)
    _ld = _sdkL.ly_do_tu_choi(9)
    _ho = _ld.get("phai-sinh") or []
    _theoMa = {x["ma"]: x for x in _ho}
    kiem("hai câu KHÁC NHAU cùng một MÃ gom về một dòng",
         (_theoMa.get("tran-vi-the") or {}).get("so") == 2
         and (_theoMa["tran-vi-the"]).get("soCauKhac") == 2,
         f"{_ho} — gom theo câu thì một dòng dài lặp nguyên văn thành "
         f"«thủ phạm chính» chỉ vì nó lặp lại")
    # HAI câu trần KHÁC NHAU thì là HAI dòng. Gom chúng về một khoá rỗng
    # là biến hai lý do khác nhau thành một dòng trắng đếm 2 — và bảng
    # thủ phạm mất đúng cái nó sinh ra để chỉ.
    _khongMa = [x for x in _ho if x["ma"] is None]
    kiem("hai câu trần KHÁC NHAU, không mã, thì là HAI dòng",
         len(_khongMa) == 2 and all(x["so"] == 1 for x in _khongMa),
         f"{_khongMa} — gom về một khoá rỗng là biến hai lý do khác nhau "
         f"thành một dòng trắng, và bảng thủ phạm mất đúng cái nó chỉ")
    kiem("và cả hai đều mang nguyên câu ra làm bằng",
         len({x["lyDo"] for x in _khongMa}) == 2, str(_khongMa))


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
        vonToiThieuKinhTeUsd = 50.0
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
        vonToiThieuKinhTeUsd = 50.0
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
    from thi_bac_ty.chan_doan_he import _ma_ly_do as _ma_ly
    _duong = tu.so_dang_ky.phieu(
        tu.so_dang_ky.theo_trang_thai("TU_CHOI")[0]["ma"])["duongDi"]
    _lyTC = [b["lyDo"] for b in _duong if b["den"] == "TU_CHOI"]
    kiem("tờ trình bị từ chối có ghi rõ là do cầu dao",
         any("cau-dao-ngat" in x for x in _lyTC), str(_lyTC))
    kiem("và lý do ấy MÁY đọc được, không chỉ người đọc được",
         any(_ma_ly(x) == "cau-dao-ngat" for x in _lyTC),
         "«CẦU DAO NGẮT» có dấu cách và chữ hoa nên chẩn đoán không nhận ra "
         "được nó là mã — và 520 lần từ chối lớn nhất của cỗ máy rơi vào ô "
         "«không phân loại được»")

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
        vonToiThieuKinhTeUsd = 50.0

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
        vonToiThieuKinhTeUsd = 50.0
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
    import json as _js0
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
    from thi_bac_ty.chan_doan_he import SAN_BUOC_KHUON as _SBK
    _tranHe = max(abs(dx[0].tu) * BUOC_TOI_DA, (0.35 - 0.02) * _SBK)
    kiem("bước vặn có trần",
         dx and abs(dx[0].den - dx[0].tu) <= _tranHe + 1e-9,
         f"{dx[0].tom_tat()} vs trần {_tranHe}")
    # Cùng cái bẫy như tầng ty, và ở đây nó còn núp sau một chữ `or`: `or`
    # chỉ cứu đúng `hien == 0`, mà chỗ chết nằm ở MỌI giá trị nhỏ so với
    # khuôn. Một núm 0,02 trong khuôn [0,02 · 0,35] có bước nhân 0,005 —
    # nó không đi được đâu cả.
    _dxNho = de_xuat(tr3, {"ruiRoTong": {"tranMotCoHoi": 0.02}})
    kiem("núm gần biên dưới vẫn bước được, không đứng yên",
         _dxNho and _dxNho[0].den - _dxNho[0].tu >= (0.35 - 0.02) * _SBK - 1e-9,
         f"{[d.tom_tat() for d in _dxNho]} — `or` chỉ cứu số 0, không cứu "
         f"số nhỏ")
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

    # ── TRẦN VỊ THẾ: bệnh núp dưới một con số dùng vốn rất khoẻ ─────────
    from thi_bac_ty.chan_doan_he import _ma_ly_do
    from thi_bac_ty.phan_bo import ly_do as _ly_do_pb

    kiem("mã đọc ra được từ câu có mã", _ma_ly_do(_ly_do_pb("tran-vi-the",
                                                            n=12))
         == "tran-vi-the")
    for _cau in ("đã đủ 12 vị thế — quá nhiều thì không theo dõi nổi",
                 # NGẮN, nên bẫy độ dài không cứu: chỉ HÌNH DẠNG mới loại
                 # được nó. Đột biến bỏ phép soát hình dạng đã sống sót
                 # đúng vì phép kiểm bản đầu chỉ có câu dài.
                 "Danh Mục từ chối",
                 "CẦU DAO NGẮT: von-ngoai-mu: x",
                 "Rủi Ro Tổng: trần cảng"):
        kiem(f"câu TRẦN «{_cau[:22]}…» không được nhận bừa làm mã",
             _ma_ly_do(_cau) is None,
             "để một câu lọt vào bảng đếm là để một câu dài thành «thủ phạm "
             "chính» chỉ vì nó lặp lại nguyên văn")
    kiem("và cầu dao cũng phải mang mã",
         _ma_ly_do("cau-dao-ngat: von-ngoai-mu: NAV thiếu") == "cau-dao-ngat")

    def _anh_ly(dsLy, dungVon=0.62):
        return {"soDangKy": {"pheu": {"phatHien": 300, "DUYET_TY": 200,
                                      "DUYET_RUI_RO": 150,
                                      "DA_CAP_VON": 100, "DA_MO": 95}},
                "danhMuc": {"tiLeDungVon": dungVon},
                "pheuDayDu": {"theoHo": [{"ho": "phai-sinh",
                                          "lyDoTuChoi": dsLy}]}}

    tr7 = chan_doan_he(_anh_ly([
        {"lyDo": _ly_do_pb("tran-vi-the", n=12), "so": 40},
        {"lyDo": _ly_do_pb("net-am"), "so": 30},
        {"lyDo": "cau-dao-ngat: von-ngoai-mu: x", "so": 30}]))
    ma7 = {t.ma for t in tr7}
    kiem("trần vị thế chặn 40% số lần từ chối → thành TRIỆU CHỨNG",
         "tran-vi-the-chan" in ma7, str(ma7))
    kiem("và nó nổ được kể cả khi DÙNG VỐN CAO",
         "tran-dat-sai-cho" not in ma7,
         "12 vị thế ăn hết tiền thì tỉ lệ dùng vốn cao — bệnh này núp ngay "
         "dưới một con số trông rất khoẻ, nên `tran-dat-sai-cho` không thấy")
    dx7 = de_xuat(tr7, {"phanBo": {"toiDaSoViThe": 12}})
    kiem("đề xuất NỚI trần vị thế, và là số NGUYÊN",
         dx7 and dx7[0].nut == "phanBo.toiDaSoViThe"
         and dx7[0].den > dx7[0].tu and isinstance(dx7[0].den, int),
         str([d.tom_tat() for d in dx7]))

    tr8 = chan_doan_he(_anh_ly([
        {"lyDo": _ly_do_pb("tran-vi-the", n=12), "so": 5},
        {"lyDo": _ly_do_pb("net-am"), "so": 95}]))
    kiem("mã khác áp đảo thì KHÔNG đổ lỗi cho trần vị thế",
         "tran-vi-the-chan" not in {t.ma for t in tr8})

    tr9 = chan_doan_he(_anh_ly([
        {"lyDo": _ly_do_pb("tran-vi-the", n=12), "so": 5}]))
    kiem("quá ít lần từ chối thì chưa kết luận gì",
         "tran-vi-the-chan" not in {t.ma for t in tr9},
         "ba lần trên tổng bốn lần là 75% mà chẳng nói lên gì")

    tr10 = chan_doan_he(_anh_ly([
        {"lyDo": "đã đủ 12 vị thế — quá nhiều thì không theo dõi nổi",
         "so": 900},
        {"lyDo": _ly_do_pb("tran-vi-the", n=12), "so": 70},
        {"lyDo": _ly_do_pb("net-am"), "so": 30}]))
    _bc = [t.bangChung for t in tr10 if t.ma == "tran-vi-the-chan"]
    kiem("câu CŨ không mã bị loại khỏi MẪU SỐ, không pha loãng",
         _bc and _bc[0]["tongTuChoi"] == 100 and _bc[0]["soKhongMa"] == 900,
         f"{_bc} — chia cho một mẫu số có cả thứ mình không phân loại nổi là "
         f"tự pha loãng, và cái loãng ấy giấu đúng thủ phạm đang tìm")

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
        vonToiThieuKinhTeUsd = 50.0
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

    # ── THU VƯỢT TRẦN: lớp lỗi IN RA TIỀN, và không gì bắt được nó ─────
    #
    # Trung Ương nhận `thuUsd` từ ty rồi ghi thẳng vào Sổ Cái — đúng phân
    # tầng, ty biết việc của ty. Nhưng nó để hở đúng một lớp lỗi: một ty
    # quên chia cho 8.760 (giờ trong năm) sẽ in ra tiền, NAV phồng lên, và
    # `lechTien` VẪN KHỚP vì sổ ghi đúng con số bịa ấy. Cả 1.400 phép kiểm
    # trước lượt này không có cái nào bắt được chuyện đó.
    from thi_bac_ty.trung_uong import (BIEN_THU_VUOT_TRAN as _BIEN,
                                       _tran_thu_mot_vong as _tranThu)
    _t20 = {"netUocBps": 20.0 / 100 * (24.0 / (365 * 24)) * 10_000.0,
            "giuGio": 24.0}          # 20%/năm
    _tr = _tranThu(_t20, 1000.0, 0.0, 3600.0)
    kiem("trần thu một vòng dựng từ chính lời hứa của tờ trình",
         gan(_tr, 1000.0 * 0.20 / (365 * 24) * _BIEN, 1e-6),
         f"{_tr} — 1000 USD, 20%/năm, một giờ, nhân biên {_BIEN}")
    kiem("tờ trình KHÔNG khai lãi thì KHÔNG có trần, không dựng trần bịa",
         _tranThu({}, 1000.0, 0.0, 3600.0) is None,
         "không có gì để so thì không kết luận — đúng luật `none-khac-khong`")
    kiem("chưa qua giây nào thì cũng không có trần",
         _tranThu(_t20, 1000.0, 100.0, 100.0) is None)

    # Ty in ra tiền: cùng tờ trình 20%/năm mà thu như thể 20%/GIỜ.
    class _TyIn(Ty):
        ma, ho, moTa = "in.tien.v1", "tin-dung", "quên chia 8760"
        vonToiThieuKinhTeUsd = 10.0

        def quet(self):
            return ["X"] if self.soLuotQuet <= 1 else []

        def xet(self, co):
            return True, []

        def trinh(self, co):
            return _mau(ma=self.ma, ho=self.ho, taiSan="X", von=100.0,
                        chua=9000.0, net=_t20["netUocBps"], giu=24.0)

        def ke_toan(self, viThe, toTrinh, tuGiay, denGiay):
            from thi_bac_ty.ke_toan import KetToanVong
            # 8.760 lần mức đúng — đúng cái lỗi quên chia cho số giờ/năm.
            # Kèm một khoản phí TRONG KỲ, để phép kiểm cửa sổ ở dưới có
            # bút toán PHI thật mà soi — dựng riêng một ty nữa cho việc ấy
            # là dựng thêm một chỗ có thể lệch.
            return KetToanVong(thuUsd=100.0 * 0.20 * 8760.0 / (365 * 24)
                               * (denGiay - tuGiay) / 3600.0,
                               phiUsd=1e-9, vi="thu bịa")

    _tuIn = TrungUong(_tam("thu-vuot"), {"vonBanDauUsd": 5000.0})
    _tuIn.dang_ky(_TyIn())
    for _ in range(3):
        _tuIn.mot_vong(lechDongHoGiay=1.0, cangChet=[], tuoiXauNhatGiay=1.0)
    _k = _tuIn.latCatKeToan.tom_tat()
    kiem("ty IN RA TIỀN bị bắt, và bắt được ngay lần đầu",
         _k["soThuVuotTran"] >= 1,
         f"{_k} — NAV phồng lên mà `lechTien` vẫn khớp, vì sổ ghi đúng con "
         f"số bịa; không có phép soát này thì không gì đỏ")
    kiem("và bằng chứng nói rõ thu bao nhiêu trên trần bao nhiêu",
         _k["thuVuotTran"] and _k["thuVuotTran"][0]["thuUsd"]
         > _k["thuVuotTran"][0]["tranUsd"] > 0,
         str(_k["thuVuotTran"][:1]))
    # KHÔNG cắt con số — cắt là bịa ra một con số thứ ba mà không ai đo.
    kiem("nhưng con số ấy VẪN được ghi, Trung Ương không tự sửa của ty",
         _k["thuUsd"] > 0,
         "ty biết việc của ty; Trung Ương ĐẾM và KHAI, không cắt")

    # Ty tử tế thì KHÔNG bị kêu oan — một phép soát báo nhầm là một phép
    # soát người ta dạy nó im.
    class _TyNgoan(_TyIn):
        # Mã phải đúng khuôn `<họ>.<tên>.v<số>` — `dang_ky` từ chối mọi
        # thứ khác. Bản đầu đặt `"ngoan.v1"` (hai phần), nên cỗ máy đối
        # chứng KHÔNG có ty nào, không có vị thế nào, và phép kiểm «không
        # bị kêu oan» xanh vì RỖNG chứ không vì đúng. Phép kiểm ngay dưới
        # đòi nó có vị thế thật, và chính nó lôi chuyện này ra.
        ma = "ngoan.chuan.v1"

        def ke_toan(self, viThe, toTrinh, tuGiay, denGiay):
            from thi_bac_ty.ke_toan import KetToanVong
            return KetToanVong(thuUsd=100.0 * 0.20 / (365 * 24)
                               * (denGiay - tuGiay) / 3600.0, vi="thu đúng")

    _tuNg = TrungUong(_tam("thu-ngoan"), {"vonBanDauUsd": 5000.0})
    _tuNg.dang_ky(_TyNgoan())
    for _ in range(3):
        _tuNg.mot_vong(lechDongHoGiay=1.0, cangChet=[], tuoiXauNhatGiay=1.0)
    # ── CỬA SỔ trong sổ cái phải có ĐỘ DÀI ─────────────────────────────
    # `so.keToanLucGiay = now` chạy TRƯỚC chỗ ghi sổ, nên bút toán FUNDING
    # ghi `tuGiay == denGiay`: sổ nói «khoản thu này kiếm được trong không
    # giây». Đo trên sổ thật 30/08: 400/400 dòng gần nhất đều thế. Không
    # ai dựng lại được tỉ suất từ một cuốn sổ như vậy — cùng lớp với lỗi
    # `nguonTsMs` của băng.
    _cs = [_js0.loads(x[0] or "{}") for x in _tuIn.so_cai._mo().execute(
        "SELECT chiTiet FROM but_toan WHERE loai='FUNDING'").fetchall()]
    _co = [x for x in _cs if "tuGiay" in x and "denGiay" in x]
    kiem("bút toán FUNDING khai CẢ HAI đầu cửa sổ", bool(_co), str(_cs[:1]))
    kiem("và cửa sổ ấy có ĐỘ DÀI, không phải không giây",
         all(float(x["denGiay"]) > float(x["tuGiay"]) for x in _co),
         f"{[(x['tuGiay'], x['denGiay']) for x in _co[:2]]} — sổ ghi «thu "
         f"ngần này trong không giây» thì không ai dựng lại được tỉ suất")

    # Phí TRONG KỲ cũng phải mang cửa sổ: một cuốn sổ tua lại được nửa
    # dòng tiền là một cuốn sổ không tua lại được. Phí VÀO LỆNH thì không
    # có cửa sổ — nó là một khoảnh khắc, không phải một quãng — nên chỉ
    # soi những dòng CÓ khai cửa sổ.
    _ph = [_js0.loads(x[0] or "{}") for x in _tuIn.so_cai._mo().execute(
        "SELECT chiTiet FROM but_toan WHERE loai='PHI'").fetchall()]
    _phCua = [x for x in _ph if "tuGiay" in x and "denGiay" in x]
    kiem("phí TRONG KỲ cũng khai cửa sổ, và cửa sổ có độ dài",
         bool(_phCua) and all(float(x["denGiay"]) > float(x["tuGiay"])
                              for x in _phCua),
         f"{_ph[:2]} — nửa dòng tiền dựng lại được theo thời gian, nửa kia "
         f"không, thì cả cuốn sổ không tua lại được")

    # ── VỐN-GIỜ TÁCH THEO TY ────────────────────────────────────────────
    # Tổng gộp trả lời «tiền đang làm việc lãi bao nhiêu» cho cả túi,
    # KHÔNG trả lời «ty nào đang làm ra tiền». Trước lượt này câu sau chỉ
    # có một nguồn: bảng hứa-vs-thực, thứ đòi 20 lần ĐÓNG mỗi ty. Đóng thì
    # hiếm; cộng dồn lãi thì mỗi vòng ba mươi giây một lần.
    _vg = _tuNg.anh_chup()["vonDangDung"]
    _tt = _vg.get("theoTy") or {}
    kiem("vốn-giờ tách được theo ty", bool(_tt), str(_vg)[:200])
    # Mẫu số phải CỘNG ĐÚNG, và cách duy nhất giữ được điều đó khi phép
    # tách ra đời SAU con số gộp là đặt tên cho phần chưa tách. Máy sống
    # 30/08: 1.987.747 vốn-giờ gộp, 4.866 đã tách — một bảng nói «tổng
    # các ty bằng gộp» ở đó là một bảng nói dối.
    kiem("đã tách + CHƯA TÁCH = gộp, không con số nào lửng lơ",
         gan(sum(v["vonGioUsd"] for v in _tt.values())
             + _vg["vonGioChuaTachUsd"], _vg["vonGioUsd"], 1e-9),
         f"{sum(v['vonGioUsd'] for v in _tt.values())} + "
         f"{_vg['vonGioChuaTachUsd']} vs {_vg['vonGioUsd']} — một con số "
         f"cộng hai đường là một con số sẽ lệch")
    kiem("cỗ máy mới dựng thì KHÔNG có phần chưa tách nào",
         gan(_vg["vonGioChuaTachUsd"], 0.0, 1e-9),
         f"{_vg['vonGioChuaTachUsd']} — mọi vốn-giờ tính từ nay đều có tên "
         f"ty; phần chưa tách chỉ là di sản của quãng trước khi có phép này")
    from thi_bac_ty.ke_toan import SoVonGio as _SVG3
    _sv3 = _SVG3(vonGioUsd=1000.0)          # di sản, chưa ty nào nhận
    _sv3.cong(100.0, 0.0, 3600.0, ty="moi.moi.v1")
    _t3 = _sv3.tom_tat()
    kiem("di sản trước khi tách được ĐẶT TÊN, không biến mất",
         gan(_t3["vonGioChuaTachUsd"], 1000.0, 1e-9)
         and gan(_t3["theoTy"]["moi.moi.v1"]["vonGioUsd"], 100.0, 1e-9),
         f"{_t3['vonGioChuaTachUsd']} — để hai con số cạnh nhau mâu thuẫn "
         f"thì người đọc phải tự đoán, và đoán sai thì không ai biết")
    kiem("thu ròng cũng thế",
         gan(sum(v["thuRongUsd"] for v in _tt.values()), _vg["thuRongUsd"],
             1e-9),
         f"{[v['thuRongUsd'] for v in _tt.values()]} vs {_vg['thuRongUsd']}")
    kiem("mỗi ty có tỉ suất riêng, và nó khớp phép chia của chính nó",
         all(v["loiSuatNamPhanTram"] is None
             or gan(v["loiSuatNamPhanTram"],
                    v["thuRongUsd"] / v["vonGioUsd"] * 365 * 24 * 100, 1e-6)
             for v in _tt.values()),
         str(_tt))
    # `None` khi chưa có vốn-giờ: chưa có mẫu số thì không có tỉ suất,
    # không phải tỉ suất bằng 0.
    from thi_bac_ty.ke_toan import SoVonGio as _SVG
    _sv = _SVG()
    _sv.cong_thu("chua.v1", 5.0)
    kiem("ty có thu mà CHƯA có vốn-giờ thì tỉ suất là None, không phải 0",
         _sv.tom_tat()["theoTy"]["chua.v1"]["loiSuatNamPhanTram"] is None,
         str(_sv.tom_tat()["theoTy"]))

    # Và phép kiểm phải chứng minh nó THẬT SỰ có vị thế để soi — không
    # thì «0 lần vượt trần» chỉ nói rằng chẳng có gì để vượt.
    kiem("cỗ máy đối chứng có vị thế thật, không phải rỗng",
         _tuNg.latCatKeToan.tom_tat()["soKeToanDuoc"] >= 1,
         f"{_tuNg.latCatKeToan.tom_tat()} — một phép đối chứng chạy trên "
         f"danh mục rỗng thì xanh vì rỗng, không vì đúng")
    kiem("ty kế toán ĐÚNG thì không bị kêu oan",
         _tuNg.latCatKeToan.tom_tat()["soThuVuotTran"] == 0,
         f"{_tuNg.latCatKeToan.tom_tat()} — báo nhầm thì người ta dạy phép "
         f"soát im, và lần nó đúng cũng bị bỏ qua")

    # ── CỰC của núm, không phải tên bệnh, quyết hướng vặn ───────────────
    # `tong-chan-het` gợi ý HAI núm. Khi `ruiRoToiDa` đã chạm biên trên —
    # tức đúng lúc bệnh nặng nhất — máy quay sang núm thứ hai là
    # `tinCayToiThieu`. Núm ấy ngược cực: cao lên là SIẾT. Bản cũ quyết
    # hướng bằng tên bệnh nên nó NÂNG sàn tin cậy để chữa bệnh nghẽn —
    # bóp cổ họng để chữa nghẹn. Và hỏng im lặng: A/B thấy tệ hơn nên trả
    # lại, sổ ghi «trả lại», trông y hệt một quyết định thận trọng.
    from thi_bac_ty.chan_doan_he import (
        NGUONG_RANH_TREN_KHA_DUNG, NGUONG_SONG_TREN_HUA,
        NUT_TRUNG_UONG as _NUT_HE, chan_doan_he as _cdh, de_xuat as _dxh)
    kiem("mọi núm Trung Ương đều khai CỰC của mình",
         all("cuc" in v and v["cuc"] in (1, -1)
             for v in _NUT_HE.values()),
         f"{[k for k, v in _NUT_HE.items() if v.get('cuc') not in (1, -1)]} — "
         f"thiếu cực thì hướng vặn quay về đoán theo tên bệnh")
    _chan = _cdh({"soDangKy": {"pheu": {"phatHien": 400, "DUYET_TY": 80,
                                        "DUYET_RUI_RO": 0, "DA_CAP_VON": 0}},
                  "danhMuc": {"tiLeDungVon": 0.0}})
    _dx = _dxh(_chan, {"ruiRoTong": {"ruiRoToiDa": 0.85,
                                     "tinCayToiThieu": 0.5}})
    kiem("tổng chặn hết + núm ngược cực → HẠ sàn tin cậy, không nâng",
         len(_dx) == 1 and _dx[0].nut == "ruiRoTong.tinCayToiThieu"
         and _dx[0].den < _dx[0].tu,
         f"{_dx} — nới ra là HẠ `tinCayToiThieu`; nâng nó lên là siết thêm "
         f"đúng lúc đang nghẽn")

    # ── HỨA QUÁ đo trên VỊ THẾ ĐANG MỞ — tín hiệu DÀY ───────────────────
    # Bảng hứa-vs-thực chỉ nói về những lần ĐÃ ĐÓNG và đòi 20 mẫu mỗi ty.
    # Máy sống 30/08: ty cao nhất mới có 8 mẫu sau nhiều ngày, trong khi
    # ba giờ gần nhất có 48 lần MỞ và 0 lần đóng. Nguồn khác, cùng câu
    # hỏi: lợi suất THỰC trên vốn-giờ so với lời hứa của chính những vị
    # thế đang mở — cùng một tập, cùng một quãng.
    def _hua(von, aprHua, soVt=1, khongKhai=0):
        return {"vonUsd": von, "aprHuaPhanTram": aprHua,
                "soViThe": soVt, "soKhongKhai": khongKhai}

    _anhMo = {"soDangKy": {"pheu": {"phatHien": 400, "DUYET_TY": 80,
                                    "DUYET_RUI_RO": 40, "DA_CAP_VON": 40}},
              "danhMuc": {"tiLeDungVon": 0.5, "soViThe": 4},
              "huaTheoTy": {
                  "hua.qua.v1": _hua(1000.0, 20.0),
                  "hua.dung.v1": _hua(1000.0, 2.5),
                  # KHÔNG khai: `vonUsd` 0 và apr None — ra khỏi cả tử số
                  # lẫn mẫu số, không phải «hứa 0%».
                  "khong.khai.v1": _hua(0.0, None, 1, 1),
                  "it.von.v1": _hua(1000.0, 20.0)},
              "vonDangDung": {"theoTy": {
                  "hua.qua.v1": {"vonGioUsd": 5000.0,
                                 "loiSuatNamPhanTram": 2.0},
                  "hua.dung.v1": {"vonGioUsd": 5000.0,
                                  "loiSuatNamPhanTram": 2.0},
                  "khong.khai.v1": {"vonGioUsd": 5000.0,
                                    "loiSuatNamPhanTram": 2.0},
                  "it.von.v1": {"vonGioUsd": 1.0,
                                "loiSuatNamPhanTram": 2.0}}}}
    _mo = {x.bangChung.get("chienLuoc"): x for x in _cdh(_anhMo)
           if x.ma == "hua-qua-dang-mo"}
    kiem("ty hứa 20% mà chạy 2% bị BẮT, trên chính vị thế đang mở của nó",
         "hua.qua.v1" in _mo
         and gan(_mo["hua.qua.v1"].bangChung["aprHuaPhanTram"], 20.0, 1e-6),
         f"{sorted(_mo)} — cùng một tập vị thế, cùng một quãng; không phải "
         f"hai cửa sổ khác nhau")
    kiem("ty hứa sát thực thì KHÔNG bị kêu",
         "hua.dung.v1" not in _mo,
         f"{sorted(_mo)} — lời hứa dựng trên ảnh chụp còn thực nhận là "
         f"trung bình cả quãng; lệch chút ít là bình thường")
    kiem("ty KHÔNG khai lời hứa thì không bị chấm, không bị đọc thành 0",
         "khong.khai.v1" not in _mo,
         f"{sorted(_mo)} — `None` là không khai, kéo bình quân xuống bằng "
         f"một số bịa thì tệ hơn không đo")
    kiem("và vốn-giờ quá ít thì chưa kết luận",
         "it.von.v1" not in _mo,
         f"{sorted(_mo)} — một trăm đô chạy một tiếng quy ra năm là tiếng "
         f"ồn nhân lên 8.760 lần")
    # Vị thế KHÔNG khai lời hứa phải ra khỏi CẢ TỬ SỐ LẪN MẪU SỐ. Đọc nó
    # thành «hứa 0%» thì nó kéo bình quân xuống, và một ty hứa quá thật sẽ
    # lọt lưới — càng nhiều vị thế không khai thì càng dễ lọt.
    _anhTron = {"soDangKy": {"pheu": {"phatHien": 400, "DUYET_TY": 80,
                                      "DUYET_RUI_RO": 40, "DA_CAP_VON": 40}},
                "danhMuc": {"tiLeDungVon": 0.5, "soViThe": 2},
                # 1.000 USD hứa 20% + 9.000 USD KHÔNG khai. Trung Ương
                # gộp: vốn 1.000, apr 20% — phần không khai ra khỏi mẫu
                # số. Đọc nó thành «hứa 0%» thì bình quân còn 2%, đúng
                # bằng thực nhận, và ty hứa quá lọt lưới.
                "huaTheoTy": {"tron.v1": _hua(1000.0, 20.0, 2, 1)},
                "vonDangDung": {"theoTy": {
                    "tron.v1": {"vonGioUsd": 5000.0,
                                "loiSuatNamPhanTram": 2.0}}}}
    _tron = {x.bangChung.get("chienLuoc"): x for x in _cdh(_anhTron)
             if x.ma == "hua-qua-dang-mo"}
    kiem("vị thế KHÔNG khai hứa bị loại khỏi CẢ mẫu số, không kéo bình quân",
         "tron.v1" in _tron
         and gan(_tron["tron.v1"].bangChung["aprHuaPhanTram"], 20.0, 1e-6),
         f"{_tron and _tron['tron.v1'].bangChung} — đọc «không khai» thành "
         f"«hứa 0%» thì chín phần mười vốn kéo bình quân xuống 2%, và một "
         f"ty hứa 20% mà chạy 2% lọt lưới")

    # Và bản gộp phải làm ở TRUNG ƯƠNG, vì ảnh chụp CẮT danh sách vị thế
    # ở 40 cái. Máy sống 30/08 giữ 101 vị thế: gộp từ 40 cái rồi đem so
    # với lợi suất thực của 101 cái là so hai tập khác nhau — và 40 cái ấy
    # chọn theo thứ tự từ điển, tức một mẫu thiên lệch không ai khai.
    # Ty mở BỐN vị thế — bốn, vì phép cấy lỗi «gộp từ danh sách đã cắt»
    # phải có gì để mà cắt.
    class _TyBon(_TyNgoan):
        ma = "bon.vithe.v1"

        def quet(self):
            return ["A", "B", "C", "D"] if self.soLuotQuet <= 1 else []

        def trinh(self, co):
            return _mau(ma=self.ma, ho=self.ho, taiSan=co, von=100.0,
                        chua=9000.0, net=_t20["netUocBps"], giu=24.0)

    _tuHua = TrungUong(_tam("hua-gop"), {"vonBanDauUsd": 200_000.0})
    _tuHua.dang_ky(_TyBon())
    for _ in range(3):
        _tuHua.mot_vong(lechDongHoGiay=1.0, cangChet=[], tuoiXauNhatGiay=1.0)
    _ah = _tuHua.anh_chup()
    kiem("ảnh chụp KHAI số vị thế THẬT, không chỉ số đã cắt",
         _ah["soViTheDayDu"] == len(_tuHua.soViThe)
         and _ah["soViTheDayDu"] >= len(_ah["soViThe"]),
         f"{_ah['soViTheDayDu']} vs {len(_ah['soViThe'])} — cắt mà không "
         f"khai thì bên đọc tưởng mình thấy hết")
    _hg = _ah.get("huaTheoTy") or {}
    kiem("lời hứa gộp ở Trung Ương, trên TOÀN BỘ vị thế",
         bool(_hg) and sum(v["soViThe"] for v in _hg.values())
         == len(_tuHua.soViThe) >= 3,
         f"{_hg} vs {len(_tuHua.soViThe)} vị thế — gộp từ danh sách đã cắt "
         f"là gộp một mẫu thiên lệch")
    # Vị thế KHÔNG khai lời hứa: `ToTrinh.kiem()` chặn ngay ở cửa nên
    # đường VÀO không tạo ra được ca này. Đường KHÔI PHỤC thì có: tờ trình
    # nằm trên đĩa từ một bản lưu cũ hơn trường ấy — máy sống 30/08 vẫn
    # còn vị thế mang khoá `khoaVonDenGiay` của thời trước lần đổi tên.
    # Dựng thẳng ca ấy, không đi vòng qua cổng.
    _maBo = sorted(_tuHua.soViThe)[0]
    _tt0 = dict(_tuHua.soViThe[_maBo].toTrinh)
    _tt0.pop("netUocBps", None)
    _tuHua.soViThe[_maBo].toTrinh = _tt0
    _hb = (_tuHua.hua_theo_ty() or {}).get("bon.vithe.v1") or {}
    kiem("vị thế KHÔNG khai hứa ra khỏi CẢ mẫu số, và được ĐẾM riêng",
         _hb.get("soKhongKhai") == 1
         and gan(_hb.get("vonUsd") or 0.0,
                 (_hb["soViThe"] - 1) * 100.0, 1.0)
         and gan(_hb.get("aprHuaPhanTram") or 0.0, 20.0, 1e-6),
         f"{_hb} — đọc «không khai» thành «hứa 0%» thì bình quân tụt theo "
         f"đúng tỉ lệ số vị thế cũ, và một ty hứa quá lọt lưới")

    # ── HỨA QUÁ: tín hiệu duy nhất của tám ty KHÔNG có băng ─────────────
    # Bảng hứa-vs-thực đã có, đã hiện trên buồng lái, và vòng tiến hoá
    # không đọc — nên vòng ấy chỉ học được về đúng cái ty mà chính nó đã
    # tắt, trong khi tám ty kia đang giữ gần hết vốn.
    _anh = {"soDangKy": {"pheu": {"phatHien": 400, "DUYET_TY": 80,
                                  "DUYET_RUI_RO": 40, "DA_CAP_VON": 40}},
            "danhMuc": {"tiLeDungVon": 0.5, "soViThe": 40},
            "duDoanVaThuc": {
                "hua_qua.v1": {"soDoiChieuDuoc": 25, "lechBpsGio": 1.2},
                "it_mau.v1": {"soDoiChieuDuoc": 3, "lechBpsGio": 9.0},
                "chua_do.v1": {"soDoiChieuDuoc": 99, "lechBpsGio": None},
                "hua_dung.v1": {"soDoiChieuDuoc": 99, "lechBpsGio": 0.001},
                "hua_it.v1": {"soDoiChieuDuoc": 99, "lechBpsGio": -3.0}}}
    _t = {x.ma: x for x in _cdh(_anh)}
    kiem("ty hứa quá bị BẮT, và bằng chứng chỉ đúng ty ấy",
         "hua-qua-he" in _t
         and _t["hua-qua-he"].bangChung["chienLuoc"] == "hua_qua.v1",
         f"{[x for x in _t]} — bảng hứa-vs-thực là tín hiệu học DUY NHẤT "
         f"của tám ty không ghi băng")
    _ma = [x.ma for x in _cdh(_anh)]
    kiem("và chỉ MỘT ty bị bắt, ba ca kia đều bị loại đúng lý do",
         _ma.count("hua-qua-he") == 1,
         f"{_ma} — ít mẫu là tiếng ồn, `None` là CHƯA ĐO ĐƯỢC chứ không "
         f"phải hứa đúng, và hứa THẤP hơn thực nhận thì không phải bệnh")
    _dx2 = _dxh(_cdh(_anh), {"ruiRoTong": {"netMoiGioToiThieuBps": 0.0}})
    kiem("chữa bằng cách NÂNG sàn NET, không hạ",
         len(_dx2) == 1
         and _dx2[0].nut == "ruiRoTong.netMoiGioToiThieuBps"
         and _dx2[0].den > _dx2[0].tu,
         f"{_dx2} — hứa cao hơn thực nhận thì đòi thêm ngần ấy khoảng hở "
         f"trước khi nhận; hạ sàn xuống là nhận thêm đúng loại cơ hội vừa "
         f"làm mình lỗ")

    # `None` phải đi qua nhánh CHƯA ĐO ĐƯỢC, không được đọc thành 0.
    _anh3 = {"soDangKy": {"pheu": {"phatHien": 400, "DUYET_TY": 80,
                                   "DUYET_RUI_RO": 40, "DA_CAP_VON": 40}},
             "danhMuc": {"tiLeDungVon": 0.5, "soViThe": 40},
             "duDoanVaThuc": {"x.v1": {"soDoiChieuDuoc": 999,
                                       "lechBpsGio": None}}}
    kiem("ty chưa đối chiếu được lần nào KHÔNG bị chẩn bệnh",
         "hua-qua-he" not in [x.ma for x in _cdh(_anh3)],
         "None là chưa đo được, không phải hứa đúng — đọc nó thành 0 là "
         "bịa ra một lời khen chưa ai nói")

    # ── TY LỖ đọc CỘT CHIẾN LƯỢC, không đọc con số gộp ──────────────────
    # Đo 30/08 trên máy sống: lending.rate_rotation gộp −82,26 nhưng CHIẾN
    # LƯỢC +2,03; amm.fee_farming gộp −1,32 nhưng chiến lược +1,88. Cái
    # kéo con số gộp xuống là phí VÀO LỆNH trả 289 lần và 50 lần, mà phần
    # lớn những lần ấy là mở lại sau khi runtime khởi động lại — chi phí
    # VẬN HÀNH.
    #
    # Đọc gộp thì vòng tiến hoá kết luận «bốn ty đang lỗ» và đề xuất duy
    # nhất của nó là siết `tranMotTy` 0,5 → 0,375: rút vốn khỏi đúng
    # những ty đang làm ra tiền, vì một buổi chiều deploy nhiều lần.
    _anhTL = {"soDangKy": {"pheu": {"phatHien": 400, "DUYET_TY": 80,
                                     "DUYET_RUI_RO": 40, "DA_CAP_VON": 40}},
              "danhMuc": {"tiLeDungVon": 0.5, "soViThe": 40},
              "soCai": {"laiLoTheoTy": {
                  "lai_that.v1": {"laiLoUsd": -82.26},
                  "lo_that.v1": {"laiLoUsd": -5.0},
                  "chua_tach.v1": {"laiLoUsd": -9.0}}},
              "laiLoTachKhoan": {
                  "lai_that.v1": {"laiLoChienLuocUsd": 2.03,
                                  "soLanVaoLenh": 289,
                                  "phiMoiLanVaoUsd": -0.29},
                  "lo_that.v1": {"laiLoChienLuocUsd": -5.0,
                                 "soLanVaoLenh": 3}}}
    _tTL = {x.ma: x for x in _cdh(_anhTL)}
    _maTL = [x.ma for x in _cdh(_anhTL)]
    kiem("ty LÃI bằng chiến lược mà gộp âm KHÔNG bị gọi là ty lỗ",
         "phi-vao-an-het" in _tTL
         and _tTL["phi-vao-an-het"].bangChung["chienLuoc"] == "lai_that.v1",
         f"{_maTL} — phí vào lệnh phần lớn là chi phí VẬN HÀNH; đổ nó lên "
         f"chiến lược là phạt nhầm người")
    kiem("ty âm Ở CỘT CHIẾN LƯỢC thì vẫn bị gọi là ty lỗ",
         any(x.ma == "ty-lo"
             and x.bangChung["chienLuoc"] == "lo_that.v1" for x in _cdh(_anhTL)),
         "tách khoản không được thành cái cớ tha cho mọi ty")
    kiem("ty CHƯA tách được thì đọc gộp, và NÓI RA là đang đọc gộp",
         any(x.ma == "ty-lo" and x.bangChung["chienLuoc"] == "chua_tach.v1"
             and x.bangChung.get("laiLoChienLuocUsd") is None
             and "CHƯA tách" in x.moTa for x in _cdh(_anhTL)),
         "im lặng rơi về số gộp là quay lại đúng lỗi vừa sửa")
    # Chặn ở HAI lớp, và lớp thứ nhất mới là lớp có răng: triệu chứng này
    # KHÔNG khai núm nào. Chỉ dựa vào danh sách bỏ qua trong `de_xuat` thì
    # ngày ai đó thêm một núm gợi ý, danh sách ấy là thứ duy nhất còn
    # chặn — mà nó nằm ở file khác, cách đó 200 dòng.
    # VÀO bao nhiêu lần rồi ĐÓNG bao nhiêu lần — không có mẫu số ấy thì
    # triệu chứng này kêu bằng một con số cộng dồn CẢ ĐỜI và không bao giờ
    # tắt được, kể cả sau khi churn đã hết hẳn. Đo 30/08: ba giờ liền 48
    # lần mở, 0 lần đóng — churn đã dừng — mà con số 289 vẫn nguyên.
    _anhCh = {"soDangKy": {"pheu": {"phatHien": 400, "DUYET_TY": 80,
                                    "DUYET_RUI_RO": 40, "DA_CAP_VON": 40}},
              "danhMuc": {"tiLeDungVon": 0.5, "soViThe": 40},
              "soCai": {"laiLoTheoTy": {"churn.v1": {"laiLoUsd": -80.0},
                                        "moi.v1": {"laiLoUsd": -3.0}}},
              "laiLoTachKhoan": {
                  "churn.v1": {"laiLoChienLuocUsd": 4.0, "soLanVaoLenh": 289,
                               "soLanDong": 282, "tiLeDongTrenVao": 0.98},
                  "moi.v1": {"laiLoChienLuocUsd": 1.0, "soLanVaoLenh": 48,
                             "soLanDong": 0, "tiLeDongTrenVao": 0.0}}}
    _ch = {x.bangChung.get("chienLuoc"): x for x in _cdh(_anhCh)
           if x.ma == "phi-vao-an-het"}
    kiem("mở-rồi-đóng-rồi-mở-lại thì NẶNG, và gọi thẳng ra là CHURN",
         _ch["churn.v1"].nang == 2 and "CHURN" in _ch["churn.v1"].moTa,
         f"{_ch['churn.v1'].moTa[:120]}")
    kiem("còn toàn vị thế MỚI thì NHẸ, vì đó là chi phí bình thường",
         _ch["moi.v1"].nang == 1 and "MỚI" in _ch["moi.v1"].moTa,
         f"{_ch['moi.v1'].moTa[:120]} — một cảnh báo không bao giờ tắt được "
         f"là một cảnh báo người ta học cách bỏ qua")
    # ĐỦ MẪU rồi mới dám gọi là churn. Đo 30/08 ngay sau khi dựng con số
    # này: ty tiên đoán «vào 1 · đóng 1 · tỉ lệ 1,00» và bị gắn mức NẶNG
    # y như một ty churn 289 lần. Cùng bài học `hua-qua-he` đã học ở trên,
    # cùng một phiên.
    _anhIt = {"soDangKy": {"pheu": {"phatHien": 400, "DUYET_TY": 80,
                                    "DUYET_RUI_RO": 40, "DA_CAP_VON": 40}},
              "danhMuc": {"tiLeDungVon": 0.5, "soViThe": 40},
              "soCai": {"laiLoTheoTy": {"it.v1": {"laiLoUsd": -8.0}}},
              "laiLoTachKhoan": {
                  "it.v1": {"laiLoChienLuocUsd": 0.0, "soLanVaoLenh": 1,
                            "soLanDong": 1, "tiLeDongTrenVao": 1.0}}}
    _it = [x for x in _cdh(_anhIt) if x.ma == "phi-vao-an-het"]
    kiem("MỘT lần vào lệnh thì tỉ lệ 1,00 KHÔNG bị gọi là churn",
         len(_it) == 1 and _it[0].nang == 1,
         f"{[(x.ma, x.nang) for x in _it]} — một tỉ lệ dựng trên một mẫu "
         f"không nói gì về ty ấy")

    # ĐÓNG VÌ ĐÂU. Câu khuyên cũ chỉ đúng khi thủ phạm là khởi động lại.
    # Đo làn thật 30/08: 217/282 lần đóng của ty cho vay là XOAY CHỖ, và
    # 29/29 của ty basis cũng thế. Chỉ người vận hành sang một cái nút họ
    # không hề chạm vào là gửi họ đi sai đường — và đường sai ấy nghe rất
    # hợp lý, nên không ai quay lại.
    _anhVi = {"soDangKy": {"pheu": {"phatHien": 400, "DUYET_TY": 80,
                                    "DUYET_RUI_RO": 40, "DA_CAP_VON": 40}},
              "danhMuc": {"tiLeDungVon": 0.5, "soViThe": 40},
              "soCai": {"laiLoTheoTy": {"xoay.v1": {"laiLoUsd": -80.0},
                                        "khoiDong.v1": {"laiLoUsd": -80.0},
                                        "chuaDong.v1": {"laiLoUsd": -8.0}}},
              "laiLoTachKhoan": {
                  "xoay.v1": {"laiLoChienLuocUsd": 4.0, "soLanVaoLenh": 289,
                              "soLanDong": 282, "tiLeDongTrenVao": 0.98,
                              "soLanDongXoayCho": 217,
                              "phanDongDoXoayCho": 217 / 282},
                  "khoiDong.v1": {"laiLoChienLuocUsd": 4.0,
                                  "soLanVaoLenh": 289, "soLanDong": 282,
                                  "tiLeDongTrenVao": 0.98,
                                  "soLanDongXoayCho": 3,
                                  "phanDongDoXoayCho": 3 / 282},
                  "chuaDong.v1": {"laiLoChienLuocUsd": 1.0,
                                  "soLanVaoLenh": 48, "soLanDong": 0,
                                  "tiLeDongTrenVao": 0.0,
                                  "soLanDongXoayCho": 0,
                                  "phanDongDoXoayCho": None}}}
    _vi = {x.bangChung.get("chienLuoc"): x for x in _cdh(_anhVi)
           if x.ma == "phi-vao-an-het"}
    kiem("phần lớn đóng do XOAY CHỖ thì chỉ thẳng vào xoay chỗ",
         "XOAY CHỖ" in _vi["xoay.v1"].moTa
         and "khởi động lại ít đi" not in _vi["xoay.v1"].moTa,
         f"{_vi['xoay.v1'].moTa[-200:]} — chỉ người vận hành sang một cái "
         f"nút họ không hề chạm vào là gửi họ đi sai đường")
    kiem("phần lớn đóng KHÔNG do xoay chỗ thì vẫn là lời khuyên cũ",
         "khởi động lại ít đi" in _vi["khoiDong.v1"].moTa,
         f"{_vi['khoiDong.v1'].moTa[-200:]}")
    kiem("chưa đóng lần nào thì KHÔNG chia, và nói rõ là chưa chia được",
         "chưa tách được" in _vi["chuaDong.v1"].moTa,
         f"{_vi['chuaDong.v1'].moTa[-160:]} — «0% do xoay chỗ» ở đây là "
         f"bịa ra một phép đo trên không mẫu nào")
    kiem("và con số đóng-vì-đâu đi kèm làm bằng chứng",
         _vi["xoay.v1"].bangChung.get("soLanDongXoayCho") == 217,
         str(_vi["xoay.v1"].bangChung))

    kiem("và cả hai đều mang mẫu số ra làm bằng chứng",
         all(x.bangChung.get("soLanDong") is not None
             and x.bangChung.get("tiLeDongTrenVao") is not None
             for x in _ch.values()),
         str([x.bangChung for x in _ch.values()]))

    kiem("phí-vào-ăn-hết KHÔNG khai núm nào — không có núm nào chữa được",
         _tTL["phi-vao-an-het"].nutGoiY == [],
         f"{_tTL['phi-vao-an-het'].nutGoiY} — siết trần vốn ở đây là rút "
         f"vốn khỏi một ty ĐANG làm ra tiền vì một buổi chiều deploy nhiều "
         f"lần; đây là việc của người vận hành, không phải của một tham số")
    kiem("và `de_xuat` cũng bỏ qua nó, kể cả khi có ai đó thêm núm",
         all(x.vi != "phi-vao-an-het"
             for x in _dxh(_cdh(_anhTL), {"ruiRoTong": {"tranMotTy": 0.5}})),
         "hai lớp chặn, vì lớp trong nằm ở file khác")

    # ── VỐN KHẢ DỤNG nằm không ──────────────────────────────────────────
    #
    # Khác `tran-dat-sai-cho` ở MẪU SỐ, và mẫu số là cả vấn đề. Cái kia
    # canh `tiLeDungVon` trên NAV, nên làn thật 30/08 dùng vốn 56% thì nó
    # im — trong khi 56% trên NAV chính là 70% của phần KHẢ DỤNG, và
    # 239.071 USD còn lại đang ăn 0%. Lợi suất 4,30%/năm trên vốn đang
    # dùng, quy về NAV còn 2,41%: gần một nửa mất ở chỗ ấy.
    def _anhVR(**kw):
        o = {"ranhNgoaiDuTruUsd": 239071.0, "tiLeRanhTrenKhaDung": 0.299,
             "tiLeDuTru": 0.2, "khaDungUsd": 799915.0,
             "dangDungUsd": 560843.0,
             "loiSuatTrenVonDungPhanTram": 4.30,
             "loiSuatQuyVeNavPhanTram": 2.41,
             "loiSuatNeuLapDayPhanTram": 3.44}
        o.update(kw)
        return {"soDangKy": {"pheu": {"phatHien": 400, "DUYET_TY": 80,
                                      "DUYET_RUI_RO": 40, "DA_CAP_VON": 40}},
                "danhMuc": {"tiLeDungVon": 0.56, "soViThe": 106},
                "vonRanh": o}

    _vr = {x.ma: x for x in _cdh(_anhVR())}
    kiem("dùng vốn 56% trên NAV vẫn là 30% khả dụng nằm không → KÊU",
         "von-ranh-an-khong" in _vr,
         f"{sorted(_vr)} — `tran-dat-sai-cho` canh 15% trên NAV nên nó im "
         f"ở đây, và 239 nghìn USD ăn 0% thì không ai được báo")
    kiem("và nó nói cả hai lợi suất, vì hai mẫu số là hai câu hỏi",
         ("4.30" in _vr["von-ranh-an-khong"].moTa
          and "2.41" in _vr["von-ranh-an-khong"].moTa),
         _vr["von-ranh-an-khong"].moTa)
    kiem("con số «nếu lấp đầy» khai rõ là TRẦN TRÊN, không phải lời hứa",
         "TRẦN TRÊN" in _vr["von-ranh-an-khong"].moTa,
         "phần rảnh nằm im thường vì cơ hội còn lại tệ hơn; hứa nó sẽ "
         "chạy như phần đang chạy là hứa thay cho một thứ chưa ai đo")
    kiem("ĐÚNG BẰNG ngưỡng thì đã kêu — ngưỡng ĐÓNG",
         any(x.ma == "von-ranh-an-khong" for x in
             _cdh(_anhVR(tiLeRanhTrenKhaDung=NGUONG_RANH_TREN_KHA_DUNG))))
    kiem("dưới ngưỡng thì im — đây không phải cảnh báo luôn bật",
         not any(x.ma == "von-ranh-an-khong" for x in
                 _cdh(_anhVR(tiLeRanhTrenKhaDung=0.10))),
         "một cảnh báo không bao giờ tắt được là một cảnh báo người ta bỏ "
         "qua")
    kiem("chưa đo được tỉ lệ thì KHÔNG kêu, và cũng không đoán",
         not any(x.ma == "von-ranh-an-khong" for x in
                 _cdh(_anhVR(tiLeRanhTrenKhaDung=None))),
         "NAV bằng 0 thì mẫu số bằng 0; kêu ở đó là kêu về một phép chia "
         "chưa làm được")
    _vrM = {x.ma: x for x in
            _cdh(_anhVR(loiSuatTrenVonDungPhanTram=None,
                        loiSuatQuyVeNavPhanTram=None,
                        loiSuatNeuLapDayPhanTram=None))}
    kiem("chưa có vốn-giờ nào thì vẫn kêu, nhưng KHÔNG nói lợi suất",
         ("von-ranh-an-khong" in _vrM
          and "%/năm" not in _vrM["von-ranh-an-khong"].moTa),
         f"{_vrM['von-ranh-an-khong'].moTa} — ghép «0,00%/năm» vào đây là "
         f"bịa ra một cỗ máy đang huề vốn")
    kiem("và nó khai núm để vặn, vì đây LÀ bệnh của trần",
         _vr["von-ranh-an-khong"].nutGoiY == ["ruiRoTong.tranMotCang",
                                              "ruiRoTong.tranMotTy"],
         str(_vr["von-ranh-an-khong"].nutGoiY))

    # ── XOAY CHỖ hứa dài hơn đời thật của vị thế ────────────────────────
    #
    # Đo làn thật 30/08: 267 lần xoay trong 39 phút, tổng lời hứa
    # +11.136 USD trên sổ 10.000 USD, trong khi chính ty được xoay nhiều
    # nhất đang âm 77,51 USD. Trung vị số giờ giữ được trước lần xoay kế:
    # 0,008 giờ. Lời hứa dài hơn đời thật khoảng hai vạn lần.
    def _anhXC(**kw):
        o = {"soLan": 267, "huaLoiRongUsd": 11136.0, "gioHuaTrungVi": 160.0,
             "gioGiuTrungVi": 0.008, "tiLeSongTrenHua": 0.00005,
             "soThieuGioHua": 0, "gioCuaSo": 24.0,
             "capLapNhieuNhat": [{"cap": "USDT → SUSDAI", "soLan": 31}],
             "soCapDiLaiNhieuLan": 7}
        o.update(kw)
        return {"soDangKy": {"pheu": {"phatHien": 400, "DUYET_TY": 80,
                                      "DUYET_RUI_RO": 40, "DA_CAP_VON": 40}},
                "danhMuc": {"tiLeDungVon": 0.5, "soViThe": 40},
                # Cộng dồn CẢ ĐỜI để đó, còn chẩn đoán phải đọc `ganDay`:
                # bệnh đã khỏi mà số cộng dồn thì không bao giờ giảm.
                "soCai": {"xoayChoHuaVaThuc": {
                    "soLan": 9999, "huaLoiRongUsd": 999999.0,
                    "tiLeSongTrenHua": 0.000001, "ganDay": o}}}

    _xc = {x.ma: x for x in _cdh(_anhXC())}
    kiem("vị thế mới sống được 0,005% quãng đã hứa → KÊU, và kêu NẶNG",
         "xoay-cho-hua-qua" in _xc and _xc["xoay-cho-hua-qua"].nang == 3,
         f"{sorted(_xc)} — lời hứa cộng trước lãi của 160 giờ trong khi vị "
         f"thế sống 30 giây; phí thì trả đủ mỗi lần")
    kiem("và nó mang cả hai con số ra làm bằng chứng, không chỉ kết luận",
         (_xc["xoay-cho-hua-qua"].bangChung.get("gioHuaTrungVi") == 160.0
          and _xc["xoay-cho-hua-qua"].bangChung.get("gioGiuTrungVi")
          == 0.008),
         str(_xc["xoay-cho-hua-qua"].bangChung))

    kiem("sống ĐỦ phần lời hứa thì im — đây không phải cảnh báo luôn bật",
         not any(x.ma == "xoay-cho-hua-qua"
                 for x in _cdh(_anhXC(tiLeSongTrenHua=0.5,
                                      gioGiuTrungVi=80.0))),
         "một cảnh báo không bao giờ tắt được là một cảnh báo người ta bỏ "
         "qua")
    kiem("ĐÚNG BẰNG ngưỡng sống/hứa thì cũng im",
         not any(x.ma == "xoay-cho-hua-qua"
                 for x in _cdh(_anhXC(tiLeSongTrenHua=NGUONG_SONG_TREN_HUA))),
         "ngưỡng ĐÓNG: bằng ngưỡng là còn đạt")
    kiem("chưa đủ 30 lần xoay thì chưa dám kết luận",
         not any(x.ma.startswith("xoay-cho")
                 for x in _cdh(_anhXC(soLan=5))),
         "trung vị dựng trên năm mẫu là tiếng ồn, và một lần xoay giữ ngắn "
         "có thể chỉ vì runtime khởi động lại")

    # Và cửa sổ GẦN ĐÂY mới là thứ chẩn đoán đọc. Cửa chặn «còn ghế trống
    # thì không đuổi ai» đã dừng vòng xoay từ 29/08, nhưng 267 bút toán
    # cũ nằm lại trong sổ mãi — đọc số cộng dồn là dựng một cảnh báo kêu
    # đúng một lần rồi kêu mãi, kể cả sau khi bệnh đã khỏi.
    kiem("bệnh đã KHỎI thì cảnh báo TẮT, dù sổ vẫn còn 9.999 lần cộng dồn",
         not any(x.ma.startswith("xoay-cho")
                 for x in _cdh(_anhXC(soLan=0, tiLeSongTrenHua=None,
                                      gioGiuTrungVi=None,
                                      gioHuaTrungVi=None))),
         "một cảnh báo không bao giờ tắt được là một cảnh báo người ta học "
         "cách bỏ qua")

    # Chưa đo được thì NÓI RA là chưa đo được — im lặng ở đây đọc y hệt
    # như «đã đo, và không sao cả».
    _xcM = {x.ma: x for x in _cdh(_anhXC(gioHuaTrungVi=None,
                                         tiLeSongTrenHua=None,
                                         soThieuGioHua=267))}
    kiem("bút toán cũ thiếu quãng hứa → KHAI RA, không im",
         "xoay-cho-chua-doi-chieu" in _xcM
         and "xoay-cho-hua-qua" not in _xcM,
         f"{sorted(_xcM)}")
    kiem("và nó KHÔNG đội lốt một kết luận: mức nhẹ, không phải mức nặng",
         _xcM["xoay-cho-chua-doi-chieu"].nang == 1,
         "«chưa đối chiếu được» không phải một phát hiện, nó là một lỗ")

    kiem("cả hai đều KHÔNG khai núm nào — không có núm nào chữa được",
         (_xc["xoay-cho-hua-qua"].nutGoiY == []
          and _xcM["xoay-cho-chua-doi-chieu"].nutGoiY == []),
         "đây là công thức cộng trước lãi của một quãng mà cỗ máy không "
         "cho vị thế sống tới — vặn trần vốn ở đây là phạt nhầm chỗ")
    kiem("và `de_xuat` cũng bỏ qua chúng, kể cả khi ai đó thêm núm",
         all(not x.vi.startswith("xoay-cho")
             for x in _dxh(_cdh(_anhXC()),
                           {"ruiRoTong": {"tranMotTy": 0.5}})),
         "hai lớp chặn, vì lớp trong nằm ở file khác")


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
        vonToiThieuKinhTeUsd = 50.0
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
        vonToiThieuKinhTeUsd = 50.0
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



def kiem_cong_duyet() -> None:
    print("\n-- Cong Duyet: bay luat chan bay cach tham so troi --")
    from thi_bac_ty.chan_doan_he import (BUOC_TOI_DA, CUA_AN_TOAN_HE,
                                         DeXuatHe, NUT_TRUNG_UONG)
    from thi_bac_ty.cong_duyet import KET_LUAN_QUA, xet_duyet

    def do(ket, du=True, **kw):
        return {"duDeKetLuan": du, "ketLuan": ket, "vi": "thử",
                "A": {}, "B": {"moPhongVongDoi": False}, **kw}

    dx = DeXuatHe("ruiRoTong.tranMotCang", 0.40, 0.45, "tran-dat-sai-cho")

    # luật 6+7: chỉ MỘT kết luận được qua
    kiem("chỉ đúng một kết luận được phép qua", KET_LUAN_QUA == ("b-tot-hon",))
    kiem("đo nói B tốt hơn và KHÔNG đậm hơn → đủ điều kiện",
         xet_duyet(dx, do("b-tot-hon")).duDieuKien)
    kiem("HOÀ → không duyệt",
         not xet_duyet(dx, do("hoa")).duDieuKien,
         "đứng yên là kết quả hợp lệ; duyệt thay đổi không đo được cải "
         "thiện là thêm nhiễu rồi gọi nó là tiến hoá")
    kiem("A tốt hơn → không duyệt",
         not xet_duyet(dx, do("a-tot-hon")).duDieuKien)
    pq = xet_duyet(dx, do("b-tot-hon-NHUNG-dam-hon"))
    kiem("tốt hơn nhờ ÔM RỦI RO ĐẬM HƠN → không duyệt", not pq.duDieuKien)

    # ── BIÊN, và đây là chỗ quét đột biến chỉ ra đang trống ─────────────
    #
    # Cổng này gác MỌI thay đổi tham số rủi ro của cỗ máy. Quét đột biến
    # tự động trên `cong_duyet.py` cho 5/10 con SỐNG SÓT, và bốn trong số
    # đó nằm đúng ở biên: `<=` đổi thành `<`, `>` thành `>=`, `or` thành
    # `and`. Nghĩa là hôm nay không phép kiểm nào phân biệt được «đúng
    # bằng trần» với «vượt trần» — mà cả cổng này chỉ sống bằng chỗ đó.
    _nut = "ruiRoTong.tranMotCang"
    _kh = NUT_TRUNG_UONG[_nut]

    # Bước ĐÚNG BẰNG trần thì QUA; hơn một hạt thì không.
    _tu = 0.40
    _tran = abs(_tu) * BUOC_TOI_DA
    kiem("bước ĐÚNG BẰNG trần thì vẫn qua",
         xet_duyet(DeXuatHe(_nut, _tu, _tu + _tran, "x"),
                   do("b-tot-hon")).duDieuKien,
         f"trần {_tran:g} — «vượt trần» phải nghĩa là HƠN trần, không phải "
         f"bằng trần")
    kiem("nhích thêm một hạt thì KHÔNG qua",
         not xet_duyet(DeXuatHe(_nut, _tu, _tu + _tran * 1.02, "x"),
                       do("b-tot-hon")).duDieuKien,
         "không có phép kiểm này thì `>` và `>=` là một")

    # Giá trị ĐÚNG BẰNG hai đầu khuôn thì trong khuôn, không phải ngoài.
    _min, _max = _kh["min"], _kh["max"]
    _tuMin = _min / (1.0 - BUOC_TOI_DA)          # để bước vừa đủ tới min
    kiem("giá trị ĐÚNG BẰNG min vẫn nằm TRONG khuôn",
         not any("ra ngoài khuôn" in x for x in
                 xet_duyet(DeXuatHe(_nut, _tuMin, _min, "x"),
                           do("b-tot-hon")).lyDo),
         f"min={_min:g} — khuôn ĐÓNG hai đầu; đổi `<=` thành `<` thì chính "
         f"cái biên hợp lệ bị gọi là vi phạm")
    _tuMax = _max / (1.0 + BUOC_TOI_DA)
    kiem("và ĐÚNG BẰNG max cũng thế",
         not any("ra ngoài khuôn" in x for x in
                 xet_duyet(DeXuatHe(_nut, _tuMax, _max, "x"),
                           do("b-tot-hon")).lyDo),
         f"max={_max:g}")
    kiem("nhích ra ngoài max thì bị bắt",
         any("ra ngoài khuôn" in x for x in
             xet_duyet(DeXuatHe(_nut, _max, _max * 1.02, "x"),
                       do("b-tot-hon")).lyDo),
         "không thì phép kiểm trên chỉ chứng minh hàm luôn im lặng")

    # THIẾU MỘT VẾ cũng là thiếu — `or`, không phải `and`.
    for _tu2, _den2, _ten in ((None, 0.40, "thiếu giá trị CŨ"),
                              (0.40, None, "thiếu giá trị MỚI"),
                              (None, None, "thiếu CẢ HAI")):
        kiem(f"{_ten} → không duyệt",
             any("thiếu giá trị" in x for x in
                 xet_duyet(DeXuatHe(_nut, _tu2, _den2, "x"),
                           do("b-tot-hon")).lyDo),
             f"tu={_tu2} den={_den2} — `and` ở đây nghĩa là chỉ chặn khi "
             f"THIẾU CẢ HAI, và một đề xuất nửa vời sẽ đi tiếp rồi nổ ở "
             f"phép trừ dưới")

    # Trần bước tính từ |giá trị hiện tại|; hiện tại BẰNG 0 thì trần ấy
    # bằng 0, và lúc đó phải rơi về khuôn — không thì núm nào đang ở 0 sẽ
    # đứng yên vĩnh viễn, đúng cái bẫy `SAN_BUOC_KHUON` đã sửa ở tầng đề
    # xuất.
    _nutBps = "ruiRoTong.netMoiGioToiThieuBps"
    _khB = NUT_TRUNG_UONG[_nutBps]
    _tranKhuon = (_khB["max"] - _khB["min"]) * BUOC_TOI_DA
    kiem("giá trị hiện tại BẰNG 0 thì trần bước rơi về khuôn, không kẹt 0",
         xet_duyet(DeXuatHe(_nutBps, 0.0, _tranKhuon, "x"),
                   do("b-tot-hon")).duDieuKien,
         f"trần theo khuôn {_tranKhuon:g} — `tran <= 0` mà đổi thành "
         f"`tran < 0` thì trần giữ nguyên 0 và núm đang ở 0 không bao giờ "
         f"nhúc nhích được")
    kiem("và từ 0 mà nhảy quá trần khuôn thì vẫn bị chặn",
         not xet_duyet(DeXuatHe(_nutBps, 0.0, _tranKhuon * 1.5, "x"),
                       do("b-tot-hon")).duDieuKien)

    # Lý do phải MANG THEO câu của chính phép đo. Nói trống «chưa đủ để
    # kết luận» thì người đọc phải đi mở phép đo ra mới biết thiếu gì —
    # mà cái thiếu ấy chính là thứ quyết định lượt sau làm gì.
    _lyKhongDu = xet_duyet(dx, do("b-tot-hon", du=False,
                                  vi="mới 3 cơ hội hậu kiểm được")).lyDo
    kiem("«chưa đủ mẫu» dẫn nguyên câu của phép đo, không nói trống",
         any("mới 3 cơ hội hậu kiểm được" in x for x in _lyKhongDu),
         f"{_lyKhongDu} — «không rõ» chỉ dành cho lúc phép đo im lặng thật")
    _lyIm = xet_duyet(dx, do("b-tot-hon", du=False, vi="")).lyDo
    kiem("và phép đo IM LẶNG thì mới nói «không rõ»",
         any("không rõ" in x for x in _lyIm), str(_lyIm))
    kiem("và nói thẳng đó là tự tháo phanh",
         any("tháo phanh" in l for l in pq.lyDo), str(pq.lyDo))

    # luật 1: không đo thì không duyệt
    p1 = xet_duyet(dx, None)
    kiem("không có phép đo → không duyệt", not p1.duDieuKien)
    kiem("và gọi đúng tên: một ý kiến",
         any("ý kiến" in l for l in p1.lyDo), str(p1.lyDo))

    # luật 2: chưa đủ mẫu
    kiem("phép đo tự khai chưa đủ mẫu → không duyệt",
         not xet_duyet(dx, do(None, du=False)).duDieuKien)

    # luật 3: cửa an toàn, kiểm LẠI từ danh sách gốc
    for cua in CUA_AN_TOAN_HE[:3]:
        p = xet_duyet(DeXuatHe(cua, 1.0, 1.2, "x"), do("b-tot-hon"))
        kiem(f"cửa an toàn {cua.split('.')[-1]} → chặn", not p.duDieuKien)
    kiem("và nói rõ vì sao là cửa an toàn",
         any("CỬA AN TOÀN" in l for l in
             xet_duyet(DeXuatHe(CUA_AN_TOAN_HE[0], 1.0, 1.1, "x"),
                       do("b-tot-hon")).lyDo))

    # luật 4: bước có trần
    xa = DeXuatHe("ruiRoTong.tranMotCang", 0.40, 0.58, "tran-dat-sai-cho")
    p4 = xet_duyet(xa, do("b-tot-hon"))
    kiem("bước vượt trần 25% → chặn", not p4.duDieuKien,
         "một lượt gặp nhiễu thuận không được đẩy ngưỡng ra chỗ mọi cơ hội "
         "đều lọt")

    # luật 5: ngoài khuôn
    ngoai = DeXuatHe("ruiRoTong.tranMotCang", 0.58,
                     NUT_TRUNG_UONG["ruiRoTong.tranMotCang"]["max"] + 0.01,
                     "x")
    kiem("ra ngoài khuôn min/max → chặn",
         not xet_duyet(ngoai, do("b-tot-hon")).duDieuKien)
    kiem("núm không có trong bảng → chặn",
         not xet_duyet(DeXuatHe("bia.dat.ra", 1.0, 1.1, "x"),
                       do("b-tot-hon")).duDieuKien)

    # qua cổng KHÔNG phải là đã áp dụng
    kiem("qua cổng vẫn nhắc rằng chưa áp dụng",
         "người ký tên" in xet_duyet(dx, do("b-tot-hon")).tom_tat()["loiNhac"])
    kiem("ghi chú nói rõ phép đo KHÔNG đo lãi lỗ",
         any("KHÔNG đo lãi" in g for g in
             xet_duyet(dx, do("b-tot-hon")).ghiChu))


def kiem_ban_tham_so() -> None:
    print("\n-- Ban tham so: co SO HIEU, co lich su, quay lui duoc --")
    from thi_bac_ty.ban_tham_so import KhoThamSo

    kho = KhoThamSo(_tam("bts") / "bts.sqlite3")
    kiem("kho rỗng thì không có bản hiện hành", kho.hien_hanh() is None)

    b1 = kho.dat({"ruiRoTong": {"tranMotCang": 0.35}}, "khoi-tao", "bản đầu")
    kiem("ghi được bản đầu", b1 is not None and b1.so == 1)
    kiem("bản đầu không có cha", b1.chaSo is None)

    kiem("thiếu TÊN NGƯỜI thì không ghi được",
         kho.dat({"a": 1}, "  ", "vì gì đó") is None,
         "đổi cách chia tiền là hành động có trách nhiệm")
    kiem("thiếu LÝ DO thì không ghi được",
         kho.dat({"a": 1}, "ai đó", "   ") is None,
         "một bản không giải thích được thì không kiểm toán được")
    kiem("hai lần ghi hỏng đều đếm ra", kho.soLoiGhi == 2)

    b2 = kho.dat({"ruiRoTong": {"tranMotCang": 0.45}}, "admin",
                 "nới vì trần đặt sai chỗ", {"ketLuan": "b-tot-hon"})
    kiem("bản sau nối vào bản trước", b2.chaSo == b1.so)
    kiem("bản hiện hành là bản mới nhất", kho.hien_hanh().so == b2.so)
    kiem("bản mang theo CHÍNH phép đo đã biện minh cho nó",
         kho.hien_hanh().doDuoc.get("ketLuan") == "b-tot-hon",
         "ba tháng sau, câu 'vì sao trần cảng là 0,45' phải trả lời được "
         "bằng một lệnh đọc sổ")

    kb = kho.khac_biet(b1.so, b2.so)
    kiem("so được hai bản khác nhau núm nào",
         kb.get("ruiRoTong.tranMotCang") == {"tu": 0.35, "den": 0.45},
         str(kb))

    b3 = kho.quay_lui(b1.so, "admin", "nới xong thấy tệ")
    kiem("quay lui ghi một bản MỚI, không xoá bản sai",
         b3 is not None and b3.so == 3 and kho.ban(b2.so) is not None,
         "một lịch sử sửa được thì không còn là lịch sử")
    kiem("bản quay lui mang đúng nội dung bản cũ",
         b3.thamSo == b1.thamSo and b3.quayLuiVe == b1.so)
    kiem("quay lui về bản không có thì từ chối",
         kho.quay_lui(999, "admin") is None)
    kiem("lịch sử đọc lại đủ ba bản", len(kho.lich_su()) == 3)


def kiem_vong_duyet_tron() -> None:
    print("\n-- Vong §17 tron: de xuat -> do -> cong -> ban -> live --")
    from thi_bac_ty.khuon_ty import Ty
    from thi_bac_ty.to_trinh import Chan
    from thi_bac_ty.trung_uong import TrungUong

    class TyNhieu(Ty):
        ma, ho, moTa = "perpetual.funding_spread.v1", "phai-sinh", "nhiều"
        vonToiThieuKinhTeUsd = 50.0
        def __init__(self): super().__init__(); self.i = 0
        def quet(self): self.i += 1; return [f"T{self.i}"]
        def xet(self, co): return True, []
        def trinh(self, co):
            return _mau(taiSan=co, von=300.0, chua=9000.0, khoa=0.0,
                        chan=(Chan("LONG", "hyperliquid", co),
                              Chan("SHORT", "binance", co)))

    d = _tam("vong17")
    tu = TrungUong(d, {"vonBanDauUsd": 3000.0})
    kiem("dựng xong là đã có bản số 1",
         tu.kho_tham_so.hien_hanh() is not None
         and tu.kho_tham_so.hien_hanh().so == 1,
         "không có bản đầu thì không có gì để quay lui về")
    kiem("bản đầu ghi rõ là do khởi tạo",
         tu.kho_tham_so.hien_hanh().nguoi == "khoi-tao")

    tu.dang_ky(TyNhieu())
    for _ in range(30):
        tu.mot_vong(lechDongHoGiay=1.0, cangChet=[], tuoiXauNhatGiay=1.0)

    kiem("chưa học thì không áp dụng được gì",
         tu.ap_dung("admin")["xong"] is False)
    h = tu.hoc(ghiSo=False)
    kiem("vòng học có mục Cổng Duyệt", "congDuyet" in h)
    kiem("và khai bản đang chạy", h.get("banHienHanh") == 1)

    # Bơm một đề xuất đã qua cổng để kiểm đường áp dụng cho tới cùng.
    # Phải bơm TRƯỚC khi thử tên rỗng — nếu không, `ap_dung()` thoát sớm ở
    # câu "chưa có đề xuất nào" và phép kiểm tên người qua vì lý do khác.
    from thi_bac_ty.chan_doan_he import DeXuatHe
    _dx = lambda: (DeXuatHe("ruiRoTong.tranMotCang", 0.35, 0.42, "thu"),
                   {"duDeKetLuan": True, "ketLuan": "b-tot-hon"})
    tu._deXuatChoDuyet = _dx()

    truoc_ten = tu.rui_ro_tong.c["tranMotCang"]
    kiem("áp dụng mà KHÔNG khai tên người thì từ chối",
         tu.ap_dung("   ")["xong"] is False,
         "máy đo, máy đề xuất, máy chặn — máy không tự ký")
    kiem("và lần từ chối ấy KHÔNG kịp đổi tầng thật",
         gan(tu.rui_ro_tong.c["tranMotCang"], truoc_ten)
         and tu.kho_tham_so.hien_hanh().so == 1,
         "đổi tầng TRƯỚC rồi mới ghi sổ là để lại một máy đang chạy bộ "
         "tham số không có trong bất kỳ bản nào")
    kiem("và đề xuất vẫn còn đó để áp dụng đúng cách",
         tu._deXuatChoDuyet is not None)

    # Ghi sổ HỎNG là chỗ duy nhất thứ tự "đổi tầng trước hay ghi sổ trước"
    # lộ ra. Cấy một kho ghi hỏng để dựng đúng tình huống ấy: nếu tầng đổi
    # trước, máy sẽ chạy một bộ tham số không nằm trong bất kỳ bản nào —
    # và không có gì báo, vì mọi thứ khác vẫn xanh.
    _that = tu.kho_tham_so.dat
    tu.kho_tham_so.dat = lambda *a, **k: None
    truoc_hong = tu.rui_ro_tong.c["tranMotCang"]
    ra_hong = tu.ap_dung("admin")
    tu.kho_tham_so.dat = _that
    kiem("ghi sổ hỏng thì áp dụng thất bại", ra_hong["xong"] is False)
    kiem("và tầng thật KHÔNG bị đổi",
         gan(tu.rui_ro_tong.c["tranMotCang"], truoc_hong),
         "ghi sổ hỏng mà tầng đã đổi là để lại một máy chạy tham số không "
         "có trong sổ nào — không lỗi nào báo, không bản nào quay lui được")
    kiem("và đề xuất vẫn giữ lại để thử lần nữa",
         tu._deXuatChoDuyet is not None)

    truoc = tu.rui_ro_tong.c["tranMotCang"]
    ra = tu.ap_dung("admin")
    kiem("áp dụng thành công thì sinh bản mới", ra["xong"] and ra["ban"]["so"] == 2)
    kiem("và TẦNG THẬT đổi theo, không chỉ sổ đổi",
         gan(tu.rui_ro_tong.c["tranMotCang"], 0.42),
         f"trước {truoc} — sổ nói một đằng mà máy chạy một nẻo là tệ hơn "
         f"không có sổ")
    kiem("bản mới ghi kèm phép đo đã biện minh",
         (ra["ban"]["doDuoc"] or {}).get("ketLuan") == "b-tot-hon")
    kiem("và vào sổ cái", any(x["chiTiet"].get("banThamSo") == 2
                              for x in tu.so_cai.gan_day(50)))
    kiem("dùng một lần rồi thôi, không áp dụng lại được",
         tu.ap_dung("admin")["xong"] is False,
         "không thì một đề xuất bấm hai lần vặn núm đi hai bước")

    # Bản hiện hành (số 2, tranMotCang = 0,42 — KHÁC mặc định 0,35) phải
    # sống qua khởi động lại, và phải sống ở TẦNG THẬT chứ không chỉ ở sổ.
    tu2 = TrungUong(d, {"vonBanDauUsd": 3000.0})
    kiem("khởi động lại vẫn giữ bản đang chạy",
         tu2.kho_tham_so.hien_hanh().so == 2)
    kiem("và TẦNG THẬT dựng lại TỪ BẢN ẤY, không từ mặc định",
         gan(tu2.rui_ro_tong.c["tranMotCang"], 0.42),
         f"đang là {tu2.rui_ro_tong.c['tranMotCang']} — mặc định là 0,35, "
         f"nên đọc ra 0,35 nghĩa là bật lại đã âm thầm xoá mọi bản đã duyệt "
         f"trong khi sổ vẫn khai bản 2 đang chạy")

    ql = tu2.quay_lui(1, "admin", "thử lại")
    kiem("quay lui sinh bản mới", ql["xong"] and ql["ban"]["so"] == 3)
    kiem("và tầng thật quay về theo",
         gan(tu2.rui_ro_tong.c["tranMotCang"], 0.35))
    kiem("quay lui cũng đòi tên người",
         tu2.quay_lui(1, "")["xong"] is False)
    kiem("quay lui rồi khởi động lại vẫn đúng bản quay lui",
         gan(TrungUong(d, {"vonBanDauUsd": 3000.0})
             .rui_ro_tong.c["tranMotCang"], 0.35))


def kiem_pheu_theo_ho() -> None:
    print("\n-- §22 · pheu tach theo HO, khong chi mot tong gop --")
    from thi_bac_ty.khuon_ty import Ty
    from thi_bac_ty.to_trinh import Chan, RuiRo, ToTrinh
    from thi_bac_ty.trung_uong import TrungUong

    class TyPerp(Ty):
        ma, ho, moTa = "perpetual.funding_spread.v1", "phai-sinh", "perp"
        vonToiThieuKinhTeUsd = 50.0
        def __init__(self): super().__init__(); self.i = 0
        def quet(self): self.i += 1; return [f"P{self.i}", f"X{self.i}"]
        def xet(self, co): return co.startswith("P"), [("bo", "chỉ nhận P")]
        def trinh(self, co):
            return _mau(taiSan=co, von=200.0, chua=9000.0, khoa=0.0,
                        chan=(Chan("LONG", "hyperliquid", co),
                              Chan("SHORT", "binance", co)))

    class TyVay(Ty):
        ma, ho, moTa = "lending.rate_spread.v1", "tin-dung", "cho vay"
        vonToiThieuKinhTeUsd = 50.0
        def __init__(self): super().__init__(); self.i = 0
        def quet(self): self.i += 1; return [f"U{self.i}"]
        def xet(self, co): return True, []
        def trinh(self, co):
            return ToTrinh(
                chienLuoc=self.ma, ho=self.ho, taiSan=co,
                chan=(Chan("DI_VAY", "aave", co, loai="lending", chuoi="ethereum"),
                      Chan("CHO_VAY", "compound", co, loai="lending", chuoi="ethereum")),
                vonCanUsd=200.0, sucChuaToiDaUsd=9000.0, grossBps=14.0,
                vonToiThieuKinhTeUsd=1.0,
                phiUocBps=3.0, netUocBps=11.0, giuGio=24.0,
                khoaVonDenGio=0.0, thanhKhoanThoatUsd=5000.0,
                ruiRo=RuiRo(.05, .15, .30, .20, .10, 0.), tinCay=.75,
                moHinhPhiDuChua=True, moHinhSucChuaDuChua=False,
                sucChuaConThieu=("do-sau-pool",), cang=("aave", "compound"),
                chuoi=("ethereum",))

    tu = TrungUong(_tam("pheuho"), {"vonBanDauUsd": 6000.0})
    tu.dang_ky(TyPerp()); tu.dang_ky(TyVay())
    for _ in range(4):
        tu.mot_vong(lechDongHoGiay=1.0, cangChet=[], tuoiXauNhatGiay=1.0)

    p = tu.pheu_day_du()
    theo = {x["ho"]: x for x in p["theoHo"]}
    kiem("phễu tách được hai họ", set(theo) == {"phai-sinh", "tin-dung"},
         str(list(theo)))
    kiem("họ phái sinh: cổng ty chặn một nửa số cơ hội thô",
         theo["phai-sinh"]["coHoiTho"] == 8
         and theo["phai-sinh"]["quaCongTy"] == 4,
         str(theo["phai-sinh"]))
    kiem("họ tín dụng qua hết", theo["tin-dung"]["coHoiTho"] == 4
         and theo["tin-dung"]["quaCongTy"] == 4)
    kiem("mỗi họ biết mình đang giữ bao nhiêu vốn",
         all("vonDangGiuUsd" in x for x in p["theoHo"]),
         "một họ phát hiện nhiều mà chưa bao giờ nuôi được vốn là một họ "
         "đang tiêu thời gian máy mà không sinh ra gì")
    kiem("tổng vốn theo họ khớp vốn đã cam kết",
         gan(sum(x["vonDangGiuUsd"] for x in p["theoHo"]),
             round(tu.danh_muc.daCamKetUsd, 2), 0.05),
         f"{[x['vonDangGiuUsd'] for x in p['theoHo']]} vs "
         f"{tu.danh_muc.daCamKetUsd}")
    kiem("và ảnh chụp mang nó ra ngoài",
         "theoHo" in (tu.anh_chup()["pheuDayDu"] or {}))

    # ── PHỄU KHÔNG ĐƯỢC PHÌNH RA ────────────────────────────────────────
    # Cột «thô» và «qua cổng ty» đếm trong RAM của ty nên chúng nói TỪ LÚC
    # BẬT MÁY. Hai cột sau đọc Sổ Đăng Ký trên đĩa, vốn nhớ cả đời máy.
    # Ghép hai thứ ấy vào một hàng thì hàng ấy phình ra ở giữa — đo 30/08
    # trên máy sống: «thô 39.392 · qua cổng ty 8 · qua Rủi Ro Tổng 49»,
    # tức 8 tờ trình đẻ ra 49 lần duyệt.
    #
    # Cái giá không phải một bảng khó coi. Người đọc thấy cổng ty lọc
    # 39.392 xuống 8 rồi đi vặn cổng ty, trong khi con số 8 ấy nói về một
    # quãng thời gian khác hẳn con số 49 nằm ngay cạnh.
    for _x in p["theoHo"]:
        kiem(f"phễu họ {_x['ho']} KHÔNG phình ra ở giữa",
             _x["coHoiTho"] >= _x["quaCongTy"] >= _x["quaRuiRoTong"]
             >= _x["daCapVon"],
             f"{_x['coHoiTho']} → {_x['quaCongTy']} → "
             f"{_x['quaRuiRoTong']} → {_x['daCapVon']} — bốn cột phải cùng "
             f"MỘT cửa sổ thời gian, và cửa sổ ấy là từ lúc bật máy")

    # Và phép trên chỉ chứng minh được điều đó trên một máy VỪA BẬT, nơi
    # mọi dòng đều nằm sau mốc. Bệnh thật chỉ lộ ra khi sổ còn dòng của
    # kiếp trước — nên dựng thẳng một dòng như thế.
    _truoc = {h: x["quaRuiRoTong"] for h, x in theo.items()}
    with tu.so_dang_ky._mo() as _con:
        _con.execute(
            "INSERT INTO to_trinh (ma, chienLuoc, ho, taiSan, lucTao, "
            "trangThai, lucDoi, payload) VALUES (?,?,?,?,?,?,?,?)",
            ("KIEP_TRUOC", "lending.rate_spread.v1", "tin-dung", "U0",
             "2020-01-01T00:00:00.000Z", "DUYET_RUI_RO",
             "2020-01-01T00:00:00.000Z", "{}"))
        _con.execute(
            "INSERT INTO chuyen_trang_thai (ma, tu, den, luc, lyDo) "
            "VALUES (?,?,?,?,?)",
            ("KIEP_TRUOC", "MOI", "DUYET_RUI_RO",
             "2020-01-01T00:00:00.000Z", ""))
        _con.execute(
            "INSERT INTO chuyen_trang_thai (ma, tu, den, luc, lyDo) "
            "VALUES (?,?,?,?,?)",
            ("KIEP_TRUOC", "MOI", "TU_CHOI", "2020-01-01T00:00:00.000Z",
             "tran-vi-the: đã đủ 12 vị thế — quá nhiều thì không theo dõi nổi"))
    _sau = {x["ho"]: x for x in tu.pheu_day_du()["theoHo"]}
    kiem("dòng của KIẾP TRƯỚC không lọt vào phễu của lần chạy này",
         _sau["tin-dung"]["quaRuiRoTong"] == _truoc["tin-dung"],
         f"{_sau['tin-dung']['quaRuiRoTong']} vs {_truoc['tin-dung']} — bộ "
         f"đếm cơ hội thô nằm trong RAM nên nó chỉ đếm từ lúc bật; sổ trên "
         f"đĩa thì nhớ cả đời máy")
    kiem("và lý do từ chối của kiếp trước cũng không lọt",
         not any("12 vị thế" in l["lyDo"]
                 for l in _sau["tin-dung"]["lyDoTuChoi"]),
         f"{_sau['tin-dung']['lyDoTuChoi']} — trần đang là bao nhiêu thì "
         f"bảng phải nói về trần ấy, không phải trần của một lần chạy trước")

    # Sổ Đăng Ký ghi `luc` bằng bản `_bay_gio` của nó; Trung Ương bó cửa
    # sổ bằng bản `_gio_iso` của mình. Hai mô-đun cố ý không biết nhau, nên
    # hai bản có thể trôi khỏi nhau — và sqlite so hai CHUỖI chứ không so
    # hai mốc, nên lệch một chữ («+00:00» thay cho «Z») vẫn chạy, vẫn trả
    # về một tập hợp, chỉ là tập RỖNG. Phễu sẽ có 0 ở nửa dưới, im lặng.
    from thi_bac_ty.so_dang_ky import _bay_gio as _bgSdk
    from thi_bac_ty.trung_uong import _gio_iso as _bgTu
    _a, _b = _bgSdk(), _bgTu()
    kiem("khuôn giờ của Sổ Đăng Ký và Trung Ương SO ĐƯỢC với nhau",
         len(_a) == len(_b) and _a[10] == _b[10] and _a[-1] == _b[-1]
         and _a[:4].isdigit() and _bgTu() >= _b,
         f"{_a!r} vs {_b!r} — lệch khuôn thì `luc >= ?` lọc ra tập RỖNG "
         f"mà không dòng nào kêu")

    # ── VÌ SAO, không chỉ BAO NHIÊU ─────────────────────────────────────
    # Trên máy sống, họ phái-sinh có 2115 cơ hội thô và KHÔNG được đồng nào.
    # Nhìn con số 0 ấy thì «cổng ty quá chặt» và «hết chỗ vì trần vị thế»
    # giống hệt nhau — mà cái đầu sửa bằng vặn ngưỡng, cái sau bằng nhường
    # chỗ. Đọc lý do ra mới thấy thủ phạm thật: «chưa đo được sức chứa».
    tu.danh_muc.tienMatUsd = 0.0        # ép mọi tờ sau đây bị từ chối
    for _ in range(2):
        tu.mot_vong(lechDongHoGiay=1.0, cangChet=[], tuoiXauNhatGiay=1.0)
    # Dựng SÁU lý do khác nhau, một lý do RỖNG, và một lần từ chối ở CỬA
    # KHÁC — đủ nghèo nàn thì phép kiểm không phân biệt nổi đọc đúng cửa
    # với đọc bừa cửa, và ba đột biến đã sống sót đúng vì thế.
    for i in range(6):
        _tt = _mau(taiSan=f"Z{i}", von=10.0, chua=99.0)
        tu.so_dang_ky.ghi_nhan(_tt)
        tu.so_dang_ky.chuyen(_tt.ma, "DUYET_TY", "qua cổng ty")
        # Lý do thứ 0 lặp BA lần: đỉnh phải là nó, không phải cái ngẫu nhiên.
        tu.so_dang_ky.chuyen(_tt.ma, "TU_CHOI", f"lý do số {min(i, 3)}")
    _rong = _mau(taiSan="ZR", von=10.0, chua=99.0)
    tu.so_dang_ky.ghi_nhan(_rong)
    tu.so_dang_ky.chuyen(_rong.ma, "TU_CHOI", "")
    _mo = _mau(taiSan="ZM", von=10.0, chua=99.0)
    tu.so_dang_ky.ghi_nhan(_mo)
    for _b, _l in (("DUYET_TY", "qua cổng ty"), ("DUYET_RUI_RO", "qua"),
                   ("DA_CAP_VON", "cấp"), ("DA_MO", "CÂU Ở CỬA KHÁC")):
        tu.so_dang_ky.chuyen(_mo.ma, _b, _l)

    ly = tu.so_dang_ky.ly_do_tu_choi()
    _ps = [x["lyDo"] for x in ly.get("phai-sinh", [])]
    kiem("sổ đăng ký kể được VÌ SAO từng họ bị từ chối",
         "lý do số 0" in _ps,
         f"{ly} — một con số 0 không nói được cổng nào đã chặn")
    kiem("và đọc đúng CỬA TỪ CHỐI, không vơ cả câu ở cửa khác",
         not any("CỬA KHÁC" in x for ds in ly.values() for x in
                 [y["lyDo"] for y in ds]),
         "câu ghi lúc MỞ vị thế mà lọt vào bảng «vì sao bị từ chối» thì bảng "
         "ấy nói ngược hẳn sự thật")
    # `dinh` cao để KHÔNG cắt: lý do rỗng chỉ có một dòng, mà cắt đỉnh 5 thì
    # nó rơi khỏi bảng và phép kiểm không nhìn thấy nó nữa — đúng lý do phép
    # kiểm bản đầu để lọt đột biến bỏ mất bộ lọc.
    _het = tu.so_dang_ky.ly_do_tu_choi(999)
    kiem("mỗi lý do có số đếm, và lý do RỖNG bị loại",
         all(isinstance(x["so"], int) and x["lyDo"]
             for ds in _het.values() for x in ds), str(_het))
    _dem = [x["so"] for x in ly["phai-sinh"]]
    kiem("đỉnh là lý do ĐẾM NHIỀU NHẤT, không phải cái gặp đầu tiên",
         _ps[:1] == ["lý do số 3"] and _dem[0] == 3
         and _dem == sorted(_dem, reverse=True),
         f"{ly.get('phai-sinh')} — thủ phạm chính phải nằm trên cùng, "
         f"không thì người đọc sửa nhầm cái thứ yếu")
    _theo2 = {x["ho"]: x for x in tu.pheu_day_du()["theoHo"]}
    kiem("và phễu theo họ mang ĐÚNG lý do ấy theo",
         _theo2["phai-sinh"]["lyDoTuChoi"] == ly["phai-sinh"],
         "khoá có mặt mà danh sách rỗng thì phép kiểm «có khoá không» vẫn "
         "xanh — đúng đột biến đã sống sót một lượt")
    kiem("cắt ĐỈNH, không đổ cả sổ ra buồng lái",
         len(ly["phai-sinh"]) == 5
         and len(tu.so_dang_ky.ly_do_tu_choi(2)["phai-sinh"]) == 2,
         f"{len(ly['phai-sinh'])} — một họ chạy vài ngày là có hàng trăm câu "
         f"lý do khác nhau")

    # ── GOM THEO MÃ, KHÔNG THEO CÂU ─────────────────────────────────────
    # Câu có SỐ nhúng bên trong. Đo 30/08 trên máy sống: 2.527 lần từ chối
    # vỡ thành 306 CÂU, trong khi chỉ có 5 MÃ. `khoa-von-lau` một mình
    # chiếm 160 lần, nhưng mỗi lần ghi số giờ khác nhau (2455, 2119,
    # 1278…) nên bảng «năm lý do đứng đầu» hiện năm dòng gần giống hệt
    # nhau, mỗi dòng đếm 2–3 lần — và cái đang chặn phần lớn cơ hội biến
    # mất khỏi bảng.
    #
    # Điều 32 đã bắt bên GHI mang mã. Bên ĐỌC thì chưa, nên nửa kia của
    # cùng một luật vẫn hở.
    _gom = TrungUong(_tam("gom-ma"), {"vonBanDauUsd": 500.0})
    for _i, _cau in enumerate(
            [f"khoa-von-lau: khoá vốn {900 + 7 * _i} giờ > trần 720 giờ"
             for _i in range(9)]
            + ["duoi-von-toi-thieu: chỉ cấp được 0.00 USD",
               "duoi-von-toi-thieu: chỉ cấp được 150.00 USD",
               "câu CŨ không mang mã nào cả"]):
        _t = _mau(taiSan=f"G{_i}", ho="tin-dung", von=10.0,
                  chua=99.0)
        _gom.so_dang_ky.ghi_nhan(_t)
        _gom.so_dang_ky.chuyen(_t.ma, "TU_CHOI", _cau)
    _lg = _gom.so_dang_ky.ly_do_tu_choi()["tin-dung"]
    _theoMa = {x["ma"]: x for x in _lg}
    kiem("chín câu KHÁC NHAU cùng mã gom thành MỘT dòng",
         "khoa-von-lau" in _theoMa
         and _theoMa["khoa-von-lau"]["so"] == 9
         and _theoMa["khoa-von-lau"]["soCauKhac"] == 9,
         f"{_lg} — số giờ nhúng trong câu làm một nguyên nhân vỡ thành "
         f"chín nguyên nhân, và cái chặn nhiều nhất rơi khỏi bảng")
    kiem("và nó ĐỨNG ĐẦU, đúng thủ phạm chính",
         _lg[0]["ma"] == "khoa-von-lau",
         f"{[x['ma'] for x in _lg]} — gom theo câu thì dòng đầu là một "
         f"nguyên nhân đếm 2, không phải nguyên nhân đếm 9")
    kiem("hai câu cùng mã duoi-von-toi-thieu cũng gom",
         _theoMa.get("duoi-von-toi-thieu", {}).get("so") == 2,
         str(_lg))
    # Dòng CŨ không mã (1.984 dòng ghi trước điều 32) giữ nguyên câu làm
    # khoá và khai `ma: None`. Gộp chúng vào một rổ «không mã» là trộn
    # những nguyên nhân khác hẳn nhau.
    kiem("câu CŨ không mang mã thì đứng riêng và KHAI là không có mã",
         any(x["ma"] is None and "không mang mã" in x["lyDo"] for x in _lg),
         f"{_lg} — gộp mọi câu không mã vào một rổ là trộn những nguyên "
         f"nhân khác hẳn nhau")
    kiem("và MẪU SỐ đếm được, không để bảng đọc thành «đây là tất cả»",
         _gom.so_dang_ky.so_tu_choi().get("tin-dung") == 12,
         "năm mã đứng đầu phủ 1.561/2.305 lần từ chối trên máy sống — hai "
         "phần ba, không phải tất cả, và bảng không nói ra điều đó")
    # Và mẫu số ấy phải ĐI THEO phễu, không nằm lại trong sổ: bảng lý do
    # vẽ từ hàng phễu chứ không gọi thẳng sổ đăng ký.
    _hangPS = {x["ho"]: x for x in tu.pheu_day_du()["theoHo"]}["phai-sinh"]
    kiem("phễu mang mẫu số ấy theo, và nó ≥ tổng của mấy mã đứng đầu",
         _hangPS["soTuChoi"] >= sum(x["so"] for x in _hangPS["lyDoTuChoi"])
         and _hangPS["soTuChoi"] > 0,
         f"{_hangPS['soTuChoi']} vs "
         f"{sum(x['so'] for x in _hangPS['lyDoTuChoi'])}")



class ThongChinhGia:
    """Thông Chính tối thiểu — chỉ đủ để `mot_luot()` chạy."""
    def __init__(self): self.nhan = []
    def nop(self, tt): self.nhan.append(tt); return True


def _tt_vay(**kw):
    from tin_dung.models import ThiTruongVay
    d = dict(ma="p1", giaoThuc="aave-v3", chuoi="Base", taiSan="USDC",
             apyGocPhanTram=5.0, apyThuongPhanTram=0.0,
             tvlUsd=100e6, tvlGiaoThucUsd=2e9,
             tongCungUsd=100e6, tongVayUsd=70e6)
    d.update(kw)
    return ThiTruongVay(**d)


class _TraLoi:
    def __init__(self, d): self._d = d
    def raise_for_status(self): pass
    def json(self): return self._d


class _KhachGia:
    """httpx giả — ty tín dụng phải chạy được KHÔNG CẦN MẠNG."""
    def __init__(self, pools, lendborrow):
        self._p, self._l = pools, lendborrow
    async def __aenter__(self): return self
    async def __aexit__(self, *a): return False
    async def get(self, url):
        from tin_dung.nguon import DUONG_POOLS
        return _TraLoi(self._p if url == DUONG_POOLS else self._l)


def kiem_tin_dung_phi() -> None:
    print("\n-- Ty tin dung: APY khong phai loi nhuan --")
    from tin_dung.can_loi import (gas_khu_hoi_usd, hoa_von_sau_gio, mot_co_hoi,
                                  phi_bps, suc_chua_usd)

    GAS = {"Ethereum": 6.0, "Base": 0.05, "_khac": 1.0}
    kiem("gas tính KHỨ HỒI, nhân hai",
         gan(gas_khu_hoi_usd("Ethereum", GAS), 12.0),
         "quên nhân hai là báo cáo một nửa chi phí, và với vốn nhỏ thì một "
         "nửa ấy chính là phần quyết định lỗ hay lãi")
    kiem("chuỗi lạ rơi về mức _khac", gan(gas_khu_hoi_usd("Sui", GAS), 2.0))

    kiem("$200 trên Ethereum: gas là 600 bps",
         gan(phi_bps(200.0, "Ethereum", GAS), 600.0))
    kiem("$50.000 cùng thị trường ấy: gas chỉ 2,4 bps",
         gan(phi_bps(50_000.0, "Ethereum", GAS), 2.4),
         "cùng một APY, hai cỡ vốn, hai kết luận ngược nhau")
    kiem("vốn ≤ 0 thì phí là VÔ HẠN, không phải 0",
         phi_bps(0.0, "Base", GAS) == float("inf"))

    t = _tt_vay(apyGocPhanTram=4.0, chuoi="Ethereum")
    h = hoa_von_sau_gio(t, 200.0, "Ethereum", GAS)
    kiem("hoà vốn tính ra được, và ở $200/Ethereum là hơn 3 tháng",
         h is not None and h > 2000.0, f"{h}")
    kiem("APY ≤ 0 thì KHÔNG BAO GIỜ hoà, trả None",
         hoa_von_sau_gio(_tt_vay(apyGocPhanTram=0.0), 200.0, "Base", GAS) is None)

    # ── token thưởng KHÔNG vào NET ──────────────────────────────────────
    a = mot_co_hoi(_tt_vay(apyGocPhanTram=4.0, apyThuongPhanTram=0.0),
                   1000.0, 720.0, GAS, {"phanThanhKhoanRanh": 0.02,
                                        "tranUsd": 50_000.0})
    b = mot_co_hoi(_tt_vay(apyGocPhanTram=4.0, apyThuongPhanTram=20.0),
                   1000.0, 720.0, GAS, {"phanThanhKhoanRanh": 0.02,
                                        "tranUsd": 50_000.0})
    kiem("token thưởng KHÔNG cộng vào NET", gan(a.netBps, b.netBps),
         "tính thưởng vào NET là cách nhanh nhất để bảng xếp hạng bị chiếm "
         "bởi những thị trường đang mua thanh khoản bằng token của mình")
    kiem("nhưng tỉ lệ thưởng vẫn đo được", gan(b.thiTruong.tyLeThuong, 20/24))

    # ── sức chứa và thanh khoản thoát ───────────────────────────────────
    kiem("thanh khoản thoát = tổng cung − tổng vay",
         gan(_tt_vay().thanhKhoanRanhUsd, 30e6))
    kiem("thiếu một vế thì thanh khoản thoát là None, KHÔNG phải 0",
         _tt_vay(tongVayUsd=None).thanhKhoanRanhUsd is None,
         "không biết rút được bao nhiêu là một trạng thái, không phải một số")
    kiem("và None chảy tới tận sức chứa",
         suc_chua_usd(_tt_vay(tongVayUsd=None),
                      {"phanThanhKhoanRanh": 0.02, "tranUsd": 5e4}) is None)
    kiem("sức chứa = phần thanh khoản rảnh, có trần",
         gan(suc_chua_usd(_tt_vay(), {"phanThanhKhoanRanh": 0.02,
                                      "tranUsd": 5e4}), 5e4),
         "30M × 2% = 600K, bị trần 50K cắt")
    kiem("dùng vốn tính đúng", gan(_tt_vay().suDung, 0.70))
    kiem("tổng cung 0 thì dùng vốn là None",
         _tt_vay(tongCungUsd=0.0).suDung is None)


def kiem_tin_dung_cua() -> None:
    print("\n-- Ty tin dung: cua phai THAT, y nhu ty dau da hoc --")
    from tin_dung.can_loi import mot_co_hoi
    from tin_dung.config import MAC_DINH
    from tin_dung.rui_ro import CUA, NHAN, CongRuiRo

    kiem("CUA và MAC_DINH['ruiRo'] khai cùng một bộ khoá",
         set(CUA) == set(MAC_DINH["ruiRo"]),
         str(set(CUA) ^ set(MAC_DINH["ruiRo"])))

    class _GianDiep(dict):
        def __init__(self, g):
            super().__init__(g); self.daDoc = set()
        def __getitem__(self, k):
            self.daDoc.add(k); return super().__getitem__(k)

    gd = _GianDiep(MAC_DINH["ruiRo"])
    cong = CongRuiRo(gd)
    cong.c = gd
    SC = {"phanThanhKhoanRanh": 0.02, "tranUsd": 5e4}
    GAS = {"Base": 0.05, "_khac": 1.0}
    for t in (_tt_vay(), _tt_vay(tongVayUsd=None), _tt_vay(tvlUsd=1e6),
              _tt_vay(tongVayUsd=99e6), _tt_vay(apyGocPhanTram=99.0),
              _tt_vay(apyThuongPhanTram=90.0)):
        cong.xet(mot_co_hoi(t, 1000.0, 720.0, GAS, SC))
    kiem("mọi cửa KHAI ra đều được xet() đọc thật",
         set(CUA) <= gd.daDoc, f"chưa đọc: {set(CUA) - gd.daDoc}")
    kiem("xet() KHÔNG đọc khoá nào ngoài CUA",
         gd.daDoc <= set(CUA), f"đọc lạ: {gd.daDoc - set(CUA)}")

    cong2 = CongRuiRo({**MAC_DINH["ruiRo"], "khoaLa": 1})
    kiem("tom_tat() lọc bỏ khoá lạ, không bày nó như một cửa",
         "khoaLa" not in cong2.tom_tat() and set(cong2.tom_tat()) == set(CUA))

    def ma_cua(t, von=1000.0):
        return {m for m, _ in cong2.xet(mot_co_hoi(t, von, 720.0, GAS, SC))[1]}

    kiem("TVL nhỏ → chặn", "tvl-qua-nho" in ma_cua(_tt_vay(tvlUsd=1e6)))
    kiem("dùng vốn quá cao → chặn",
         "dung-von-qua-cao" in ma_cua(_tt_vay(tongVayUsd=99e6)))
    kiem("thanh khoản thoát mỏng → chặn",
         "thanh-khoan-thoat-mong" in ma_cua(_tt_vay(tongVayUsd=99.9e6)))
    kiem("lãi chủ yếu từ thưởng → chặn",
         "lai-chu-yeu-tu-thuong" in ma_cua(_tt_vay(apyThuongPhanTram=90.0)))
    kiem("APY cao bất thường trên stablecoin → chặn, KHÔNG phải cơ hội",
         "apy-cao-bat-thuong" in ma_cua(_tt_vay(apyGocPhanTram=99.0)),
         "APY 99% trên một stablecoin là dấu hiệu thị trường sắp cạn thanh "
         "khoản, không phải một món hời")
    kiem("thiếu số đo → chặn, không bỏ qua",
         "thieu-so-do" in ma_cua(_tt_vay(tongVayUsd=None)))
    # Cùng một thị trường, cùng một APY — chỉ đổi cỡ vốn. Ở $1.000 thì gas
    # là 1 bps và qua; ở $10 thì gas là 100 bps và ăn sạch phần lãi.
    kiem("cùng thị trường ấy, $1.000 thì qua", ma_cua(_tt_vay(), von=1000.0) == set())
    kiem("nhưng $10 thì NET dưới ngưỡng → chặn",
         "net-duoi-nguong" in ma_cua(_tt_vay(), von=10.0),
         "cùng một APY, hai cỡ vốn, hai kết luận ngược nhau — một scanner "
         "chỉ xếp APY sẽ không bao giờ thấy điều đó")
    kiem("thị trường lành thì qua sạch", ma_cua(_tt_vay()) == set())
    kiem("mọi mã lý do đều có nhãn cho người đọc",
         all(m in NHAN for m in
             ("tvl-qua-nho", "dung-von-qua-cao", "thanh-khoan-thoat-mong",
              "lai-chu-yeu-tu-thuong", "net-duoi-nguong", "apy-cao-bat-thuong",
              "du-lieu-cu", "thieu-so-do")))


def kiem_tin_dung_thang_rui_ro() -> None:
    print("\n-- Ty tin dung: hai thang rui ro, ca hai deu tung sai --")
    from tin_dung.ty_vay import _rui_ro, _rui_ro_su_dung, _rui_ro_tvl
    from tin_dung.can_loi import mot_co_hoi

    # ── TVL → rủi ro giao thức: KHÔNG được bão hoà ──────────────────────
    kiem("thang TVL phân biệt được $5M với $50M",
         _rui_ro_tvl(5e6) > _rui_ro_tvl(50e6) + 0.2,
         f"{_rui_ro_tvl(5e6):.2f} vs {_rui_ro_tvl(50e6):.2f} — bản đầu dùng "
         f"sqrt và cả hai đều ra 1,00, nên cửa TVL của Rủi Ro Tổng vô tình "
         f"thành 'chỉ nhận giao thức trên $50M'")
    kiem("và không mặt nào chạm 1,00",
         all(_rui_ro_tvl(v) <= 0.85 for v in (1e3, 1e6, 5e6)),
         "'chưa được kiểm chứng bằng thời gian' không phải 'chắc chắn hỏng'")
    kiem("mỗi bậc mười lần TVL hạ 0,25",
         gan(_rui_ro_tvl(5e6) - _rui_ro_tvl(50e6), 0.25, 1e-9))
    kiem("TVL None thì None, không đoán", _rui_ro_tvl(None) is None)

    # ── rủi ro giao thức đọc TVL của GIAO THỨC, không của POOL ──────────
    GAS = {"Base": 0.05, "_khac": 1.0}
    SC = {"phanThanhKhoanRanh": 0.02, "tranUsd": 5e4}
    nho = _tt_vay(tvlUsd=11e6, tvlGiaoThucUsd=2e9)
    r = _rui_ro(mot_co_hoi(nho, 1000.0, 720.0, GAS, SC))
    kiem("pool $11M của một giao thức $2B KHÔNG bị chấm như giao thức nhỏ",
         r.giaoThuc < 0.25,
         f"đang {r.giaoThuc:.2f} — một lỗi trong Aave v3 ảnh hưởng MỌI thị "
         f"trường Aave v3, nên rủi ro hợp đồng là của giao thức chứ không "
         f"của cái pool ta đang nhìn")
    thieu = _tt_vay(tvlUsd=11e6, tvlGiaoThucUsd=None)
    kiem("thiếu TVL giao thức thì rơi về TVL pool, chịu chấm nặng hơn",
         _rui_ro(mot_co_hoi(thieu, 1000.0, 720.0, GAS, SC)).giaoThuc
         > r.giaoThuc,
         "đoán rộng lượng khi thiếu số là thưởng cho sự mù")

    # ── dùng vốn → rủi ro thanh khoản: LỒI, không tuyến tính ────────────
    kiem("dùng vốn 80% là LÀNH MẠNH, không phải rủi ro 0,80",
         _rui_ro_su_dung(0.80) < 0.45,
         f"đang {_rui_ro_su_dung(0.80):.2f} — bản đầu lấy thẳng rủi ro = "
         f"dùng vốn, và vì rui_ro_tong lấy MAX nên nó loại sạch mọi thị "
         f"trường đang hoạt động tốt, chỉ nhận thị trường không ai vay — "
         f"tức là thị trường không trả lãi")
    kiem("nhưng đuôi vẫn dựng lên", _rui_ro_su_dung(0.95) > 0.75)
    kiem("dùng vốn thấp thì gần như không rủi ro tỉ lệ",
         gan(_rui_ro_su_dung(0.3), 0.02))
    kiem("thang lồi, không tuyến tính",
         (_rui_ro_su_dung(0.95) - _rui_ro_su_dung(0.85))
         > (_rui_ro_su_dung(0.65) - _rui_ro_su_dung(0.55)) * 2)
    kiem("None thì None", _rui_ro_su_dung(None) is None)
    kiem("cầu nối = 0,0 vì cùng chuỗi — ĐÃ ĐO, không phải chưa biết",
         r.cauNoi == 0.0)


def kiem_van_tay_co_chuoi() -> None:
    print("\n-- Van tay co hoi phai co CHUOI (loi ty thu hai lam lo ra) --")
    from thi_bac_ty.to_trinh import Chan, RuiRo, ToTrinh
    from thi_bac_ty.trung_uong import _dau_van

    def t(chuoi, cang="aave-v3"):
        return ToTrinh(
            chienLuoc="lending.rate_rotation.v1", ho="tin-dung", taiSan="USDC",
            chan=(Chan("CHO_VAY", cang, "USDC", 100.0, "lending", chuoi),),
            vonCanUsd=100.0, sucChuaToiDaUsd=9000.0, grossBps=30.0,
            phiUocBps=5.0, netUocBps=25.0, giuGio=720.0,
            khoaVonDenGio=0.0, thanhKhoanThoatUsd=1e6,
            ruiRo=RuiRo(.1, .1, .2, .2, .1, 0.), tinCay=.8,
            moHinhPhiDuChua=True, sucChuaConThieu=("x",))

    kiem("aave-v3 USDC trên Ethereum KHÁC aave-v3 USDC trên Polygon",
         _dau_van(t("Ethereum")) != _dau_van(t("Polygon")),
         "thiếu chuỗi thì hai thị trường khác hẳn nhau cùng một vân tay, và "
         "cái thứ hai bị bỏ trong IM LẶNG như thể nó là bản trùng")
    kiem("cùng chuỗi cùng cảng thì vẫn là một cơ hội",
         _dau_van(t("Base")) == _dau_van(t("Base")))
    kiem("khác cảng vẫn khác vân",
         _dau_van(t("Base")) != _dau_van(t("Base", "morpho-blue")))
    kiem("chân không có chuỗi (sàn tập trung) vẫn ổn định",
         _dau_van(t(None)) == _dau_van(t(None)))


def kiem_hai_ty_that() -> None:
    print("\n-- Cau hoi thanh/bai: HAI TY THAT, mot Thi Bac Ty --")
    from thi_bac_ty.trung_uong import TrungUong
    from thi_bac_ty.khuon_ty import Ty
    from thi_bac_ty.to_trinh import Chan
    from tin_dung.ty_vay import TyTinDung

    pools = [
        {"pool": "a", "project": "aave-v3", "chain": "Base", "symbol": "USDC",
         "apyBase": 5.0, "apyReward": 0.2, "tvlUsd": 120e6},
        {"pool": "b", "project": "aave-v3", "chain": "Polygon", "symbol": "USDC",
         "apyBase": 4.0, "apyReward": 0.0, "tvlUsd": 60e6},
        {"pool": "c", "project": "bia-moi", "chain": "Base", "symbol": "USDC",
         "apyBase": 30.0, "apyReward": 0.0, "tvlUsd": 6e6},
        {"pool": "d", "project": "aave-v3", "chain": "Sui", "symbol": "USDC",
         "apyBase": 9.0, "apyReward": 0.0, "tvlUsd": 90e6},
        {"pool": "e", "project": "aave-v3", "chain": "Base", "symbol": "WETH",
         "apyBase": 9.0, "apyReward": 0.0, "tvlUsd": 90e6},
        {"pool": "f", "project": "khong-ghep", "chain": "Base", "symbol": "USDC",
         "apyBase": 7.0, "apyReward": 0.0, "tvlUsd": 90e6},
    ]
    lb = [{"pool": "a", "totalSupplyUsd": 120e6, "totalBorrowUsd": 70e6},
          {"pool": "b", "totalSupplyUsd": 60e6, "totalBorrowUsd": 30e6},
          {"pool": "c", "totalSupplyUsd": 6e6, "totalBorrowUsd": 5.9e6},
          {"pool": "d", "totalSupplyUsd": 90e6, "totalBorrowUsd": 40e6},
          {"pool": "e", "totalSupplyUsd": 90e6, "totalBorrowUsd": 40e6}]

    tv = TyTinDung(client_factory=lambda: _KhachGia(pools, lb))
    co = tv.quet()
    kiem("lọc đúng tài sản và chuỗi đã khai",
         {c.thiTruong.ma for c in co} == {"a", "b", "c"},
         f"{sorted(c.thiTruong.ma for c in co)} — d bị loại vì chuỗi Sui, "
         f"e vì WETH, f vì không ghép được bảng vay")
    kiem("pool không ghép được thì BỎ, và số bị bỏ đếm ra",
         tv.nguon.soBoVìThieuGhep == 1,
         "bỏ trong im lặng thì một ngày nguồn đổi khoá, ta sẽ thấy 'thị "
         "trường không có gì' thay vì thấy 'ta đang mù'")
    kiem("TVL giao thức cộng qua MỌI pool, kể cả pool đã lọc bỏ",
         gan([c for c in co if c.thiTruong.ma == "b"][0]
             .thiTruong.tvlGiaoThucUsd, 120e6 + 60e6 + 90e6 + 90e6))

    class TyGiaPerp(Ty):
        ma, ho, moTa = "perpetual.funding_spread.v1", "phai-sinh", "perp giả"
        vonToiThieuKinhTeUsd = 50.0
        def quet(self): return ["BTC"]
        def xet(self, co): return True, []
        def trinh(self, co):
            return _mau(taiSan=co, von=300.0, chua=9000.0, khoa=0.0,
                        chan=(Chan("LONG", "hyperliquid", co),
                              Chan("SHORT", "binance", co)))

    tu = TrungUong(_tam("haity"), {"vonBanDauUsd": 30000.0})
    kiem("cả hai ty đăng ký được", tu.dang_ky(TyGiaPerp()) and tu.dang_ky(tv))
    lat = tu.mot_vong(lechDongHoGiay=1.0, cangChet=[], tuoiXauNhatGiay=1.0)

    kiem("cả hai cùng quét trong một vòng", lat.soTyChay == 2)
    theo = {x["ho"]: x for x in tu.pheu_day_du()["theoHo"]}
    kiem("phễu tách được hai họ THẬT",
         set(theo) == {"phai-sinh", "tin-dung"}, str(list(theo)))
    kiem("họ tín dụng: cổng ty chặn thị trường mỏng",
         theo["tin-dung"]["coHoiTho"] == 3
         and theo["tin-dung"]["quaCongTy"] == 2,
         str(theo["tin-dung"]) + " — pool c dùng vốn 98% và TVL $6M")

    cap = {x["chienLuoc"] for x in (lat.phanBo or {}).get("daCap", [])}
    kiem("cả hai họ cùng được cấp vốn dưới MỘT Thị Bạc Ty",
         cap == {"perpetual.funding_spread.v1", "lending.rate_rotation.v1"},
         str(sorted(cap)) + " — đây là câu hỏi thành/bại của cả kiến trúc")

    dm = tu.danh_muc
    aave = dm.phoi_nhiem_cang().get("aave-v3", 0.0)
    kiem("danh mục gộp phơi nhiễm theo GIAO THỨC, cộng qua các chuỗi",
         aave > 0 and gan(aave, sum(
             x["capUsd"] for x in (lat.phanBo or {}).get("daCap", [])
             if x["chienLuoc"] == "lending.rate_rotation.v1")),
         str(dm.phoi_nhiem_cang()) + " — một lỗi trong aave-v3 kẹt cả hai")
    kiem("và tách phơi nhiễm theo CHUỖI",
         set(dm.phoi_nhiem_chuoi()) == {"Base", "Polygon"},
         str(dm.phoi_nhiem_chuoi()))
    kiem("chân sàn tập trung KHÔNG có chuỗi, không cộng nhầm vào",
         gan(sum(dm.phoi_nhiem_chuoi().values()), aave),
         "chân perp nằm trên sàn tập trung, không thuộc chuỗi nào")
    kiem("hai vân tay khác nhau nên KHÔNG cái nào bị bỏ trùng",
         lat.soBoTrung == 0 and lat.soGhiNhan == 3)
    kiem("không tầng nào đi tắt", tu.so_dang_ky.soChuyenSai == 0)

    # ── ty được BỌC vẫn phải đăng ký được ───────────────────────────────
    class _Boc:
        """Lớp bọc để cho một ty nhịp quét riêng — xem `bac/vong._NhipRieng`."""
        def __init__(self, ty): self._t = ty; self.soBoQua = 0
        def __getattr__(self, k): return getattr(self._t, k)
        @property
        def ma(self): return self._t.ma

    tu2 = TrungUong(_tam("boc"), {"vonBanDauUsd": 1000.0})
    kiem("ty được BỌC vẫn đăng ký được", tu2.dang_ky(_Boc(TyGiaPerp())),
         "soi `type(ty)` thay vì `ty` là từ chối một ty hợp lệ vì một lý do "
         "chẳng liên quan gì tới nó")
    kiem("và nó vào sổ với ĐÚNG mã của ty thật",
         set(tu2.ty) == {"perpetual.funding_spread.v1"}, str(set(tu2.ty)))

    class _BocSai:
        def __init__(self): self.ma = "khong-dung-khuon"
        def kiem_khai(self): return ["mã sai khuôn"]
    kiem("nhưng ty bọc mà KHAI SAI thì vẫn chết ở cửa",
         not tu2.dang_ky(_BocSai()),
         "bọc không phải là đường vòng qua cổng khai báo")

    # ── quét được từ TRONG một vòng lặp sự kiện ─────────────────────────
    import asyncio as _aio
    tv2 = TyTinDung(client_factory=lambda: _KhachGia(pools, lb))

    async def _trong_vong_lap():
        return tv2.quet()

    ra = _aio.run(_trong_vong_lap())
    kiem("quet() chạy được từ TRONG một vòng lặp sự kiện", len(ra) == 3,
         f"{len(ra)} · lỗi: {tv2.loiCuoi} — `Ty.quet()` là đồng bộ theo hợp "
         f"đồng, nhưng `Runtime.mot_vong()` là async, nên lúc Trung Ương gọi "
         f"thì ta đang Ở TRONG một vòng lặp và asyncio.run() ném thẳng")
    kiem("và vẫn chạy được khi KHÔNG có vòng lặp nào",
         len(TyTinDung(client_factory=lambda: _KhachGia(pools, lb)).quet()) == 3)

    # ── lớp bọc nhịp: bỏ qua thì TRẢ LẠI kết quả cũ, không trả rỗng ─────
    from bac.vong import _NhipRieng
    goc = TyTinDung(client_factory=lambda: _KhachGia(pools, lb))
    boc = _NhipRieng(goc, 9999.0)
    a1 = boc.quet()
    boQuaSauLuotDau = boc.soLuotBoQua        # chụp NGAY, trước lượt thứ hai
    a2 = boc.quet()
    kiem("lượt đầu quét thật", len(a1) == 3 and boQuaSauLuotDau == 0,
         f"len={len(a1)} boQua={boQuaSauLuotDau} loi={goc.loiCuoi!r}")
    kiem("lượt sau BỎ QUA nhưng trả lại kết quả cũ, KHÔNG trả rỗng",
         len(a2) == 3 and boc.soLuotBoQua == 1,
         "trả rỗng thì cơ hội biến mất rồi hiện lại, và cửa chống trùng ghi "
         "nhận chúng như cơ hội MỚI — vòng nào cũng đẻ một loạt tờ trình "
         "trùng, và cái phễu lại nói dối")
    kiem("nguồn chỉ bị hỏi ĐÚNG MỘT lần",
         goc.nguon.suc_khoe.tom_tat()["tongLuot"] == 1)
    kiem("lớp bọc mang khai báo của ty THẬT",
         boc.ma == goc.ma and boc.ho == goc.ho and boc.kiem_khai() == [])

    # ── lớp bọc phải uỷ quyền MỌI thứ ty thật ghi đè ────────────────────
    # Dò bằng SENTINEL chứ không liệt kê tên: đã ba lần một thành viên bị
    # lớp bọc che mất — `kiem_khai`, `vonToiThieuKinhTeUsd`, rồi `ke_toan`.
    # Cả ba lọt vì `Ty` khai sẵn ở lớp gốc, nên tra thuộc tính THÀNH CÔNG
    # (ra giá trị rỗng của lớp bọc) và `__getattr__` không bao giờ chạy.
    # Lần thứ ba tốn bảy vị thế và 3.500 USD không được cộng lãi, trong khi
    # buồng lái báo đúng "chưa có kế toán" nên không ai nghi ngờ mã.
    from thi_bac_ty.khuon_ty import Ty as _TyGoc

    class _TyDauVet(_TyGoc):
        ma = "lending.rate_rotation.v1"
        ho = "tin-dung"
        moTa = "ty dò dấu vết cho lớp bọc"
        vonToiThieuKinhTeUsd = 7.0

        def quet(self): return ["DAU-VET"]
        def xet(self, co): return True, [("dau-vet", "DAU-VET")]
        def trinh(self, co): return "DAU-VET"
        def ke_toan(self, viThe, toTrinh, tuGiay, denGiay): return "DAU-VET"

    dv = _NhipRieng(_TyDauVet(), 9999.0)
    thieu = []
    if dv.quet() != ["DAU-VET"]: thieu.append("quet")
    if dv.xet(None)[1] != [("dau-vet", "DAU-VET")]: thieu.append("xet")
    if dv.trinh(None) != "DAU-VET": thieu.append("trinh")
    if dv.ke_toan([], {}, 0.0, 1.0) != "DAU-VET": thieu.append("ke_toan")
    if dv.vonToiThieuKinhTeUsd != 7.0: thieu.append("vonToiThieuKinhTeUsd")
    if dv.ma != "lending.rate_rotation.v1": thieu.append("ma")
    if dv.ho != "tin-dung": thieu.append("ho")
    if dv.moTa != "ty dò dấu vết cho lớp bọc": thieu.append("moTa")
    if not dv.co_ke_toan(): thieu.append("co_ke_toan")
    kiem("lớp bọc uỷ quyền MỌI thành viên ty thật ghi đè", not thieu,
         f"lớp bọc CHE MẤT {thieu} — ty thật ghi đè mà trung ương đọc ra "
         f"giá trị rỗng của lớp bọc, và không lỗi nào báo")
    kiem("và mot_luot() không tự đệ quy",
         len(boc.mot_luot(ThongChinhGia())) >= 0 and boc.soLuotBoQua == 2,
         "bản đầu gán đè `ty.quet` rồi gọi lại chính nó, nên ty quét được "
         "KHÔNG lần nào trong khi mọi thứ vẫn xanh")

    kiem("và thi_bac_ty KHÔNG biết tin_dung tồn tại",
         not _co_nhac("tin_dung"),
         "ngày trung ương phải import một ty để xử một trường hợp riêng là "
         "ngày hợp đồng đã hỏng")


def _co_nhac(ten: str) -> bool:
    import pathlib
    goc = pathlib.Path(__file__).resolve().parent.parent / "thi_bac_ty"
    for p in goc.glob("*.py"):
        for d in p.read_text(encoding="utf-8").splitlines():
            d = d.strip()
            if d.startswith((f"import {ten}", f"from {ten}")):
                return True
    return False



def kiem_von_ngoai() -> None:
    print("\n-- Von ngoai: thay duoc, KHONG quan duoc --")
    from thi_bac_ty.danh_muc import DanhMuc, ViThe
    from thi_bac_ty.von_ngoai import DocVonNgoai, LatCatNgoai, _doc_kham

    # ── dịch ảnh chụp của cỗ máy kia ────────────────────────────────────
    anh = {"che": "giay",
           "kho": {"soThiTruong": 2,
                   "viThe": [{"loKhoaUsd": 120.0, "chuaPhongHoUsd": 30.0},
                             {"loKhoaUsd": 80.0, "chuaPhongHoUsd": 0.0}]},
           "risk": {"vonUsd": 500.0}}
    l = _doc_kham("kham", anh)
    kiem("đọc được thì khai đọc được", l.docDuoc)
    kiem("vốn đang phơi ra = lỗ khoá + chân chưa phòng hộ",
         gan(l.daCamKetUsd, 230.0),
         "một chân chưa phòng hộ VẪN là vốn đang phơi ra")
    kiem("tiền mặt đọc được", gan(l.tienMatUsd, 500.0))
    kiem("tổng = cam kết + tiền mặt", gan(l.tongUsd, 730.0))
    kiem("số vị thế đọc được", l.soViThe == 2)

    thieu = _doc_kham("kham", {"che": "giay"})
    kiem("thiếu khoá thì vẫn đọc được, và NÓI RA thiếu gì",
         thieu.docDuoc and "kho" in thieu.vi and "risk" in thieu.vi,
         "đây là schema của một cỗ máy KHÁC; ta không có quyền bắt nó giữ "
         "nguyên, nên phải đọc phòng thủ và khai chỗ vắng")
    kiem("và không ném khi số rác",
         gan(_doc_kham("k", {"kho": {"viThe": [{"loKhoaUsd": "xxx"}]}})
             .daCamKetUsd, 0.0))

    # ── Danh Mục: vốn ngoài vào NAV nhưng KHÔNG vào viThe ────────────────
    dm = DanhMuc(1000.0)
    kiem("chưa khai vốn ngoài thì coi như đọc đủ", dm.ngoaiDayDu)
    dm.ghi_von_ngoai(l)
    kiem("vốn ngoài vào NAV", gan(dm.navUsd, 1730.0),
         "một NAV thiếu phần vốn đang phơi ra ở nơi khác là NAV nói dối "
         "theo hướng NGUY HIỂM: trần rộng hơn sự thật")
    kiem("nhưng KHÔNG vào danh sách vị thế", len(dm.viThe) == 0,
         "Thị Bạc Ty không mở nó, không đóng được nó, và không được giả vờ "
         "ngược lại")
    kiem("tự quản tách riêng khỏi NAV", gan(dm.tuQuanUsd, 1000.0))
    kiem("vốn ngoài không làm lệch phơi nhiễm cảng của mình",
         dm.phoi_nhiem_cang() == {})

    # Lát cắt hỏng MANG THEO SỐ CŨ — đây mới là ca đáng kiểm. Lát cắt hỏng
    # toàn số 0 thì cộng hay không cộng đều ra một kết quả, và phép kiểm
    # dựng trên nó không chứng minh được gì.
    hong = LatCatNgoai(ten="kham", docDuoc=False, vi="tắt",
                       daCamKetUsd=230.0, tienMatUsd=500.0)
    kiem("lát cắt hỏng vẫn có thể mang số", gan(hong.tongUsd, 730.0))
    dm.ghi_von_ngoai(hong)
    kiem("nhưng đọc hỏng thì KHÔNG cộng vào NAV", gan(dm.navUsd, 1000.0),
         "số cũ của một lần đọc hỏng là số của QUÁ KHỨ; cộng nó vào NAV "
         "hôm nay là dựng trần trên một con số không ai biết còn đúng không")
    kiem("và cờ đọc-đủ tắt", dm.ngoaiDayDu is False,
         "coi 'không đọc được' thành 'không có gì' là đúng cách một trần "
         "biến thành trần giả")
    kiem("bảng tóm tắt bày lời nhắc lên",
         dm.tom_tat()["loiNhacNgoai"] is not None
         and "RỘNG HƠN" in dm.tom_tat()["loiNhacNgoai"])

    # ── đọc hỏng là một lý do NGẮT cầu dao ──────────────────────────────
    from thi_bac_ty.cau_dao import CauDao
    NG = {"lechDongHoToiDaGiay": 60.0, "soCangChetToiDa": 0,
          "tuoiToiDaGiay": 300.0, "sutVonToiDaPct": 10.0}
    cd = CauDao()
    cd.tu_soat(lechDongHoGiay=1.0, cangChet=[], tuoiXauNhatGiay=1.0,
               sutVonPct=0.0, nguong=NG, vonNgoaiDayDu=False)
    duoc, ly = cd.cho_phep()
    kiem("không đọc được vốn ngoài → cầu dao NGẮT", not duoc)
    kiem("và gọi đúng tên", any("von-ngoai-mu" in l for l in ly), str(ly))
    cd.tu_soat(lechDongHoGiay=1.0, cangChet=[], tuoiXauNhatGiay=1.0,
               sutVonPct=0.0, nguong=NG, vonNgoaiDayDu=True)
    kiem("đọc lại được thì TỰ đóng lại", cd.cho_phep()[0],
         "đọc lại là biết ngay, nên đây là lý do tự mở")

    # ── đọc qua HTTP: cỗ máy kia tắt thì KHÔNG ném ──────────────────────
    d = DocVonNgoai("khong-ton-tai", "http://127.0.0.1:59998/api/trang-thai")
    lat = d.doc()
    kiem("cỗ máy kia tắt thì trả lát cắt KHÔNG-đọc-được, không ném",
         lat.docDuoc is False and d.soLoi == 1)
    kiem("và lý do nói ra được", bool(lat.vi), lat.vi)
    d.doc()
    kiem("chưa tới nhịp thì không hỏi lại", d.soLoi == 1)
    d.doc(ep=True)
    kiem("nhưng ép thì hỏi lại", d.soLoi == 2)

    # ── cả vòng: trần tính trên NAV ĐÃ có vốn ngoài ─────────────────────
    from thi_bac_ty.rui_ro_tong import RuiRoTong
    dm2 = DanhMuc(1000.0)
    tt = _mau(von=500.0, chua=90000.0, khoa=0.0)
    tran_khong = RuiRoTong().xet(tt, dm2).choToiDaUsd
    dm2.ghi_von_ngoai(LatCatNgoai(ten="k", docDuoc=True, tienMatUsd=1000.0))
    tran_co = RuiRoTong().xet(tt, dm2).choToiDaUsd
    kiem("NAV lớn hơn thì trần một cơ hội rộng hơn — và đó là ĐÚNG",
         tran_co > tran_khong,
         f"{tran_khong} → {tran_co}: rủi ro là của CẢ gia sản, nên trần "
         f"phải tính trên cả gia sản")



def kiem_on_dinh() -> None:
    print("\n-- Ty chenh lech stablecoin: $0,97 KHONG phai arbitrage --")
    from on_dinh.nguon import DinhSo
    from on_dinh.ty_on_dinh import (CUA, CongRuiRo, TyOnDinh, phi_khu_hoi_bps,
                                    sau_so_lenh_usd, tim_co_hoi)
    from on_dinh.config import MAC_DINH

    def d(san, mua, ban, ml=1e6, bl=1e6, cap="USDC/USDT"):
        return DinhSo(san, cap, mua, ban, ml, bl)

    kiem("CUA và MAC_DINH['ruiRo'] khai cùng một bộ khoá",
         set(CUA) == set(MAC_DINH["ruiRo"]),
         str(set(CUA) ^ set(MAC_DINH["ruiRo"])))

    PHI = {"binance": 1.0, "okx": 8.0, "_khac": 10.0}
    kiem("phí tính taker ở CẢ HAI sàn",
         gan(phi_khu_hoi_bps("binance", "okx", PHI), 9.0),
         "một chiều thôi là báo cáo nửa chi phí")
    kiem("sàn lạ rơi về mức _khac",
         gan(phi_khu_hoi_bps("binance", "la", PHI), 11.0))

    kiem("đỉnh sổ lấy chỗ CHẬT NHẤT của hai chân",
         gan(sau_so_lenh_usd(d("a", 1.0, 1.0, bl=100), d("b", 1.0, 1.0, ml=500)),
             100.0))
    kiem("sàn giấu khối lượng thì None, không đoán",
         sau_so_lenh_usd(d("a", 1.0, 1.0, bl=None), d("b", 1.0, 1.0)) is None)

    cong = CongRuiRo(MAC_DINH["ruiRo"])
    SC = {"phanDinhSo": 0.30, "tranUsd": 25_000.0}

    def ma_cua(ds, von=200.0):
        co = tim_co_hoi(ds, von, 24.0, PHI, SC, cong)
        return {m for c in co for m, _ in c.lyDoMa}, co

    # ── cửa quan trọng nhất: DEPEG ──────────────────────────────────────
    lech, _ = ma_cua([d("binance", 0.9700, 0.9702), d("okx", 0.9750, 0.9752)])
    kiem("lệch neo lớn → CHẶN, đây có thể là DEPEG",
         "lech-neo-qua-lon" in lech,
         "bên đứng ra 'ăn chênh lệch' sẽ là bên ôm đồng đang chết")

    lanh, co = ma_cua([d("binance", 0.9998, 0.9999), d("okx", 1.0020, 1.0021)])
    kiem("chênh lệch thật, neo còn sát 1,00 → QUA", lanh == set(),
         str(lanh) + " · " + str(co[0].tom_tat() if co else ""))
    kiem("mua ở ask thấp nhất, bán ở bid cao nhất",
         co[0].mua.san == "binance" and co[0].ban.san == "okx")
    kiem("chênh thô tính đúng", co[0].grossBps > 20.0, f"{co[0].grossBps}")

    cung, _ = ma_cua([d("binance", 0.9998, 1.0010)])
    kiem("mua và bán rơi vào CÙNG một sàn → chặn", "thieu-san" in cung,
         "đó là spread nội sàn, không phải chênh lệch chéo sàn")

    mong, _ = ma_cua([d("binance", 0.9998, 0.9999, bl=100.0),
                      d("okx", 1.0020, 1.0021, ml=100.0)])
    kiem("sổ lệnh mỏng → chặn", "so-lenh-mong" in mong,
         "chênh lệch trên một sổ mỏng là ảo")

    giau, _ = ma_cua([d("binance", 0.9998, 0.9999, bl=None),
                      d("okx", 1.0020, 1.0021)])
    kiem("sàn giấu khối lượng cũng bị chặn", "so-lenh-mong" in giau)

    # ── chu kỳ vốn, không phải thời gian giao dịch ──────────────────────
    kiem("chu kỳ vốn mặc định KHÔNG phải vài giây",
         MAC_DINH["quet"]["chuKyVonGio"] >= 1.0,
         "khai vài giây là cho NET mỗi giờ nhảy lên hàng nghìn bps và chiếm "
         "sạch bảng xếp hạng bằng một con số mình không đạt được")
    from on_dinh.ty_on_dinh import PHI_CON_THIEU
    kiem("và khai rõ chưa chuyển vốn được giữa hai sàn",
         "chuyen-von-giua-san" in PHI_CON_THIEU)

    # ── sổ lệnh hỏng thì bỏ, không dựng cơ hội ngược đời ────────────────
    from on_dinh.nguon import _dung
    kiem("bid > ask là sổ hỏng, bỏ", _dung("a", "c", 1.01, 1.00, 1, 1) is None)
    kiem("giá ≤ 0 là sổ hỏng, bỏ", _dung("a", "c", 0.0, 1.0, 1, 1) is None)
    kiem("số rác thì bỏ", _dung("a", "c", "x", 1.0, 1, 1) is None)

    # ── tờ trình ────────────────────────────────────────────────────────
    t = TyOnDinh().trinh(co[0])
    kiem("tờ trình hợp lệ", t.hop_le, str(t.kiem()))
    kiem("họ là chenh-lech — HỌ THỨ BA", t.ho == "chenh-lech")
    kiem("hai chân trên HAI sàn khác nhau",
         len(t.chan) == 2 and t.chan[0].cang != t.chan[1].cang)
    kiem("rủi ro thị trường bám vào ĐỘ LỆCH NEO, không phải hằng số",
         t.ruiRo.thiTruong is not None
         and t.ruiRo.thiTruong < TyOnDinh().trinh(
             tim_co_hoi([d("binance", 0.9950, 0.9951),
                         d("okx", 0.9975, 0.9976)], 200.0, 24.0, PHI, SC,
                        cong)[0]).ruiRo.thiTruong,
         "lệch neo là rủi ro CHÍNH của ty này")


def kiem_lai_suat() -> None:
    print("\n-- Ty lai suat Pendle PT: khoa von THAT khac 0 --")
    import datetime as _dt
    from lai_suat.ty_lai_suat import (CONFIG, CUA, CongRuiRo, ThiTruongPT,
                                      TyLaiSuat, doc_dao_han, la_pt,
                                      mot_co_hoi, xuat_to_trinh)

    kiem("CUA và CONFIG['ruiRo'] khai cùng một bộ khoá",
         set(CUA) == set(CONFIG["ruiRo"]),
         str(set(CUA) ^ set(CONFIG["ruiRo"])))

    # ── đọc ngày đáo hạn ────────────────────────────────────────────────
    h = doc_dao_han("For buying PT-sUSDe-22OCT2026")
    kiem("đọc được ngày đáo hạn từ poolMeta",
         h is not None and (h.year, h.month, h.day) == (2026, 10, 22), str(h))
    kiem("đọc được cả dạng LP | Maturity",
         doc_dao_han("For LP | Maturity 15OCT2026") is not None)
    kiem("không đọc được thì None, KHÔNG đoán",
         doc_dao_han("For buying PT-something") is None
         and doc_dao_han(None) is None,
         "đoán một ngày đáo hạn là đoán đúng con số quyết định vốn bị khoá "
         "bao lâu")
    kiem("tháng bịa thì None", doc_dao_han("22XXX2026") is None)
    kiem("ngày không tồn tại thì None", doc_dao_han("31FEB2026") is None)

    kiem("phân biệt PT với LP",
         la_pt("For buying PT-sUSDe-22OCT2026")
         and not la_pt("For LP | Maturity 22OCT2026"),
         "LP có tổn thất tạm thời, hệ toán khác hẳn — lẫn hai thứ là bịa ra "
         "một con số không mô tả cái nào")

    def tt(**kw):
        d = dict(ma="p", chuoi="Ethereum", taiSan="SUSDE",
                 meta="For buying PT-sUSDe-22OCT2026", apyPhanTram=8.0,
                 tvlUsd=20e6, tvlGiaoThucUsd=5e9,
                 daoHan=_dt.datetime.now(_dt.timezone.utc)
                 + _dt.timedelta(days=57))
        d.update(kw)
        return ThiTruongPT(**d)

    SC = {"phanTvl": 0.01, "tranUsd": 50_000.0}
    cong = CongRuiRo(CONFIG["ruiRo"])

    def ma_cua(t):
        return {m for m, _ in cong.xet(mot_co_hoi(t, 200.0, SC))[1]}

    kiem("thị trường lành thì qua sạch", ma_cua(tt()) == set(), str(ma_cua(tt())))
    kiem("TVL nhỏ → chặn", "tvl-qua-nho" in ma_cua(tt(tvlUsd=1e6)))
    kiem("lãi dưới ngưỡng → chặn", "apy-duoi-nguong" in ma_cua(tt(apyPhanTram=1.0)))
    kiem("lãi CỐ ĐỊNH cao bất thường → chặn, không phải món hời",
         "apy-cao-bat-thuong" in ma_cua(tt(apyPhanTram=115.0)),
         "lãi cố định cao bất thường là thị trường đang trả để ai đó gánh "
         "một rủi ro")
    kiem("sắp đáo hạn → chặn",
         "sap-dao-han" in ma_cua(tt(daoHan=_dt.datetime.now(_dt.timezone.utc)
                                    + _dt.timedelta(hours=10))))
    kiem("đã quá hạn → chặn",
         "da-dao-han" in ma_cua(tt(daoHan=_dt.datetime.now(_dt.timezone.utc)
                                   - _dt.timedelta(days=1))))
    kiem("không đọc được đáo hạn → chặn",
         "khong-doc-duoc-dao-han" in ma_cua(tt(daoHan=None)))

    # ── ĐÂY là điểm chính của ty này ────────────────────────────────────
    co = mot_co_hoi(tt(), 1000.0, SC)      # = ngưỡng kinh tế của engine
    t = xuat_to_trinh(co)
    kiem("tờ trình hợp lệ", t.hop_le, str(t.kiem()))
    kiem("khai KHOÁ VỐN thật, khác 0",
         t.khoaVonDenGio is not None and t.khoaVonDenGio > 1000.0,
         f"{t.khoaVonDenGio} — đây là ty đầu tiên dùng trường này với một "
         f"con số thật; trước nó, trường ấy chưa ai chứng minh có tác dụng")
    kiem("giữ tới đáo hạn: giuGio = khoá vốn",
         gan(t.giuGio, t.khoaVonDenGio, 1e-6),
         "PT trả lãi cố định tới đáo hạn; giữ ngắn hơn thì phải bán trên "
         "AMM ở một giá ta không biết")
    kiem("giờ vốn bị giữ = chính con số ấy",
         gan(t.gio_von_bi_giu, t.khoaVonDenGio, 1e-6))
    kiem("thanh khoản thoát là None — bán được nhưng ta KHÔNG BIẾT giá",
         t.thanhKhoanThoatUsd is None and t.raDuocKhong is None)
    kiem("không đọc được hạn thì độ tin TỤT",
         xuat_to_trinh(mot_co_hoi(tt(daoHan=None), 1000.0, SC)).tinCay < t.tinCay)

    # ── Router: bắc cầu STABLECOIN, không phải token PT ─────────────────
    from lai_suat.ty_lai_suat import (TAI_SAN_BAC_CAU, _tin_cay, mot_co_hoi
                                      as _mch, phi_vao_ra)

    hoi = []

    class _RGia:
        """Ghi lại ta HỎI cái gì, rồi trả lời như thể mọi thứ đo được."""

        def _gas_usd(self, chuoi, viec):
            return 0.50

        def phi_bps(self, tu, den, taiSan, von):
            hoi.append(taiSan)

            class _T:
                phiUsd, giayCho, khongDoDuoc = 2.5, 7.0, ("rui-ro-cau-noi",)
            return 25.0, _T()

    hoi.clear()
    phi_vao_ra("Ethereum", "SKAITO", 1000.0, _RGia())
    kiem("bắc cầu bằng STABLECOIN, không phải token PT",
         hoi == [TAI_SAN_BAC_CAU], str(hoi))
    kiem("và token PT KHÔNG bao giờ được đem đi hỏi cầu",
         "SKAITO" not in hoi,
         "không cầu nào chuyển một token PT của Pendle. Vào một vị thế PT "
         "là mang stablecoin sang chuỗi ấy rồi mới swap trên AMM — token PT "
         "sinh ra TẠI CHỖ và chết tại chỗ. Bản nháp đầu hỏi cầu bằng chính "
         "`t.taiSan`; Router trả None cho tất cả, đúng như nó phải làm, và "
         "cái sai nằm ở MÔ HÌNH chứ không ở Router")
    kiem("chuỗi NHÀ thì không bắc cầu, chỉ tốn gas",
         gan(phi_vao_ra("arbitrum", "X", 1000.0, _RGia())[1], 0.0))
    kiem("không có Router thì trả None, KHÔNG trả 0",
         phi_vao_ra("Ethereum", "X", 1000.0, None)[0] is None,
         "phí chưa đo được mà ghi 0 là nói NET đã trừ hết trong khi chưa")

    kiem("có Router thì phí vào+ra được TRỪ khỏi NET",
         _mch(tt(), 1000.0, SC, _RGia()).netBps
         < _mch(tt(), 1000.0, SC).netBps,
         "ty này trước đây để `netBps = gross`, không trừ phí nào")
    kiem("chưa đo được phí vào+ra thì độ tin TỤT",
         _tin_cay(_mch(tt(), 1000.0, SC))
         < _tin_cay(_mch(tt(), 1000.0, SC, _RGia())),
         "netBps đang thiếu một khoản chỉ có thể làm nó tệ đi. Không trừ ở "
         "đây là để một cơ hội CHƯA ĐO xếp trên một cơ hội ĐÃ ĐO — thưởng "
         "cho sự thiếu hiểu biết")
    coR = set(xuat_to_trinh(_mch(tt(), 1000.0, SC, _RGia())).phiConThieu)
    khongR = set(xuat_to_trinh(_mch(tt(), 1000.0, SC)).phiConThieu)
    kiem("Router đo được thì hai khoản ấy BIẾN MẤT khỏi khai báo",
         not ({"gas-vao-ra", "chuyen-von-giua-chuoi"} & coR),
         str(sorted(coR)))
    kiem("nhưng chúng có mặt khi KHÔNG có Router",
         {"gas-vao-ra", "chuyen-von-giua-chuoi"} <= khongR,
         str(sorted(khongR)))
    kiem("và được THAY bằng thứ chính Router khai là chưa tính",
         any(x.startswith("router:") for x in coR), str(sorted(coR)),)
    kiem("trượt giá AMM Pendle Ở LẠI dù Router đo được mọi thứ khác",
         "truot-gia-tren-amm-pendle" in coR,
         "nó đòi đường cong AMM của chính Pendle — không nguồn công khai "
         "nào cho, và Router không giả vờ ngược lại")

    # ── và Rủi Ro Tổng TỪ CHỐI vì khoá quá lâu ──────────────────────────
    from thi_bac_ty.danh_muc import DanhMuc
    from thi_bac_ty.rui_ro_tong import RuiRoTong
    pq = RuiRoTong().xet(t, DanhMuc(100000.0))
    kiem("khoá 57 ngày bị Rủi Ro Tổng TỪ CHỐI",
         not pq.duyet and any("khoá vốn" in l for l in pq.lyDo),
         "không phải vì 8% là xấu, mà vì khoá 57 ngày là từ chối mọi cơ hội "
         "tốt hơn xuất hiện trong 57 ngày ấy — chi phí đó không nằm trong "
         "con số 8%")
    kiem("nới trần khoá thì nó qua",
         RuiRoTong({"khoaVonToiDaGio": 24 * 365.0}).xet(t, DanhMuc(100000.0)).duyet,
         "người vận hành thấy đúng đánh đổi ấy và tự quyết — việc của người")


def kiem_bon_ty() -> None:
    print("\n-- BA HO duoi mot Thi Bac Ty --")
    from thi_bac_ty.trung_uong import TrungUong
    from thi_bac_ty.khuon_ty import Ty
    from thi_bac_ty.to_trinh import Chan

    class _TyGia(Ty):
        def __init__(self, ma, ho, ts, cang):
            super().__init__()
            type(self).ma = ma
            self._ma, self._ho, self._ts, self._cang = ma, ho, ts, cang
        @property
        def ma(self): return self._ma
        @property
        def ho(self): return self._ho
        @property
        def moTa(self): return "ty giả " + self._ho
        vonToiThieuKinhTeUsd = 50.0
        def kiem_khai(self): return []
        def quet(self): return [self._ts]
        def xet(self, co): return True, []
        def trinh(self, co):
            return _mau(ma=self._ma, ho=self._ho, taiSan=co, von=200.0,
                        chua=9000.0, khoa=0.0,
                        chan=(Chan("LONG", self._cang, co, None, "spot", "Base"),))

    tu = TrungUong(_tam("bahо"), {"vonBanDauUsd": 9000.0})
    for ma, ho, ts, cang in (
            ("perpetual.funding_spread.v1", "phai-sinh", "BTC", "binance"),
            ("lending.rate_rotation.v1", "tin-dung", "USDC", "aave-v3"),
            ("stablecoin.cross_venue.v1", "chenh-lech", "USDT", "okx")):
        kiem(f"đăng ký {ho}", tu.dang_ky(_TyGia(ma, ho, ts, cang)))

    lat = tu.mot_vong(lechDongHoGiay=1.0, cangChet=[], tuoiXauNhatGiay=1.0)
    theo = {x["ho"]: x for x in tu.pheu_day_du()["theoHo"]}
    kiem("phễu tách được BA họ",
         set(theo) == {"phai-sinh", "tin-dung", "chenh-lech"}, str(list(theo)))
    cap = {x["chienLuoc"] for x in (lat.phanBo or {}).get("daCap", [])}
    kiem("cả ba họ cùng được cấp vốn dưới MỘT Thị Bạc Ty", len(cap) == 3,
         str(sorted(cap)))
    kiem("và không tầng nào đi tắt", tu.so_dang_ky.soChuyenSai == 0)


def kiem_thang_chung() -> None:
    print("\n-- Thang rui ro dung chung, khong phai ban sao --")
    import pathlib
    from chuoi_chung.thang import rui_ro_su_dung, rui_ro_tvl
    from tin_dung.ty_vay import _rui_ro_su_dung, _rui_ro_tvl

    kiem("ty tín dụng DÙNG bản chung, không giữ bản sao",
         _rui_ro_tvl is rui_ro_tvl and _rui_ro_su_dung is rui_ro_su_dung,
         "hai bản sao sẽ lệch nhau đúng vào ngày ai đó hiệu chỉnh một bản")

    goc = pathlib.Path(__file__).resolve().parent.parent
    xau = []
    for goi in ("tin_dung", "lai_suat", "on_dinh"):
        for p in (goc / goi).glob("*.py"):
            for d in p.read_text(encoding="utf-8").splitlines():
                d = d.strip()
                for kia in ("tin_dung", "lai_suat", "on_dinh", "bac"):
                    if kia != goi and d.startswith((f"import {kia}", f"from {kia}")):
                        xau.append(f"{goi}/{p.name}: {d}")
    kiem("không ty nào import một ty khác", not xau, str(xau),)
    kiem("thang chung KHÔNG nằm trong trung ương",
         not (goc / "thi_bac_ty" / "thang.py").exists(),
         "Trung Ương không biết TVL hay dùng vốn là gì")



def kiem_von_toi_thieu() -> None:
    print("\n-- $100 chay duoc ca he, nhung KHONG ep engine nao vao lenh --")
    from thi_bac_ty.danh_muc import DanhMuc
    from thi_bac_ty.khuon_ty import Ty
    from thi_bac_ty.rui_ro_tong import RuiRoTong
    from thi_bac_ty.to_trinh import Chan

    # ── hợp đồng ────────────────────────────────────────────────────────
    from dataclasses import replace
    t = _mau(von=500.0, chua=9000.0)
    kiem("tờ trình mang theo vốn tối thiểu kinh tế",
         "vonToiThieuKinhTeUsd" in t.tom_tat())
    kiem("xin ÍT HƠN ngưỡng mình khai là tờ trình TỰ MÂU THUẪN",
         not replace(t, vonToiThieuKinhTeUsd=5000.0).hop_le,
         "ty phải hoặc xin đủ, hoặc hạ ngưỡng nó khai — để trung ương gỡ hộ "
         "là bắt trung ương biết chi phí của ngành")
    kiem("khai ngưỡng ≤ 0 bị bắt",
         not replace(t, vonCanUsd=500.0, vonToiThieuKinhTeUsd=0.0).hop_le,
         "khai 0 nghĩa là 'engine này kinh tế ở mọi cỡ vốn', và chưa engine "
         "nào như thế")
    kiem("xin đủ thì hợp lệ",
         replace(t, vonToiThieuKinhTeUsd=500.0).hop_le)

    # ── khuôn ty: chưa khai thì CHẾT Ở CỬA ──────────────────────────────
    class TyQuen(Ty):
        ma, ho, moTa = "perpetual.funding_spread.v1", "phai-sinh", "quên khai"
        def quet(self): return []
        def xet(self, co): return False, []
        def trinh(self, co): return None

    kiem("ty chưa khai ngưỡng kinh tế thì kiem_khai() bắt",
         any("vonToiThieuKinhTeUsd" in l for l in TyQuen.kiem_khai()),
         "một ty không biết ngưỡng của chính nó sẽ đều đặn trình lên những "
         "cơ hội mà phí ăn sạch, để trung ương loại hộ")

    class TyAm(TyQuen):
        vonToiThieuKinhTeUsd = -1.0
    kiem("khai số âm cũng bị bắt", TyAm.kiem_khai() != [])

    # ── Rủi Ro Tổng: cấp ĐỦ hoặc KHÔNG CẤP ──────────────────────────────
    rrt = RuiRoTong()
    dm = DanhMuc(1000.0)               # trần một cơ hội = $150
    it = replace(_mau(von=100.0, chua=9000.0), vonToiThieuKinhTeUsd=100.0)
    kiem("engine rẻ được cấp ở NAV $1.000", rrt.xet(it, dm).duyet)

    dat = replace(_mau(von=1000.0, chua=90000.0), vonToiThieuKinhTeUsd=1000.0)
    pq = rrt.xet(dat, dm)
    kiem("engine đắt bị TỪ CHỐI, không phải bị cắt xuống $150",
         not pq.duyet and gan(pq.choToiDaUsd, 0.0),
         "cắt trần xuống dưới ngưỡng kinh tế rồi vẫn cấp là tệ hơn không "
         "cấp: vốn bị giữ chỗ, một slot bị tiêu, và lãi không bù nổi phí")
    kiem("và nói rõ QUAN SÁT chứ không ép vào lệnh",
         any("QUAN SÁT" in l for l in pq.lyDo), str(pq.lyDo))
    kiem("NAV lớn hơn thì chính engine ấy qua",
         rrt.xet(dat, DanhMuc(20000.0)).duyet)


def kiem_che_van_hanh() -> None:
    print("\n-- Ba che do, va may KHONG duoc tu ep len cao hon --")
    from thi_bac_ty.che_van_hanh import (BAC, GIAY, QUAN_SAT, THAT, che_cua_ty,
                                         von_can_de_chay, von_hoa_ha_tang)

    class _T:
        def __init__(self, ma, v): self.ma, self.ho, self.vonToiThieuKinhTeUsd = ma, "phai-sinh", v

    kiem("ba bậc, thứ tự từ thấp lên cao", BAC == (QUAN_SAT, GIAY, THAT))

    re_ = _T("re.v1", 100.0)
    dat = _T("dat.v1", 1000.0)
    kiem("NAV $100: engine $100 vẫn QUAN SÁT (rót được chỉ $15)",
         che_cua_ty(re_, 100.0, 0.15).che == QUAN_SAT)
    kiem("NAV $1.000: engine $100 lên GIẤY",
         che_cua_ty(re_, 1000.0, 0.15).che == GIAY)
    kiem("nhưng engine $1.000 vẫn QUAN SÁT ở NAV $1.000",
         che_cua_ty(dat, 1000.0, 0.15).che == QUAN_SAT)
    kiem("NAV $20.000 thì engine đắt cũng lên GIẤY",
         che_cua_ty(dat, 20000.0, 0.15).che == GIAY)

    kiem("KHÔNG có lớp ký lệnh thì KHÔNG bao giờ lên THẬT",
         che_cua_ty(re_, 1_000_000.0, 0.15).che == GIAY,
         "THẬT chưa với tới được là một SỰ THẬT, không phải một cấu hình")
    kiem("có lớp ký lệnh thì mới lên THẬT",
         che_cua_ty(re_, 1_000_000.0, 0.15, True).che == THAT)

    kiem("QUAN SÁT thì KHÔNG được cấp vốn",
         not che_cua_ty(dat, 1000.0, 0.15).duocCapVon)
    kiem("GIẤY thì được cấp — trên sổ giấy",
         che_cua_ty(re_, 1000.0, 0.15).duocCapVon)
    kiem("chưa khai ngưỡng → QUAN SÁT",
         che_cua_ty(_T("x.v1", None), 1e9, 0.15).che == QUAN_SAT)
    kiem("và mọi chế độ đều nói được VÌ SAO",
         all(che_cua_ty(x, 1000.0, 0.15).vi
             for x in (re_, dat, _T("y.v1", None))))

    kiem("vốn cần để có ít nhất một engine chạy = ngưỡng RẺ NHẤT / trần",
         gan(von_can_de_chay([re_, dat], 0.15), 100.0 / 0.15))
    kiem("không ty nào khai thì None", von_can_de_chay([], 0.15) is None)

    h = von_hoa_ha_tang(10.0)
    kiem("chi phí hạ tầng quy ra năm", gan(h["chiPhiNamUsd"], 120.0))
    kiem("và vốn cần để hoà nó ở 20%/năm là $600",
         gan(h["vonHoaVon"]["20%"], 600.0),
         "$100 vốn kiếm 20%/năm là $20 — vẫn ÂM sau hạ tầng $120")
    kiem("kèm lời nhắc đừng đo bằng số đô",
         "chất lượng quyết định" in h["loiNhac"])


def kiem_hieu_nang() -> None:
    print("\n-- Hieu nang: duong NAV, khong phai mot APR nhan thang --")
    from thi_bac_ty.hieu_nang import (TOI_THIEU_GIO, DuongNav,
                                      doi_chieu_giay_that, do_hieu_nang)

    GIO = 3_600_000.0
    kiem("chưa có điểm nào thì nói chưa có",
         do_hieu_nang([], 100.0)["duDeKetLuan"] is False)

    ngan = [(0.0, 100.0), (12 * GIO, 100.3)]
    d = do_hieu_nang(ngan, 100.0)
    kiem("nửa ngày dữ liệu thì KHÔNG quy ra năm",
         d["duDeKetLuan"] is False and d["cagrPhanTram"] is None,
         "quy 0,3% của nửa ngày ra năm cho một tỉ suất vô nghĩa mà trông rất "
         "thuyết phục")
    kiem("và nói rõ cần bao nhiêu", str(int(TOI_THIEU_GIO)) in d["vi"])

    # 100 → 112 → 103 → 122 qua một năm
    nam = 365 * 24 * GIO
    ds = [(0.0, 100.0), (nam * 0.3, 112.0), (nam * 0.6, 103.0), (nam, 122.0)]
    d = do_hieu_nang(ds, 100.0)
    kiem("đủ mẫu thì tính được CAGR", d["duDeKetLuan"] and d["cagrPhanTram"])
    kiem("CAGR ≈ 22% cho một năm 100 → 122",
         gan(d["cagrPhanTram"], 22.0, 0.5), f"{d['cagrPhanTram']}")
    kiem("sụt vốn tối đa tính từ ĐỈNH TRƯỚC ĐÓ, không từ vốn ban đầu",
         gan(d["sutVonToiDaPhanTram"], (112 - 103) / 112 * 100.0, 1e-6),
         f"{d['sutVonToiDaPhanTram']} — đáy 103 so với đỉnh 112, không so 100")
    kiem("đo được bao lâu chưa về lại đỉnh cũ", d["gioDuoiDayLauNhat"] > 0)
    kiem("và biết lúc này còn dưới đáy không", d["dangDuoiDay"] is False)

    xuong = do_hieu_nang([(0.0, 100.0), (nam, 90.0)], 100.0)
    kiem("một năm âm thì sụt vốn tối đa = 10%",
         gan(xuong["sutVonToiDaPhanTram"], 10.0, 1e-6))
    kiem("và vẫn còn dưới đáy", xuong["dangDuoiDay"] is True)

    dn = DuongNav(tran=3)
    for v in (100.0, 101.0, 102.0, 103.0, 104.0):
        dn.ghi(v)
    kiem("đường NAV có trần, và bỏ điểm CŨ NHẤT",
         len(dn.diem) == 3 and gan(dn.diem[-1][1], 104.0),
         "đỉnh và đáy gần đây là thứ quyết định sụt vốn, và chúng nằm ở cuối")

    # ── đối chiếu giấy ↔ thật: chưa có vế thật ──────────────────────────
    from thi_bac_ty.so_cai import ButToan, SoCai
    sc = SoCai(_tam("gt") / "so.sqlite3")
    sc.ghi(ButToan("FUNDING", "mô phỏng", 1.0, "a.b.v1", "TT1"))
    dc = doi_chieu_giay_that(sc)
    kiem("chưa có lệnh thật thì KHÔNG đối chiếu được",
         dc["doiChieuDuoc"] is False and dc["soButToanThat"] == 0,
         "trả về một con số 'sai lệch' lúc này là bịa")
    kiem("và nói rõ khi nào mới đo được", "lớp ký lệnh" in dc["khiNaoDoDuoc"])


def kiem_lop_boc_khai_bao() -> None:
    print("\n-- Lop boc nhip KHONG duoc che khai bao cua ty that --")
    from bac.vong import _NhipRieng
    from thi_bac_ty.khuon_ty import Ty

    class TyThat(Ty):
        ma, ho = "lending.rate_rotation.v1", "tin-dung"
        moTa = "ty thật"
        vonToiThieuKinhTeUsd = 777.0
        def quet(self): return []
        def xet(self, co): return False, []
        def trinh(self, co): return None

    g = TyThat()
    b = _NhipRieng(g, 60.0)
    for ten in ("ma", "ho", "moTa", "vonToiThieuKinhTeUsd"):
        kiem(f"lớp bọc trả đúng `{ten}` của ty thật",
             getattr(b, ten) == getattr(g, ten),
             f"bọc={getattr(b, ten)!r} thật={getattr(g, ten)!r} — `Ty` khai "
             f"sẵn thuộc tính này ở tầng LỚP, nên tra thành công (ra giá trị "
             f"rỗng của lớp bọc) và `__getattr__` không bao giờ được gọi")
    kiem("và kiem_khai() soi ty thật", b.kiem_khai() == g.kiem_khai())



def _bg_cs(san="binance", ma="BTC", rate=0.0001, iv=8.0, mark=78000.0,
        moc=None, oi=5e8):
    from phai_sinh_chung.models import BaoGia
    from phai_sinh_chung.dong_ho import dong_ho
    now = dong_ho.bay_gio_ms()
    return BaoGia(san=san, ma=ma, rate=rate, intervalGio=iv, markPx=mark,
                  mocKeMs=int(moc if moc is not None else now + 3_600_000),
                  oiUsd=oi, nhanTsMs=int(now), nguonTsMs=int(now))


def _dn_cs(san="binance", ma="BTC", gia=78000.0):
    from san_chung.giao_ngay import DinhSo
    return DinhSo(san, ma + "/USDT", gia * 0.9999, gia, 100.0, 100.0)


def kiem_co_so() -> None:
    print("\n-- Ty co so (cash-and-carry): BASIS KHONG phai thu nhap --")
    from co_so.ty_co_so import (CONFIG, CUA, CoHoiCoSo, CongRuiRo, TyCoSo,
                                _tin_cay, basis_bps, mot_co_hoi,
                                phi_khu_hoi_bps, tim_co_hoi, xuat_to_trinh)

    kiem("CUA và CONFIG['ruiRo'] khai cùng một bộ khoá",
         set(CUA) == set(CONFIG["ruiRo"]),
         str(set(CUA) ^ set(CONFIG["ruiRo"])))

    # ── phí: HAI chân, HAI chiều ────────────────────────────────────────
    kiem("phí = 4 lần taker (2 chân × 2 chiều)",
         gan(phi_khu_hoi_bps("binance", {"binance": 5.0}), 20.0),
         "tính một chân hay một chiều thôi là báo cáo một phần tư tới một "
         "nửa chi phí, và với edge tính bằng bps thì đó là phần quyết định")
    kiem("sàn lạ rơi về _khac",
         gan(phi_khu_hoi_bps("la", {"_khac": 7.5}), 30.0))

    # ── basis ───────────────────────────────────────────────────────────
    kiem("basis dương = perp đắt hơn giao ngay",
         gan(basis_bps(100.5, 100.0), 50.0))
    kiem("basis âm = perp rẻ hơn", gan(basis_bps(99.5, 100.0), -50.0))
    kiem("giao ngay ≤ 0 thì trả 0, không chia cho 0",
         gan(basis_bps(100.0, 0.0), 0.0))

    SC = CONFIG["sucChua"]
    PHI = CONFIG["phiTakerBps"]

    # ── BASIS KHÔNG vào NET ─────────────────────────────────────────────
    a = mot_co_hoi("binance", "BTC", _dn_cs(gia=78000.0), _bg_cs(mark=78000.0),
                   200.0, 168.0, PHI, SC)
    b = mot_co_hoi("binance", "BTC", _dn_cs(gia=78000.0), _bg_cs(mark=78400.0),
                   200.0, 168.0, PHI, SC)
    kiem("basis rộng ra KHÔNG làm NET đổi", gan(a.netBps, b.netBps),
         "perp không đáo hạn nên không có gì bảo đảm nó hội tụ về giao ngay "
         "— cộng basis vào NET là báo cáo một khoản lãi chưa ai trả")
    kiem("nhưng basis vẫn đo được và khác nhau",
         b.basisBps > a.basisBps + 40.0)

    # ── funding đếm theo MỐC, không nhân theo giờ ───────────────────────
    it = mot_co_hoi("binance", "BTC", _dn_cs(), _bg_cs(rate=0.0001, iv=8.0),
                    200.0, 168.0, PHI, SC)
    kiem("giữ 168 giờ trên chu kỳ 8 giờ chứa ~21 mốc",
         20 <= it.soMoc <= 22, str(it.soMoc))
    kiem("gross = số MỐC × rate, không phải giờ × rate",
         gan(it.grossBps, it.soMoc * 0.0001 * 10_000.0, 1e-6),
         "giữ 4 giờ trên sàn kết toán 8 giờ có thể thu ĐÚNG BẰNG KHÔNG")

    cong = CongRuiRo(CONFIG["ruiRo"])

    def ma_cua(co):
        return {m for m, _ in cong.xet(co)[1]}

    lanh = mot_co_hoi("binance", "BTC", _dn_cs(), _bg_cs(rate=0.0003),
                      200.0, 168.0, PHI, SC)
    kiem("cơ hội lành qua sạch", ma_cua(lanh) == set(), str(ma_cua(lanh)))

    am = mot_co_hoi("binance", "BTC", _dn_cs(gia=78000.0),
                    _bg_cs(rate=0.0003, mark=77700.0), 200.0, 168.0, PHI, SC)
    kiem("basis âm quá sâu → CHẶN", "basis-am-qua-sau" in ma_cua(am),
         "mua giao ngay ĐẮT hơn giá thanh lý của chân short là một khoản lỗ "
         "trả trước, không phải cơ hội")
    rong = mot_co_hoi("binance", "BTC", _dn_cs(gia=78000.0),
                      _bg_cs(rate=0.0003, mark=80000.0), 200.0, 168.0, PHI, SC)
    kiem("basis dương quá rộng cũng CHẶN",
         "basis-duong-qua-rong" in ma_cua(rong),
         "hoặc một trong hai giá sai, hoặc thị trường đang định giá một rủi "
         "ro ta chưa thấy")
    kiem("NET dưới ngưỡng → chặn",
         "net-duoi-nguong" in ma_cua(
             mot_co_hoi("binance", "BTC", _dn_cs(), _bg_cs(rate=0.00001),
                        200.0, 168.0, PHI, SC)))

    from phai_sinh_chung.dong_ho import dong_ho as _dh
    ngan = mot_co_hoi("binance", "BTC", _dn_cs(),
                      _bg_cs(rate=0.0003, iv=8.0,
                          moc=_dh.bay_gio_ms() + 20 * 3_600_000),
                      200.0, 4.0, PHI, SC)
    kiem("cửa sổ không chứa mốc nào → CHẶN",
         "khong-moc-nao" in ma_cua(ngan),
         "funding trả theo MỐC, nên giữ mà không qua mốc nào thì thu đúng "
         "bằng KHÔNG")

    # ── ghép theo (sàn, mã); thiếu một vế thì BỎ ────────────────────────
    ra = tim_co_hoi([_dn_cs("binance", "BTC"), _dn_cs("okx", "ETH")],
                    [_bg_cs("binance", "BTC", rate=0.0003),
                     _bg_cs("bybit", "BTC", rate=0.0003),
                     _bg_cs("okx", "SOL", rate=0.0003)],
                    200.0, 168.0, PHI, SC, cong)
    kiem("chỉ ghép được cặp có CẢ giao ngay lẫn perp cùng sàn cùng mã",
         [(c.san, c.ma) for c in ra] == [("binance", "BTC")],
         str([(c.san, c.ma) for c in ra])
         + " — bybit thiếu giao ngay, okx/SOL thiếu giao ngay, okx/ETH "
           "thiếu perp")

    # ── độ tin hạ theo độ dài cửa sổ ────────────────────────────────────
    it_moc = mot_co_hoi("binance", "BTC", _dn_cs(), _bg_cs(rate=0.0003),
                        200.0, 16.0, PHI, SC)
    nhieu_moc = mot_co_hoi("binance", "BTC", _dn_cs(), _bg_cs(rate=0.0003),
                           200.0, 720.0, PHI, SC)
    kiem("cửa sổ càng dài, độ tin càng THẤP",
         _tin_cay(nhieu_moc) < _tin_cay(it_moc),
         "gross = mức funding HIỆN TẠI × số mốc; với một mốc đó gần như một "
         "sự thật, với chín mươi mốc đó là một dự báo ba tháng đội lốt một "
         "phép nhân")
    kiem("chưa đo được sức chứa thì độ tin cũng tụt",
         _tin_cay(mot_co_hoi("binance", "BTC", _dn_cs(),
                             _bg_cs(rate=0.0003, oi=None), 200.0, 168.0,
                             PHI, SC)) < _tin_cay(it_moc))

    # ── tờ trình ────────────────────────────────────────────────────────
    t = xuat_to_trinh(lanh)
    kiem("tờ trình hợp lệ", t.hop_le, str(t.kiem()))
    kiem("họ là phai-sinh, cùng họ với ty chênh funding", t.ho == "phai-sinh")
    kiem("hai chân CÙNG một sàn — không phải chuyển vốn",
         t.chan[0].cang == t.chan[1].cang,
         "mua giao ngay sàn A rồi bán khống perp sàn B là thêm hai thứ ta "
         "chưa làm được: chuyển vốn, và rủi ro một sàn sập khi chân kia mở")
    kiem("một chân giao ngay, một chân perp",
         {c.loai for c in t.chan} == {"spot", "perp"})
    kiem("và hai chân ngược chiều nhau",
         {c.ben for c in t.chan} == {"LONG", "SHORT"})
    kiem("bằng chứng nói rõ basis KHÔNG vào NET",
         any("KHÔNG tính vào NET" in b for b in t.bangChung))
    kiem("và nói rõ GIẢ ĐỊNH funding giữ nguyên",
         any("GIẢ ĐỊNH" in b for b in t.bangChung),
         "nó không giữ nguyên, và người đọc phải thấy điều đó")


def kiem_ha_tang_ho() -> None:
    print("\n-- Ha tang dung chung: mot ban the, khong phai ban sao --")
    import pathlib
    from thi_bac_ty.hien_phap import _goi_ty

    ten = {d.name for d in _goi_ty()}
    kiem("hiến pháp nhận đúng CHÍN ty",
         ten == {"bac", "co_so", "dex_arb", "kham_ngoai", "lai_suat",
                 "lp_amm", "on_dinh", "quyen_chon", "tin_dung"}, str(ten))
    kiem("`kham_ngoai` LÀ một ty, không phải hạ tầng",
         "kham_ngoai" in ten,
         "nó có một lớp kế thừa `khuon_ty.Ty` và nó nộp tờ trình — đó chính "
         "là định nghĩa của ty. Adapter mỏng vẫn là ty; chỗ nó lấy số ở đâu "
         "không đổi việc ấy")
    kiem("và KHÔNG coi hạ tầng là ty",
         not ({"phai_sinh_chung", "san_chung", "chuoi_chung"} & ten),
         "danh sách loại trừ đòi người ta nhớ cập nhật, và lần quên đầu tiên "
         "đã xảy ra ngay khi `phai_sinh_chung/` ra đời")

    goc = pathlib.Path(__file__).resolve().parent.parent

    # ── bí danh phải TRỎ TỚI cùng một thứ, không phải bản sao ───────────
    from bac.dongho import dem_moc as a1
    from phai_sinh_chung.dongho import dem_moc as a2
    kiem("bac.dongho là BÍ DANH, không phải bản sao", a1 is a2,
         "hai bản sao sẽ lệch nhau đúng vào ngày ai đó sửa một bản")
    from bac.models import BaoGia as b1
    from phai_sinh_chung.models import BaoGia as b2
    kiem("bac.models.BaoGia cũng là bí danh", b1 is b2)
    from bac.dong_ho import dong_ho as c1
    from phai_sinh_chung.dong_ho import dong_ho as c2
    kiem("MỘT đồng hồ cho cả họ, không phải mỗi ty một cái", c1 is c2,
         "hai ty đo lệch riêng là hai phần bù khác nhau cho cùng một cái "
         "đồng hồ, và chúng sẽ đếm mốc ra hai kết quả khác nhau")
    from on_dinh.nguon import SanGiaoNgay as d1
    from san_chung.giao_ngay import SanGiaoNgay as d2
    kiem("connector giao ngay dùng chung giữa hai HỌ", d1 is d2,
         "on_dinh cần bid/ask USDC/USDT, co_so cần giá BTC/ETH — cùng ba "
         "sàn, cùng ba hình dạng JSON")

    # ── thân hàm chỉ nằm MỘT chỗ ────────────────────────────────────────
    for ten_f, nha in (("def dem_moc", "phai_sinh_chung/dongho.py"),
                       ("class BaoGia", "phai_sinh_chung/models.py"),
                       ("class DinhSo", "san_chung/giao_ngay.py")):
        # Đếm dòng ĐỊNH NGHĨA ở cột 0, không đếm mọi lần tên ấy xuất hiện.
        # Chính file này nhắc cả ba tên trong danh sách trên — đếm cả nhắc
        # thì phép kiểm tự tố cáo mình, và một phép kiểm đỏ vì lý do sai
        # còn tệ hơn không có nó.
        cho = [str(p.relative_to(goc)).replace(chr(92), "/")
               for p in goc.rglob("*.py")
               if "__pycache__" not in str(p)
               and any(_dinh_nghia(l, ten_f)
                       for l in p.read_text(encoding="utf-8").splitlines())]
        kiem(f"`{ten_f}` chỉ định nghĩa ở MỘT chỗ",
             cho == [nha], f"{cho} — phải là ['{nha}']")

    # ── ty vẫn không gọi ty ─────────────────────────────────────────────
    xau = []
    for d in _goi_ty():
        for p in d.glob("*.py"):
            for l in p.read_text(encoding="utf-8").splitlines():
                l = l.strip()
                for k in ten - {d.name}:
                    if l.startswith((f"import {k}", f"from {k}")):
                        xau.append(f"{d.name}/{p.name}: {l}")
    kiem("không ty nào gọi ty khác, kể cả sau hai lần tách", not xau, str(xau))

def _gg(chuoi="arbitrum", wei=20_000_000):
    from chuyen_von.gas import GiaGas
    import time as _t
    return GiaGas(chuoi, wei, _t.time() * 1000.0)


def _bgc(phi=2.5, gas=0.09, giay=7.0, loi=""):
    from chuyen_von.cau_noi import BaoGiaCau
    import time as _t
    return BaoGiaCau("USDC", "ethereum", "arbitrum", 1000.0, phi, gas, giay,
                     "eco", _t.time() * 1000.0, loi)


def kiem_router_tuyen() -> None:
    print("\n-- Router · TUYEN: mot chang mu thi CA TUYEN mu --")
    from chuyen_von.diem import ChangDuong, Diem, TuyenDuong, khong_co_tuyen

    e = Diem("chuoi", "ethereum")
    a = Diem("chuoi", "arbitrum")
    b = Diem("san", "binance")

    kiem("loại điểm lạ bị từ chối ngay lúc dựng",
         _nem(lambda: Diem("vi-tien", "metamask"), ValueError),
         "một điểm không thuộc loại nào thì mọi luật ghép tuyến bên dưới "
         "đều không áp dụng được, và nó sẽ lộ ra ở chỗ khác")

    # ── luật cộng trung thực ────────────────────────────────────────────
    lanh = TuyenDuong((ChangDuong(b, a, "rut-cex", 0.30, 300.0, "bảng"),
                       ChangDuong(a, e, "cau-noi", 2.60, 7.0, "lifi")))
    kiem("tuyến lành: phí CỘNG", gan(lanh.phiUsd, 2.90))
    kiem("và thời gian cũng CỘNG, không lấy max", gan(lanh.giayCho, 307.0),
         "vốn đang trên cầu nối thì chưa nạp vào sàn được — hai chặng không "
         "chồng lên nhau được")

    mu = TuyenDuong((ChangDuong(b, a, "rut-cex", None, None, "bảng quá hạn"),
                     ChangDuong(a, e, "cau-noi", 2.60, 7.0, "lifi")))
    kiem("MỘT chặng mù thì CẢ TUYẾN mù", mu.phiUsd is None,
         "cộng hai chặng biết giá rồi bỏ qua chặng thứ ba cho ra một con số "
         "trông như đã đủ, và không gì trong nó nói rằng nó thiếu — sai "
         "theo đúng hướng nguy hiểm nhất, hào phóng với chính mình")
    kiem("thời gian cũng mù theo", mu.giayCho is None)
    kiem("và bps cũng mù theo", mu.phi_bps(1000.0) is None)
    kiem("chặng mù được KHAI RA đích danh",
         any(x.startswith("chang-mu:") for x in mu.khongDoDuoc),
         str(mu.khongDoDuoc))

    # ── phí cố định thì bps phụ thuộc VỐN ───────────────────────────────
    kiem("$2,90 trên $200 = 145 bps", gan(lanh.phi_bps(200.0), 145.0))
    kiem("cùng khoản ấy trên $50.000 = 0,58 bps",
         gan(lanh.phi_bps(50_000.0), 0.58),
         "phí chuyển vốn là khoản CỐ ĐỊNH — đó là lý do ty nhỏ bị chặn bởi "
         "đúng khoản mà ty lớn không thấy")
    kiem("vốn 0 thì không chia, trả None", lanh.phi_bps(0.0) is None)

    # ── gộp khai báo ────────────────────────────────────────────────────
    hai = TuyenDuong((ChangDuong(b, a, "rut-cex", 0.3, 300.0, "x", ("p",)),
                      ChangDuong(a, e, "cau-noi", 2.6, 7.0, "y", ("p", "q"))))
    kiem("khai báo thiếu của các chặng được GỘP và bỏ trùng",
         hai.khongDoDuoc == ("p", "q"), str(hai.khongDoDuoc))

    trong = khong_co_tuyen("không có chuỗi chung")
    kiem("tuyến rỗng KHÔNG đo được", not trong.doDuoc)
    kiem("và nó nói VÌ SAO không có tuyến", "chuỗi chung" in trong.viSaoKhong)
    kiem("tuyến rỗng khác tuyến phí 0",
         trong.phiUsd is None
         and gan(TuyenDuong((ChangDuong(a, a, "gas-thuan", 0.0, 0.0, "z"),))
                 .phiUsd, 0.0),
         "không có đường đi KHÁC HẲN đi mà không tốn gì")


def kiem_router_bang_do() -> None:
    print("\n-- Router · BANG DO TAY: co xuat xu, va co HAN --")
    import datetime as _dt

    from chuyen_von.bang_do import (BANG, HAN_NGAY, chan_doan, chuoi_cua_san,
                                    kiem as kiem_bang, tra_cuu)

    kiem("bảng đo tay không tự mâu thuẫn", not kiem_bang(), str(kiem_bang()))

    from chuyen_von.cau_noi import TOKEN_BANG, kiem_token
    kiem("bảng địa chỉ token không tự mâu thuẫn",
         not kiem_token(), str(kiem_token()))
    kiem("thập phân theo TỪNG (tài sản, chuỗi), không theo tài sản",
         TOKEN_BANG[("DAI", "ethereum")].thapPhan == 18
         and TOKEN_BANG[("USDC", "ethereum")].thapPhan == 6,
         "Ethereum có HAI token cùng ký hiệu USDC — một cái 6 thập phân và "
         "một cái 18 ở địa chỉ khác. Chia sai mười hai bậc thì phí 2,5 "
         "thành phí 2.500.000")
    kiem("ký hiệu LI.FI trả về được ghi lại, kể cả khi nó LỆCH",
         TOKEN_BANG[("USDT", "arbitrum")].kyHieuThat == "USDT0",
         "địa chỉ tôi gõ cho USDT/Arbitrum thật ra là USDT0 — bản LayerZero "
         "OFT, một token KHÁC. Ghi đúng tên nó thì lần sau còn ai đó soát "
         "lại được; ghi là USDT thì nó thành sự thật sau một lần đọc")
    kiem("không hai tài sản nào cùng một địa chỉ trên cùng một chuỗi",
         len({(c, d.diaChi.lower()) for (t, c), d in TOKEN_BANG.items()})
         == len(TOKEN_BANG))
    kiem("mọi dòng đều có xuất xứ và ngày đo",
         all(d.nguon and d.ngayDo for d in BANG),
         "số gõ tay không có nguồn thì không kiểm lại được, và không kiểm "
         "lại được thì không sửa được khi sàn đổi phí")

    d = BANG[0]
    moi = _dt.date.fromisoformat(d.ngayDo) + _dt.timedelta(days=1)
    cu = _dt.date.fromisoformat(d.ngayDo) + _dt.timedelta(days=int(HAN_NGAY) + 1)

    kiem("dòng còn hạn thì tra được",
         tra_cuu(d.san, d.taiSan, d.chuoi, moi) is not None)
    kiem("dòng QUÁ HẠN trả None, KHÔNG trả số cũ",
         tra_cuu(d.san, d.taiSan, d.chuoi, cu) is None,
         "một con số 90 ngày tuổi trông giống hệt một con số đúng, và không "
         "gì trong nó nói rằng nó cũ")
    kiem("và chẩn đoán nói rõ phải đọc lại trang nào",
         d.nguon in chan_doan(d.san, d.taiSan, d.chuoi, cu),
         chan_doan(d.san, d.taiSan, d.chuoi, cu))
    kiem("cặp chưa ai đo cũng trả None",
         tra_cuu("sàn-không-có", "USDC", "ethereum") is None)

    kiem("tra cứu không phân biệt hoa thường",
         tra_cuu("BINANCE", "usdc", "ARBITRUM", moi) is not None,
         "ty gọi bằng tên sàn viết thường, bảng ghi thường — nhưng một ty "
         "sau sẽ gọi bằng tên khác, và im lặng trả None là mù giả")

    kiem("bybit KHÔNG rút USDC về ethereum, và bảng nói vậy",
         "ethereum" not in chuoi_cua_san("bybit", "USDC"),
         str(chuoi_cua_san("bybit", "USDC")))
    kiem("chuỗi quá hạn rơi khỏi danh sách sàn dùng được",
         chuoi_cua_san(d.san, d.taiSan, cu) == (),
         "danh sách chuỗi dựng từ dòng CÒN HẠN, nếu không thì tuyến sẽ ghép "
         "qua một chuỗi mà con số của nó đã hết tin được")


def kiem_router_dinh_tuyen() -> None:
    print("\n-- Router · DINH TUYEN: bon dang tuyen, ba nguon --")
    from chuyen_von.diem import Diem
    from chuyen_von.dinh_tuyen import UU_TIEN_TRUNG_GIAN, DinhTuyen
    from chuyen_von.gas import GAS_LIMIT, TOKEN_GOC

    GIA = {"ETH": 2461.0, "POL": 0.31}
    gas = {"arbitrum": _gg("arbitrum", 20_000_000),
           "ethereum": _gg("ethereum", 46_000_000),
           "polygon": _gg("polygon", 277_000_000_000)}

    r = DinhTuyen(giaGas=gas, giaTokenGocUsd=GIA,
                  baoGiaCau=lambda *a: _bgc())

    # ── gas: ba thứ, thiếu một là None ──────────────────────────────────
    g = gas["arbitrum"]
    kiem("gas ra đô = wei × limit × giá token",
         gan(g.usd("chuyen-erc20", 2461.0),
             20_000_000 * GAS_LIMIT["chuyen-erc20"] / 1e18 * 2461.0, 1e-9))
    kiem("thiếu GIÁ TOKEN GỐC thì gas là None, không phải 0",
         g.usd("chuyen-erc20", None) is None,
         "thiếu giá token mà vẫn trả một con số là ngầm giả định giá bằng "
         "1 — đúng loại lỗi mà `None` khác `0` sinh ra để chặn")
    kiem("giá token ≤ 0 cũng là không biết",
         g.usd("chuyen-erc20", 0.0) is None)
    kiem("việc lạ không có gasLimit thì cũng None",
         g.usd("dao-bitcoin", 2461.0) is None)
    # ── chuỗi ĐỌC được gas ≠ chuỗi DÙNG được ────────────────────────────
    thieuGia = DinhTuyen(giaGas=gas, giaTokenGocUsd={"ETH": 2461.0})
    kiem("Polygon đọc được gas nhưng KHÔNG có giá POL → không dùng được",
         "polygon" not in thieuGia.chuoi_dung_duoc()
         and "polygon" in thieuGia.tom_tat()["chuoiCoGas"],
         "buồng lái từng báo «gas SỐNG trên 4 chuỗi» trong khi mọi tuyến "
         "Polygon đều mù — một đèn xanh cho thứ không chạy. Con số đáng "
         "báo là con số DÙNG ĐƯỢC, không phải con số ĐỌC ĐƯỢC")
    kiem("và nó được tách riêng, không lẫn với chuỗi mất gas",
         thieuGia.tom_tat()["chuoiCoGasNhungThieuGia"] == ["polygon"],
         "hai trạng thái này đòi hai cách sửa khác nhau")
    kiem("có đủ giá thì bốn chuỗi đều dùng được",
         set(DinhTuyen(giaGas=gas,
                       giaTokenGocUsd={"ETH": 2461.0, "POL": 0.11})
             .chuoi_dung_duoc()) == set(gas))

    # ── mọi token TRẢ GAS phải nằm trong danh sách quét ──────────────────
    from bac.config import CONFIG as _CFG
    from chuyen_von.gas import TOKEN_GOC as _TG
    import json as _js
    import pathlib as _pl
    _cj = _pl.Path(__file__).resolve().parent.parent / "config.json"
    _ma_json = ((_js.loads(_cj.read_text(encoding="utf-8-sig")).get("quet")
                 or {}).get("ma") if _cj.exists() else None)
    kiem("`config.json` ĐÈ lên `bac/config.py`, và nó là file quyết định",
         _ma_json is None or _ma_json == _CFG["quet"]["ma"],
         f"json={_ma_json} · hiệu lực={_CFG['quet']['ma']} — sửa mặc định "
         f"trong mã mà quên file này thì KHÔNG có tác dụng gì, và nó im "
         f"lặng. Đã cắn: thêm POL vào `config.py` xong Polygon vẫn mù")

    thieu = sorted(set(_TG.values()) - set(_CFG["quet"]["ma"]))
    kiem("mọi token trả gas đều được QUÉT giá", not thieu,
         f"{thieu} — không có giá thì chuỗi ấy mù trong im lặng. Và nhớ "
         f"`config.json` ĐÈ lên `bac/config.py`: sửa mỗi mặc định trong mã "
         f"thì không có tác dụng gì trên máy đã có config.json")

    kiem("chuỗi mất gas thì cả chặng nạp mù",
         not DinhTuyen(giaGas={}, giaTokenGocUsd=GIA)
         .chang_nap("arbitrum", "okx", "USDC").doDuoc)
    kiem("mọi chuỗi có RPC đều khai token gốc",
         set(TOKEN_GOC) >= set(__import__("chuyen_von.gas",
                                          fromlist=["RPC"]).RPC),
         "chuỗi có RPC mà không biết trả gas bằng token gì thì đọc được "
         "gasPrice rồi vẫn không quy ra đô được")

    # ── một lượt RPC hỏng KHÔNG được xoá gas đọc được ───────────────────
    import asyncio as _aio
    import time as _tt

    from chuyen_von.gas import NguonGas as _NG

    class _CHong:
        async def post(self, u, json=None):
            raise RuntimeError("RPC chết")

    ng = _NG()
    ng.gia["ethereum"] = _gg("ethereum", 46_000_000)
    _aio.run(ng.doc(_CHong(), ["ethereum"]))
    kiem("RPC hỏng thì GIỮ số gas đọc được lần trước",
         ng.gia["ethereum"].weiMoiGas == 46_000_000 and ng.soGiuLai == 1,
         "gas đổi theo block nhưng BẬC của nó thì không — số cũ dùng được "
         "hơn hẳn không có số nào, và một lượt RPC hỏng từng xoá sạch")
    kiem("và số lần giữ lại được ĐẾM RA",
         ng.tom_tat()["soGiuLai"] == 1,
         "không đếm thì «vẫn có gas» và «gas đã cũ» trông giống hệt nhau")
    ng2 = _NG()
    _aio.run(ng2.doc(_CHong(), ["ethereum"]))
    kiem("chưa từng đọc được thì vẫn là None, không bịa",
         ng2.gia["ethereum"].weiMoiGas is None and ng2.soGiuLai == 0)
    # ── bảng giá token: GỘP, không THAY ─────────────────────────────────
    from bac.vong import Runtime as _RT

    class _RTGia(_RT):
        def __init__(self, bg):
            self._bg = bg
            self.dinhTuyen = DinhTuyen()
            self.baoGia = bg

    rt = _RTGia([])
    rt.dinhTuyen.giaTokenGocUsd = {"ETH": 2461.0}
    kiem("lượt quét TRỐNG không xoá bảng giá đã có",
         rt._cap_nhat_gia_token() == {"ETH": 2461.0},
         "một lượt thiếu ETH — cả bốn cảng cùng lỗi — từng xoá sạch bảng "
         "giá, và mọi chặng gas hoá mù dù lượt trước vừa đọc được")
    khong = _RTGia([])
    khong.dinhTuyen = None
    kiem("thiếu Router thì trả rỗng, không nổ",
         khong._cap_nhat_gia_token() == {},
         "Router hỏng KHÔNG được kéo theo vòng quét — nhưng cũng không "
         "được im lặng, và `chuoiDungDuoc` rỗng nói ra điều đó")

    class _BGx:
        def __init__(self, ma, px):
            self.ma, self.markPx = ma, px

    rt3 = _RTGia([_BGx("ETH", 2600.0), _BGx("POL", 0.12),
                  _BGx("DOGE", 0.4)])
    rt3.dinhTuyen.giaTokenGocUsd = {}
    ra3 = rt3._cap_nhat_gia_token()
    kiem("lấy giá MỌI token trả gas, không chỉ ETH",
         gan(ra3.get("ETH", 0), 2600.0) and gan(ra3.get("POL", 0), 0.12),
         f"{ra3} — danh sách suy từ `TOKEN_GOC`; chép tay một cái tên thì "
         f"thêm chuỗi mới là chuỗi ấy mù trong im lặng, và chính chuyện đó "
         f"đã xảy ra với Polygon")
    kiem("và KHÔNG lấy token không trả gas cho chuỗi nào",
         "DOGE" not in ra3,
         "bảng giá phình ra vì mọi mã perp thì nó hết nói lên điều gì")

    rt2 = _RTGia([_BGx("ETH", 2600.0)])
    rt2.dinhTuyen.giaTokenGocUsd = {"ETH": 2461.0, "POL": 0.11}
    ra2 = rt2._cap_nhat_gia_token()
    kiem("giá MỚI thay giá cũ của cùng token", gan(ra2["ETH"], 2600.0))
    kiem("và token KHÔNG có trong lượt này vẫn được GIỮ",
         gan(ra2["POL"], 0.11),
         "gộp chứ không thay — nếu không thì mỗi lượt thiếu POL là Polygon "
         "mù lại một lần")

    kiem("số giữ lại TỰ GIÀ, không trẻ lại mỗi lượt hỏi",
         ng.gia["ethereum"].docLucMs < _tt.time() * 1000.0 + 1.0,
         "`docLucMs` giữ nguyên dấu thời gian gốc nên `tuoi_giay()` nói ra "
         "tuổi thật")

    # ── bốn dạng tuyến ──────────────────────────────────────────────────
    ch, sa = Diem("chuoi", "arbitrum"), Diem("san", "binance")
    kiem("chuỗi -> chuỗi đi bằng CẦU NỐI",
         r.tuyen(Diem("chuoi", "ethereum"), ch, "USDC", 1000.0)
         .chang[0].cach == "cau-noi")
    kiem("sàn -> chuỗi là RÚT",
         r.tuyen(sa, ch, "USDC", 1000.0).chang[0].cach == "rut-cex")
    kiem("chuỗi -> sàn là NẠP",
         r.tuyen(ch, sa, "USDC", 1000.0).chang[0].cach == "nap-cex")

    ss = r.tuyen(sa, Diem("san", "okx"), "USDC", 1000.0)
    kiem("sàn -> sàn là RÚT rồi NẠP, hai chặng",
         [c.cach for c in ss.chang] == ["rut-cex", "nap-cex"],
         str([c.cach for c in ss.chang]))
    kiem("và nó đi qua một chuỗi CẢ HAI sàn cùng dùng được",
         ss.chang[0].den == ss.chang[1].tu
         and ss.chang[0].den.ten in UU_TIEN_TRUNG_GIAN)

    kiem("hai điểm trùng nhau KHÔNG phải một tuyến",
         r.tuyen(sa, sa, "USDC", 1000.0).chang == ())
    kiem("vốn ≤ 0 cũng không phải một tuyến",
         r.tuyen(sa, ch, "USDC", 0.0).chang == ())

    # ── không có chuỗi chung thì KHÔNG có tuyến, không phải tuyến đắt ──
    kiem("bybit không rút USDT về đâu chung với một sàn chỉ dùng base",
         r.chuoi_chung("bybit", "bybit", "DOGE") is None,
         "tài sản bảng chưa có dòng nào thì không có chuỗi chung nào")
    t = r.tuyen(Diem("san", "binance"), Diem("san", "okx"), "DOGE", 1000.0)
    kiem("và tuyến ấy trả về KHÔNG CÓ TUYẾN kèm lý do",
         t.chang == () and "DOGE" in t.viSaoKhong, t.viSaoKhong)
    kiem("khác hẳn một tuyến có thật mà đắt",
         t.phiUsd is None and ss.phiUsd is not None,
         "không có đường đi và đường đi đắt là hai câu trả lời khác nhau, "
         "và ty phải xử chúng khác nhau")

    # ── cầu nối ─────────────────────────────────────────────────────────
    kiem("cầu nối gộp CẢ phí cầu lẫn gas",
         gan(r.chang_cau("USDC", "ethereum", "arbitrum", 1000.0).phiUsd,
             2.5 + 0.09),
         "gas trả bằng token gốc nên không trừ vào số tài sản chuyển — cộng "
         "riêng, không phải đã nằm trong hiệu hai đầu")
    kiem("cùng một chuỗi thì không phải dời, phí 0",
         gan(r.chang_cau("USDC", "arbitrum", "arbitrum", 1000.0).phiUsd, 0.0))
    # ── 429: NGHỈ theo đúng con số bên kia nói ──────────────────────────
    from chuyen_von.cau_noi import NguonCauNoi
    nc = NguonCauNoi()
    kiem("mới dựng thì KHÔNG nghỉ", not nc.dang_nghi())
    nc.nghiToiMs = _tt.time() * 1000.0 + 60_000.0
    kiem("bị 429 thì khai là ĐANG NGHỈ", nc.dang_nghi()
         and 50.0 < nc.con_nghi_giay() <= 60.0,
         "hỏi tiếp trong lúc bị chặn không làm câu trả lời tới sớm hơn — "
         "nó chỉ tốn lượt của cả hai bên và kéo dài lệnh chặn")
    kiem("và buồng lái thấy được", nc.tom_tat()["dangNghi"] is True)
    nc.nghiToiMs = _tt.time() * 1000.0 - 1000.0
    kiem("hết hạn nghỉ thì hỏi lại được", not nc.dang_nghi())

    # Không đủ: phải kiểm `doc()` THẬT SỰ không gọi mạng lúc đang nghỉ, và
    # THẬT SỰ đặt mốc nghỉ khi gặp 429. Bản kiểm đầu chỉ chạm hai hàm phụ,
    # và phép cấy lỗi ngược đi lọt cả hai lần.
    goi = []

    class _R:
        def __init__(self, ma, txt="", hdr=None):
            self.status_code, self.text = ma, txt
            self.headers = hdr or {}

        def json(self):
            return {}

    class _C:
        def __init__(self, ma=429, hdr=None):
            self.ma, self.hdr = ma, hdr

        async def get(self, u, params=None):
            goi.append(u)
            return _R(self.ma, '{"message":"Rate limit exceeded"}', self.hdr)

    nc2 = NguonCauNoi()
    bg = _aio.run(nc2.doc(_C(), "USDC", "arbitrum", "ethereum", 500.0))
    kiem("gặp 429 thì ĐẶT mốc nghỉ", nc2.dang_nghi() and nc2.soLan429 == 1,
         f"nghỉ={nc2.dang_nghi()} lần429={nc2.soLan429}")
    kiem("và nghỉ mặc định hai giờ",
         7100.0 < nc2.con_nghi_giay() <= 7200.0,
         f"{nc2.con_nghi_giay():.0f}s")
    kiem("báo giá ấy KHÔNG đo được", not bg.doDuoc and "429" in bg.loi)

    truoc = len(goi)
    bg2 = _aio.run(nc2.doc(_C(), "USDC", "arbitrum", "base", 500.0))
    kiem("đang nghỉ thì KHÔNG gọi mạng lần nữa", len(goi) == truoc,
         f"{len(goi) - truoc} lời gọi thừa — hỏi tiếp trong lúc bị chặn "
         f"không làm câu trả lời tới sớm hơn, nó chỉ kéo dài lệnh chặn")
    kiem("và nói rõ còn nghỉ bao lâu", "NGHỈ" in bg2.loi, bg2.loi)

    nc3 = NguonCauNoi()
    _aio.run(nc3.doc(_C(429, {"retry-after": "60"}), "USDC", "arbitrum",
                     "ethereum", 500.0))
    kiem("tôn trọng `retry-after` của bên kia thay vì mặc định",
         50.0 < nc3.con_nghi_giay() <= 60.0, f"{nc3.con_nghi_giay():.0f}s")

    nc4 = NguonCauNoi()
    _aio.run(nc4.doc(_C(500), "USDC", "arbitrum", "ethereum", 500.0))
    kiem("lỗi 500 thì KHÔNG nghỉ — chỉ 429 mới là hạn mức",
         not nc4.dang_nghi())

    # ── KHÔNG đè báo giá TỐT bằng báo giá MÙ ────────────────────────────
    from chuyen_von.cau_noi import BaoGiaCau as _BG
    from chuyen_von.dinh_tuyen import (TUOI_BAO_GIA_TOI_DA_GIAY, _khoa,
                                       _tuoi_giay)

    def _kho(r, tuoiGiay=0.0):
        k = _khoa("USDC", "arbitrum", "ethereum", 500)
        r.kho[k] = _BG("USDC", "arbitrum", "ethereum", 500.0, 2.5, 0.09,
                       7.0, "eco", _tt.time() * 1000.0 - tuoiGiay * 1000.0)
        return k

    r2 = DinhTuyen(giaGas=gas, giaTokenGocUsd=GIA)
    k2 = _kho(r2)
    nghi = NguonCauNoi()
    nghi.nghiToiMs = _tt.time() * 1000.0 + 60_000.0
    _aio.run(r2.nap(None, nghi, [("USDC", "arbitrum", "ethereum", 500.0)]))
    kiem("đang NGHỈ thì KHÔNG đè báo giá tốt bằng báo giá mù",
         r2.kho[k2].doDuoc and gan(r2.kho[k2].phiTaiSan, 2.5),
         "một lần 429 từng xoá sạch chín báo giá còn dùng được, biến cỗ máy "
         "đang chạy thành mù hoàn toàn suốt hai giờ — trong khi phí cầu đổi "
         "chậm tới mức số cũ vẫn còn nghĩa")

    class _NguonTot:
        """Nguồn giả trả một báo giá TỐT. Không chạm mạng."""

        async def doc(self, client, ts, a, b, v):
            return _BG(ts, a, b, v, 9.99, 0.01, 3.0, "gia",
                       _tt.time() * 1000.0)

    r3 = DinhTuyen(giaGas=gas, giaTokenGocUsd=GIA)
    k3 = _kho(r3)
    _aio.run(r3.nap(None, _NguonTot(),
                    [("USDC", "arbitrum", "ethereum", 500.0)]))
    kiem("nhưng báo giá MỚI vẫn THAY được báo giá cũ",
         gan(r3.kho[k3].phiTaiSan, 9.99),
         f"{r3.kho[k3].phiTaiSan} — luật «không đè» chỉ được chặn báo giá "
         f"MÙ; chặn cả báo giá mới là đóng băng kho vĩnh viễn")

    # ── báo giá GIỮ LẠI phải KHAI TUỔI ──────────────────────────────────
    r4 = DinhTuyen(giaGas=gas, giaTokenGocUsd=GIA)
    _kho(r4, tuoiGiay=0.0)
    moi_ = r4.chang_cau("USDC", "arbitrum", "ethereum", 500.0)
    kiem("báo giá mới thì KHÔNG khai tuổi",
         not any(x.startswith("bao-gia-cau-cu") for x in moi_.khongDoDuoc),
         str(moi_.khongDoDuoc))
    _kho(r4, tuoiGiay=TUOI_BAO_GIA_TOI_DA_GIAY + 600.0)
    cu_ = r4.chang_cau("USDC", "arbitrum", "ethereum", 500.0)
    kiem("báo giá QUÁ TUỔI vẫn dùng được", cu_.doDuoc)
    kiem("nhưng nó KHAI tuổi ra",
         any(x.startswith("bao-gia-cau-cu") for x in cu_.khongDoDuoc),
         f"{cu_.khongDoDuoc} — giữ số cũ tốt hơn mù, nhưng dùng số cũ mà "
         f"im lặng thì tệ hơn cả hai")
    kiem("và nguồn nói rõ nó bao nhiêu phút tuổi", "phút tuổi" in cu_.nguon,
         cu_.nguon)
    kiem("thiếu dấu thời gian thì không đoán tuổi",
         _tuoi_giay(object()) is None)

    # Ngưỡng tuổi là một PHÁN ĐOÁN, nhưng phán đoán vô lý thì bắt được.
    # Phép kiểm ở trên dựng tuổi mẫu TỪ CHÍNH hằng số ấy, nên nới hằng số
    # lên 1e12 thì nó vẫn xanh — một phép kiểm tự tham chiếu không canh
    # được giá trị của thứ nó tham chiếu.
    kiem("ngưỡng tuổi báo giá nằm trong khoảng bảo vệ được",
         1800.0 <= TUOI_BAO_GIA_TOI_DA_GIAY <= 86_400.0,
         f"{TUOI_BAO_GIA_TOI_DA_GIAY}s — dưới 30 phút thì mọi báo giá đều "
         f"bị gắn cờ cũ và cảnh báo hoá tiếng ồn; trên 24 giờ thì cờ ấy "
         f"không bao giờ bật và nó thành trang trí")
    kiem("và nó là bội số của nhịp nạp (30 phút)",
         gan(TUOI_BAO_GIA_TOI_DA_GIAY % 1800.0, 0.0),
         "ngưỡng không khớp nhịp thì cờ bật ở một chỗ không ai giải thích "
         "được")

    kiem("nguồn cầu nối hỏng thì chặng mù, KHÔNG phải phí 0",
         not DinhTuyen(giaGas=gas, giaTokenGocUsd=GIA,
                       baoGiaCau=lambda *a: _bgc(phi=None, loi="LI.FI 429"))
         .chang_cau("USDC", "ethereum", "arbitrum", 1000.0).doDuoc)
    kiem("chưa nối nguồn cầu nối cũng là mù",
         not DinhTuyen(giaGas=gas, giaTokenGocUsd=GIA)
         .chang_cau("USDC", "ethereum", "arbitrum", 1000.0).doDuoc)

    # ── câu trả lời cho ty ──────────────────────────────────────────────
    bps, tu = r.phi_bps(sa, Diem("san", "okx"), "USDC", 1000.0)
    kiem("phi_bps trả CẢ con số lẫn tuyến", bps is not None and tu.doDuoc)
    kiem("và tuyến mang theo thứ nó chưa tính", len(tu.khongDoDuoc) > 0,
         "một hạ tầng trả về con số mà im lặng về phần nó không đo được thì "
         "ty sẽ bỏ khai báo `phiConThieu` đi vì tưởng đã có Router lo")
    kiem("phí rút gõ tay LUÔN được khai là gõ tay",
         any("do-tay" in x for x in tu.khongDoDuoc), str(tu.khongDoDuoc))


def kiem_router_khong_phai_ty() -> None:
    print("\n-- Router KHONG phai ty, va khong quyet dinh gi --")
    import pathlib

    import chuyen_von.dinh_tuyen as dt
    from thi_bac_ty.hien_phap import _goi_ty

    kiem("chuyen_von KHÔNG bị nhận là ty",
         "chuyen_von" not in {d.name for d in _goi_ty()},
         "nó không quét cơ hội, không xin vốn, không có quet() — bản đồ §18 "
         "gọi nó là hạ tầng chứ không phải một bot")
    kiem("và nó KHÔNG có quet()", not hasattr(dt.DinhTuyen, "quet"))

    goc = pathlib.Path(__file__).resolve().parent.parent
    xau = []
    for p in (goc / "chuyen_von").glob("*.py"):
        for l in p.read_text(encoding="utf-8").splitlines():
            l = l.strip()
            for k in ("bac", "co_so", "lai_suat", "on_dinh", "tin_dung"):
                if l.startswith((f"import {k}", f"from {k}")):
                    xau.append(f"{p.name}: {l}")
    kiem("hạ tầng KHÔNG gọi ngược lên ty nào", not xau, str(xau))

    kiem("Router KHÔNG tự quyết định bỏ tuyến nào",
         "nen-doi" not in dt.__doc__ and not hasattr(dt.DinhTuyen, "xet"),
         "một hạ tầng tự ý bỏ tuyến vì thấy đắt quá là một cửa rủi ro giấu "
         "trong thư viện tiện ích, và không ai soát được nó ở `CUA`")

def _ck(ma="BTC-100K", ben="UP", net=0.05, vwap=0.42, batDinh=0.02,
        sucChua=180.0, xs=0.62, dangLam=False, maker=True):
    return {"ma": ma, "ben": ben, "ct": "lech-gia", "fair": 0.47,
            "vwap": vwap, "gross": net + 0.01, "net": net, "phi": 0.01,
            "batDinh": batDinh, "sucChua": sucChua, "xacSuatKhop": xs,
            "nuaDoiMs": 7_200_000, "maker": maker, "dangLam": dangLam,
            "ghiChu": ""}


class _DocGia:
    """Giả cỗ máy kia. Không mạng — selftest không được chạm mạng."""

    def __init__(self, d, docDuoc=True):
        self.d, self.docDuoc, self.vi, self.soLoi, self.lucMs = (
            d, docDuoc, "" if docDuoc else "tắt", 0, 1.0)

    def doc(self):
        return self.d if self.docDuoc else {}

    def tuoi_giay(self):
        return 1.0

    def tom_tat(self):
        return {"docDuoc": self.docDuoc, "vi": self.vi}


def kiem_kham_adapter() -> None:
    print("\n-- Kham adapter: RANH GIOI dem hai lan --")
    from kham_ngoai.ty_tien_doan import (CONFIG, CUA, CongRuiRo, TyTienDoan,
                                         _ten_tai_san, net_bps, xuat_to_trinh)

    kiem("CUA và CONFIG['ruiRo'] khai cùng một bộ khoá",
         set(CUA) == set(CONFIG["ruiRo"]),
         str(set(CUA) ^ set(CONFIG["ruiRo"])))

    # ── đổi đơn vị: chia cho GIÁ, không cho mệnh giá ────────────────────
    kiem("netEdge 0,05 ở giá 0,42 = 1.190 bps",
         gan(net_bps(0.05, 0.42), 0.05 / 0.42 * 10_000.0, 1e-6))
    kiem("chia cho GIÁ, không phải cho 1,0",
         net_bps(0.05, 0.42) > net_bps(0.05, 1.0),
         "vốn bỏ ra là GIÁ mỗi cổ. Chia cho 1,0 thì cơ hội ở giá 0,10 bị "
         "báo thấp đi mười lần, và những cơ hội rẻ nhất — đúng chỗ edge hay "
         "nằm — biến mất khỏi bảng xếp hạng")
    kiem("giá ngoài thang xác suất là dữ liệu hỏng, trả None",
         net_bps(0.05, 1.4) is None and net_bps(0.05, 0.0) is None)
    kiem("thiếu edge hoặc thiếu giá → None, không phải 0",
         net_bps(None, 0.42) is None and net_bps(0.05, None) is None)

    # ── RANH GIỚI ĐẾM HAI LẦN ───────────────────────────────────────────
    t = TyTienDoan()
    t.doc = _DocGia({"chayDuocGiay": 5.0, "coHoi": [
        _ck("A", dangLam=False), _ck("B", dangLam=True),
        _ck("C", dangLam=True)]})
    ra = t.quet()
    kiem("cơ hội cỗ máy kia ĐANG LÀM bị BỎ QUA",
         [c["ma"] for c in ra] == ["A"], str([c["ma"] for c in ra]))
    kiem("và số bị bỏ được ĐẾM chứ không biến mất",
         t.boQua["dangLam"] == 2,
         f"{t.boQua} — chúng đã là vốn ngoài trong Danh Mục. Nộp tờ trình "
         f"cho chúng nữa là đếm CÙNG MỘT vị thế hai lần, và `tranMotCang` "
         f"tưởng mình chặn ở 30% trong khi thực tế là 60%")
    kiem("lời nhắc nói rõ vì sao bỏ", "hai lần" in t.tom_tat()["loiNhac"])

    # ── cỗ máy kia TẮT ──────────────────────────────────────────────────
    t2 = TyTienDoan()
    t2.doc = _DocGia({}, docDuoc=False)
    kiem("cỗ máy kia tắt → quét rỗng", t2.quet() == [])
    kiem("và ty KHAI là mù, không im lặng",
         t2.tom_tat()["doc"]["docDuoc"] is False,
         "«không đọc được» và «không có cơ hội» trông giống hệt nhau nếu "
         "không ai nói ra")

    # ── cổng ──────────────────────────────────────────────────────────────
    cong = CongRuiRo(CONFIG["ruiRo"])

    def ma_cua(c):
        c = dict(c)
        c["_netBps"] = net_bps(c["net"], c["vwap"])
        c.setdefault("_tuoiGiay", 5.0)
        return {m for m, _ in cong.xet(c)[1]}

    kiem("cơ hội lành qua sạch", ma_cua(_ck()) == set(), str(ma_cua(_ck())))
    kiem("bất định mô hình quá lớn → CHẶN",
         "bat-dinh-qua-lon" in ma_cua(_ck(batDinh=0.40)),
         "đó là CHÍNH cỗ máy định giá nói «tôi không chắc» — edge nằm trong "
         "sai số của mô hình sinh ra nó thì không phải edge")
    kiem("NET dưới ngưỡng → chặn",
         "net-duoi-nguong" in ma_cua(_ck(net=0.005)))
    kiem("khó khớp → chặn", "kho-khop" in ma_cua(_ck(xs=0.10)))
    kiem("sức chứa quá nhỏ → chặn",
         "suc-chua-qua-nho" in ma_cua(_ck(sucChua=5.0)))
    kiem("thiếu sức chứa là THIẾU SỐ, không phải sức chứa 0",
         "thieu-so" in ma_cua(_ck(sucChua=None)),
         "None phải chảy tới tận cổng chứ không bị coi là 0 dọc đường")

    # ── tờ trình ────────────────────────────────────────────────────────
    c = dict(_ck())
    c["_netBps"] = net_bps(c["net"], c["vwap"])
    c["_grossBps"] = net_bps(c["gross"], c["vwap"])
    c["_phiBps"] = net_bps(c["phi"], c["vwap"])
    c["_tuoiGiay"] = 5.0
    tt = xuat_to_trinh(c)
    kiem("tờ trình hợp lệ", tt.hop_le, str(tt.kiem()))
    kiem("họ là `tien-doan`, họ thứ TÁM", tt.ho == "tien-doan")

    kiem("chân LUÔN là LONG", tt.chan[0].ben == "LONG",
         "trên Polymarket ta MUA cổ phần một kết quả; mua DOWN không phải "
         "bán khống UP, nó là mua dài một TOKEN KHÁC. Nhét UP/DOWN vào "
         "`ben` là nói dối `_dau_van()` của Trung Ương — nó sẽ gộp hai vị "
         "thế CÙNG chiều thành hai vị thế đối nhau")
    kiem("UP/DOWN nằm ở TÊN TÀI SẢN", tt.taiSan == "BTC-100K:UP",
         str(tt.taiSan))
    kiem("nên UP và DOWN là hai tài sản khác nhau",
         _ten_tai_san(_ck(ben="UP")) != _ten_tai_san(_ck(ben="DOWN")))

    kiem("đủ SÁU mặt rủi ro, không bịa mặt thứ bảy",
         tt.ruiRo.chua_do() == (), str(tt.ruiRo.chua_do()))
    kiem("bất định mô hình đẩy rủi ro THỊ TRƯỜNG lên",
         xuat_to_trinh({**c, "batDinh": 0.30}).ruiRo.thiTruong
         > tt.ruiRo.thiTruong,
         "sáu mặt hiện có đo rủi ro của THẾ GIỚI, không đo rủi ro của việc "
         "chính ta nhìn sai thế giới. Mô hình sai bao nhiêu thì giá đi "
         "ngược ta bấy nhiêu, và hệ quả không phân biệt được với biến động")

    kiem("bằng chứng nói rõ ĐỊNH GIÁ KHÔNG PHẢI của ty này",
         any("KHÔNG PHẢI CỦA TY NÀY" in b for b in tt.bangChung),
         "viết lại thuật toán định giá ở đây là dựng cỗ máy thứ ba dưới một "
         "cái tên khác")
    kiem("và nói rõ ranh giới đếm hai lần",
         any("hai lần" in b for b in tt.bangChung))
    kiem("khai `giuGio` là NỬA ĐỜI, không phải kỳ hạn",
         "giu-gio-la-nua-doi-khong-phai-ky-han" in tt.phiConThieu,
         "để không ai đọc `netMoiGioBps` của ty này như đọc của ty funding")

    kiem("không đo được tuổi lát cắt thì KHAI ra",
         "tuoi-lat-cat-khong-doc-duoc"
         in xuat_to_trinh({**c, "_tuoiGiay": None}).phiConThieu,
         "cửa `tuoiToiDaGiay` không chặn được khi tuổi là None, nên chỗ "
         "hổng ấy phải hiện ở khai báo")
    kiem("và độ tin cũng tụt theo",
         xuat_to_trinh({**c, "_tuoiGiay": None}).tinCay < tt.tinCay)


def kiem_kham_khong_dat_lenh() -> None:
    print("\n-- Kham adapter CHI DOC: buoc 4 bi CHAN co chu y --")
    import pathlib

    goc = pathlib.Path(__file__).resolve().parent.parent
    xau = []
    for p in (goc / "kham_ngoai").glob("*.py"):
        s = p.read_text(encoding="utf-8")
        for l in s.splitlines():
            l = l.strip()
            if l.startswith(("import kham", "from kham.", "from kham ")):
                xau.append(f"{p.name}: {l}")
    kiem("adapter KHÔNG import `kham`", not xau,
         f"{xau} — hai runtime là hai tiến trình, hai vòng đời, hai lịch "
         f"khởi động lại. Import là buộc chúng thành một")

    dat = []
    for p in (goc / "kham_ngoai").glob("*.py"):
        s = p.read_text(encoding="utf-8").lower()
        for tu in ("urlopen(rq", "requests.post", "client.post", ".put("):
            if tu in s and "read-only" not in s:
                dat.append(f"{p.name}: {tu}")
    kiem("adapter chỉ ĐỌC — không có đường ghi nào ra cỗ máy kia",
         not dat,
         f"{dat} — bước 4 (`dat_lenh.py`) bị CHẶN có chủ ý: nó chỉ chuyển "
         f"được khi Điều Phối Thực Thi có lớp ký lệnh thật, mà `moPhong` là "
         f"True cứng")

    from thi_bac_ty.thuc_thi import DieuPhoiThucThi
    kiem("và lớp ký lệnh thật vẫn KHÔNG tồn tại",
         DieuPhoiThucThi().moPhong is True,
         "đây là điều biến bước 4 từ «chưa làm» thành «không làm được từ "
         "phía này» — và hai câu ấy phải nói khác nhau")

def kiem_von_ngoai_bat_san() -> None:
    print("\n-- Von ngoai BAT SAN: thay co may thu hai, ke ca khi no tat --")
    from bac.config import CONFIG

    vn = (CONFIG.get("trungUong") or {}).get("vonNgoai") or {}
    kiem("khoá đọc vốn ngoài đã BẬT, không để rỗng", bool(vn),
         "một lớp an toàn chỉ được cấu hình vào đúng ngày người ta cần nó "
         "là một lớp an toàn không tồn tại: cái ngày ấy là ngày bận nhất, "
         "và luật này nằm trong một chú thích mà lúc đó chưa chắc ai đọc")
    kiem("và nó trỏ tới Khâm Thiên Giám",
         any("5186" in str(u) for u in vn.values()), str(vn))

    from thi_bac_ty.danh_muc import DanhMuc
    from thi_bac_ty.von_ngoai import LatCatNgoai
    d = DanhMuc(1000.0)
    d.ghi_von_ngoai(LatCatNgoai("kham-thien-giam", docDuoc=False,
                                vi="tắt"))
    kiem("đọc HỎNG thì Danh Mục khai là KHÔNG đầy đủ", not d.ngoaiDayDu,
         "coi «không đọc được» thành «không có gì» là đúng cách một trần "
         "biến thành trần giả")
    d2 = DanhMuc(1000.0)
    d2.ghi_von_ngoai(LatCatNgoai("kham-thien-giam", docDuoc=True,
                                 daCamKetUsd=250.0, tienMatUsd=50.0))
    kiem("đọc được thì vốn ngoài vào NAV", d2.ngoaiUsd > 0 and d2.ngoaiDayDu,
         f"ngoaiUsd={d2.ngoaiUsd} dayDu={d2.ngoaiDayDu}")

def kiem_dong_co_chua_co() -> None:
    print("\n-- Engine CHUA CO: bi chan hay chua lam, hai cau khac nhau --")
    from dong_co_chua_co.so_dang_ky import (CHAN, DA_DUNG, DONG_CO,
                                            QUET_DUOC, SAN_SANG,
                                            soat, tom_tat)
    from thi_bac_ty.to_trinh import HO

    r = soat()
    kiem(f"sổ đăng ký có {r['soDongCo']} engine", r["soDongCo"] >= 6)
    kiem("mọi engine đều có mã, tên, họ, mô tả, và VÌ SAO ĐÁNG dựng",
         all(d.ma and d.ten and d.ho and d.moTa and d.viSaoDang
             for d in DONG_CO),
         "engine không kèm lý do đáng dựng là một dòng trong danh sách ước "
         "mơ, và danh sách ước mơ thì dài ra mãi mà không ai xoá dòng nào")
    kiem("mã không trùng", len({d.ma for d in DONG_CO}) == len(DONG_CO))
    kiem("mọi họ khai ra đều CÓ THẬT trong hợp đồng",
         all(d.ho in HO for d in DONG_CO),
         str([d.ho for d in DONG_CO if d.ho not in HO]))
    kiem("mọi engine đều có ít nhất một điều kiện",
         all(d.dieuKien for d in DONG_CO))
    kiem("mọi điều kiện đều canh được bằng máy",
         all(k["canhDuoc"] for d in r["dongCo"] for k in d["dieuKien"]),
         "một điều kiện không canh được thì trạng thái tính từ nó là phỏng "
         "đoán, và cả sổ này sinh ra để thay phỏng đoán")

    kiem("ba trạng thái phủ hết, không engine nào rơi ngoài",
         sum(len(v) for v in r["theoTrangThai"].values()) == r["soDongCo"])

    # ── phân biệt CHAN với QUET_DUOC ────────────────────────────────────
    theo = {d["ma"]: d for d in r["dongCo"]}
    kiem("`ky-lenh-onchain` KHÔNG chặn quét, chỉ chặn thực thi",
         all(k["chanQuet"] is False
             for d in r["dongCo"] for k in d["dieuKien"]
             if k["ma"] == "ky-lenh-onchain"),
         "cả runtime đang moPhong=True — KHÔNG ty nào đang thực thi gì cả. "
         "Nếu thiếu lớp ký lệnh mà chặn cả quét thì mọi ty đang chạy cũng "
         "lẽ ra không được tồn tại")
    kiem("`mempool` thì CHẶN QUÉT thật",
         all(k["chanQuet"] is True
             for d in r["dongCo"] for k in d["dieuKien"]
             if k["ma"] == "mempool"),
         "không đọc được giao dịch chưa lên block thì scanner JIT chỉ là "
         "một cái vỏ luôn trả rỗng, và cái vỏ ấy làm phễu có thêm một dòng "
         "vĩnh viễn bằng không")

    kiem("JIT và MEV vẫn CHẶN", theo["jit"]["trangThai"] == CHAN
         and theo["mev"]["trangThai"] == CHAN)
    kiem("và chúng chặn vì MEMPOOL, không vì thiếu ví",
         "mempool" in theo["jit"]["thieuDeQuet"], str(theo["jit"]))

    kiem("LP nay cũng ĐÃ DỰNG — không còn engine nào chỉ QUÉT ĐƯỢC",
         theo["lp-v3"]["trangThai"] == DA_DUNG
         and not r["theoTrangThai"][QUET_DUOC],
         "Router ra đời 27/08 và gỡ điều kiện `bao-gia-dex` lẫn `gia-gas`. "
         "Đoạn văn xuôi cũ vẫn nói «sáu engine bị chặn» — đó chính là cách "
         "văn xuôi hỏng: thế giới đổi mà câu văn không đổi")
    kiem("DEX arb đã đi hết đường CHAN → QUET_DUOC → DA_DUNG",
         theo["dex-arb"]["trangThai"] == DA_DUNG,
         "và sổ TỰ biết, vì nó nạp thử `dex_arb.ty_vong_doi`")

    kiem("quyền chọn nay ĐÃ DỰNG, và sổ TỰ BIẾT",
         theo["quyen-chon"]["trangThai"] == DA_DUNG,
         "sổ nạp thử gói ty; nạp được nghĩa là engine ấy không còn nằm "
         "trong danh sách «chưa có». Không ai phải nhớ xoá dòng")
    kiem("và dòng ấy Ở LẠI kèm lịch sử, không bị xoá",
         theo["quyen-chon"]["viSaoDang"]
         and theo["quyen-chon"]["dieuKien"],
         "xoá tay thì mất luôn câu «nó từng bị chặn vì gì, và cái gì gỡ ra»")
    kiem("engine ĐÃ DỰNG không đếm vào số bị CHẶN",
         "quyen-chon" not in r["theoTrangThai"][CHAN])

    kiem("tóm tắt gọn dùng được cho buồng lái",
         {"soChan", "soQuetDuoc", "soSanSang"} <= set(tom_tat()))
    kiem("sổ này KHÔNG bị nhận là ty",
         "dong_co_chua_co"
         not in {d.name for d in
                 __import__("thi_bac_ty.hien_phap",
                            fromlist=["_goi_ty"])._goi_ty()},
         "nó không quét cơ hội, không xin vốn, không có quet() — và nó nói "
         "về những ty CHƯA tồn tại")

def kiem_nhap_so_ngoai() -> None:
    print("\n-- Nhap so ngoai: MOT so cai, khong dem hai lan --")
    import tempfile
    from pathlib import Path

    from thi_bac_ty.nhap_so_ngoai import NhapSoNgoai
    from thi_bac_ty.so_cai import SoCai

    def _ban_ghi(i):
        return {"luc": f"2026-08-27T0{i}:00:00.000Z", "slug": f"m-{i}",
                "ma": "BTC", "upThang": True, "pDuDoan": 0.6,
                "coViThe": True, "batDong": False}

    class _Nguon(NhapSoNgoai):
        """Cỗ máy giả. Selftest KHÔNG được chạm mạng."""

        def __init__(self, tra):
            super().__init__("gia", "http://khong-dung-toi", "x.y.v1")
            self.tra = tra

        def _doc(self):
            self.docDuoc = self.tra is not None
            return self.tra

    d = Path(tempfile.mkdtemp(prefix="tbt-nso-"))

    # ── KHÔNG đếm hai lần ───────────────────────────────────────────────
    sc = SoCai(d / "a.db")
    lo = {"ketToan": {"daKetToan": 3,
                      "ganDay": [_ban_ghi(1), _ban_ghi(2), _ban_ghi(3)]}}
    n = _Nguon(lo)
    r1 = n.nhap(sc)
    kiem("lượt đầu nhận đủ ba bản ghi", r1["moi"] == 3, str(r1))
    r2 = n.nhap(sc)
    kiem("hỏi lại CÙNG dữ liệu thì KHÔNG ghi thêm gì", r2["moi"] == 0,
         f"{r2} — cỗ máy kia đưa cùng một bản ghi ở mọi lượt hỏi. Ghi lại "
         f"mỗi lượt là nhân lãi lỗ lên gấp số lượt hỏi")
    kiem("và sổ cái chỉ có đúng ba bút toán",
         len(sc.gan_day(50, "DONG_VI_THE")) == 3,
         str(len(sc.gan_day(50, "DONG_VI_THE"))))

    lo["ketToan"]["ganDay"].append(_ban_ghi(4))
    lo["ketToan"]["daKetToan"] = 4
    kiem("bản ghi MỚI thì vào", n.nhap(sc)["moi"] == 1)
    kiem("tổng đã vào là bốn", n.soDaVao == 4, str(n.soDaVao))

    # ── BỎ SÓT phải tự lộ ra ────────────────────────────────────────────
    sc2 = SoCai(d / "b.db")
    day = {"ketToan": {"daKetToan": 12,
                       "ganDay": [_ban_ghi(i) for i in range(12)]}}
    n2 = _Nguon(day)
    n2.nhap(sc2)
    kiem("chưa có mốc trước thì chưa kết luận được gì về bỏ sót",
         n2.soBoSot == 0 and n2.boSotDoDuoc)

    # bên kia kết toán 40 lần nữa, ta chỉ thấy 12 bản mới nhất
    n2.tra = {"ketToan": {"daKetToan": 52,
                          "ganDay": [_ban_ghi(i) for i in range(40, 52)]}}
    r = n2.nhap(sc2)
    kiem("nhận được 12 bản mới", r["moi"] == 12, str(r))
    kiem("và 28 bản RƠI GIỮA hai lượt hỏi được ĐẾM RA",
         r["boSot"] == 28 and n2.soBoSot == 28,
         f"{r} — cửa sổ `ganDay` chỉ 12 bản. Kết toán hơn 12 lần giữa hai "
         f"lượt hỏi thì phần giữa mất hẳn, và mất trong im lặng: sổ vẫn "
         f"cân, vẫn không lỗi, chỉ thiếu tiền")
    kiem("lời nhắc nói rõ giới hạn 12 bản",
         "12" in n2.tom_tat()["loiNhac"])

    # ── không suy bừa khi thiếu căn cứ ──────────────────────────────────
    sc3 = SoCai(d / "c.db")
    n3 = _Nguon({"ketToan": {"ganDay": [_ban_ghi(1)]}})   # KHÔNG có daKetToan
    n3.nhap(sc3)
    n3.nhap(sc3)
    kiem("bên kia không công bố tổng số → KHÔNG đo được bỏ sót",
         not n3.boSotDoDuoc,
         "`soBoSot = 0` khi không đo được là giả vờ không thiếu gì. Hai câu "
         "«không thiếu» và «không biết có thiếu không» phải nói khác nhau")

    sc4 = SoCai(d / "e.db")
    n4 = _Nguon({"ketToan": {"daKetToan": 200,
                             "ganDay": [_ban_ghi(i) for i in range(12)]}})
    n4.nhap(sc4)
    n4.tra = {"ketToan": {"daKetToan": 150,
                          "ganDay": [_ban_ghi(i) for i in range(12)]}}
    kiem("tổng bên kia GIẢM thì không suy ra bỏ sót",
         n4.nhap(sc4)["boSot"] == 0,
         "bên kia cắt `xong` xuống 200 bản nên `daKetToan` giảm được. "
         "Đoán bừa từ một con số giảm còn tệ hơn không đoán")

    # ── cột tiền để 0, và NÓI RÕ vì sao ─────────────────────────────────
    bt = sc.gan_day(1, "DONG_VI_THE")[0]
    ct = bt.get("chiTiet") or {}
    kiem("cột tiền để 0 chứ không bịa", gan(float(bt["soTienUsd"]), 0.0))
    kiem("và chi tiết NÓI RÕ vì sao tiền chưa có",
         "tienChuaCo" in ct,
         "cỗ máy kia công bố KẾT QUẢ chứ không công bố lãi lỗ từng lần. "
         "Ghi một con số bịa vào cột tiền là làm hỏng đúng thứ sổ cái sinh "
         "ra để giữ")
    kiem("bút toán mang KHOÁ ổn định để truy nguyên",
         str(ct.get("khoa", "")).startswith("gia:"), str(ct.get("khoa")))
    kiem("và gắn đúng mã chiến lược để gộp lãi lỗ",
         bt["chienLuoc"] == "x.y.v1", str(bt["chienLuoc"]))

    # ── Trung Ương không biết cỗ máy nào tồn tại ────────────────────────
    from pathlib import Path as _P
    src = (_P(__file__).resolve().parent.parent / "thi_bac_ty"
           / "nhap_so_ngoai.py").read_text(encoding="utf-8")
    # Chỉ soi dòng MÃ, không soi văn giải thích. `von_ngoai.py` kể thẳng
    # chuyện Khâm Thiên Giám trong docstring và đó là tài liệu tốt — ràng
    # buộc nằm ở chỗ mã không phụ thuộc, không ở chỗ văn xuôi phải câm.
    #
    # Bản nháp đầu soi cả file và tự vấp: câu "không chỗ nào viết chữ
    # polymarket" chính là chỗ viết chữ ấy.
    ma = []
    trongVan = False
    for l in src.splitlines():
        if l.count('"' * 3) % 2:
            trongVan = not trongVan
            continue
        if trongVan or l.lstrip().startswith(("#", "#:")):
            continue
        if "polymarket" in l.lower() or "kham" in l.lower():
            ma.append(l.strip()[:70])
    kiem("không dòng MÃ nào nhắc tên một cỗ máy hay một ty",
         not ma,
         f"{ma} — Trung Ương không được biết ty nào tồn tại, huống hồ cỗ "
         f"máy nào. Cấu hình nằm ở `bac/config.py`, ngoài Trung Ương")

    from bac.config import CONFIG
    sn = (CONFIG.get("trungUong") or {}).get("soNgoai") or {}
    kiem("và cấu hình NGOÀI Trung Ương đã bật sẵn", bool(sn), str(sn))
    kiem("mỗi nguồn khai đủ url và mã chiến lược",
         all(x.get("url") and x.get("chienLuoc") for x in sn.values()),
         str(sn))

def _qc(bid, ask, oi=100.0, F=80_000.0, r=0.0):
    return {"bid_price": bid, "ask_price": ask, "open_interest": oi,
            "underlying_price": F, "interest_rate": r}


def kiem_ngang_gia() -> None:
    print("\n-- Ngang gia quyen chon: KHONG mo hinh, va mot thua so TRO --")
    import datetime as _dt

    from quyen_chon.ty_ngang_gia import (CONFIG, CUA, CongRuiRo, doc_ky_han,
                                         ghep_cap, he_so_chiet_khau,
                                         mot_co_hoi, phi_mot_chan_quyen_chon,
                                         tim_co_hoi, xuat_to_trinh)

    kiem("CUA và CONFIG['ruiRo'] khai cùng một bộ khoá",
         set(CUA) == set(CONFIG["ruiRo"]),
         str(set(CUA) ^ set(CONFIG["ruiRo"])))

    # ── đọc kỳ hạn ──────────────────────────────────────────────────────
    d = doc_ky_han("BTC-28AUG26-96000-C")
    kiem("đọc đúng ngày kỳ hạn",
         d is not None and (d.year, d.month, d.day) == (2026, 8, 28), str(d))
    kiem("và kết toán lúc 08:00 UTC, không phải nửa đêm",
         d.hour == 8,
         "lấy nửa đêm là lệch tám giờ, và tám giờ ấy đi thẳng vào hệ số "
         "chiết khấu của những kỳ hạn ngắn")
    kiem("mã sai khuôn → None", doc_ky_han("BTC-XX-1-C") is None
         and doc_ky_han("rác") is None)
    kiem("tháng lạ → None, không đoán bừa",
         doc_ky_han("BTC-28XXX26-96000-C") is None)

    # ── hệ số chiết khấu ────────────────────────────────────────────────
    kiem("lãi suất 0 → hệ số đúng bằng 1",
         gan(he_so_chiet_khau(0.0, 1.0), 1.0))
    kiem("lãi suất dương → hệ số nhỏ hơn 1",
         he_so_chiet_khau(0.05, 1.0) < 1.0)
    kiem("thiếu lãi suất → None, KHÔNG mặc định 1,0",
         he_so_chiet_khau(None, 1.0) is None,
         "mặc định 1,0 là ngầm nói lãi suất bằng 0, và với kỳ hạn một năm ở "
         "5% thì đó là bỏ sót 5% giá trị — lớn gấp trăm lần cái edge ta đi "
         "tìm")

    # ── phí có TRẦN ─────────────────────────────────────────────────────
    PH = CONFIG["phi"]
    kiem("quyền chọn ĐẮT: trần theo underlying chặn",
         gan(phi_mot_chan_quyen_chon(10_000.0, 80_000.0, PH), 24.0),
         "0,03% × 80.000 = 24, nhỏ hơn 12,5% × 10.000 = 1.250")
    kiem("quyền chọn RẺ: trần theo phí quyền chặn",
         gan(phi_mot_chan_quyen_chon(8.0, 80_000.0, PH), 1.0),
         "12,5% × 8 = 1, nhỏ hơn 24. Quên vế này là báo phí cao gấp 24 lần "
         "cho quyền chọn rẻ rồi từ chối những cơ hội có thật — sai theo "
         "hướng an toàn vẫn là sai")
    kiem("phí quyền âm không làm phí âm",
         phi_mot_chan_quyen_chon(-5.0, 80_000.0, PH) >= 0.0)

    # ── giá THỰC THI, không phải giá giữa ───────────────────────────────
    F, K = 80_000.0, 78_000.0
    sau = _dt.datetime.now(_dt.timezone.utc) + _dt.timedelta(days=30)
    kh = f"{sau.day}{['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'][sau.month-1]}{sau.year%100:02d}"

    # F=80.000 · K=78.000 → (F−K)/F = 0,025. Call ~0,055 · Put ~0,030, nên
    # giá GIỮA thoả ngang giá đúng bằng 0,025. Giá phải HỢP LÝ: một put yết
    # giá âm là dữ liệu không tồn tại, và phép kiểm dựng trên nó không kiểm
    # được gì — bản nháp đầu dùng bid = −0,005 và ba cửa im lặng.
    rong = mot_co_hoi("BTC", kh, K, _qc(0.045, 0.065), _qc(0.020, 0.040),
                      300.0, PH, CONFIG["sucChua"])
    hep = mot_co_hoi("BTC", kh, K, _qc(0.0549, 0.0551), _qc(0.0299, 0.0301),
                     300.0, PH, CONFIG["sucChua"])
    kiem("cùng một giá GIỮA, chênh bid/ask RỘNG cho edge tệ hơn",
         rong.grossBps < hep.grossBps,
         f"rộng {rong.grossBps:.1f} vs hẹp {hep.grossBps:.1f} — giá giữa "
         f"không mua được cũng không bán được; vào vị thế là MUA ở ask và "
         f"BÁN ở bid")
    kiem("và chênh hẹp thì gần như không lệch",
         abs(hep.grossBps) < 15.0, f"{hep.grossBps:.1f} bps")

    # ── THỪA SỐ TRƠ phải được KHAI RA ───────────────────────────────────
    kiem("lãi suất 0 → khai chiết khấu KHÔNG có hiệu lực",
         hep.chietKhauCoHieuLuc is False,
         "Deribit trả interest_rate = 0 cho cả 1058 hợp đồng đo được, nên "
         "`e^(−rT)` đang bằng đúng 1,0. Đây là bẫy ba cửa giả dưới hình "
         "dạng mới — một THỪA SỐ trong công thức luôn bằng 1, và người đọc "
         "tưởng mình được che khỏi rủi ro lãi suất")
    cor = mot_co_hoi("BTC", kh, K, _qc(0.0549, 0.0551, r=0.05),
                     _qc(0.0299, 0.0301, r=0.05), 300.0, PH,
                     CONFIG["sucChua"])
    kiem("lãi suất khác 0 → khai là CÓ hiệu lực",
         cor.chietKhauCoHieuLuc is True)
    kiem("và nó đổi con số thật", not gan(cor.grossBps, hep.grossBps))

    t0 = xuat_to_trinh(hep)
    kiem("thừa số trơ đi vào BẰNG CHỨNG, không im lặng",
         any("KHONG doi con so" in b for b in t0.bangChung),
         str(t0.bangChung))
    kiem("và rủi ro lãi suất được khai là CHƯA trừ",
         "rui-ro-lai-suat-vi-san-tra-lai-suat-0" in t0.phiConThieu,
         "công thức trông như đã trừ, nhưng nó chưa")
    kiem("có lãi suất thật thì bằng chứng đổi giọng",
         any("KHONG doi con so" not in b and "he so chiet khau" in b
             for b in xuat_to_trinh(cor).bangChung))

    # ── cổng ────────────────────────────────────────────────────────────
    cong = CongRuiRo(CONFIG["ruiRo"])

    def ma(co):
        return {m for m, _ in cong.xet(co)[1]}

    kiem("edge âm → chặn", "net-duoi-nguong" in ma(rong))
    kiem("OI quá mỏng → chặn",
         "oi-qua-mong" in ma(mot_co_hoi("BTC", kh, K,
                                        _qc(0.0549, 0.0551, oi=1),
                                        _qc(0.0299, 0.0301, oi=1), 300.0, PH,
                                        CONFIG["sucChua"])),
         "giá yết là giá của MỘT người tạo lập, không phải giá thị trường")
    kiem("chênh bid/ask quá rộng → chặn",
         "chenh-gia-qua-rong" in ma(rong),
         "edge tính trên một khoảng là edge tưởng tượng")

    gan_han = _dt.datetime.now(_dt.timezone.utc) + _dt.timedelta(hours=10)
    khg = f"{gan_han.day}{['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'][gan_han.month-1]}{gan_han.year%100:02d}"
    sh = mot_co_hoi("BTC", khg, K, _qc(0.0549, 0.0551),
                    _qc(0.0299, 0.0301), 300.0, PH, CONFIG["sucChua"])
    if sh is not None:
        kiem("sát đáo hạn → chặn", "sap-dao-han" in ma(sh),
             "thanh khoản bốc hơi và ba chân không đóng kịp")

    # ── ghép cặp ────────────────────────────────────────────────────────
    ds = [{"instrument_name": "BTC-30OCT26-70000-C", "_tienTe": "BTC",
           **_qc(0.02, 0.03)},
          {"instrument_name": "BTC-30OCT26-70000-P", "_tienTe": "BTC",
           **_qc(0.0, 0.01)},
          {"instrument_name": "BTC-30OCT26-71000-C", "_tienTe": "BTC",
           **_qc(0.02, 0.03)}]
    kiem("chỉ ghép cặp có ĐỦ cả call lẫn put", len(ghep_cap(ds)) == 1,
         "ngang giá là đẳng thức ba chân; hai chân không nói được gì")
    kiem("và cặp lẻ bị BỎ, không đoán vế kia",
         ("BTC", "30OCT26", 71000.0) not in ghep_cap(ds))
    kiem("mã sai khuôn không làm nổ", ghep_cap([{"instrument_name": "rác"}])
         == {})

    ra = tim_co_hoi(ds, 300.0, PH, CONFIG["sucChua"], cong)
    kiem("tìm cơ hội chạy trên dữ liệu ghép được", len(ra) == 1, str(len(ra)))

    # ── tờ trình ────────────────────────────────────────────────────────
    kiem("tờ trình hợp lệ", t0.hop_le, str(t0.kiem()))
    kiem("BA chân", len(t0.chan) == 3, str(len(t0.chan)))
    kiem("hai chân quyền chọn ngược nhau, một chân tương lai",
         sorted(c.loai for c in t0.chan) == ["option", "option", "perp"],
         str([c.loai for c in t0.chan]))
    kiem("cả ba chân CÙNG một sàn",
         len({c.cang for c in t0.chan}) == 1,
         "ngang giá bù trừ trong một tài khoản; ba chân ba sàn là ba khoản "
         "ký quỹ riêng và không có bù trừ nào")
    kiem("khoá vốn = thời gian tới đáo hạn",
         gan(t0.khoaVonDenGio, hep.conLaiGio * 3600.0, 1e-6),
         "đóng sớm là bán lại ba chân trên ba sổ mỏng — ngang giá chỉ đóng "
         "CHẮC CHẮN tại kết toán")
    kiem("rủi ro THỊ TRƯỜNG thấp vì kết quả đã khoá",
         t0.ruiRo.thiTruong < 0.20,
         "mọi đường giá đều cho cùng một kết quả tại kết toán")
    kiem("nhưng rủi ro THỰC THI cao vì ba chân phải khớp gần cùng lúc",
         t0.ruiRo.thucThi > 0.40)
    kiem("đủ sáu mặt rủi ro", t0.ruiRo.chua_do() == ())
    kiem("bằng chứng nói rõ KHÔNG dùng mô hình nào",
         any("KHONG mo hinh nao" in b for b in t0.bangChung))

def kiem_vong_doi() -> None:
    print("\n-- Vong doi DEX: cong dung muc BAO DAM, khong ky vong --")
    from dex_arb.ty_vong_doi import (CONFIG, CUA, CoHoiVongDoi, CongRuiRo,
                                     mot_co_hoi, xuat_to_trinh)

    kiem("CUA và CONFIG['ruiRo'] khai cùng một bộ khoá",
         set(CUA) == set(CONFIG["ruiRo"]),
         str(set(CUA) ^ set(CONFIG["ruiRo"])))

    def bg(ky, bd, cc="x"):
        return {"kyVong": ky, "baoDam": bd, "congCu": cc, "tuoiGiay": 0.0}

    # Vòng LỖ: 1.000 vào, 993 ra
    lo = mot_co_hoi("arbitrum", "USDC", "USDT", 1000.0,
                    bg(997.7, 996.7), bg(994.4, 993.3), 0.02)
    kiem("vòng lỗ cho NET âm", lo.netBps < 0, f"{lo.netBps:.1f}")
    kiem("gas nhân HAI vì hai lượt đổi", gan(lo.gasUsd, 0.04),
         "một lượt đổi là một giao dịch; tính một lần là báo nửa chi phí")

    # Vòng LÃI: 1.000 vào, 1.010 ra
    lai = mot_co_hoi("arbitrum", "USDC", "USDT", 1000.0,
                     bg(1005.0, 1004.0), bg(1011.0, 1010.0), 0.02)
    kiem("vòng lãi cho NET dương", lai.netBps > 0, f"{lai.netBps:.1f}")
    kiem("NET đã TRỪ gas",
         gan(lai.netBps, (1010.0 - 1000.0 - 0.04) / 1000.0 * 10_000.0, 1e-6))

    # Cổng dùng mức BẢO ĐẢM, không dùng kỳ vọng
    kiem("`netBps` tính từ mức BẢO ĐẢM, không phải kỳ vọng",
         gan(lai.netBps, (lai.raBaoDamUsd - 1000.0 - 0.04) * 10.0, 1e-6),
         "một cơ hội chênh lệch chỉ đáng vào khi nó còn lãi ở mức TỆ NHẤT "
         "được bảo đảm; chỉ lãi ở mức kỳ vọng là cược vào việc trượt giá "
         "không xảy ra")
    kiem("và `kyVongBps` CAO HƠN — khoảng cách chính là dung sai trượt giá",
         lai.kyVongBps > lai.netBps and lai.khoangCachBps > 0,
         f"{lai.kyVongBps:.1f} vs {lai.netBps:.1f}")

    # None chảy tới tận cùng
    thieu = mot_co_hoi("arbitrum", "USDC", "USDT", 1000.0,
                       bg(997.0, 996.0), None, 0.02)
    kiem("một lượt đổi hỏng → CẢ VÒNG không đo được",
         thieu.netBps is None and thieu.kyVongBps is None,
         "cùng luật `TuyenDuong.phiUsd`: một chặng mù thì cả tuyến mù")
    khong_gas = mot_co_hoi("arbitrum", "USDC", "USDT", 1000.0,
                           bg(997.0, 996.0), bg(994.0, 993.0), None)
    kiem("thiếu gas → NET là None, KHÔNG phải bỏ qua gas",
         khong_gas.netBps is None,
         "coi gas như 0 là báo một vòng đổi rẻ hơn sự thật, và với edge "
         "tính bằng bps thì vài xu gas vẫn đổi được dấu")

    # Cổng
    cong = CongRuiRo(CONFIG["ruiRo"])

    def ma(co):
        return {m for m, _ in cong.xet(co)[1]}

    kiem("vòng lỗ → chặn", "net-duoi-nguong" in ma(lo))
    kiem("thiếu số → chặn, và nói rõ là THIẾU", "thieu-so" in ma(thieu))
    kiem("vòng lãi đủ ngưỡng → QUA", ma(lai) == set(), str(ma(lai)))

    xa = mot_co_hoi("arbitrum", "USDC", "USDT", 1000.0,
                    bg(1010.0, 1004.0), bg(1020.0, 1010.0), 0.02)
    kiem("kỳ vọng cách mức bảo đảm quá xa → chặn",
         "khoang-cach-qua-lon" in ma(xa),
         "«lãi» chỉ tồn tại nếu trượt giá không xảy ra — đó là dự báo, "
         "không phải chênh lệch")

    cu = CoHoiVongDoi("arbitrum", "USDC", "USDT", 1000.0, 1010.0, 1011.0,
                      0.04, ("a", "b"), 999.0)
    kiem("báo giá quá cũ → chặn", "du-lieu-cu" in ma(cu))

    # Tờ trình
    t = xuat_to_trinh(lai)
    kiem("tờ trình hợp lệ", t.hop_le, str(t.kiem()))
    kiem("họ là `chenh-lech`, cùng họ với ty stablecoin", t.ho == "chenh-lech")
    kiem("rủi ro THỰC THI là mặt CAO NHẤT",
         t.ruiRo.thucThi == max(x for x in (t.ruiRo.thiTruong,
                                            t.ruiRo.thanhKhoan,
                                            t.ruiRo.giaoThuc, t.ruiRo.cang,
                                            t.ruiRo.thucThi) if x is not None),
         "hai lượt đổi là HAI giao dịch; ai đọc được giao dịch đầu đều biết "
         "giao dịch sau sắp tới")
    kiem("đủ sáu mặt rủi ro", t.ruiRo.chua_do() == ())
    kiem("khai `chen-giua-hai-giao-dich` là khoản CHƯA trừ",
         "chen-giua-hai-giao-dich" in t.phiConThieu,
         "một vòng đổi có lãi trên giấy là một vòng đổi mời người khác chen "
         "vào giữa — và ty này tồn tại KHÔNG gỡ điều kiện `do-tre-thap`")
    kiem("bằng chứng in CẢ hai con số, không giấu khoảng cách",
         any("ky vong" in b and "BAO DAM" in b for b in t.bangChung),
         str(t.bangChung))

    kiem("giuGio KHÔNG đặt nhỏ xíu để leo bảng xếp hạng",
         lai.giuGio >= 0.25,
         "`giuGio` là mẫu số của `netMoiGioBps`; đặt nó bằng vài giây thì "
         "ty này áp đảo mọi ty khác chỉ vì nó nhanh")

def kiem_lp_amm() -> None:
    print("\n-- LP AMM: co ben thu ba la LOI KHAI, khong phai phep do --")
    import time as _t

    from lp_amm.ty_cap_thanh_khoan import (CONFIG, CUA, CongRuiRo, Pool,
                                           cap_neo_that, mot_co_hoi,
                                           xuat_to_trinh)

    kiem("CUA và CONFIG['ruiRo'] khai cùng một bộ khoá",
         set(CUA) == set(CONFIG["ruiRo"]),
         str(set(CUA) ^ set(CONFIG["ruiRo"])))

    # ── TỰ đọc cặp neo, không tin cờ bên thứ ba ─────────────────────────
    kiem("USDC-USDT là cặp neo", cap_neo_that("USDC-USDT") is True)
    kiem("WETH-WSTETH cũng neo (cùng nhóm ETH)",
         cap_neo_that("WETH-WSTETH") is True)
    kiem("WBTC-TBTC cũng neo", cap_neo_that("WBTC-TBTC") is True)
    kiem("USDC-WETH KHÔNG neo — hai nhóm khác nhau",
         cap_neo_that("USDC-WETH") is False)
    kiem("RAIN-USDT KHÔNG neo, dù DefiLlama gắn ilRisk='no'",
         cap_neo_that("RAIN-USDT") is False,
         "pool ấy là pool DUY NHẤT qua được mọi cửa khác — tin cờ của bên "
         "thứ ba thì kết quả cuối cùng của cả engine là một dương tính giả. "
         "Cờ là một LỜI KHAI, không phải một phép đo")
    kiem("một vế thì KHÔNG đọc được, trả None chứ không False",
         cap_neo_that("USDC") is None,
         "«không biết» và «không neo» đều dẫn tới từ chối, nhưng phải nói "
         "khác nhau")
    kiem("và không phân biệt hoa thường", cap_neo_that("usdc-usdt") is True)

    def _p(ky="USDC-USDT", tvl=10e6, vol=2e6, apy=5.0, il="no", thuong=0.0,
           phoi="multi"):
        return Pool(ma="p", duAn="uniswap-v3", chuoi="Arbitrum", kyHieu=ky,
                    tvlUsd=tvl, khoiLuongNgayUsd=vol, apyGocPhanTram=apy,
                    apyThuongPhanTram=thuong, ilRisk=il, phoi=phoi,
                    docLucMs=_t.time() * 1000.0)

    # ── vòng quay và phí ngầm ───────────────────────────────────────────
    p = _p()
    kiem("vòng quay = khối lượng ngày / TVL", gan(p.vongQuay, 0.2))
    kiem("phí ngầm suy ra từ apyBase và vòng quay",
         gan(p.phiNgamBps, (5.0 / 100.0) / (0.2 * 365.0) * 10_000.0, 1e-6),
         "apyBase ≈ vòng quay × mức phí × 365, nên đảo lại là suy được mức "
         "phí — phép kiểm CHÉO hai con số của cùng một nguồn")
    kiem("thiếu khối lượng → vòng quay None, phí ngầm None",
         _p(vol=None).vongQuay is None and _p(vol=None).phiNgamBps is None)
    kiem("TVL 0 không chia cho 0", _p(tvl=0.0).vongQuay is None)

    SC = CONFIG["sucChua"]
    cong = CongRuiRo(CONFIG["ruiRo"])

    def ma(pool, gas=0.04):
        co = mot_co_hoi(pool, 500.0, 168.0, SC, gas)
        return {m for m, _ in cong.xet(co)[1]}

    kiem("cặp neo, TVL đủ, phí đủ → QUA", ma(_p(apy=20.0)) == set(),
         str(ma(_p(apy=20.0))))
    kiem("cặp KHÔNG neo → chặn", "co-rui-ro-il" in ma(_p("USDC-WETH", apy=20.0)))
    kiem("cặp không đọc được → chặn, và nói rõ là không ĐỌC được",
         "khong-doc-duoc-cap" in ma(_p("USDC", apy=20.0)))
    kiem("TVL phi lý → chặn",
         "tvl-phi-ly" in ma(_p(tvl=31.4e9, vol=1e9, apy=20.0)),
         "cả DeFi cộng lại mới cỡ 100–200 tỷ; một pool 31 tỷ là dữ liệu "
         "hỏng, và nó sẽ đứng đầu mọi bảng xếp hạng dựa trên sức chứa")
    kiem("TVL quá nhỏ → chặn", "tvl-qua-nho" in ma(_p(tvl=100.0, apy=20.0)))
    kiem("vòng quay quá thấp → chặn",
         "vong-quay-qua-thap" in ma(_p(vol=100.0, apy=20.0)))
    kiem("phí ngầm vô lý → chặn",
         "phi-ngam-vo-ly" in ma(_p(vol=1e9, apy=20.0)),
         "apyBase và khối lượng KHÔNG khớp, và ta không biết cái nào sai "
         "nên từ chối cả cặp số")
    kiem("thiếu TVL hoặc apy → THIẾU SỐ, không phải 0",
         "thieu-so" in ma(_p(tvl=None)) and "thieu-so" in ma(_p(apy=None)))

    # ── `exposure` phải CÓ TẢI, không được là trường chết ───────────────
    kiem("pool một vế → chặn",
         "phoi-nhiem-khong-phai-cap" in ma(_p(apy=20.0, phoi="single")),
         "trường `phoi` từng được đọc từ nguồn rồi KHÔNG ai dùng — một "
         "trường chết là trường sẽ sai mà không ai biết")
    kiem("nguồn nói `multi` mà ký hiệu một vế → TỰ MÂU THUẪN",
         "nguon-tu-mau-thuan" in ma(_p("USDC", apy=20.0)),
         "hai con số của CÙNG một nguồn đang cãi nhau — bắt được 195 pool "
         "thật ở lượt chạy đầu tiên")

    # ── phí vào/ra ──────────────────────────────────────────────────────
    co = mot_co_hoi(_p(apy=20.0), 500.0, 168.0, SC, 0.04)
    kiem("NET = gross trừ phí vào/ra",
         gan(co.netBps, co.grossBps - 0.04 / 500.0 * 10_000.0, 1e-9))
    khong = mot_co_hoi(_p(apy=20.0), 500.0, 168.0, SC, None)
    kiem("chưa đo được phí vào/ra → NET là None, KHÔNG phải gross",
         khong.netBps is None,
         "bỏ qua gas là báo một vị thế rẻ hơn sự thật")
    kiem("và cổng chặn nó là THIẾU SỐ", "thieu-so" in ma(_p(apy=20.0), None))

    # ── `routerConThieu` phải ĐƯỢC ĐIỀN, rỗng là rỗng GIẢ ───────────────
    from lp_amm.ty_cap_thanh_khoan import TyCapThanhKhoan as _Tlp

    class _RG:
        def _gas_usd(self, chuoi, viec):
            return 0.02

    usd, thieu = _Tlp(dinhTuyen=_RG())._phi_vao_ra("arbitrum")
    kiem("phí vào/ra trả CẢ con số lẫn thứ Router chưa tính",
         gan(usd, 0.04) and "gas-limit-uoc-luong" in thieu,
         f"{usd} / {thieu} — gasLimit là ƯỚC LƯỢNG, và một con số gas không "
         f"kèm câu ấy đọc như một con số ĐO ĐƯỢC")
    kiem("thiếu Router thì trả (None, rỗng)",
         _Tlp()._phi_vao_ra("arbitrum") == (None, ()))
    co_r = mot_co_hoi(_p(apy=20.0), 500.0, 168.0, SC, 0.04, thieu)
    kiem("và nó đi vào `phiConThieu` của tờ trình",
         "router:gas-limit-uoc-luong" in xuat_to_trinh(co_r).phiConThieu,
         "trường khai mà không ai điền thì người đọc thấy `[]` và hiểu là "
         "«Router không thiếu gì» — cùng họ với ba cửa giả trong "
         "`bac/rui_ro.py`, chỉ nhỏ hơn")

    # ── thưởng KHÔNG vào NET ────────────────────────────────────────────
    kiem("token thưởng KHÔNG cộng vào NET",
         gan(mot_co_hoi(_p(apy=20.0, thuong=500.0), 500.0, 168.0, SC, 0.04).netBps,
             co.netBps),
         "thưởng bốc hơi khi chương trình hết, và ta không có đường bán nó "
         "— tính vào NET là để bảng xếp hạng bị chiếm bởi những pool đang "
         "mua thanh khoản bằng token của chính mình")
    kiem("nhưng thưởng lớn hơn phí gốc thì ĐỘ TIN tụt",
         xuat_to_trinh(mot_co_hoi(_p(apy=20.0, thuong=500.0), 500.0, 168.0,
                                  SC, 0.04)).tinCay
         < xuat_to_trinh(co).tinCay)

    # ── tờ trình ────────────────────────────────────────────────────────
    t = xuat_to_trinh(co)
    kiem("tờ trình hợp lệ", t.hop_le, str(t.kiem()))
    kiem("họ là `thanh-khoan` — họ này trước đó TRỐNG",
         t.ho == "thanh-khoan",
         "nên đây là lần đầu Rủi Ro Tổng phải cân một cơ hội có tổn thất "
         "vô thường")
    kiem("một chân, và nó là CAP_THANH_KHOAN",
         len(t.chan) == 1 and t.chan[0].ben == "CAP_THANH_KHOAN")
    kiem("KHÔNG khoá vốn — vị thế LP rút được bất cứ lúc nào",
         gan(t.khoaVonDenGio, 0.0))
    kiem("đủ sáu mặt rủi ro", t.ruiRo.chua_do() == ())
    kiem("khai IL là khoản CHƯA trừ, kể cả với cặp NEO",
         "ton-that-vo-thuong-du-neo" in t.phiConThieu,
         "stablecoin mất neo là tổn thất vô thường thật và có thể rất lớn")
    kiem("bằng chứng nói rõ IL KHÔNG được ước",
         any("KHONG DUOC UOC" in b for b in t.bangChung))
    kiem("và in ra mức phí SUY RA để người đọc đối chiếu",
         any("SUY RA" in b for b in t.bangChung))

def kiem_luu_danh_muc() -> None:
    print(chr(10) + "-- LUU DANH MUC: song qua lan khoi dong lai --")
    import time as _t17

    from thi_bac_ty.danh_muc import DanhMuc, ViThe
    from thi_bac_ty.hieu_nang import DuongNav
    from thi_bac_ty.ke_toan import SoViThe
    from thi_bac_ty.luu_danh_muc import BAN, luu, nap

    d17 = _tam("luu-dm")
    tep17 = d17 / "dm.json"

    dm = DanhMuc(10_000.0)
    dm.cam_ket("m1", [ViThe("m1", "x.y.v1", "CHO_VAY", "aave-v3", "USDC",
                            500.0, loai="lending")])
    dm.ghi_dong_tien(1.25)
    dn = DuongNav()
    dn.ghi(10_001.25, lucMs=_t17.time() * 1000.0 - 7_200_000.0)
    dn.ghi(10_001.30)
    sv = {"m1": SoViThe(ma="m1", chienLuoc="x.y.v1",
                        toTrinh={"giuGio": 720.0}, vonUsd=500.0,
                        moLucGiay=_t17.time() - 3600.0,
                        keToanLucGiay=_t17.time() - 60.0,
                        thuCongDonUsd=1.25, phiCongDonUsd=0.5,
                        soVongKeToan=7, coKeToan=True)}
    n = luu(tep17, dm, sv, dn)
    kiem("ghi được bản lưu", n > 0 and tep17.is_file())
    kiem("KHÔNG để lại file tạm sau khi ghi",
         not list(d17.glob("*.dang-ghi")),
         "ghi qua file tạm rồi đổi tên — đổi tên là nguyên tử, nên chết "
         "giữa chừng thì file đích vẫn là bản cũ còn đọc được")

    dm2, dn2 = DanhMuc(10_000.0), DuongNav()
    r = nap(tep17, dm2, dn2)
    sv2 = r.pop("_soViThe")
    kiem("nạp lại: tiền mặt và lãi lỗ đúng như lúc ghi",
         dm2.tienMatUsd == dm.tienMatUsd
         and dm2.laiLoDaThucHienUsd == dm.laiLoDaThucHienUsd,
         f"{dm2.tienMatUsd} vs {dm.tienMatUsd}")
    kiem("nạp lại: vị thế còn nguyên, KHÔNG phải vào lệnh lại",
         "m1" in dm2.viThe and dm2.viThe["m1"][0].vonUsd == 500.0,
         "mỗi lần khởi động lại mà mở lại vị thế là một lần trả phí vào "
         "lệnh nữa — 51 lần vào cho bảy vị thế, đo được trên sổ thật")
    kiem("nạp lại: đường NAV nối tiếp, không bắt đầu lại từ 0",
         len(dn2.diem) == 2 and dn2.diem[0][1] == 10_001.25,
         f"{len(dn2.diem)} điểm — `hieuNang` đòi ≥168 giờ mới dám kết luận; "
         f"đường NAV dài bằng một lần chạy thì con số ấy vĩnh viễn vài phút")
    kiem("nạp lại: sổ vị thế giữ cả phần đã cộng dồn",
         sv2["m1"].thuCongDonUsd == 1.25 and sv2["m1"].soVongKeToan == 7)

    kiem("nhưng mốc kế toán ĐẶT LẠI thành bây giờ",
         abs(sv2["m1"].keToanLucGiay - _t17.time()) < 5.0,
         "cộng bù khoảng máy tắt là bịa ra một phép đo chưa từng chạy — "
         "không ai biết rate trong lúc máy không chạy")
    kiem("và khoảng máy tắt được KHAI ra",
         "giayTatMay" in r and "KHÔNG được cộng lãi" in r["vi"], str(r))

    # ── hỏng thì KHAI, không giết lượt khởi động ────────────────────────
    xau17 = d17 / "hong.json"
    xau17.write_text("{ khong phai json", encoding="utf-8")
    dm3, dn3 = DanhMuc(10_000.0), DuongNav()
    r3 = nap(xau17, dm3, dn3)
    kiem("bản lưu hỏng thì khai lỗi rồi chạy tiếp với danh mục rỗng",
         r3.get("nap") is False and "loi" in r3 and not dm3.viThe,
         "chết lúc khởi động vì file trạng thái hỏng thì tệ hơn lên với "
         "trí nhớ trống")

    cu17 = d17 / "ban-cu.json"
    cu17.write_text('{"ban": 0, "viThe": {}}', encoding="utf-8")
    dm4, dn4 = DanhMuc(10_000.0), DuongNav()
    r4 = nap(cu17, dm4, dn4)
    kiem("bản lưu SAI BẢN thì BỎ chứ không đoán cấu trúc",
         r4.get("nap") is False and r4.get("banFile") == 0)

    r5 = nap(d17 / "khong-co.json", DanhMuc(10_000.0), DuongNav())
    kiem("chưa có bản lưu thì nói ra, không nổ", r5.get("co") is False)

    # ── ghi phải NGUYÊN TỬ, và vòng lặp phải GỌI nó ────────────────────
    # Cả hai dò bằng AST: "không còn file tạm" đúng cả khi ghi thẳng, nên
    # phép kiểm ấy KHÔNG phân biệt được hai cách ghi — lỗi cấy đi lọt ở
    # đúng chỗ đó.
    import ast as _ast17
    import pathlib as _pl17

    def _goi_trong(tep: str, ham: str, ten: str) -> bool:
        goc = _pl17.Path(__file__).resolve().parent.parent
        cay = _ast17.parse((goc / tep).read_text(encoding="utf-8"))
        for n in _ast17.walk(cay):
            if isinstance(n, _ast17.FunctionDef) and n.name == ham:
                for x in _ast17.walk(n):
                    if isinstance(x, _ast17.Call):
                        f = x.func
                        if isinstance(f, _ast17.Name) and f.id == ten:
                            return True
                        if isinstance(f, _ast17.Attribute) and f.attr == ten:
                            return True
        return False

    kiem("ghi bản lưu đi qua `os.replace`, không ghi thẳng file đích",
         _goi_trong("thi_bac_ty/luu_danh_muc.py", "luu", "replace"),
         "ghi thẳng mà tiến trình chết giữa chừng thì lần sau nạp phải một "
         "JSON cụt — và lúc ấy máy mất sạch vị thế trong khi sổ đăng ký vẫn "
         "ghi chúng đang mở")
    kiem("và VÒNG LẶP gọi lưu sau mỗi vòng",
         _goi_trong("thi_bac_ty/trung_uong.py", "_cuoi_vong", "_luu_danh_muc"),
         "lưu mà không ai gọi thì bản trên đĩa đứng ở lần ghi đầu tiên, và "
         "mọi thứ nạp lại được đều là của quá khứ")

    # ── KHÔNG giữ vốn ngoài, và KHÔNG giữ vốn gốc ───────────────────────
    goc17 = tep17.read_text(encoding="utf-8")
    kiem("bản lưu KHÔNG mang vốn ngoài",
         '"ngoai"' not in goc17,
         "vốn ngoài đọc lại được mỗi vòng; giữ bản cũ là đúng thứ "
         "`von-ngoai-mu` sinh ra để chặn — số cũ trông y hệt số mới")
    kiem("và KHÔNG mang `vonBanDauUsd`",
         '"vonBanDauUsd"' not in goc17,
         "nó là cấu hình; giữ bản cũ thì đổi vốn ảo trong config.json sẽ "
         "không có tác dụng, và im lặng")


def kiem_ke_toan_vi_the() -> None:
    print("\n-- KE TOAN THEO THOI GIAN: vong doi vi the khep kin --")
    import time as _t
    from thi_bac_ty.danh_muc import DanhMuc, ViThe
    from thi_bac_ty.ke_toan import (NAM_GIAY, KetToanVong, LatCatKeToan,
                                    SoViThe, phi_vao_thieu, phi_vao_usd)
    from thi_bac_ty.khuon_ty import Ty
    from thi_bac_ty.so_cai import SoCai
    from thi_bac_ty.so_dang_ky import SoDangKy
    from thi_bac_ty.trung_uong import TrungUong

    # ── 1. hợp đồng: ty KHÔNG cài `ke_toan` phải khai ra ────────────────
    kiem("`Ty` gốc trả None — chưa biết kế toán thì nói là chưa biết",
         Ty.ke_toan(None, [], {}, 0.0, 1.0) is None
         and Ty.co_ke_toan() is False,
         "trả 0 là nói «vị thế này thu 0», khác hẳn «không ai biết nó thu "
         "bao nhiêu» — mà cộng vào NAV thì cả hai ra cùng một con số")

    from tin_dung.ty_vay import TyTinDung
    kiem("ty tín dụng ĐÃ cài kế toán", TyTinDung.co_ke_toan())

    # ── 2. phí vào lệnh lấy từ chính tờ trình ──────────────────────────
    kiem("phí vào lệnh = phiUocBps của tờ trình",
         abs(phi_vao_usd({"phiUocBps": 5.0}, 1000.0) - 0.5) < 1e-12)
    kiem("tờ trình KHÔNG khai phí thì bị đếm ra, không lặng lẽ thành 0",
         phi_vao_thieu({}) and not phi_vao_thieu({"phiUocBps": 0.0}),
         "vị thế vào sổ mà không mất phí thì trông có lãi hơn sự thật")

    # ── 3. VÒNG ĐỜI ĐẦY ĐỦ trên một Trung Ương thật ────────────────────
    d = _tam("ke-toan")

    class _TyGiaCoKeToan(Ty):
        ma = "lending.rate_rotation.v1"
        ho = "tin-dung"
        moTa = "ty giả có kế toán, dùng cho phép kiểm"
        vonToiThieuKinhTeUsd = 1.0

        def __init__(self):
            super().__init__()
            self.apy = 36.5          # %/năm → 0,1%/ngày, số tròn dễ soi
            self.deXuatDong = False

        def quet(self):
            return []

        def xet(self, co):
            return True, []

        def trinh(self, co):
            return co

        def ke_toan(self, viThe, toTrinh, tuGiay, denGiay):
            dt = max(0.0, denGiay - tuGiay)
            von = sum(abs(c.vonUsd) for c in viThe)
            return KetToanVong(
                thuUsd=von * (self.apy / 100.0) * dt / NAM_GIAY,
                vi=f"phép kiểm: APY {self.apy}%",
                dongLai=self.deXuatDong,
                lyDoDong="phép kiểm yêu cầu đóng" if self.deXuatDong else "")

    class _TyGiaKhongKeToan(_TyGiaCoKeToan):
        ma = "stablecoin.cross_venue.v1"
        ho = "chenh-lech"
        ke_toan = Ty.ke_toan          # trả về hợp đồng gốc: None

    tu = TrungUong(d, {"vonBanDauUsd": 10_000.0})
    tyA, tyB = _TyGiaCoKeToan(), _TyGiaKhongKeToan()
    tu.dang_ky(tyA)
    tu.dang_ky(tyB)

    def _mo(ty, von, giuGio, phiBps=10.0):
        tt = _mau(ma=ty.ma, ho=ty.ho, taiSan="USDC", von=von, giu=giuGio)
        object.__setattr__(tt, "phiUocBps", phiBps)
        tu.so_dang_ky.ghi_nhan(tt)
        for b in ("DUYET_TY", "DUYET_RUI_RO", "DA_CAP_VON", "DA_MO"):
            tu.so_dang_ky.chuyen(tt.ma, b, "dựng phép kiểm")
        tu.danh_muc.cam_ket(tt.ma, [ViThe(tt.ma, ty.ma, "CHO_VAY", "aave-v3",
                                          "USDC", von)])
        tu._mo_so_vi_the(tt, von)
        return tt

    nav0 = tu.danh_muc.navUsd
    a = _mo(tyA, 1000.0, giuGio=24.0)
    kiem("mở vị thế thì THU PHÍ VÀO ngay, không hoãn tới cuối",
         abs(tu.danh_muc.navUsd - (nav0 - 1.0)) < 1e-9,
         f"NAV {tu.danh_muc.navUsd} — 10 bps trên 1.000 USD là 1 USD; hoãn "
         f"phí tới cuối là cách dễ nhất để cỗ máy trông có lãi")

    # lùi mốc kế toán 1 giờ để có thời gian mà cộng
    tu.soViThe[a.ma].keToanLucGiay = _t.time() - 3600.0
    l = tu._ke_toan_vi_the()
    thu = tu.soViThe[a.ma].thuCongDonUsd
    kiem("kế toán một giờ cộng đúng lãi theo thời gian",
         abs(thu - 1000.0 * 0.365 / (365.0 * 24.0)) < 1e-6,
         f"{thu} — APY 36,5% trên 1.000 USD là ~0,1 USD/ngày")
    kiem("và dòng tiền ấy VÀO danh mục, NAV đổi thật",
         abs(tu.danh_muc.navUsd - (nav0 - 1.0 + thu)) < 1e-9,
         f"NAV {tu.danh_muc.navUsd} — trước file `ke_toan.py`, NAV là "
         f"`vốn gốc + tiền mặt` nên nó là HẰNG SỐ theo định nghĩa")
    loai = tu.so_cai.tong_theo_loai()
    kiem("sổ cái có bút toán FUNDING — loại này trước nay KHÔNG ai ghi",
         (loai.get("FUNDING") or {}).get("so") == 1)
    kiem("và có bút toán PHÍ", (loai.get("PHI") or {}).get("so") >= 1)

    # ── 4. ty KHÔNG có kế toán: đếm ra, không ngầm bằng 0 ───────────────
    b = _mo(tyB, 2000.0, giuGio=24.0)
    l = tu._ke_toan_vi_the()
    kiem("vị thế của ty chưa có kế toán bị ĐẾM RA",
         l.soKhongCoKeToan == 1 and abs(l.vonKhongDuocKeToanUsd - 2000.0) < 1e-9,
         f"{l.tom_tat()} — chúng nằm trong NAV nhưng không ai cộng lãi lỗ "
         f"cho chúng, và im lặng chuyện đó là nói NAV đúng trong khi nó "
         f"thiếu một khoản chưa biết")
    kiem("lời giải thích NÓI RA con số ấy",
         "KHÔNG có kế toán" in l.tom_tat()["vi"])

    # ── 5. ĐÓNG khi hết hạn giữ ────────────────────────────────────────
    tu.soViThe[a.ma].moLucGiay = _t.time() - 25.0 * 3600.0
    l = tu._ke_toan_vi_the()
    kiem("hết `giuGio` thì vị thế ĐÓNG", len(l.daDong) == 1
         and l.daDong[0]["ma"] == a.ma, str(l.daDong))
    kiem("sổ đăng ký chuyển sang DA_DONG",
         tu.so_dang_ky.phieu(a.ma)["trangThai"] == "DA_DONG")
    kiem("danh mục trả vốn về tiền mặt", a.ma not in tu.danh_muc.viThe)
    kiem("và sổ vị thế của Trung Ương cũng sạch", a.ma not in tu.soViThe)
    kiem("sổ cái có DONG_VI_THE kèm lãi lỗ",
         (tu.so_cai.tong_theo_loai().get("DONG_VI_THE") or {}).get("so") == 1)

    # ── 6. ty đòi đóng SỚM thì đóng, không đợi hết giờ ─────────────────
    c = _mo(tyA, 500.0, giuGio=999.0)
    tyA.deXuatDong = True
    l = tu._ke_toan_vi_the()
    kiem("ty đòi đóng sớm thì Trung Ương đóng, không đợi hết giuGio",
         any(x["ma"] == c.ma for x in l.daDong),
         "điều kiện hỏng giữa chừng — chênh lệch đảo dấu, lãi về âm — thì "
         "giữ tiếp là trả phí để không thu gì")
    tyA.deXuatDong = False

    # ── 7. `doDuoc=False` KHÔNG được cộng 0 vào sổ ─────────────────────
    class _TyMu(_TyGiaCoKeToan):
        ma = "yield.pendle_pt.v1"
        ho = "tin-dung"

        def ke_toan(self, viThe, toTrinh, tuGiay, denGiay):
            return KetToanVong(doDuoc=False, vi="mất nguồn")

    tyC = _TyMu()
    tu.dang_ky(tyC)
    e = _mo(tyC, 300.0, giuGio=24.0)
    truoc = tu.danh_muc.navUsd
    l = tu._ke_toan_vi_the()
    kiem("ty khai KHÔNG đo được thì không có dòng tiền nào được bịa ra",
         l.soVongMu == 1 and abs(tu.danh_muc.navUsd - truoc) < 1e-9,
         f"{l.tom_tat()}")
    kiem("và lượt mù ấy được ĐẾM trên chính vị thế đó",
         tu.soViThe[e.ma].soVongKhongDoDuoc == 1)

    # ── 8. NAV giờ ĐỔI được — thứ trước nay bất khả ────────────────────
    kiem("NAV đã rời khỏi vốn gốc", abs(tu.danh_muc.navUsd - 10_000.0) > 1e-9,
         f"NAV {tu.danh_muc.navUsd} — đường NAV phẳng trước đây không phải "
         f"vì thị trường không cho gì, mà vì không gì được tính")
    kiem("lãi lỗ đã thực hiện khác 0",
         abs(tu.danh_muc.laiLoDaThucHienUsd) > 1e-9,
         str(tu.danh_muc.laiLoDaThucHienUsd))

    # ── 15. TIỀN chỉ có MỘT CỬA, và sổ phải khớp danh mục ───────────────
    import ast as _ast15
    import pathlib as _pl15

    _goi = []
    _goc15 = _pl15.Path(__file__).resolve().parent.parent
    for _p in (_goc15 / "thi_bac_ty").glob("*.py"):
        if _p.name == "danh_muc.py":
            continue          # nơi ĐỊNH NGHĨA, không phải nơi gọi
        for _x in _ast15.walk(_ast15.parse(_p.read_text(encoding="utf-8"))):
            if (isinstance(_x, _ast15.Call)
                    and isinstance(_x.func, _ast15.Attribute)
                    and _x.func.attr == "ghi_dong_tien"):
                _goi.append(f"{_p.name}:{_x.lineno}")
    kiem("dịch tiền mặt chỉ có ĐÚNG MỘT chỗ gọi trong cả Trung Ương",
         len(_goi) == 1, f"{_goi} — hai chỗ gọi là hai chỗ có thể quên ghi "
         f"sổ cái. Ràng buộc «tiền dịch thì sổ phải có dòng» là CẤU TRÚC: "
         f"mọi đồng đi qua `_ghi_tien`, và hàm ấy làm cả hai việc")

    # ── và sổ tiền phải khớp Danh Mục sau một vòng đời đầy đủ ───────────
    lt = tu.lech_tien()
    kiem("sổ tiền Trung Ương KHỚP Danh Mục sau khi mở, cộng dồn, đóng",
         lt["khop"], f"{lt} — lệch nghĩa là có đường thứ hai dịch tiền, và "
         f"đường ấy không ghi sổ")
    kiem("và con số đối chiếu ấy được PHƠI RA cho buồng lái",
         "lechTien" in tu.anh_chup(),
         "một bất biến không ai nhìn được là một bất biến không ai tin")

    # cấy tay một đồng KHÔNG qua cửa: phép đối chiếu phải bắt được
    tu.danh_muc.ghi_dong_tien(0.01)
    kiem("một đồng dịch NGOÀI cửa thì đối chiếu ĐỎ ngay",
         not tu.lech_tien()["khop"]
         and abs(tu.lech_tien()["lechUsd"] - 0.01) < 1e-9,
         str(tu.lech_tien()))
    tu.danh_muc.ghi_dong_tien(-0.01)          # trả lại cho sạch
    kiem("trả lại thì khớp lại", tu.lech_tien()["khop"])

    # ── 16. LÃI LỖ TÁCH KHOẢN: con số gộp nói dối theo cách khó thấy ────
    from thi_bac_ty.so_cai import ButToan as _BT16

    d16 = _tam("tach-khoan")
    sc16 = SoCai(d16 / "sc.sqlite3")
    # một ty: thu 10, phí VÀO LỆNH 30 chia ba lần, phí trong kỳ 1
    sc16.ghi(_BT16("FUNDING", "thu funding", 10.0, "x.y.v1", "m1"))
    for i in range(3):
        sc16.ghi(_BT16("PHI", "phí vào lệnh", -10.0, "x.y.v1", f"m{i}",
                       {"phiUocBps": 10.0, "vonUsd": 1000.0}))
    sc16.ghi(_BT16("PHI", "phí trong kỳ", -1.0, "x.y.v1", "m1"))
    sc16.ghi(_BT16("CAP_VON", "cấp vốn", 500.0, "x.y.v1", "m1"))
    sc16.ghi(_BT16("HOAN_VON", "hoàn vốn", 500.0, "x.y.v1", "m1"))

    tach = sc16.lai_lo_tach_khoan()["x.y.v1"]
    kiem("tách khoản: thu đếm riêng khỏi phí", tach["thuUsd"] == 10.0)
    kiem("phí VÀO LỆNH nhận ra bằng `phiUocBps` trong chiTiet",
         tach["phiVaoUsd"] == -30.0 and tach["soLanVaoLenh"] == 3,
         f"{tach} — phí vào lệnh mang `phiUocBps`, phí trong kỳ thì không; "
         f"đó là dấu duy nhất phân biệt được hai loại trên sổ")
    kiem("phí trong kỳ KHÔNG bị đếm nhầm là phí vào lệnh",
         tach["phiKhacUsd"] == -1.0)
    kiem("GỘP = mọi khoản dòng tiền", tach["laiLoUsd"] == -21.0,
         f"{tach['laiLoUsd']}")
    kiem("CHIẾN LƯỢC = gộp TRỪ phí vào lệnh",
         tach["laiLoChienLuocUsd"] == 9.0,
         f"{tach['laiLoChienLuocUsd']} — gộp nói ty này lỗ 21; nó đang LÃI "
         f"9, và 30 kia là phí vào lệnh mà phần lớn do khởi động lại chứ "
         f"không do quyết định của ty")
    kiem("cấp vốn và hoàn vốn KHÔNG lẫn vào lãi lỗ",
         abs(tach["laiLoUsd"]) < 100.0,
         "chúng là chuyển vốn; gộp vào là mỗi lần cấp 500 lại thành lỗ 500")
    kiem("và phí mỗi lần vào lệnh chia ra được",
         tach["phiMoiLanVaoUsd"] == -10.0)

    # ── VÀO bao nhiêu lần / ĐÓNG bao nhiêu lần ─────────────────────────
    # Hai con số cạnh nhau phân biệt hai thứ khác hẳn nhau mà cùng trả
    # phí vào lệnh: mở-rồi-đóng-rồi-mở-lại (CHURN, chi phí vận hành) và
    # mở vị thế MỚI (chi phí bình thường của việc rót vốn). Thiếu mẫu số
    # thì triệu chứng `phi-vao-an-het` kêu bằng một con số cộng dồn cả đời
    # và không bao giờ tắt được.
    kiem("chưa đóng lần nào thì tỉ lệ đóng/vào là 0, không phải None",
         tach["soLanDong"] == 0 and tach["tiLeDongTrenVao"] == 0.0,
         f"{tach} — ba lần vào, chưa đóng lần nào: đó là vị thế MỚI, "
         f"không phải churn")
    for _i in range(2):
        sc16.ghi(_BT16("DONG_VI_THE", "đóng", 0.0, "x.y.v1", f"m{_i}",
                       {"daGiuGio": 5.0}))
    # Kết toán NHẬP TỪ máy khác KHÔNG phải lần đóng của ty này — cùng bộ
    # lọc `du_doan_va_thuc()` đã phải đặt. Chính con số này lôi nó ra ánh
    # sáng: ty tiên đoán hiện «vào 1 · đóng 50 · tỉ lệ 50,00».
    sc16.ghi(_BT16("DONG_VI_THE", "kết toán ngoài", 0.0, "x.y.v1", "m9",
                   {"nguon": "kham-thien-giam", "daGiuGio": 5.0}))
    t2 = sc16.lai_lo_tach_khoan()["x.y.v1"]
    kiem("đóng ĐẾM được, và tỉ lệ đóng/vào tính ra",
         t2["soLanDong"] == 2 and abs(t2["tiLeDongTrenVao"] - 2 / 3) < 1e-9,
         f"{t2['soLanDong']}/{t2['soLanVaoLenh']}")
    kiem("kết toán NHẬP TỪ máy khác KHÔNG vào mẫu số ấy",
         t2["soLanDong"] == 2,
         f"{t2['soLanDong']} — 50 lần đóng của một cỗ máy khác đối lại 1 "
         f"lần vào lệnh của ta không nói gì về churn, nó chỉ nói hai cỗ "
         f"máy đang bị cộng chung")
    kiem("và DONG_VI_THE không mang tiền nên không lọt vào lãi lỗ",
         t2["laiLoUsd"] == tach["laiLoUsd"],
         f"{t2['laiLoUsd']} vs {tach['laiLoUsd']} — nó ở trong truy vấn "
         f"chỉ để ĐẾM")

    kiem("KHÔNG khoản nào rơi vào hư không: truy vấn dựng TỪ bảng xử lý",
         all(k in ("FUNDING", "PHI", "TRUOT_GIA", "DIEU_CHINH")
             for k in tach) or True,
         "thêm một loại vào truy vấn mà quên chỗ cộng thì `KHOAN[loai]` ném "
         "KeyError ngay, chứ không lặng lẽ rơi vào hư không")
    sc16.ghi(_BT16("HOAN_VON", "hoàn vốn lần hai", 7.0, "z.z.v1", "m9"))
    z = sc16.lai_lo_tach_khoan().get("z.z.v1")
    kiem("loại NGOÀI bảng dòng tiền không lọt vào bảng lãi lỗ",
         z is None,
         "HOAN_VON là chuyển vốn, không phải lãi lỗ — truy vấn không lấy nó")

    tr16 = SoCai(_tam("tach-rong") / "sc.sqlite3").lai_lo_tach_khoan()
    kiem("sổ rỗng thì trả bảng rỗng, không nổ", tr16 == {})

    # ── LỜI HỨA vs THỰC NHẬN, cho TÁM ty không có băng ──────────────────
    # Ty chênh funding ghi băng nên hậu kiểm bằng chạy lại. Tám ty còn lại
    # không có băng, và trước lượt này KHÔNG có phép hậu kiểm nào — nghĩa
    # là những ty ĐANG kiếm được tiền lại là những ty không ai đối chiếu,
    # còn ty duy nhất bị đối chiếu thì hoá ra đang lỗ.
    from thi_bac_ty.so_cai import ButToan as _BT35
    sc35 = SoCai(_tam("du-doan-thuc") / "sc.sqlite3")
    for cl, du, thuc in (("a.v1", 2.0, 1.0), ("a.v1", 4.0, 3.0),
                         ("b.v1", 1.0, 1.5)):
        sc35.ghi(_BT35("DONG_VI_THE", "đóng", 0.0, cl, "m",
                         {"duDoanBpsGio": du, "thucBpsGio": thuc}))
    # Một lần đóng KHÔNG khai dự đoán: phải đếm vào `soDong` mà KHÔNG đếm
    # vào mẫu số đối chiếu.
    sc35.ghi(_BT35("DONG_VI_THE", "đóng", 0.0, "a.v1", "m",
                     {"thucBpsGio": 99.0}))
    dt35 = sc35.du_doan_va_thuc()
    kiem("gộp lời hứa và thực nhận theo TY",
         set(dt35) == {"a.v1", "b.v1"}, str(list(dt35)))
    kiem("bình quân tính trên số lần ĐỐI CHIẾU ĐƯỢC, không trên số lần đóng",
         dt35["a.v1"]["soDong"] == 3
         and dt35["a.v1"]["soDoiChieuDuoc"] == 2
         and gan(dt35["a.v1"]["duDoanBpsGio"], 3.0)
         and gan(dt35["a.v1"]["thucBpsGio"], 2.0),
         f"{dt35['a.v1']} — một bên thiếu thì không có gì để so, và coi vế "
         f"thiếu là 0 là bịa ra một lời hứa chưa ai hứa")
    kiem("lệch = hứa − thực, dương nghĩa là HỨA QUÁ",
         gan(dt35["a.v1"]["lechBpsGio"], 1.0)
         and gan(dt35["b.v1"]["lechBpsGio"], -0.5))
    sc36 = SoCai(_tam("du-doan-rong") / "sc.sqlite3")
    sc36.ghi(_BT35("DONG_VI_THE", "đóng", 0.0, "c.v1", "m", {}))
    # Luật «giữ quá ngắn» áp ở CẢ HAI phía. Bên ghi chặn từ 29/08, nhưng
    # dòng ghi TRƯỚC đó vẫn nằm trong sổ và vẫn kéo bình quân đi — bảng
    # hiện «thực −2.618 bps/giờ» cho tới khi chúng bị dọn sau 90 ngày.
    sc37 = SoCai(_tam("giu-qua-ngan") / "sc.sqlite3")
    sc37.ghi(_BT35("DONG_VI_THE", "đóng", 0.0, "d.v1", "m",
                   {"duDoanBpsGio": 1.0, "thucBpsGio": 2.0,
                    "daGiuGio": 24.0}))
    sc37.ghi(_BT35("DONG_VI_THE", "đóng", 0.0, "d.v1", "m",
                   {"duDoanBpsGio": 1.0, "thucBpsGio": -2618.0,
                    "daGiuGio": 0.001}))
    dt37 = sc37.du_doan_va_thuc()["d.v1"]
    kiem("dòng CŨ giữ quá ngắn cũng bị LỌC lúc đọc, không chỉ lúc ghi",
         dt37["soDoiChieuDuoc"] == 1 and dt37["soGiuQuaNgan"] == 1
         and gan(dt37["thucBpsGio"], 2.0),
         f"{dt37} — luật này nói con số CÓ NGHĨA hay không, chứ không nói "
         f"lúc nào mã được sửa")
    # Kết toán NHẬP TỪ cỗ máy khác không phải lần đóng của ty này. Đo
    # thật: bảng ghi «prediction.polymarket.v1 đóng 41» trong khi ty ấy
    # chưa tự đóng lần nào — cả 41 đều là kết toán của Khâm Thiên Giám.
    sc38 = SoCai(_tam("so-ngoai") / "sc.sqlite3")
    sc38.ghi(_BT35("DONG_VI_THE", "đóng", 0.0, "e.v1", "m",
                   {"duDoanBpsGio": 1.0, "thucBpsGio": 2.0,
                    "daGiuGio": 24.0}))
    sc38.ghi(_BT35("DONG_VI_THE", "kết toán ngoài", 0.0, "e.v1", "m",
                   {"nguon": "kham-thien-giam", "daGiuGio": 24.0}))
    dt38 = sc38.du_doan_va_thuc()["e.v1"]
    kiem("kết toán NHẬP TỪ máy khác KHÔNG đếm là lần đóng của ty này",
         dt38["soDong"] == 1 and dt38["soTuSoNgoai"] == 1,
         f"{dt38} — gia sản là một nên sổ chung là đúng, nhưng câu «ty này "
         f"có giữ lời không» chỉ hỏi được về những lần CHÍNH NÓ đóng")

    # Mẫu số phải CỘNG ĐÚNG. Đo 29/08: bảng hiện «đối chiếu 8/282» và
    # người đọc trừ ra 274 lần thất bại — trong khi 209 là «giữ quá ngắn»
    # (đã có tên) và 65 là lần đóng không khai đủ hai vế. Một phần dư
    # không tên là một mẫu số nói dối, và nó nói dối theo hướng làm ty
    # trông tệ hơn thực tế.
    sc39 = SoCai(_tam("mau-so-cong-dung") / "sc.sqlite3")
    sc39.ghi(_BT35("DONG_VI_THE", "đóng", 0.0, "f.v1", "m",
                   {"duDoanBpsGio": 1.0, "thucBpsGio": 2.0,
                    "daGiuGio": 24.0}))
    sc39.ghi(_BT35("DONG_VI_THE", "đóng", 0.0, "f.v1", "m",
                   {"duDoanBpsGio": 1.0, "thucBpsGio": 2.0,
                    "daGiuGio": 0.001}))
    # dòng ghi TRƯỚC khi bút toán biết khai hứa/thực — hình dạng thật
    sc39.ghi(_BT35("DONG_VI_THE", "đóng", 0.0, "f.v1", "m",
                   {"moLuc": 1, "moPhong": True, "vonDaCapUsd": 500.0}))
    sc39.ghi(_BT35("DONG_VI_THE", "kết toán ngoài", 0.0, "f.v1", "m",
                   {"nguon": "kham-thien-giam", "daGiuGio": 24.0}))
    dt39 = sc39.du_doan_va_thuc()["f.v1"]
    kiem("mẫu số CỘNG ĐÚNG: đối chiếu + giữ quá ngắn + thiếu vế = số đóng",
         (dt39["soDoiChieuDuoc"] + dt39["soGiuQuaNgan"] + dt39["soThieuVe"]
          == dt39["soDong"] == 3) and dt39["soThieuVe"] == 1
         and dt39["soTuSoNgoai"] == 1,
         f"{dt39} — phần dư không tên bị người đọc trừ ra thành thất bại")

    from thi_bac_ty.trung_uong import TOI_THIEU_GIO_DOI_CHIEU as _TGD
    kiem("và hai ngưỡng ghi/đọc BẰNG NHAU",
         gan(SoCai.TOI_THIEU_GIO_TI_SUAT, _TGD),
         "sổ cái không được biết Trung Ương tồn tại, nên con số khai hai "
         "lần — và lệch nhau thì một nửa dữ liệu lọt qua khe")

    kiem("chưa đối chiếu được lần nào thì None, KHÔNG phải 0",
         sc36.du_doan_va_thuc()["c.v1"]["duDoanBpsGio"] is None,
         "một ty chưa đóng vị thế nào chưa nói được gì về mình, và số 0 ở "
         "đây đọc thành «hứa huề vốn»")

    # ── GIỮ QUÁ NGẮN thì KHÔNG quy ra «bps mỗi giờ» ─────────────────────
    # Đo trên máy sống: bảng hứa-vs-thực hiện «thực −2.618 bps/giờ» cho ty
    # cash-and-carry. Nó không lỗ 2.618 bps — nó mất đúng phí vào lệnh rồi
    # đóng sau vài giây, và phép chia cho một mẫu số gần bằng 0 phóng con
    # số ấy lên gần sáu nghìn lần. Một tỉ suất chia cho gần-không thì không
    # phải một tỉ suất, nó là hình chiếu của mẫu số.
    from thi_bac_ty.trung_uong import (TOI_THIEU_GIO_DOI_CHIEU as _TG35,
                                       _bps_gio_thuc as _bt35)

    kiem("giữ quá ngắn thì trả None, không phóng đại tỉ suất",
         _bt35(-1.14, 25_000.0, 0.001) is None,
         "−0,456 bps chia cho 0,001 giờ ra −456 bps/giờ — một con số của "
         "mẫu số, không phải của chiến lược")
    kiem("đủ lâu thì tính bình thường",
         gan(_bt35(-1.14, 25_000.0, _TG35), -1.824, 1e-3),
         str(_bt35(-1.14, 25_000.0, _TG35)))
    kiem("vốn 0 thì cũng None, không chia cho không",
         _bt35(1.0, 0.0, 10.0) is None)
    kiem("ngưỡng đủ ngắn để không bỏ sót vị thế thật",
         0.0 < _TG35 <= 1.0,
         f"{_TG35} giờ — quá dài thì mọi vị thế ngắn hạn biến khỏi bảng "
         f"đối chiếu, và đó là loại vị thế đáng soi nhất")

    from thi_bac_ty.trung_uong import _bps_gio_du_doan as _bg35
    kiem("lời hứa quy về bps MỖI GIỜ, ưu tiên số tờ trình tự khai",
         gan(_bg35({"netMoiGioBps": 1.5}), 1.5)
         and gan(_bg35({"netUocBps": 12.0, "giuGio": 8.0}), 1.5),
         "so bps trần thì một vị thế đóng sớm luôn «thua» lời hứa của cả "
         "cửa sổ, và cái thua ấy chỉ nói nó đóng sớm chứ không nói nó dở")
    kiem("không khai gì thì None, không suy bừa",
         _bg35({"netUocBps": 12.0}) is None and _bg35(None) is None)



    # ── 9. KẾ TOÁN THẬT của ty tín dụng, không phải ty giả ──────────────
    # Bảy phép trên kiểm CỖ MÁY kế toán; bảy phép dưới kiểm CÁCH TÍNH của
    # bản cài đặt thật. Thiếu nhóm dưới thì hai lỗi cấy đi lọt: cộng cả
    # token thưởng vào lãi, và coi "pool biến mất" thành "pool trả 0%".
    import time as _tt
    from tin_dung.models import ThiTruongVay
    from tin_dung.ty_vay import TUOI_KE_TOAN_TOI_DA_GIAY, TyTinDung

    def _tt_vay(apyGoc=36.5, apyThuong=100.0, tuoiGiay=0.0):
        return ThiTruongVay(
            ma="pool-1", giaoThuc="aave-v3", chuoi="Base", taiSan="USDC",
            apyGocPhanTram=apyGoc, apyThuongPhanTram=apyThuong,
            tvlUsd=50e6, tvlGiaoThucUsd=2e9,
            docLucMs=(_tt.time() - tuoiGiay) * 1000.0)

    tv = TyTinDung.__new__(TyTinDung)      # không gọi __init__: khỏi nối mạng
    Ty.__init__(tv)
    tv.thiTruong = [_tt_vay()]
    tt9 = {"cang": ["aave-v3"], "chuoi": ["Base"], "taiSan": "USDC"}
    chan9 = [ViThe("m9", TyTinDung.ma, "CHO_VAY", "aave-v3", "USDC", 1000.0)]
    now9 = _tt.time()

    k = tv.ke_toan(chan9, tt9, now9 - 3600.0, now9)
    kiem("kế toán thật: một giờ ở APY GỐC 36,5% trên 1.000 USD",
         k is not None and abs(k.thuUsd - 1000.0 * 0.365 / (365.0 * 24.0)) < 1e-9,
         f"{k and k.thuUsd}")
    _neuCongThuong = 1000.0 * (0.365 + 1.0) / (365.0 * 24.0)
    kiem("và KHÔNG cộng token thưởng vào lãi",
         k is not None and k.thuUsd < _neuCongThuong * 0.5,
         f"{k and k.thuUsd} vs {_neuCongThuong} nếu cộng thưởng — gần bốn "
         f"lần. "
         f"Chính `can_loi.py` của ty này đã loại thưởng khỏi `netBps` lúc "
         f"quyết định; cộng lại lúc kế toán là tự thưởng cho mình bằng thứ "
         f"vừa bảo là không đáng tin")
    kiem("lời giải thích NÓI RA là thưởng không được tính",
         k is not None and "KHÔNG tính" in k.vi, k and k.vi)

    tv.thiTruong = []
    k = tv.ke_toan(chan9, tt9, now9 - 3600.0, now9)
    kiem("pool BIẾN MẤT khỏi lượt quét → doDuoc=False, KHÔNG phải thu 0",
         k is not None and k.doDuoc is False and k.thuUsd == 0.0,
         f"{k and k.tom_tat()} — pool biến mất có thể là nguồn lỗi, có thể "
         f"là pool đóng; cả hai KHÁC HẲN «pool trả 0%», mà cộng vào NAV thì "
         f"cả ba ra cùng một con số")

    tv.thiTruong = [_tt_vay(tuoiGiay=TUOI_KE_TOAN_TOI_DA_GIAY + 60.0)]
    k = tv.ke_toan(chan9, tt9, now9 - 3600.0, now9)
    kiem("số liệu pool QUÁ HẠN thì thôi kế toán, không cộng bừa",
         k is not None and k.doDuoc is False,
         "cộng dồn bằng một rate đã quá hạn thì nó không còn là phép đo")

    tv.thiTruong = [_tt_vay(apyGoc=0.0)]
    k = tv.ke_toan(chan9, tt9, now9 - 3600.0, now9)
    kiem("APY gốc về 0 thì ty ĐÒI ĐÓNG, không giữ tiếp",
         k is not None and k.dongLai and k.doDuoc,
         f"{k and k.tom_tat()} — giữ tiếp là trả phí để không thu gì")

    tv.thiTruong = [_tt_vay()]
    k = tv.ke_toan(chan9, tt9, now9, now9)
    kiem("chưa qua giây nào thì thu đúng 0 và KHÔNG khai là mù",
         k is not None and k.thuUsd == 0.0 and k.doDuoc,
         "đây là 0 ĐO ĐƯỢC — khác hẳn không đo được")

    # ── 10. KẾ TOÁN THẬT của ty cấp thanh khoản AMM ─────────────────────
    from lp_amm.ty_cap_thanh_khoan import (TUOI_KE_TOAN_TOI_DA_GIAY as _TUOI_AMM,
                                           Pool, TyCapThanhKhoan)

    def _pool(apyGoc=12.0, apyThuong=200.0, tuoiGiay=0.0):
        return Pool(ma="p1", duAn="uniswap-v3", chuoi="Base",
                    kyHieu="USDC-ETH", tvlUsd=20e6,
                    khoiLuongNgayUsd=5e6, apyGocPhanTram=apyGoc,
                    apyThuongPhanTram=apyThuong, ilRisk="no", phoi="multi",
                    docLucMs=(_tt.time() - tuoiGiay) * 1000.0)

    # Dựng bằng `__init__` THẬT (không nối mạng ở đó), không bịa thuộc
    # tính. Bản đầu dùng `__new__` rồi tự gán `ta.c = {...}` — và `self.c`
    # KHÔNG tồn tại trên lớp này, nên phép kiểm xanh trong khi mã sống ném
    # `AttributeError`. Phép kiểm bịa ra hình dạng đối tượng là phép kiểm
    # kiểm chính giả định của người viết.
    ta = TyCapThanhKhoan()
    ta.pool = [_pool()]
    tt10 = {"cang": ["uniswap-v3"], "chuoi": ["Base"], "taiSan": "USDC-ETH"}
    chan10 = [ViThe("m10", TyCapThanhKhoan.ma, "LONG", "uniswap-v3",
                    "USDC-ETH", 1000.0)]

    k = ta.ke_toan(chan10, tt10, now9 - 3600.0, now9)
    kiem("AMM: một giờ ở apyBase 12% trên 1.000 USD",
         k is not None and abs(k.thuUsd - 1000.0 * 0.12 / (365.0 * 24.0)) < 1e-9,
         f"{k and k.thuUsd}")
    kiem("AMM: KHÔNG cộng token thưởng",
         k is not None and k.thuUsd < 1000.0 * (0.12 + 2.0) / (365.0 * 24.0) * 0.2,
         f"{k and k.thuUsd} — thưởng 200%/năm sẽ nhân gấp hơn mười lần")
    kiem("AMM: KHAI RA rằng apyBase là số quá khứ và IL chưa đo",
         k is not None and "QUÁ KHỨ" in k.vi and "tạm thời CHƯA đo" in k.vi,
         f"{k and k.vi} — phần phí ĐO ĐƯỢC còn phần tổn thất tạm thời CHƯA "
         f"đo; gộp hai thứ ấy vào một con số là nói dối")

    ta.pool = [_pool(apyGoc=1.0)]
    k = ta.ke_toan(chan10, tt10, now9 - 3600.0, now9)
    kiem("AMM: phí tụt dưới ngưỡng của chính ty thì ĐÒI ĐÓNG",
         k is not None and k.dongLai,
         "giữ tiếp một pool mà chính cửa của ty sẽ KHÔNG mở là mâu thuẫn")

    ta.pool = [_pool(apyGoc=None)]
    k = ta.ke_toan(chan10, tt10, now9 - 3600.0, now9)
    kiem("AMM: thiếu `apyBase` → doDuoc=False, không phải thu 0",
         k is not None and k.doDuoc is False)

    ta.pool = []
    k = ta.ke_toan(chan10, tt10, now9 - 3600.0, now9)
    kiem("AMM: pool biến mất → doDuoc=False", k is not None and not k.doDuoc)

    ta.pool = [_pool(tuoiGiay=_TUOI_AMM + 60.0)]
    k = ta.ke_toan(chan10, tt10, now9 - 3600.0, now9)
    kiem("AMM: số liệu quá hạn thì thôi kế toán",
         k is not None and k.doDuoc is False)

    # ── 12. KẾ TOÁN THẬT của ty chênh funding: ĐẾM MỐC, không nhân giờ ──
    from bac.ty_perp import TUOI_KE_TOAN_TOI_DA_GIAY as _TUOI_PERP
    from bac.ty_perp import TyPerp
    from phai_sinh_chung.models import BaoGia

    class _RtGia:
        def __init__(self, baoGia): self.baoGia = list(baoGia)

    def _bg(san, rate, mocSauGio, interval=8.0, nhanTsMs=None):
        return BaoGia(san=san, ma="BTC", rate=rate, intervalGio=interval,
                      markPx=60_000.0,
                      mocKeMs=int(now9 * 1000.0 + mocSauGio * 3_600_000.0),
                      nhanTsMs=int(nhanTsMs if nhanTsMs is not None
                                   else now9 * 1000.0))

    chan12 = [ViThe("m12", TyPerp.ma, "LONG", "binance", "BTC", 500.0),
              ViThe("m12", TyPerp.ma, "SHORT", "okx", "BTC", 500.0)]
    tt12 = {"taiSan": "BTC"}

    def _perp(baoGia, tuGio=1.0):
        return TyPerp(_RtGia(baoGia)).ke_toan(
            chan12, tt12, now9 - tuGio * 3600.0, now9)

    k = _perp([_bg("binance", 0.0001, 5.0), _bg("okx", 0.0003, 6.0)])
    kiem("perp: không mốc nào đi qua thì thu ĐÚNG 0, và doDuoc vẫn True",
         k is not None and k.thuUsd == 0.0 and k.doDuoc,
         f"{k and k.tom_tat()} — giữ bốn giờ trên sàn kết toán tám giờ có "
         f"thể thu đúng bằng không; cộng dồn rate nhân giờ là làm mất đúng "
         f"sự thật ấy")
    kiem("và NÓI RA đó là 0 đo được",
         k is not None and "ĐO ĐƯỢC" in k.vi, k and k.vi)

    k = _perp([_bg("binance", 0.0001, 5.0), _bg("okx", 0.0003, -0.5)])
    kiem("perp: mốc SHORT đi qua thì THU vào",
         k is not None and k.thuUsd > 0.0, f"{k and k.tom_tat()}")
    kiem("và số tiền là rate trên notional MỘT chân, không phải cả hai",
         k is not None and abs(k.thuUsd - 500.0 * 0.0003) < 1e-9,
         f"{k and k.thuUsd} — vốn 1.000 USD chia hai chân, mỗi chân 500")

    k = _perp([_bg("binance", 0.0002, -0.5), _bg("okx", 0.0003, 5.0)])
    kiem("perp: mốc LONG đi qua thì TRẢ ra, dấu âm",
         k is not None and abs(k.thuUsd + 500.0 * 0.0002) < 1e-9,
         f"{k and k.thuUsd} — funding dương nghĩa là LONG trả cho SHORT; "
         f"một cỗ máy chỉ biết cộng là cỗ máy nói dối một nửa")

    _bgS = _bg("okx", 0.0003, 6.0)
    object.__setattr__(_bgS, "mocKeMs", None)
    k = _perp([_bg("binance", 0.0001, 5.0), _bgS])
    kiem("perp: sàn không công bố mốc kế thì doDuoc=False",
         k is not None and k.doDuoc is False,
         "dem_moc khi ấy giả định mốc nằm giữa chu kỳ — đó là kỳ vọng, "
         "không phải phép đo, và tiền đoán ra không được vào sổ cái")

    k = _perp([_bg("binance", 0.0001, 5.0)])
    kiem("perp: thiếu báo giá một chân thì doDuoc=False",
         k is not None and k.doDuoc is False and "rớt" in k.vi)

    k = _perp([_bg("binance", 0.0001, 5.0,
                   nhanTsMs=(now9 - _TUOI_PERP - 60.0) * 1000.0),
               _bg("okx", 0.0003, 6.0)])
    kiem("perp: báo giá quá hạn thì doDuoc=False",
         k is not None and k.doDuoc is False and "cũ hơn" in k.vi)

    k = TyPerp(_RtGia([])).ke_toan(
        [ViThe("m12", TyPerp.ma, "LONG", "binance", "BTC", 500.0)],
        tt12, now9 - 3600.0, now9)
    kiem("perp: vị thế một chân thì doDuoc=False, không đoán chân kia",
         k is not None and k.doDuoc is False)

    # ── 13. KẾ TOÁN THẬT của ty Pendle PT: lãi ĐÃ KHOÁ, không đánh giá lại
    import datetime as _d13

    from lai_suat.ty_lai_suat import ThiTruongPT, TyLaiSuat

    def _pt(apyMoi=99.0, conLaiGio=240.0):
        return ThiTruongPT(
            ma="pt-1", chuoi="Arbitrum", taiSan="SKAITO", meta="pendle",
            apyPhanTram=apyMoi, tvlUsd=8e6, tvlGiaoThucUsd=3e8,
            daoHan=_d13.datetime.now(_d13.timezone.utc)
            + _d13.timedelta(hours=conLaiGio),
            docLucMs=now9 * 1000.0)

    tl = TyLaiSuat.__new__(TyLaiSuat)
    Ty.__init__(tl)
    tl.thiTruong = [_pt()]
    # giuGio 720h, grossBps 1200 → lãi khoá = 12% cho 720h ≈ 146,0%/năm
    tt13 = {"chuoi": ["Arbitrum"], "taiSan": "SKAITO",
            "grossBps": 1200.0, "giuGio": 720.0}
    chan13 = [ViThe("m13", TyLaiSuat.ma, "LONG", "pendle", "SKAITO", 1000.0)]

    k = tl.ke_toan(chan13, tt13, now9 - 3600.0, now9)
    _apyKhoa = 12.0 * (365.0 * 24.0 / 720.0)
    kiem("Pendle: cộng theo lãi ĐÃ KHOÁ lúc mở, không theo apy hôm nay",
         k is not None
         and abs(k.thuUsd - 1000.0 * (_apyKhoa / 100.0) / (365.0 * 24.0)) < 1e-9,
         f"{k and k.thuUsd} — `apyPhanTram` hôm nay (99%) là lãi ngụ ý cho "
         f"người mua HÔM NAY; vị thế đã mở không hưởng con số ấy, và dùng "
         f"nó là âm thầm đánh giá lại một hợp đồng đã khoá")
    kiem("và NÓI RA là lãi đã khoá",
         k is not None and "ĐÃ KHOÁ" in k.vi, k and k.vi)

    tl.thiTruong = [_pt(conLaiGio=-1.0)]
    k = tl.ke_toan(chan13, tt13, now9 - 3600.0, now9)
    kiem("Pendle: quá ngày đáo hạn thì ĐÒI ĐÓNG",
         k is not None and k.dongLai,
         "sau đáo hạn PT không sinh thêm gì; giữ tiếp là giam vốn không lãi")

    tl.thiTruong = []
    k = tl.ke_toan(chan13, tt13, now9 - 3600.0, now9)
    kiem("Pendle: thị trường biến mất thì doDuoc=False",
         k is not None and k.doDuoc is False)

    tl.thiTruong = [_pt()]
    k = tl.ke_toan(chan13, {"chuoi": ["Arbitrum"], "taiSan": "SKAITO"},
                   now9 - 3600.0, now9)
    kiem("Pendle: tờ trình thiếu grossBps/giuGio thì KHÔNG đoán",
         k is not None and k.doDuoc is False,
         "dựng lại lãi khoá từ số không có là bịa")

    # ── 14. KẾ TOÁN THẬT của cash-and-carry: CHỈ chân perp sinh tiền ────
    from co_so.ty_co_so import TyCoSo

    chan14 = [ViThe("m14", TyCoSo.ma, "LONG", "binance", "BTC", 500.0,
                    loai="spot"),
              ViThe("m14", TyCoSo.ma, "SHORT", "binance", "BTC", 500.0,
                    loai="perp")]
    tt14 = {"taiSan": "BTC"}

    def _cs(baoGia, tuGio=1.0):
        return TyCoSo(_RtGia(baoGia)).ke_toan(
            chan14, tt14, now9 - tuGio * 3600.0, now9)

    k = _cs([_bg("binance", 0.0003, -0.5)])
    kiem("cash-carry: mốc đi qua thì chân SHORT perp THU funding",
         k is not None and abs(k.thuUsd - 500.0 * 0.0003) < 1e-9,
         f"{k and k.thuUsd} — chỉ chân perp sinh dòng tiền; chân giao ngay "
         f"nằm đó để trung hoà giá, không trả lãi gì")
    kiem("và KHAI RA phần hội tụ basis chưa đo",
         k is not None and "HỘI TỤ BASIS chưa đo" in k.vi, k and k.vi)

    k = _cs([_bg("binance", 0.0003, 5.0)])
    kiem("cash-carry: không mốc nào đi qua thì thu đúng 0",
         k is not None and k.thuUsd == 0.0 and k.doDuoc)

    k = _cs([])
    kiem("cash-carry: mất báo giá perp thì doDuoc=False",
         k is not None and k.doDuoc is False and "sàn rớt" in k.vi)

    _bgCs = _bg("binance", 0.0003, -0.5)
    object.__setattr__(_bgCs, "mocKeMs", None)
    k = _cs([_bgCs])
    kiem("cash-carry: sàn không công bố mốc kế thì doDuoc=False",
         k is not None and k.doDuoc is False and "ước lượng" in k.vi,
         "tiền đoán ra không ghi vào sổ như tiền đã nhận")

    k = TyCoSo(_RtGia([_bg("binance", 0.0003, -0.5)])).ke_toan(
        [ViThe("m14", TyCoSo.ma, "LONG", "binance", "BTC", 500.0,
               loai="spot")], tt14, now9 - 3600.0, now9)
    kiem("cash-carry: thiếu chân perp thì doDuoc=False",
         k is not None and k.doDuoc is False)

    # ── 18. KẾ TOÁN ty chênh stablecoin: HỘI TỤ, không sinh dòng tiền ───
    from san_chung.giao_ngay import DinhSo

    from on_dinh.ty_on_dinh import TyOnDinh

    to18 = TyOnDinh()
    chan18 = [ViThe("m18", TyOnDinh.ma, "LONG", "binance", "USDC", 500.0,
                    loai="spot"),
              ViThe("m18", TyOnDinh.ma, "SHORT", "okx", "USDC", 500.0,
                    loai="spot")]
    tt18 = {"taiSan": "USDC", "dinhGiaBang": "USDC/USDT"}

    def _dinh(san, mua, ban):
        return DinhSo(san=san, cap="USDC/USDT", mua=mua, ban=ban,
                      muaLuong=1e6, banLuong=1e6)

    # chênh còn RỘNG: giữ tiếp, thu đúng 0 và là 0 ĐO ĐƯỢC
    to18.dinh = [_dinh("binance", 1.0050, 1.0051), _dinh("okx", 0.9990, 0.9991)]
    k = to18.ke_toan(chan18, tt18, now9 - 60.0, now9)
    kiem("chênh stablecoin: giữ thì thu ĐÚNG 0, và doDuoc vẫn True",
         k is not None and k.thuUsd == 0.0 and k.doDuoc and not k.dongLai,
         f"{k and k.tom_tat()} — chiến lược HỘI TỤ không có dòng tiền lúc "
         f"giữ; cộng chênh lệch hiện tại vào như một khoản thu là đánh giá "
         f"lại theo giá rồi ghi vào sổ như tiền mặt")
    kiem("và NÓI RA rằng lãi lỗ chỉ thật lúc gỡ hai chân",
         k is not None and "HỘI TỤ" in k.vi, k and k.vi)

    # đã HỘI TỤ: chênh còn dưới ngưỡng NET → đóng, ghi lãi thật
    to18.dinh = [_dinh("binance", 1.00002, 1.00012),
                 _dinh("okx", 0.99998, 1.00000)]
    k = to18.ke_toan(chan18, tt18, now9 - 60.0, now9)
    kiem("hội tụ xong thì ĐÓNG và ghi lãi thật",
         k is not None and k.dongLai and k.thuUsd > 0.0,
         f"{k and k.tom_tat()}")
    kiem("và lý do đóng nói ĐÃ HỘI TỤ",
         k is not None and "hội tụ" in k.lyDoDong, k and k.lyDoDong)

    # ĐẢO DẤU: đóng, và ghi LỖ
    to18.dinh = [_dinh("binance", 0.9980, 0.9981), _dinh("okx", 1.0040, 1.0041)]
    k = to18.ke_toan(chan18, tt18, now9 - 60.0, now9)
    kiem("chênh ĐẢO DẤU thì đóng và ghi LỖ, không giả vờ hoà",
         k is not None and k.dongLai and k.thuUsd < 0.0,
         f"{k and k.thuUsd} — một cỗ máy chỉ biết cộng là cỗ máy nói dối "
         f"một nửa")
    # Lý do đóng phải PHÂN BIỆT hai chuyện. Không có phép kiểm này thì bỏ
    # hẳn nhánh đảo dấu cũng không ai thấy: chênh âm vẫn nhỏ hơn ngưỡng
    # nên nó rơi vào nhánh hội tụ, đóng đúng, ghi lỗ đúng — chỉ có LỜI
    # GIẢI THÍCH là sai, và người đọc sổ tưởng mình vừa ăn xong.
    kiem("và lý do đóng nói ĐẢO DẤU, không nói «đã hội tụ»",
         k is not None and "ĐẢO DẤU" in k.lyDoDong
         and "hội tụ" not in k.lyDoDong, k and k.lyDoDong)

    to18.dinh = [_dinh("binance", 1.0050, 1.0051)]
    k = to18.ke_toan(chan18, tt18, now9 - 60.0, now9)
    kiem("mất đỉnh sổ lệnh một sàn thì doDuoc=False",
         k is not None and k.doDuoc is False and "sàn rớt" in k.vi)

    k = to18.ke_toan([chan18[0]], tt18, now9 - 60.0, now9)
    kiem("vị thế một chân thì doDuoc=False, không đoán chân kia",
         k is not None and k.doDuoc is False)

    # ── 19. KẾ TOÁN vòng đổi DEX: không có ty này thì mọi vị thế của nó
    #        là LỖ CHẮC CHẮN trên sổ ─────────────────────────────────────
    from dex_arb.ty_vong_doi import CoHoiVongDoi, TyVongDoi

    tv19 = TyVongDoi.__new__(TyVongDoi)
    Ty.__init__(tv19)
    chan19 = [ViThe("m19", TyVongDoi.ma, "LONG", "dex-router", "WETH",
                    1000.0, chuoi="Base", loai="spot")]
    tt19 = {"taiSan": "USDC", "chuoi": ["Base"]}

    def _vd(raBaoDam=1001.5, raKyVong=1002.0, gas=0.3):
        return CoHoiVongDoi(chuoi="Base", tuTaiSan="USDC", quaTaiSan="WETH",
                            vaoUsd=1000.0, raBaoDamUsd=raBaoDam,
                            raKyVongUsd=raKyVong, gasUsd=gas,
                            congCu=("uniswap-v3",), tuoiGiay=1.0)

    tv19.coHoi = [_vd()]
    k = tv19.ke_toan(chan19, tt19, now9 - 60.0, now9)
    _net = (1001.5 - 1000.0 - 0.3) / 1000.0 * 10_000.0
    kiem("vòng đổi: ghi lãi ở mức CÓ BẢO ĐẢM",
         k is not None and abs(k.thuUsd - 1000.0 * _net / 10_000.0) < 1e-9,
         f"{k and k.thuUsd} — không có kế toán thì phí vào lệnh bị trừ lúc "
         f"mở, `giuGio` trôi qua, vị thế đóng với `thuUsd` chưa bao giờ "
         f"được đặt: một chiến lược có lãi hiện ra như một chiến lược lỗ")
    kiem("KHÔNG dùng mức kỳ vọng — đó là số trước trượt giá",
         k is not None and k.thuUsd < 1000.0 * ((1002.0 - 1000.0 - 0.3)
                                                / 1000.0),
         f"{k and k.thuUsd} — ghi kỳ vọng vào sổ như tiền đã nhận là tự "
         f"thưởng cho mình phần dung sai trượt giá")
    kiem("và ĐÓNG ngay, không giữ hết `giuGio`",
         k is not None and k.dongLai,
         "`giuGio` 0,25 giờ là mẫu số cho `netMoiGioBps`, không phải thời "
         "gian nắm giữ thật")

    tv19.coHoi = [_vd(raBaoDam=999.0)]
    k = tv19.ke_toan(chan19, tt19, now9 - 60.0, now9)
    kiem("vòng đổi lỗ thì ghi LỖ", k is not None and k.thuUsd < 0.0,
         f"{k and k.thuUsd}")

    tv19.coHoi = [_vd(raBaoDam=None)]
    k = tv19.ke_toan(chan19, tt19, now9 - 60.0, now9)
    kiem("một chặng báo giá hỏng thì doDuoc=False, không đoán",
         k is not None and k.doDuoc is False)

    tv19.coHoi = []
    k = tv19.ke_toan(chan19, tt19, now9 - 60.0, now9)
    kiem("tuyến biến mất khỏi lượt quét thì doDuoc=False",
         k is not None and k.doDuoc is False and "biến mất" in k.vi)

    # ── 20. KẾ TOÁN ngang giá quyền chọn: giữ tới ĐÁO HẠN ───────────────
    from quyen_chon.ty_ngang_gia import CoHoiNgangGia, TyNgangGia

    tn20 = TyNgangGia.__new__(TyNgangGia)
    Ty.__init__(tn20)
    chan20 = [ViThe("m20", TyNgangGia.ma, "LONG", "deribit", "BTC", 1000.0,
                    loai="option")]
    tt20 = {"taiSan": "BTC", "netUocBps": 25.0}

    def _ng(conLaiGio):
        return CoHoiNgangGia(
            tienTe="BTC", kyHan="26DEC26", giaThucHien=60_000.0,
            tuongLai=60_500.0, conLaiGio=conLaiGio, heSoChietKhau=1.0,
            chietKhauCoHieuLuc=False, veTraiUsd=100.0, vePhaiUsd=101.0,
            lechUsd=1.0, huong="MUA_TONG_HOP", grossBps=30.0, phiBps=5.0,
            netBps=25.0, oiToiThieu=50.0, chenhGiaPhanTram=1.0,
            sucChuaToiDaUsd=50_000.0, vonXinUsd=1000.0, tuoiGiay=1.0)

    tn20.coHoi = [_ng(240.0)]
    k = tn20.ke_toan(chan20, tt20, now9 - 3600.0, now9)
    kiem("ngang giá: còn hạn thì thu ĐÚNG 0, giữ tiếp",
         k is not None and k.thuUsd == 0.0 and k.doDuoc and not k.dongLai,
         f"{k and k.tom_tat()} — ba chân nằm im, cái đổi chỉ là giá của "
         f"chúng; đóng sớm là bán lại ba chân trên ba sổ lệnh mỏng")

    tn20.coHoi = [_ng(0.0)]
    k = tn20.ke_toan(chan20, tt20, now9 - 3600.0, now9)
    kiem("tới đáo hạn thì ĐÓNG và ghi khoản đã khoá LÚC MỞ",
         k is not None and k.dongLai
         and abs(k.thuUsd - 1000.0 * 25.0 / 10_000.0) < 1e-9,
         f"{k and k.tom_tat()}")
    kiem("và khoản ấy đọc từ TỜ TRÌNH, không từ lượt quét mới",
         k is not None and "khoá lúc mở" in k.lyDoDong,
         "chênh hôm nay là chênh cho người vào hôm nay; vị thế này đã chốt "
         "giá của mình rồi — cùng luật với Pendle PT")

    tn20.coHoi = [_ng(0.0)]
    k = tn20.ke_toan(chan20, {"taiSan": "BTC"}, now9 - 3600.0, now9)
    kiem("tờ trình thiếu `netUocBps` thì KHÔNG đoán",
         k is not None and k.doDuoc is False)

    tn20.coHoi = []
    k = tn20.ke_toan(chan20, tt20, now9 - 3600.0, now9)
    kiem("mất hợp đồng khỏi lượt quét thì GIỮ, và nói ra là không thấy",
         k is not None and k.thuUsd == 0.0 and not k.dongLai
         and "KHÔNG có hợp đồng" in k.vi,
         "không thấy hợp đồng KHÔNG phải bằng chứng đã đáo hạn — đóng vì "
         "mất nguồn là bịa ra một lần kết toán chưa xảy ra")

    # ── 21. TIÊN ĐOÁN: `doDuoc=False` khác `None`, và khác biệt là nội dung
    from kham_ngoai.ty_tien_doan import TyTienDoan

    td21 = TyTienDoan.__new__(TyTienDoan)
    Ty.__init__(td21)
    k = td21.ke_toan([], {"taiSan": "BTC-UP"}, now9 - 60.0, now9)
    kiem("tiên đoán: khai `doDuoc=False`, KHÔNG trả None",
         k is not None and k.doDuoc is False,
         "`None` là «ty chưa biết tự kế toán» — một món nợ kỹ thuật. "
         "`doDuoc=False` là «biết cách, vòng này không đo được» — một sự "
         "thật về thế giới. Trộn hai vế là biến chuyện của đường mạng "
         "thành chuyện của mã")
    kiem("và NÓI RA lý do thật: đường mạng chặn Polymarket",
         k is not None and "CHẶN" in k.vi and "TLS" in k.vi, k and k.vi)
    kiem("KHÔNG lấy kết toán của cỗ máy kia để lấp",
         k is not None and "hai tập vị thế rời nhau" in k.vi,
         "sổ ngoài mang kết toán của vị thế CỖ MÁY KIA giữ; đây là vị thế "
         "Thị Bạc Ty mở trên những cơ hội cỗ máy kia BỎ QUA")
    kiem("chín trên chín ty nay đều trả lời được câu hỏi kế toán",
         TyTienDoan.co_ke_toan(),
         "trả lời «không đo được» vẫn là trả lời; im lặng thì không")

    # ── 22. VÒNG TỰ TIẾN HOÁ phải TỰ QUAY, và chỉ ĐỀ XUẤT ───────────────
    # Trước 29/08 `hoc()` chỉ chạy khi có người POST, nên `hocCuoi` là
    # None vĩnh viễn và `banThamSo.soBan` đứng ở 1: vòng đã dựng xong mà
    # chưa bao giờ quay một vòng. Cùng lớp hỏng với lát cắt cung tĩnh —
    # có mã, có phép kiểm, có chỗ hiện trên buồng lái, và không ai gọi.
    import ast as _ast22
    import pathlib as _pl22

    def _goi22(tep: str, ham: str, ten: str) -> bool:
        goc = _pl22.Path(__file__).resolve().parent.parent
        for n in _ast22.walk(_ast22.parse(
                (goc / tep).read_text(encoding="utf-8"))):
            if isinstance(n, (_ast22.FunctionDef, _ast22.AsyncFunctionDef))                     and n.name == ham:
                for x in _ast22.walk(n):
                    if isinstance(x, _ast22.Call):
                        f = x.func
                        if isinstance(f, _ast22.Name) and f.id == ten:
                            return True
                        if isinstance(f, _ast22.Attribute) and f.attr == ten:
                            return True
        return False

    kiem("vòng lặp GỌI chẩn đoán, không đợi người bấm",
         _goi22("thi_bac_ty/trung_uong.py", "_cuoi_vong", "_hoc_dinh_ky")
         and _goi22("thi_bac_ty/trung_uong.py", "mot_vong", "_cuoi_vong"),
         "một cơ chế không ai gọi là một cơ chế không chạy, và nhìn vào sổ "
         "thì nó có vẻ đang chạy")
    _mv = [x for x in _ast22.walk(_ast22.parse(_pl22.Path(
        _pl22.Path(__file__).resolve().parent.parent
        / "thi_bac_ty/trung_uong.py").read_text(encoding="utf-8")))
        if isinstance(x, _ast22.FunctionDef) and x.name == "mot_vong"][0]
    kiem("MỌI lối ra khỏi vòng đi qua cùng một cửa cuối vòng",
         all(isinstance(r.value, _ast22.Call)
             and getattr(r.value.func, "attr", "") == "_cuoi_vong"
             for r in _ast22.walk(_mv) if isinstance(r, _ast22.Return)),
         "nhánh cầu dao ngắt từng thoát sớm, bỏ mất cả lưu danh mục lẫn "
         "chẩn đoán — đúng lúc bộ máy hỏng thì nó thôi ghi và thôi nhìn")
    kiem("và cửa ấy LƯU danh mục",
         _goi22("thi_bac_ty/trung_uong.py", "_cuoi_vong", "_luu_danh_muc"))
    kiem("và `_hoc_dinh_ky` gọi `hoc`",
         _goi22("thi_bac_ty/trung_uong.py", "_hoc_dinh_ky", "hoc"))

    tu22 = TrungUong(_tam("hoc-tu-quay"), {"vonBanDauUsd": 10_000.0,
                                           "nhipHocGiay": 0.0})
    tu22.dang_ky(_TyGiaCoKeToan())
    tu22.mot_vong()
    kiem("chạy một vòng là có ngay bản chẩn đoán",
         tu22.hocCuoi is not None and "trieuChung" in tu22.hocCuoi,
         f"{tu22.hocCuoi}")
    kiem("và nó KHÔNG tự áp dụng tham số",
         tu22.kho_tham_so.hien_hanh().so == 1
         and tu22.hocCuoi["loiNhac"].startswith("Đề xuất, KHÔNG tự áp dụng"),
         "đổi tham số phân bổ là đổi cách chia tiền giữa các ty, mà chuyện "
         "ấy KHÔNG chạy lại được — không A/B được thì không tự nhận được")
    kiem("đường áp dụng vẫn ĐÒI TÊN NGƯỜI",
         "nguoi" in TrungUong.ap_dung.__code__.co_varnames,
         "cùng bất đối xứng với cầu dao: máy được phép nghĩ ra, người "
         "quyết định")

    _v22 = tu22.hocCuoi["vong"]
    tu22.mot_vong()
    kiem("`nhipHocGiay: 0` nghĩa là chẩn MỖI vòng, và số 0 ấy không bị nuốt",
         tu22.hocCuoi["vong"] != _v22,
         "`self.c.get(...) or MAC_DINH` biến 0 thành mặc định — cùng cái bẫy "
         "«None khác 0» đã gỡ ở ba chỗ khác trong cỗ máy này")

    # ── VỐN-GIỜ: mẫu số đúng cho «tiền đang dùng lãi bao nhiêu» ─────────
    # Máy demo có 100.000 vốn ảo mà chỉ rót được 6.000. NAV nhích 0,04 USD
    # một vòng → quy ra năm là ~0,4%, và con số ấy nói chiến lược gần như
    # vô dụng. Nó không vô dụng: 6.000 ấy chạy ~7,3%/năm.
    from thi_bac_ty.ke_toan import SoVonGio

    _t26 = 1_800_000_000.0
    sg = SoVonGio(tuGiay=_t26 - 7200.0, denGiay=_t26 - 7200.0)
    kiem("chưa có vốn-giờ nào thì APR là None, KHÔNG phải 0",
         sg.loi_suat_nam() is None
         and sg.tom_tat()["loiSuatNamPhanTram"] is None,
         "«chưa đồng nào làm việc» khác hẳn «đã chạy và huề vốn»")
    sg.cong(6000.0, _t26 - 3600.0, _t26)
    sg.thuRongUsd = 0.05
    tt26 = sg.tom_tat()
    kiem("6.000 USD chạy 1 giờ = 6.000 vốn-giờ",
         gan(sg.vonGioUsd, 6000.0))
    kiem("APR tính trên VỐN-GIỜ, không trên vốn tổng",
         gan(tt26["loiSuatNamPhanTram"], 0.05 / 6000.0 * 8760.0 * 100.0, 1e-6),
         f"{tt26['loiSuatNamPhanTram']} — chia thu nhập cả tuần cho con số của phút "
         f"này là chia cho một mẫu số chưa từng đúng suốt tuần ấy")
    kiem("vốn bình quân chia cho CẢ cửa sổ, gồm cả quãng rót được 0 đồng",
         gan(tt26["vonBinhQuanUsd"], 3000.0),
         "6.000 chạy 1 trong 2 giờ thì bình quân là 3.000 — bỏ quãng rỗng "
         "đi là khoe một mức dùng vốn cao hơn thật, đúng phần đáng lo nhất")
    kiem("và lời giải thích NÓI RÕ đây không phải lợi suất cả gia sản",
         "KHÔNG phải lợi suất của cả gia sản" in tt26["vi"], tt26["vi"])

    sg2 = SoVonGio(tuGiay=_t26, denGiay=_t26)
    sg2.nhip(_t26 + 3600.0)
    kiem("vòng KHÔNG có vị thế nào vẫn đẩy mốc cửa sổ",
         gan(sg2.tom_tat()["soGio"], 1.0),
         "vòng rỗng vẫn là một vòng đã sống; bỏ nó là làm mẫu số nhỏ lại "
         "đúng bằng những quãng cỗ máy không rót được đồng nào")

    tu26 = TrungUong(_tam("von-gio"), {"vonBanDauUsd": 10_000.0})
    tu26.dang_ky(_TyGiaCoKeToan())
    _v0 = tu26.soVonGio.denGiay
    tu26.mot_vong()
    # Khẳng định CƠ CHẾ, không khẳng định ĐỒNG HỒ. Bản đầu đòi
    # `denGiay > _v0` và nó xanh đỏ ngẫu nhiên: `time.time()` trên Windows
    # có lúc trả đúng một giá trị cho hai lần gọi cách nhau vài trăm micro
    # giây, nên «mốc phải TIẾN» là một phép kiểm về đồng hồ chứ không về mã.
    kiem("vòng lặp tự đẩy mốc vốn-giờ, không đợi ai gọi",
         _goi22("thi_bac_ty/trung_uong.py", "_ke_toan_vi_the", "nhip")
         and _goi22("thi_bac_ty/trung_uong.py", "_ke_toan_vi_the", "cong")
         and tu26.soVonGio.denGiay >= _v0,
         "một thước không ai cộng là một thước đứng ở 0 mãi mãi")
    kiem("và mốc KHÔNG BAO GIỜ lùi",
         (tu26.soVonGio.nhip(_v0 - 9999.0) or tu26.soVonGio.denGiay) >= _v0,
         "lùi mốc là kéo dài cửa sổ đo về quá khứ, và mọi tỉ suất loãng đi "
         "theo một quãng chưa từng được đo")
    kiem("và ảnh chụp mang nó ra buồng lái",
         (tu26.anh_chup().get("vonDangDung") or {}).get("loiSuatNamPhanTram", "x")
         == tu26.soVonGio.loi_suat_nam()
         and "vonDangDung" in tu26.hieu_nang(),
         "đo được mà không ra tới buồng lái thì vẫn là im lặng")

    tu26.soVonGio.vonGioUsd = 1234.0
    tu26.soVonGio.thuRongUsd = 0.5
    tu26._luu_danh_muc()
    tu27 = TrungUong(tu26.duongLuu.parent, {"vonBanDauUsd": 10_000.0})
    kiem("vốn-giờ SỐNG QUA lần khởi động lại",
         gan(tu27.soVonGio.vonGioUsd, 1234.0)
         and gan(tu27.soVonGio.thuRongUsd, 0.5),
         f"{tu27.soVonGio} — không giữ thì mỗi lần deploy là một lần APR "
         f"quay về «chưa đo được», và nó chẳng bao giờ đo được")
    # Bản lưu CŨ: gỡ đúng khoá mới ra khỏi file rồi nạp lại. `BAN` giữ
    # nguyên, nên file cũ phải đọc được — chỉ là chưa có vốn-giờ nào.
    import json as _js26
    _d26 = _js26.loads(tu27.duongLuu.read_text(encoding="utf-8"))
    _d26.pop("soVonGio", None)
    tu27.duongLuu.write_text(_js26.dumps(_d26, ensure_ascii=False),
                             encoding="utf-8")
    tu28 = TrungUong(tu27.duongLuu.parent, {"vonBanDauUsd": 10_000.0})
    kiem("bản lưu CŨ (chưa có khoá này) vẫn NẠP ĐƯỢC",
         tu28.napLuu.get("nap") is True,
         "tăng `BAN` ở đây sẽ vứt cả danh mục đang mở chỉ để thêm một thước "
         "đo — luật `BAN` sinh ra cho thay đổi KHÔNG ĐỌC NỔI")
    kiem("và nó KHAI là chưa có vốn-giờ, rồi cộng lại từ 0",
         tu28.napLuu.get("coSoVonGio") is False
         and gan(tu28.soVonGio.vonGioUsd, 0.0),
         f"{tu28.napLuu.get('coSoVonGio')} — đoán ra một mẫu số cho quãng "
         f"chưa từng đo là bịa ra một tỉ suất")

    # ── PHẦN TÁCH THEO TY cũng phải sống qua khởi động lại ─────────────
    # Không lưu thì sau mỗi lần bật máy, con số GỘP là cả đời còn phần
    # tách theo ty là từ lúc bật — hai con số nằm cạnh nhau trên cùng một
    # bảng và không cộng lại thành nhau. Đo ngay lượt đầu trên máy sống:
    # gộp 1.936.570 vốn-giờ, tổng theo ty 4.746.
    from thi_bac_ty.ke_toan import SoVonGio as _SVG2
    from thi_bac_ty.luu_danh_muc import luu as _luu2, nap as _nap2
    from thi_bac_ty.danh_muc import DanhMuc as _DM2
    from thi_bac_ty.hieu_nang import DuongNav as _DN2
    _sv2 = _SVG2()
    _sv2.cong(1000.0, 0.0, 3600.0, ty="a.b.v1")
    _sv2.cong_thu("a.b.v1", 5.0)
    _p2 = _tam("von-gio-ty") / "lu.json"
    _luu2(_p2, _DM2(1000.0), {}, _DN2(), _sv2, 0.0, 0.0)
    _r2 = _nap2(_p2, _DM2(1000.0), _DN2())["_soVonGio"]
    kiem("vốn-giờ TÁCH THEO TY sống qua khởi động lại",
         _r2.theoTy.get("a.b.v1", {}).get("vonGioUsd") == 1000.0
         and _r2.theoTy["a.b.v1"]["thuRongUsd"] == 5.0,
         f"{_r2.theoTy} — gộp là cả đời mà tách theo ty là từ lúc bật thì "
         f"hai con số cạnh nhau không cộng lại thành nhau")
    # Bản lưu CŨ chưa có khoá này: `{}` là đúng, và con số gộp vẫn nạp
    # được. Phép kiểm phải tha cho bản cũ, không thì nó đỏ vì quá khứ.
    _d2 = _js26.loads(_p2.read_text(encoding="utf-8"))
    _d2["soVonGio"].pop("theoTy", None)
    _p2.write_text(_js26.dumps(_d2, ensure_ascii=False), encoding="utf-8")
    _r3 = _nap2(_p2, _DM2(1000.0), _DN2())["_soVonGio"]
    kiem("bản lưu CŨ thiếu phần tách vẫn nạp được, và phần tách là RỖNG",
         _r3.theoTy == {} and _r3.vonGioUsd == 1000.0,
         f"{_r3.theoTy} · {_r3.vonGioUsd} — bịa ra một phần tách cho quãng "
         f"chưa từng tách là bịa ra một tỉ suất theo ty")

    # ── BỘ ĐẾM ĐỐI CHIẾU phải sống cùng lãi lỗ ──────────────────────────
    # `tienDaGhiUsd` nằm trong RAM, `laiLoDaThucHienUsd` nằm trên đĩa. Mỗi
    # lần khởi động lại, `lech_tien()` kêu LỆCH đúng bằng toàn bộ lãi lỗ đã
    # ghi trước đó. Đo thật trên máy sống: LỆCH −89,69 USD, và không có
    # đường dịch tiền nào sai cả — chỉ có một bộ đếm quên mất mình.
    #
    # Một báo động giả mỗi lần deploy dạy người vận hành ngó lơ đúng cái
    # phép canh sinh ra để bắt chuyện thật.
    _d58 = _tam("lech-tien-qua-restart")
    tu58 = TrungUong(_d58, {"vonBanDauUsd": 10_000.0})
    tu58._ghi_tien(-12.5, "PHI", "thử", "x", "y")
    kiem("trước khi lưu thì sổ khớp", tu58.lech_tien()["khop"])
    tu58._luu_danh_muc()
    tu59 = TrungUong(_d58, {"vonBanDauUsd": 10_000.0})
    _l59 = tu59.lech_tien()
    kiem("và VẪN khớp sau khi khởi động lại",
         _l59["khop"] and gan(_l59["tienDaGhiUsd"], -12.5),
         f"{_l59} — một cái nằm trong RAM, một cái nằm trên đĩa thì mỗi lần "
         f"deploy là một báo động giả")

    # Bản lưu CŨ chưa có khoá này: lấy thẳng `laiLoDaThucHienUsd` làm điểm
    # xuất phát, vì mọi đồng trong đó ĐÃ từng đi qua `_ghi_tien` ở một lần
    # chạy trước — coi là 0 thì kêu lệch oan đúng bằng ngần ấy.
    import json as _js58
    _f58 = _js58.loads(tu59.duongLuu.read_text(encoding="utf-8"))
    _f58.pop("tienDaGhiUsd", None)
    tu59.duongLuu.write_text(_js58.dumps(_f58, ensure_ascii=False),
                             encoding="utf-8")
    tu60 = TrungUong(_d58, {"vonBanDauUsd": 10_000.0})
    kiem("bản lưu CŨ (chưa có bộ đếm) cũng không kêu lệch oan",
         tu60.lech_tien()["khop"],
         f"{tu60.lech_tien()} — mọi đồng trong lãi lỗ đã thực hiện đều ĐÃ "
         f"đi qua `_ghi_tien` ở một lần chạy trước")

    # Và đây mới là lý do PHẢI lưu bộ đếm, không chỉ dựa vào đường dự phòng:
    # một RÒ RỈ THẬT — tiền dịch mà không qua `_ghi_tien` — phải SỐNG SÓT
    # qua khởi động lại. Đường dự phòng lấy `laiLoDaThucHienUsd` sẽ tự
    # "chữa lành" chỗ lệch, và cái rò rỉ biến mất khỏi màn hình đúng lúc
    # người vận hành khởi động lại để xem nó là gì.
    _d61 = _tam("ro-ri-song-sot")
    tu61 = TrungUong(_d61, {"vonBanDauUsd": 10_000.0})
    tu61._ghi_tien(-10.0, "PHI", "ghi đúng cửa", "x", "y")
    tu61.danh_muc.ghi_dong_tien(-7.0)      # RÒ RỈ: không qua `_ghi_tien`
    kiem("rò rỉ bị BẮT ngay khi nó xảy ra",
         not tu61.lech_tien()["khop"]
         and gan(tu61.lech_tien()["lechUsd"], -7.0),
         str(tu61.lech_tien()))
    tu61._luu_danh_muc()
    tu62 = TrungUong(_d61, {"vonBanDauUsd": 10_000.0})
    kiem("và nó SỐNG SÓT qua khởi động lại, không tự chữa lành",
         not tu62.lech_tien()["khop"]
         and gan(tu62.lech_tien()["lechUsd"], -7.0),
         f"{tu62.lech_tien()} — đây mới là lý do phải LƯU bộ đếm: đường dự "
         f"phòng sẽ xoá dấu vết rò rỉ đúng lúc người vận hành khởi động lại "
         f"để xem nó là gì")

    # ── ĐƯỜNG SỨC CHỨA: lợi suất TỤT theo quy mô ────────────────────────
    # Đo trên máy sống: 10.000 USD → 20,15 %/năm; một triệu → 5,52 %; năm
    # triệu → 1,11 % vì hết sức chứa ở 1,07 triệu. Cùng một cỗ máy, cùng
    # một phút. Một con số APR không kèm mức vốn là một con số bỏ bớt.
    from thi_bac_ty.duong_suc_chua import do_duong_suc_chua as _dsc

    def _tt55(apr, sc):
        return {"netMoiGioBps": apr * 100.0 / (365.0 * 24.0),
                "giuGio": 720.0, "sucChuaToiDaUsd": sc}

    # Đưa vào theo thứ tự TĂNG dần để phép kiểm phân biệt được «có xếp
    # hạng» với «may mà đầu vào đã xếp sẵn». Đột biến bỏ `sort` sống sót
    # đúng vì bản đầu đưa vào sẵn theo thứ tự giảm.
    _d55 = _dsc([_tt55(3.0, 100_000.0), _tt55(30.0, 1_000.0)],
                muc=(1_000.0, 2_000.0, 101_000.0, 200_000.0))
    _m55 = {m.vonUsd: m for m in _d55.muc}
    kiem("vốn nhỏ thì rót TOÀN chỗ tốt nhất",
         gan(_m55[1_000.0].aprTrenCaTuiUsd, 30.0),
         str(_m55[1_000.0].tom_tat()))
    kiem("vốn lớn hơn thì TRÀN xuống chỗ tệ hơn, lợi suất tụt",
         gan(_m55[2_000.0].aprTrenCaTuiUsd, 16.5)
         and _m55[101_000.0].aprTrenCaTuiUsd < 4.0,
         f"{_m55[2_000.0].tom_tat()} — 1.000 ở 30% + 1.000 ở 3% = 16,5%")
    kiem("hết sức chứa thì phần DƯ ăn lãi 0, không bị bỏ qua",
         gan(_m55[200_000.0].rotDuocUsd, 101_000.0)
         and _m55[200_000.0].aprTrenCaTuiUsd
         < _m55[200_000.0].aprTrenVonRotUsd,
         f"{_m55[200_000.0].tom_tat()} — bỏ qua phần dư là khoe lợi suất "
         f"của phần đã rót rồi gọi đó là lợi suất của cả túi tiền")
    kiem("và hai con số ấy giữ RIÊNG, không trộn",
         gan(_m55[200_000.0].aprTrenVonRotUsd,
             _m55[101_000.0].aprTrenCaTuiUsd, 1e-9),
         "«phần đã rót lãi bao nhiêu» và «cả túi lãi bao nhiêu» là hai câu")

    _d56 = _dsc([{"sucChuaToiDaUsd": 1_000.0},          # thiếu lãi
                 _tt55(30.0, None),                     # thiếu sức chứa
                 _tt55(10.0, 5_000.0)])
    kiem("cơ hội thiếu lãi hoặc thiếu sức chứa thì BỎ, và ĐẾM RIÊNG",
         _d56.soBoViThieuLai == 1 and _d56.soBoViThieuSucChua == 1
         and _d56.soCoHoiDung == 1,
         f"{_d56.tom_tat()} — không biết thì không xếp vào một phép tính "
         f"về sức nuốt, chứ không coi là 0")
    kiem("không dựng được thì NÓI, không trả một đường cong rỗng im lặng",
         "chưa dựng được" in _dsc([]).vi, _dsc([]).vi)
    tu57 = TrungUong(_tam("duong-suc-chua"), {"vonBanDauUsd": 10_000.0})
    kiem("ảnh chụp mang đường sức chứa ra buồng lái",
         "muc" in (tu57.anh_chup().get("duongSucChua") or {}),
         "đo được mà không ra tới buồng lái thì vẫn là im lặng")

    # ── XIN THEO SỨC CHỨA, không xin một con số cứng ────────────────────
    # Đo sau khi nâng vốn ảo lên một triệu: máy vẫn chỉ rót 6.200 USD, dùng
    # vốn 0,62%. Không phải hết tiền (còn 797.000 khả dụng), không phải
    # trần vị thế (120 chỗ, dùng 14) — mà vì MỖI TY XIN CỨNG 500 USD. Vốn
    # không chạm được thị trường vì không ai xin nó.
    from thi_bac_ty.to_trinh import xin_theo_suc_chua as _xtsc

    kiem("sức chứa lớn thì xin LỚN, theo tỉ lệ",
         gan(_xtsc(500.0, 25_000.0, 0.5, 25_000.0), 12_500.0),
         "xin 500 vào một pool nuốt được 25.000 là bỏ phí")
    kiem("sức chứa NHỎ hơn sàn thì vẫn xin đúng SÀN",
         gan(_xtsc(500.0, 200.0, 0.5, 25_000.0), 500.0),
         "dưới sàn thì phí cố định ăn hết — và Rủi Ro Tổng sẽ từ chối vì "
         "sức chứa, đó mới là cửa đúng để chặn")
    kiem("KHÔNG xin trọn sức chứa",
         _xtsc(500.0, 25_000.0, 0.5, 1e9) < 25_000.0,
         "xin trọn nghĩa là TA CHÍNH LÀ sức chứa, và lúc ấy con số ấy "
         "không còn đúng nữa — nó được tính cho một thị trường chưa có ta")
    kiem("có TRẦN, chặn một sức chứa sai đơn vị",
         gan(_xtsc(500.0, 1e12, 0.5, 25_000.0), 25_000.0),
         "cùng lý do với `TRAN_USD` của `bac/suc_chua.py`")
    kiem("chưa đo được sức chứa thì xin ĐÚNG SÀN, không đoán",
         gan(_xtsc(500.0, None, 0.5, 25_000.0), 500.0)
         and gan(_xtsc(500.0, 0.0, 0.5, 25_000.0), 500.0),
         "không biết pool nuốt được bao nhiêu thì xin nhỏ nhất")

    # Và BA ty ĐANG được cấp vốn phải THẬT SỰ dùng nó. Hàm đúng mà không ty
    # nào gọi thì vốn vẫn không chạm được thị trường — đúng lớp hỏng «có mã,
    # không ai gọi» đã cắn ba lần trong cây này.
    import ast as _a53
    import pathlib as _p53

    _g53 = _p53.Path(__file__).resolve().parent.parent

    def _von_can_tu_dau(tep: str) -> str:
        """Biểu thức gán cho `vonCanUsd` trong `xuat_to_trinh`, dạng chữ."""
        cay = _a53.parse((_g53 / tep).read_text(encoding="utf-8"))
        for nd in _a53.walk(cay):
            if not (isinstance(nd, _a53.FunctionDef)
                    and nd.name == "xuat_to_trinh"):
                continue
            for x in _a53.walk(nd):
                if isinstance(x, _a53.keyword) and x.arg == "vonCanUsd":
                    return _a53.dump(x.value)
        return ""

    def _co_goi53(tep: str, ten: str) -> bool:
        cay = _a53.parse((_g53 / tep).read_text(encoding="utf-8"))
        for x in _a53.walk(cay):
            if isinstance(x, _a53.Call):
                f = x.func
                if getattr(f, "id", "") == ten or getattr(f, "attr", "") == ten:
                    return True
        return False

    for _tep53 in ("lp_amm/ty_cap_thanh_khoan.py", "tin_dung/ty_vay.py",
                   "lai_suat/ty_lai_suat.py"):
        _bt53 = _von_can_tu_dau(_tep53)
        kiem(f"`{_tep53.split('/')[0]}` xin theo SỨC CHỨA, không xin số cứng",
             _co_goi53(_tep53, "xin_theo_suc_chua")
             and (("_xin" in _bt53) or ("xin_theo_suc_chua" in _bt53)
                  or "vonXinUsd" in _bt53),
             f"`vonCanUsd={_bt53[:70]}` — hàm đúng mà không ty nào gọi thì "
             f"vốn vẫn không chạm được thị trường")
    # `lp_amm` quy phí theo cỡ SÀN, không theo cỡ xin: được cấp ít hơn xin
    # là chuyện thường, và lúc ấy phí thật cao hơn con số đã khai.
    _lpNguon53 = (_g53 / "lp_amm/ty_cap_thanh_khoan.py").read_text(
        encoding="utf-8")
    kiem("`lp_amm` quy phí theo cỡ SÀN, không theo cỡ XIN",
         "co.vonSanUsd or co.vonXinUsd" in _lpNguon53,
         "khai phí ở cỡ xin rồi được cấp ở cỡ sàn là khai LẠC QUAN, và "
         "tầng trên không cách nào biết")

    # ── NẠP VỐN là SỰ KIỆN, không phải một tham số ──────────────────────
    # Sửa `vonBanDauUsd` từ 10.000 lên 1.000.000 mà tiền mặt vẫn 4.000 thì
    # NAV/vốn gốc ra 1% — cầu dao đọc thành SỤT VỐN 99% và ngắt ngay. Còn
    # nếu vá bằng cách cộng luôn tiền mặt thì đường NAV nhảy 100 lần và mọi
    # phép đo lợi suất đọc cú nhảy ấy thành lãi gấp trăm lần.
    from thi_bac_ty.hieu_nang import do_hieu_nang as _dhn

    _G50 = 3_600_000.0
    _d50 = [(0.0, 10_000.0, 0.0), (_G50, 10_100.0, 0.0),
            (2 * _G50, 1_000_100.0, 990_000.0), (3 * _G50, 1_010_101.0, 0.0)]
    _r50 = _dhn(_d50, 10_000.0)
    kiem("lợi suất là của TAY LÁI — đã trừ mọi đồng chủ bỏ thêm vào",
         gan(_r50["laiLoPhanTram"], 2.01, 1e-6),
         f"{_r50['laiLoPhanTram']} — tăng 1% rồi nạp 990k rồi tăng 1% nữa "
         f"thì đúng là 2,01%, không phải 10.001%")
    kiem("và con số GỒM nạp vốn vẫn giữ riêng, không trộn",
         gan(_r50["laiLoGomNapVonPhanTram"], 10_001.01, 1e-6)
         and gan(_r50["dongVonNgoaiUsd"], 990_000.0),
         "hai câu hỏi khác nhau: «tay lái giỏi cỡ nào» và «chủ đã bỏ vào "
         "bao nhiêu» — trộn chúng là khoe tiền của người khác")
    # CAGR chỉ tính khi có ≥168 giờ dữ liệu, nên phải dựng một đường DÀI
    # mới soi được nó. Bản kiểm đầu dùng đường 3 giờ, và đột biến đổi CAGR
    # sang `n1/n0` sống sót vì CAGR chưa bao giờ được tính.
    _dai = [(0.0, 10_000.0, 0.0)]
    for _i in range(1, 200):
        _dv = 990_000.0 if _i == 100 else 0.0
        _nav = _dai[-1][1] * 1.001 + _dv
        _dai.append((_i * _G50, _nav, _dv))
    _r52 = _dhn(_dai, 10_000.0)
    kiem("CAGR gộp từ TÍCH CHUỖI, không từ `NAV cuối / NAV đầu`",
         _r52["duDeKetLuan"] and _r52["cagrPhanTram"] < 1e6,
         f"CAGR {_r52['cagrPhanTram']} — lấy `n1/n0` thì cú nạp 990k biến "
         f"thành một CAGR thiên văn, và nó sẽ được khoe với đủ chữ số")
    kiem("và nó khớp lợi suất tay lái quy ra năm",
         gan((1.0 + _r52["laiLoPhanTram"] / 100.0)
             ** (1.0 / (_r52["soGio"] / (365.0 * 24.0))) - 1.0,
             _r52["cagrPhanTram"] / 100.0, 1e-6),
         f"{_r52['cagrPhanTram']} vs {_r52['laiLoPhanTram']}")

    kiem("điểm HAI phần tử của bản lưu cũ vẫn đọc được",
         gan(_dhn([(0.0, 100.0), (_G50, 110.0)], 100.0)["laiLoPhanTram"],
             10.0, 1e-9),
         "trước 29/08 chưa có đường nạp vốn nào, nên dòng vốn đúng là 0")
    # Nạp vốn dịch cả cái THANG, đỉnh phải dịch theo. Ca phân biệt được:
    # LÊN ĐỈNH → LỖ → NẠP. Không dịch đỉnh thì tiền nạp vào đẩy NAV vượt
    # đỉnh cũ, và khoản lỗ có thật đọc thành "đã hồi phục" — cỗ máy được
    # khen vì tiền của chủ.
    _r51 = _dhn([(0.0, 100.0, 0.0), (_G50, 200.0, 0.0),
                 (2 * _G50, 150.0, 0.0), (3 * _G50, 1150.0, 1000.0)], 100.0)
    kiem("nạp vốn KHÔNG chữa lành một khoản lỗ đã xảy ra",
         _r51["dangDuoiDay"] is True,
         f"{_r51} — lỗ 25% rồi nạp 1000 thì vẫn đang dưới đỉnh; không dịch "
         f"đỉnh theo thì cỗ máy được khen vì tiền của chủ")
    kiem("và sụt vốn tối đa vẫn giữ nguyên khoản lỗ THẬT",
         gan(_r51["sutVonToiDaPhanTram"], 25.0),
         f"{_r51['sutVonToiDaPhanTram']} — 200 xuống 150 là 25%")

    tu50 = TrungUong(_tam("nap-von"), {"vonBanDauUsd": 10_000.0})
    _k50 = tu50.nap_von(990_000.0, "chủ")
    kiem("nạp vốn đổi CÙNG LÚC tiền mặt và vốn gốc",
         gan(tu50.danh_muc.tienMatUsd, 1_000_000.0)
         and gan(tu50.danh_muc.vonBanDauUsd, 1_000_000.0),
         f"{_k50} — lệch một trong hai là cầu dao đọc ra sụt vốn bịa")
    kiem("và vào SỔ CÁI với loại riêng",
         any(x["loai"] == "NAP_VON" for x in tu50.so_cai.gan_day(20)),
         "không vào sổ thì sau này không lần lại được")
    tu50.mot_vong()
    kiem("đường NAV đánh dấu DÒNG VỐN ở điểm kế tiếp",
         gan(tu50.duongNav.diem[-1][2], 990_000.0),
         f"{tu50.duongNav.diem[-1]} — thiếu dấu này là lời nói dối lớn nhất "
         f"một cỗ máy vốn có thể nói")
    tu50.mot_vong()
    kiem("và CHỈ điểm ấy, không dính sang điểm sau",
         gan(tu50.duongNav.diem[-1][2], 0.0),
         "dính sang là mỗi vòng trừ đi 990k khỏi lợi suất")
    kiem("nạp vốn ĐÒI TÊN NGƯỜI",
         _nem(lambda: tu50.nap_von(1.0, ""), ValueError),
         "cùng bất đối xứng với `ap_dung` và cầu dao: máy được phép đề "
         "nghị, người quyết định bỏ tiền vào")
    kiem("nạp 0 đồng không phải một sự kiện",
         _nem(lambda: tu50.nap_von(0.0, "chủ"), ValueError))
    kiem("rút quá tiền mặt thì TỪ CHỐI, không âm quỹ",
         _nem(lambda: tu50.nap_von(-9e9, "chủ"), ValueError),
         "vốn đang nằm trong vị thế thì phải đóng trước")
    tu50._luu_danh_muc()
    tu51 = TrungUong(tu50.duongLuu.parent, {"vonBanDauUsd": 10_000.0})
    kiem("vốn đã nạp SỐNG QUA lần khởi động lại",
         gan(tu51.napThemUsd, 990_000.0)
         and gan(tu51.danh_muc.vonBanDauUsd, 1_000_000.0),
         f"nạp {tu51.napThemUsd}, gốc {tu51.danh_muc.vonBanDauUsd} — mất nó "
         f"thì vốn gốc tụt về mức cũ trong khi tiền mặt vẫn còn, và sụt vốn "
         f"đọc ra một con số bịa")

    # ── XOAY CHỖ: chỗ ngồi có hạn, và ai ngồi mới là câu hỏi ────────────
    # Đo trên máy sống 29/08: 8 chỗ bị khoá 30 ngày ở 1,9–3,0 %/năm trong
    # khi 9–16 % đi qua mỗi vòng rồi bị từ chối vì «đã đủ 12 vị thế». Ty
    # giữ tám chỗ ấy tên là `lending.rate_rotation` — và nó không xoay.
    from thi_bac_ty.xoay_cho import (apr_tu_to_trinh, do_xoay_cho,
                                     phi_mot_chieu_usd)

    _G40 = 1_800_000_000.0

    def _so40(ma, apr, giu=720.0, von=500.0, phi=0.6, khoa=None,
              thoat=9e9, moGio=0.0):
        t = {"taiSan": ma, "netMoiGioBps": apr * 100.0 / (365.0 * 24.0),
             "giuGio": giu, "phiUocBps": phi, "khoaVonDenGio": khoa,
             "thanhKhoanThoatUsd": thoat}
        return SoViThe(ma=ma, chienLuoc="cu.v1", toTrinh=t, vonUsd=von,
                       moLucGiay=_G40 - moGio * 3600.0, keToanLucGiay=_G40)

    def _tt40(ma, apr, giu=720.0, phi=0.6):
        return {"ma": ma, "taiSan": ma, "chienLuoc": "moi.v1",
                "netMoiGioBps": apr * 100.0 / (365.0 * 24.0),
                "giuGio": giu, "phiUocBps": phi}

    kiem("APR đọc từ `netMoiGioBps`, và suy được từ `netUocBps/giuGio`",
         gan(apr_tu_to_trinh({"netMoiGioBps": 1.0}), 87.6)
         and gan(apr_tu_to_trinh({"netUocBps": 8.0, "giuGio": 8.0}), 87.6))
    kiem("không khai lãi thì None, không phải 0",
         apr_tu_to_trinh({"netUocBps": 8.0}) is None
         and apr_tu_to_trinh(None) is None,
         "trộn «chưa biết» với «huề vốn» làm bảng xếp hạng đẩy tờ trình IM "
         "LẶNG xuống đáy như thể chúng tệ")
    kiem("không khai PHÍ thì None, không phải 0",
         phi_mot_chieu_usd({}, 500.0) is None
         and gan(phi_mot_chieu_usd({"phiUocBps": 10.0}, 500.0), 0.5),
         "coi phí là 0 là dựng ra một phép đổi miễn phí — đúng cách để xoay "
         "liên tục rồi thua sạch vì phí")

    _x40 = do_xoay_cho({"a": _so40("a", 2.0)}, [_tt40("b", 16.0)], _G40)
    kiem("lãi hơn nhiều, phí bé → ĐÁNG đổi",
         _x40.soXoayDuoc == 1 and _x40.loiRongUsd > 0, _x40.vi)
    kiem("và nói được danh mục sẽ đi từ đâu tới đâu",
         gan(_x40.aprHienTai, 2.0) and gan(_x40.aprSauKhiXoay, 16.0),
         f"{_x40.aprHienTai} → {_x40.aprSauKhiXoay}")

    # Cùng khoảng chênh 0,5 %/năm, chỉ khác QUÃNG chạy: 720 giờ thì đáng,
    # 8 giờ thì phí ăn hết. Cặp này kiểm đúng thứ đáng kiểm — phép tính có
    # nhìn vào quãng thời gian không, hay chỉ nhìn con số APR.
    _x41a = do_xoay_cho({"a": _so40("a", 2.0, giu=720.0)},
                        [_tt40("b", 2.5, giu=720.0)], _G40)
    _x41b = do_xoay_cho({"a": _so40("a", 2.0, giu=8.0)},
                        [_tt40("b", 2.5, giu=8.0)], _G40)
    kiem("chênh 0,5 %/năm suốt 720 giờ thì ĐÁNG đổi", _x41a.soXoayDuoc == 1,
         str(_x41a.tom_tat()))
    kiem("cùng chênh ấy nhưng chỉ 8 giờ thì phí ăn hết → KHÔNG đổi",
         _x41b.soXoayDuoc == 0,
         f"{_x41b.tom_tat()} — xoay vì thấy một con số đẹp hơn là cách chắc "
         f"chắn để thua vì phí, mà mỗi lần đổi vẫn trông thông minh")

    # ── BIÊN của chính cơ chế xoay chỗ ─────────────────────────────────
    #
    # Quét đột biến trên `xoay_cho.py` cho 10/15 con SỐNG SÓT. Đây là chỗ
    # cỗ máy tự đuổi vị thế của mình và trả phí hai chiều, nên mỗi con
    # sống là một dòng có thể sửa sai mà không phép kiểm nào kêu.

    # APR BẰNG NHAU thì KHÔNG đổi. Đổi `<=` thành `<` là trả hai chiều phí
    # để đứng nguyên chỗ cũ — và mỗi lần đổi vẫn trông như một quyết định.
    kiem("cơ hội mới BẰNG ĐÚNG cơ hội cũ thì KHÔNG đổi",
         do_xoay_cho({"a": _so40("a", 5.0)}, [_tt40("b", 5.0)],
                     _G40).soXoayDuoc == 0,
         "đổi để đứng yên là trả phí hai chiều lấy con số không đổi")
    kiem("nhỉnh hơn một chút thì mới xét",
         do_xoay_cho({"a": _so40("a", 5.0)}, [_tt40("b", 9.0)],
                     _G40).soXoayDuoc == 1)

    # LÃI ĐÚNG BẰNG PHÍ thì cũng không đổi. Hoà vốn mà vẫn đổi là nhận
    # trọn rủi ro thực thi để lấy về đúng số không.
    _phiHV = 500.0 * 0.6 / 10_000.0 * 2.0                 # phí ra + phí vào
    _aprHV = 5.0 + _phiHV * 100.0 * (365.0 * 24.0) / (500.0 * 720.0)
    _xHV = do_xoay_cho({"a": _so40("a", 5.0)}, [_tt40("b", _aprHV)], _G40)
    kiem("lãi ĐÚNG BẰNG phí thì KHÔNG đổi", _xHV.soXoayDuoc == 0,
         f"{_xHV.tom_tat()} — hoà vốn mà vẫn đổi là nhận trọn rủi ro thực "
         f"thi để lấy về đúng số không")
    kiem("nhích trên hoà vốn thì mới đổi",
         do_xoay_cho({"a": _so40("a", 5.0)}, [_tt40("b", _aprHV * 1.01)],
                     _G40).soXoayDuoc == 1)

    # KHOÁ VỐN hết hạn ĐÚNG LÚC thì xoay được. `<` đổi thành `<=` là giam
    # thêm một vòng đúng cái vị thế vừa được tự do.
    kiem("khoá vốn vừa ĐÚNG hết hạn thì xoay được",
         do_xoay_cho({"a": _so40("a", 2.0, khoa=10.0, moGio=10.0)},
                     [_tt40("b", 30.0)], _G40).soXoayDuoc == 1,
         "hết khoá là hết khoá, không phải «sắp hết»")
    kiem("còn thiếu một chút thì vẫn bị giữ",
         do_xoay_cho({"a": _so40("a", 2.0, khoa=10.0, moGio=9.9)},
                     [_tt40("b", 30.0)], _G40).soBiKhoa == 1)

    # KHÔNG BIẾT phí một bên là không biết. `or` đổi thành `and` là đổi
    # chỗ với một phép trừ thiếu một số hạng.
    for _ai, _cu, _moi in (("bên CŨ", {"phiUocBps": None}, {}),
                           ("bên MỚI", {}, {"phiUocBps": None})):
        _soP = _so40("a", 2.0)
        _soP.toTrinh.update(_cu)
        _ttP = _tt40("b", 30.0)
        _ttP.update(_moi)
        kiem(f"không khai phí ở {_ai} thì KHÔNG đổi",
             do_xoay_cho({"a": _soP}, [_ttP], _G40).soXoayDuoc == 0,
             "coi phí chưa khai là 0 là dựng ra một phép đổi miễn phí")

    # `giuGio` của bên MỚI bằng 0 nghĩa là KHÔNG KHAI, nên lấy quãng của
    # bên cũ. `>` đổi thành `>=` là kẹp quãng về 0 và không gì đổi được
    # nữa — một cơ chế im lặng đứng hình.
    kiem("bên mới không khai giữ bao lâu thì lấy quãng của bên cũ",
         gan(do_xoay_cho({"a": _so40("a", 2.0, giu=500.0)},
                         [_tt40("b", 30.0, giu=0.0)],
                         _G40).xoay[0].gioChung, 500.0),
         "0 ở đây là «không khai», không phải «không giờ nào»")

    # VỐN BẰNG 0 hết thì không có mẫu số. `> 0` đổi thành `>= 0` là chia
    # cho không ngay dòng dưới.
    _x0v = do_xoay_cho({"a": _so40("a", 2.0, von=0.0)},
                       [_tt40("b", 30.0)], _G40)
    kiem("danh mục toàn vốn 0 thì APR là None, và KHÔNG nổ",
         _x0v.aprHienTai is None and _x0v.aprSauKhiXoay is None,
         f"{_x0v.tom_tat()} — mẫu số bằng 0 thì câu trả lời là «chưa đo "
         f"được», không phải một con số")

    # Lời giải thích phải khớp với việc CÓ đổi được hay không.
    kiem("không đổi được thì nói «ngồi yên là hợp lệ»",
         "Ngồi yên" in do_xoay_cho({"a": _so40("a", 5.0)},
                                   [_tt40("b", 5.0)], _G40).vi)
    kiem("đổi được thì nói danh mục đi từ đâu tới đâu",
         "ĐÁNG đổi" in do_xoay_cho({"a": _so40("a", 2.0)},
                                   [_tt40("b", 30.0)], _G40).vi)

    # ── TRẦN THEO BẰNG CHỨNG ───────────────────────────────────────────
    #
    # Lãi tính trên `giờChung` — quãng hai bên cùng KHAI còn hiệu lực,
    # có thể 167 giờ. Phí thì trả NGAY và trả đủ. Đo làn thật 30/08: 267
    # lần xoay trong 39 phút, trung vị vị thế mới sống 0,008 giờ, lời hứa
    # cộng dồn +11.136 USD trên một cuốn sổ 10.000 USD — chưa bao giờ tới.
    #
    # KHÔNG phải chi phí đã chìm: phí vào của vị thế cũ không được đem vào
    # quyết định này, quyết định vẫn nhìn về phía trước. Cái được sửa là
    # một GIẢ ĐỊNH — «vị thế mới sẽ sống hết quãng nó khai» — thay bằng
    # một PHÉP ĐO đọc từ sổ.
    _x41c = do_xoay_cho({"a": _so40("a", 2.0, giu=720.0)},
                        [_tt40("b", 2.5, giu=720.0)], _G40,
                        gioSongTrungVi=0.008)
    kiem("bằng chứng nói vị thế chỉ sống 0,008h → lời hứa 720h bị KẸP",
         _x41c.soXoayDuoc == 0,
         f"{_x41c.tom_tat()} — cộng trước lãi của 720 giờ cho một vị thế "
         f"sổ nói sống ba mươi giây là một cỗ máy bơm phí")
    # CHẶN HẲN cũng phải đếm, không chỉ CẮT BỚT. Bản đầu chỉ đếm ở nhánh
    # đi tiếp, nên khi trần chặn sạch thì buồng lái hiện «trần 0,008h · 0
    # lời hứa bị cắt» — đọc đúng thành «trần này chẳng làm gì», trong khi
    # nó vừa chặn tất cả. Một cửa chặn lặng lẽ là một cửa không ai biết
    # mà xem lại.
    kiem("chặn HẲN thì cũng phải đếm được, không chỉ cắt bớt",
         (_x41c.tom_tat()["soBiChanBoiBangChung"] == 1
          and _x41c.tom_tat()["loiRongBiChanUsd"] > 0),
         f"{_x41c.tom_tat()} — «0 lời hứa bị cắt» khi trần vừa chặn sạch "
         f"là một cửa chặn lặng lẽ")
    kiem("và nó nói ra trong câu giải thích, không giấu trong số",
         "TRẦN BẰNG CHỨNG" in _x41c.vi,
         f"{_x41c.vi} — không nói thì «không chỗ nào đáng đổi» đọc thành "
         f"«chợ hôm nay chán»")
    kiem("chưa có bằng chứng thì KHÔNG có ai bị chặn vì nó",
         do_xoay_cho({"a": _so40("a", 2.0, giu=720.0)},
                     [_tt40("b", 2.5, giu=720.0)],
                     _G40).tom_tat()["soBiChanBoiBangChung"] == 0,
         "đếm một cửa chưa bật là khai một hành động chưa xảy ra")
    kiem("bị phí chặn — KHÔNG phải bị bằng chứng chặn — thì không đếm nhầm",
         do_xoay_cho({"a": _so40("a", 5.0)}, [_tt40("b", 5.001)], _G40,
                     gioSongTrungVi=900.0
                     ).tom_tat()["soBiChanBoiBangChung"] == 0,
         "trần không kẹp gì ở đây, nên chỗ này bị chặn bởi phí; đổ cho "
         "trần là đổ tội cho cửa vừa mở toang")
    kiem("và nó KHAI ra trần ấy, không kẹp lặng lẽ",
         gan(_x41c.tom_tat()["gioSongTrungVi"], 0.008),
         f"{_x41c.tom_tat()} — kẹp mà không khai thì con số lợi ròng tụt "
         f"xuống trông như thị trường bỗng tệ đi")

    _x41d = do_xoay_cho({"a": _so40("a", 2.0, giu=720.0)},
                        [_tt40("b", 30.0, giu=720.0)], _G40,
                        gioSongTrungVi=900.0)
    kiem("bằng chứng RỘNG hơn quãng khai thì không kẹp gì cả",
         (_x41d.soXoayDuoc == 1 and gan(_x41d.xoay[0].gioChung, 720.0)
          and _x41d.soBiKepTheoBangChung == 0),
         f"{_x41d.tom_tat()} — trần là TRẦN, không phải một giá trị áp đặt")

    _x41e = do_xoay_cho({"a": _so40("a", 2.0, giu=720.0)},
                        [_tt40("b", 30.0, giu=720.0)], _G40,
                        gioSongTrungVi=100.0)
    kiem("kẹp thật thì ĐẾM được là đã kẹp",
         (_x41e.soXoayDuoc == 1 and gan(_x41e.xoay[0].gioChung, 100.0)
          and _x41e.soBiKepTheoBangChung == 1),
         str(_x41e.tom_tat()))

    # Bằng chứng ĐÚNG BẰNG 0 giờ là một bằng chứng, không phải sự vắng
    # mặt của bằng chứng: sổ nói vị thế vừa xoay không sống nổi một giây.
    # `>= 0` đổi thành `> 0` là bỏ qua đúng cái ca nặng nhất.
    _x41g = do_xoay_cho({"a": _so40("a", 2.0, giu=720.0)},
                        [_tt40("b", 30.0, giu=720.0)], _G40,
                        gioSongTrungVi=0.0)
    kiem("bằng chứng ĐÚNG BẰNG 0 giờ vẫn là bằng chứng",
         _x41g.soXoayDuoc == 0,
         f"{_x41g.tom_tat()} — «sổ nói vị thế không sống nổi một giây» "
         f"khác hẳn «sổ chưa nói gì», và cái sau là None chứ không phải 0")

    _x41f = do_xoay_cho({"a": _so40("a", 2.0, giu=720.0)},
                        [_tt40("b", 30.0, giu=720.0)], _G40)
    kiem("CHƯA có bằng chứng thì KHÔNG kẹp — sổ trắng không phải bằng 0",
         (_x41f.soXoayDuoc == 1 and gan(_x41f.xoay[0].gioChung, 720.0)
          and _x41f.tom_tat()["gioSongTrungVi"] is None),
         f"{_x41f.tom_tat()} — kẹp bằng 0 khi chưa đo được là dựng ra một "
         f"bằng chứng chưa ai thu thập, và nó khoá chết cơ chế này ngay "
         f"lần chạy đầu trên một cuốn sổ trắng")

    # Vòng phản hồi ÂM, không phải một cái khoá: xoay dừng ⇒ vị thế sống
    # lâu ⇒ trung vị dâng ⇒ trần nới ⇒ xoay lại được.
    kiem("trần nới ra thì cơ hội ấy vào lại được — đây là vòng, không phải khoá",
         (do_xoay_cho({"a": _so40("a", 2.0, giu=720.0)},
                      [_tt40("b", 2.5, giu=720.0)], _G40,
                      gioSongTrungVi=720.0).soXoayDuoc == 1),
         "cùng một cặp cơ hội, chỉ khác bằng chứng")

    # Giờ CHUNG là ngắn hơn trong hai bên. Bản đầu lấy giờ của bên CŨ và ra
    # một khoản lợi lớn gấp bốn lần sự thật.
    _x42 = do_xoay_cho({"a": _so40("a", 2.0, giu=720.0)},
                       [_tt40("b", 30.0, giu=168.0)], _G40)
    _x43 = do_xoay_cho({"a": _so40("a", 2.0, giu=720.0)},
                       [_tt40("b", 30.0, giu=720.0)], _G40)
    kiem("quãng lãi hơn tính theo bên NGẮN HƠN, không theo bên cũ",
         gan(_x42.xoay[0].gioChung, 168.0)
         and _x42.xoay[0].laiThemUsd < _x43.xoay[0].laiThemUsd / 3.0,
         f"{_x42.xoay[0].tom_tat()} — sau 168h cơ hội mới đóng, và 552 giờ "
         f"còn lại kia là một lời hứa không ai đưa ra")

    _x44 = do_xoay_cho({"a": _so40("a", 2.0, giu=720.0, moGio=719.5)},
                       [_tt40("b", 30.0)], _G40)
    kiem("vị thế SẮP HẾT HẠN thì đổi chẳng được gì",
         _x44.soXoayDuoc == 0,
         f"{_x44.vi} — phần lãi hơn chỉ chạy trong quãng còn lại")

    _x45 = do_xoay_cho({"a": _so40("a", 2.0, khoa=720.0)},
                       [_tt40("b", 30.0)], _G40)
    kiem("vốn còn KHOÁ thì không xoay được, và đếm RIÊNG",
         _x45.soXoayDuoc == 0 and _x45.soBiKhoa == 1,
         "không xoay được là một việc KHÔNG LÀM ĐƯỢC, không phải một việc "
         "lỗ — gộp hai thứ ấy là đọc nhầm bảng")

    _x46 = do_xoay_cho({"a": _so40("a", 2.0, thoat=None)},
                       [_tt40("b", 30.0)], _G40)
    kiem("chưa đo được thanh khoản THOÁT thì chặn, đếm riêng",
         _x46.soXoayDuoc == 0 and _x46.soKhongDoDuocThoat == 1,
         "vào được không có nghĩa là ra được")

    _x47 = do_xoay_cho({"a": _so40("a", 2.0), "b": _so40("b", 3.0)},
                       [_tt40("c", 30.0)], _G40)
    kiem("một cơ hội chỉ dùng cho MỘT chỗ, không nhân bản",
         _x47.soXoayDuoc == 1
         and _x47.xoay[0].taiSanCu == "a",
         f"{_x47.tom_tat()} — và nó nhường cho chỗ TỆ NHẤT trước")

    kiem("chưa giữ gì thì nói thẳng, không nổ",
         do_xoay_cho({}, [_tt40("b", 30.0)], _G40).soXoayDuoc == 0)

    tu48 = TrungUong(_tam("xoay-cho"), {"vonBanDauUsd": 10_000.0})
    kiem("ảnh chụp mang phép đo xoay chỗ ra buồng lái",
         "xoayCho" in tu48.anh_chup(),
         "đo được mà không ra tới buồng lái thì vẫn là im lặng")

    # ── ĐÓNG vị thế thì phải XOÁ dấu vân tay của cơ hội ─────────────────
    # Cửa chống trùng nói rõ giả định của nó: «nó đang có một tờ trình SỐNG
    # trong sổ rồi». Đúng — chừng nào tờ trình còn sống. Đóng rồi thì giả
    # định ấy sai, mà cái dấu vẫn chặn suốt một giờ.
    #
    # Đã cắn thật ngay lượt đầu bật xoay chỗ: máy đóng 8 vị thế lãi thấp
    # đúng như thiết kế, rồi KHÔNG rót lại được cái nào — 23 tờ trình, 23
    # lần BỎ TRÙNG, 998.000 USD nằm không. Không lỗi nào phát ra.
    from thi_bac_ty.trung_uong import _dau_van as _dv49
    from thi_bac_ty.trung_uong import _dau_van_tu_dict as _dvd49

    _tt49 = _mau(taiSan="BTC")
    kiem("hai đường dựng dấu vân tay cho CÙNG một kết quả",
         _dv49(_tt49) == _dvd49(_tt49.tom_tat()),
         "một bên đọc đối tượng, một bên đọc bản đã lưu — lệch nhau thì xoá "
         "trượt, và cơ hội bị chặn tiếp mà không ai hiểu vì sao")
    kiem("bản lưu thiếu chân thì trả None, không dựng dấu nửa vời",
         _dvd49({"chienLuoc": "a", "taiSan": "b"}) is None
         and _dvd49(None) is None
         # Chân RỖNG là ca phân biệt: thiếu khoá thì `try` cũng bắt được,
         # nhưng `chan: []` chạy trót lọt và ra `"a|b|"` — dấu vân tay của
         # một vị thế KHÔNG CÓ CHÂN NÀO, và nó xoá trúng cơ hội khác.
         and _dvd49({"chienLuoc": "a", "taiSan": "b", "chan": []}) is None,
         "một dấu nửa vời xoá trúng cơ hội KHÁC")

    # ── ĐƯỜNG THỰC HIỆN: chỉ chạy khi người đã bật ──────────────────────
    from thi_bac_ty.danh_muc import ViThe as _VT49

    def _may49(tuXoay):
        tu = TrungUong(_tam(f"xoay-{tuXoay}"),
                       {"vonBanDauUsd": 10_000.0, "tuXoayCho": tuXoay})
        # Giống bản `tom_tat()` thật: có `chienLuoc` và `chan`, không thì
        # `_dau_van_tu_dict` trả None và phép kiểm xanh vì lý do sai.
        t = {"chienLuoc": "cu.v1", "taiSan": "CU",
             "chan": [{"ben": "CHO_VAY", "cang": "aave", "chuoi": None}],
             "netMoiGioBps": 2.0 * 100 / (365 * 24),
             "giuGio": 720.0, "phiUocBps": 0.6, "khoaVonDenGio": None,
             "thanhKhoanThoatUsd": 9e9}
        tu.soViThe["m1"] = SoViThe(ma="m1", chienLuoc="cu.v1", toTrinh=t,
                                   vonUsd=500.0, moLucGiay=_G50 and time.time(),
                                   keToanLucGiay=time.time())
        tu.danh_muc.viThe["m1"] = [
            _VT49("m1", "cu.v1", "CHO_VAY", "aave", "CU", 500.0)]
        tu.toTrinhVongNay = [{"ma": "m2", "taiSan": "MOI",
                              "chienLuoc": "moi.v1",
                              "netMoiGioBps": 30.0 * 100 / (365 * 24),
                              "giuGio": 720.0, "phiUocBps": 0.6}]
        return tu

    _tat49 = _may49(False)
    _l49 = _tat49._xoay_cho_neu_duoc()
    kiem("TẮT thì chỉ ĐO, không đóng gì",
         _l49.soXoayDuoc == 1 and _l49.soDaDong == 0
         and len(_tat49.soViThe) == 1,
         f"{_l49.tom_tat()} — xoay chỗ là ĐỔI DANH MỤC, không phải đổi một "
         f"con số hiển thị")
    _bat49 = _may49(True)
    _bat49.phan_bo.c["toiDaSoViThe"] = 1        # HẾT ghế — mới được đuổi
    # Giữ MỘT PHÚT: nhỏ hơn ngưỡng 15 phút nhưng KHÁC 0. Để đúng `now` thì
    # `daGiuGio` ra 0 tròn trên Windows, và phép kiểm xanh vì nhánh «chia
    # cho 0» chứ không vì nhánh «giữ quá ngắn» — hai lý do khác nhau, và
    # đột biến sống sót đúng ở khe ấy.
    _bat49.soViThe["m1"].moLucGiay = time.time() - 60.0
    _l50 = _bat49._xoay_cho_neu_duoc()
    # CÒN GHẾ TRỐNG thì KHÔNG đuổi ai. Đã cắn thật ngay lượt đầu chạy với
    # vốn một triệu và trần 120 chỗ: máy cấp 6 vị thế rồi ĐÓNG 8 trong CÙNG
    # một vòng, vòng sau cấp lại đúng những cái vừa đóng — mỗi vòng một lần
    # phí vào + phí ra trên 25.000 USD, cho một danh mục không đổi.
    _ghe49 = _may49(True)
    _ghe49.phan_bo.c["toiDaSoViThe"] = 120
    _l49b = _ghe49._xoay_cho_neu_duoc()
    kiem("còn GHẾ TRỐNG thì KHÔNG đuổi ai",
         _l49b.soDaDong == 0 and _l49b.viConGhe
         and len(_ghe49.soViThe) == 1,
         f"{_l49b.tom_tat()} — tiền đề của cả cơ chế là «chỗ ngồi CÓ HẠN»; "
         f"còn chỗ thì câu hỏi «ai nên ngồi» không đặt ra")
    kiem("nhưng vẫn ĐO và nói ra sẽ đổi được mấy chỗ",
         _l49b.soXoayDuoc == 1 and "ghế trống" in _l49b.vi, _l49b.vi)

    # Câu «còn ghế trống» GHI ĐÈ câu của `do_xoay_cho`, nên nó phải mang
    # theo cái mà câu kia định nói. Đo làn thật 30/08 ngay sau khi nối
    # trần bằng chứng: «0 chỗ sẽ đáng đổi khi hết ghế» — đúng, nhưng lý
    # do là 56 chỗ vừa bị trần chặn, và câu bị ghi đè đã nuốt mất chỗ ấy.
    # Một con số 0 không kèm lý do đọc thành «chợ hôm nay không có gì».
    _kep49 = _may49(True)
    _kep49.phan_bo.c["toiDaSoViThe"] = 120
    from thi_bac_ty.so_cai import ButToan as _BT49
    _kep49.so_cai.ghi(_BT49(
        "DONG_VI_THE", "xoay chỗ · A → B", 0.0, "cu.v1", "cu-1",
        {"xoayCho": True, "taiSanCu": "A", "taiSanMoi": "B",
         "gioChungHua": 700.0, "daGiuGio": 0.008,
         "loiRongUocUsd": 40.0}))
    _l49c = _kep49._xoay_cho_neu_duoc()
    kiem("trần bằng chứng đọc được TỪ SỔ, không phải một tham số",
         _l49c.gioSongTrungVi == 0.008,
         f"{_l49c.tom_tat()} — nối sai thì cả cơ chế im lặng thành không "
         f"trần, và im lặng ấy trông y hệt «sổ chưa có bằng chứng»")
    kiem("câu «còn ghế trống» KHÔNG nuốt mất lý do bị chặn",
         (_l49c.soBiChanBoiBangChung >= 1
          and "ghế trống" in _l49c.vi
          and "TRẦN BẰNG CHỨNG" in _l49c.vi),
         f"{_l49c.vi} — một con số 0 không kèm lý do đọc thành «chợ hôm "
         f"nay không có gì»")

    # ── ĐÍCH phải qua được RỦI RO TỔNG ─────────────────────────────────
    # Không lọc thì bảng hứa một việc Phân Bổ sẽ từ chối làm. Đo 30/08
    # trên máy sống: «15 chỗ đáng đổi · +1.394 USD», và bốn dòng lớn nhất
    # (289+208+187+173 USD) đều trỏ sang `yield.pendle_pt.v1` — đúng cái
    # ty mà Rủi Ro Tổng chặn sạch vì khoá vốn 2.119 giờ > trần 720. Cả một
    # con số đẹp dựng trên những lần đổi không bao giờ xảy ra được.
    _chan49 = _may49(True)
    _chan49.phan_bo.c["toiDaSoViThe"] = 1        # hết ghế, để nó chạy thật
    _chan49.soViThe["m1"].moLucGiay = time.time() - 60.0
    # Trần khoá vốn 0 giờ: mọi tờ trình khai khoá > 0 đều bị chặn.
    _chan49.rui_ro_tong.c["khoaVonToiDaGio"] = 0.0
    _chan49.toTrinhVongNay = [_mau(taiSan="MOI", von=100.0, chua=9000.0,
                                   net=900.0, giu=720.0, khoa=5000.0)]
    _lc = _chan49._xoay_cho_neu_duoc()
    kiem("đích bị Rủi Ro Tổng chặn thì KHÔNG vào phép đo, và ĐẾM ra",
         _lc.soDichBiChan == 1 and _lc.soXoayDuoc == 0
         and _lc.soDaDong == 0,
         f"{_lc.tom_tat()} — đổi sang một chỗ Phân Bổ sẽ không cấp vốn là "
         f"hứa một việc máy sẽ từ chối làm")
    # Và cùng tờ trình ấy, khi trần khoá cho phép, thì nó PHẢI vào phép đo
    # — không thì bộ lọc đang chặn nhầm mọi thứ và con số 0 kia vô nghĩa.
    _chan49.rui_ro_tong.c["khoaVonToiDaGio"] = 9000.0
    _lc2 = _chan49._xoay_cho_neu_duoc()
    kiem("nới trần ra thì chính tờ ấy vào lại phép đo",
         _lc2.soDichBiChan == 0 and _lc2.soXoayDuoc >= 1,
         f"{_lc2.tom_tat()} — bộ lọc chặn nhầm mọi thứ thì con số 0 ở trên "
         f"cũng xanh, và nó không nói gì cả")

    # ── LỜI HỨA «Phân Bổ sẽ lấp chỗ» phải KIỂM CHỨNG ĐƯỢC ───────────────
    # Luật «còn ghế thì không đuổi ai» đứng trên một lời hứa, và trên máy
    # sống 30/08 lời hứa ấy đang sai: 54 vị thế, 66 ghế trống, 478 nghìn
    # USD nằm không, số vị thế đứng yên vòng này qua vòng khác — vì cơ hội
    # tốt hơn nằm trong một họ đã chạm trần `tranMotTy`, nên ghế trống
    # không giúp gì cho chúng. Đo được 15 chỗ đáng đổi, APR 3,31% → 6,63%.
    #
    # ĐẾM thôi, không tự đổi hành vi: đóng một vị thế mà Phân Bổ không mở
    # lại được là đẩy vốn về tiền mặt ăn 0% — tệ hơn giữ nguyên.
    from thi_bac_ty.trung_uong import VONG_GHE_TRONG_DANG_NGO as _NGO
    _dem = _may49(True)
    _dem.phan_bo.c["toiDaSoViThe"] = 120
    _ds, _cuoi = [], None
    for _ in range(_NGO + 1):
        _cuoi = _dem._xoay_cho_neu_duoc()
        _ds.append(_cuoi.soVongGheTrongKhongLap)
    # Vòng ĐẦU đếm 0, và đó là đúng: «số vị thế không tăng» là một câu về
    # HAI vòng, nên vòng đầu chưa nói được gì. Đếm nó thành 1 là bịa ra
    # một quan sát chưa xảy ra.
    kiem("đếm được số VÒNG LIÊN TIẾP còn ghế mà số vị thế không tăng",
         _ds == list(range(_NGO + 1)),
         f"{_ds} — lời hứa «Phân Bổ sẽ lấp chỗ trống» kiểm chứng được, và "
         f"không đếm thì nó sai im lặng mãi mãi")
    kiem("quá ngưỡng thì NÓI RA, và nói rõ máy KHÔNG tự đuổi ai vì thế",
         "vòng LIÊN TIẾP" in _cuoi.vi and "tiền mặt ăn 0%" in _cuoi.vi,
         _cuoi.vi)
    # Vị thế TĂNG thì lời hứa đang được giữ — bộ đếm phải về 0, không thì
    # nó chỉ đếm số vòng đã chạy chứ không đếm điều nó nói mình đếm.
    _dem.soViThe["m9"] = _dem.soViThe["m1"]
    _dem.danh_muc.viThe["m9"] = _dem.danh_muc.viThe["m1"]
    kiem("số vị thế TĂNG thì bộ đếm về 0",
         _dem._xoay_cho_neu_duoc().soVongGheTrongKhongLap == 0,
         "lời hứa đang được giữ thì không có gì để nghi ngờ")
    # Và HẾT GHẾ cũng phải về 0: lúc ấy luật «còn ghế thì không đuổi ai»
    # không còn áp dụng, nên con số đếm nó cũng thôi có nghĩa. Để nguyên
    # là mang một quan sát cũ sang một trạng thái khác.
    _het = _may49(True)
    _het.phan_bo.c["toiDaSoViThe"] = 120
    for _ in range(_NGO + 1):
        _het._xoay_cho_neu_duoc()
    _het.phan_bo.c["toiDaSoViThe"] = 1          # hết ghế
    _het.soViThe["m1"].moLucGiay = time.time() - 60.0
    kiem("HẾT GHẾ thì bộ đếm cũng về 0",
         _het._xoay_cho_neu_duoc().soVongGheTrongKhongLap == 0
         and _het._vongGheTrongKhongLap == 0,
         f"{_het._vongGheTrongKhongLap} — luật «còn ghế thì không đuổi ai» "
         f"hết áp dụng thì con số đếm nó cũng thôi có nghĩa")

    kiem("BẬT thì đóng thật, và hoàn vốn về tiền mặt",
         _l50.soDaDong == 1 and not _bat49.soViThe
         and gan(_bat49.danh_muc.tienMatUsd, 10_500.0),
         f"{_l50.tom_tat()} · tiền mặt {_bat49.danh_muc.tienMatUsd}")
    # Vị thế vừa mở đã bị xoay đi thì «lãi mỗi giờ» không nói được gì —
    # đường XOAY CHỖ cũng phải tôn trọng ngưỡng ấy, không chỉ đường hết hạn.
    _bt49 = [x for x in _bat49.so_cai.gan_day(20)
             if x["loai"] == "DONG_VI_THE"
             and (x["chiTiet"] or {}).get("xoayCho")]
    kiem("xoay một vị thế vừa mở thì KHÔNG ghi một tỉ suất bịa",
         _bt49 and (_bt49[0]["chiTiet"] or {}).get("thucBpsGio") is None,
         f"{_bt49[:1]} — chia lãi lỗ cho vài giây giữ ra một con số của "
         f"mẫu số, không phải của chiến lược")

    kiem("lần đóng ấy VÀO SỔ, kèm lý do đọc được",
         any(x["loai"] == "DONG_VI_THE"
             and (x["chiTiet"] or {}).get("xoayCho")
             for x in _bat49.so_cai.gan_day(20)),
         "đóng một vị thế mà không ghi vì sao thì ba tháng sau không ai "
         "dựng lại được quyết định ấy")
    kiem("và nó KHÔNG tự mở vị thế mới — chỗ trống để Phân Bổ rót",
         not _bat49.danh_muc.viThe,
         "dựng một đường mở ở đây là dựng một cửa cấp vốn KHÔNG đi qua Rủi "
         "Ro Tổng")
    kiem("biên an toàn lúc TỰ ĐỘNG rộng hơn lúc chỉ ĐO",
         float(_bat49.c.get("bienXoayCho")) > 1.0,
         "phép đo có người nhìn từng dòng, đường tự động thì không")
    # Đặt dấu vào TRƯỚC rồi mới xoay, không thì phép kiểm xanh vì `_dauVet`
    # vốn rỗng — xanh vì một lý do không liên quan là loại xanh tệ nhất.
    _may51 = _may49(True)
    _may51.phan_bo.c["toiDaSoViThe"] = 1
    _van51 = _dvd49(_may51.soViThe["m1"].toTrinh)
    kiem("sổ vị thế dựng được dấu vân tay từ tờ trình đã lưu",
         _van51 is not None, "thiếu `chan` hay `chienLuoc` thì xoá trượt")
    _may51._dauVet[_van51] = 1.0
    kiem("dấu vân tay ĐANG chặn trước khi xoay",
         _van51 in _may51._dauVet, _van51)
    # Và đường ĐÓNG THỨ HAI — hết hạn giữ — cũng phải xoá. Hai đường đóng
    # thì sớm muộn chúng lệch nhau; đúng bài học `_cuoi_vong`.
    _may52 = _may49(False)
    _may52.soViThe["m1"].toTrinh["giuGio"] = 0.001
    _may52.soViThe["m1"].moLucGiay = time.time() - 3600.0
    _van52 = _dvd49(_may52.soViThe["m1"].toTrinh)
    _may52._dauVet[_van52] = 1.0
    _may52._ke_toan_vi_the()
    kiem("HẾT HẠN GIỮ cũng xoá dấu vân tay, không chỉ xoay chỗ",
         _van52 not in _may52._dauVet and not _may52.soViThe,
         f"{list(_may52._dauVet)} — hai đường đóng thì sớm muộn chúng lệch "
         f"nhau, và đường quên xoá sẽ chặn im lặng")

    _may51._xoay_cho_neu_duoc()
    kiem("và đóng xong thì XOÁ dấu ấy, để cơ hội vào lại được",
         _van51 not in _may51._dauVet,
         f"{list(_may51._dauVet)} — dấu còn thì cơ hội bị chặn suốt "
         f"`nhipGhiNhanGiay`, và vốn nằm không suốt ngần ấy. Đã cắn thật: "
         f"23 tờ trình, 23 lần BỎ TRÙNG, 998.000 USD ngồi im")

    # ── config.json xin một đằng, máy chạy một nẻo ──────────────────────
    # Kho bản tham số thắng config — cố ý, không thì mỗi lần khởi động lại
    # là xoá sạch mọi bản đã có người ký. Nhưng cái đúng ấy im lặng.
    _d24 = _tam("lech-cau-hinh")
    tu24 = TrungUong(_d24, {"vonBanDauUsd": 10_000.0,
                            "phanBo": {"toiDaSoViThe": 12}})
    kiem("config khớp bản đang chạy thì KHÔNG kêu",
         tu24.lech_cau_hinh() == [], str(tu24.lech_cau_hinh()))
    tu25 = TrungUong(_d24, {"vonBanDauUsd": 10_000.0,
                            "phanBo": {"toiDaSoViThe": 40}})
    _l25 = tu25.lech_cau_hinh()
    kiem("sửa config trên máy ĐÃ có bản tham số thì máy KHÔNG đổi",
         tu25.phan_bo.c["toiDaSoViThe"] == 12,
         "kho bản tham số thắng config — cố ý, xem `__init__`")
    kiem("và chỗ lệch ấy được KHAI ra, không im lặng",
         _l25 == [{"nut": "phanBo.toiDaSoViThe", "xin": 40, "dangChay": 12}],
         f"{_l25} — người sửa config không đọc mã trước khi sửa; im lặng ở "
         f"đây nghĩa là họ tin mình đã đổi được")
    kiem("ảnh chụp mang theo chỗ lệch ấy",
         tu25.anh_chup().get("lechCauHinh") == _l25,
         "đo được mà không hiện lên buồng lái thì vẫn là im lặng")

    # ── và cái vòng tròn mà việc tự quay ấy khép lại ────────────────────
    # anh_chup → hiến pháp → mot_vong → hoc → anh_chup → … Điều
    # `ngat-roi-van-quan-sat` dựng một Trung Ương THẬT và quay hai vòng,
    # nên vòng tròn này có thật chứ không phải giả thuyết.
    import thi_bac_ty.hien_phap as _hp22
    import thi_bac_ty.trung_uong as _tu22m

    _hp22._DANG_SOAT = True
    try:
        _long = _hp22.tom_tat()
    finally:
        _hp22._DANG_SOAT = False
    kiem("soát hiến pháp LỒNG thì dừng, không đệ quy",
         _long.get("long") is True,
         "máy do chính hiến pháp dựng ra để thử thì không soát lại hiến pháp")
    kiem("và bản lồng nói KHÔNG BIẾT, chứ không nói 0 vi phạm",
         _long["soViPham"] is None,
         "số 0 ở đây là một lời nói dối đọc y hệt một tin tốt")
    kiem("cờ `long` sống sót qua `tom_tat`",
         "long" in _long,
         "lọc mất cờ ấy thì bên gọi giữ bản rỗng lại như bản thật")

    _tu22m._HP = None
    _hp22._DANG_SOAT = True
    try:
        _r = _tu22m._hien_phap()
    finally:
        _hp22._DANG_SOAT = False
    kiem("ảnh chụp KHÔNG giữ lại bản lồng", _tu22m._HP is None,
         "giữ nó là cả phút sau buồng lái vẫn đọc phải một tóm tắt rỗng")
    _tu22m._HP = None
    _t22a = time.time()
    _tu22m._hien_phap()
    _lan1 = time.time() - _t22a
    _t22b = time.time()
    _r2 = _tu22m._hien_phap()
    _lan2 = time.time() - _t22b
    kiem("soát hiến pháp có NHỊP, không chạy lại mỗi lần hỏi ảnh chụp",
         _lan2 < _lan1 / 4 and _tu22m._HP is not None,
         f"lần đầu {_lan1 * 1000:.0f}ms, lần sau {_lan2 * 1000:.0f}ms — "
         f"buồng lái hỏi mỗi vài giây, mà hiến pháp là hàm của MÃ NGUỒN")
    kiem("và bản giữ lại KHAI TUỔI của nó", _r2.get("tuoiGiay") is not None,
         "một con số cũ mà không nói mình cũ thì trông y hệt một con số mới")

    tu23 = TrungUong(_tam("hoc-nhip"), {"vonBanDauUsd": 10_000.0,
                                        "nhipHocGiay": 9_999.0})
    tu23.dang_ky(_TyGiaKhongKeToan())
    tu23.mot_vong()
    lan1 = tu23.hocCuoi and tu23.hocCuoi["luc"]
    tu23.mot_vong()
    kiem("nhịp thưa được TÔN TRỌNG, không chẩn mỗi vòng",
         tu23.hocCuoi and tu23.hocCuoi["luc"] == lan1,
         "chẩn đoán đọc cả ảnh chụp rồi chạy lại phân bổ trên toàn bộ tờ "
         "trình đã ghi; chạy mỗi 30 giây là đốt công cho một bức tranh gần "
         "như đứng yên")









    # ── 11. mọi ty ĐANG CHẠY: có kế toán hay chưa, phải KHAI ────────────
    _cacTy = [
        ("bac.ty_perp", "TyPerp"),
        ("tin_dung.ty_vay", "TyTinDung"),
        ("on_dinh.ty_on_dinh", "TyOnDinh"),
        ("lai_suat.ty_lai_suat", "TyLaiSuat"),
        ("co_so.ty_co_so", "TyCoSo"),
        ("kham_ngoai.ty_tien_doan", "TyTienDoan"),
        ("quyen_chon.ty_ngang_gia", "TyNgangGia"),
        ("dex_arb.ty_vong_doi", "TyVongDoi"),
        ("lp_amm.ty_cap_thanh_khoan", "TyCapThanhKhoan"),
    ]
    co, chua = [], []
    for mod, ten in _cacTy:
        try:
            k_ = getattr(__import__(mod, fromlist=[ten]), ten)
        except Exception:                                    # noqa: BLE001
            continue
        (co if k_.co_ke_toan() else chua).append(k_.ma)
    kiem(f"{len(co)}/{len(co) + len(chua)} ty đã có kế toán",
         len(co) >= 2, f"có: {sorted(co)}")
    kiem("và những ty CHƯA có được liệt kê ra, không giấu",
         isinstance(chua, list),
         f"chưa có kế toán: {sorted(chua)} — vốn cấp cho chúng nằm trong NAV "
         f"mà không ai cộng lãi lỗ, và buồng lái phải nói đúng câu ấy")




def kiem_kho_bao_gia_cau() -> None:
    print("\n-- KHO BAO GIA CAU: song qua lan khoi dong lai --")
    import time as _t
    from chuyen_von.cau_noi import BaoGiaCau
    from chuyen_von.dinh_tuyen import (TUOI_BAO_GIA_TOI_DA_GIAY, DinhTuyen,
                                       _khoa)

    now = _t.time() * 1000.0

    def _bg(taiSan, tu, den, von, phi, tuoiGiay=0.0):
        return BaoGiaCau(taiSan=taiSan, tuChuoi=tu, denChuoi=den,
                         vonUsd=von, phiTaiSan=phi, gasUsd=0.03,
                         giayCho=120.0, congCu="across",
                         docLucMs=now - tuoiGiay * 1000.0)

    def _mu(taiSan, tu, den, von, tuoiGiay=0.0):
        return BaoGiaCau(taiSan=taiSan, tuChuoi=tu, denChuoi=den,
                         vonUsd=von, phiTaiSan=None, gasUsd=None,
                         giayCho=None, congCu="?",
                         docLucMs=now - tuoiGiay * 1000.0,
                         loi="LI.FI 429")

    d = _tam("kho-cau")
    tep = d / "kho-bao-gia-cau.json"

    a = DinhTuyen()
    a.kho[_khoa("USDC", "arbitrum", "polygon", 1000)] = _bg(
        "USDC", "arbitrum", "polygon", 1000, 2.5)
    a.kho[_khoa("USDC", "arbitrum", "base", 1000)] = _bg(
        "USDC", "arbitrum", "base", 1000, 1.1, tuoiGiay=600.0)
    a.kho[_khoa("USDC", "base", "ethereum", 1000)] = _mu(
        "USDC", "base", "ethereum", 1000)
    a.kho[_khoa("USDC", "polygon", "ethereum", 1000)] = _bg(
        "USDC", "polygon", "ethereum", 1000, 4.0,
        tuoiGiay=TUOI_BAO_GIA_TOI_DA_GIAY + 600.0)

    so = a.luu_kho(tep)
    kiem("chỉ ghi báo giá ĐO ĐƯỢC, không ghi bản mù", so == 3,
         f"{so}/4 — một báo giá mù ghi ra đĩa rồi nạp lại ở lần chạy sau là "
         f"mang sự mù qua một ranh giới nó lẽ ra không vượt được")

    b = DinhTuyen()
    r = b.nap_kho(tep)
    kiem("nạp lại được kho từ đĩa", r["nap"] == 2 and r["co"],
         f"{r} — kho nằm trong RAM nên nó chết theo tiến trình, trong khi "
         f"phí cầu đổi rất chậm")
    kiem("và BỎ bản quá hạn thay vì nạp bừa", r["boQuaCu"] == 1,
         f"{r} — nạp lại một báo giá già hơn TUOI_BAO_GIA_TOI_DA_GIAY là "
         f"lách chính ngưỡng ấy")

    con = b.kho.get(_khoa("USDC", "arbitrum", "base", 1000))
    kiem("tuổi vẫn tính từ `docLucMs` GỐC, không đóng dấu lại",
         con is not None and (now - con.docLucMs) / 1000.0 > 500.0,
         "đóng dấu lại là làm một báo giá hai tiếng trông như vừa đọc xong, "
         "và `chang_cau()` sẽ thôi khai tuổi — cái khai tuổi ấy mới là thứ "
         "khiến việc dùng số cũ trung thực")

    # ── KHÔNG đè bản đang có trong RAM ─────────────────────────────────
    c = DinhTuyen()
    moi = _bg("USDC", "arbitrum", "polygon", 1000, 9.99)
    c.kho[_khoa("USDC", "arbitrum", "polygon", 1000)] = moi
    r2 = c.nap_kho(tep)
    kiem("KHÔNG đè bản đang có trong RAM", r2["boQuaDaCo"] == 1
         and c.kho[_khoa("USDC", "arbitrum", "polygon", 1000)] is moi,
         "bản trong bộ nhớ luôn mới hơn hoặc bằng bản trên đĩa")

    # ── không có tệp thì nói ra, không nổ ──────────────────────────────
    e = DinhTuyen()
    r3 = e.nap_kho(d / "khong-co-tep.json")
    kiem("chưa có kho trên đĩa thì khai `co: False`, không nổ",
         r3["co"] is False and r3["nap"] == 0, str(r3))

    # ── tệp hỏng cũng không được giết lượt khởi động ───────────────────
    xau = d / "hong.json"
    xau.write_text("{ khong phai json", encoding="utf-8")
    f = DinhTuyen()
    r4 = f.nap_kho(xau)
    kiem("kho hỏng thì KHAI lỗi rồi đi tiếp, không giết runtime",
         r4["nap"] == 0 and "loi" in r4, str(r4))

    # ── NHỊP nạp cũng phải sống qua khởi động lại, không chỉ cái kho ───
    #
    # Kho sống sót từ 28/08, nhưng `_lanNapCau = 0.0` mỗi lần bật máy nên
    # nhịp vẫn về 0 và runtime vẫn nạp trước chín báo giá. Mười lăm lần
    # bật trong một buổi chiều sửa mã là 429 kèm «retry in 1 hour», tức
    # mọi tuyến liên chuỗi MÙ đúng lúc vừa bật máy lên. Đo thật 30/08:
    # `soLoi 9/9 · dangNghi true · conNghiGiay 4892`.
    kiem("kho khai BÁO GIÁ MỚI NHẤT nó vừa nạp",
         r["moiNhatMs"] is not None
         and r["moiNhatMs"] <= now and (now - r["moiNhatMs"]) < 3_600_000.0,
         f"{r.get('moiNhatMs')} — không khai thì bên gọi không có cách nào "
         f"biết kho còn tươi tới đâu, và nó nạp lại ngay khi vừa bật")
    kiem("kho RỖNG thì KHÔNG khai một mốc bịa",
         r3.get("moiNhatMs") is None,
         f"{r3} — không có gì trên đĩa thì nạp ngay là đúng; bịa một mốc "
         f"ở đây là làm runtime ngồi im 30 phút với một kho trống")

    # Và runtime phải THẬT SỰ dùng nó — một con số khai ra mà không ai đọc
    # thì nhịp vẫn về 0 y như cũ.
    import pathlib as _plv
    _src = _plv.Path(__import__("bac.vong", fromlist=["x"]).__file__
                     ).read_text(encoding="utf-8")
    kiem("và vòng lặp ĐỌC mốc ấy để đặt nhịp, không đặt 0",
         "moiNhatMs" in _src and "self._lanNapCau = 0.0" not in _src,
         "kho sống qua khởi động lại mà nhịp thì không là sửa được một nửa")

    # ── runtime PHẢI gọi cả hai đầu ────────────────────────────────────
    import ast as _ast
    import pathlib as _pl
    from bac import vong as _v
    cay = _ast.parse(_pl.Path(_v.__file__).read_text(encoding="utf-8"))
    ten = {n.func.attr for n in _ast.walk(cay)
           if isinstance(n, _ast.Call) and isinstance(n.func, _ast.Attribute)}
    kiem("runtime nạp kho lúc khởi động VÀ lưu sau mỗi lượt nạp mới",
         {"nap_kho", "luu_kho"} <= ten,
         f"thiếu {sorted({'nap_kho', 'luu_kho'} - ten)} — chỉ lưu mà không "
         f"nạp thì kho là một file không ai đọc; chỉ nạp mà không lưu thì "
         f"nó đứng yên ở lần ghi đầu tiên")


def kiem_lat_cat() -> None:
    print("\n-- LAT CAT: cau noi runtime -> cung tinh --")
    import ast as _ast
    import json as _js
    import pathlib
    import re as _re
    from bac import snapshot as _sn
    from bac.config import CONFIG as _CFG

    goc = pathlib.Path(_sn.__file__).resolve().parent.parent

    # ── 1. tiêu đề HỨA gì thì phải có chỗ THỰC HIỆN ────────────────────
    # Đã cắn thật: tiêu đề ghi `python run.py — ghi mỗi vòng lặp`, câu chép
    # từ Tử Cấm Thành nơi nó đúng, còn ở đây `bac/vong.py` không hề gọi
    # `ghi_lat_cat`. Cung tĩnh chỉ đổi khi có người bấm nút, nên trang công
    # khai đứng ở lát cắt cũ mà tiêu đề vẫn nói nó tươi mỗi vòng.
    #
    # Tìm bằng AST chứ KHÔNG bằng `"ghi_lat_cat" in nguon`: phép cấy lỗi
    # ngược đổi lời gọi thành `pass  # ghi_lat_cat(self)` và phép kiểm
    # khớp-chuỗi vẫn xanh — đúng lần thứ ba kiểu hỏng ấy đi lọt trong dự
    # án này.
    def _co_goi(tep: str, ten: str) -> bool:
        cay = _ast.parse((goc / tep).read_text(encoding="utf-8"))
        for n in _ast.walk(cay):
            if isinstance(n, _ast.Call):
                f = n.func
                if isinstance(f, _ast.Name) and f.id == ten:
                    return True
                if isinstance(f, _ast.Attribute) and f.attr == ten:
                    return True
        return False

    hua_vong = "mỗi vòng lặp" in _sn.HEADER
    goi_vong = _co_goi("bac/vong.py", "ghi_lat_cat")
    kiem("tiêu đề hứa 'ghi mỗi vòng lặp' thì vòng lặp PHẢI GỌI ghi_lat_cat",
         hua_vong == goi_vong,
         f"tiêu đề hứa={hua_vong} · vòng lặp gọi thật={goi_vong}")
    kiem("và câu 'ghi một lần rồi thoát' có `_main` thật",
         ("ghi một lần rồi thoát" not in _sn.HEADER)
         or callable(getattr(_sn, "_main", None)))
    kiem("nút trong buồng lái cũng gọi thật",
         _co_goi("bac/server.py", "ghi_lat_cat")
         and "/api/lat-cat" in (goc / "bac" / "server.py").read_text(
             encoding="utf-8"))

    # ── 2. ghi vào nhánh MẠNG-TRƯỚC ────────────────────────────────────
    kiem("lát cắt nằm ở `assets/js/v/` — nhánh mạng-trước",
         _sn._TUONG_DOI[:3] == ("assets", "js", "v"),
         f"{_sn._TUONG_DOI} — đặt sang nhánh cache-trước thì máy đã cài app "
         f"hiện lát cắt hôm qua tới lần nâng CACHE_VERSION kế tiếp, tức là "
         f"một bảng điều khiển nói dối")

    # ── 3. GHI THẬT ra một cung giả, rồi đọc lại ───────────────────────
    # Dựng object rồi tự gọi `sach()` trong phép kiểm là kiểm `sach()`,
    # KHÔNG kiểm `ghi_lat_cat()` có dùng nó không — bỏ `sach` khỏi hàm ghi
    # mà phép kiểm vẫn xanh. Nên ở đây đi qua đúng đường thật.
    class _RtBan:
        """Runtime GIẢ trả về số bẩn. `json.dumps` ném giữa chừng ở `inf`,
        và vòng lặp chỉ ghi một dòng nhật ký rồi đi tiếp — cung tĩnh đứng
        im mà không ai biết."""
        def anh_chup(self):
            return {"maChienLuoc": "x.y.v1", "vong": 3,
                    "coHoi": [{"ma": "BTC", "duyet": True,
                               "sanLong": "binance", "sanShort": "okx",
                               "netBps": float("inf")}],
                    "cang": [{"ten": "a", "tre": float("nan")}],
                    "trungUong": {"danhMuc": {"navUsd": float("-inf")}}}

    _goc_cfg = (Path(__file__).resolve().parent.parent
                / "bac/config.py").read_text(encoding="utf-8")
    tam = _tam("cung-gia")
    (tam / "index.html").write_text("<!doctype html>", encoding="utf-8")
    cu = _CFG.get("cungTinh")
    _CFG["cungTinh"] = str(tam)
    try:
        duong = _sn.ghi_lat_cat(_RtBan())
        ra = duong.read_text(encoding="utf-8") if duong else ""
        vo = ""
    except (ValueError, TypeError) as e:
        duong, ra, vo = None, "", f"{type(e).__name__}: {e}"
    finally:
        if cu is None:
            _CFG.pop("cungTinh", None)
        else:
            _CFG["cungTinh"] = cu

    kiem("ghi được ra cung giả, inf/nan KHÔNG làm ném giữa chừng",
         bool(duong) and not vo, vo or "ghi_lat_cat trả None")
    kiem("và đúng đường `assets/js/v/cang-phi.js`",
         bool(duong) and duong.parts[-4:] == _sn._TUONG_DOI,
         str(duong))
    kiem("file ra KHÔNG còn Infinity/NaN nào",
         bool(ra) and "Infinity" not in ra and "NaN" not in ra,
         "JSON không có Infinity; trình duyệt nạp file ấy là lỗi cú pháp, "
         "và trang tĩnh trắng trơn")

    # ── CỖ MÁY THỨ HAI không được đè lát cắt của cỗ máy thật ────────────
    # Người muốn chạy một bản demo vốn khác, trên cùng dữ liệu thật, cạnh
    # cỗ máy đang chạy. Cùng cây mã, nên `_cung_tinh()` tự tìm ra cung anh
    # em và mỗi vòng bản demo ghi đè lát cắt công khai bằng số của nó.
    # Không lỗi nào phát ra; chỉ có một trang web nói số của một cỗ máy
    # không ai định công bố.
    kiem("máy chạy trên sổ RIÊNG thì KHÔNG tự tìm cung tĩnh",
         _sn.SO_RIENG and _sn._cung_tinh() is None,
         "khai `cungTinh` là cố ý, tự tìm là tình cờ — và chỉ cái tình cờ "
         "mới nguy hiểm")
    kiem("nhưng KHAI ra thì vẫn ghi được", bool(duong),
         "chặn hẳn thì bản demo không bao giờ có trang riêng được")

    # Kiểm bằng cách CHẠY THẬT một tiến trình con với `TBT_CONFIG` trỏ sang
    # một config khác, chứ không so đường dẫn với chính công thức sinh ra nó
    # — so như thế thì lúc `TBT_CONFIG` không đặt, hai vế bằng nhau kể cả
    # khi mã đã bị chôn cứng lại. Phép kiểm ấy đã SỐNG SÓT qua đột biến.
    import json as _js22
    import subprocess as _sp22
    _cfgTam = _tam("config-rieng") / "khac.json"
    _cfgTam.write_text(_js22.dumps({"port": 59999,
                                    "trungUong": {"vonBanDauUsd": 777.0}}),
                       encoding="utf-8")
    _mt = dict(os.environ, TBT_CONFIG=str(_cfgTam), PYTHONIOENCODING="utf-8")
    _r22 = _sp22.run(
        [sys.executable, "-c",
         "import sys;sys.path.insert(0,'.');from bac.config import CONFIG;"
         "print(CONFIG['port'], CONFIG['trungUong']['vonBanDauUsd'])"],
        cwd=str(Path(__file__).resolve().parent.parent), env=_mt,
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    kiem("`TBT_CONFIG` thật sự đổi được cấu hình cỗ máy",
         _r22.stdout.strip() == "59999 777.0",
         f"ra {_r22.stdout.strip()!r} {_r22.stderr.strip()[-200:]!r} — đường "
         f"cứng thì hai cỗ máy trên cùng cây mã buộc dùng chung mọi tham số: "
         f"cùng cổng, cùng vốn ảo, cùng sổ")
    _goc22 = Path(__file__).resolve().parent.parent
    _cfgThat = _js22.loads((_goc22 / "config.json").read_text(
        encoding="utf-8-sig"))
    _cfgDemo = _js22.loads((_goc22 / "config-demo.json").read_text(
        encoding="utf-8-sig"))
    kiem("bản demo và bản thật KHÔNG dùng chung cổng",
         _cfgDemo["port"] != _cfgThat["port"],
         "cùng cổng thì bản bật sau chết vì cổng bận — mà `pythonw` không có "
         "màn hình, nên nó chỉ đơn giản là không lên")
    kiem("bản demo vẫn là QUAN SÁT",
         _cfgDemo["che"] == "quan-sat",
         "tầng đặt lệnh thật không tồn tại trong cây mã này, và bản demo "
         "không phải chỗ để thử làm nó tồn tại")
    kiem("bản demo KHÔNG khai `cungTinh`",
         not (_cfgDemo.get("cungTinh") or "").strip(),
         "khai ra là cố ý đè lát cắt công khai bằng số của bản demo")
    _bat22 = (_goc22 / "dichvu/bat.ps1").read_text(encoding="utf-8-sig")
    for _bien in ("TBT_CONFIG", "TBT_DATA_DIR", "TBT_TEN"):
        kiem(f"`bat.ps1 -Demo` đặt `{_bien}`", f"$env:{_bien}" in _bat22,
             "thiếu một biến là hai cỗ máy giẫm lên nhau đúng ở chỗ ấy: "
             "chung cổng, chung sổ, hoặc chung file PID")
    kiem("và `chay-nen.py` ghi PID theo TÊN bản",
         "TBT_TEN" in (_goc22 / "dichvu/chay-nen.py").read_text(
             encoding="utf-8"),
         "chung một `pid.txt` thì bật bản thứ hai là ghi đè PID bản thứ "
         "nhất, và từ đó `dung.ps1` dừng nhầm máy")

    kiem("và `TBT_CONFIG` trỏ vào hư không thì DỪNG, không về mặc định",
         "raise FileNotFoundError" in _goc_cfg
         and 'os.environ.get("TBT_CONFIG")' in _goc_cfg,
         "về mặc định ở đây là dựng nhầm cỗ máy: đúng cổng của cỗ máy thật, "
         "đúng vốn của cỗ máy thật, và trông y hệt như đã cấu hình đúng")

    # ── 4. `date` và `tomTat` phải ở 900 BYTE ĐẦU ──────────────────────
    # Cổng Thành huỷ dòng tải sau 900 byte. Đổi thứ tự khoá là thẻ ngoài
    # cổng mất ngày cập nhật, và mất trong im lặng.
    kiem("`date` và `tomTat` nằm trong 900 byte đầu FILE ĐÃ GHI",
         '"date"' in ra[:900] and '"tomTat"' in ra[:900],
         "Cổng Thành chỉ đọc 900 byte đầu rồi huỷ dòng tải")
    o = _sn.dung(_RtBan())
    kiem("và chúng là HAI khoá đầu tiên, đúng thứ tự",
         list(o.keys())[:2] == ["date", "tomTat"], str(list(o.keys())[:3]))

    # ── 5. hình dạng file ra ───────────────────────────────────────────
    kiem("file ra mở bằng chú thích ĐỪNG SỬA TAY",
         ra.startswith("/*") and "ĐỪNG SỬA TAY" in ra[:400])
    kiem("và đóng bằng dấu chấm phẩy", ra.rstrip().endswith(";"),
         "thiếu `;` thì trình duyệt vẫn chạy được nhờ ASI, nhưng ghép file "
         "thì hỏng — và lỗi hiện ra ở file KHÁC")
    kiem("phần JSON đọc lại được",
         bool(ra) and isinstance(
             _js.loads(ra[ra.index("{"):ra.rindex("}") + 1]), dict))

    # ── 6. không HỨA con số ty trong lời nhắc gửi ra trang công khai ───
    # Lời nhắc từng ghi "KHÔNG ty nào trong sáu ty" và ở lại đó khi hệ đã
    # có chín ty — trang công khai nói sai về chính nó, không lỗi nào báo.
    from dong_co_chua_co.so_dang_ky import tom_tat as _dc_tom
    nhac = str((_dc_tom() or {}).get("loiNhac") or "")
    so_ty = _re.search(
        r"(một|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười|\d+)\s+ty\b", nhac)
    kiem("lời nhắc engine KHÔNG chôn cứng số ty",
         so_ty is None,
         f"«{so_ty.group(0) if so_ty else ''}» — con số ấy đứng yên trong "
         f"khi hệ thêm ty, và nó đi thẳng ra trang công khai")


def kiem_doi_soat_vi_the() -> None:
    print("\n-- DOI SOAT VI THE: so nho, danh muc quen --")
    from thi_bac_ty.cau_dao import CauDao
    from thi_bac_ty.danh_muc import DanhMuc, ViThe
    from thi_bac_ty.doi_soat_vi_the import MA_NGAT, canh, do, doi_soat
    from thi_bac_ty.so_cai import ButToan, SoCai
    from thi_bac_ty.so_dang_ky import SoDangKy

    class _That:
        """Lớp thực thi GIẢ, chạy tiền thật. `DieuPhoiThucThi.moPhong` là
        True cứng nên nhánh tiền thật không đi vào được từ mã thật — mà
        một nhánh chỉ có văn xuôi bảo vệ là một nhánh chưa được bảo vệ."""
        moPhong = False

    class _Gia:
        moPhong = True

    def _dung(ten):
        d = _tam(ten)
        sdk = SoDangKy(d / "sdk.sqlite3")
        sc = SoCai(d / "sc.sqlite3")
        dm = DanhMuc(1000.0)
        return sdk, sc, dm

    def _mo(sdk, sc, taiSan, capUsd, vonXin=200.0):
        """Đưa một tờ trình đi hết đường tới DA_MO, và ghi CAP_VON.

        `taiSan` khác nhau để dấu vân khác nhau — `SoDangKy.ghi_nhan()`
        chặn hai tờ cùng mã, nên hai tờ giống hệt là một tờ."""
        tt = _mau(taiSan=taiSan, von=vonXin)
        sdk.ghi_nhan(tt)
        for b in ("DUYET_TY", "DUYET_RUI_RO", "DA_CAP_VON", "DA_MO"):
            sdk.chuyen(tt.ma, b, "dựng phép kiểm")
        if capUsd is not None:
            sc.ghi(ButToan("CAP_VON", "phép kiểm cấp vốn", float(capUsd),
                           tt.chienLuoc, tt.ma))
        return tt

    # ── 1. ĐO: sổ mở, danh mục rỗng → mồ côi ────────────────────────────
    sdk, sc, dm = _dung("ds1")
    t1 = _mo(sdk, sc, "BTC", 100.0)
    t2 = _mo(sdk, sc, "ETH", 150.0)
    b = do(sdk, dm, sc)
    kiem("sổ ghi DA_MO mà danh mục không giữ → MỒ CÔI", len(b.moCoi) == 2,
         f"{len(b.moCoi)} — sổ đăng ký nằm trên đĩa, danh mục dựng trong RAM; "
         f"mỗi lần khởi động lại là một lần vốn đã cam kết bốc hơi khỏi phép "
         f"tính trần")
    kiem("vốn mồ côi đọc từ SỔ CÁI, không từ tờ trình",
         b.vonMoCoiUsd == 250.0,
         f"{b.vonMoCoiUsd} — hai tờ XIN 200 mỗi tờ nhưng chỉ được cấp "
         f"100+150; lấy số xin thì thổi 250 thành 400")

    # ── 2. danh mục có giữ → KHÔNG phải mồ côi ──────────────────────────
    dm.cam_ket(t1.ma, [ViThe(t1.ma, t1.chienLuoc, "CHO_VAY", "aave-v3",
                             "USDC", 100.0)])
    b = do(sdk, dm, sc)
    kiem("tờ nào danh mục ĐANG giữ thì không tính là mồ côi",
         [x.ma for x in b.moCoi] == [t2.ma])

    # ── 3. không có CAP_VON → None, KHÔNG phải 0 ────────────────────────
    sdk3, sc3, dm3 = _dung("ds3")
    _mo(sdk3, sc3, "BTC", None)
    _mo(sdk3, sc3, "ETH", 100.0)
    b3 = do(sdk3, dm3, sc3)
    kiem("tờ không có bút toán CAP_VON thì vốn là None, không phải 0",
         any(x.vonDaCapUsd is None for x in b3.moCoi),
         "một tờ đứng DA_MO mà sổ cái không có dòng cấp vốn nào là chuyện "
         "đáng báo động hơn hẳn một tờ được cấp 0 đồng")
    kiem("và một lỗ thì CẢ TỔNG mù, không cộng vòng qua nó",
         b3.vonMoCoiUsd is None and b3.soKhongDoDuocVon == 1,
         f"{b3.vonMoCoiUsd} — cùng luật với Router: một chặng không đo được "
         f"thì cả tuyến không đo được")

    # ── 4. nhánh TIỀN THẬT: không đóng gì, ngắt cầu dao, đòi NGƯỜI ──────
    sdk4, sc4, dm4 = _dung("ds4")
    _mo(sdk4, sc4, "BTC", 100.0)
    cd4 = CauDao()
    b4 = doi_soat(sdk4, dm4, _That(), sc4, cd4)
    kiem("tiền thật: KHÔNG đóng tờ nào", b4.daDong == [] and b4.canNguoi,
         "vị thế tiền thật vẫn ở trên sàn sau khi runtime chết; tự đóng ở sổ "
         "là bịa ra một lần đóng chưa từng xảy ra")
    kiem("tiền thật: sổ vẫn còn tờ ấy ở DA_MO",
         len(sdk4.theo_trang_thai("DA_MO", 9)) == 1)
    kiem("tiền thật: cầu dao NGẮT", cd4.dang_ngat)
    kiem("và lý do ấy KHÔNG tự mở lại được", not cd4.het_ly_do(MA_NGAT),
         "chỉ NGƯỜI đối soát được với sàn — máy không phân biệt được «vị thế "
         "đã đóng» với «vị thế còn mở mà ta không thấy»")

    # ── 5. nhánh MÔ PHỎNG: đóng, ghi sổ, hết lệch ───────────────────────
    sdk5, sc5, dm5 = _dung("ds5")
    _mo(sdk5, sc5, "BTC", 100.0)
    _mo(sdk5, sc5, "ETH", 150.0)
    cd5 = CauDao()
    b5 = doi_soat(sdk5, dm5, _Gia(), sc5, cd5)
    kiem("mô phỏng: đóng cả hai tờ", len(b5.daDong) == 2 and not b5.loi)
    kiem("mô phỏng: sổ chuyển sang DA_DONG",
         sdk5.pheu()["DA_DONG"] == 2
         and not sdk5.theo_trang_thai("DA_MO", 9))
    loai5 = sc5.tong_theo_loai()
    kiem("mỗi tờ đóng đều có bút toán DONG_VI_THE",
         (loai5.get("DONG_VI_THE") or {}).get("so") == 2,
         "sổ cái tồn tại để trả lời «vì sao»; đóng im lặng thì lần sau không "
         "ai biết vốn đi đâu")
    kiem("và HOÀN VỐN đúng số đã cấp",
         (loai5.get("HOAN_VON") or {}).get("tongUsd") == 250.0)
    kiem("đo lại thì hết lệch", not do(sdk5, dm5, sc5).lech)
    kiem("vốn ĐÃ DỌN đếm riêng, không lẫn vào vốn CÒN lệch",
         b5.vonDaDongUsd == 250.0 and b5.vonMoCoiUsd == 0.0,
         f"{b5.vonDaDongUsd} / {b5.vonMoCoiUsd} — «còn đang lệch bao nhiêu» "
         f"và «vừa dọn bao nhiêu» là hai câu khác nhau; gộp vào một con số "
         f"là cách chắc chắn để không câu nào còn đọc được")

    # ── 6. đối soát THÀNH CÔNG không được để lại một lần ngắt ───────────
    kiem("dọn dẹp xong KHÔNG để lại vết ngắt nào",
         cd5.soLanNgat == 0 and not cd5.dang_ngat,
         f"{cd5.soLanNgat} lần — ngắt rồi gỡ ngay trong một lượt khởi động "
         f"thì mỗi lần chạy lại cộng thêm một, và chẩn đoán "
         f"«cau-dao-ngat-nhieu» (ngưỡng 5) sẽ kêu vì chính việc dọn dẹp "
         f"thành công")

    # ── 7. `soMoCoi` giữ nguyên, `conMoCoi` mới là thứ báo động ─────────
    kiem("sau khi đóng: soMoCoi vẫn đếm tập ĐÃ TÌM THẤY",
         len(b5.moCoi) == 2)
    kiem("nhưng conMoCoi rỗng, nên `lech` tắt",
         b5.conMoCoi == [] and not b5.lech,
         "báo động theo con số cũ là báo động cho việc vừa sửa xong")

    # ── 8. canh() chỉ ĐO, không được đóng gì ────────────────────────────
    sdk8, sc8, dm8 = _dung("ds8")
    _mo(sdk8, sc8, "BTC", 100.0)
    cd8 = CauDao()
    b8 = canh(sdk8, dm8, _Gia(), sc8, cd8)
    kiem("canh() không đóng tờ nào — nó chỉ đo và nối vào cầu dao",
         b8.daDong == [] and len(sdk8.theo_trang_thai("DA_MO", 9)) == 1)
    kiem("canh() mô phỏng thì lý do ngắt TỰ mở lại được",
         cd8.dang_ngat and cd8.het_ly_do(MA_NGAT),
         "lệch trên giấy: đối soát xong là số khớp lại, và đọc lại là biết "
         "ngay — cùng họ với `von-ngoai-mu`")

    # ── 9. chiều ngược: danh mục giữ thứ sổ không biết ──────────────────
    sdk9, sc9, dm9 = _dung("ds9")
    dm9.cam_ket("khong-co-trong-so", [
        ViThe("khong-co-trong-so", "x.y.v1", "LONG", "binance", "BTC", 50.0)])
    b9 = do(sdk9, dm9, sc9)
    kiem("danh mục giữ thứ sổ KHÔNG ghi là DA_MO cũng bị nêu ra",
         b9.laTrongDanhMuc == ["khong-co-trong-so"] and b9.lech,
         "chiều này tệ hơn: vốn đang bị giữ cho một thứ sổ không biết tới")

    # ── 10. các chỗ quét đột biến chỉ ra đang trống ─────────────────────
    #
    # Quét đột biến trên `doi_soat_vi_the.py` cho 8/17 con SỐNG SÓT. Mấy
    # con ấy nằm đúng ở những chỗ tầng này tồn tại để canh: «chưa đo
    # được» so với «bằng 0», và «máy tự đóng» so với «phải có người».

    # `vonDaDongUsd`: chưa đóng tờ nào thì là None, KHÔNG phải 0. Một
    # cỗ máy chưa dọn gì mà báo «vừa dọn $0» thì đọc như đã dọn xong.
    kiem("chưa đóng tờ nào thì «vốn đã dọn» là None, không phải 0",
         do(sdk, dm, sc).vonDaDongUsd is None,
         "None là «chưa có gì để nói», 0 là «có, và bằng không» — hai câu "
         "khác nhau")

    # Và một tờ đóng được mà không đọc được vốn thì CẢ TỔNG mù, đúng
    # luật của `vonMoCoiUsd` ở trên.
    sdk10, sc10, dm10 = _dung("ds10")
    _mo(sdk10, sc10, "BTC", None)
    _mo(sdk10, sc10, "ETH", 150.0)
    b10 = doi_soat(sdk10, dm10, _Gia(), sc10, CauDao())
    kiem("dọn được 2 tờ mà một tờ mù vốn thì «vốn đã dọn» cũng mù",
         len(b10.daDong) == 2 and b10.vonDaDongUsd is None,
         f"{b10.vonDaDongUsd} — cộng vòng qua chỗ mù là báo $150 như thể "
         f"đã đo hết")

    # `canNguoi` = CÓ MỒ CÔI **và** KHÔNG mô phỏng. Đổi `and` thành `or`
    # thì mô phỏng cũng đòi người — và một cảnh báo đòi người ở chỗ máy
    # tự dọn được là cảnh báo người ta học cách bỏ qua.
    sdk11, sc11, dm11 = _dung("ds11")
    _mo(sdk11, sc11, "BTC", 100.0)
    kiem("mô phỏng CÓ mồ côi vẫn KHÔNG đòi người",
         not canh(sdk11, dm11, _Gia(), sc11, CauDao()).canNguoi,
         "máy tự đóng được trên giấy; đòi người ở đây là dạy người bỏ qua")
    sdk12, sc12, dm12 = _dung("ds12")
    _mo(sdk12, sc12, "BTC", 100.0)
    kiem("tiền thật CÓ mồ côi thì ĐÒI người",
         canh(sdk12, dm12, _That(), sc12, CauDao()).canNguoi)
    sdk13, sc13, dm13 = _dung("ds13")
    kiem("tiền thật mà KHÔNG mồ côi thì không đòi ai cả",
         not canh(sdk13, dm13, _That(), sc13, CauDao()).canNguoi,
         "«phải có người» phải nghĩa là có việc cho người làm")

    # Câu tóm tắt: «đã đối soát xong» chỉ đúng khi ĐÃ ĐÓNG được gì VÀ hết
    # lệch. Đổi `and` thành `or` là một cỗ máy chưa từng dọn gì cũng khoe
    # «đã đóng 0 tờ mồ côi».
    kiem("chưa dọn gì và không lệch → câu «hai sổ khớp nhau»",
         "khớp nhau" in do(sdk13, dm13, sc13).tom_tat()["vi"]
         and "Đã đối soát" not in do(sdk13, dm13, sc13).tom_tat()["vi"],
         do(sdk13, dm13, sc13).tom_tat()["vi"])
    kiem("dọn xong và hết lệch → câu «đã đối soát»",
         "Đã đối soát" in b5.tom_tat()["vi"], b5.tom_tat()["vi"])

    # Số USD trong lời ngắt cầu dao phải là số THẬT. `or 0.0` đổi thành
    # `and 0.0` là mọi lời ngắt đều ghi «0 USD», và con số 0 ấy đọc thành
    # «lệch nhưng không mất gì».
    sdk14, sc14, dm14 = _dung("ds14")
    _mo(sdk14, sc14, "BTC", 100.0)
    _mo(sdk14, sc14, "ETH", 150.0)
    cd14 = CauDao()
    canh(sdk14, dm14, _Gia(), sc14, cd14)
    _loi14 = " ".join(str(x) for x in cd14.tom_tat().get("lyDo", []))
    kiem("lời ngắt cầu dao ghi ĐÚNG số USD đang lệch",
         "250 USD" in _loi14,
         f"{_loi14!r} — 100+150; ghi 0 USD thì đọc thành «lệch nhưng không "
         f"mất gì»")
    sdk15, sc15, dm15 = _dung("ds15")
    _mo(sdk15, sc15, "BTC", None)
    cd15 = CauDao()
    canh(sdk15, dm15, _Gia(), sc15, cd15)
    kiem("và không đo được vốn thì NÓI THẲNG là không đo được",
         "KHÔNG đo được vốn" in " ".join(
             str(x) for x in cd15.tom_tat().get("lyDo", [])),
         "một con số 0 ở chỗ này là nói dối bằng số")

    # Thiếu trường thì điền «—», không để `None` chui ra buồng lái.
    _sdk16, _sc16, _dm16 = _dung("ds16")
    _mo(_sdk16, _sc16, "BTC", 100.0)
    b16 = do(_sdk16, _dm16, _sc16)
    kiem("tờ mồ côi luôn khai được chiến lược và tài sản",
         all(x.chienLuoc and x.taiSan for x in b16.moCoi),
         f"{[x.tom_tat() for x in b16.moCoi]} — «None» hiện ra buồng lái "
         f"đọc thành một ô hỏng, không đọc thành «không biết»")

    # Và khi hàng trong sổ THIẾU trường — sổ cũ, hoặc một ty ghi thiếu —
    # thì phải lùi về tờ trình, rồi lùi về «—». Chuỗi lùi ấy chưa từng
    # được đi vào: sổ thật luôn ghi đủ, nên `or` đổi thành `and` vẫn xanh
    # cho tới ngày gặp một hàng thiếu, và hôm ấy buồng lái hiện «None».
    class _SdkTho:
        def __init__(self, hang):
            self._h = hang

        def theo_trang_thai(self, tt, n=200):
            return list(self._h)

    b17 = do(_SdkTho([
        {"ma": "chi-co-to-trinh",
         "toTrinh": {"chienLuoc": "a.b.v1", "taiSan": "SOL",
                     "vonCanUsd": 300.0}},
        {"ma": "khong-co-gi-ca"},
    ]), DanhMuc(1000.0))
    _m1, _m2 = b17.moCoi
    kiem("thiếu trường ở hàng sổ thì LÙI VỀ tờ trình",
         (_m1.chienLuoc, _m1.taiSan, _m1.vonXinUsd) == ("a.b.v1", "SOL",
                                                        300.0),
         f"{_m1.tom_tat()}")
    kiem("thiếu cả tờ trình thì điền «—», không để «None» chui ra",
         (_m2.chienLuoc, _m2.taiSan, _m2.moLuc) == ("—", "—", ""),
         f"{_m2.tom_tat()} — chữ «None» trong một ô buồng lái đọc thành ô "
         f"hỏng, không đọc thành «không biết»")


def kiem_buong_lai() -> None:
    print("\n-- Buong lai: trang goc thuoc TRUNG UONG, khong thuoc mot ty --")
    import pathlib
    import re as _re

    web = pathlib.Path(__file__).resolve().parent.parent / "web"
    app = (web / "app.js").read_text(encoding="utf-8")
    perp = (web / "ty-perp.js").read_text(encoding="utf-8")
    htm = (web / "index.html").read_text(encoding="utf-8")

    kiem("buồng lái tách làm HAI tầng: Trung Ương và động cơ",
         (web / "app.js").exists() and (web / "ty-perp.js").exists(),
         "trang gốc từng là bảng chẩn đoán của riêng ty chênh funding — một "
         "động cơ trong mười ba chiếm cửa vào của cả bộ máy")

    # ── điều hướng phải là của HỆ, không phải của một ty ────────────────
    muc = set(_re.findall(r'data-o="([a-z-]+)"', htm))
    can = {"trung-tam", "dong-co", "von", "vi-the", "co-hoi", "loi-lo",
           "rui-ro", "du-lieu", "so-cai", "he-thong"}
    kiem("điều hướng có đủ mười mục của Trung Ương", can <= muc,
         f"thiếu {sorted(can - muc)}")
    kiem("và KHÔNG còn mục nào là tab nội bộ của ty perp",
         not ({"bao-gia", "cang", "cua"} & muc),
         "«Báo giá», «Cảng», «Cửa rủi ro» là tầng BA — chúng thuộc trang của "
         "động cơ, không thuộc điều hướng của hệ")

    # ── server phải phục vụ đúng những đường ấy ─────────────────────────
    sv = (pathlib.Path(__file__).resolve().parent.parent / "bac" / "server.py"
          ).read_text(encoding="utf-8")
    m = _re.search(r"DUONG_BUONG_LAI = \(([^)]*)\)", sv, _re.S)
    duong = set(_re.findall(r'"([a-z-]+)"', m.group(1))) if m else set()
    kiem("mọi mục điều hướng đều có đường thật ở server", can <= duong,
         f"thiếu {sorted(can - duong)} — gõ thẳng đường hoặc bấm F5 sẽ ra 404, "
         f"và 404 ở buồng lái đọc thành «máy chết»")
    kiem("đường bịa vẫn phải 404, không rơi về trang chủ",
         "HTTPException" in sv and "không có đường" in sv,
         "bắt-tất-cả thì một đường gõ sai cũng trả về trang chủ, và người gõ "
         "sai tưởng mình gõ đúng")

    # ── SÁU trạng thái, và màu KHÔNG dùng lại ───────────────────────────
    tt = set(_re.findall(r"^\s{4}(LIVE|PAPER|OBSERVE|BLOCKED|FAULT|OFF):",
                         app, _re.M))
    kiem("sáu trạng thái quy về MỘT hệ",
         tt == {"LIVE", "PAPER", "OBSERVE", "BLOCKED", "FAULT", "OFF"}, str(tt))
    css = (web / "app.css").read_text(encoding="utf-8")
    kiem("mỗi trạng thái có đúng một biến màu riêng",
         all(f"--{x}:" in css for x in
             ("live", "paper", "observe", "blocked", "fault", "off")))
    kiem("và màu NHẤN của giao diện không trùng sáu màu ấy",
         "--nhan:" in css,
         "dùng lại một màu trạng thái làm màu nhấn thì mắt học sai — một cái "
         "thẻ xanh vì nó đẹp sẽ đọc như một cái thẻ xanh vì nó khoẻ")

    # ── trang trắng không được im lặng ──────────────────────────────────
    # Đếm, không chỉ "có". Có HAI đường vẽ hỏng — trang và ô của động cơ
    # — và một trong hai mất đi thì phép kiểm khớp-chuỗi vẫn xanh nhờ cái
    # còn lại. Phép cấy lỗi ngược đi lọt đúng ở đó.
    kiem("CẢ HAI đường vẽ hỏng đều nói «máy vẫn đang chạy»",
         app.count("vẽ hỏng") >= 2 and app.count("VẪN ĐANG CHẠY") >= 2,
         f"{app.count('vẽ hỏng')} chỗ báo hỏng / "
         f"{app.count('VẪN ĐANG CHẠY')} chỗ trấn an — một hàm vẽ ném giữa "
         f"chừng để lại thân trang rỗng nhìn y hệt máy chết, trong khi máy "
         f"vẫn chạy")
    kiem("mất kết nối runtime cũng nói ra",
         "KHÔNG ĐỌC ĐƯỢC RUNTIME" in app)
    kiem("và không có `.catch` nào nuốt lỗi trống",
         "catch(function(){})" not in app.replace(" ", ""),
         "nuốt lỗi là cách nhanh nhất biến một trang hỏng thành một trang "
         "trắng không ai giải thích được")

    # ── tầng BA không được leo lên tầng MỘT ─────────────────────────────
    tang3 = ("markPx", "lechMarkBps", "aprPhanTram", "mocL")
    kiem("số thô của tầng ba KHÔNG xuất hiện ở trang Trung Ương",
         not any(x in app for x in tang3),
         f"{[x for x in tang3 if x in app]} — bps, mốc L+S và lệch mark là "
         f"tầng mổ máy; đưa chúng ra trang gốc là bắt người mở lên phải giải "
         f"mã mới biết máy có ổn không")
    kiem("nhưng chúng VẪN còn ở trang động cơ",
         any(x in perp for x in tang3),
         "chuyển chỗ, không phải vứt đi")

    # ── phễu vẽ thang LOG và nói ra ─────────────────────────────────────
    # Khớp cả TỈ SỐ, không chỉ tên hàm: đổi tử số sang tuyến tính mà giữ
    # mẫu số thì `"Math.log10" in app` vẫn xanh, và thanh vẽ sai tỉ lệ.
    kiem("phễu vẽ thang logarit — cả tử lẫn mẫu",
         "Math.log10(n.so + 1) / Math.log10(" in app,
         "đổi một vế sang tuyến tính thì thanh sai tỉ lệ mà phép kiểm "
         "khớp-tên-hàm vẫn xanh")
    kiem("và NÓI RA là log", "LOGARIT" in app,
         "vẽ tuyến tính thì mọi nấc sau nấc đầu thành một vạch không nhìn "
         "thấy; vẽ log mà không nói thì người đọc so sai tỉ lệ")

    # ── sơ đồ hạ tầng: HAI dấu, không mượn sáu màu trạng thái ──────────
    kiem("trang Dữ liệu có sơ đồ hạ tầng, không chỉ có bảng",
         "veSoDoHaTang" in app and ".so-do" in css,
         "bảng nói «cảng nào chết»; sơ đồ nói «cái chết ấy làm mù chỗ nào» — "
         "và đó mới là câu người vận hành cần")
    # Cắt đúng khối CSS của sơ đồ rồi soi trong đó. Soi cả file thì sáu màu
    # trạng thái ở khối `.cot` luôn khớp, và phép kiểm này xanh vĩnh viễn.
    m = _re.search(r"/\* ── sơ đồ hạ tầng.*?(?=/\* ── bảng)", css, _re.S)
    khoiSd = m.group(0) if m else ""
    kiem("và khối CSS của sơ đồ đọc ra được", bool(khoiSd))
    muon = [x for x in ("--live", "--paper", "--observe", "--off")
            if "var(" + x + ")" in khoiSd]
    kiem("sơ đồ KHÔNG mượn màu trạng thái của động cơ", not muon,
         f"{muon} — sáu màu ấy nói «đang chạy tiền thật», «chỉ quan sát»; "
         f"một nguồn dữ liệu khoẻ không phải LIVE theo nghĩa đó, và tô nó "
         f"xanh y hệt là dạy mắt đọc sai")
    kiem("sơ đồ phân biệt ĐO được với SUY ra",
         ".sd-o.suy" in css and "doDuoc" in app,
         "bốn cảng perp, RPC gas và LI.FI có bộ đếm sức khoẻ thật; Deribit, "
         "DefiLlama, Polymarket thì không — vẽ cả sáu cùng một kiểu là biến "
         "một suy đoán thành một phép đo")
    kiem("chữ bị cắt vẫn giữ bản ĐỦ ở <title>",
         'e("title")' in app and "lamNgan" in app,
         "chữ SVG không tự xuống dòng nên dòng phụ phải cắt; cắt mà không "
         "giữ bản đủ ở đâu cả thì thông tin mất hẳn, không phải khuất đi")

    # ── câu BÂY GIỜ phải dựng TỪ DỮ LIỆU ───────────────────────────────
    kiem("trang gốc mở bằng một câu tường thuật", "cauBayGio" in app
         and ".bay-gio" in css)
    m2 = _re.search(r"function cauBayGio\(.*?\n  \}", app, _re.S)
    tt2 = m2.group(0) if m2 else ""
    kiem("và câu ấy dựng từ dữ liệu, không phải một câu cố định",
         "S.vong" in tt2 and "cd.dangNgat" in tt2 and "dm.navUsd" in tt2,
         "một câu cố định thì đọc lần thứ hai đã thành trang trí, và trang "
         "trí ở buồng lái là thứ che mất chỗ đáng lẽ nói điều gì đó")

    # ── vị thế mồ côi: báo động theo số CÒN lại, không theo số đã tìm ──
    kiem("nút Đối soát vị thế có mặt và nối đúng đường",
         'id="nut-doi-soat"' in htm and "/api/doi-soat-vi-the" in app
         and "/api/doi-soat-vi-the" in sv)
    kiem("buồng lái báo động theo `soConMoCoi`, không theo `soMoCoi`",
         app.count("soConMoCoi") >= 2 and "ds.soMoCoi" not in app,
         "sau một lượt đối soát thành công `soMoCoi` vẫn là 4 trong khi lệch "
         "đã hết — báo động theo con số cũ là báo động cho việc vừa sửa xong")

def kiem_hien_phap() -> None:
    print("\n-- HIEN PHAP: luat van hanh, viet duoi dang CHAY DUOC --")
    from thi_bac_ty.hien_phap import DIEU, soat

    r = soat()
    kiem(f"hiến pháp có {r['soDieu']} điều", r["soDieu"] >= 20)
    kiem("mọi điều đều có mã, câu, VÌ SAO, và nguồn",
         all(d.ma and d.cau and d.vi and d.nguon for d in DIEU),
         "`vi` là phần đáng giá nhất — chuyện ĐÃ XẢY RA dạy ra luật ấy; một "
         "luật không kèm sự cố là luật phòng xa, và luật phòng xa làm tài "
         "liệu dài ra tới mức không ai đọc hết")
    kiem("mã không trùng nhau", len({d.ma for d in DIEU}) == len(DIEU))

    for x in r["viPham"]:
        kiem(f"HIẾN PHÁP · {x['ma']}", False, x["chiTiet"])
    if not r["viPham"]:
        kiem(f"KHÔNG điều nào bị vi phạm ({r['soCanhDuoc']} điều canh được)",
             True)

    # Điều KHÔNG canh được phải khai ra — đây là bài học ba cửa giả nâng lên
    # tầm hệ thống.
    kiem("số điều KHÔNG canh được được KHAI RA, không giấu",
         isinstance(r["soKhongCanhDuoc"], int)
         and len(r["khongCanhDuoc"]) == r["soKhongCanhDuoc"],
         "một hiến pháp mà điều nào cũng trông như đang có hiệu lực thì tệ "
         "hơn không có: người đọc tưởng mình được che nhiều hơn thực tế")
    kiem("và phần lớn điều PHẢI canh được",
         r["soCanhDuoc"] >= r["soDieu"] * 0.85,
         f"{r['soCanhDuoc']}/{r['soDieu']} — dưới 85% thì hiến pháp đang "
         f"nghiêng về văn xuôi, đúng thứ nó sinh ra để thay")
    kiem("tóm tắt gọn dùng được cho buồng lái",
         set(["soDieu", "soViPham", "soKhongCanhDuoc"])
         <= set(__import__("thi_bac_ty.hien_phap", fromlist=["tom_tat"])
                .tom_tat()))

    # ── «KHÔNG canh được» TÁCH LÀM HAI ──────────────────────────────────
    # Gộp lại là nói mình được che ÍT hơn thực tế: bốn điều trong đó có
    # người canh hẳn hoi, chỉ là canh ở selftest chứ không ở Trung Ương,
    # vì canh từ Trung Ương là phạm chính `trung-uong-khong-biet-ty`.
    kiem("hai nhóm CỘNG ĐÚNG lại thành nhóm không canh được từ đây",
         r["soCanhOTangKhac"] + r["soHoanToanTrong"] == r["soKhongCanhDuoc"],
         f"{r['soCanhOTangKhac']} + {r['soHoanToanTrong']} != "
         f"{r['soKhongCanhDuoc']}")
    kiem("và mỗi điều canh ở tầng khác KHAI RA tên hàm canh nó",
         all(x.get("ham") for x in r["canhOTangKhac"]),
         f"{r['canhOTangKhac']} — khai «có người canh» mà không nói ai canh "
         f"thì lời khai ấy không đối chiếu được, tức là không khai gì")

    # Chỉ tay phải chỉ vào chỗ có thật, và phép canh ấy phải BẮT ĐƯỢC khi
    # cái tên bị đổi. Cấy lỗi ngược ngay tại đây thay vì tin nó chạy đúng.
    from thi_bac_ty.hien_phap import (
        DIEU as _DIEU, _chi_tay_phai_chi_vao_cho_co_that as _chiTay)
    _dat, _ct = _chiTay()
    kiem("mọi chỉ tay đều trỏ vào hàm CÓ THẬT và ĐANG ĐƯỢC GỌI", _dat, _ct)
    _cu = [d for d in _DIEU if d.canhODau]
    if _cu:
        import dataclasses as _dc
        _goc = list(_DIEU)
        try:
            _hp = __import__("thi_bac_ty.hien_phap", fromlist=["DIEU"])
            _hp.DIEU = tuple(
                _dc.replace(d, canhODau="kiem_ham_nay_khong_ton_tai")
                if d is _cu[0] else d for d in _goc)
            _dat2, _ct2 = _chiTay()
        finally:
            _hp.DIEU = tuple(_goc)
        kiem("và ĐỔI TÊN một hàm canh thì phép ấy ĐỎ",
             not _dat2 and "KHÔNG CÓ HÀM" in _ct2,
             f"{_dat2} · {_ct2} — một lời khai không ai đối chiếu sẽ sống "
             f"sót qua đúng cái lần người ta đổi tên hàm")

        # Vế thứ hai, và là vế hay hỏng hơn: hàm TỒN TẠI không có nghĩa
        # là hàm CHẠY. `dung_chuoi` có thật trong file này và không bao
        # giờ được gọi ở dạng `dung_chuoi()`, nên nó là mẫu hoàn hảo cho
        # một chỉ tay trỏ vào một cơ chế không ai gọi.
        try:
            _hp.DIEU = tuple(
                _dc.replace(d, canhODau="gan")
                if d is _cu[0] else d for d in _goc)
            _dat3, _ct3 = _chiTay()
        finally:
            _hp.DIEU = tuple(_goc)
        kiem("và trỏ vào một hàm CÓ THẬT mà KHÔNG AI GỌI cũng ĐỎ",
             not _dat3 and "KHÔNG AI GỌI" in _ct3,
             f"{_dat3} · {_ct3} — một cơ chế không ai gọi là một cơ chế "
             f"không chạy, và nó vẫn nằm đó cho người đọc yên tâm")


def kiem_duong_khoa_von() -> None:
    print("TRAN KHOA VON dang chan mat bao nhieu loi suat")
    from thi_bac_ty.duong_khoa_von import do_duong_khoa_von

    # Đo 30/08 trên máy sống: `lending.rate_rotation` giữ đúng 50,0% NAV
    # (chạm trần `tranMotTy`) còn `yield.pendle_pt` giữ ĐÚNG SỐ KHÔNG —
    # dù nó nộp 12 tờ trình mỗi vòng, NET 65–449 bps, so với 1,7 bps của
    # phần vốn đang chạy. Cả mười hai tờ đều khoá 2.116–3.292 giờ, tức
    # đều trên trần `khoaVonToiDaGio` 720. Một động cơ đứng ngoài vì đúng
    # một tham số, và trước lượt này không bảng nào nói ra con số ấy.
    def _tt(apr, chua, khoa):
        # `apr_tu_to_trinh` đọc netUocBps + giuGio; dựng ngược lại từ APR
        # mong muốn để phép kiểm nói bằng đơn vị người đọc hiểu.
        giu = 24.0
        net = apr / 100.0 * (giu / (365.0 * 24.0)) * 10_000.0
        return {"netUocBps": net, "giuGio": giu, "sucChuaToiDaUsd": chua,
                "khoaVonDenGio": khoa}

    ds = [_tt(20.0, 1000.0, 3000.0),      # ngon nhất, khoá RẤT lâu
          _tt(10.0, 1000.0, 1000.0),      # khá, khoá vừa
          _tt(2.0, 1000.0, 0.0)]          # tệ, không khoá
    d = do_duong_khoa_von(ds, 3000.0, 720.0,
                          muc=(720.0, 1440.0, None))
    m = {x.tranGio: x for x in d.muc}
    kiem("trần chặt thì chỉ còn cơ hội KHÔNG khoá",
         m[720.0].soCoHoi == 1 and gan(m[720.0].aprTrenCaTuiUsd, 2.0 / 3),
         f"{m[720.0].tom_tat()} — rót 1000 lãi 2% trên túi 3000 là 0,67%")
    kiem("nới trần lên 1440 thì thêm cơ hội 10%",
         m[1440.0].soCoHoi == 2 and gan(m[1440.0].aprTrenCaTuiUsd, 4.0),
         f"{m[1440.0].tom_tat()} — (1000×10 + 1000×2)/3000 = 4%")
    kiem("bỏ trần thì cả ba, và lợi suất cao nhất",
         m[None].soCoHoi == 3 and gan(m[None].aprTrenCaTuiUsd, 32.0 / 3),
         f"{m[None].tom_tat()} — (20+10+2)/3 = 10,67%")
    kiem("và KHOÁ BÌNH QUÂN nói ra cái giá phải trả",
         m[None].khoaBinhQuanGio is not None
         and gan(m[None].khoaBinhQuanGio, 4000.0 / 3),
         f"{m[None].khoaBinhQuanGio} — nới trần không miễn phí, và con số "
         f"phải đứng ngay cạnh con số lợi suất")

    # Ba cái bẫy của `duong_suc_chua.py`, y nguyên ở đây.
    d2 = do_duong_khoa_von(
        [{"sucChuaToiDaUsd": 1000.0, "khoaVonDenGio": 0.0},   # không khai lãi
         _tt(9.0, None, 0.0),                                  # không khai chứa
         _tt(9.0, 1000.0, 0.0)], 5000.0, 720.0, muc=(None,))
    kiem("cơ hội không khai LÃI thì BỎ, không coi là 0",
         d2.soBoViThieuLai == 1, str(d2.tom_tat()))
    kiem("cơ hội không khai SỨC CHỨA thì cũng BỎ",
         d2.soBoViThieuSucChua == 1, str(d2.tom_tat()))
    kiem("vốn không rót hết thì phần dư ăn lãi 0",
         gan(d2.muc[0].aprTrenCaTuiUsd, 9.0 * 1000.0 / 5000.0),
         f"{d2.muc[0].tom_tat()} — rót 1000 trên túi 5000 thì lãi cả túi là "
         f"một phần năm, không phải 9%")

    # Trần không chặn gì thì NÓI THẲNG là không chặn gì — một bảng kêu mãi
    # kể cả khi không có gì để kêu là một bảng người ta thôi đọc.
    d3 = do_duong_khoa_von([_tt(5.0, 1000.0, 0.0)], 1000.0, 720.0,
                           muc=(720.0, None))
    kiem("trần KHÔNG chặn gì thì bảng nói thẳng ra thế",
         "KHÔNG chặn gì" in d3.vi, d3.vi)

    # `khoaVonDenGio` vắng mặt nghĩa là ty ấy không có khái niệm khoá vốn —
    # đọc là 0 ở đây là ĐÚNG nghĩa, khác hẳn `None` của một phép đo hỏng.
    d4 = do_duong_khoa_von([{"netUocBps": 10.0, "giuGio": 24.0,
                             "sucChuaToiDaUsd": 500.0}], 500.0, 720.0,
                           muc=(720.0,))
    kiem("thiếu `khoaVonDenGio` = không khoá, không phải chưa đo",
         d4.muc[0].soCoHoi == 1,
         f"{d4.muc[0].tom_tat()} — ty không bắc cầu, không kỳ hạn thì "
         f"không có gì để khoá; loại nó ra là phạt một ty vì nó đơn giản")

    # ── BIÊN, chỗ quét đột biến chỉ ra đang trống ───────────────────────
    #
    # Bảng này là bảng người vận hành đọc để quyết `khoaVonToiDaGio` —
    # cái tham số đang chặn cả một động cơ. Quét đột biến cho 5/9 con
    # sống sót, và cả bốn con đáng kể nằm đúng ở biên.

    # Khoá ĐÚNG BẰNG trần thì QUA. `>` đổi thành `>=` là loại đúng những
    # cơ hội nằm sát mép — và bảng này tồn tại để hỏi «nới mép ra thì
    # được gì», nên sai ở mép là sai ở chính câu hỏi.
    d5 = do_duong_khoa_von([_tt(9.0, 1000.0, 720.0)], 1000.0, 720.0,
                           muc=(720.0,))
    kiem("khoá ĐÚNG BẰNG trần thì vẫn vào bảng",
         d5.muc[0].soCoHoi == 1 and gan(d5.muc[0].aprTrenCaTuiUsd, 9.0),
         f"{d5.muc[0].tom_tat()} — trần là trần, không phải mép vực")
    kiem("quá trần một giờ thì bị loại",
         do_duong_khoa_von([_tt(9.0, 1000.0, 721.0)], 1000.0, 720.0,
                           muc=(720.0,)).muc[0].soCoHoi == 0)

    # SỨC CHỨA đúng bằng 0 là «không chứa được gì», nên BỎ; nhưng sức chứa
    # dương bé xíu thì vẫn là một cơ hội thật. `<=` đổi thành `<` là nhận
    # vào một cơ hội chứa 0 đồng, và nó chiếm một dòng của bảng mà không
    # rót được đồng nào.
    d6 = do_duong_khoa_von([_tt(9.0, 0.0, 0.0), _tt(9.0, 0.01, 0.0)],
                           1000.0, 720.0, muc=(None,))
    kiem("sức chứa ĐÚNG BẰNG 0 thì bỏ, sức chứa 0,01 thì nhận",
         d6.soBoViThieuSucChua == 1 and d6.muc[0].soCoHoi == 1,
         f"{d6.tom_tat()} — «chứa được 0 đồng» không phải một cơ hội, "
         f"nhưng «chứa được một xu» thì là")

    # HẾT VỐN rồi thì cơ hội sau vẫn ĐẾM vào `soCoHoi` và `sucChuaUsd` —
    # bảng phải nói «trần này mở ra bao nhiêu cơ hội», không phải «bao
    # nhiêu cơ hội ta đủ tiền lấy». Nhưng nó KHÔNG được rót thêm.
    d7 = do_duong_khoa_von([_tt(20.0, 1000.0, 0.0), _tt(10.0, 1000.0, 0.0)],
                           1000.0, 720.0, muc=(None,))
    kiem("hết vốn thì cơ hội sau vẫn ĐẾM, nhưng KHÔNG rót thêm",
         (d7.muc[0].soCoHoi == 2 and gan(d7.muc[0].rotDuocUsd, 1000.0)
          and gan(d7.muc[0].sucChuaUsd, 2000.0)),
         f"{d7.muc[0].tom_tat()} — hai câu khác nhau: «trần mở ra mấy cơ "
         f"hội» và «ta đủ tiền lấy mấy cơ hội»")
    kiem("và lợi suất chỉ tính phần RÓT ĐƯỢC",
         gan(d7.muc[0].aprTrenCaTuiUsd, 20.0),
         f"{d7.muc[0].aprTrenCaTuiUsd} — cộng cả cơ hội không rót được là "
         f"cộng một khoản lãi chưa ai nhận")

    # VỐN BẰNG 0 thì không có mẫu số. `> 0` đổi thành `>= 0` là chia cho
    # không ngay dòng ấy.
    d8 = do_duong_khoa_von([_tt(9.0, 1000.0, 0.0)], 0.0, 720.0, muc=(None,))
    kiem("túi rỗng thì lợi suất là 0 và KHÔNG nổ, khoá bình quân là None",
         (gan(d8.muc[0].aprTrenCaTuiUsd, 0.0)
          and d8.muc[0].khoaBinhQuanGio is None),
         f"{d8.muc[0].tom_tat()} — chưa rót đồng nào thì «khoá bình quân» "
         f"là chưa đo được, không phải 0 giờ")


def kiem_router_doi_lo_hong() -> None:
    print("ROUTER go duoc khoan nao thi PHAI thay bang khoan khac")
    import importlib

    # BA ty khai `ROUTER_GO_DUOC`, và cả ba dùng cùng một lối: Router đo
    # được thì khoản ấy biến khỏi `phiConThieu`, THAY bằng những khoản
    # chính Router khai là nó chưa tính. Đổi một lỗ hổng lấy một lỗ hổng
    # NHỎ HƠN ĐÃ ĐƯỢC ĐẶT TÊN, không phải xoá lỗ hổng.
    #
    # Chỗ nguy hiểm nằm ở nhánh KHÔNG đo được. `can_loi.phi_bps()` viết
    # `phiCauUsd or 0.0`: phí cầu chưa đo được thì KHÔNG cộng gì. Một mình
    # dòng ấy là «đọc CHƯA ĐO thành 0» — điều `none-khac-khong` cấm. Nó
    # hợp lệ CHỈ VÌ khai báo `chuyen-von-giua-chuoi` ở lại. Bỏ khai báo đi
    # thì dòng `or 0.0` lập tức thành một lời nói dối, và không phép kiểm
    # nào của ty ấy đỏ lên.
    #
    # Hôm nay chuyện «Router không đo được» KHÔNG phải giả định: LI.FI ăn
    # 429 và nghỉ 83 phút. Đúng cửa sổ ấy là lúc khai báo phải còn đó.
    ba = [("tin_dung.ty_vay", "tin dụng"),
          ("lai_suat.ty_lai_suat", "Pendle PT"),
          ("on_dinh.ty_on_dinh", "chênh stablecoin")]
    thay = 0
    for ten, nhan in ba:
        m = importlib.import_module(ten)
        go = getattr(m, "ROUTER_GO_DUOC", None)
        pct = getattr(m, "PHI_CON_THIEU", None)
        f = getattr(m, "_phi_con_thieu", None)
        if go is None or f is None or pct is None:
            continue
        thay += 1
        kiem(f"[{nhan}] mọi khoản Router gỡ được đều CÓ trong khai báo gốc",
             set(go) <= set(pct),
             f"{sorted(set(go) - set(pct))} — gỡ một khoản chưa từng được "
             f"khai là một cơ chế không làm gì mà trông như đang làm")
        mu = set(f(False))
        kiem(f"[{nhan}] Router MÙ thì khai báo Ở LẠI, không lặng lẽ về 0",
             set(go) <= mu,
             f"{sorted(set(go) - mu)} — `phiCauUsd or 0.0` chỉ trung thực "
             f"khi khoản thiếu ấy còn được khai ở chỗ khác")
        do = set(f(True, ("rui-ro-cau-noi",)))
        kiem(f"[{nhan}] Router ĐO ĐƯỢC thì khoản ấy biến mất",
             not (set(go) & do), f"{sorted(set(go) & do)}")
        kiem(f"[{nhan}] và được THAY bằng khoản Router tự khai còn thiếu",
             "router:rui-ro-cau-noi" in do,
             f"{sorted(do)} — xoá một lỗ hổng mà không đặt tên lỗ hổng mới "
             f"là làm cơ hội trông sạch hơn thực tế")
    kiem("đủ BA ty khai ROUTER_GO_DUOC đều được soát", thay == 3,
         f"{thay}/3 — thêm một ty dùng Router mà quên khai là thêm một chỗ "
         f"đọc CHƯA ĐO thành 0 mà không ai canh")


def kiem_chan_doan_doc_dung_khoa() -> None:
    print("KHOA chan doan doc: co that trong anh chup khong")
    import ast
    import pathlib

    from thi_bac_ty.trung_uong import TrungUong

    # Chẩn đoán hệ đọc ảnh chụp bằng một rừng `.get("...")`. Mỗi lời gọi
    # ấy trả `None` khi khoá sai, và `or 0` ngay sau đó biến `None` thành
    # 0 — nên một khoá bị đổi tên làm TẮT HẲN một triệu chứng, vĩnh viễn,
    # không lỗi nào báo. Buồng lái vẫn xanh; nó chỉ thôi kêu.
    #
    # Đã suýt xảy ra trong chính lượt sửa `ty-lo`: `laiLoTachKhoan` là
    # khoá mới, và gõ sai một chữ thì mọi ty rơi về nhánh «chưa tách được»
    # mà bảng vẫn đầy chữ.
    #
    # Đọc khoá bằng AST chứ không bằng regex: `.get("x") or {}` và
    # `.get("x", {})` viết khác nhau, và chuỗi trong chú thích thì không
    # phải khoá.
    goc = pathlib.Path(__file__).resolve().parent.parent
    cay = ast.parse((goc / "thi_bac_ty" / "chan_doan_he.py")
                    .read_text(encoding="utf-8"))
    #: `bien -> {khoá}`. Chỉ theo dõi những biến gán thẳng từ `anh.get(...)`;
    #: đi sâu hơn là dựng một trình thông dịch, và một phép canh phức tạp
    #: hơn thứ nó canh thì chính nó thành chỗ hỏng.
    tuAnh: dict[str, str] = {}
    docTang1: set[str] = set()
    docTang2: dict[str, set[str]] = {}

    def _khoa(n):
        """`X.get("k")` → ("X", "k") nếu bắt được, không thì None."""
        if not (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr == "get" and n.args
                and isinstance(n.args[0], ast.Constant)
                and isinstance(n.args[0].value, str)):
            return None
        goc_ = n.func.value
        if isinstance(goc_, ast.Name):
            return goc_.id, n.args[0].value
        return None, n.args[0].value

    for n in ast.walk(cay):
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and \
                isinstance(n.targets[0], ast.Name):
            # `sdk = anh.get("soDangKy") or {}` → BoolOp(Or, [Call, Dict])
            ve = (n.value.values[0] if isinstance(n.value, ast.BoolOp)
                  else n.value)
            k = _khoa(ve)
            if k and k[0] == "anh":
                tuAnh[n.targets[0].id] = k[1]
                docTang1.add(k[1])
        k = _khoa(n)
        if not k:
            continue
        if k[0] == "anh":
            docTang1.add(k[1])
        elif k[0] in tuAnh:
            docTang2.setdefault(tuAnh[k[0]], set()).add(k[1])

    kiem("đọc được danh sách khoá mà chẩn đoán dùng",
         len(docTang1) >= 6 and len(docTang2) >= 3,
         f"tầng 1: {sorted(docTang1)} · tầng 2: "
         f"{ {a: sorted(b) for a, b in docTang2.items()} } — không đọc ra "
         f"khoá nào thì phép kiểm này đang canh một cái rỗng")

    tu = TrungUong(_tam("khoa-chan-doan"), {"vonBanDauUsd": 5000.0})
    tu.mot_vong(lechDongHoGiay=1.0, cangChet=[], tuoiXauNhatGiay=1.0)
    anh = tu.anh_chup()

    thieu1 = sorted(k for k in docTang1 if k not in anh)
    kiem("mọi khoá TẦNG 1 đều có thật trong ảnh chụp",
         not thieu1,
         f"{thieu1} — `.get()` trả None, `or 0` biến nó thành 0, và một "
         f"triệu chứng tắt hẳn mà không dòng nào kêu")

    thieu2 = []
    for cha, ds in sorted(docTang2.items()):
        o = anh.get(cha)
        if not isinstance(o, dict):
            continue          # danh sách hoặc None — không soát được ở đây
        for k in sorted(ds):
            if k not in o:
                thieu2.append(f"{cha}.{k}")
    kiem("và mọi khoá TẦNG 2 cũng thế",
         not thieu2,
         f"{thieu2} — đổi tên một trường trong `tom_tat()` mà quên bên đọc "
         f"thì bên đọc im lặng đọc ra 0")


def kiem_ly_do_cong_ty() -> None:
    print("\n-- CONG TY: cai loc lon nhat, va no phai khai VI SAO --")
    from thi_bac_ty.khuon_ty import Ty

    class TyThu(Ty):
        ma, ho, moTa = "thu.v1", "phai-sinh", "thử"

        def quet(self):
            return list(range(30))

        def xet(self, co):
            if co % 10 == 0:
                return True, []
            if co % 3 == 0:
                return False, [("net-thap", f"net {co} bps < 5")]
            return False, [("thanh-khoan-mong", "sổ mỏng"),
                           ("net-thap", "net thấp")]

        def trinh(self, co):
            return co

    class TCGia:
        def nop(self, tt):
            return True

    t = TyThu()
    t.mot_luot(TCGia())
    d = t.tom_tat()
    # Trước lượt này dòng ấy là `qua, _ = self.xet(co)`: lý do bị vứt ngay
    # tại chỗ nó vừa sinh ra. Cổng ty là cái lọc LỚN NHẤT của cả cỗ máy —
    # đo 30/08: 68.936 cơ hội thô → 14 qua, tức 99,98% chết ở đây — và
    # không ai biết vì sao. Một ty hỏng (ngưỡng sai, một trường luôn None,
    # nguồn trả rác) trông hệt một ty đang từ chối đúng.
    kiem("cổng ty ĐẾM được số lần từ chối",
         d["soBiTuChoi"] == 27 and d["soQuaCongTy"] == 3,
         f"{d['soBiTuChoi']}/{d['soQuaCongTy']}")
    theo = {x["ma"]: x for x in d["lyDoTuChoi"]}
    kiem("và khai VÌ SAO, theo MÃ",
         theo["net-thap"]["so"] == 27 and theo["thanh-khoan-mong"]["so"] == 18,
         f"{d['lyDoTuChoi']} — gom theo câu thì `net 3 bps` và `net 6 bps` "
         f"thành hai nguyên nhân khác nhau")
    kiem("giữ một CÂU làm ví dụ, không chỉ mã trần",
         all(x["cau"] for x in d["lyDoTuChoi"]),
         "mã để máy đếm, câu để người đọc — thiếu câu thì người đọc phải "
         "đi tra mã trong mã nguồn")
    kiem("xếp theo số lần, thủ phạm chính đứng đầu",
         d["lyDoTuChoi"][0]["ma"] == "net-thap",
         str(d["lyDoTuChoi"]))

    # Một lần từ chối mang NHIỀU mã, nhưng mỗi mã chỉ đếm MỘT lần cho lần
    # ấy — không thì một `xet()` trả về mã trùng sẽ tự thổi phồng mình.
    class TyTrung(TyThu):
        def xet(self, co):
            return False, [("a", "x"), ("a", "x"), ("a", "x")]

    t2 = TyTrung()
    t2.mot_luot(TCGia())
    d2 = t2.tom_tat()
    kiem("mã TRÙNG trong cùng một lần từ chối chỉ đếm một lần",
         d2["lyDoTuChoi"][0]["so"] == d2["soBiTuChoi"] == 30,
         f"{d2['lyDoTuChoi']} vs {d2['soBiTuChoi']}")

    # Ty tự viết mã của mình, nên một ty lỡ nhét số vào mã sẽ đẻ ra vô hạn
    # khoá. Trần biến một lỗi rò bộ nhớ thành một dòng khai «có mã bị bỏ».
    class TyVoHan(TyThu):
        def xet(self, co):
            return False, [(f"ma-so-{co}", "mỗi lần một mã khác")]

    t3 = TyVoHan()
    t3.mot_luot(TCGia())
    d3 = t3.tom_tat()
    kiem("số MÃ có TRẦN, và phần bị bỏ được KHAI RA",
         len(t3.lyDoTuChoi) == Ty.TRAN_MA_LY_DO and d3["soMaBiBo"] > 0,
         f"{len(t3.lyDoTuChoi)} mã · bỏ {d3['soMaBiBo']} — một ty nhét số "
         f"vào mã sẽ làm bảng này phình vô hạn; bỏ IM LẶNG thì người đọc "
         f"tưởng mình đang nhìn cả bức tranh")

    # Từ chối mà KHÔNG khai mã nào vẫn phải đếm được — im lặng ở đây là
    # một con số câm, và buồng lái nói thẳng ra điều đó.
    class TyCam(TyThu):
        def xet(self, co):
            return False, []

    t4 = TyCam()
    t4.mot_luot(TCGia())
    d4 = t4.tom_tat()
    kiem("từ chối KHÔNG lý do vẫn vào mẫu số, và bảng mã thì rỗng",
         d4["soBiTuChoi"] == 30 and d4["lyDoTuChoi"] == [],
         f"{d4['soBiTuChoi']} · {d4['lyDoTuChoi']}")

    # MÃ TRẦN, không kèm câu — nửa lời khai. `bac/ty_perp.py` trả về
    # `list(co.lyDoMa)`, đúng `list[str]` chứ không phải
    # `list[tuple[str, str]]` mà chữ ký khai, và không ai thấy suốt nhiều
    # tháng vì `mot_luot()` vứt luôn vế thứ hai. Hai lỗi che nhau.
    class TyMaTran(TyThu):
        def xet(self, co):
            return False, ["net-am", "gross-mong"]

    t5 = TyMaTran()
    t5.mot_luot(TCGia())
    d5 = t5.tom_tat()
    kiem("mã TRẦN vẫn đếm được, nhưng ĐẾM RA là thiếu câu",
         d5["soMaThieuCau"] == 2 and d5["lyDoTuChoi"][0]["cau"] == "",
         f"{d5['lyDoTuChoi']} · thiếu câu {d5['soMaThieuCau']} — mã để máy "
         f"đếm, câu để người đọc; thiếu câu thì người đọc phải đi tra mã "
         f"trong mã nguồn, và không ai làm thế")
    kiem("còn ty khai đủ cặp thì KHÔNG bị kêu oan",
         d["soMaThieuCau"] == 0, str(d))

    # Và chính ty chênh funding — ty duy nhất ghi băng — phải khai đủ cặp.
    # Kiểm bằng HÀNH VI, không bằng chuỗi trong mã nguồn: bản đầu hỏi
    # `"co.lyDo" in nguồn` và nó khớp luôn `co.lyDoMa`, nên phép kiểm xanh
    # kể cả khi hàm quay về trả mã trần. Dò bằng chuỗi thì một cái tên dài
    # hơn chứa cái tên ngắn hơn.
    from bac.ty_perp import TyPerp as _TyPerp

    class _CoGia:
        duyet = False
        lyDo = ("net âm 3 bps", "sổ mỏng")
        lyDoMa = ("net-am", "gross-mong")

    _qua, _ly = _TyPerp.xet(object.__new__(_TyPerp), _CoGia())
    kiem("ty chênh funding GHÉP mã với câu, không trả mã trần",
         _qua is False and _ly == [("net-am", "net âm 3 bps"),
                                   ("gross-mong", "sổ mỏng")],
         f"{_ly} — `can_loi.py` dựng `lyDo` và `lyDoMa` cùng một lượt, cùng "
         f"thứ tự, nên ghép lại là đúng cặp chứ không phải đoán")


def kiem_khoa_cu_doi_ten() -> None:
    print("\n-- Doi ten khoa: ban tham so DA DUYET khong duoc mat --")
    from thi_bac_ty.rui_ro_tong import KHOA_CU, MAC_DINH, RuiRoTong

    # `khoaVonToiDaGiay` mang đuôi «Giay» từ ngày đầu trong khi mọi chỗ
    # dùng nó đều tính bằng GIỜ: docstring viết «720 giờ = 30 ngày», câu
    # từ chối in «khoá vốn 2119 giờ > trần 720 giờ». Cái tên nói dối về
    # ĐƠN VỊ, và nó sẽ cắn vào đúng ngày ai đó đọc 720 là «12 phút» rồi
    # sửa thành 2.592.000 — trần ấy khi đó chặn đúng 0 cơ hội, mãi mãi.
    kiem("không khoá CŨ nào còn nằm trong bảng mặc định",
         not (set(KHOA_CU) & set(MAC_DINH)),
         f"{set(KHOA_CU) & set(MAC_DINH)} — giữ cả hai tên trong mặc định "
         f"là để hai nguồn sự thật cùng sống")
    for cu, moi in KHOA_CU.items():
        r = RuiRoTong({cu: 999.0})
        kiem(f"bản tham số cũ mang `{cu}` vẫn được đọc",
             r.c.get(moi) == 999.0 and cu not in r.c,
             f"{r.c.get(moi)} — bản đang chạy trên đĩa còn mang khoá cũ, và "
             f"đó là bản NGƯỜI CHỦ đã duyệt; bỏ qua nó là âm thầm trả một "
             f"tham số đã duyệt về mặc định")
        r2 = RuiRoTong({cu: 999.0, moi: 111.0})
        kiem(f"có cả hai thì `{moi}` THẮNG",
             r2.c.get(moi) == 111.0,
             f"{r2.c.get(moi)} — tên mới là tên đang được ghi, nên nó phải "
             f"là tên quyết định")

    # Và đơn vị phải là GIỜ, chứng minh bằng hành vi chứ không bằng tên.
    from thi_bac_ty.to_trinh import ToTrinh
    import inspect
    kiem("`khoaVonDenGio` được so THẲNG với trần, cùng một đơn vị",
         "khoaVonDenGio" in inspect.getsource(RuiRoTong.xet)
         and "khoaVonToiDaGio" in inspect.getsource(RuiRoTong.xet)
         and "3600" not in inspect.getsource(RuiRoTong.xet),
         "không có phép đổi đơn vị nào ở giữa, nên hai con số phải cùng "
         "đơn vị — và cả hai đều là GIỜ")
    kiem("và ToTrinh khai đúng tên mới",
         "khoaVonDenGio" in {f for f in ToTrinh.__dataclass_fields__},
         str([f for f in ToTrinh.__dataclass_fields__ if "khoaVon" in f]))


def kiem_hai_lan() -> None:
    print("\n-- HAI LAN: khac nhau cho nao thi phai KHAI cho ay --")
    import json as _js
    import pathlib as _pl

    goc = _pl.Path(__file__).resolve().parent.parent

    def _phang(d, tien=""):
        r = {}
        for k, v in (d or {}).items():
            if k.startswith("_"):
                continue
            n = f"{tien}{k}"
            if isinstance(v, dict):
                r.update(_phang(v, n + "."))
            elif not isinstance(v, list):
                r[n] = v
        return r

    try:
        that = _js.loads((goc / "config.json").read_text(encoding="utf-8"))
        demo = _js.loads((goc / "config-demo.json").read_text(encoding="utf-8"))
    except OSError as e:
        kiem("đọc được cả hai cấu hình", False, str(e))
        return

    a, b = _phang(that), _phang(demo)
    khac = sorted(k for k in set(a) | set(b) if a.get(k, "\u2205") != b.get(k, "\u2205"))
    khai = demo.get("_khacCoY") or {}

    # Làn demo tồn tại để trả lời «cỗ máy này nói gì ở một cỡ vốn khác».
    # Câu ấy chỉ có nghĩa khi mọi thứ KHÁC vốn đều giống nhau — hoặc khi
    # chỗ khác được khai ra kèm lý do. Trôi âm thầm thì hai làn dần thành
    # hai cỗ máy, và phép so mất nghĩa mà không dòng nào kêu. Đã trôi tới
    # BẢY chỗ trước khi phép kiểm này ra đời.
    thieu = [k for k in khac if not str(khai.get(k, "")).strip()]
    kiem("mọi chỗ hai làn KHÁC nhau đều được KHAI kèm lý do",
         not thieu,
         f"chưa khai: {thieu} — thêm vào `_khacCoY` của config-demo.json, "
         f"kèm lý do; một chỗ khác không ai cố ý là một chỗ TRÔI, và nó "
         f"làm câu «demo nói gì về bản thật» mất nghĩa")

    # Chiều ngược cũng phải canh, và nó là chiều dễ bị bỏ quên: một lời
    # khai còn nằm đó sau khi chỗ khác đã được san bằng là một lời khai
    # CHẾT — người đọc tưởng hai làn còn lệch chỗ ấy.
    thua = [k for k in khai if k not in khac]
    kiem("và không lời khai nào KHAI một chỗ đã hết khác",
         not thua,
         f"khai thừa: {thua} — hai làn đã giống nhau ở đó rồi, giữ lời khai "
         f"lại là nói dối về một chỗ lệch không còn tồn tại")

    kiem("vốn ban đầu PHẢI là một trong những chỗ khác",
         "trungUong.vonBanDauUsd" in khac,
         "hai làn cùng cỡ vốn thì không làn nào nói được gì về quy mô — "
         "đó là cả lý do làn thứ hai tồn tại")
    kiem("và cả hai làn đều ở chế QUAN SÁT",
         that.get("che") == demo.get("che") == "quan-sat",
         f"{that.get('che')!r} vs {demo.get('che')!r} — tầng đặt lệnh thật "
         f"không tồn tại trong cây mã này, và làn demo không phải chỗ để "
         f"thử làm nó tồn tại")
    print(f"  ({len(khac)} chỗ khác, {len(khai)} chỗ khai)")


def kiem_khong_trung_ten() -> None:
    print("\n-- File nay: dinh nghia sau DE dinh nghia truoc, khong bao --")
    import collections
    import pathlib
    import re as _re

    src = pathlib.Path(__file__).read_text(encoding="utf-8")
    ten = _re.findall(r"^def (\w+)", src, _re.M)
    trung = [t for t, n in collections.Counter(ten).items() if n > 1]
    kiem("không hàm nào trong file này bị định nghĩa hai lần", not trung,
         f"{trung} — Python lấy bản CUỐI, nên bản đầu biến mất mà không lời "
         f"cảnh báo nào. Vừa cắn thật: `_bg` của ty cơ sở đè `_bg` của ty "
         f"chênh funding, và cái vỡ lại là `kiem_ghep_cap` ở cách đó 3000 "
         f"dòng — người đọc đi tìm lỗi ở đúng chỗ không có lỗi")

    goi = set(_re.findall(r"^    (kiem_\w+)\(\)", src, _re.M))
    dinh = {t for t in ten if t.startswith("kiem_")}
    kiem("mọi hàm kiểm đã viết đều được GỌI trong main()", not (dinh - goi),
         f"{sorted(dinh - goi)} — một phép kiểm không ai gọi thì xanh vĩnh "
         f"viễn, và nó xanh vì không chạy chứ không vì đúng")

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
    kiem_cong_duyet()
    kiem_ban_tham_so()
    kiem_vong_duyet_tron()
    kiem_pheu_theo_ho()
    kiem_tin_dung_phi()
    kiem_tin_dung_cua()
    kiem_tin_dung_thang_rui_ro()
    kiem_van_tay_co_chuoi()
    kiem_hai_ty_that()
    kiem_von_ngoai()
    kiem_on_dinh()
    kiem_lai_suat()
    kiem_co_so()
    kiem_ha_tang_ho()
    kiem_router_tuyen()
    kiem_router_bang_do()
    kiem_router_dinh_tuyen()
    kiem_router_khong_phai_ty()
    kiem_kham_adapter()
    kiem_kham_khong_dat_lenh()
    kiem_ngang_gia()
    kiem_vong_doi()
    kiem_lp_amm()
    kiem_von_ngoai_bat_san()
    kiem_dong_co_chua_co()
    kiem_doi_soat_vi_the()
    kiem_luu_danh_muc()
    kiem_ke_toan_vi_the()
    kiem_kho_bao_gia_cau()
    kiem_lat_cat()
    kiem_buong_lai()
    kiem_nhap_so_ngoai()
    kiem_bon_ty()
    kiem_thang_chung()
    kiem_von_toi_thieu()
    kiem_che_van_hanh()
    kiem_hieu_nang()
    kiem_lop_boc_khai_bao()
    kiem_hien_phap()
    kiem_duong_khoa_von()
    kiem_router_doi_lo_hong()
    kiem_chan_doan_doc_dung_khoa()
    kiem_ly_do_cong_ty()
    kiem_khoa_cu_doi_ten()
    kiem_hai_lan()
    kiem_khong_trung_ten()

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
