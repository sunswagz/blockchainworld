"""ĐỐI SOÁT VỊ THẾ — sổ đăng ký nhớ, danh mục thì quên.

Sự cố đã dạy ra file này, đo ngày 28/08/2026 trên chính máy đang chạy:
sổ đăng ký có **4 tờ trình đứng ở `DA_MO`**, mở ngày 26/08, và sổ cái ghi
`CAP_VON` tổng **500 USD** cho đúng bốn tờ ấy. Danh mục cùng lúc báo
`soViThe: 0`, `daCamKetUsd: 0`, `tiLeDungVon: 0`.

Cả hai đều đúng theo cách của mình, và đó mới là chỗ nguy:

    sổ đăng ký   nằm trên đĩa   → sống qua mọi lần khởi động lại
    danh mục     dựng trong RAM → `DanhMuc.__init__` đặt `viThe = {}`

Nên **mỗi lần khởi động lại là một lần vốn đã cam kết bốc hơi khỏi phép
tính trần**, trong khi sổ vẫn ghi là đang mở. Hậu quả cùng họ với
`von-ngoai-mu` nhưng ngược chiều: ở đó NAV thiếu một phần nên trần rộng
hơn sự thật; ở đây phần ĐÃ TIÊU bị quên nên tiền rảnh rộng hơn sự thật.
Trên NAV 1000 thì 500 USD bị quên là một nửa. Không lỗi nào nổ, không
dòng nhật ký nào báo — chỉ có một con số 0 trông rất khoẻ.

Và nó không tự hết. Trong cả hệ **không có đường nào chuyển sang
`DA_DONG`** (`grep -rn DA_DONG` chỉ ra bảng trạng thái và phép kiểm, không
ra một lời gọi nào). Vị thế mở ra thì ở lại `DA_MO` vĩnh viễn.

## CẬP NHẬT 29/08: danh mục nay SỐNG QUA lần khởi động lại

Câu "danh mục dựng trong RAM nên mỗi lần khởi động lại là một lần vốn đã
cam kết bốc hơi" **không còn đúng**. `luu_danh_muc.py` ghi danh mục ra
đĩa sau mỗi vòng và nạp lại lúc khởi động, nên đường bình thường không
sinh ra tờ mồ côi nào nữa.

Điều đó KHÔNG làm file này thừa — nó đổi ý nghĩa của một tờ mồ côi, và
đổi theo hướng nặng hơn. Trước đây mồ côi là chuyện thường tình sau mỗi
lần restart; **nay mồ côi nghĩa là bản lưu đã mất hoặc hỏng**, tức là
danh mục thật sự không còn biết mình đang giữ gì. Chính vì thế mà phép
đối soát này phải ở lại: nó là thứ duy nhất phát hiện ra chuyện ấy.

Con số đã đo, giữ lại làm chứng cứ cho vì sao bản lưu tồn tại: trước khi
có nó, sổ ghi **51 lần vào lệnh cho 7 vị thế** trong một buổi chiều, và
3,43 USD phí vào lệnh ấy đội lốt lỗ của chiến lược.

## Hai nhánh, và ranh giới giữa chúng là `moPhong`

**Mô phỏng.** Vị thế không tồn tại ở đâu ngoài máy này — không sàn nào
giữ nó, không đồng nào đã đi. Nên khi danh mục KHÔNG còn giữ nó (bản lưu
mất hoặc hỏng) thì nó thật sự không còn ở đâu cả, và đóng ở sổ kèm bút
toán là ghi lại đúng cái đã xảy ra. Không có gì để đối soát với ai.

**Tiền thật.** Ngược hẳn: vị thế VẪN Ở ĐÓ trên sàn sau khi runtime chết.
Tự đóng ở sổ lúc ấy là bịa ra một lần đóng chưa từng xảy ra, và bỏ quên
một vị thế thật đang chạy — hai lời nói dối cùng lúc. Nên nhánh này
KHÔNG đóng gì: nó ngắt cầu dao và đòi NGƯỜI.

Nhánh thứ hai chưa chạy được ở bản này (`DieuPhoiThucThi.moPhong` là True
cứng), nhưng phép kiểm dựng một lớp thực thi giả để đi vào nó — một nhánh
chỉ có văn xuôi bảo vệ là một nhánh chưa được bảo vệ.

## Vì sao đọc vốn từ SỔ CÁI chứ không từ tờ trình

`toTrinh["vonCanUsd"]` là vốn **xin**; Phân Bổ cấp ít hơn là chuyện
thường, và ở đây đã thật: bốn tờ xin 200 mỗi tờ, được cấp 100·150·100·150.
Lấy số xin mà báo là "vốn bị quên" thì thổi 500 thành 800. Nên số thật
lấy từ bút toán `CAP_VON` của chính tờ trình ấy — và tờ nào không tìm
thấy bút toán thì trả `None`, **không trả 0**: "không biết" và "không có"
là hai chuyện, gộp lại là mất đúng thứ đáng báo động.
"""
from __future__ import annotations

