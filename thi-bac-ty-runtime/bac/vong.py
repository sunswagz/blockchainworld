"""Vòng lặp nền — hỏi bốn cảng, ghép cặp, cân lợi, ghi sổ.

Một vòng làm đúng năm việc, theo đúng thứ tự này:

    1. hỏi CẢ BỐN cảng song song, cùng một lúc
    2. bỏ báo giá quá cũ
    3. ghép mọi cặp sàn cho từng mã, tính NET
    4. cho qua cổng rủi ro
    5. ghi sổ — kể cả khi không cơ hội nào qua cửa

**Hỏi song song không phải để nhanh.** Bốn cảng hỏi tuần tự cách nhau vài trăm
mili giây là bốn ảnh chụp ở bốn thời điểm khác nhau, rồi đem so với nhau như
thể chúng cùng lúc. Trong một cú biến động, mark của cảng hỏi trước và cảng
hỏi sau lệch nhau chỉ vì thứ tự hỏi — và cổng `lechMarkToiDaBps` sẽ chặn một
cơ hội hoàn toàn lành, hoặc tệ hơn, thả một cơ hội đã hỏng.
"""
from __future__ import annotations

import asyncio
import sys
import threading
import time
from pathlib import Path

import httpx

from .bang import may_ghi
from .bus import bus
from .can_loi import tim_co_hoi
from .config import CONFIG, DATA_DIR, MA_CHIEN_LUOC, che_hieu_luc
from .dong_ho import NGUONG_KEU_MS, do_lech, dong_ho
from .models import BaoGia
from .rui_ro import NHAN, CongRuiRo
from .san import TAT_CA
from thi_bac_ty.khuon_ty import Ty

#: Thư mục gốc của cây mã — `python -m bac.tien_hoa` phải chạy TỪ ĐÂY.
GOC_MA = Path(__file__).resolve().parent.parent

#: Quá ngần này thì giết tiến trình hậu kiểm. Một lượt bình thường ~90 giây;
#: mười phút là đủ rộng cho một cuốn băng dài gấp mấy lần, và đủ chặt để một
#: tiến trình treo không nằm đó mãi.
TREO_TIEN_HOA_GIAY = 600.0

#: Bao lâu chạy lại BĂNG một lượt. Sáu giờ — hậu kiểm đọc cả băng và chạy
#: lại hàng trăm nghìn cơ hội, mất khoảng 30 giây; và bức tranh nó vẽ đổi
#: theo NGÀY, không theo phút. Chạy dày hơn là đốt CPU cho cùng một câu
#: trả lời.
NHIP_TIEN_HOA_GIAY = 6 * 3600.0

from .so import So
from .ty_perp import TyPerp
from .xuat_to_trinh import xuat_to_trinh


#: Bao lâu hỏi lại giờ máy chủ một lần. Lệch đồng hồ trôi chậm (NTP tắt thì
#: nó trôi cỡ giây mỗi giờ), nên hỏi mỗi 5 phút là quá đủ — ba lượt hỏi thêm
#: mỗi 30 giây chỉ tổ tốn hạn mức cho một con số gần như đứng yên.
NHIP_DO_DONG_HO_GIAY = 300.0


class _NhipRieng(Ty):
    """Bọc một ty để nó quét THƯA hơn nhịp chung.

    Vòng quét chạy mỗi 30 giây vì funding đổi theo giây. Lãi cho vay thì đổi
    theo giờ, mà một lượt quét nó là kéo về hai bảng ~17.000 dòng — nên bám
    nhịp chung là đốt băng thông cho một con số gần như đứng yên, và làm
    phiền một nguồn công cộng miễn phí.

    Giữa hai lượt, `quet()` trả lại **kết quả lượt trước** chứ không trả
    rỗng. Trả rỗng thì cơ hội biến mất rồi hiện lại, và cửa chống trùng ở
    Trung Ương ghi nhận chúng như cơ hội MỚI — vòng nào cũng đẻ một loạt tờ
    trình trùng, và cái phễu lại nói dối.

    ## Kế thừa `Ty`, KHÔNG vá nóng

    Bản đầu bọc bằng cách gán đè `ty.quet` rồi gọi `ty.mot_luot()`. Nó tự
    đệ quy: `mot_luot` gọi `self.quet` — nay chính là hàm của lớp bọc — và
    hàm ấy gọi lại `self._ty.quet`, cũng chính nó. Không có `RecursionError`
    vì lần gọi thứ hai rơi đúng vào nhánh "chưa tới nhịp" và trả rỗng, nên
    ty quét được **không lần nào** trong khi mọi thứ vẫn xanh.

    Đúng loại hỏng im lặng mà cả runtime này sinh ra để bắt, và nó lọt vì
    lớp bọc thông minh hơn mức cần thiết. Nay nó là một `Ty` bình thường:
    ba hàm, `quet()` có nhịp, hai hàm kia uỷ quyền thẳng.
    """

    def __init__(self, ty, nhipGiay: float) -> None:
        super().__init__()
        self._ty = ty
        self._nhip = float(nhipGiay)
        self._lanCuoi = 0.0
        self._cu: list = []
        self.soLuotBoQua = 0
        self._quetMoi = True

    # ── khai báo là của ty THẬT, không của lớp bọc ───────────────────────
    #
    # Phải viết TAY từng thuộc tính, không dựa được vào `__getattr__`:
    # `Ty` đã khai sẵn `ma`/`ho`/`moTa`/`vonToiThieuKinhTeUsd` ở tầng lớp,
    # nên tra thuộc tính THÀNH CÔNG (ra giá trị rỗng của lớp bọc) và
    # `__getattr__` không bao giờ được gọi.
    #
    # Lỗi này đã xảy ra hai lần: một lần với `kiem_khai`, một lần với
    # `vonToiThieuKinhTeUsd` — lần thứ hai làm ba ty tụt xuống QUAN_SAT vì
    # trung ương đọc ra "chưa khai ngưỡng". Có phép kiểm canh: mọi thuộc
    # tính KHAI BÁO của lớp bọc phải khớp ty thật.
    @property
    def ma(self): return self._ty.ma

    @property
    def ho(self): return self._ty.ho

    @property
    def moTa(self): return self._ty.moTa

    @property
    def vonToiThieuKinhTeUsd(self): return self._ty.vonToiThieuKinhTeUsd

    def kiem_khai(self):
        """Soi khai báo của ty THẬT. Bọc không phải đường vòng qua cổng."""
        return type(self._ty).kiem_khai()

    # ── ba việc ───────────────────────────────────────────────────────────
    def quet(self):
        now = time.monotonic()
        if self._lanCuoi and (now - self._lanCuoi) < self._nhip:
            self.soLuotBoQua += 1
            self._quetMoi = False
            return list(self._cu)
        self._quetMoi = True
        self._lanCuoi = now
        self._cu = list(self._ty.quet())
        return list(self._cu)

    def quet_moi(self) -> bool:
        """Lượt vừa rồi có hỏi nguồn không. Xem `khuon_ty.Ty.quet_moi`."""
        return self._quetMoi

    def xet(self, co):
        return self._ty.xet(co)

    def trinh(self, co):
        return self._ty.trinh(co)

    # ── việc thứ TƯ: kế toán ─────────────────────────────────────────────
    #
    # Uỷ quyền như ba việc kia, và phải viết TAY vì cùng lý do ở trên:
    # `Ty.ke_toan` có sẵn ở lớp gốc nên tra thuộc tính THÀNH CÔNG (ra hàm
    # gốc trả `None`) và `__getattr__` không bao giờ chạy.
    #
    # Đây là lần thứ BA cùng một kiểu hỏng — sau `kiem_khai` và
    # `vonToiThieuKinhTeUsd`. Lần này hậu quả là mọi ty có nhịp riêng đều
    # bị báo "chưa có kế toán": bảy vị thế, 3.500 USD, không đồng lãi nào
    # được cộng, và buồng lái nói đúng câu ấy nên không ai nghi ngờ mã.
    # Phép kiểm nay dò MỌI thành viên uỷ quyền được, không chỉ ba cái tên
    # ai đó nhớ ra.
    def ke_toan(self, viThe, toTrinh, tuGiay, denGiay):
        return self._ty.ke_toan(viThe, toTrinh, tuGiay, denGiay)

    def co_ke_toan(self) -> bool:
        return type(self._ty).co_ke_toan()

    # Tiện đọc `._nguon`, `.coHoi`… của ty thật từ buồng lái.
    def __getattr__(self, ten):
        return getattr(self.__dict__["_ty"], ten)

    def tom_tat(self) -> dict:
        return {**super().tom_tat(), "nhipGiay": self._nhip,
                "soLuotBoQua": self.soLuotBoQua}


