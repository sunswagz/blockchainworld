"""Adapter — `CoHoi` của ty Phái Sinh → `ToTrinh` của Thị Bạc Ty.

**Không viết lại thuật toán nào.** `can_loi.py`, `dongho.py`, `rui_ro.py` giữ
nguyên; file này chỉ dịch từ ngôn ngữ nội bộ sang ngôn ngữ chung.

    CoHoi  ──►  xuat_to_trinh()  ──►  ToTrinh

Chiều phụ thuộc đúng một chiều: ty import trung ương, trung ương không biết
ty. `thi_bac_ty/to_trinh.py` không có một dòng nào nhắc tới funding.

## Chỗ dịch KHÔNG tầm thường: chấm rủi ro

`CoHoi` có `lyDoMa` — danh sách cửa đã chặn nó. Nhưng cửa rủi ro của ty trả
lời câu **"có vào không"** (PASS/REJECT), còn `ToTrinh.ruiRo` phải trả lời
câu **"nặng tới đâu"** trên thang [0,1] để trung ương cộng được với ty khác.

Hai câu khác nhau, nên đây là chỗ dễ bịa số nhất trong cả file. Luật tự đặt:

  * Chỉ chấm mặt nào **suy được từ số đã đo**. Suy không nổi thì `None`.
  * `None` ≠ 0. Ty Phái Sinh không chạm chuỗi khối nên rủi ro giao thức và
    cầu nối là `None` — **không phải 0**. Ghi 0 là nói "đã xét, không có rủi
    ro", và Rủi Ro Tổng sẽ cộng những số 0 ấy lại thành một danh mục trông
    an toàn giả.

Ty Tín Dụng sau này sẽ chấm `giaoThuc` thật (Aave có rủi ro hợp đồng thông
minh), còn ty Cầu Nối sẽ chấm `cauNoi`. Lúc ấy `None` của ty này và số thật
của ty kia nằm cạnh nhau, và trung ương phân biệt được — đó là cả mục đích.
"""
from __future__ import annotations

from .config import MA_CHIEN_LUOC
from .models import CoHoi
from .suc_chua import uoc_luong
# Import TUYỆT ĐỐI, không phải `..thi_bac_ty`: `bac` và `thi_bac_ty` là hai
# gói NGANG HÀNG dưới gốc runtime, không phải cha con. Viết tương đối thì
# `ImportError: attempted relative import beyond top-level package`.
from thi_bac_ty.to_trinh import Chan, RuiRo, ToTrinh

#: Lấy từ `config.py` — MỘT nguồn. Khai lại ở đây là dựng bản sao thứ
#: hai, và bản sao thứ hai đã lệch thật một lần.
CHIEN_LUOC = MA_CHIEN_LUOC
HO = "phai-sinh"

#: Một nguồn duy nhất cho cả khai báo của ty lẫn
#: từng tờ trình nó xuất ra.
_VON_TOI_THIEU = 100.0

#: Trần lệch mark dùng để quy `lechMarkBps` về thang [0,1]. Vượt trần là rủi
#: ro thị trường bằng 1 — chứ không phải "chưa tới hạn nên bằng 0".
TRAN_LECH_MARK_BPS = 100.0

#: Tuổi dữ liệu (giây) quy về thang [0,1] cho rủi ro thực thi: dữ liệu càng
#: cũ thì khả năng vào lệnh trượt khỏi thứ ta vừa thấy càng cao.
TRAN_TUOI_GIAY = 120.0


def _thang(gt: float | None, tran: float) -> float | None:
    """Quy một đại lượng dương về [0,1] theo trần. `None` giữ nguyên `None`."""
    if gt is None:
        return None
    return max(0.0, min(1.0, abs(gt) / tran))


