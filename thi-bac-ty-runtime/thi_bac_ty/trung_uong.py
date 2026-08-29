"""TRUNG ƯƠNG — nơi khép vòng, và nơi ép mọi tầng đi đúng thứ tự.

Bảy module kia mỗi cái làm một việc. File này là thứ khiến chúng thành **một
hệ thống** chứ không phải một đống module cạnh nhau.

## Vòng tuần hoàn

    THỊ TRƯỜNG
        │  các ty quét
        ▼
    TỜ TRÌNH ────► THÔNG CHÍNH TY ────► SỔ ĐĂNG KÝ (PHAT_HIEN)
                                              │
                                              ▼
                                        RỦI RO TỔNG   ◄── DANH MỤC
                                       cho tối đa $X
                                              │
                                              ▼
                                        PHÂN BỔ VỐN
                                       cấp TUẦN TỰ
                                              │
                                              ▼
                                     ĐIỀU PHỐI THỰC THI
                                     máy trạng thái hai chân
                                              │
                                              ▼
                                          SỔ CÁI
                                              │
                                              ▼
                                        CHẨN ĐOÁN
                                              │
                                              ▼
                                     XÉT LẠI THAM SỐ
                                              │
                                              └──► quay lại THỊ TRƯỜNG

Vòng này là thứ nâng `scan → record → replay → diagnose → evolve` của MỘT ty
lên tầm hệ thống. Ty vẫn tự tiến hoá tham số chuyên môn của nó; Trung Ương
tiến hoá tham số **phân bổ và rủi ro tổng** — hai chuyện khác nhau, hai vòng
khác nhau, và chúng không được giẫm lên nhau.

## Bốn luật KHÔNG được vi phạm, và có phép kiểm canh từng luật

**1. Không tầng nào đi tắt.** Vốn chỉ tới được vị thế qua đúng đường
Thông Chính → Sổ Đăng Ký → Rủi Ro Tổng → Phân Bổ → Thực Thi. `so_dang_ky`
từ chối mọi chuyển trạng thái nhảy cóc và đếm số lần bị từ chối.

**2. Cầu dao đứng trên tất cả.** `mot_vong()` hỏi `cau_dao.cho_phep()`
TRƯỚC khi phân bổ. Ngắt thì vẫn quét, vẫn ghi nhận, vẫn chẩn đoán — chỉ
KHÔNG cam kết vốn. Dừng cả việc quan sát là tự làm mình mù đúng lúc cần
nhìn nhất.

**3. Ty không biết Trung Ương.** `Ty` chỉ thấy `thong_chinh.nop()`. Nó
không có tham chiếu tới Danh Mục, Sổ Cái hay Cầu Dao.

**4. Mọi quyết định về VỐN vào Sổ Cái kèm LÝ DO.** Kể cả từ chối. Nhất là
từ chối — một hệ thống chỉ ghi lại lúc nó đồng ý thì lịch sử của nó toàn
thắng lợi.

Ranh giới của "về vốn": Rủi Ro Tổng từ chối thì vào Sổ Cái, vì đó là một
quyết định KHÔNG cấp tiền. Còn cơ hội bị loại ở khâu xếp hạng (NET ≤ 0) thì
chỉ vào Sổ Đăng Ký — chúng chưa bao giờ tới được tầng vốn, và mỗi lượt quét
đẻ ra hàng chục cái, nên đưa vào Sổ Cái là chôn mọi dòng tiền thật dưới một
đống dòng không đồng nào. Sổ Cái là sổ TIỀN; Sổ Đăng Ký là sổ VÒNG ĐỜI, và
mọi lần từ chối đều có lý do trong sổ ấy.
"""
from __future__ import annotations

import datetime as _dt
import json
from dataclasses import dataclass, field
from pathlib import Path

from .ban_tham_so import KhoThamSo
from .cau_dao import CauDao
from .che_van_hanh import che_cua_ty, von_can_de_chay, von_hoa_ha_tang
from .chan_doan_he import chan_doan_he, de_xuat
from .chay_lai_he import doi_chieu, thu_hoach
from .cong_duyet import xet_duyet
from .danh_muc import DanhMuc
from .doi_soat_vi_the import canh as canh_vi_the, doi_soat as doi_soat_vi_the
from .ke_toan import (LatCatKeToan, SoViThe, SoVonGio, phi_vao_thieu,
                      phi_vao_usd)
from .luu_danh_muc import luu as luu_danh_muc, nap as nap_danh_muc
from .hieu_nang import DuongNav, doi_chieu_giay_that
from .phan_bo import PhanBo
from .rui_ro_tong import RuiRoTong
from .so_cai import ButToan, SoCai
from .so_dang_ky import SoDangKy
from .thong_chinh import ThongChinh
from .thuc_thi import DieuPhoiThucThi, YChiThucThi
from .nhap_so_ngoai import NhapSoNgoai
from .von_ngoai import DocVonNgoai

#: Nhịp mặc định cho vòng chẩn đoán → đề xuất. `config.json` đè được.
NHIP_HOC_GIAY = 3600.0

MAC_DINH = {
    "vonBanDauUsd": 1000.0,
    #: Bao lâu chẩn đoán + đề xuất một lượt. Triệu chứng của bộ máy đổi
    #: theo GIỜ, không theo giây; chạy mỗi vòng là đốt công cho một bức
    #: tranh gần như đứng yên.
    "nhipHocGiay": 3600.0,
    #: Cho máy TỰ đóng vị thế lãi thấp để nhường chỗ cho cơ hội tốt hơn.
    #: Tắt mặc định: xoay chỗ là ĐỔI DANH MỤC, không phải đổi một con số
    #: hiển thị, và người bật là người chịu trách nhiệm.
    "tuXoayCho": False,
    #: Lúc tự động thì đòi lợi ròng phải bằng NGẦN NÀY LẦN phí đổi. Rộng
    #: hơn mức 1,0 của phép ĐO, vì phép đo có người nhìn từng dòng còn
    #: đường tự động thì không — và mọi sai số của `netUocBps` đều dồn vào
    #: đúng cái hiệu số nhỏ mà phép tính này dựa lên.
    "bienXoayCho": 1.5,
    "duLieuTrong": "thi-bac-ty",
    "nguongCauDao": {
        "lechDongHoToiDaGiay": 60.0,
        "soCangChetToiDa": 0,
        "tuoiToiDaGiay": 300.0,
        "sutVonToiDaPct": 10.0,
    },
    "ruiRoTong": {},
    "phanBo": {},
    "giuNgaySoDangKy": 90,
    #: Cỗ máy KHÁC đang giữ vốn mà Thị Bạc Ty không quản. Xem
    #: `thi_bac_ty/von_ngoai.py` và mục "NỢ KIẾN TRÚC" trong README.
    #: `{tên: url}`. Rỗng = không có vốn ngoài nào được khai.
    "vonNgoai": {},
    #: Sổ cái của cỗ máy ngoài, nhập vào sổ này. Rỗng ở đây và khai ngoài
    #: Trung Ương — nó không được biết cỗ máy nào tồn tại.
    "soNgoai": {},
    #: VPS + RPC + API. Đối thủ THẬT của vốn nhỏ: $10/tháng là
    #: $120/năm, trong khi $100 vốn kiếm 20% chỉ ra $20.
    "chiPhiHaTangUsdThang": 10.0,
    #: Cùng MỘT cơ hội chỉ vào sổ đăng ký một lần trong ngần này giây.
    #:
    #: Ty quét mỗi 30 giây, và một chênh lệch funding sống hàng giờ. Không có
    #: cửa này thì một cơ hội duy nhất vào sổ 120 lần mỗi giờ, mỗi lần một mã
    #: mới. Hai hậu quả, và hậu quả thứ hai tệ hơn nhiều:
    #:
    #:   1. sổ phình — 30 cơ hội × 2.880 lượt/ngày × 90 ngày ≈ 7,8 triệu dòng
    #:   2. **cái phễu nói dối** — mẫu số thành 86.400 "phát hiện" cho 30 cơ
    #:      hội có thật, nên mọi tỉ lệ sống sót đều chia cho một con số bịa.
    #:
    #: Cái phễu là thứ duy nhất trả lời được "cỗ máy này có học không". Một
    #: mẫu số sai làm hỏng đúng thứ cả Sổ Đăng Ký sinh ra để đo.
    "nhipGhiNhanGiay": 3600.0,
}


def _dau_van(tt) -> str:
    """Dấu vân tay của một CƠ HỘI, khác với `tt.ma` là dấu của một LẦN TRÌNH.

    Cùng ty, cùng tài sản, cùng bộ chân (bên + cảng + CHUỖI) thì là cùng một
    cơ hội, dù quét lại một trăm lần. Cố ý KHÔNG gộp giá hay NET vào đây:
    chúng nhúc nhích mỗi lượt quét, nên gộp vào là mỗi lượt lại ra một vân
    tay mới và cửa chống trùng thành vô dụng.

    **Chuỗi phải có mặt.** Bản đầu chỉ lấy `bên@cảng`, và với ty phái sinh
    thì không sao — bốn sàn perp đều là sàn tập trung, mỗi sàn một cảng.
    Nhưng `aave-v3 USDC trên Ethereum` và `aave-v3 USDC trên Polygon` là
    HAI thị trường khác hẳn: khác lãi suất, khác thanh khoản, khác gas.
    Thiếu chuỗi thì chúng cùng một vân tay, và cái thứ hai bị bỏ trong im
    lặng như thể nó là bản trùng của cái thứ nhất.

    Lỗi này chỉ lộ ra khi ty thứ HAI cắm vào — và đó đúng là công dụng của
    phép thử "hai chiến lược khác hẳn nhau có sống chung được không".
    """
    return (f"{tt.chienLuoc}|{tt.taiSan}|"
            + ",".join(sorted(f"{c.ben}@{c.cang}@{c.chuoi or '-'}"
                              for c in tt.chan)))


def _dau_van_tu_dict(d: dict) -> str | None:
    """Cùng dấu vân tay ấy, dựng từ bản `tom_tat()` đã lưu ở sổ vị thế.

    Cần nó để XOÁ dấu lúc vị thế đóng. Phải khớp từng chữ với hàm trên, nên
    hai chỗ này sửa cùng nhau — và phép kiểm dựng cả hai từ CÙNG một tờ
    trình rồi đòi chúng bằng nhau, để không ai sửa một bên rồi quên bên kia.
    """
    if not isinstance(d, dict):
        return None
    chan = d.get("chan")
    if not isinstance(chan, (list, tuple)) or not chan:
        return None
    try:
        return (f"{d['chienLuoc']}|{d['taiSan']}|"
                + ",".join(sorted(
                    f"{c['ben']}@{c['cang']}@{c.get('chuoi') or '-'}"
                    for c in chan)))
    except (KeyError, TypeError):
        return None


@dataclass
class LatCatVong:
    luc: str
    soTyChay: int = 0
    soToTrinhNhan: int = 0
    soGhiNhan: int = 0
    soBoTrung: int = 0
    cauDaoNgat: bool = False
    lyDoNgat: list = field(default_factory=list)
    phanBo: dict | None = None
    soThucThi: int = 0
    soPhangGap: int = 0

    def tom_tat(self) -> dict:
        return {"luc": self.luc, "soTyChay": self.soTyChay,
                "soToTrinhNhan": self.soToTrinhNhan,
                "soGhiNhan": self.soGhiNhan,
                "soBoTrung": self.soBoTrung,
                "cauDaoNgat": self.cauDaoNgat, "lyDoNgat": list(self.lyDoNgat),
                "phanBo": self.phanBo, "soThucThi": self.soThucThi,
                "soPhangGap": self.soPhangGap}