def _giu_toi_thieu(baoGia, nowMs: float) -> list:
    """Mỗi cảng: phải giữ ít nhất bao nhiêu giờ mới CHẠM một mốc kết toán.

    Funding trả theo MỐC. Giữ bốn giờ trên sàn kết toán tám giờ có thể thu
    đúng bằng KHÔNG — và người vận hành không nên phải tự suy ra điều đó từ
    một bảng mốc kế tiếp.
    """
    from phai_sinh_chung.dongho import gio_giu_toi_thieu
    ra = []
    for b in baoGia:
        try:
            g = gio_giu_toi_thieu(nowMs, b.mocKeMs, b.intervalGio)
        except Exception:                                     # noqa: BLE001
            continue
        ra.append({"san": b.san, "ma": b.ma, "gio": g,
                   "chuKyGio": b.intervalGio})
    ra.sort(key=lambda x: -x["gio"])
    return ra[:8]


def _tom_dong_co() -> dict:
    """Sổ engine chưa dựng. Bọc try vì một phép canh nổ KHÔNG được làm chết
    ảnh chụp — buồng lái mất một ô còn hơn mất cả trang."""
    try:
        from dong_co_chua_co.so_dang_ky import tom_tat
        return tom_tat()
    except Exception as e:                                    # noqa: BLE001
        return {"loi": f"{type(e).__name__}: {e}"}


#: Nạp lại giá gas sau bao nhiêu giây. Đổi theo block, nhưng ta chỉ cần BẬC.
NHIP_NAP_GAS_GIAY = 300.0

#: Nạp lại báo giá cầu sau bao nhiêu giây.
#:
#: 30 phút, không phải 15: chín lời gọi mỗi lượt ở nhịp 15 phút là 36 lời
#: gọi mỗi giờ, và phí cầu không đổi nhanh tới mức ấy. LI.FI có hạn mức,
#: và nó chặn ở 429 kèm «retry in 2 hours» — bản trước đã ăn đúng lệnh ấy.
NHIP_NAP_CAU_GIAY = 1800.0


def xet_keu_lech(lechMs, daKeu: bool, nguongMs: float = NGUONG_KEU_MS):
    """Có nên kêu ĐỒNG HỒ LỆCH không. Trả `(nênKêu, chốt mới)`.

    Kêu một lần cho MỖI ĐỢT lệch, không phải một lần cho cả đời tiến
    trình. Bản trước đặt `_daKeuLech = True` rồi **không bao giờ gỡ**,
    nên đợt lệch thứ hai — kể cả một đợt lớn hơn hẳn — đi qua trong im
    lặng. Runtime này chạy nhiều ngày liền, và lệch đồng hồ là thứ quay
    lại: máy ngủ, VPN đổi, NTP trượt.

    Lệch đã bù khi đếm mốc nên đây là cảnh báo KHUYÊN, không phải cảnh
    báo chặn — càng đúng lý do để nó đừng câm: thứ duy nhất nó làm là
    nói cho người vận hành biết nên chỉnh NTP, và nói một lần rồi thôi
    thì lần thứ hai không ai biết.

    Ba nhánh, và nhánh giữa mới là nhánh dễ viết sai:

      · CHƯA ĐO ĐƯỢC (`None`) — giữ nguyên chốt. «Không đo được» khác
        hẳn «đã về bình thường»; gỡ chốt ở đây là mở đường cho một
        chuỗi kêu đi kêu lại mỗi lần mất mạng.
      · TRONG ngưỡng — GỠ chốt, để đợt sau còn kêu được.
      · QUÁ ngưỡng — kêu nếu chưa kêu, và cài chốt.
    """
    if lechMs is None:
        return False, daKeu
    if abs(lechMs) <= nguongMs:
        return False, False
    return (not daKeu), True


def can_nap_router(gio: float, lanNapGas: float, lanNapCau: float):
    """Tới lúc nạp lại gas / báo giá cầu chưa. Trả `(canGas, canCau)`.

    Hai nhịp RIÊNG vì hai nguồn đổi ở hai tốc độ, và hỏi cả hai theo nhịp
    của cái nhanh hơn là vừa lãng phí vừa bất lịch sự với một API có hạn
    mức. Tách khỏi `_nap_router()` để kiểm được không cần mạng.
    """
    return (gio - lanNapGas > NHIP_NAP_GAS_GIAY,
            gio - lanNapCau > NHIP_NAP_CAU_GIAY)


