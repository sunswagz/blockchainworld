"""Sáu engine chưa dựng, và điều kiện chặn của từng cái — dạng CHẠY ĐƯỢC.

Mỗi `DieuKien` là một hàm trả `(dat, chiTiet)`. Không hàm nào chạm mạng: nó
kiểm xem **hạ tầng có tồn tại trong kho này không**, chứ không kiểm xem hôm
nay mạng có thông không. Hai câu hỏi khác nhau, và chỉ câu đầu quyết định
được "có dựng được engine này không".
"""
from __future__ import annotations

import importlib
import os
from dataclasses import dataclass, field

CHAN = "CHAN"
QUET_DUOC = "QUET_DUOC"
SAN_SANG = "SAN_SANG"


@dataclass(frozen=True)
class DieuKien:
    ma: str
    cau: str
    kiem: object = None          # () -> (bool, str)
    #: Điều kiện này chặn việc QUÉT, hay chỉ chặn việc THỰC THI?
    chanQuet: bool = True

    def soat(self) -> dict:
        if self.kiem is None:
            return {"ma": self.ma, "cau": self.cau, "canhDuoc": False,
                    "dat": False, "chiTiet": "không canh được bằng máy",
                    "chanQuet": self.chanQuet}
        try:
            dat, ct = self.kiem()
        except Exception as e:                                # noqa: BLE001
            dat, ct = False, f"{type(e).__name__}: {e}"
        return {"ma": self.ma, "cau": self.cau, "canhDuoc": True,
                "dat": bool(dat), "chiTiet": ct, "chanQuet": self.chanQuet}


@dataclass(frozen=True)
class DongCo:
    ma: str
    ten: str
    ho: str
    moTa: str
    #: Vì sao nó đáng dựng — bằng số, không bằng cảm giác.
    viSaoDang: str
    dieuKien: tuple[DieuKien, ...] = field(default_factory=tuple)

    def soat(self) -> dict:
        ds = [d.soat() for d in self.dieuKien]
        thieuQuet = [x for x in ds if x["chanQuet"] and not x["dat"]]
        thieuThucThi = [x for x in ds if not x["chanQuet"] and not x["dat"]]
        trangThai = (CHAN if thieuQuet
                     else (QUET_DUOC if thieuThucThi else SAN_SANG))
        return {
            "ma": self.ma, "ten": self.ten, "ho": self.ho,
            "moTa": self.moTa, "viSaoDang": self.viSaoDang,
            "trangThai": trangThai,
            "thieuDeQuet": [x["ma"] for x in thieuQuet],
            "thieuDeThucThi": [x["ma"] for x in thieuThucThi],
            "dieuKien": ds,
        }


# ══════════════════════════════════════════════════════════════════════
#  Hàm canh — kiểm HẠ TẦNG TRONG KHO, không kiểm mạng
# ══════════════════════════════════════════════════════════════════════

def _co_goi(ten: str, thu=()) -> tuple[bool, str]:
    try:
        m = importlib.import_module(ten)
    except Exception as e:                                    # noqa: BLE001
        return False, f"không nạp được `{ten}`: {type(e).__name__}"
    thieu = [t for t in thu if not hasattr(m, t)]
    if thieu:
        return False, f"`{ten}` thiếu {thieu}"
    return True, f"`{ten}` có, và có {list(thu) or 'đủ'}"


def _co_bao_gia_dex() -> tuple[bool, str]:
    """LI.FI báo giá được swap CÙNG một chuỗi, không chỉ liên chuỗi.

    Đây là điều kiện Router vừa gỡ mà đoạn văn xuôi cũ chưa kịp biết: hỏi
    `fromChain == toChain` thì LI.FI trả về tuyến swap qua DEX, kèm đúng
    những trường ta đã biết đọc.
    """
    ok, ct = _co_goi("chuyen_von.cau_noi", ("NguonCauNoi", "TOKEN_BANG"))
    if not ok:
        return False, ct
    from chuyen_von.cau_noi import TOKEN_BANG
    chuoi = {c for _, c in TOKEN_BANG}
    return (len(chuoi) >= 2,
            f"báo giá swap qua LI.FI dùng được trên {len(chuoi)} chuỗi: "
            f"{sorted(chuoi)}")


def _co_gia_gas() -> tuple[bool, str]:
    ok, ct = _co_goi("chuyen_von.gas", ("NguonGas", "RPC"))
    if not ok:
        return False, ct
    from chuyen_von.gas import RPC
    return len(RPC) >= 1, f"gas đọc được trên {len(RPC)} chuỗi: {sorted(RPC)}"