class TrungUong:
    def __init__(self, thuMucDuLieu: Path, cau_hinh: dict | None = None) -> None:
        c = {**MAC_DINH, **(cau_hinh or {})}
        self.c = c
        d = Path(thuMucDuLieu)
        d.mkdir(parents=True, exist_ok=True)
        ten = c["duLieuTrong"]

        self.so_cai = SoCai(d / f"{ten}-so-cai.sqlite3")
        self.so_dang_ky = SoDangKy(d / f"{ten}-so-dang-ky.sqlite3")
        self.thong_chinh = ThongChinh()
        self.danh_muc = DanhMuc(float(c["vonBanDauUsd"]), nguonThat=False)
        # Bản tham số ĐANG CHẠY quyết định cấu hình hai tầng dưới, không
        # phải `cau_hinh` truyền vào. Nếu kho đã có bản, nó thắng — nếu
        # không thì `cau_hinh` là bản số 1. Ngược lại thì mỗi lần khởi động
        # lại sẽ âm thầm quay về mặc định, xoá sạch mọi bản đã duyệt.
        self.kho_tham_so = KhoThamSo(d / f"{ten}-ban-tham-so.sqlite3")
        ban = self.kho_tham_so.hien_hanh()
        if ban is None:
            self.rui_ro_tong = RuiRoTong(c["ruiRoTong"])
            self.phan_bo = PhanBo(c["phanBo"])
            self.kho_tham_so.dat(
                {"ruiRoTong": dict(self.rui_ro_tong.c),
                 "phanBo": dict(self.phan_bo.c)},
                "khoi-tao", "bản đầu tiên, dựng từ mặc định và config")
        else:
            self.rui_ro_tong = RuiRoTong(ban.thamSo.get("ruiRoTong") or {})
            self.phan_bo = PhanBo(ban.thamSo.get("phanBo") or {})
        self.duongNav = DuongNav()
        #: Đếm cho luật «còn ghế thì không đuổi ai» — xem `_xoay_cho_neu_duoc`.
        self._vongGheTrongKhongLap = 0
        self._soViTheVongTruoc = 0
        # Mốc BẬT MÁY. Bộ đếm cơ hội thô nằm trong RAM của từng ty nên
        # nó đếm từ lúc này; mọi con số ghép cạnh nó phải bó về cùng
        # cửa sổ, không thì phễu trộn hai quãng thời gian.
        self.lucKhoiDong = _gio_iso()
        self.cau_dao = CauDao()
        self.thuc_thi = DieuPhoiThucThi()

        #: Danh mục SỐNG QUA lần khởi động lại — xem `luu_danh_muc.py`.
        #:
        #: Nạp TRƯỚC `doi_soat_vi_the`: đối soát so sổ đăng ký với danh
        #: mục, nên phải để danh mục đầy đủ rồi mới so. Đảo thứ tự là đối
        #: soát thấy danh mục rỗng, đóng sạch vị thế ở sổ, rồi bản nạp
        #: mới về sau lại dựng lên những vị thế vừa bị đóng.
        #: Tổng mọi đồng ĐÃ đi qua `_ghi_tien`. Đối chiếu với
        #: `danh_muc.laiLoDaThucHienUsd` mỗi vòng — xem `lech_tien()`.
        #: Dựng TRƯỚC khi nạp bản lưu: nạp rồi mới dựng là dựng đè lên đúng
        #: thứ vừa nạp về, và phép đối chiếu quay lại kêu lệch oan.
        self.tienDaGhiUsd = 0.0
        #: Vốn-giờ và thu ròng — mẫu số đúng cho «tiền ĐANG DÙNG lãi bao
        #: nhiêu». Xem `ke_toan.SoVonGio`. Dựng TRƯỚC khi nạp bản lưu: nạp
        #: rồi mới dựng là dựng đè lên đúng thứ vừa nạp về.
        self.soVonGio = SoVonGio(tuGiay=_gio_he(), denGiay=_gio_he())
        #: Vốn CHỦ bỏ thêm vào, cộng dồn. Nằm ở bản lưu chứ không ở config:
        #: `vonBanDauUsd` trong config là vốn KHỞI ĐIỂM và nó phải đổi được;
        #: `napThemUsd` là chuỗi sự kiện đã xảy ra và nó không được mất.
        self.napThemUsd = 0.0
        self._dongVonChoGhi = 0.0
        self.duongLuu = d / f"{ten}-danh-muc.json"
        self.napLuu = nap_danh_muc(self.duongLuu, self.danh_muc,
                                   self.duongNav)
        self.soViThe = self.napLuu.pop("_soViThe", {})
        # Nạp SAU khi `__init__` đã dựng sổ mới: bản trên đĩa thắng, còn
        # thiếu thì giữ sổ vừa dựng (bắt đầu cộng từ bây giờ).
        _vg = self.napLuu.pop("_soVonGio", None)
        if _vg is not None:
            self.soVonGio = _vg
        # Vốn đã nạp phải cộng LẠI vào vốn gốc: `vonBanDauUsd` dựng từ
        # config (vốn khởi điểm), còn tiền mặt trong bản lưu ĐÃ gồm phần
        # nạp. Không cộng thì hai vế lệch nhau đúng bằng số đã nạp, và sụt
        # vốn đọc ra một con số bịa.
        # Bộ đếm đối chiếu phải sống cùng lãi lỗ đã thực hiện. Bản lưu CŨ
        # không có nó: lúc ấy lấy thẳng `laiLoDaThucHienUsd` làm điểm xuất
        # phát, vì mọi đồng trong đó ĐÃ từng đi qua `_ghi_tien` ở một lần
        # chạy trước — coi là 0 thì kêu lệch oan đúng bằng ngần ấy.
        _tdg = self.napLuu.pop("_tienDaGhiUsd", 0.0)
        self.tienDaGhiUsd = float(
            _tdg if self.napLuu.get("coTienDaGhi")
            else self.danh_muc.laiLoDaThucHienUsd)
        self.napThemUsd = float(self.napLuu.pop("_napThemUsd", 0.0) or 0.0)
        if self.napThemUsd:
            self.danh_muc.vonBanDauUsd += self.napThemUsd

        #: Đối soát NGAY lúc khởi động, trước khi vòng nào chạy. Sổ đăng ký
        #: sống trên đĩa còn danh mục dựng lại rỗng, nên đúng lúc này là
        #: lúc lệch lớn nhất — và cũng là lúc duy nhất sửa được mà không
        #: giẫm lên vị thế của vòng đang chạy. Xem `doi_soat_vi_the.py`.
        self.doiSoatViThe = doi_soat_vi_the(
            self.so_dang_ky, self.danh_muc, self.thuc_thi, self.so_cai,
            self.cau_dao)
        #: GIỮ RIÊNG bản đối soát lúc khởi động. `doiSoatViThe` bị lượt
        #: đo mỗi vòng ghi đè sau đúng một nhịp, nên nếu chỉ có nó thì
        #: "vừa đóng 4 tờ mồ côi, 500 USD" sống được 30 giây rồi biến mất
        #: khỏi buồng lái — trong khi đó là việc đáng kể nhất một lần khởi
        #: động làm. Sổ cái vẫn giữ bút toán, nhưng buồng lái phải nói ra
        #: mà không bắt người đi tra sổ.
        self.doiSoatKhoiDong = self.doiSoatViThe

        self.docVonNgoai = [DocVonNgoai(t, u)
                            for t, u in (c["vonNgoai"] or {}).items()]
        #: Sổ nhập kết toán từ cỗ máy ngoài — MỘT sổ của sự thật.
        #: `{"ten": {"url": ..., "chienLuoc": ...}}`, khai ngoài Trung Ương.
        self.nhapSoNgoai = [
            NhapSoNgoai(t, x["url"], x["chienLuoc"],
                        x.get("duongDan", "ketToan"))
            for t, x in (c.get("soNgoai") or {}).items()]
        self.ty: dict[str, object] = {}
        self.vong = 0
        self.latCatCuoi: LatCatVong | None = None
        #: Tờ trình ĐÃ NỘP trong vòng gần nhất. Buồng lái đọc chỗ này chứ
        #: không tự dựng lại — dựng lại thì mỗi lần một mã khác, và người
        #: đọc không nối được tờ trên màn hình với tờ trong sổ đăng ký.
        self.toTrinhVongNay: list = []
        #: Sổ vị thế đang mở của Trung Ương: mã tờ trình → `SoViThe`.
        #: Tách khỏi `DanhMuc.viThe` vì Danh Mục trả lời "đang phơi nhiễm
        #: bao nhiêu", còn sổ này trả lời "đã sống bao lâu, đã cộng dồn
        #: được gì". Chỉ sống trong RAM — vị thế mô phỏng không mang qua
        #: được lần khởi động lại, và `doi_soat_vi_the` dọn phần sót ở sổ.
        self.latCatKeToan = LatCatKeToan()
        self.latCatXoayCho = None
        #: dấu vân cơ hội → lần cuối vào sổ (giây, đồng hồ đơn điệu)
        self._dauVet: dict[str, float] = {}
        self.soBoTrung = 0
        self.hocCuoi: dict | None = None
        self._lanHoc = 0.0
        self.loiHoc = ""
        self._deXuatChoDuyet = None
        self._soXet = d / f"{ten}-xet-tham-so.jsonl"
        self._ngayDon = ""

    # ── đăng ký ty ────────────────────────────────────────────────────────
    def dang_ky(self, ty) -> bool:
        """Nhận một ty vào hệ thống. Khai sai thì **chết ở cửa**.

        Hỏi `ty.kiem_khai()` chứ KHÔNG hỏi `type(ty).kiem_khai()`. Khác biệt
        nhỏ, hậu quả thật: một ty được bọc — chẳng hạn để cho nó nhịp quét
        riêng — thì `type(ty)` là lớp bọc, và lớp bọc không có `kiem_khai`.
        Trung Ương sẽ từ chối một ty hoàn toàn hợp lệ, và từ chối vì một lý
        do chẳng liên quan gì tới ty ấy.

        Đây cũng là chiều đúng: Trung Ương quan tâm ty **trả lời được gì**,
        không quan tâm nó thuộc lớp nào. Soi lớp cụ thể là buộc mọi ty phải
        kế thừa trực tiếp, và điều đó chặn cả một lớp cách dùng hợp lệ.
        """
        loi = ty.kiem_khai()
        if loi:
            self.so_cai.ghi(ButToan(
                "TU_CHOI", "từ chối đăng ký ty: " + "; ".join(loi),
                0.0, getattr(ty, "ma", None), None, {"khaiSai": loi}))
            return False
        if ty.ma in self.ty:
            return False
        self.ty[ty.ma] = ty
        return True

    # ── một vòng ──────────────────────────────────────────────────────────
    def mot_vong(self, *, lechDongHoGiay: float | None = None,
                 cangChet: list[str] | None = None,
                 tuoiXauNhatGiay: float | None = None) -> LatCatVong:
        """Một vòng trọn vẹn. Xem sơ đồ ở đầu file."""
        lat = LatCatVong(luc=_bay_gio())
        self.vong += 1

        # ── 1. các ty quét và trình ──────────────────────────────────────
        for ty in self.ty.values():
            ty.mot_luot(self.thong_chinh)
            lat.soTyChay += 1

        nhan = self.thong_chinh.lay_het()
        lat.soToTrinhNhan = len(nhan)
        self.toTrinhVongNay = list(nhan)

        # ── 2. ghi nhận vào sổ đăng ký ───────────────────────────────────
        song = []
        nhip = float(self.c["nhipGhiNhanGiay"])
        gio = _monotonic()
        for tt in nhan:
            van = _dau_van(tt)
            truoc = self._dauVet.get(van)
            if truoc is not None and gio - truoc < nhip:
                # Vẫn là cơ hội cũ, chưa tới nhịp ghi lại. Không vào sổ, và
                # cũng KHÔNG đi tiếp — nó đang có một tờ trình sống trong sổ
                # rồi; cấp vốn lần nữa là cấp hai lần cho một cơ hội.
                lat.soBoTrung += 1
                self.soBoTrung += 1
                continue
            if self.so_dang_ky.ghi_nhan(tt):
                self._dauVet[van] = gio
                lat.soGhiNhan += 1
                # Tờ trình đã qua cổng ty trước khi được nộp — ghi ngay bước
                # ấy để cái phễu có mẫu số đúng.
                self.so_dang_ky.chuyen(tt.ma, "DUYET_TY", "qua cổng ty")
                song.append(tt)

        # ── 2b. vốn NGOÀI — đọc trước khi tính bất kỳ trần nào ───────────
        # Trần của Rủi Ro Tổng tính theo NAV. Đọc vốn ngoài sau khi đã phân
        # bổ thì cả vòng ấy chạy trên một NAV thiếu, và trần rộng hơn sự
        # thật đúng vào lúc nó cần chặt nhất.
        for d in self.docVonNgoai:
            self.danh_muc.ghi_von_ngoai(d.doc())

        # Nhập kết toán cỗ máy ngoài vào CÙNG một sổ cái. Nhịp riêng (2
        # phút) vì kết toán không xảy ra theo giây, và hỏi dồn dập không
        # làm bản ghi tới sớm hơn.
        #
        # Bọc try vì một sổ ngoài hỏng KHÔNG được giết vòng đang chạy —
        # nhưng `soLoi` đếm ra được và buồng lái hiện nó.
        for n in self.nhapSoNgoai:
            if not n.den_han():
                continue
            try:
                n.nhap(self.so_cai)
            except Exception:                                 # noqa: BLE001
                n.soLoi += 1

        # Đường NAV ghi ở ĐÂY, sau khi đã cộng vốn ngoài và trước khi phân
        # bổ: đó là ảnh chụp gia sản lúc bắt đầu vòng, và mọi phép đo sụt
        # vốn phải dựa trên cùng một thời điểm trong vòng.
        # ── 2b. KẾ TOÁN vị thế đang mở, TRƯỚC khi ghi đường NAV ─────────
        # Thứ tự bắt buộc: kế toán xong thì `navUsd` mới gồm dòng tiền của
        # vòng này. Ghi đường NAV trước là ghi lại ảnh chụp của vòng
        # TRƯỚC, và mọi phép đo sụt vốn lệch đi đúng một nhịp.
        self.latCatKeToan = self._ke_toan_vi_the()
        self.latCatXoayCho = self._xoay_cho_neu_duoc()

        self.duongNav.ghi(self.danh_muc.navUsd,
                          dongVonUsd=self._dongVonChoGhi)
        self._dongVonChoGhi = 0.0

        # ── 3. cầu dao — TRƯỚC khi cam kết bất cứ đồng nào ───────────────
        sut = None
        if self.danh_muc.vonBanDauUsd > 0:
            sut = max(0.0, (1.0 - self.danh_muc.navUsd
                            / self.danh_muc.vonBanDauUsd) * 100.0)
        # Lệch sổ/danh mục đo lại MỖI VÒNG, không chỉ lúc khởi động: đo một
        # lần rồi tin mãi là đúng cái thói quen mà `von-ngoai-mu` đã dạy —
        # trạng thái đọc được thì phải đọc lại, không được nhớ.
        self.doiSoatViThe = canh_vi_the(
            self.so_dang_ky, self.danh_muc, self.thuc_thi, self.so_cai,
            self.cau_dao)
        self.cau_dao.tu_soat(
            lechDongHoGiay=lechDongHoGiay, cangChet=list(cangChet or []),
            tuoiXauNhatGiay=tuoiXauNhatGiay, sutVonPct=sut,
            nguong=self.c["nguongCauDao"], so_cai=self.so_cai,
            vonNgoaiDayDu=self.danh_muc.ngoaiDayDu)

        duoc, ly = self.cau_dao.cho_phep()
        lat.cauDaoNgat = not duoc
        lat.lyDoNgat = list(ly)

        if not duoc:
            # Vẫn quét, vẫn ghi nhận, vẫn chẩn đoán — CHỈ không cam kết vốn.
            # Dừng cả việc quan sát là tự làm mình mù đúng lúc cần nhìn nhất.
            for tt in song:
                self.so_dang_ky.chuyen(tt.ma, "TU_CHOI",
                                       # Mã trước, câu sau — cùng kỷ luật
                                       # `phan_bo.ly_do()`. "CẦU DAO NGẮT"
                                       # có dấu cách và chữ hoa nên chẩn
                                       # đoán không nhận ra được nó là mã,
                                       # và 520 lần từ chối lớn nhất của cỗ
                                       # máy rơi vào ô «không phân loại».
                                       "cau-dao-ngat: " + "; ".join(ly))
            return self._cuoi_vong(lat)

        # ── 4. rủi ro tổng + phân bổ (cấp TUẦN TỰ, xem phan_bo.py) ───────
        pb = self.phan_bo.chia(song, self.rui_ro_tong, self.danh_muc,
                               self.so_cai, lat.luc)
        lat.phanBo = pb.tom_tat()

        cap = {x["maToTrinh"] for x in pb.daCap}
        tu_choi = {x["maToTrinh"]: _ly_do(x) for x in pb.tuChoi}
        for tt in song:
            if tt.ma in cap:
                self.so_dang_ky.chuyen(tt.ma, "DUYET_RUI_RO", "qua rủi ro tổng")
                self.so_dang_ky.chuyen(tt.ma, "DA_CAP_VON", "đã cấp vốn")
            else:
                self.so_dang_ky.chuyen(
                    tt.ma, "TU_CHOI",
                    tu_choi.get(tt.ma, "không được cấp vốn")[:400])

        # ── 5. thực thi (mô phỏng, nhưng đi đúng máy trạng thái) ─────────
        theo_ma = {tt.ma: tt for tt in song}
        for x in pb.daCap:
            tt = theo_ma.get(x["maToTrinh"])
            if tt is None:
                continue
            p = self.thuc_thi.chay(
                YChiThucThi(tt.ma, tt.chienLuoc, tt.chan, x["capUsd"],
                            f"phân bổ cấp {x['capUsd']:.0f} USD"),
                self.so_cai)
            lat.soThucThi += 1
            if p.trangThai == "DA_DOI_SOAT":
                # đóng gấp vì legging — vốn phải trả lại danh mục
                lat.soPhangGap += 1
                self.danh_muc.dong(tt.ma, 0.0)
                self.so_dang_ky.chuyen(tt.ma, "HONG",
                                       "chân B không khớp, đã đóng gấp")
            elif p.trangThai == "GIU":
                self.so_dang_ky.chuyen(tt.ma, "DA_MO", "hai chân đã vào")
                self._mo_so_vi_the(tt, x["capUsd"])

        return self._cuoi_vong(lat)

    def _cuoi_vong(self, lat: LatCatVong) -> LatCatVong:
        """MỘT cửa duy nhất để rời `mot_vong` — mọi lối ra đi qua đây.

        Vòng có HAI lối ra: cầu dao ngắt thì thoát sớm ở bước 3, không thì
        chạy hết tới bước 5. Trước 29/08 mỗi lối làm một việc khác nhau, và
        lối ngắt bỏ mất hai thứ:

        **Bỏ `_luu_danh_muc`.** Kế toán đã chạy ở bước 2b rồi mới tới cầu
        dao, nên lúc ngắt vẫn có thu nhập vừa cộng vào sổ vị thế — và không
        ai ghi nó xuống đĩa. Cầu dao ngắt vì sụt vốn thì nó ngắt HÀNG GIỜ;
        khởi động lại giữa quãng ấy là mất trắng phần đã cộng.

        **Bỏ `_hoc_dinh_ky`.** Đúng lúc bộ máy hỏng thì nó thôi chẩn đoán,
        trong khi comment ngay trên nhánh ấy hứa «vẫn quét, vẫn ghi nhận,
        vẫn chẩn đoán — CHỈ không cam kết vốn». Lời hứa đúng, mã sai.

        Cùng một bài với `_ghi_tien` và với cửa vòng đời khung của Khâm
        Thiên Giám: **hai lối ra thì sớm muộn chúng lệch nhau**. Gộp lại
        một cửa thì thêm việc cuối vòng chỉ phải nhớ một chỗ.
        """
        self.latCatCuoi = lat
        self._don_dinh_ky()
        self._hoc_dinh_ky()
        self._luu_danh_muc()
        return lat

    def _hoc_dinh_ky(self) -> None:
        """Chẩn đoán và ĐỀ XUẤT theo nhịp riêng. Không tự áp dụng.

        Trước 29/08 `hoc()` chỉ chạy khi có người `POST /api/hoc`, nên
        `hocCuoi` là `None` vĩnh viễn và `banThamSo.soBan` đứng ở 1 —
        **vòng tự tiến hoá đã dựng xong nhưng chưa bao giờ quay một
        vòng**. Cùng lớp hỏng với lát cắt cung tĩnh: một cơ chế có mã, có
        phép kiểm, có chỗ hiện trên buồng lái, và không ai gọi.

        Chạy tự động ở đây AN TOÀN vì `hoc()` chỉ đề xuất: đường áp dụng
        là `ap_dung(nguoi)` và nó đòi TÊN NGƯỜI, đúng bất đối xứng của cầu
        dao. Máy được phép nghĩ ra; người quyết định.

        Nhịp RIÊNG và thưa: chẩn đoán đọc cả ảnh chụp rồi chạy lại phân bổ
        trên toàn bộ tờ trình đã ghi. Chạy mỗi 30 giây là đốt công cho một
        bức tranh gần như đứng yên — triệu chứng của bộ máy đổi theo giờ,
        không theo giây.
        """
        import time as _t
        # `or` ở đây sẽ nuốt số 0: `nhipHocGiay: 0` nghĩa là «chẩn mỗi
        # vòng», một cấu hình hợp lệ, mà `0 or 3600` lại ra 3600. Cùng cái
        # bẫy «None khác 0» đã gỡ ở ba chỗ khác trong cỗ máy này.
        nhip = self.c.get("nhipHocGiay")
        nhip = NHIP_HOC_GIAY if nhip is None else float(nhip)
        gio = _t.time()
        if gio - getattr(self, "_lanHoc", 0.0) < nhip:
            return
        self._lanHoc = gio
        try:
            self.hoc(ghiSo=True)
        except Exception as e:                            # noqa: BLE001
            self.loiHoc = f"{type(e).__name__}: {e}"
        else:
            self.loiHoc = ""

    def _xoay_cho_neu_duoc(self):
        """Đóng vị thế lãi thấp để nhường chỗ — CHỈ KHI người đã bật.

        Chạy NGAY SAU kế toán và TRƯỚC cầu dao: kế toán xong thì lãi lỗ của
        vị thế sắp đóng đã đủ, và đóng trước phân bổ thì chỗ trống có ngay
        trong lượt phân bổ của chính vòng này. Đóng sau phân bổ là để trống
        một chỗ suốt cả vòng.

        Chỉ ĐÓNG, không mở. Chỗ trống rồi thì `phan_bo.chia()` ở bước 4 tự
        rót vào theo đúng thứ hạng của nó — dựng một đường mở thứ hai ở đây
        là dựng một cửa cấp vốn KHÔNG đi qua Rủi Ro Tổng.
        """
        from .xoay_cho import do_xoay_cho
        gio = _gio_he()
        # ĐÍCH phải qua được Rủi Ro Tổng, không thì bảng này hứa một việc
        # Phân Bổ sẽ từ chối làm.
        #
        # Đo 30/08 trên máy sống: «15 chỗ đáng đổi · +1.394 USD», và bốn
        # dòng lớn nhất đều trỏ sang `yield.pendle_pt.v1` — đúng cái ty bị
        # chặn sạch vì khoá vốn 2.119 giờ > trần 720. Cả một con số đẹp
        # dựng trên những lần đổi không bao giờ xảy ra được.
        #
        # Hỏi CHÍNH tầng ấy chứ không chép luật của nó xuống đây: hai bản
        # chép sẽ lệch nhau đúng vào ngày ai đó sửa một bản, và bản lệch ở
        # đây sẽ nói dối theo hướng lạc quan.
        duoc, chan = [], 0
        for tt in self.toTrinhVongNay:
            try:
                if self.rui_ro_tong.xet(tt, self.danh_muc).duyet:
                    duoc.append(tt)
                else:
                    chan += 1
            except Exception:                            # noqa: BLE001
                # Xét hỏng thì GIỮ tờ ấy: bỏ nó đi là lặng lẽ thu hẹp phép
                # đo vì một lỗi ở chỗ khác.
                duoc.append(tt)
        # TRẦN THEO BẰNG CHỨNG cho quãng tính lãi. Đọc từ sổ cái, cửa sổ
        # gần đây: vị thế vừa xoay THẬT SỰ sống được bao lâu trước lần
        # xoay kế. Đo làn thật 30/08: trung vị 0,008 giờ, trong khi lời
        # hứa tính trên 160 giờ. Xem docstring `do_xoay_cho`.
        #
        # Hỏng thì KHÔNG kẹp, chứ không kẹp bằng 0: một lỗi đọc sổ mà làm
        # đứng hẳn cơ chế xoay chỗ là để một chuyện của lớp lưu trữ quyết
        # thay cho một chuyện của danh mục.
        try:
            gsong = ((self.so_cai.xoay_cho_hua_va_thuc().get("ganDay") or {})
                     .get("gioGiuTrungVi"))
        except Exception:                                # noqa: BLE001
            gsong = None
        lat = do_xoay_cho(self.soViThe, duoc, gio,
                          bienAnToan=float(self.c.get("bienXoayCho") or 1.5),
                          gioSongTrungVi=gsong)
        lat.soDichBiChan = chan
        if not self.c.get("tuXoayCho"):
            return lat
        # CÒN GHẾ TRỐNG thì không đuổi ai. Tiền đề của cả cơ chế này là
        # «chỗ ngồi CÓ HẠN, và ai ngồi mới là câu hỏi» — còn chỗ thì câu
        # hỏi ấy không đặt ra: cơ hội tốt hơn cứ ngồi vào ghế trống.
        #
        # Đã cắn thật 29/08, ngay lượt đầu chạy với vốn một triệu và trần
        # 120 chỗ: máy cấp 6 vị thế rồi ĐÓNG 8 trong CÙNG một vòng, và
        # vòng sau lại cấp lại đúng những cái vừa đóng. Mỗi vòng một lần
        # phí vào + phí ra trên 25.000 USD, cho một danh mục không đổi.
        # Cửa chống trùng từng che lỗi này; gỡ nó ra thì nó lộ ngay.
        tran = int(self.phan_bo.c.get("toiDaSoViThe") or 0)
        n = len(self.danh_muc.viThe)
        if tran and n < tran:
            # Luật này dựa trên một LỜI HỨA — «Phân Bổ sẽ lấp chỗ trống» —
            # và lời hứa ấy kiểm chứng được. Đếm số vòng liên tiếp còn ghế
            # mà số vị thế KHÔNG tăng: đó chính là số vòng lời hứa không
            # được giữ. Trên máy sống 30/08 nó đang sai vì cơ hội tốt hơn
            # nằm trong một họ đã chạm trần `tranMotTy`, nên ghế trống
            # không giúp gì cho chúng.
            #
            # ĐẾM, không tự đổi hành vi: đóng một vị thế mà Phân Bổ không
            # mở lại được là đẩy vốn về tiền mặt ăn 0%, tệ hơn giữ nguyên.
            self._vongGheTrongKhongLap = (
                self._vongGheTrongKhongLap + 1
                if n <= self._soViTheVongTruoc else 0)
            self._soViTheVongTruoc = n
            lat.viConGhe = True
            lat.soVongGheTrongKhongLap = self._vongGheTrongKhongLap
            k = self._vongGheTrongKhongLap
            lat.vi = (f"còn {tran - n} ghế trống — KHÔNG đuổi ai. Cơ hội tốt "
                      f"hơn cứ ngồi vào chỗ trống, và Phân Bổ làm việc ấy ở "
                      f"bước 4. ({lat.soXoayDuoc} chỗ sẽ đáng đổi khi hết "
                      f"ghế.)")
            # Câu này GHI ĐÈ câu của `do_xoay_cho`, nên nó phải mang theo
            # cái mà câu kia định nói. Đo làn thật 30/08 ngay sau khi nối
            # trần bằng chứng: «0 chỗ sẽ đáng đổi khi hết ghế» — đúng,
            # nhưng lý do là 56 chỗ vừa bị trần chặn, và câu bị ghi đè đã
            # nuốt mất chỗ ấy. Một con số 0 không kèm lý do đọc thành
            # «chợ hôm nay không có gì».
            if lat.soBiChanBoiBangChung and lat.gioSongTrungVi is not None:
                lat.vi += (
                    f" Trong đó {lat.soBiChanBoiBangChung} chỗ bị TRẦN BẰNG "
                    f"CHỨNG chặn ({lat.gioSongTrungVi:.3f}h): công thức cũ "
                    f"sẽ nhận cả, và sẽ hứa {lat.loiRongBiChanUsd:+.2f} USD "
                    f"trên một quãng mà sổ nói vị thế không sống tới.")
            if k >= VONG_GHE_TRONG_DANG_NGO:
                lat.vi += (
                    f" ⚠ Nhưng đã {k} vòng LIÊN TIẾP còn ghế mà số vị thế "
                    f"không tăng — lời hứa «Phân Bổ sẽ lấp chỗ» đang KHÔNG "
                    f"được giữ. Xem phễu: cơ hội tốt hơn có đang kẹt ở một "
                    f"trần nào không. Máy KHÔNG tự đuổi ai vì chuyện này: "
                    f"đóng một vị thế mà Phân Bổ không mở lại được là đẩy "
                    f"vốn về tiền mặt ăn 0%.")
            return lat
        self._vongGheTrongKhongLap = 0
        self._soViTheVongTruoc = n
        for x in lat.xoay:
            so = self.soViThe.get(x.maCu)
            if so is None:
                continue
            laiLo = so.thuCongDonUsd - so.phiCongDonUsd
            daGiu = so.daGiuGio(gio)
            if not self.danh_muc.dong(x.maCu, 0.0):
                continue
            self.so_dang_ky.chuyen(
                x.maCu, "DA_DONG",
                f"xoay-cho: nhường chỗ cho {x.taiSanMoi} "
                f"({x.aprCu:.2f}% → {x.aprMoi:.2f}%/năm, lợi ròng "
                f"{x.loiRongUsd:+.4f} USD đã trừ phí)"[:400])
            self.so_cai.ghi(ButToan(
                "DONG_VI_THE", f"xoay chỗ · {x.taiSanCu} → {x.taiSanMoi}",
                0.0, so.chienLuoc, x.maCu,
                {"laiLoUsd": laiLo, "thuUsd": so.thuCongDonUsd,
                 "phiUsd": so.phiCongDonUsd, "daGiuGio": daGiu,
                 "duDoanBpsGio": _bps_gio_du_doan(so.toTrinh),
                 "thucBpsGio": _bps_gio_thuc(laiLo, so.vonUsd, daGiu),
                 # Tài sản đi và tài sản đến là TRƯỜNG, không phải chữ
                 # trong câu lý do. Muốn biết có đang xoay vòng quanh
                 # cùng một cặp hay không thì phải đếm được cặp ấy, mà
                 # tách chuỗi "xoay chỗ · A → B" là dựng một phép phân
                 # tích trên câu văn — đúng cái lỗi «mã chứ không phải
                 # câu» đã sửa ở Sổ Đăng Ký.
                 "xoayCho": True, "aprCu": x.aprCu, "aprMoi": x.aprMoi,
                 "taiSanCu": x.taiSanCu, "taiSanMoi": x.taiSanMoi,
                 "chienLuocMoi": x.chienLuocMoi,
                 # Lời hứa được TÍNH TRÊN chừng này giờ. Không ghi nó
                 # xuống thì sau này không đối chiếu được lời hứa với
                 # số giờ vị thế mới THẬT SỰ sống.
                 "gioChungHua": x.gioChung,
                 "loiRongUocUsd": x.loiRongUsd}))
            self._xoa_dau_van(so.toTrinh)
            self.soViThe.pop(x.maCu, None)
            lat.soDaDong += 1
        return lat

    def _luu_danh_muc(self) -> None:
        """Ghi danh mục sau MỖI vòng. Hỏng thì khai ra, đừng giết vòng."""
        try:
            luu_danh_muc(self.duongLuu, self.danh_muc, self.soViThe,
                         self.duongNav, self.soVonGio, self.napThemUsd,
                         self.tienDaGhiUsd)
            self.loiLuu = ""
        except OSError as e:                              # noqa: BLE001
            self.loiLuu = f"{type(e).__name__}: {e}"

    # ── CỬA DUY NHẤT cho mọi đồng tiền ────────────────────────────────────
    def _ghi_tien(self, soTienUsd: float, loai: str, lyDo: str,
                  chienLuoc=None, ma=None, chiTiet=None) -> None:
        """Dịch tiền mặt VÀ ghi sổ cái, trong một lời gọi.

        Trước hàm này, hai việc ấy là hai dòng cạnh nhau ở ba chỗ. Không gì
        buộc chúng đi cùng nhau, nên một dòng thiếu là tiền dịch mà sổ
        không biết — hoặc sổ ghi mà tiền không dịch. Cả hai đều im lặng, và
        cả hai đều làm `laiLoDaThucHienUsd` với sổ cái nói hai chuyện khác
        nhau mà không ai đối chiếu.

        Ràng buộc ấy nay là CẤU TRÚC chứ không phải phép canh: muốn dịch
        tiền thì phải đi qua đây, và đi qua đây thì sổ cái luôn có dòng.
        `scripts/selftest.py` canh bằng AST rằng `ghi_dong_tien()` chỉ có
        ĐÚNG MỘT chỗ gọi trong cả `thi_bac_ty/`.

        `soTienUsd` dương là tiền VÀO, âm là tiền RA — cùng quy ước với
        `DanhMuc.ghi_dong_tien()`, và bút toán mang đúng dấu ấy để sổ cộng
        lại ra đúng dòng tiền ròng.
        """
        if not soTienUsd:
            return
        self.danh_muc.ghi_dong_tien(soTienUsd)
        self.tienDaGhiUsd += soTienUsd
        self.so_cai.ghi(ButToan(loai, lyDo, soTienUsd, chienLuoc, ma,
                                dict(chiTiet or {})))

    def lech_tien(self) -> dict:
        """Sổ tiền của Trung Ương có khớp Danh Mục không.

        Hai con số phải bằng nhau tuyệt đối: `tienDaGhiUsd` là tổng mọi
        đồng ĐI QUA `_ghi_tien`, còn `laiLoDaThucHienUsd` là tổng Danh Mục
        đã cộng. Lệch nghĩa là có đường thứ hai dịch tiền — và đường thứ
        hai ấy không ghi sổ.

        `dong()` cũng cộng vào `laiLoDaThucHienUsd`, nhưng Trung Ương luôn
        truyền `0.0` cho nó: mọi dòng tiền đã được ghi lúc phát sinh, cộng
        lại lần nữa lúc đóng là đếm hai lần.
        """
        a = float(self.tienDaGhiUsd)
        b = float(self.danh_muc.laiLoDaThucHienUsd)
        return {"tienDaGhiUsd": a, "laiLoDanhMucUsd": b, "lechUsd": b - a,
                "khop": abs(b - a) < 1e-9,
                "vi": ("sổ tiền Trung Ương khớp Danh Mục"
                       if abs(b - a) < 1e-9 else
                       f"LỆCH {b - a:+.10f} USD — có đường dịch tiền KHÔNG "
                       f"đi qua `_ghi_tien`, nên sổ cái thiếu mất nó")}

    # ── kế toán vị thế đang mở ────────────────────────────────────────────
    def _ke_toan_vi_the(self) -> LatCatKeToan:
        """Mỗi vòng: hỏi ty "vị thế này thu/mất bao nhiêu", rồi đóng cái
        đã hết hạn giữ.

        Đây là nửa vòng đời trước 28/08/2026 không tồn tại. Xem
        `thi_bac_ty/ke_toan.py` để biết vì sao nó không được nằm ở Trung
        Ương và vì sao ty trả `None` phải được ĐẾM chứ không ngầm là 0.
        """
        import time as _time
        from .ke_toan import LatCatKeToan as _L

        now = _time.time()
        l = _L()
        # Đẩy mốc TRƯỚC lối thoát sớm: vòng không có vị thế nào vẫn là một
        # vòng nằm trong cửa sổ đo. Bỏ nó là làm mẫu số nhỏ lại đúng bằng
        # những quãng cỗ máy không rót được đồng nào.
        self.soVonGio.nhip(now)
        if not self.soViThe:
            return l

        for ma in list(self.soViThe.keys()):
            so = self.soViThe.get(ma)
            if so is None:
                continue
            chan = self.danh_muc.viThe.get(ma)
            if chan is None:
                # Danh mục không giữ nữa mà sổ còn — đóng gấp đã dọn bên
                # kia. Bỏ khỏi sổ chứ đừng kế toán cho một thứ không còn.
                self.soViThe.pop(ma, None)
                continue

            l.soViThe += 1
            # Cộng vốn-giờ TRƯỚC khi hỏi ty: khoảng thời gian này vốn ĐÃ
            # nằm trong vị thế, bất kể ty có kế toán nổi hay không. Cộng
            # sau nhánh `kq is None` là bỏ mất mẫu số của đúng những vị
            # thế mù — và tỉ suất sẽ đẹp lên nhờ giấu bớt mẫu số.
            self.soVonGio.cong(abs(so.vonUsd), so.keToanLucGiay, now,
                               ty=so.chienLuoc)
            ty = self.ty.get(so.chienLuoc)
            kq = None
            if ty is not None:
                try:
                    kq = ty.ke_toan(list(chan), dict(so.toTrinh),
                                    so.keToanLucGiay, now)
                except Exception as e:                    # noqa: BLE001
                    l.loi.append(f"{ma}: ke_toan ném {type(e).__name__}: {e}")
                    kq = None

            if kq is None:
                so.coKeToan = False
                l.soKhongCoKeToan += 1
                l.vonKhongDuocKeToanUsd += abs(so.vonUsd)
            else:
                so.coKeToan = True
                # MỐC ĐẦU cửa sổ, giữ TRƯỚC khi ghi đè. Dòng dưới đẩy
                # `keToanLucGiay` lên `now`, nên mọi chỗ sau đó đọc nó sẽ
                # thấy đầu cửa sổ TRÙNG cuối cửa sổ.
                #
                # Đã cắn im lặng: bút toán FUNDING ghi
                # `{"tuGiay": …, "denGiay": …}` với hai con số BẰNG NHAU —
                # đo trên sổ thật 30/08 thì 400/400 dòng gần nhất đều thế.
                # Sổ nói «khoản thu này kiếm được trong không giây», nên
                # không ai dựng lại được tỉ suất từ nó. Cùng lớp với lỗi
                # `nguonTsMs` của băng: ghi một con số đã dẫn thay cho
                # nguyên liệu là ghi một cuốn sổ không tua lại được.
                tu0 = so.keToanLucGiay
                so.keToanLucGiay = now
                so.soVongKeToan += 1
                if not getattr(kq, "doDuoc", True):
                    so.soVongKhongDoDuoc += 1
                    l.soVongMu += 1
                else:
                    l.soKeToanDuoc += 1
                    thu = float(getattr(kq, "thuUsd", 0.0) or 0.0)
                    phi = float(getattr(kq, "phiUsd", 0.0) or 0.0)
                    # SOÁT TRẦN, không sửa số. Ty là người biết việc của
                    # ty, nên Trung Ương KHÔNG cắt con số ấy — cắt là bịa
                    # ra một con số thứ ba mà không ai đo. Nhưng nó ĐẾM và
                    # KHAI, vì lớp lỗi ở đây in ra tiền: một ty quên chia
                    # cho 8.760 làm NAV phồng lên, và `lechTien` vẫn khớp
                    # vì sổ ghi đúng con số bịa ấy.
                    tran = _tran_thu_mot_vong(so.toTrinh, so.vonUsd,
                                              tu0, now)
                    if tran is not None and thu > tran:
                        l.soThuVuotTran += 1
                        l.thuVuotTran.append(
                            {"ma": ma, "chienLuoc": so.chienLuoc,
                             "thuUsd": thu, "tranUsd": tran,
                             "lanVuot": (thu / tran) if tran > 0 else None})
                    self.soVonGio.thuRongUsd += thu - phi
                    self.soVonGio.cong_thu(so.chienLuoc, thu - phi)
                    if thu:
                        so.thuCongDonUsd += thu
                        l.thuUsd += thu
                        self._ghi_tien(
                            thu, "FUNDING",
                            (getattr(kq, "vi", "") or
                             f"thu theo thời gian · {so.chienLuoc}"),
                            so.chienLuoc, ma,
                            {"tuGiay": tu0, "denGiay": now})
                    if phi:
                        so.phiCongDonUsd += phi
                        l.phiUsd += phi
                        # Phí TRONG KỲ cũng phải mang cửa sổ, cùng lý do
                        # khoản thu: không có nó thì nửa dòng tiền của một
                        # vị thế dựng lại được theo thời gian, nửa kia thì
                        # không — và một cuốn sổ tua lại được một nửa là
                        # một cuốn sổ không tua lại được.
                        self._ghi_tien(
                            -phi, "PHI",
                            (getattr(kq, "vi", "") or
                             f"phí trong kỳ · {so.chienLuoc}"),
                            so.chienLuoc, ma,
                            {"tuGiay": tu0, "denGiay": now})

            # ── đóng: hết hạn giữ, hoặc ty đòi đóng ──────────────────────
            lyDo = ""
            if kq is not None and getattr(kq, "dongLai", False):
                lyDo = getattr(kq, "lyDoDong", "") or "ty yêu cầu đóng sớm"
            elif so.giuGio > 0 and so.daGiuGio(now) >= so.giuGio:
                lyDo = (f"hết hạn giữ: {so.daGiuGio(now):.2f}h "
                        f"≥ {so.giuGio:.2f}h")
            if not lyDo:
                continue

            laiLo = so.thuCongDonUsd - so.phiCongDonUsd
            if not self.danh_muc.dong(ma, 0.0):
                l.loi.append(f"{ma}: danh mục từ chối đóng")
                continue
            self.so_dang_ky.chuyen(ma, "DA_DONG", lyDo[:400])
            # DỰ ĐOÁN vs THỰC NHẬN, ghi ngay lúc đóng.
            #
            # Ty chênh funding có băng nên hậu kiểm được bằng cách chạy lại.
            # Tám ty còn lại KHÔNG có băng — nhưng chúng không cần: tờ trình
            # lúc mở đã HỨA `netUocBps` trong `giuGio` giờ, và sổ vị thế lúc
            # đóng biết đã thu thật bao nhiêu trong bao lâu. Hai con số ấy
            # đủ để hỏi câu quan trọng nhất: **lời hứa có đúng không.**
            #
            # Quy về bps MỖI GIỜ ở cả hai vế. So bps trần thì một vị thế
            # đóng sớm luôn "thua" lời hứa của cả cửa sổ, và cái thua ấy chỉ
            # nói nó đóng sớm chứ không nói nó dở.
            gio = so.daGiuGio(now)
            duDoan = _bps_gio_du_doan(so.toTrinh)
            thuc = _bps_gio_thuc(laiLo, so.vonUsd, gio)
            self.so_cai.ghi(ButToan(
                "DONG_VI_THE", f"đóng · {lyDo}", 0.0, so.chienLuoc, ma,
                {"laiLoUsd": laiLo, "thuUsd": so.thuCongDonUsd,
                 "phiUsd": so.phiCongDonUsd,
                 "daGiuGio": gio,
                 "duDoanBpsGio": duDoan, "thucBpsGio": thuc,
                 "soVongKeToan": so.soVongKeToan,
                 "coKeToan": so.coKeToan}))
            self._xoa_dau_van(so.toTrinh)
            self.soViThe.pop(ma, None)
            l.daDong.append({"ma": ma, "chienLuoc": so.chienLuoc,
                             "laiLoUsd": laiLo, "lyDo": lyDo})
        return l

    def _mo_so_vi_the(self, tt, vonUsd: float) -> None:
        """Ghi một vị thế vừa mở vào sổ, và THU PHÍ VÀO ngay lúc này.

        Phí trước, thu nhập sau — cỗ máy nào cũng dễ trông có lãi khi phí
        được hoãn tới cuối. Hệ quả cố ý: mở rồi đóng ngay là hiện ra một
        khoản LỖ đúng bằng phí, và đó là sự thật.
        """
        import time as _time
        now = _time.time()
        d = tt.tom_tat() if hasattr(tt, "tom_tat") else dict(tt)
        self.soViThe[tt.ma] = SoViThe(
            ma=tt.ma, chienLuoc=tt.chienLuoc, toTrinh=d, vonUsd=float(vonUsd),
            moLucGiay=now, keToanLucGiay=now)
        so = self.soViThe[tt.ma]
        phi = phi_vao_usd(d, vonUsd)
        if phi > 0:
            so.phiCongDonUsd += phi
            self._ghi_tien(
                -phi, "PHI",
                f"phí vào lệnh · {d.get('phiUocBps')} bps trên "
                f"{vonUsd:.2f} USD", tt.chienLuoc, tt.ma,
                {"phiUocBps": d.get("phiUocBps"), "vonUsd": vonUsd})
        elif phi_vao_thieu(d):
            # Tờ trình không khai phí thì vị thế vào sổ mà không mất đồng
            # nào — trông có lãi hơn sự thật. Ghi ra để đếm được.
            self.so_cai.ghi(ButToan(
                "PHI", "tờ trình KHÔNG khai `phiUocBps` — vị thế này vào "
                       "sổ mà không bị trừ phí vào lệnh nào",
                0.0, tt.chienLuoc, tt.ma, {"phiThieu": True}))

    def _don_dinh_ky(self) -> None:
        ngay = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d")
        if ngay == self._ngayDon:
            return
        self._ngayDon = ngay
        self.so_dang_ky.don_cu(int(self.c["giuNgaySoDangKy"]))
        # Dấu vết cũ hơn hai nhịp thì không còn chặn gì nữa, chỉ tốn chỗ.
        han = _monotonic() - float(self.c["nhipGhiNhanGiay"]) * 2.0
        self._dauVet = {k: v for k, v in self._dauVet.items() if v > han}

    def _xoa_dau_van(self, toTrinh: dict) -> None:
        """Xoá dấu vân tay của một cơ hội vừa ĐÓNG.

        Cửa chống trùng nói rõ giả định của nó: «nó đang có một tờ trình
        SỐNG trong sổ rồi; cấp vốn lần nữa là cấp hai lần cho một cơ hội».
        Đúng — chừng nào tờ trình còn sống. Vị thế đóng rồi thì giả định
        ấy sai, mà cái dấu vẫn nằm đó chặn suốt `nhipGhiNhanGiay` (một giờ).

        Đã cắn thật 29/08, ngay lượt đầu bật xoay chỗ: máy đóng 8 vị thế
        lãi thấp đúng như thiết kế, rồi **không rót lại được cái nào** —
        23 tờ trình, 23 lần BỎ TRÙNG, và 998.000 USD nằm không. Không lỗi
        nào phát ra; cỗ máy chỉ đơn giản là ngồi im.

        Đúng lớp hỏng «một giả định viết trong chú thích thôi đúng mà chú
        thích vẫn còn đó»: cửa chống trùng không sai, nó chỉ không biết có
        một đường đóng vị thế mới.
        """
        van = _dau_van_tu_dict(toTrinh)
        if van:
            self._dauVet.pop(van, None)

    # ── bước 6–7: CHẨN ĐOÁN → XÉT LẠI THAM SỐ ────────────────────────────
    def nap_von(self, soTienUsd: float, nguoi: str, vi: str = "") -> dict:
        """CHỦ bỏ thêm vốn vào (dương) hay rút ra (âm). **ĐÒI TÊN NGƯỜI.**

        ## Vì sao không phải là sửa một con số trong config

        Sửa `vonBanDauUsd` từ 10.000 lên 1.000.000 mà tiền mặt vẫn 4.000 thì
        NAV/vốn gốc ra 1% — **cầu dao đọc thành sụt vốn 99% và ngắt ngay**.
        Còn nếu vá chỗ ấy bằng cách cộng luôn tiền mặt, thì đường NAV nhảy
        từ 10.000 lên 1.000.000 và mọi phép đo lợi suất đọc cú nhảy ấy
        thành **lãi gấp một trăm lần**.

        Nạp vốn là một SỰ KIỆN, không phải một tham số. Nó phải:

            vào tiền mặt          để có mà rót
            nâng vốn gốc          để sụt vốn tính đúng thang
            vào SỔ CÁI            để sau này còn lần lại được
            đánh dấu ĐƯỜNG NAV    để lợi suất không tính nó thành lãi

        Thiếu bước cuối là lời nói dối lớn nhất một cỗ máy vốn có thể nói.

        Đòi tên người vì cùng một bất đối xứng với `ap_dung` và cầu dao: máy
        được phép đề nghị, người quyết định bỏ tiền vào.
        """
        nguoi = (nguoi or "").strip()
        if not nguoi:
            raise ValueError("nạp vốn phải có TÊN NGƯỜI — máy không tự nạp")
        x = float(soTienUsd)
        if x == 0.0:
            raise ValueError("nạp 0 đồng không phải một sự kiện")
        if self.danh_muc.tienMatUsd + x < 0.0:
            raise ValueError(
                f"rút {abs(x):,.2f} nhưng tiền mặt chỉ {self.danh_muc.tienMatUsd:,.2f}"
                f" — vốn đang nằm trong vị thế, phải đóng trước")
        self.danh_muc.tienMatUsd += x
        self.danh_muc.vonBanDauUsd += x
        self.napThemUsd += x
        # Cộng dồn để `mot_vong` gắn vào ĐIỂM NAV kế tiếp. Không ghi thẳng
        # vào đường NAV ở đây: điểm NAV chỉ sinh ra ở một chỗ duy nhất, và
        # thêm một cửa thứ hai là mở đường cho hai cửa lệch nhau.
        self._dongVonChoGhi += x
        self.so_cai.ghi(ButToan(
            "NAP_VON", vi or f"{nguoi} {'nạp' if x > 0 else 'rút'} vốn",
            x, "", "", {"nguoi": nguoi, "vonGocMoiUsd":
                        self.danh_muc.vonBanDauUsd,
                        "napThemUsd": self.napThemUsd}))
        return {"soTienUsd": x, "nguoi": nguoi,
                "tienMatUsd": self.danh_muc.tienMatUsd,
                "vonGocUsd": self.danh_muc.vonBanDauUsd,
                "napThemUsd": self.napThemUsd,
                "vi": (f"{nguoi} {'nạp' if x > 0 else 'rút'} "
                       f"{abs(x):,.2f} USD ẢO. Vốn gốc nay "
                       f"{self.danh_muc.vonBanDauUsd:,.2f}. Đường NAV đánh "
                       f"dấu dòng vốn này, nên lợi suất KHÔNG tính nó là "
                       f"lãi.")}

    def duong_suc_chua(self) -> dict:
        """Lợi suất ở từng mức vốn, dựng từ cơ hội của ĐÚNG vòng này."""
        from .duong_suc_chua import do_duong_suc_chua
        return do_duong_suc_chua(self.toTrinhVongNay).tom_tat()

    def hua_theo_ty(self) -> dict:
        """Lời hứa BÌNH QUÂN THEO VỐN của mọi vị thế đang mở, theo ty.

        Vì sao phải gộp Ở ĐÂY chứ không để bên đọc tự gộp từ `soViThe`:
        ảnh chụp CẮT danh sách vị thế ở 40 cái, để payload khỏi phình.
        Máy sống 30/08 giữ 101 vị thế, tức bên đọc chỉ thấy 40 — mà lợi
        suất THỰC thì tính trên cả 101.

        Đem một lời hứa lấy từ 40 cái đi so với thực nhận của 101 cái là
        so hai tập khác nhau, đúng cái bẫy mà chính triệu chứng
        `hua-qua-dang-mo` sinh ra để tránh. Tệ hơn: 40 cái ấy chọn theo
        thứ tự từ điển, tức là một mẫu thiên lệch mà không ai khai.

        `soKhongKhai` đếm vị thế không khai `netUocBps` — chúng ra khỏi
        CẢ tử số lẫn mẫu số, chứ không bị đọc thành «hứa 0%».
        """
        ra: dict = {}
        for so in self.soViThe.values():
            t = so.toTrinh if isinstance(so.toTrinh, dict) else {}
            o = ra.setdefault(so.chienLuoc or "?",
                              {"vonUsd": 0.0, "_x": 0.0, "soViThe": 0,
                               "soKhongKhai": 0})
            o["soViThe"] += 1
            net, giu = t.get("netUocBps"), t.get("giuGio")
            von = abs(float(so.vonUsd or 0.0))
            if net is None or not giu or von <= 0:
                o["soKhongKhai"] += 1
                continue
            o["vonUsd"] += von
            o["_x"] += von * (float(net) / 10_000.0
                              * (24.0 / float(giu)) * 365.0 * 100.0)
        for o in ra.values():
            o["aprHuaPhanTram"] = (o["_x"] / o["vonUsd"]
                                   if o["vonUsd"] > 0 else None)
            o.pop("_x", None)
        return ra

    def duong_khoa_von(self) -> dict:
        """Trần khoá vốn đang chặn mất bao nhiêu lợi suất — ĐO, không đề xuất.

        Đo trên TIỀN MẶT đang có, không trên NAV: câu hỏi là «số tiền chưa
        rót ấy có thể đi đâu», và phần đã rót thì đã đi rồi.
        """
        from .duong_khoa_von import do_duong_khoa_von
        tran = self.rui_ro_tong.c.get("khoaVonToiDaGio")
        return do_duong_khoa_von(
            self.toTrinhVongNay, float(self.danh_muc.tienMatUsd),
            None if tran is None else float(tran)).tom_tat()

    def xoay_cho(self):
        """Chỗ nào đang ngồi mà đáng nhường cho cơ hội tốt hơn — ĐO thôi.

        Dùng tờ trình của CHÍNH vòng này (`toTrinhVongNay`), không dùng sổ
        đăng ký: câu hỏi là «ngay bây giờ có gì tốt hơn đang gõ cửa», và
        một tờ trình từ ba giờ trước không còn là cơ hội đang gõ cửa nữa.
        """
        from .xoay_cho import do_xoay_cho
        return do_xoay_cho(self.soViThe, self.toTrinhVongNay, _gio_he())

    def lech_cau_hinh(self) -> list[dict]:
        """`config.json` xin một đằng, máy chạy một nẻo — kể ra chỗ nào.

        Kho bản tham số THẮNG `config.json`, và đó là cố ý: không thế thì
        mỗi lần khởi động lại sẽ âm thầm quay về mặc định, xoá sạch mọi bản
        đã có người ký duyệt. Nhưng cái đúng ấy sinh ra một cái im lặng —
        sửa `phanBo.toiDaSoViThe` trong config, khởi động lại, và **không
        có gì xảy ra, cũng không có gì báo**.

        Đúng lớp hỏng mà `bac/config.py` đã ghi ở `MAC_DINH`: «sửa mỗi chỗ
        này thì KHÔNG có tác dụng gì trên máy đã có config.json». Ở đó lời
        cảnh báo nằm trong chú thích; ở đây nó phải ĐO được, vì người sửa
        config không đọc mã trước khi sửa.

        Không tự áp: đường đổi tham số vẫn là `hoc()` → `ap_dung(nguoi)`.
        Việc của hàm này chỉ là không để ai tưởng mình đã đổi được.
        """
        dang = self.tham_so()
        ra = []
        for tang in ("ruiRoTong", "phanBo"):
            xin = self.c.get(tang) or {}
            for nut, gt in xin.items():
                co = (dang.get(tang) or {}).get(nut)
                if co != gt:
                    ra.append({"nut": f"{tang}.{nut}", "xin": gt,
                               "dangChay": co})
        return ra

    def tham_so(self) -> dict:
        """Tham số ĐANG CÓ HIỆU LỰC — đọc từ chính các tầng, không từ `self.c`.

        `self.c` chỉ chứa phần người dùng ghi đè; giá trị thật là bản đã gộp
        với mặc định nằm trong từng tầng. Chẩn đoán mà đọc `self.c` thì sẽ
        thấy `{}` và kết luận là không có núm nào — sai theo cách im lặng.
        """
        return {"ruiRoTong": dict(self.rui_ro_tong.c),
                "phanBo": dict(self.phan_bo.c),
                "nguongCauDao": dict(self.c["nguongCauDao"])}

    def hoc(self, ghiSo: bool = True) -> dict:
        """Chẩn cả bộ máy, và ĐỀ XUẤT vặn — **không tự vặn**.

        Vì sao không tự vặn, dù tầng ty thì tự vặn được: đổi tham số phân bổ
        là đổi cách chia tiền giữa các ty, mà chuyện đó **không chạy lại
        được**. Chạy lại một quyết định phân bổ đòi biết những cơ hội đã
        KHÔNG được cấp diễn biến ra sao — chúng không được mở nên không có
        kết cục. Không A/B được thì không tự nhận được. Người duyệt.
        """
        anh = self.anh_chup()
        trieu = chan_doan_he(anh)
        goc = self.tham_so()
        dx = de_xuat(trieu, goc)

        # ĐO đề xuất, đừng để nó trần. Chạy lại không nói được lãi lỗ, nhưng
        # nó nói được HÌNH DẠNG phân bổ đổi ra sao — và quan trọng hơn: nó
        # bắt được lúc một đề xuất chỉ "tốt hơn" nhờ ôm rủi ro đậm hơn.
        do = None
        duyet = None
        if dx:
            tt, hong = thu_hoach(self.so_dang_ky)
            moi = _dat_nut(goc, dx[0].nut, dx[0].den)
            do = doi_chieu(tt, goc, moi, self.danh_muc.vonBanDauUsd, hong)
            # Cổng Duyệt đứng SAU phép đo và TRƯỚC mọi đường áp dụng.
            duyet = xet_duyet(dx[0], do).tom_tat()
            self._deXuatChoDuyet = (dx[0], do) if duyet["duDieuKien"] else None
        else:
            self._deXuatChoDuyet = None

        ra = {"luc": _bay_gio(), "vong": self.vong,
              "trieuChung": [t.tom_tat() for t in trieu],
              "deXuat": [d.tom_tat() for d in dx],
              "doDuoc": do,
              "congDuyet": duyet,
              "banHienHanh": (self.kho_tham_so.hien_hanh().so
                              if self.kho_tham_so.hien_hanh() else None),
              "tuVan": False,
              "loiNhac": "Đề xuất, KHÔNG tự áp dụng. Xem `hoc()` trong "
                         "trung_uong.py để biết vì sao."}
        if ghiSo:
            self._ghi_xet(ra)
        self.hocCuoi = ra
        return ra

    def _ghi_xet(self, ra: dict) -> None:
        try:
            with open(self._soXet, "a", encoding="utf-8", newline="\n") as f:
                f.write(json.dumps(ra, ensure_ascii=False) + "\n")
        except OSError:
            pass                 # mất một dòng nhật ký không được làm chết vòng

    # ── phễu đầy đủ ───────────────────────────────────────────────────────
    def pheu_day_du(self) -> dict:
        """Phễu từ CƠ HỘI THÔ tới vị thế, không phải từ tờ trình tới vị thế.

        `SoDangKy.pheu()` một mình bắt đầu ở chỗ đã có tờ trình — mà tờ trình
        chỉ ra đời sau khi cơ hội qua cổng ty. Nên nấc đầu và nấc hai của nó
        luôn bằng nhau, và tỉ lệ sống sót qua cổng ty vĩnh viễn là 100%.

        Một con số luôn đẹp là một con số không nói gì. Số cơ hội THẬT SỰ
        nhìn thấy nằm ở bộ đếm của từng ty, nên phải nối vào đây mới thành
        cái phễu mà `so_dang_ky.py` mô tả.
        """
        tho = sum(t.soCoHoi for t in self.ty.values())
        qua = sum(t.soQuaCongTy for t in self.ty.values())
        p = self.so_dang_ky.pheu()
        nac = [("coHoiTho", tho), ("quaCongTy", qua)] + [
            (t, int(p.get(t) or 0)) for t in
            ("DUYET_RUI_RO", "DA_CAP_VON", "DA_MO", "DA_DONG")]
        return {
            "theoHo": self._pheu_theo_ho(),
            "nac": [{"ten": k, "so": v,
                     # `None` chứ không phải 0: "chưa thấy cơ hội nào" khác
                     # hẳn "thấy rồi mà không cái nào qua".
                     "tiLe": (v / tho if tho else None)} for k, v in nac],
            "coHoiTho": tho, "quaCongTy": qua,
            "tuChoi": int(p.get("TU_CHOI") or 0),
            "hong": int(p.get("HONG") or 0),
            "soChuyenSai": self.so_dang_ky.soChuyenSai,
        }

    def von_ranh(self) -> dict:
        """Bao nhiêu vốn ĐƯỢC PHÉP làm việc mà đang không làm gì.

        MẪU SỐ ở đây là VỐN KHẢ DỤNG, không phải NAV. Dự trữ là một lựa
        chọn có chủ ý (`phanBo.tiLeDuTru`, đang 20%) — tính nó vào phần
        «nằm không» là buộc tội cỗ máy vì chính cái luật ta đặt ra cho
        nó. Còn phần ngoài dự trữ mà vẫn nằm im thì không ai chọn cả.

        Vì sao cần con số này. Chẩn đoán `tran-dat-sai-cho` canh
        `tiLeDungVon < 0,15` — tỉ lệ trên NAV. Làn thật 30/08 dùng vốn
        56%, nên nó im; mà 56% trên NAV là **70% của phần khả dụng**, và
        30% còn lại — **239.071 USD** — đang ăn 0%. Lợi suất trên vốn
        đang dùng là 4,30%/năm, quy về NAV còn **2,41%**. Gần một nửa
        lợi suất mất ở chỗ này, và không cảnh báo nào kêu.

        `loiSuatNeuLapDayPhanTram` là câu «nếu phần rảnh cũng chạy được
        như phần đang chạy thì NAV sinh lời bao nhiêu». Đó là một PHÉP
        ĐỐI CHIẾU, không phải một lời hứa: phần rảnh nằm im thường vì
        những cơ hội còn lại tệ hơn hoặc bị trần chặn, nên nó là TRẦN
        TRÊN của phần đang bỏ lỡ, không phải số sẽ thu được.
        """
        nav = float(self.danh_muc.navUsd)
        mat = float(self.danh_muc.tienMatUsd)
        ti_du_tru = float(self.phan_bo.c.get("tiLeDuTru") or 0.0)
        du_tru = nav * ti_du_tru
        kha_dung = nav * (1.0 - ti_du_tru)
        dang_dung = nav - mat
        ranh = max(0.0, mat - du_tru)

        # Lợi suất trên vốn ĐANG DÙNG, gia quyền theo VỐN-GIỜ. Không lấy
        # trung bình cộng các ty: một ty giữ 764 nghìn vốn-giờ và một ty
        # giữ 1.587 không nói cùng một tiếng.
        theo_ty = (self.soVonGio.tom_tat() or {}).get("theoTy") or {}
        tong_vg = 0.0
        tong_ls = 0.0
        mu = 0
        for o in theo_ty.values():
            vg = float(o.get("vonGioUsd") or 0.0)
            ls = o.get("loiSuatNamPhanTram")
            if ls is None:
                mu += 1
                continue
            tong_vg += vg
            tong_ls += vg * float(ls)
        # `None` chứ không phải 0: chưa có vốn-giờ nào thì ta chưa biết
        # lợi suất, khác hẳn biết nó bằng không.
        ls_dung = (tong_ls / tong_vg) if tong_vg > 0 else None
        ls_nav = (ls_dung * dang_dung / nav) if (ls_dung is not None
                                                 and nav > 0) else None
        ls_lap = (ls_dung * kha_dung / nav) if (ls_dung is not None
                                                and nav > 0) else None
        return {
            "navUsd": nav, "tienMatUsd": mat,
            "tiLeDuTru": ti_du_tru, "duTruUsd": du_tru,
            "khaDungUsd": kha_dung, "dangDungUsd": dang_dung,
            "ranhNgoaiDuTruUsd": ranh,
            "tiLeRanhTrenKhaDung": (ranh / kha_dung) if kha_dung > 0 else None,
            "loiSuatTrenVonDungPhanTram": ls_dung,
            "loiSuatQuyVeNavPhanTram": ls_nav,
            "loiSuatNeuLapDayPhanTram": ls_lap,
            "soTyChuaDoDuocLoiSuat": mu,
        }

    # ── chế độ vận hành từng ty ───────────────────────────────────────────
    def che_ty(self) -> list[dict]:
        """Chế độ của từng ty: QUAN_SAT · GIAY · THAT.

        Suy tất định từ NAV và ngưỡng kinh tế của ty. Không ai gõ tay, và
        máy KHÔNG được tự ép một ty lên chế độ cao hơn — luật của bản đồ:
        engine nào không đủ vốn tối thiểu thì chỉ được QUAN SÁT.
        """
        tran = float(self.rui_ro_tong.c.get("tranMotCoHoi") or 0.0)
        nav = self.danh_muc.navUsd
        # `moPhong` là True CỨNG ở bản này, nên THAT chưa với tới được —
        # đọc từ chính tầng thực thi chứ không từ một cờ cấu hình.
        co_ky = not getattr(self.thuc_thi, "moPhong", True)
        return [che_cua_ty(t, nav, tran, co_ky).tom_tat()
                for t in self.ty.values()]

    def hieu_nang(self) -> dict:
        """CAGR, sụt vốn tối đa, và chi phí hạ tầng — xem `hieu_nang.py`."""
        d = self.duongNav.do(self.danh_muc.vonBanDauUsd)
        d["haTang"] = von_hoa_ha_tang(float(self.c["chiPhiHaTangUsdThang"]))
        d["vonCanDeCoMotEngineChay"] = von_can_de_chay(
            list(self.ty.values()),
            float(self.rui_ro_tong.c.get("tranMotCoHoi") or 0.0))
        d["giayVaThat"] = doi_chieu_giay_that(self.so_cai)
        # HAI mẫu số, hai câu hỏi. `laiLoPhanTram` bên trên tính trên vốn
        # TỔNG — nó trả lời «cỗ máy đang làm ăn ra sao». Con số dưới đây
        # tính trên vốn ĐANG DÙNG — «chiến lược đang làm ăn ra sao». Máy
        # demo rót được 6.000 trên 100.000 vốn ảo, và hai câu ấy lệch nhau
        # gần hai mươi lần.
        d["vonDangDung"] = self.soVonGio.tom_tat()
        return d

    # ── §17 · áp dụng và quay lui, cả hai đều đòi TÊN NGƯỜI ──────────────
    def ap_dung(self, nguoi: str) -> dict:
        """Áp dụng đề xuất đã QUA CỔNG DUYỆT ở lượt `hoc()` gần nhất.

        Ba điều kiện, và không điều nào bỏ được:

          1. phải có một đề xuất đã qua cổng (`hoc()` chạy trước)
          2. phải có tên người — máy không tự ký
          3. bản mới ghi kèm CHÍNH phép đo đã biện minh cho nó

        Điều 3 là chỗ đáng giá nhất: ba tháng sau, câu hỏi "vì sao trần cảng
        là 0,45" trả lời được bằng một lệnh đọc sổ, không phải bằng trí nhớ.
        """
        if not (nguoi or "").strip():
            return {"xong": False,
                    "vi": "thiếu tên người — đổi cách chia tiền là hành động "
                          "có trách nhiệm, và sổ phải ghi được ai làm"}
        cho = getattr(self, "_deXuatChoDuyet", None)
        if cho is None:
            return {"xong": False,
                    "vi": "không có đề xuất nào đã qua Cổng Duyệt. Chạy "
                          "`hoc()` trước, và nhớ rằng phần lớn lượt học kết "
                          "thúc bằng 'không đề xuất gì' — đó là kết quả hợp lệ"}
        dx, do = cho
        moi = _dat_nut(self.tham_so(), dx.nut, dx.den)
        ban = self.kho_tham_so.dat(
            {"ruiRoTong": moi.get("ruiRoTong") or {},
             "phanBo": moi.get("phanBo") or {}},
            nguoi,
            f"{dx.nut}: {dx.tu:g} -> {dx.den:g} (vì triệu chứng «{dx.vi}»)",
            do)
        if ban is None:
            return {"xong": False, "vi": self.kho_tham_so.loiCuoi or "ghi hỏng"}

        # Dựng lại hai tầng từ bản mới. Không dựng lại thì bản đã ghi vào sổ
        # mà máy vẫn chạy tham số cũ — sổ nói một đằng, máy làm một nẻo.
        self.rui_ro_tong = RuiRoTong(ban.thamSo.get("ruiRoTong") or {})
        self.phan_bo = PhanBo(ban.thamSo.get("phanBo") or {})
        self._deXuatChoDuyet = None
        self.so_cai.ghi(ButToan(
            "DIEU_CHINH", f"tham số: bản #{ban.so} — {ban.vi}", 0.0, None,
            None, {"banThamSo": ban.so, "nguoi": nguoi}))
        return {"xong": True, "ban": ban.tom_tat()}

    def dat_tham_so(self, nguoi: str, duong: str, giaTri,
                    vi: str = "") -> dict:
        """Đổi THẲNG một núm, có TÊN NGƯỜI. Ghi thành một bản mới.

        `ap_dung()` chỉ áp được đề xuất mà chính máy vừa nghĩ ra. Nhưng có
        những lần người muốn đổi một thứ máy KHÔNG đề xuất — vì triệu chứng
        chưa đủ nặng, hoặc vì người biết một điều máy chưa đo được. Trần vị
        thế 12 là ví dụ: nó chặn ba trên bốn họ, mà lý do đặt ra nó («quá
        nhiều thì không theo dõi nổi») là lý do của thời chưa có kế toán tự
        động — máy không biết lý do ấy đã hết hiệu lực.

        Vẫn đi qua kho bản tham số, nên vẫn có số hiệu, vẫn `quay_lui`
        được, và vẫn ghi ai đổi + vì sao. Khác `ap_dung` đúng một chỗ:
        không kèm phép đo chạy lại, vì không có đề xuất nào để đo. Bản ghi
        nói thẳng điều đó thay vì giả vờ có bằng chứng.
        """
        if not (nguoi or "").strip():
            return {"xong": False,
                    "vi": "thiếu tên người — đổi cách chia tiền là hành động "
                          "có trách nhiệm"}
        if not (vi or "").strip():
            return {"xong": False,
                    "vi": "thiếu lý do — một bản không giải thích được thì "
                          "không kiểm toán được"}
        cu = _lay_nut(self.tham_so(), duong)
        if cu is None:
            return {"xong": False,
                    "vi": f"không có núm «{duong}» ở tầng phân bổ hay rủi ro "
                          f"tổng — gõ nhầm tên thì đổi trúng hư không"}
        moi = _dat_nut(self.tham_so(), duong, giaTri)
        ban = self.kho_tham_so.dat(
            {"ruiRoTong": moi.get("ruiRoTong") or {},
             "phanBo": moi.get("phanBo") or {}},
            nguoi,
            f"{duong}: {cu} -> {giaTri} — NGƯỜI đặt thẳng, KHÔNG qua phép "
            f"chạy lại. Lý do: {vi}")
        if ban is None:
            return {"xong": False, "vi": self.kho_tham_so.loiCuoi or "ghi hỏng"}
        self.rui_ro_tong = RuiRoTong(ban.thamSo.get("ruiRoTong") or {})
        self.phan_bo = PhanBo(ban.thamSo.get("phanBo") or {})
        self.so_cai.ghi(ButToan(
            "DIEU_CHINH", f"tham số: bản #{ban.so} — {ban.vi}", 0.0, None,
            None, {"banThamSo": ban.so, "nguoi": nguoi, "nut": duong,
                   "tu": cu, "den": giaTri, "quaChayLai": False}))
        return {"xong": True, "ban": ban.tom_tat(), "tu": cu, "den": giaTri}

    def quay_lui(self, veSo: int, nguoi: str, vi: str = "") -> dict:
        """Quay về nội dung bản `veSo`, bằng cách ghi một bản MỚI.

        Không xoá bản sai. Cùng luật với `so_cai.dao()`: một lịch sử sửa
        được thì không còn là lịch sử.
        """
        if not (nguoi or "").strip():
            return {"xong": False, "vi": "thiếu tên người"}
        ban = self.kho_tham_so.quay_lui(int(veSo), nguoi, vi)
        if ban is None:
            return {"xong": False, "vi": self.kho_tham_so.loiCuoi or "hỏng"}
        self.rui_ro_tong = RuiRoTong(ban.thamSo.get("ruiRoTong") or {})
        self.phan_bo = PhanBo(ban.thamSo.get("phanBo") or {})
        self._deXuatChoDuyet = None
        self.so_cai.ghi(ButToan(
            "DIEU_CHINH", f"tham số: bản #{ban.so} quay lui về #{veSo}", 0.0,
            None, None, {"banThamSo": ban.so, "quayLuiVe": int(veSo),
                         "nguoi": nguoi}))
        return {"xong": True, "ban": ban.tom_tat()}

    def _pheu_theo_ho(self) -> list[dict]:
        """Phễu tách theo HỌ, đúng bảng §22 của bản đồ.

        Tổng gộp nói được "cỗ máy có học không". Tách theo họ nói được thứ
        khác, và là thứ Người Phân Bổ Vốn cần: **họ nào đang nuôi được vốn**.
        Một họ phát hiện nhiều mà chưa bao giờ qua nổi Rủi Ro Tổng là một họ
        đang tiêu thời gian máy mà không sinh ra gì.

        Số cơ hội THÔ lấy từ bộ đếm của từng ty, không từ sổ đăng ký — sổ chỉ
        có tờ trình, mà tờ trình chỉ ra đời sau khi đã qua cổng ty.

        **Cả năm cột phải cùng MỘT cửa sổ thời gian, và cửa sổ ấy là TỪ LÚC
        BẬT MÁY.** Bộ đếm của ty nằm trong RAM nên nó không thể trả lời câu
        nào rộng hơn; sổ đăng ký thì nằm trên đĩa và trả lời cả đời máy.
        Ghép hai thứ ấy vào một hàng cho ra một cái phễu PHÌNH RA ở giữa:
        đo 30/08 trên máy sống, họ thanh-khoan hiện «thô 39.392 · qua cổng
        ty 8 · qua Rủi Ro Tổng 49» — 8 tờ trình đẻ ra 49 lần duyệt.

        Một phễu phình ra không chỉ khó coi. Nó chỉ sai chỗ nghẽn: người
        đọc thấy cổng ty lọc 39.392 xuống 8 và đi vặn cổng ty, trong khi
        con số 8 ấy nói về một quãng khác hẳn con số 49 bên cạnh. Và bảng
        lý do từ chối kéo theo cùng bệnh — nó hiện «đã đủ 12 vị thế» hàng
        chục lần trong khi trần đang là 120, vì đó là những lần từ chối
        của trước một lần nạp vốn.
        """
        tho: dict[str, int] = {}
        qua: dict[str, int] = {}
        for t in self.ty.values():
            h = getattr(t, "ho", "?") or "?"
            tho[h] = tho.get(h, 0) + t.soCoHoi
            qua[h] = qua.get(h, 0) + t.soQuaCongTy
        tu = self.lucKhoiDong
        try:
            with self.so_dang_ky._mo() as con:
                rr = {r[0]: r[1] for r in con.execute(
                    "SELECT ho, COUNT(DISTINCT ma) FROM to_trinh WHERE ma IN "
                    "(SELECT ma FROM chuyen_trang_thai WHERE den='DUYET_RUI_RO'"
                    " AND luc >= ?) GROUP BY ho", (tu,)).fetchall()}
                cv = {r[0]: r[1] for r in con.execute(
                    "SELECT ho, COUNT(DISTINCT ma) FROM to_trinh WHERE ma IN "
                    "(SELECT ma FROM chuyen_trang_thai WHERE den='DA_CAP_VON'"
                    " AND luc >= ?) GROUP BY ho", (tu,)).fetchall()}
        except Exception:                                # noqa: BLE001
            rr, cv = {}, {}
        von = self.danh_muc.phoi_nhiem_ty()
        von_ho: dict[str, float] = {}
        for t in self.ty.values():
            h = getattr(t, "ho", "?") or "?"
            von_ho[h] = von_ho.get(h, 0.0) + von.get(getattr(t, "ma", ""), 0.0)
        # VÌ SAO, không chỉ BAO NHIÊU. Một họ có 2115 cơ hội mà không được
        # đồng nào: cổng ty quá chặt và hết chỗ vì trần vị thế trông giống
        # hệt nhau nếu chỉ nhìn con số 0 — mà hai cái ấy sửa bằng hai việc
        # khác hẳn.
        ly = self.so_dang_ky.ly_do_tu_choi(tuLuc=tu)
        # Mẫu số cho bảng lý do. Không có nó thì «năm mã đứng đầu»
        # đọc như «đây là tất cả», và người đọc không biết năm dòng
        # ấy phủ 15 lần từ chối hay 140.
        tuChoi = self.so_dang_ky.so_tu_choi(tuLuc=tu)
        return [{"ho": h, "coHoiTho": tho.get(h, 0), "quaCongTy": qua.get(h, 0),
                 "quaRuiRoTong": int(rr.get(h, 0)),
                 "daCapVon": int(cv.get(h, 0)),
                 "vonDangGiuUsd": round(von_ho.get(h, 0.0), 2),
                 "soTuChoi": int(tuChoi.get(h, 0)),
                 "lyDoTuChoi": ly.get(h, [])}
                for h in sorted(tho)]

    # ── ảnh chụp ──────────────────────────────────────────────────────────
    def anh_chup(self) -> dict:
        return {
            "vong": self.vong,
            "ty": [t.tom_tat() for t in self.ty.values()],
            "thongChinh": self.thong_chinh.tom_tat(),
            "soDangKy": self.so_dang_ky.tom_tat(),
            "danhMuc": self.danh_muc.tom_tat(),
            "vonNgoai": [d.tom_tat() for d in self.docVonNgoai],
            "soNgoai": [n.tom_tat() for n in self.nhapSoNgoai],
            "ruiRoTong": self.rui_ro_tong.tom_tat(),
            "phanBo": self.phan_bo.tom_tat(),
            "cauDao": self.cau_dao.tom_tat(),
            "doiSoatViThe": self.doiSoatViThe.tom_tat(),
            "doiSoatKhoiDong": self.doiSoatKhoiDong.tom_tat(),
            "keToan": self.latCatKeToan.tom_tat(),
            "lechTien": self.lech_tien(),
            "luuDanhMuc": {**self.napLuu,
                           "loiGhi": getattr(self, "loiLuu", "")},
            # Lãi lỗ TÁCH KHOẢN. Con số gộp nói dối theo một cách khó
            # thấy: phí vào lệnh phần lớn do runtime bị khởi động lại chứ
            # không do quyết định của ty, mà gộp vào thì một chiến lược
            # đang lãi trông như đang lỗ. Xem `SoCai.lai_lo_tach_khoan`.
            "laiLoTachKhoan": self.so_cai.lai_lo_tach_khoan(),
            # CẮT ở 40 để payload khỏi phình — nên MỌI phép tính gộp
            # phải làm ở Trung Ương, không để bên đọc gộp từ danh sách
            # đã cắt. Xem `hua_theo_ty()`.
            "soViThe": [v.tom_tat(_gio_he()) for v in
                        list(self.soViThe.values())[:40]],
            "soViTheDayDu": len(self.soViThe),
            "huaTheoTy": self.hua_theo_ty(),
            "thucThi": self.thuc_thi.tom_tat(),
            "soCai": self.so_cai.tom_tat(),
            "pheuDayDu": self.pheu_day_du(),
            "toTrinh": [t.tom_tat() for t in self.toTrinhVongNay],
            "latCatVong": self.latCatCuoi.tom_tat() if self.latCatCuoi else None,
            "hoc": self.hocCuoi,
            "loiHoc": getattr(self, "loiHoc", ""),
            "thamSo": self.tham_so(),
            "hienPhap": _hien_phap(),
            "cheTy": self.che_ty(),
            "hieuNang": self.hieu_nang(),
            "banThamSo": self.kho_tham_so.tom_tat(),
            "lechCauHinh": self.lech_cau_hinh(),
            "vonDangDung": self.soVonGio.tom_tat(),
            "vonRanh": self.von_ranh(),
            # Hậu kiểm cho TÁM ty không có băng: lời hứa lúc mở vs thực
            # nhận lúc đóng. Ty duy nhất có băng thì hậu kiểm bằng chạy
            # lại, và nó nằm ở `trangThai.tienHoa`.
            "duDoanVaThuc": self.so_cai.du_doan_va_thuc(),
            # Chỗ ngồi có hạn, và ai ngồi mới là câu hỏi. Xem `xoay_cho.py`.
            # ĐO thôi — đường thực hiện chưa nối.
            # Lát cắt của CHÍNH vòng vừa chạy, không đo lại: đo lại ở đây
            # là chạy phép tính hai lần trên hai bức tranh khác nhau, và
            # buồng lái sẽ hiện một bản kê không khớp việc máy đã làm.
            # Lợi suất TỤT theo quy mô — một con số APR không kèm mức vốn
            # là một con số bỏ bớt. Xem `duong_suc_chua.py`.
            "duongSucChua": self.duong_suc_chua(),
            # Trần khoá vốn 720 giờ chặn mất bao nhiêu. Đo 30/08 trên máy
            # sống: cùng 460k tiền mặt, 2,48%/năm dưới trần và 9,38% nếu
            # bỏ trần — cả động cơ Pendle PT đứng ngoài vì một tham số.
            # ĐO, không đề xuất: nới trần là cửa `dat_tham_so`.
            "duongKhoaVon": self.duong_khoa_von(),
            "xoayCho": (self.latCatXoayCho.tom_tat()
                        if self.latCatXoayCho is not None
                        else self.xoay_cho().tom_tat()),
        }


