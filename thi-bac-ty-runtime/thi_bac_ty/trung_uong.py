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

from .cau_dao import CauDao
from .chan_doan_he import chan_doan_he, de_xuat
from .chay_lai_he import doi_chieu, thu_hoach
from .danh_muc import DanhMuc
from .phan_bo import PhanBo
from .rui_ro_tong import RuiRoTong
from .so_cai import ButToan, SoCai
from .so_dang_ky import SoDangKy
from .thong_chinh import ThongChinh
from .thuc_thi import DieuPhoiThucThi, YChiThucThi

MAC_DINH = {
    "vonBanDauUsd": 1000.0,
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

    Cùng ty, cùng tài sản, cùng bộ chân (bên + cảng) thì là cùng một cơ hội,
    dù quét lại một trăm lần. Cố ý KHÔNG gộp giá hay NET vào đây: chúng nhúc
    nhích mỗi lượt quét, nên gộp vào là mỗi lượt lại ra một vân tay mới và
    cửa chống trùng thành vô dụng.
    """
    return (f"{tt.chienLuoc}|{tt.taiSan}|"
            + ",".join(sorted(f"{c.ben}@{c.cang}" for c in tt.chan)))


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
        self.rui_ro_tong = RuiRoTong(c["ruiRoTong"])
        self.phan_bo = PhanBo(c["phanBo"])
        self.cau_dao = CauDao()
        self.thuc_thi = DieuPhoiThucThi()

        self.ty: dict[str, object] = {}
        self.vong = 0
        self.latCatCuoi: LatCatVong | None = None
        #: Tờ trình ĐÃ NỘP trong vòng gần nhất. Buồng lái đọc chỗ này chứ
        #: không tự dựng lại — dựng lại thì mỗi lần một mã khác, và người
        #: đọc không nối được tờ trên màn hình với tờ trong sổ đăng ký.
        self.toTrinhVongNay: list = []
        #: dấu vân cơ hội → lần cuối vào sổ (giây, đồng hồ đơn điệu)
        self._dauVet: dict[str, float] = {}
        self.soBoTrung = 0
        self.hocCuoi: dict | None = None
        self._soXet = d / f"{ten}-xet-tham-so.jsonl"
        self._ngayDon = ""

    # ── đăng ký ty ────────────────────────────────────────────────────────
    def dang_ky(self, ty) -> bool:
        """Nhận một ty vào hệ thống. Khai sai thì **chết ở cửa**."""
        loi = type(ty).kiem_khai()
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

        # ── 3. cầu dao — TRƯỚC khi cam kết bất cứ đồng nào ───────────────
        sut = None
        if self.danh_muc.vonBanDauUsd > 0:
            sut = max(0.0, (1.0 - self.danh_muc.navUsd
                            / self.danh_muc.vonBanDauUsd) * 100.0)
        self.cau_dao.tu_soat(
            lechDongHoGiay=lechDongHoGiay, cangChet=list(cangChet or []),
            tuoiXauNhatGiay=tuoiXauNhatGiay, sutVonPct=sut,
            nguong=self.c["nguongCauDao"], so_cai=self.so_cai)

        duoc, ly = self.cau_dao.cho_phep()
        lat.cauDaoNgat = not duoc
        lat.lyDoNgat = list(ly)

        if not duoc:
            # Vẫn quét, vẫn ghi nhận, vẫn chẩn đoán — CHỈ không cam kết vốn.
            # Dừng cả việc quan sát là tự làm mình mù đúng lúc cần nhìn nhất.
            for tt in song:
                self.so_dang_ky.chuyen(tt.ma, "TU_CHOI",
                                       "CẦU DAO NGẮT: " + "; ".join(ly))
            self.latCatCuoi = lat
            self._don_dinh_ky()
            return lat

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

        self.latCatCuoi = lat
        self._don_dinh_ky()
        return lat

    def _don_dinh_ky(self) -> None:
        ngay = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d")
        if ngay == self._ngayDon:
            return
        self._ngayDon = ngay
        self.so_dang_ky.don_cu(int(self.c["giuNgaySoDangKy"]))
        # Dấu vết cũ hơn hai nhịp thì không còn chặn gì nữa, chỉ tốn chỗ.
        han = _monotonic() - float(self.c["nhipGhiNhanGiay"]) * 2.0
        self._dauVet = {k: v for k, v in self._dauVet.items() if v > han}

    # ── bước 6–7: CHẨN ĐOÁN → XÉT LẠI THAM SỐ ────────────────────────────
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
        if dx:
            tt, hong = thu_hoach(self.so_dang_ky)
            moi = _dat_nut(goc, dx[0].nut, dx[0].den)
            do = doi_chieu(tt, goc, moi, self.danh_muc.vonBanDauUsd, hong)

        ra = {"luc": _bay_gio(), "vong": self.vong,
              "trieuChung": [t.tom_tat() for t in trieu],
              "deXuat": [d.tom_tat() for d in dx],
              "doDuoc": do,
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
            "nac": [{"ten": k, "so": v,
                     # `None` chứ không phải 0: "chưa thấy cơ hội nào" khác
                     # hẳn "thấy rồi mà không cái nào qua".
                     "tiLe": (v / tho if tho else None)} for k, v in nac],
            "coHoiTho": tho, "quaCongTy": qua,
            "tuChoi": int(p.get("TU_CHOI") or 0),
            "hong": int(p.get("HONG") or 0),
            "soChuyenSai": self.so_dang_ky.soChuyenSai,
        }

    # ── ảnh chụp ──────────────────────────────────────────────────────────
    def anh_chup(self) -> dict:
        return {
            "vong": self.vong,
            "ty": [t.tom_tat() for t in self.ty.values()],
            "thongChinh": self.thong_chinh.tom_tat(),
            "soDangKy": self.so_dang_ky.tom_tat(),
            "danhMuc": self.danh_muc.tom_tat(),
            "ruiRoTong": self.rui_ro_tong.tom_tat(),
            "phanBo": self.phan_bo.tom_tat(),
            "cauDao": self.cau_dao.tom_tat(),
            "thucThi": self.thuc_thi.tom_tat(),
            "soCai": self.so_cai.tom_tat(),
            "pheuDayDu": self.pheu_day_du(),
            "toTrinh": [t.tom_tat() for t in self.toTrinhVongNay],
            "latCatVong": self.latCatCuoi.tom_tat() if self.latCatCuoi else None,
            "hoc": self.hocCuoi,
            "thamSo": self.tham_so(),
        }


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


def _monotonic() -> float:
    """Đồng hồ đơn điệu — chỉnh giờ máy không được làm cửa chống
    trùng mở toang hay đóng vĩnh viễn."""
    import time
    return time.monotonic()


def _bay_gio() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(
        timespec="milliseconds").replace("+00:00", "Z")
