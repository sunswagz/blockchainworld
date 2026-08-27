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
        khoaVonDenGiay=khoa, thanhKhoanThoatUsd=thoat,
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
         "rui_ro_tong.khoaVonToiDaGiay đã chặn")

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
                khoaVonDenGiay=0.0, thanhKhoanThoatUsd=5000.0,
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
            khoaVonDenGiay=0.0, thanhKhoanThoatUsd=1e6,
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
         t.khoaVonDenGiay is not None and t.khoaVonDenGiay > 1000.0,
         f"{t.khoaVonDenGiay} — đây là ty đầu tiên dùng trường này với một "
         f"con số thật; trước nó, trường ấy chưa ai chứng minh có tác dụng")
    kiem("giữ tới đáo hạn: giuGio = khoá vốn",
         gan(t.giuGio, t.khoaVonDenGiay, 1e-6),
         "PT trả lãi cố định tới đáo hạn; giữ ngắn hơn thì phải bán trên "
         "AMM ở một giá ta không biết")
    kiem("giờ vốn bị giữ = chính con số ấy",
         gan(t.gio_von_bi_giu, t.khoaVonDenGiay, 1e-6))
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
         RuiRoTong({"khoaVonToiDaGiay": 24 * 365.0}).xet(t, DanhMuc(100000.0)).duyet,
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
         "cả runtime đang moPhong=True — KHÔNG ty nào trong sáu ty hiện có "
         "thực thi gì cả. Nếu thiếu lớp ký lệnh mà chặn cả quét thì sáu ty "
         "đang chạy cũng lẽ ra không được tồn tại")
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
         gan(t0.khoaVonDenGiay, hep.conLaiGio * 3600.0, 1e-6),
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
         gan(t.khoaVonDenGiay, 0.0))
    kiem("đủ sáu mặt rủi ro", t.ruiRo.chua_do() == ())
    kiem("khai IL là khoản CHƯA trừ, kể cả với cặp NEO",
         "ton-that-vo-thuong-du-neo" in t.phiConThieu,
         "stablecoin mất neo là tổn thất vô thường thật và có thể rất lớn")
    kiem("bằng chứng nói rõ IL KHÔNG được ước",
         any("KHONG DUOC UOC" in b for b in t.bangChung))
    kiem("và in ra mức phí SUY RA để người đọc đối chiếu",
         any("SUY RA" in b for b in t.bangChung))

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
         r["soCanhDuoc"] >= r["soDieu"] * 0.8,
         f"{r['soCanhDuoc']}/{r['soDieu']} — dưới 80% thì hiến pháp đang "
         f"nghiêng về văn xuôi, đúng thứ nó sinh ra để thay")
    kiem("tóm tắt gọn dùng được cho buồng lái",
         set(["soDieu", "soViPham", "soKhongCanhDuoc"])
         <= set(__import__("thi_bac_ty.hien_phap", fromlist=["tom_tat"])
                .tom_tat()))


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
    kiem_nhap_so_ngoai()
    kiem_bon_ty()
    kiem_thang_chung()
    kiem_von_toi_thieu()
    kiem_che_van_hanh()
    kiem_hieu_nang()
    kiem_lop_boc_khai_bao()
    kiem_hien_phap()
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