#: Giữ ngắn hơn ngần này giờ thì KHÔNG quy ra «bps mỗi giờ».
#:
#: Đo trên máy sống 29/08: bảng «hứa vs thực» hiện `thực −2.618 bps/giờ`
#: cho ty cash-and-carry. Không phải nó lỗ 2.618 bps — nó mất đúng phí vào
#: lệnh (−0,45 bps) rồi đóng sau vài giây, và phép chia cho một mẫu số gần
#: bằng 0 phóng con số ấy lên gần sáu nghìn lần.
#:
#: Một tỉ suất chia cho gần-không thì không phải một tỉ suất — nó là hình
#: chiếu của mẫu số. Mười lăm phút là chỗ đứng: đủ ngắn để không bỏ sót vị
#: thế thật, đủ dài để mẫu số nói được điều gì.
TOI_THIEU_GIO_DOI_CHIEU = 0.25

#: Bao nhiêu vòng liên tiếp còn ghế trống mà số vị thế không tăng thì bắt
#: đầu nghi ngờ lời hứa «Phân Bổ sẽ lấp chỗ trống». Ba vòng, vì một vòng
#: có thể là chưa có cơ hội nào và hai vòng có thể là trùng hợp; ba vòng
#: liên tiếp thì đó là một trạng thái, không phải một lúc.
VONG_GHE_TRONG_DANG_NGO = 3