def cap_can_bao_gia(coVon, token, nha: str):
    """Những chặng cầu cần hỏi giá: `(tài sản, từ, tới, vốn)`.

    **CHỈ USDC, và chỉ khi CHÍNH `nha` cũng có USDC.** Nạp cả ba tài sản
    × ba cỡ vốn là 27 lời gọi mỗi lượt, và LI.FI chặn ở 429 kèm «retry in
    2 hours». USDC là tài sản `lai_suat` thật sự bắc cầu, và là đồng phổ
    biến nhất; tài sản khác thì tuyến MÙ, ty giữ nguyên khai báo
    `phiConThieu` — đó là hệ thống chạy ĐÚNG, không phải hỏng.

    Cửa `("USDC", nha) in token` không thừa: thiếu nó thì ta đi hỏi giá
    một chặng mà chính nhà xuất phát không có đồng ấy, và mọi lời gọi
    trong lượt đều trả về rỗng — kho trống, tuyến mù, không dòng nào kêu.
    """
    return [(ts, nha, ch, von)
            for von in coVon
            for (ts, ch) in token
            if ts == "USDC" and ch != nha and ("USDC", nha) in token]


def loc_bao_gia_cu(tho, nowMs: float, tranGiay: float):
    """Bỏ báo giá quá cũ. Trả `(giữ lại, số bị bỏ)`.

    **Lọc TRƯỚC khi ghép cặp.** Lọc sau thì một báo giá chết vẫn kịp sinh
    ra ba cặp, và cả ba mang lý do từ chối giống hệt nhau — nhật ký ngập
    ba dòng nói cùng một chuyện.

    `tuoi_giay()` trả `None` khi sàn không đóng dấu thời gian. **Giữ**, và
    đó là lựa chọn có ý: không biết tuổi thì không kết luận là cũ. Cửa
    rủi ro phía sau còn hỏi lại, còn ở đây mà bỏ thì cả một sàn không
    đóng dấu sẽ biến mất khỏi mọi phép ghép cặp mà không dòng nào kêu.

    Tách khỏi `mot_vong()` để KIỂM ĐƯỢC mà không cần mạng — bản trước nằm
    trong thân một coroutine gọi bốn sàn, nên phép cấy lỗi ngược đi lọt:
    không phép kiểm nào chạm tới cửa `t > tran`, và một `>=` viết nhầm ở
    đó vứt đúng những báo giá nằm sát mép — chỗ phần lớn báo giá thật nằm
    khi mạng chậm.
    """
    giu = []
    bo = 0
    for b in tho:
        t = b.tuoi_giay(nowMs)
        if t is not None and t > tranGiay:
            bo += 1
            continue
        giu.append(b)
    return giu, bo


def cang_dang_hong(cang, nhipGiay: float):
    """Tên những cảng có lỗi và lỗi ấy còn MỚI. Trả list tên.

    Hai vế phải cùng đúng, và vế thứ hai mới là vế khó: một cảng từng lỗi
    rồi hồi phục vẫn giữ `loiCuoi` mãi, nên chỉ hỏi `loiCuoi` là dựng một
    danh sách hỏng chỉ dài thêm, không bao giờ ngắn lại — đúng dạng cảnh
    báo mà người ta học cách bỏ qua.

    `tuoi_giay()` trả `None` nghĩa là chưa có lượt nào thành công kể từ
    lỗi ấy, và đó là ca XẤU NHẤT chứ không phải ca chưa biết — nên nó
    được đọc thành `1e9` giây, tức chắc chắn quá hạn.
    """
    return [c.ten for c in cang
            if c.suc_khoe.loiCuoi
            and (c.suc_khoe.tuoi_giay() or 1e9) > float(nhipGiay) * 2]