def _tin_cay(co: CoHoi) -> float:
    """Độ tin của tờ trình này, [0,1]. Trừ dần theo từng chỗ phải đoán.

    Bắt đầu từ 1 rồi trừ, chứ không cộng dần lên: mặc định là tin, và mỗi chỗ
    mù mờ phải TRẢ GIÁ. Cộng dần thì một tờ trình không có thông tin gì sẽ
    nhận điểm 0 và trông giống hệt một tờ trình đã xét kỹ mà thấy tệ.
    """
    d = 1.0
    if co.uocLuongMoc:
        d -= 0.30                      # mốc kết toán phải đoán
    if co.lechMarkBps is None:
        d -= 0.25                      # thiếu mark một bên
    if co.tuoiXauNhatGiay is None:
        d -= 0.15                      # không đo được độ tươi
    elif co.tuoiXauNhatGiay > 60.0:
        d -= 0.10
    if co.soMocLong == 0 and co.soMocShort == 0:
        d -= 0.20                      # thu thực bằng 0, mọi ước lượng vô nghĩa
    return max(0.0, round(d, 3))


def xuat_to_trinh(co: CoHoi, vonXinUsd: float,
                  oiLongUsd: float | None = None,
                  oiShortUsd: float | None = None) -> ToTrinh:
    """Dịch một `CoHoi` thành `ToTrinh`.

    `vonXinUsd` do ty quyết định XIN, không phải trần ty tự áp — quyền chia
    vốn nằm ở trung ương. Đây đúng là chỗ luật "không ty nào tự quyết danh
    mục" hiện ra thành mã.
    """
    suc, thieu_suc = uoc_luong(oiLongUsd, oiShortUsd)

    rr = RuiRo(
        # Lệch mark = hai cảng đang nhìn hai thế giới → chân này lãi chân kia
        # lỗ. Thiếu mark thì KHÔNG BIẾT, không phải không lệch.
        thiTruong=_thang(co.lechMarkBps, TRAN_LECH_MARK_BPS),
        # Chưa có độ sâu sổ lệnh, nên thanh khoản chỉ suy được khi ước lượng
        # được sức chứa. Không có sức chứa thì thà nói không biết.
        thanhKhoan=None if suc is None else max(0.0, min(1.0, vonXinUsd / suc)),
        # Ty Phái Sinh không chạm hợp đồng thông minh và không bắc cầu.
        # `None` chứ không phải 0 — xem docstring đầu file.
        giaoThuc=None,
        cauNoi=None,
        # Rủi ro cảng: chưa có mô hình xếp hạng sàn. Không bịa.
        cang=None,
        thucThi=_thang(co.tuoiXauNhatGiay, TRAN_TUOI_GIAY),
    )

    return ToTrinh(
        chienLuoc=CHIEN_LUOC, ho=HO, taiSan=co.ma,
        chan=(
            Chan("LONG", co.sanLong, co.ma, vonXinUsd, "perp"),
            Chan("SHORT", co.sanShort, co.ma, vonXinUsd, "perp"),
        ),
        vonCanUsd=vonXinUsd,
        vonToiThieuKinhTeUsd=_VON_TOI_THIEU,
        sucChuaToiDaUsd=suc,
        grossBps=co.grossBpsNgay,
        phiUocBps=co.phiBps,
        netUocBps=co.netBps,
        giuGio=co.giuGio,
        ruiRo=rr,
        tuoiDuLieuGiay=co.tuoiXauNhatGiay,
        tinCay=_tin_cay(co),
        # Chép thẳng lời khai của `CoHoi`, không dựng lại — hai bản sao thì
        # sẽ lệch, và bản lệch sẽ là bản trung ương đọc.
        moHinhPhiDuChua=co.moHinhPhiDuChua,
        phiConThieu=tuple(co.phiConThieu),
        moHinhSucChuaDuChua=False,
        sucChuaConThieu=thieu_suc,
        cang=(co.sanLong, co.sanShort),
        bangChung=(
            f"gross {co.grossBpsNgay:+.2f} bps/ngày",
            f"mốc kết toán {co.soMocLong}+{co.soMocShort} trong {co.giuGio:g}h",
            f"thu {co.thuBps:+.2f} − phí {co.phiBps:.1f} = NET {co.netBps:+.2f} bps",
            (f"lệch mark {co.lechMarkBps:.1f} bps"
             if co.lechMarkBps is not None else "THIẾU mark một bên"),
        ) + (() if co.duyet else
             ("cổng ty CHẶN: " + " · ".join(co.lyDo),)),
    )