def _bps_gio_thuc(laiLoUsd: float, vonUsd: float,
                  daGiuGio: float) -> float | None:
    """Lãi lỗ THỰC quy ra bps mỗi giờ. `None` khi giữ quá ngắn để chia.

    `None` chứ không phải 0: «giữ chưa đủ lâu để nói» khác hẳn «huề vốn»,
    và bảng đối chiếu đã biết cách bỏ qua `None` mà đếm riêng.
    """
    if daGiuGio < TOI_THIEU_GIO_DOI_CHIEU or not vonUsd:
        return None
    return laiLoUsd / abs(vonUsd) * 10_000.0 / daGiuGio


def _bps_gio_du_doan(toTrinh: dict) -> float | None:
    """Lời hứa của tờ trình, quy về bps MỖI GIỜ. `None` khi không khai.

    Ưu tiên `netMoiGioBps` nếu tờ trình có sẵn — đó là con số chính tờ trình
    đã quy đổi, và tự quy lại là dựng bản sao thứ hai của một phép tính đã
    có. Không có thì suy từ `netUocBps / giuGio`.

    `None` chứ không phải 0: một ty không khai dự đoán thì nó chưa hứa gì,
    khác hẳn một ty hứa huề vốn — và trộn hai thứ ấy làm bảng đối chiếu
    khen nhầm đúng những ty im lặng.
    """
    if not isinstance(toTrinh, dict):
        return None
    v = toTrinh.get("netMoiGioBps")
    if v is not None:
        return float(v)
    net, gio = toTrinh.get("netUocBps"), toTrinh.get("giuGio")
    if net is None or not gio:
        return None
    return float(net) / float(gio)