from dataclasses import dataclass, field

MA_NGAT = "vi-the-mo-coi"


@dataclass
class ViTheMoCoi:
    """Một tờ trình đang `DA_MO` ở sổ mà danh mục không giữ chân nào."""
    ma: str
    chienLuoc: str
    taiSan: str
    moLuc: str
    #: Vốn ĐƯỢC CẤP, đọc từ bút toán CAP_VON. `None` = không tìm thấy
    #: bút toán nào, tức là không biết — khác hẳn không có.
    vonDaCapUsd: float | None
    #: Vốn tờ trình XIN. Giữ lại để so, không dùng để cộng.
    vonXinUsd: float | None

    def tom_tat(self) -> dict:
        return {"ma": self.ma, "chienLuoc": self.chienLuoc,
                "taiSan": self.taiSan, "moLuc": self.moLuc,
                "vonDaCapUsd": self.vonDaCapUsd, "vonXinUsd": self.vonXinUsd}


@dataclass
class BaoCao:
    """Kết quả một lượt đối soát. `daDong` rỗng KHÔNG có nghĩa là sạch."""
    moCoi: list[ViTheMoCoi] = field(default_factory=list)
    #: Mã có trong danh mục mà sổ không ghi là DA_MO. Chiều ngược lại, và
    #: nó tệ hơn: vốn đang bị giữ cho một thứ sổ không biết tới.
    laTrongDanhMuc: list[str] = field(default_factory=list)
    daDong: list[str] = field(default_factory=list)
    canNguoi: bool = False
    loi: list[str] = field(default_factory=list)

    @property
    def soKhongDoDuocVon(self) -> int:
        """Số tờ CÒN mồ côi mà không đọc được vốn đã cấp. Cộng tiền trên một
        tập có lỗ hổng rồi in ra như tổng đầy đủ là đúng lỗi Router cấm."""
        return sum(1 for x in self.conMoCoi if x.vonDaCapUsd is None)

    @property
    def vonMoCoiUsd(self) -> float | None:
        """`None` nếu có tờ nào không đọc được vốn — một lỗ thì cả tổng mù."""
        if self.soKhongDoDuocVon:
            return None
        return sum(float(x.vonDaCapUsd or 0.0) for x in self.conMoCoi)

    @property
    def vonDaDongUsd(self) -> float | None:
        """Vốn của những tờ ĐÃ đóng được. Không gộp vào `vonMoCoiUsd` —
        cái đó là "còn đang lệch bao nhiêu", cái này là "vừa dọn bao
        nhiêu". Gộp hai câu khác nhau vào một con số là cách chắc chắn để
        không câu nào còn đọc được."""
        xong = set(self.daDong)
        ds = [x for x in self.moCoi if x.ma in xong]
        if not ds or any(x.vonDaCapUsd is None for x in ds):
            return None
        return sum(float(x.vonDaCapUsd or 0.0) for x in ds)

    @property
    def conMoCoi(self) -> list[ViTheMoCoi]:
        """Mồ côi CHƯA đóng được. Khác `moCoi` — đó là tập lúc bắt đầu.

        Buồng lái phải đọc con số này chứ không phải `soMoCoi`: sau một lượt
        đối soát thành công, `soMoCoi` vẫn là 4 (đã tìm thấy 4) trong khi
        lệch đã hết. Báo động theo con số cũ là báo động cho việc vừa sửa
        xong — và cảnh báo báo nhầm thì lần đúng cũng bị bỏ qua.
        """
        xong = set(self.daDong)
        return [x for x in self.moCoi if x.ma not in xong]

    @property
    def lech(self) -> bool:
        return bool(self.conMoCoi or self.laTrongDanhMuc)

    def tom_tat(self) -> dict:
        return {
            "lech": self.lech,
            "soMoCoi": len(self.moCoi),
            "soConMoCoi": len(self.conMoCoi),
            "soLaTrongDanhMuc": len(self.laTrongDanhMuc),
            "vonMoCoiUsd": self.vonMoCoiUsd,
            "vonDaDongUsd": self.vonDaDongUsd,
            "soKhongDoDuocVon": self.soKhongDoDuocVon,
            "daDong": list(self.daDong),
            "canNguoi": self.canNguoi,
            "moCoi": [x.tom_tat() for x in self.moCoi],
            "laTrongDanhMuc": list(self.laTrongDanhMuc),
            "loi": list(self.loi),
            "vi": _vi(self),
        }