class Runtime:
    def __init__(self) -> None:
        self.cang = {}
        for ten, lop in TAT_CA.items():
            if (CONFIG["san"].get(ten) or {}).get("bat", False):
                self.cang[ten] = lop()

        self.cong = CongRuiRo(CONFIG["ruiRo"])
        self.so = So()

        # ── Thị Bạc Ty đứng TRÊN ty này ──────────────────────────────────
        # Chiều phụ thuộc chỉ đi một hướng: `bac` biết `thi_bac_ty`, không
        # bao giờ ngược lại. Ngày trung ương phải import một ty để xử một
        # trường hợp riêng là ngày hợp đồng đã hỏng — `scripts/selftest.py`
        # canh đúng chuyện đó.
        tu = CONFIG.get("trungUong") or {}
        self.trungUong = None
        self.tyTinDung = None
        self.tyPhu = {}
        if tu.get("bat", True):
            from thi_bac_ty.trung_uong import TrungUong
            self.trungUong = TrungUong(
                DATA_DIR, {k: v for k, v in tu.items()
                           if k not in ("bat", "tyTinDung", "tyOnDinh",
                                        "tyLaiSuat", "tyCoSo",
                                        "tyTienDoan", "tyNgangGia",
                                        "tyVongDoi", "tyCapThanhKhoan")})
            self.trungUong.dang_ky(TyPerp(self))

            # Ty thứ hai — TÍN DỤNG. Nó cắm vào cùng `khuon_ty.Ty`, không
            # dựng runtime riêng, và đó là toàn bộ điểm của nó: hai chiến
            # lược khác hẳn nhau sống dưới một Thị Bạc Ty.
            #
            # Bọc try vì một ty mới không được phép làm chết vòng quét của
            # ty đang chạy. Hỏng thì `loiVongCuoi` nói ra, không im.
            # Ba ty còn lại, cùng một lối: bọc nhịp riêng, bọc try riêng.
            # Một ty mới hỏng KHÔNG được làm chết vòng quét của ty đang
            # chạy, và cũng không được kéo theo hai ty mới còn lại — nên
            # mỗi cái một `try`, không gộp.
            # Router dựng TRƯỚC các ty, vì ba ty nhận nó vào hàm dựng.
            # Hỏng thì `dinhTuyen` là None và mọi ty vẫn quét được — chỉ là
            # `phiConThieu` của chúng dài hơn, và chúng tự khai điều đó.
            self.dinhTuyen = None
            self.nguonGas = None
            self.nguonCau = None
            try:
                from chuyen_von.cau_noi import NguonCauNoi
                from chuyen_von.dinh_tuyen import DinhTuyen
                from chuyen_von.gas import NguonGas
                self.nguonGas, self.nguonCau = NguonGas(), NguonCauNoi()
                self.dinhTuyen = DinhTuyen()
                # Kho báo giá cầu SỐNG QUA lần khởi động lại. LI.FI có hạn
                # mức giờ và mỗi lần bật máy nạp trước chín báo giá — khởi
                # động lại năm lần trong một giờ (chuyện thường lúc đang
                # sửa mã) là tự đẩy mình vào 429 và nghỉ 80 phút, tức là
                # mọi tuyến liên chuỗi MÙ đúng lúc vừa bật máy lên. Đã xảy
                # ra thật 28/08/2026. Xem `DinhTuyen.nap_kho`.
                self.duongKhoCau = DATA_DIR / "kho-bao-gia-cau.json"
                self.napKhoCau = self.dinhTuyen.nap_kho(self.duongKhoCau)
            except Exception as e:                       # noqa: BLE001
                self.loiVongCuoi = f"router: {type(e).__name__}: {e}"

            self.tyPhu = {}
            for khoa, nap, nhip in (
                    ("tyTinDung",
                     lambda: __import__("tin_dung.ty_vay",
                                        fromlist=["TyTinDung"])
                     .TyTinDung(dinhTuyen=self.dinhTuyen),
                     900.0),
                    ("tyOnDinh",
                     lambda: __import__("on_dinh.ty_on_dinh",
                                        fromlist=["TyOnDinh"])
                     .TyOnDinh(dinhTuyen=self.dinhTuyen),
                     120.0),
                    ("tyLaiSuat",
                     lambda: __import__("lai_suat.ty_lai_suat",
                                        fromlist=["TyLaiSuat"])
                     .TyLaiSuat(dinhTuyen=self.dinhTuyen),
                     3600.0),
                    # Ty cơ sở nhận `self`: nó đọc lại `baoGia` của lượt quét
                    # này thay vì hỏi perp lần nữa. Hai lượt hỏi là hai ảnh
                    # chụp ở hai thời điểm rồi ghép như thể cùng lúc.
                    ("tyCoSo",
                     lambda: __import__("co_so.ty_co_so",
                                        fromlist=["TyCoSo"]).TyCoSo(self),
                     60.0),
                    # Cỗ máy thứ hai vào dưới Rủi Ro Tổng — nhưng chỉ phần
                    # nó CHƯA lấy. Phần đang giữ đã là vốn ngoài trong Danh
                    # Mục, và đếm cả hai là đếm một vị thế hai lần.
                    ("tyTienDoan",
                     lambda: __import__("kham_ngoai.ty_tien_doan",
                                        fromlist=["TyTienDoan"]).TyTienDoan(),
                     90.0),
                    # Engine thứ bảy — và engine đầu tiên KHÔNG cần mô hình:
                    # ngang giá là một đẳng thức, không phải một dự báo.
                    ("tyNgangGia",
                     lambda: __import__("quyen_chon.ty_ngang_gia",
                                        fromlist=["TyNgangGia"]).TyNgangGia(),
                     300.0),
                    # Engine thứ tám. Nhận Router để lấy gas SỐNG — thiếu
                    # nó thì `netBps` là None và ty tự khai là mù.
                    ("tyVongDoi",
                     lambda: __import__("dex_arb.ty_vong_doi",
                                        fromlist=["TyVongDoi"])
                     .TyVongDoi(dinhTuyen=self.dinhTuyen),
                     600.0),
                    # Engine thứ chín — và ty ĐẦU TIÊN của họ `thanh-khoan`,
                    # nên đây là lần đầu Rủi Ro Tổng phải cân một cơ hội có
                    # tổn thất vô thường.
                    ("tyCapThanhKhoan",
                     lambda: __import__("lp_amm.ty_cap_thanh_khoan",
                                        fromlist=["TyCapThanhKhoan"])
                     .TyCapThanhKhoan(dinhTuyen=self.dinhTuyen),
                     1800.0)):
                cf = (tu.get(khoa) or {})
                if not cf.get("bat", True):
                    continue
                try:
                    t = _NhipRieng(nap(), float(cf.get("nhipGiay", nhip)))
                    if self.trungUong.dang_ky(t):
                        self.tyPhu[khoa] = t
                except Exception as e:                   # noqa: BLE001
                    self.loiVongCuoi = f"{khoa}: {type(e).__name__}: {e}"
            self.tyTinDung = self.tyPhu.get("tyTinDung")
        self.latCatTrungUong = None

        #: Hậu kiểm trên băng — chạy ở luồng nền, xem `_tien_hoa_dinh_ky`.
        #: `_lanTienHoa = 0` để lượt ĐẦU chạy ngay lúc máy lên: không thế
        #: thì mỗi lần deploy đẩy lượt hậu kiểm lùi thêm sáu tiếng, và một
        #: buổi chiều deploy mười lăm lần là một buổi chiều không hậu kiểm.
        self._lanTienHoa = 0.0
        self._luongTienHoa = None
        self.tienHoaCuoi: dict | None = None
        self.loiTienHoa = ""

        self.vong = 0
        self.batDauLuc = time.time()
        self.tamDung = False
        self.baoGia: list[BaoGia] = []
        self.coHoi = []
        self.loiVongCuoi: str | None = None
        self._lanNapGas = 0.0
        # NHỊP nạp cầu cũng phải sống qua khởi động lại, không chỉ cái kho.
        # `0.0` nghĩa là «nạp ngay», nên mỗi lần bật máy là chín lời gọi
        # LI.FI nữa — mà LI.FI có hạn mức GIỜ. Mười lăm lần bật trong một
        # buổi chiều sửa mã là 429 kèm nghỉ 83 phút, tức mọi tuyến liên
        # chuỗi MÙ đúng lúc vừa bật máy lên. Đã xảy ra thật hai lần: 28/08
        # (trước khi có kho) và 30/08 (có kho rồi, nhưng nhịp vẫn về 0).
        #
        # Kho biết báo giá mới nhất của nó đọc lúc nào, nên nhịp bắt đầu
        # TỪ ĐÓ. Kho rỗng hay quá hạn thì `moiNhatMs` là None và nhịp về 0
        # như cũ — lúc ấy nạp ngay là đúng, vì thật sự không còn gì.
        # `getattr`, không phải `self.napKhoCau`: khối dựng Router nằm
        # trong một `try`, nên nó ném thì thuộc tính này không tồn tại —
        # và lúc ấy `__init__` chết giữa chừng vì một dòng tối ưu hoá
        # nhịp nạp. Dòng 835 đã dùng `getattr` cho đúng lý do ấy.
        _moi = (getattr(self, "napKhoCau", None) or {}).get("moiNhatMs")
        self._lanNapCau = float(_moi) / 1000.0 if _moi else 0.0
        self.quetCuoiMs: float = 0.0
        self.quetLauNhatMs: float = 0.0

        self._chay = False
        self._luong: threading.Thread | None = None
        self._ngayDonSo = ""
        self._daKeuLech = False
        self._lanDoDongHo = 0.0
        self._doDongHoHong = False

    # ── điều khiển ────────────────────────────────────────────────────────
    def bat(self) -> None:
        if self._chay:
            return
        self._chay = True
        self._luong = threading.Thread(target=self._vong_lap, daemon=True)
        self._luong.start()
        bus.ghi(f"Thị Bạc Ty chạy — {len(self.cang)} cảng, "
                f"{len(CONFIG['quet']['ma'])} mã, chế độ {che_hieu_luc()}", loai="he")

    def dung(self) -> None:
        self._chay = False
        may_ghi.dong()
        bus.ghi("runtime dừng", loai="he")

    def _vong_lap(self) -> None:
        nhip = float(CONFIG["nhipGiay"])
        while self._chay:
            t0 = time.time()
            try:
                if not self.tamDung:
                    asyncio.run(self.mot_vong())
            except Exception as e:                  # noqa: BLE001
                self.loiVongCuoi = f"{type(e).__name__}: {e}"
                bus.ghi(f"vòng {self.vong} lỗi: {self.loiVongCuoi}", loai="loi")

            # KHÔNG ghi lát cắt cung tĩnh ở đây, và đó là quyết định có lý
            # do — xem `bac/snapshot.py`. Bản 28/08 từng thêm lời gọi vào
            # đúng chỗ này vì tiêu đề file sinh ra hứa "ghi mỗi vòng lặp";
            # sai lầm là chữa MÃ cho khớp một lời hứa vốn đã sai thiết kế.
            # Trang công khai đọc bản ĐÃ COMMIT, nên ghi 30 giây một lần
            # không làm site tươi hơn một giây nào — nó chỉ để lại một file
            # được theo dõi luôn ở trạng thái bẩn, và `git merge --ff-only`
            # ở cây chính hỏng ngay lần đầu có commit chạm tới file ấy.

            con = nhip - (time.time() - t0)
            if con > 0:
                time.sleep(con)

    def _hen_do_dong_ho(self) -> float:
        """Đo hỏng thì thử lại sớm, đừng khoá trọn 5 phút.

        Bản đầu đặt mốc hẹn TRƯỚC khi gọi, nên một lượt đo hỏng vẫn khoá
        tiếp 5 phút: lỗi báo đúng một lần rồi im, và runtime chạy tiếp trên
        giờ MÁY chưa bù trong khi bảng không nói gì. Đã cắn thật lúc dựng —
        `NameError` ở vòng 1, rồi ba vòng sau xanh trơn.
        """
        return 30.0 if self._doDongHoHong else NHIP_DO_DONG_HO_GIAY

    # ── một vòng ──────────────────────────────────────────────────────────
    async def _nap_router(self, bus) -> None:
        """Đọc gas và báo giá cầu cho Router, theo nhịp RIÊNG.

        Nhịp riêng vì ba nguồn đổi ở ba tốc độ khác nhau, và hỏi cả ba theo
        nhịp của cái nhanh nhất là lãng phí lẫn bất lịch sự:

            báo giá perp   30 giây   — giá đổi từng giây
            gas            5 phút    — đổi theo block, nhưng ta chỉ cần bậc
            cầu nối        30 phút   — phí cầu đổi chậm, và LI.FI có
                                     hạn mức: 429 kèm nghỉ 2 GIỜ

        Client RIÊNG vì hết-giờ khác: LI.FI phải đi hỏi hàng chục cầu rồi
        mới trả lời, chậm hơn hẳn một `bookTicker`. Dùng chung client với
        vòng quét perp là bắt vòng quét chờ theo nhịp của thứ chậm nhất.
        """
        if self.dinhTuyen is None:
            return
        gio = time.time()
        canGas, canCau = can_nap_router(gio, self._lanNapGas,
                                        self._lanNapCau)
        if not (canGas or canCau):
            return
        try:
            from chuyen_von.cau_noi import TOKEN
            from chuyen_von.dinh_tuyen import NHA
            async with httpx.AsyncClient(
                    timeout=30.0,
                    headers={"User-Agent": "thi-bac-ty/0.1 "
                                           "(+public data only)"}) as c:
                if canGas:
                    # `NguonGas` tự giữ số cũ khi một chuỗi lỗi, nên
                    # gán thẳng ở đây là an toàn — nó trả về CHÍNH `self.gia`
                    # đã được vá, không phải một bảng mới rỗng.
                    self.dinhTuyen.giaGas = await self.nguonGas.doc(c)
                    self._lanNapGas = gio
                    # Giá token gốc lấy từ báo giá perp của CHÍNH lượt quét
                    # này — không đi hỏi thêm một nguồn giá thứ hai, vì hai
                    # nguồn giá là hai câu trả lời cho cùng một câu hỏi.
                    self._cap_nhat_gia_token()
                if canCau:
                    # Cỡ vốn phải là cỡ CÁC TY THẬT SỰ HỎI, không phải một
                    # con số tròn ai đó chọn. Kho khoá theo (tài sản, từ,
                    # tới, vốn); hỏi cỡ khác cỡ đã nạp là trượt kho, và
                    # tuyến thành MÙ trong im lặng.
                    #
                    # Đã cắn: `lai_suat` hỏi $1.000 trong khi kho chỉ có
                    # $500, nên tích hợp Router của nó KHÔNG chạy trong sản
                    # xuất — dù chạy đúng trong mọi thử nghiệm rời.
                    # Vì sao CHỈ USDC, và vì sao cửa `("USDC", NHA) in
                    # TOKEN` không thừa: xem `cap_can_bao_gia`.
                    can = cap_can_bao_gia(self._co_von_cac_ty(), TOKEN, NHA)
                    await self.dinhTuyen.nap(c, self.nguonCau, can)
                    self._lanNapCau = gio
                    try:
                        self.dinhTuyen.luu_kho(self.duongKhoCau)
                    except OSError as e:
                        bus.ghi(f"lưu kho báo giá cầu hỏng: {e}", loai="loi")
        except Exception as e:                                # noqa: BLE001
            bus.ghi(f"Router không nạp được: {type(e).__name__}: {e} — các ty "
                    f"sẽ giữ nguyên khai báo phiConThieu", loai="canh")

    @staticmethod
    def _co_von_cac_ty() -> tuple:
        """Những cỡ vốn các ty thật sự xin, đọc THẲNG từ config của chúng.

        Chép tay một danh sách ở đây thì nó lệch đúng vào ngày ai đó đổi
        `moiCoHoiUsd` của một ty — và lệch im lặng, vì trượt kho chỉ hiện
        ra dưới dạng "tuyến không đo được".
        """
        ra = set()
        for m in ("tin_dung.config", "lai_suat.ty_lai_suat",
                  "on_dinh.ty_on_dinh", "lp_amm.ty_cap_thanh_khoan"):
            try:
                c = getattr(__import__(m, fromlist=["CONFIG"]), "CONFIG")
                ra.add(float(c["von"]["moiCoHoiUsd"]))
            except Exception:                                 # noqa: BLE001
                continue
        return tuple(sorted(ra)) or (500.0,)

    def _cap_nhat_gia_token(self) -> dict:
        """GỘP giá mới vào bảng, KHÔNG thay cả bảng.

        Một lượt quét thiếu ETH — cả bốn cảng cùng lỗi — từng xoá sạch bảng
        giá, và mọi chặng gas hoá mù dù lượt trước vừa đọc được. Cùng lỗi
        với `NguonGas` và với kho báo giá cầu: thay tri thức bằng vô tri
        trong im lặng.

        Tách thành hàm riêng để KIỂM ĐƯỢC mà không cần mạng — bản trước nằm
        trong `_nap_router()`, và phép cấy lỗi ngược đi lọt vì không phép
        kiểm nào chạm tới.
        """
        if self.dinhTuyen is None:
            return {}
        self.dinhTuyen.giaTokenGocUsd.update(self._gia_token_goc())
        return self.dinhTuyen.giaTokenGocUsd

    def _gia_token_goc(self) -> dict:
        """Giá token TRẢ GAS, lấy từ mark perp của chính lượt quét này.

        Thiếu một giá thì chặng gas của chuỗi ấy mù, và cái mù chảy lên tận
        tổng — đúng thứ ta muốn, chứ không phải một con số bịa.

        Danh sách suy ra từ `TOKEN_GOC` chứ không chép tay: thêm một chuỗi
        vào Router mà quên thêm giá ở đây thì chuỗi ấy mù trong im lặng, và
        chính chuyện đó đã xảy ra với Polygon.
        """
        from chuyen_von.gas import TOKEN_GOC
        can = set(TOKEN_GOC.values())
        ra: dict = {}
        for b in self.baoGia:
            if b.ma in can and b.markPx and b.ma not in ra:
                ra[b.ma] = float(b.markPx)
        return ra

    async def mot_vong(self) -> None:
        self.vong += 1
        t0 = time.perf_counter()
        q = CONFIG["quet"]

        async with httpx.AsyncClient(
                timeout=float(q["hetGioHoiGiay"]),
                headers={"User-Agent": "thi-bac-ty/0.1 (+public data only)"}) as client:
            # Đo lệch đồng hồ TRƯỚC khi hỏi báo giá: adapter đóng dấu bằng
            # `bay_gio_ms()`, nên phần bù phải sẵn sàng trước lúc chúng chạy.
            if time.time() - self._lanDoDongHo > self._hen_do_dong_ho():
                soMau = await do_lech(client, dong_ho)
                self._lanDoDongHo = time.time()
                self._doDongHoHong = soMau == 0
                if soMau == 0:
                    bus.ghi("KHÔNG đo được lệch đồng hồ — mọi phép đếm mốc "
                            "đang chạy trên giờ MÁY, thử lại sau 30s", loai="canh")

            ds = list(self.cang.values())
            goi = await asyncio.gather(*(c.bao_gia(client, list(q["ma"])) for c in ds))

        tho: list[BaoGia] = [b for lo in goi for b in lo]

        now = dong_ho.bay_gio_ms()

        lech = dong_ho.lech_ms()
        _keu, self._daKeuLech = xet_keu_lech(lech, self._daKeuLech)
        if _keu:
            bus.ghi(f"ĐỒNG HỒ MÁY lệch {lech / 1000:+.0f}s so với sàn — đã bù "
                    f"khi đếm mốc, nhưng nên chỉnh lại NTP", loai="canh")

        # Lọc báo giá quá cũ TRƯỚC khi ghép cặp. Lọc sau thì một báo giá chết
        # vẫn kịp sinh ra ba cặp, và cả ba đều mang lý do từ chối giống hệt
        # nhau — nhật ký ngập ba dòng nói cùng một chuyện.
        tran = float(CONFIG["ruiRo"]["tuoiToiDaGiay"])
        self.baoGia, bo_cu = loc_bao_gia_cu(tho, now, tran)
        if bo_cu:
            bus.ghi(f"bỏ {bo_cu} báo giá cũ hơn {tran:.0f}s", loai="canh")

        self.coHoi = tim_co_hoi(self.baoGia, now, float(q["giuGio"]),
                                CONFIG["san"], self.cong)

        await self._nap_router(bus)

        loi = cang_dang_hong(self.cang.values(), CONFIG["nhipGiay"])
        self.so.ghi_luot(self.coHoi, len(self.baoGia), loi)

        # Băng ghi NGUYÊN LIỆU, sổ ghi KẾT LUẬN. Thiếu băng thì không chạy
        # lại được, và không chạy lại được thì mọi lần vặn ngưỡng đều là đổi
        # số cho vui — không cách nào biết tốt hơn hay chỉ khác đi.
        may_ghi.ghi({
            "luc": now,
            "vong": self.vong,
            "giuGio": float(q["giuGio"]),
            "lechDongHoMs": dong_ho.lech_ms(),
            "baoGia": [b.tom_tat(now) for b in self.baoGia],
        })

        duyet = [c for c in self.coHoi if c.duyet]
        for c in duyet:
            bus.ghi(f"{c.ma}: LONG {c.sanLong} / SHORT {c.sanShort} · "
                    f"NET {c.netBps:+.2f} bps trong {c.giuGio:g}h "
                    f"({c.soMocLong}+{c.soMocShort} mốc)", loai="tin")

        # ── giao lại cho Trung Ương ──────────────────────────────────────
        # Đặt SAU khi đã ghi băng: băng là nguyên liệu, phải còn nguyên kể cả
        # khi trung ương nổ. Và bọc try vì một lỗi ở tầng phân bổ không được
        # phép làm chết vòng quét — mất một vòng phân bổ là mất một cơ hội,
        # mất vòng quét là mất cả khả năng nhìn.
        if self.trungUong is not None:
            try:
                self.latCatTrungUong = self.trungUong.mot_vong(
                    lechDongHoGiay=(None if lech is None else lech / 1000.0),
                    cangChet=loi,
                    tuoiXauNhatGiay=max(
                        (t for t in (b.tuoi_giay(now) for b in self.baoGia)
                         if t is not None), default=None))
                l = self.latCatTrungUong
                if l.cauDaoNgat:
                    bus.ghi("CẦU DAO NGẮT — không cam kết vốn: "
                            + "; ".join(l.lyDoNgat), loai="canh")
                elif l.phanBo and l.phanBo["soCap"]:
                    bus.ghi(f"Thị Bạc Ty cấp {l.phanBo['tongCapUsd']:.0f} USD "
                            f"cho {l.phanBo['soCap']} tờ trình "
                            f"[SỔ GIẤY]", loai="tin")
            except Exception as e:                       # noqa: BLE001
                self.loiVongCuoi = f"trung ương: {type(e).__name__}: {e}"
                bus.ghi(f"Trung Ương lỗi: {e}", loai="canh")

        self._don_so_moi_ngay()
        self._tien_hoa_dinh_ky()
        d = (time.perf_counter() - t0) * 1000.0
        self.quetCuoiMs = d
        self.quetLauNhatMs = max(self.quetLauNhatMs, d)

    def _tien_hoa_dinh_ky(self) -> None:
        """Chạy lại BĂNG và hậu kiểm, theo nhịp riêng, trong LUỒNG NỀN.

        ## Vì sao việc này từng không bao giờ chạy

        `tien_hoa.mot_luot()` chỉ tới được qua `POST /api/tien-hoa`. Nên
        `duong_tien_hoa()` đứng ở `soLuot: 0` từ lúc dựng, và cỗ máy ghi
        băng suốt 188 giờ mà chưa một lần đọc lại. Lần thứ BA trong cùng một
        cây mã: có mã, có phép kiểm, có ô trên buồng lái, và không ai gọi.

        ## Vì sao phải TIẾN TRÌNH RIÊNG, không phải luồng

        Một lượt mất ~90 giây: đọc băng, dựng chỉ mục, rồi chạy lại 460.000
        cơ hội BA lượt (nền + hai bộ đối chiếu). Toàn mã Python thuần.

        Bản đầu ném sang một LUỒNG, và đo thật thì cổng 5188 câm suốt 90
        giây kể từ lúc máy lên: buồng lái không mở được, và cầu dao đo tuổi
        dữ liệu nên nó sắp ngắt vì chính phép đo của mình. Luồng trong
        Python chia GIL với cả tiến trình — "nền" không có nghĩa là không
        cản ai. Nhường GIL theo nhịp khung có đỡ, nhưng đo lại vẫn ~90 giây
        câm, nên không đủ.

        Tiến trình riêng thì hết chuyện: GIL riêng, khoá riêng, chết cũng
        không kéo ai theo. Giá là một lần khởi động Python mỗi sáu tiếng.
        Luồng vẫn còn ở đây, nhưng nó chỉ ngồi ĐỢI tiến trình con — đợi thì
        nhả GIL.

        ## Vì sao THỬ, không THẬT

        `thu=True` nghĩa là chẩn, đề xuất, chạy lại đo, ghi sổ — nhưng KHÔNG
        vặn `config.json`. Tầng ty A/B được nên nó có quyền tự nhận (khác
        tầng phân bổ), nhưng "có quyền" và "được bật sẵn" là hai chuyện.
        Bật bằng `tuVanTienHoa: true` trong config, và người bật là người
        chịu trách nhiệm.
        """
        gio = time.time()
        if gio - self._lanTienHoa < float(
                CONFIG.get("nhipTienHoaGiay") or NHIP_TIEN_HOA_GIAY):
            return
        self._lanTienHoa = gio
        if self._luongTienHoa is not None and self._luongTienHoa.is_alive():
            return                    # lượt trước còn chạy — đừng chồng lên

        def _chay():
            import json as _js
            import subprocess as _sp
            lenh = [sys.executable, "-m", "bac.tien_hoa"]
            if CONFIG.get("tuVanTienHoa"):
                lenh.append("--that")
            try:
                # Kế thừa môi trường: `TBT_DATA_DIR` và `TBT_CONFIG` phải đi
                # theo, không thì bản demo hậu kiểm trên băng của bản thật.
                r = _sp.run(lenh, cwd=str(GOC_MA), capture_output=True,
                            text=True, encoding="utf-8", errors="replace",
                            timeout=TREO_TIEN_HOA_GIAY)
                if r.returncode != 0:
                    raise RuntimeError(
                        f"thoát {r.returncode}: {(r.stderr or '')[-300:]}")
                self.tienHoaCuoi = _js.loads((r.stdout or "").strip()
                                             .splitlines()[-1])
                self.loiTienHoa = ""
                bus.ghi(f"tiến hoá: {self.tienHoaCuoi.get('soDoDuoc')} cơ hội "
                        f"hậu kiểm được · "
                        f"{str(self.tienHoaCuoi.get('ghiChu'))[:160]}",
                        loai="he")
            except Exception as e:                        # noqa: BLE001
                self.loiTienHoa = f"{type(e).__name__}: {e}"
                bus.ghi(f"tiến hoá lỗi: {e}", loai="canh")

        self._luongTienHoa = threading.Thread(
            target=_chay, name="tien-hoa", daemon=True)
        self._luongTienHoa.start()

    def _don_so_moi_ngay(self) -> None:
        ngay = time.strftime("%Y-%m-%d", time.gmtime())
        if ngay == self._ngayDonSo:
            return
        self._ngayDonSo = ngay
        n = self.so.don_cu(int(CONFIG["so"]["giuNgay"]))
        nb = may_ghi.don_cu()
        if n or nb:
            bus.ghi(f"dọn: xoá {n} bản ghi sổ và {nb} file băng quá "
                    f"{CONFIG['so']['giuNgay']} ngày", loai="he")

    # ── xuất tờ trình lên Thị Bạc Ty ──────────────────────────────────────
    def to_trinh(self) -> list:
        """Tờ trình ĐÃ NỘP lên Thông Chính Ty trong vòng gần nhất.

        Đọc lại từ Trung Ương chứ **không dựng lại**. Dựng lại thì mỗi lần
        sinh một `ma` mới (uuid), nên tờ trên màn hình và tờ trong sổ đăng ký
        mang hai mã khác nhau cho cùng một cơ hội — người đọc không nối được
        hai bảng, và cả sổ đăng ký mất tác dụng truy nguyên.

        Trung Ương tắt thì dựng tại chỗ, để buồng lái vẫn xem được ty đang
        định trình gì.
        """
        if self.trungUong is not None:
            return list(self.trungUong.toTrinhVongNay)
        oi = {(b.ma, b.san): b.oiUsd for b in self.baoGia}
        xin = float((CONFIG.get("von") or {}).get("moiCoHoiUsd", 100.0))
        return [xuat_to_trinh(c, vonXinUsd=xin,
                              oiLongUsd=oi.get((c.ma, c.sanLong)),
                              oiShortUsd=oi.get((c.ma, c.sanShort)))
                for c in self.coHoi if c.duyet]

    # ── ảnh chụp cho buồng lái và cho lát cắt ─────────────────────────────
    def anh_chup(self) -> dict:
        now = dong_ho.bay_gio_ms()
        q = CONFIG["quet"]
        duyet = [c for c in self.coHoi if c.duyet]

        # Đếm lý do từ chối. Đây là số liệu ĐÁNG GIÁ NHẤT của cả bảng: không
        # cơ hội nào qua cửa thì câu hỏi tiếp theo luôn là "vì sao", và không
        # có bảng này thì người vận hành đi nới bừa từng ngưỡng một.
        #
        # Gộp theo MÃ, không theo câu. Bản đầu cắt chuỗi câu để lấy khoá, mà
        # câu có mang con số — nên "NET sau phí" vỡ thành sáu dòng nói cùng
        # một chuyện, và bảng mất đúng công dụng của nó.
        vi_sao: dict[str, int] = {}
        for c in self.coHoi:
            for ma in c.lyDoMa:
                vi_sao[NHAN.get(ma, ma)] = vi_sao.get(NHAN.get(ma, ma), 0) + 1

        return {
            "maChienLuoc": MA_CHIEN_LUOC,
            "vong": self.vong,
            "batDauLuc": self.batDauLuc,
            "chayDuocGiay": time.time() - self.batDauLuc,
            "tamDung": self.tamDung,
            "che": che_hieu_luc(), "cheKhai": CONFIG.get("che"),
            "nhipGiay": CONFIG["nhipGiay"],
            "giuGio": q["giuGio"],
            "ma": list(q["ma"]),
            "quetCuoiMs": self.quetCuoiMs,
            "quetLauNhatMs": self.quetLauNhatMs,
            "loiVongCuoi": self.loiVongCuoi,
            # Hậu kiểm trên băng: SỔ GIẤY nói một đằng, BĂNG nói một nẻo.
            # Đây là phép đo duy nhất trong cả cỗ máy dám gọi là hậu kiểm,
            # và nó phải nằm ngay trong ảnh chụp chứ không đợi ai bấm nút.
            "tienHoa": self.tienHoaCuoi,
            "loiTienHoa": self.loiTienHoa,
            "cang": [c.suc_khoe.tom_tat() for c in self.cang.values()],
            "dongHo": dong_ho.tom_tat(),
            # "giữ dưới N giờ thì thu ĐÚNG BẰNG KHÔNG" — con số này từng
            # có hàm tính (`gio_giu_toi_thieu`) mà không ai gọi, trong khi
            # docstring của nó viết "buồng lái cần con số này". Một lời
            # khai sai, và nó sai suốt vì không gì đối chiếu.
            "giuToiThieuGio": _giu_toi_thieu(self.baoGia, now),
            "phiSan": {k: v for k, v in CONFIG["san"].items()
                       if (v or {}).get("bat")},
            "ruiRo": self.cong.tom_tat(),
            # Tách hẳn khỏi `ruiRo`: đây là trần vốn CHƯA có hiệu lực, không
            # phải cửa rủi ro. Gộp chung là bày ba con số không chặn gì dưới
            # nhãn "đang có hiệu lực" — đúng lỗi vừa gỡ.
            "von": dict(CONFIG.get("von") or {}),
            "baoGia": [b.tom_tat(now) for b in self.baoGia],
            "coHoi": [c.tom_tat() for c in self.coHoi[:60]],

            # TỜ TRÌNH — cùng những cơ hội ấy, viết bằng ngôn ngữ chung của
            # Thị Bạc Ty. `coHoi` là ngôn ngữ NỘI BỘ của ty (có `soMocLong`,
            # `intervalShortGio` — ty Tín Dụng không hiểu và không cần hiểu);
            # `toTrinh` là thứ trung ương đọc được.
            #
            # Chỉ trình cơ hội đã QUA cổng ty. Cổng ty là tầng rủi ro thứ
            # nhất; trình cả thứ chính mình đã chặn là đẩy việc sang trung
            # ương và làm loãng sổ đăng ký.
            "toTrinh": [t.tom_tat() for t in self.to_trinh()],
            "soDuyet": len(duyet),
            "viSaoTuChoi": vi_sao,
            "so": self.so.thong_ke(),
            "bang": may_ghi.tom_tat(),
            "doDai": [
                {**self.so.do_dai(c.ma, c.sanLong, c.sanShort),
                 "ma": c.ma, "sanLong": c.sanLong, "sanShort": c.sanShort}
                for c in self.coHoi[:12]
            ],
            # THỊ BẠC TY — bộ máy đứng trên ty này. Cả chín tầng trong một
            # khối, để buồng lái không phải ghép từ nhiều đường API.
            # Router và sổ engine — HAI cơ chế chạy mà buồng lái không
            # thấy. Một cơ chế không ai nhìn được là một cơ chế không ai
            # tin, và nó im lặng hỏng đúng như ba cửa giả đã im lặng.
            "router": (self.dinhTuyen.tom_tat()
                       if getattr(self, "dinhTuyen", None) is not None
                       else {"co": False,
                             "vi": "Router chưa dựng — các ty giữ nguyên "
                                   "khai báo phiConThieu"}),
            "dongCoChuaCo": _tom_dong_co(),
            "nguonGas": (self.nguonGas.tom_tat()
                         if getattr(self, "nguonGas", None) is not None
                         else {}),
            "nguonCau": (self.nguonCau.tom_tat()
                         if getattr(self, "nguonCau", None) is not None
                         else {}),
            # Kho báo giá cầu nạp lại từ đĩa lúc khởi động. Buồng lái phải
            # thấy: "chín tuyến đo được" mà không nói chúng đến từ ĐÂU thì
            # người đọc không phân biệt được số vừa hỏi với số nạp lại.
            "khoCau": getattr(self, "napKhoCau", None),
            "trungUong": (self.trungUong.anh_chup()
                          if self.trungUong is not None else
                          {"tat": True,
                           "loiNhac": "Trung Ương đang TẮT — ty vẫn quét và "
                                      "vẫn trình, nhưng không tầng nào cấp "
                                      "vốn. Bật ở CONFIG['trungUong']['bat']."}),
            "duongSo": str(DATA_DIR),
            "nhatKy": bus.gan_day(80),
        }


runtime = Runtime()