def _lay_nut(thamSo: dict, duong: str):
    """Giá trị hiện tại của một núm, hoặc `None` khi không có núm ấy.

    `None` để bên gọi TỪ CHỐI, chứ không phải để nó tạo ra một núm mới:
    gõ nhầm `phanBo.toiDaSoVite` mà máy vẫn ghi thành công là đổi trúng hư
    không, và bản tham số mới trông y hệt một bản đã có hiệu lực.
    """
    o = thamSo
    for k in duong.split("."):
        if not isinstance(o, dict) or k not in o:
            return None
        o = o[k]
    return o


def _dat_nut(thamSo: dict, duong: str, gt) -> dict:
    """Bản SAO của tham số với một núm đã đổi. Không sửa bản gốc.

    Sửa tại chỗ thì lượt chạy lại A và B dùng chung một dict, và B thắng
    tuyệt đối vì A cũng đã bị vặn — một phép so sánh luôn nói "có tiến bộ".
    """
    import copy
    ra = copy.deepcopy(thamSo)
    o = ra
    phan = duong.split(".")
    for k in phan[:-1]:
        o = o.setdefault(k, {})
    o[phan[-1]] = gt
    return ra


def _ly_do(x: dict) -> str:
    """Lý do từ chối. `Phân Bổ` trả về hai dạng — chuỗi, và danh sách từ
    `PhanQuyet.tom_tat()`. Sổ Đăng Ký chỉ nhận một chuỗi, nên gộp ở đây."""
    l = x.get("lyDo")
    if isinstance(l, (list, tuple)):
        return "; ".join(str(i) for i in l) or "Rủi Ro Tổng từ chối"
    return str(l or "không được cấp vốn")