def _co_nguon_pool() -> tuple[bool, str]:
    """DefiLlama — `tin_dung/` đã đọc nó, nên nó có thật và đã chạy."""
    return _co_goi("tin_dung.nguon", ("DefiLlama",))


def _co_rpc_ky_lenh() -> tuple[bool, str]:
    """Ví ký được giao dịch on-chain. KHÔNG có, và không được có.

    Runtime này chỉ đọc dữ liệu công khai. `DieuPhoiThucThi.moPhong` là
    `True` cứng và không cấu hình nào mở được.
    """
    from thi_bac_ty.thuc_thi import DieuPhoiThucThi
    if DieuPhoiThucThi().moPhong:
        return False, ("`moPhong=True` cứng — không có lớp ký lệnh, và "
                       "không được phép có")
    return True, "có lớp ký lệnh"


def _co_mempool() -> tuple[bool, str]:
    """Đọc giao dịch CHƯA lên block. Đòi node riêng hoặc dịch vụ trả tiền."""
    if os.environ.get("TBT_MEMPOOL_WS"):
        return True, "TBT_MEMPOOL_WS đã đặt"
    return False, ("chưa có nguồn mempool — RPC công khai chỉ trả trạng "
                   "thái ĐÃ lên block, và mempool là toàn bộ điểm của "
                   "engine này")


def _co_quan_he_builder() -> tuple[bool, str]:
    if os.environ.get("TBT_BUILDER_RPC"):
        return True, "TBT_BUILDER_RPC đã đặt"
    return False, ("chưa có đường tới builder/relay — không gửi bundle được "
                   "thì mọi cơ hội tìm ra đều là bài tập trên giấy")


def _co_do_tre_thap() -> tuple[bool, str]:
    """Máy đặt cạnh sàn/node. Đo được: máy này chạy Windows ở nhà."""
    return False, ("runtime chạy trên máy để bàn qua Internet thường — "
                   "đường về sàn tính bằng chục tới trăm mili giây, trong "
                   "khi engine này thắng thua ở đơn vị mili giây")


def _co_nguon_quyen_chon() -> tuple[bool, str]:
    """Deribit công bố mặt IV công khai, không cần khoá.

    Chưa viết connector — nhưng "chưa viết" khác "không viết được", và
    phân biệt hai câu ấy chính là việc của file này.
    """
    ok, _ = _co_goi("san_chung.giao_ngay", ("SanGiaoNgay",))
    return (False,
            "chưa có connector Deribit. Dữ liệu CÔNG KHAI và không cần khoá "
            "— đây là việc CHƯA LÀM, không phải việc không làm được"
            + (" · khuôn connector đã có ở `san_chung/`" if ok else ""))


def _co_suc_khoe_khoan_vay() -> tuple[bool, str]:
    """Health factor từng khoản vay — cần subgraph hoặc đọc hợp đồng.

    DefiLlama cho TVL và lãi suất mức POOL, không cho từng khoản vay. Hai
    thứ ấy khác hẳn nhau, và nhầm chúng là dựng một scanner thanh lý không
    bao giờ thấy khoản nào sắp bị thanh lý.
    """
    return False, ("DefiLlama chỉ cho số mức POOL, không cho health factor "
                   "từng khoản vay — cần subgraph The Graph hoặc đọc thẳng "
                   "hợp đồng qua RPC (đọc được, chưa viết)")


# ══════════════════════════════════════════════════════════════════════
#  Sáu engine
# ══════════════════════════════════════════════════════════════════════