def _vi(b: BaoCao) -> str:
    if b.daDong and not b.lech:
        return (f"Đã đối soát: đóng {len(b.daDong)} tờ mồ côi ở sổ, kèm bút "
                f"toán. Danh mục không giữ chân nào cho chúng — bản lưu "
                f"danh mục đã mất hoặc hỏng, vì đường bình thường nay giữ "
                f"được vị thế qua lần khởi động lại. Hai sổ giờ khớp nhau.")
    if not b.lech:
        return ("Sổ đăng ký và danh mục khớp nhau: không tờ nào đứng DA_MO "
                "mà danh mục không giữ.")
    if b.canNguoi:
        return ("LỆCH, và máy KHÔNG tự đóng: lớp thực thi đang chạy tiền "
                "thật nên vị thế vẫn ở trên sàn sau khi runtime chết. Tự "
                "đóng ở sổ là bịa ra một lần đóng chưa từng xảy ra. Phải có "
                "NGƯỜI đối soát với sàn rồi đóng tay.")
    if b.loi:
        return (f"LỆCH, và đối soát HỎNG giữa chừng: đóng được "
                f"{len(b.daDong)}/{len(b.moCoi)} tờ. Xem `loi`.")
    von = b.vonMoCoiUsd
    return (f"LỆCH: {len(b.conMoCoi)} vị thế đứng DA_MO ở sổ mà danh mục "
            f"không giữ chân nào" + (f", tổng {von:.0f} USD đã cấp"
                                     if von is not None else "")
            + ". Vốn ấy đang nằm ngoài mọi phép tính trần.")


def do(so_dang_ky, danh_muc, so_cai=None, n: int = 200) -> BaoCao:
    """ĐO, không sửa gì. Tách hẳn khỏi `doi_soat()` để buồng lái gọi được
    mỗi vòng mà không sợ nó âm thầm ghi sổ."""
    b = BaoCao()
    try:
        hang = so_dang_ky.theo_trang_thai("DA_MO", n)
    except Exception as e:                                  # noqa: BLE001
        b.loi.append(f"{type(e).__name__}: {e}")
        return b

    trong_danh_muc = set(getattr(danh_muc, "viThe", {}) or {})
    trong_so = set()
    for h in hang:
        ma = str(h.get("ma") or "")
        trong_so.add(ma)
        if ma in trong_danh_muc:
            continue
        tt = h.get("toTrinh") or {}
        b.moCoi.append(ViTheMoCoi(
            ma=ma,
            chienLuoc=str(h.get("chienLuoc") or tt.get("chienLuoc") or "—"),
            taiSan=str(h.get("taiSan") or tt.get("taiSan") or "—"),
            moLuc=str(h.get("lucDoi") or ""),
            vonDaCapUsd=_cap_von(so_cai, ma),
            vonXinUsd=_so(tt.get("vonCanUsd")),
        ))
    b.laTrongDanhMuc = sorted(trong_danh_muc - trong_so)
    return b


def canh(so_dang_ky, danh_muc, thuc_thi, so_cai, cau_dao, n: int = 200):
    """Đo mỗi vòng và nối vào cầu dao. **Không đóng tờ nào.**

    `tuMo` lấy từ `moPhong`, và đây là chỗ duy nhất quyết định điều đó —
    `CauDao.ngat()` GHI ĐÈ cả `tuMo` khi ngắt lại cùng một mã, nên hai chỗ
    cùng ngắt `vi-the-mo-coi` với hai giá trị khác nhau sẽ hạ một lý do
    "phải có người" xuống thành "máy tự đóng" mà không ai thấy.

    · mô phỏng → `tuMo=True`: lệch trên giấy, đối soát xong là số khớp lại,
      và đọc lại là biết ngay — cùng họ với `von-ngoai-mu`.
    · tiền thật → `tuMo=False`: chỉ NGƯỜI đối soát được với sàn.
    """
    b = do(so_dang_ky, danh_muc, so_cai, n)
    mo_phong = bool(getattr(thuc_thi, "moPhong", False))
    b.canNguoi = bool(b.moCoi) and not mo_phong
    _noi_cau_dao(b, mo_phong, cau_dao, so_cai)
    return b