#: Nhịp soát hiến pháp trong ảnh chụp. Xem `_hien_phap`.
NHIP_HIEN_PHAP_GIAY = 60.0
_HP: tuple[float, dict] | None = None


def _hien_phap() -> dict:
    """Tóm tắt hiến pháp. Bọc try vì một phép canh nổ KHÔNG được làm chết
    ảnh chụp — buồng lái mất một ô còn hơn mất cả trang.

    ## Có NHỊP, vì soát hiến pháp KHÔNG rẻ

    Ba mươi mốt điều, phần lớn phân tích AST cả cây mã, và một điều dựng
    hẳn một Trung Ương rồi quay hai vòng thật — có ghi đĩa, có thư mục tạm.
    Buồng lái hỏi ảnh chụp mỗi vài giây, nên soát mỗi lần hỏi là chạy cả
    bộ luật vài chục lần một phút để nhận về **đúng một kết quả**: hiến
    pháp là hàm của MÃ NGUỒN, và mã nguồn không đổi giữa hai lần hỏi.

    Nên giữ bản cũ trong `NHIP_HIEN_PHAP_GIAY` giây, và **khai tuổi của
    nó**. Một con số cũ mà không nói mình cũ thì trông y hệt một con số
    mới — đúng cái bẫy `von-ngoai-mu` đã dạy.

    Bản LỒNG (`long`) không bao giờ được giữ: nó là ảnh chụp của cỗ máy do
    chính hiến pháp dựng lên để thử, giữ nó là để cả phút sau buồng lái
    vẫn đọc phải một tóm tắt rỗng.
    """
    global _HP
    import time as _t
    gio = _t.time()
    if _HP is not None and gio - _HP[0] < NHIP_HIEN_PHAP_GIAY:
        return dict(_HP[1], tuoiGiay=round(gio - _HP[0], 1))
    try:
        from .hien_phap import tom_tat
        ra = tom_tat()
    except Exception as e:                                # noqa: BLE001
        return {"loi": f"{type(e).__name__}: {e}"}
    if not ra.get("long"):
        _HP = (gio, ra)
    return dict(ra, tuoiGiay=0.0)