DONG_CO: tuple[DongCo, ...] = (
    DongCo(
        "dex-arb", "Chênh lệch DEX", "chenh-lech",
        "cùng một token, hai AMM trên cùng một chuỗi, hai giá",
        "Sáu ty hiện có đều ăn chênh lệch CHẬM (funding, lãi suất). Đây là "
        "họ chênh lệch nhanh, và nó có mặt cắt rủi ro khác hẳn — không giữ "
        "qua đêm, không rủi ro kỳ hạn.",
        (DieuKien("bao-gia-dex", "báo giá swap trên cùng một chuỗi",
                  _co_bao_gia_dex),
         DieuKien("gia-gas", "gas để tính phí thật", _co_gia_gas),
         DieuKien("ky-lenh-onchain", "ví ký được giao dịch",
                  _co_rpc_ky_lenh, chanQuet=False),
         DieuKien("do-tre-thap", "đường mạng đủ nhanh để không bị cướp",
                  _co_do_tre_thap, chanQuet=False))),

    DongCo(
        "lp-v3", "Cấp thanh khoản AMM", "thanh-khoan",
        "phí LP trừ tổn thất vô thường trên một khoảng giá",
        "Họ `thanh-khoan` hiện KHÔNG có ty nào. Phễu theo họ vì thế thiếu "
        "hẳn một dòng, và Rủi Ro Tổng chưa bao giờ phải cân một cơ hội có "
        "tổn thất vô thường.",
        (DieuKien("nguon-pool", "APY và TVL mức pool", _co_nguon_pool),
         DieuKien("gia-gas", "gas vào/ra vị thế", _co_gia_gas),
         DieuKien("ky-lenh-onchain", "ví ký được giao dịch",
                  _co_rpc_ky_lenh, chanQuet=False))),

    DongCo(
        "thanh-ly", "Thanh lý", "thanh-ly",
        "mua tài sản thế chấp giá chiết khấu khi khoản vay tụt dưới ngưỡng",
        "Cùng nguồn dữ liệu với `tin_dung/` nhưng ở mức TỪNG KHOẢN VAY. "
        "Họ `thanh-ly` cũng đang trống.",
        (DieuKien("suc-khoe-khoan-vay", "health factor từng khoản vay",
                  _co_suc_khoe_khoan_vay),
         DieuKien("ky-lenh-onchain", "ví ký được giao dịch",
                  _co_rpc_ky_lenh, chanQuet=False),
         DieuKien("do-tre-thap", "nhanh hơn bot thanh lý khác",
                  _co_do_tre_thap, chanQuet=False))),

    DongCo(
        "quyen-chon", "Quyền chọn", "phai-sinh",
        "bán biến động khi IV cao hơn biến động thực hiện",
        "Họ `phai-sinh` đã có hai ty, nhưng cả hai ăn FUNDING. Quyền chọn "
        "ăn một thứ khác hẳn — chênh giữa biến động ngụ ý và biến động "
        "thật — nên nó không tương quan với hai ty kia.",
        (DieuKien("nguon-quyen-chon", "mặt IV công khai (Deribit)",
                  _co_nguon_quyen_chon),)),

    DongCo(
        "jit", "Thanh khoản JIT", "thanh-khoan",
        "bơm thanh khoản đúng một block, ngay trước một lệnh lớn",
        "Lợi nhuận cao nhất trong mười ba họ, và cũng là họ đòi hạ tầng "
        "khắt khe nhất — ghi ra đây để không ai nhầm nó là việc dễ.",
        (DieuKien("mempool", "đọc được giao dịch chưa lên block",
                  _co_mempool),
         DieuKien("quan-he-builder", "gửi được bundle tới builder",
                  _co_quan_he_builder),
         DieuKien("ky-lenh-onchain", "ví ký được giao dịch",
                  _co_rpc_ky_lenh, chanQuet=False))),

    DongCo(
        "mev", "Tìm kiếm MEV", "mev",
        "sandwich, backrun, chênh lệch nguyên tử trong một block",
        "Họ `mev` trống. Và nó là họ duy nhất mà việc KHÔNG dựng là một "
        "lựa chọn đạo đức chứ không chỉ là hạ tầng — sandwich lấy tiền của "
        "một người dùng cụ thể.",
        (DieuKien("mempool", "đọc được giao dịch chưa lên block",
                  _co_mempool),
         DieuKien("quan-he-builder", "gửi được bundle tới builder",
                  _co_quan_he_builder),
         DieuKien("do-tre-thap", "cạnh tranh trong cùng một block",
                  _co_do_tre_thap))),
)


def soat() -> dict:
    ds = [d.soat() for d in DONG_CO]
    theo = {t: [x["ma"] for x in ds if x["trangThai"] == t]
            for t in (CHAN, QUET_DUOC, SAN_SANG)}
    return {
        "soDongCo": len(ds),
        "theoTrangThai": theo,
        "soChan": len(theo[CHAN]),
        "soQuetDuoc": len(theo[QUET_DUOC]),
        "soSanSang": len(theo[SAN_SANG]),
        "dongCo": ds,
        "loiNhac": (
            "QUET_DUOC nghĩa là quét được NGAY, chỉ chưa thực thi được — mà "
            "cả runtime đang moPhong=True, nên KHÔNG ty nào trong sáu ty "
            "hiện có thực thi gì cả. «Chưa thực thi được» không phải lý do "
            "để không dựng. Cái phân biệt QUET_DUOC với CHAN là dữ liệu "
            "công khai không cần khoá."),
    }


def tom_tat() -> dict:
    r = soat()
    return {k: r[k] for k in ("soDongCo", "soChan", "soQuetDuoc",
                              "soSanSang", "theoTrangThai", "loiNhac")}
