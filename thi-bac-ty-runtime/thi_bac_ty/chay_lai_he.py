"""CHẠY LẠI HỆ — đo lại một bộ tham số phân bổ trên tờ trình ĐÃ GHI.

`bac/chay_lai.py` chạy lại băng để đo funding THỰC NHẬN. File này chạy lại
một thứ khác hẳn: **quyết định phân bổ**.

## Thứ file này KHÔNG đo được, nói trước

    ✗ lãi lỗ
    ✗ tờ trình bị từ chối đáng lẽ có lãi hay không

Vì cơ hội không được cấp vốn thì không được mở, nên nó **không có kết cục**.
Không có kho dữ liệu nào trên đời chứa kết cục của một việc chưa từng làm.

Đó là lý do Trung Ương chỉ ĐỀ XUẤT chứ không tự vặn — xem `trung_uong.hoc()`.

## Thứ nó ĐO được, và vì sao vẫn đáng

Cùng một lô tờ trình đã ghi, hai bộ tham số cho ra **hình dạng phân bổ**
khác nhau, và hình dạng ấy đo được hết:

    bao nhiêu vốn được rót ra          bao nhiêu nằm không
    rót vào cơ hội tốt đến mức nào     (NET/giờ bình quân theo vốn)
    dồn vào một cảng bao nhiêu         dồn vào một ty bao nhiêu
    trần nào là trần thật sự chặn      (đếm theo `lyDoCat`)

Nhờ đó câu *"nới trần cảng lên 0,45 thì sao"* thôi là phỏng đoán.

## Cái bẫy phải chặn ngay trong thiết kế

Nới hết mọi trần thì **luôn** rót được nhiều vốn hơn và NET/giờ bình quân
gần như luôn đẹp hơn. Nếu chấm điểm chỉ bằng hai con số ấy thì vòng tiến
hoá sẽ học đúng một bài: **bỏ hết giới hạn**.

Nên `doi_chieu()` KHÔNG tuyên bố người thắng khi bên B rót nhiều hơn mà độ
tập trung cũng cao hơn. Nó nói thẳng là "B nhận thêm rủi ro để đổi lấy lợi
suất" và để người đọc quyết. Một cỗ máy tự chấm điểm mình phải bị cấm cái
thang điểm mà nó có thể leo bằng cách tự tháo phanh.

## Một giản lược, khai rõ

Cả cửa sổ được coi là MỘT lô, rót trên một danh mục sạch. Nó trả lời
*"với ngần này cơ hội và ngần này vốn, bộ tham số nào rót ra sao"*. Nó
KHÔNG mô phỏng vòng đời vị thế — không có lớp đặt lệnh nên không biết vị
thế nào đóng lúc nào. `moPhongVongDoi=False` trong kết quả nói điều đó.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .danh_muc import DanhMuc
from .phan_bo import PhanBo
from .rui_ro_tong import RuiRoTong
from .to_trinh import Chan, RuiRo, ToTrinh

#: Dưới ngần này tờ trình thì mọi so sánh đều là tiếng ồn.
TOI_THIEU_MAU = 20

#: Chênh lệch NET/giờ bình quân phải vượt ngần này (bps) mới coi là thật.
BIEN_VUOT_BPS = 0.02

#: Tỉ trọng phải dày thêm ngần này mới gọi là ĐẬM HƠN. Một phần mười của
#: một điểm phần trăm.
#:
#: Vế NET của cùng một phán quyết đã có biên nhiễu từ đầu
#: (`BIEN_VUOT_BPS`), vế TẬP TRUNG thì so ở 1e-9 — và cái lệch ấy nằm im
#: cho tới khi `quet_truc` bắt đầu hỏi cùng câu. Quét
#: `ruiRoTong.ruiRoToiDa` làn thật 05/09/2026:
#:
#:     0.6  (đang dùng)   400,18 USD/giờ   tỉ trọng ty 0,4661773
#:     0.75              418,71 USD/giờ   tỉ trọng ty 0,4662804
#:
#: Thu hơn **4,6%**, tập trung dày thêm **0,0103 điểm phần trăm** — và
#: luật 1e-9 loại nó. Bảng còn in cả hai dòng là «46.6%», nên người đọc
#: thấy một kẻ bị loại vì một khác biệt không hiện ra ở đâu.
#:
#: Con số 0,001 chọn TRƯỚC khi xem nó cho ra đáp án nào, theo
#: `nguong-tu-mau-thuan-voi-du-doan`: nó là độ phân giải cỗ máy này DÙNG
#: để báo tỉ trọng (một chữ số thập phân của phần trăm). Hai cấu hình
#: chênh nhau ít hơn thế thì in ra giống hệt nhau. Thả hai dự đoán vào:
#: «0,01 điểm là nhiễu» phải QUA, «gần mười điểm là thật» phải BỊ LOẠI —
#: ca `tranMotCang` 47,4% → 57,1% dày gấp **chín trăm lần** biên này.
#:
#: Đây là NỚI cổng duyệt, nói thẳng ra thế. Nó không lật đề xuất đang
#: chờ chữ ký: đường `hoc` vốn đã khai `damHon=False` cho đúng cặp ấy
#: trên cửa sổ của nó, nên phép sửa này không phải sửa để lấy đáp án.
BIEN_TAP_TRUNG = 0.001


def _pt(v) -> str:
    return "—" if v is None else f"{v * 100:.0f}%"


def _so(v):
    return None if v is None else float(v)


def dung_lai(d: dict) -> ToTrinh | None:
    """Dựng lại một `ToTrinh` từ payload đã lưu trong Sổ Đăng Ký.

    Trả `None` nếu payload thiếu/hỏng thay vì ném: một dòng hỏng trong sổ
    không được làm chết cả lượt chạy lại, nhưng nó phải bị ĐẾM ra — hàm gọi
    lo việc đếm.
    """
    try:
        chan = tuple(
            Chan(c["ben"], c["cang"], c["taiSan"], _so(c.get("vonUsd")),
                 c.get("loai") or "perp", c.get("chuoi"))
            for c in (d.get("chan") or ()))
        r = d.get("ruiRo") or {}
        return ToTrinh(
            chienLuoc=d["chienLuoc"], ho=d["ho"], taiSan=d["taiSan"], chan=chan,
            vonCanUsd=float(d["vonCanUsd"]),
            sucChuaToiDaUsd=_so(d.get("sucChuaToiDaUsd")),
            grossBps=float(d.get("grossBps") or 0.0),
            phiUocBps=float(d.get("phiUocBps") or 0.0),
            netUocBps=float(d.get("netUocBps") or 0.0),
            giuGio=float(d.get("giuGio") or 1.0),
            ruiRo=RuiRo(*(_so(r.get(m)) for m in
                          ("thiTruong", "thanhKhoan", "giaoThuc",
                           "cang", "thucThi", "cauNoi"))),
            tuoiDuLieuGiay=_so(d.get("tuoiDuLieuGiay")),
            tinCay=_so(d.get("tinCay")),
            moHinhPhiDuChua=bool(d.get("moHinhPhiDuChua")),
            phiConThieu=tuple(d.get("phiConThieu") or ()),
            moHinhSucChuaDuChua=bool(d.get("moHinhSucChuaDuChua")),
            sucChuaConThieu=tuple(d.get("sucChuaConThieu") or ()),
            dinhGiaBang=d.get("dinhGiaBang") or "USDT",
            cang=tuple(d.get("cang") or ()),
            chuoi=tuple(d.get("chuoi") or ()),
            bangChung=tuple(d.get("bangChung") or ()),
            ma=d["ma"], luc=d.get("luc") or "")
    except (KeyError, TypeError, ValueError):
        return None


def thu_hoach(so_dang_ky, n: int = 2000) -> tuple[list[ToTrinh], int]:
    """Đọc tờ trình đã ghi. Trả `(danh sách, số dòng hỏng)`."""
    ra, hong = [], 0
    try:
        with so_dang_ky._mo() as con:
            h = con.execute(
                "SELECT payload FROM to_trinh ORDER BY lucTao DESC LIMIT ?",
                (int(n),)).fetchall()
    except Exception:                                    # noqa: BLE001
        return [], 0
    import json
    for (p,) in h:
        try:
            t = dung_lai(json.loads(p))
        except (json.JSONDecodeError, TypeError):
            t = None
        if t is None:
            hong += 1
        else:
            ra.append(t)
    # Trả theo thứ tự thời gian vì đó là điều người gọi mong đợi ở một hàm
    # "thu hoạch". Nhưng nói rõ: `mot_luot()` KHÔNG phụ thuộc thứ tự này —
    # `phan_bo.chia()` tự xếp hạng lại theo điểm. Bỏ dòng này đi thì không
    # phép kiểm nào đỏ, và đó chính là lý do phải ghi ra đây: người sau đọc
    # một dòng sắp xếp sẽ tưởng nó đang giữ một bất biến nào đó.
    ra.sort(key=lambda t: t.luc)
    return ra, hong


@dataclass
class KetQua:
    nhan: str
    soToTrinh: int = 0
    soCap: int = 0
    tongCapUsd: float = 0.0
    vonNamKhongUsd: float = 0.0
    netMoiGioBinhQuanBps: float | None = None
    dayNhatCangUsd: float = 0.0
    dayNhatCang: str = ""
    dayNhatTyUsd: float = 0.0

    @property
    def tiTrongCang(self) -> float | None:
        """Phần vốn đã rót nằm ở cảng dày nhất.

        So bằng TỈ TRỌNG chứ không bằng USD, và đây là chỗ bản đầu làm sai:
        trong một hệ chỉ có MỘT ty, rót thêm đồng nào cũng làm `dayNhatTyUsd`
        tăng, nên mọi bộ tham số rót nhiều hơn đều bị chấm là "đậm hơn". Cái
        thước ấy không phân biệt được *rót nhiều* với *dồn một chỗ* — mà chỉ
        chuyện thứ hai mới là tập trung rủi ro.

        Còn *rót nhiều bao nhiêu* thì đã có `tranTongDungVon` và `tiLeDuTru`
        canh, và cả hai nằm trong `CUA_AN_TOAN_HE` nên vòng tiến hoá không
        vặn được.
        """
        return (self.dayNhatCangUsd / self.tongCapUsd
                if self.tongCapUsd > 0 else None)

    @property
    def tiTrongTy(self) -> float | None:
        return (self.dayNhatTyUsd / self.tongCapUsd
                if self.tongCapUsd > 0 else None)
    tranChanNhieuNhat: dict = field(default_factory=dict)
    soDongHong: int = 0
    #: Luôn False ở bản này — xem docstring đầu file.
    moPhongVongDoi: bool = False

    def tom_tat(self) -> dict:
        return {
            "nhan": self.nhan, "soToTrinh": self.soToTrinh,
            "soCap": self.soCap, "tongCapUsd": self.tongCapUsd,
            "vonNamKhongUsd": self.vonNamKhongUsd,
            "netMoiGioBinhQuanBps": self.netMoiGioBinhQuanBps,
            "dayNhatCang": self.dayNhatCang,
            "dayNhatCangUsd": self.dayNhatCangUsd,
            "dayNhatTyUsd": self.dayNhatTyUsd,
            "tiTrongCang": self.tiTrongCang,
            "tiTrongTy": self.tiTrongTy,
            "tranChanNhieuNhat": dict(self.tranChanNhieuNhat),
            "soDongHong": self.soDongHong,
            "moPhongVongDoi": self.moPhongVongDoi,
            "khongDoDuoc": ["lãi lỗ", "cơ hội bị từ chối đáng lẽ có lãi hay không"],
        }


def mot_luot(toTrinh: list, thamSo: dict, vonBanDauUsd: float,
             nhan: str = "", soDongHong: int = 0) -> KetQua:
    """Rót lại cả lô trên một danh mục SẠCH, với bộ tham số cho trước."""
    dm = DanhMuc(float(vonBanDauUsd))
    rrt = RuiRoTong(thamSo.get("ruiRoTong") or {})
    # `or {}` là lớp thứ hai: `PhanBo.__init__` đã viết `cau_hinh or {}`,
    # nên `None` đi qua được cả hai đường. Con đột biến TƯƠNG ĐƯƠNG.
    pb = PhanBo(thamSo.get("phanBo") or {})
    lat = pb.chia(list(toTrinh), rrt, dm, None, "chay-lai")

    kq = KetQua(nhan=nhan or "?", soToTrinh=len(toTrinh),
                soCap=len(lat.daCap), tongCapUsd=lat.tongCapUsd,
                vonNamKhongUsd=dm.tienMatUsd, soDongHong=soDongHong)

    # NET/giờ bình quân THEO VỐN, không theo số cơ hội: rót $500 vào một cơ
    # hội 2 bps/giờ và $10 vào một cơ hội 40 bps/giờ thì bình quân theo đầu
    # cơ hội là 21, mà thực tế danh mục chỉ kiếm được gần 2.
    if lat.tongCapUsd > 0:
        kq.netMoiGioBinhQuanBps = sum(
            x["capUsd"] * x["netMoiGioBps"] for x in lat.daCap) / lat.tongCapUsd

    pn_cang = dm.phoi_nhiem_cang()
    if pn_cang:
        kq.dayNhatCang, kq.dayNhatCangUsd = max(pn_cang.items(),
                                                key=lambda kv: kv[1])
    pn_ty = dm.phoi_nhiem_ty()
    if pn_ty:
        kq.dayNhatTyUsd = max(pn_ty.values())

    # Trần nào chặn nhiều nhất — câu trả lời cho "nới cái nào thì đáng".
    dem: dict[str, int] = {}
    for x in lat.daCap:
        for l in x.get("lyDoCat") or ():
            k = str(l).split(":")[0]
            dem[k] = dem.get(k, 0) + 1
    for x in lat.tuChoi:
        ly = x.get("lyDo")
        for l in (ly if isinstance(ly, (list, tuple)) else [ly]):
            k = str(l or "").split(":")[0][:60]
            if k:
                dem[k] = dem.get(k, 0) + 1
    kq.tranChanNhieuNhat = dict(sorted(dem.items(), key=lambda kv: -kv[1])[:8])
    return kq


def dam_hon_hai_ben(aCang, aTy, bCang, bTy) -> bool:
    """B TẬP TRUNG hơn A — một chỗ duy nhất giữ luật này.

    `quet_truc.tot_nhat` cũng phải hỏi đúng câu ấy, và chép phép so ra
    hai nơi là hai nơi sẽ lệch. Biên `BIEN_TAP_TRUNG` nuốt trọn chỗ `>`
    khác `>=`, nên con đột biến ở đó TƯƠNG ĐƯƠNG; cái đáng kiểm là hai
    vế `is not None` và chính cái biên.
    """
    def _hon(x, y):
        return x is not None and y is not None and x > y + BIEN_TAP_TRUNG
    return _hon(bCang, aCang) or _hon(bTy, aTy)


def doi_chieu(toTrinh: list, thamSoA: dict, thamSoB: dict,
              vonBanDauUsd: float, soDongHong: int = 0) -> dict:
    """Chạy A và B trên CÙNG một lô, rồi nói ra chênh lệch — không phán."""
    if len(toTrinh) < TOI_THIEU_MAU:
        return {
            "duDeKetLuan": False,
            "vi": f"mới {len(toTrinh)} tờ trình, cần ≥ {TOI_THIEU_MAU} — "
                  f"dưới ngưỡng này mọi chênh lệch đều là tiếng ồn",
            "soToTrinh": len(toTrinh),
        }

    a = mot_luot(toTrinh, thamSoA, vonBanDauUsd, "A", soDongHong)
    b = mot_luot(toTrinh, thamSoB, vonBanDauUsd, "B", soDongHong)

    na, nb = a.netMoiGioBinhQuanBps, b.netMoiGioBinhQuanBps
    lech = None if (na is None or nb is None) else nb - na
    # Tập trung so bằng TỈ TRỌNG vốn đã rót — xem `KetQua.tiTrongCang`.
    dam_hon = dam_hon_hai_ben(a.tiTrongCang, a.tiTrongTy,
                              b.tiTrongCang, b.tiTrongTy)

    if lech is None:
        ket, vi = "khong-ket-luan", "một bên không rót được đồng nào"
    elif abs(lech) < BIEN_VUOT_BPS:
        ket, vi = "hoa", (f"chênh {lech:+.4f} bps/giờ chưa vượt biên nhiễu "
                          f"{BIEN_VUOT_BPS} — đứng yên là kết quả hợp lệ")
    elif lech > 0 and dam_hon:
        # ĐÂY là nhánh giữ cho vòng tiến hoá không học được cách tự tháo phanh.
        ket, vi = "b-tot-hon-NHUNG-dam-hon", (
            f"B hơn {lech:+.4f} bps/giờ, nhưng độ tập trung CŨNG cao hơn "
            f"(cảng dày nhất {_pt(a.tiTrongCang)} → {_pt(b.tiTrongCang)} "
            f"vốn đã rót, ty {_pt(a.tiTrongTy)} → {_pt(b.tiTrongTy)}). Đây "
            f"là đổi rủi ro lấy lợi suất, không phải cải thiện. Người quyết.")
    elif lech > 0:
        ket, vi = "b-tot-hon", (
            f"B hơn {lech:+.4f} bps/giờ mà KHÔNG tập trung hơn — đây mới là "
            f"cải thiện thật")
    else:
        ket, vi = "a-tot-hon", f"A hơn {-lech:+.4f} bps/giờ"

    return {
        "duDeKetLuan": True, "ketLuan": ket, "vi": vi,
        "lechNetMoiGioBps": lech, "damHon": dam_hon,
        "A": a.tom_tat(), "B": b.tom_tat(),
        "loiNhac": "So HÌNH DẠNG phân bổ, KHÔNG so lãi lỗ. Cơ hội không được "
                   "cấp vốn thì không được mở, nên nó không có kết cục để mà "
                   "đo.",
    }