#: Thu một vòng được vượt lời hứa bao nhiêu LẦN trước khi bị kêu.
#:
#: Rộng, và cố ý rộng: funding đảo chiều, phí AMM bùng lên khi có biến —
#: thu gấp mấy lần mức hứa là chuyện thật của thị trường. Cái phép soát
#: này săn là lỗi ĐƠN VỊ (quên chia 8.760 giờ, 365 ngày, 24 giờ), và
#: những lỗi ấy sai gấp hàng trăm lần chứ không phải gấp mười.
BIEN_THU_VUOT_TRAN = 10.0


def _tran_thu_mot_vong(toTrinh, vonUsd, tuGiay, denGiay):
    """Vòng này thu nhiều nhất bao nhiêu thì còn hợp lý. `None` = không đo.

    Dựng từ chính lời hứa của tờ trình. Thiếu lời hứa thì trả `None` —
    không có gì để so thì không kết luận, chứ không dựng một trần bịa.
    """
    from .xoay_cho import apr_tu_to_trinh
    t = toTrinh if isinstance(toTrinh, dict) else (
        toTrinh.tom_tat() if hasattr(toTrinh, "tom_tat") else {})
    apr = apr_tu_to_trinh(t)
    if apr is None or apr <= 0:
        return None
    dt = (float(denGiay) - float(tuGiay)) / 3600.0
    if dt <= 0:
        return None
    return (abs(float(vonUsd)) * (apr / 100.0) * (dt / (365.0 * 24.0))
            * BIEN_THU_VUOT_TRAN)