def _noi_cau_dao(b: BaoCao, mo_phong: bool, cau_dao, so_cai) -> None:
    """Nối kết quả đo vào cầu dao. Chỉ tính tờ **chưa đóng được**.

    Gọi SAU hành động, không phải trước. Ngắt rồi gỡ ngay trong một lượt
    khởi động thì `soLanNgat` cộng thêm một mỗi lần chạy lại — và chẩn đoán
    `cau-dao-ngat-nhieu` (ngưỡng 5 lần) sẽ kêu vì chính việc dọn dẹp thành
    công, tức là một cảnh báo báo nhầm đều đặn.
    """
    if cau_dao is None:
        return
    con = [x for x in b.moCoi if x.ma not in set(b.daDong)]
    if not con:
        cau_dao.het_ly_do(MA_NGAT)
        return
    von = (None if any(x.vonDaCapUsd is None for x in con)
           else sum(float(x.vonDaCapUsd or 0.0) for x in con))
    cau_dao.ngat(
        MA_NGAT,
        f"{len(con)} vị thế đứng DA_MO ở sổ mà danh mục không giữ chân nào ("
        + (f"{von:.0f} USD" if von is not None else "KHÔNG đo được vốn")
        + ") — vốn đã cam kết đang nằm ngoài mọi phép tính trần, nên tiền "
          "rảnh đang RỘNG HƠN sự thật"
        + ("" if mo_phong else
           ". Lớp thực thi chạy TIỀN THẬT: vị thế có thể vẫn đang mở trên "
           "sàn, máy KHÔNG tự đóng."),
        mo_phong, so_cai)


def doi_soat(so_dang_ky, danh_muc, thuc_thi, so_cai, cau_dao=None,
             n: int = 200) -> BaoCao:
    """ĐO rồi XỬ LÝ. Gọi lúc khởi động, và mỗi khi người bấm đối soát."""
    from .so_cai import ButToan

    b = do(so_dang_ky, danh_muc, so_cai, n)
    mo_phong = bool(getattr(thuc_thi, "moPhong", False))
    b.canNguoi = bool(b.moCoi) and not mo_phong
    if not b.moCoi or b.canNguoi:
        _noi_cau_dao(b, mo_phong, cau_dao, so_cai)
        return b

    for x in b.moCoi:
        ly_do = ("danh mục KHÔNG giữ chân nào cho tờ này — bản lưu danh "
                 "mục đã mất hoặc hỏng, vì đường bình thường nay giữ được "
                 "vị thế qua lần khởi động lại (xem luu_danh_muc.py)")
        if not so_dang_ky.chuyen(x.ma, "DA_DONG", ly_do):
            b.loi.append(f"{x.ma}: sổ từ chối chuyển DA_MO → DA_DONG")
            continue
        b.daDong.append(x.ma)
        try:
            so_cai.ghi(ButToan(
                "DONG_VI_THE", "[ĐỐI SOÁT] " + ly_do,
                0.0, x.chienLuoc, x.ma,
                {"vonDaCapUsd": x.vonDaCapUsd, "moLuc": x.moLuc,
                 "moPhong": True}))
            if x.vonDaCapUsd:
                so_cai.ghi(ButToan(
                    "HOAN_VON",
                    "[ĐỐI SOÁT] trả lại vốn đã cấp cho vị thế mô phỏng "
                    "không còn tồn tại",
                    float(x.vonDaCapUsd), x.chienLuoc, x.ma,
                    {"moLuc": x.moLuc}))
        except Exception as e:                              # noqa: BLE001
            b.loi.append(f"{x.ma}: ghi sổ cái hỏng — {type(e).__name__}: {e}")
    _noi_cau_dao(b, mo_phong, cau_dao, so_cai)
    return b


def _cap_von(so_cai, ma: str) -> float | None:
    """Vốn đã cấp cho một tờ trình, cộng từ bút toán `CAP_VON` của nó.

    `None` khi không có bút toán `CAP_VON` nào — và đó KHÔNG phải 0. Một tờ
    đứng `DA_MO` mà sổ cái không có dòng cấp vốn nào là chuyện đáng báo
    động hơn hẳn một tờ được cấp 0 đồng; trả 0 ở đây là dìm nó vào giữa
    những con số bình thường.
    """
    if so_cai is None:
        return None
    try:
        dong = so_cai.theo_to_trinh(ma)
    except Exception:                                       # noqa: BLE001
        return None
    cap = [d for d in dong if d.get("loai") == "CAP_VON"]
    if not cap:
        return None
    return sum(float(d.get("soTienUsd") or 0.0) for d in cap)


def _so(v) -> float | None:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None