def _gio_iso() -> str:
    """Giờ UTC theo ĐÚNG khuôn Sổ Đăng Ký ghi vào `chuyen_trang_thai.luc`.

    Khuôn phải trùng vì nó được đem đi so bằng `luc >= ?` — sqlite so hai
    chuỗi, không so hai mốc thời gian. Lệch một chữ (`+00:00` thay cho
    `Z`, hay `timespec="seconds"`) thì phép so vẫn chạy, vẫn trả về một
    tập hợp, chỉ là tập hợp sai — và sai theo hướng RỖNG, tức phễu tự
    nhiên có 0 ở nửa dưới mà không dòng nào kêu.

    Sổ Đăng Ký giữ bản của nó vì mỗi mô-đun ở đây cố ý không biết mô-đun
    khác tồn tại. Cái giá là hai bản có thể trôi khỏi nhau, nên chỗ ấy
    được canh bằng một phép kiểm chứ không bằng trí nhớ.
    """
    return _dt.datetime.now(_dt.timezone.utc).isoformat(
        timespec="milliseconds").replace("+00:00", "Z")


def _gio_he() -> float:
    """Giờ hệ thống, giây. Tách khỏi `_monotonic()` vì hai việc khác nhau:
    đơn điệu dùng cho cửa chống trùng, còn giờ hệ dùng cho tuổi vị thế —
    và tuổi vị thế phải so được với `moLucGiay` ghi lúc mở."""
    import time
    return time.time()


def _monotonic() -> float:
    """Đồng hồ đơn điệu — chỉnh giờ máy không được làm cửa chống
    trùng mở toang hay đóng vĩnh viễn."""
    import time
    return time.monotonic()


def _bay_gio() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(
        timespec="milliseconds").replace("+00:00", "Z")
