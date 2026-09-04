"""SỔ LUẬT — «lúc nào nên làm thế này, lúc nào nên làm thế kia», CHẠY ĐƯỢC.

Mỗi luật là một `Luat` có hàm `khop(bc)` đọc BỐI CẢNH và trả `True/False`,
kèm hành động nó gợi và câu vì sao. Bối cảnh là một dict phẳng (xem
`BoiCanh`), nên luật kiểm được ở selftest mà không cần mạng, không cần pool.

## Bảy hành động

    CHO        chưa đủ số để quyết — nói rõ thiếu gì
    VAO        thêm thanh khoản ở dải đề xuất
    GIU        đang giữ, để yên
    NOI_RONG   rút rồi vào lại dải rộng hơn
    THU_HEP    rút rồi vào lại dải hẹp hơn
    DOI_DAI    giá đã ra ngoài dải, vào lại quanh giá mới
    RUT        rút hẳn

## Luật thắng luật thế nào

Luật CHẶN (`chan=True`) thắng mọi luật mở: một luật chặn khớp là hành động
cuối cùng KHÔNG thể là VAO / THU_HEP / DOI_DAI. Trong các luật còn lại,
luật đứng trước trong `SO_LUAT` thắng. Thứ tự là quyết định thiết kế và
có phép kiểm canh: luật «không σ» phải đứng đầu, luật «giữ» đứng cuối.

Mỗi luật mang trường `vi` — chuyện đã xảy ra hoặc phép đo dạy ra nó. Luật
không có `vi` là luật phòng xa, và sổ này không nhận luật phòng xa.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .lich import CUOI_TUAN, MO_CUA, SAU_DONG, TRUOC_MO

CHO, VAO, GIU, NOI_RONG, THU_HEP, DOI_DAI, RUT = (
    "CHO", "VAO", "GIU", "NOI_RONG", "THU_HEP", "DOI_DAI", "RUT")
HANH_DONG = (CHO, VAO, GIU, NOI_RONG, THU_HEP, DOI_DAI, RUT)
HANH_DONG_MO = (VAO, THU_HEP, DOI_DAI)


@dataclass
class BoiCanh:
    """Mọi thứ luật được phép nhìn. Phẳng, có chủ ý — luật đọc dict lồng
    nhau là luật khó kiểm."""
    kyHieu: str = ""
    dangGiu: bool = False
    trangThaiPhien: str = CUOI_TUAN
    coSigma: bool = False
    soPhienSigma: int = 0
    sigma: float | None = None
    giaTuoiGiay: float | None = None
    tuoiGiaToiDaGiay: float = 21_600.0
    trongDai: bool | None = None          # None khi không có vị thế
    xacSuatVang: float | None = None
    tiLePhiTrenLvr: float | None = None
    netBps: float | None = None
    gioToiSuKien: float | None = None     # sự kiện GẦN NHẤT ảnh hưởng mã này
    tenSuKien: str = ""
    gioToiHetThuong: float | None = None
    thuongChiemPhanLon: bool = False      # thưởng > phí gốc
    tvlUsd: float | None = None
    lechGiaChuoiSoGocPct: float | None = None   # |giá chuỗi/giá đóng cửa − 1|
    nut: dict = field(default_factory=dict)
    cua: dict = field(default_factory=dict)

    def n(self, k, macDinh):
        return float(self.nut.get(k, macDinh))

    def c(self, k, macDinh):
        v = self.cua.get(k, macDinh)
        return v


@dataclass(frozen=True)
class Luat:
    ma: str
    cau: str
    vi: str
    hanhDong: str
    khop: object                 # (BoiCanh) -> bool
    chan: bool = False           # luật chặn: cấm mọi hành động MỞ
    lyDo: object = None          # (BoiCanh) -> str, mặc định = cau


def _ly(bc, l: Luat) -> str:
    try:
        return l.lyDo(bc) if l.lyDo else l.cau
    except Exception:                                         # noqa: BLE001
        return l.cau


SO_LUAT = (
    Luat("khong-sigma",
         "không đo được σ thì không định giá được IL — CHỜ, và nói thiếu gì",
         "lp_amm/ từ chối 11.276 pool vì đúng chuyện này; ty này chỉ khác ở "
         "chỗ có σ. Bỏ luật này là quay về đoán.",
         CHO, lambda bc: bool(bc.c("doiHoiSigma", True)) and not bc.coSigma,
         chan=True,
         lyDo=lambda bc: (f"σ chưa đo được: có {bc.soPhienSigma} phiên, cần "
                          f"≥ {int(bc.c('soPhienToiThieuChoSigma', 10))} — "
                          f"chưa có sàn gốc hoặc băng giá chưa đủ dày")),
    Luat("gia-cu",
         "giá cũ hơn trần thì mọi con số trên nó là của quá khứ — CHỜ",
         "cùng luật tuoiToiDaGiay của ty perp: một cửa rủi ro chạy trên báo "
         "giá cũ là cửa không chặn gì",
         CHO, lambda bc: (bc.giaTuoiGiay is not None
                          and bc.giaTuoiGiay > bc.tuoiGiaToiDaGiay),
         chan=True,
         lyDo=lambda bc: f"giá đã {bc.giaTuoiGiay / 3600:.1f} giờ tuổi > trần "
                         f"{bc.tuoiGiaToiDaGiay / 3600:.0f} giờ"),
    Luat("sat-su-kien",
         "trong N giờ trước FOMC / kết quả kinh doanh: KHÔNG vào, không đổi "
         "dải; đang giữ dải hẹp thì NỚI hoặc RÚT trước giờ ấy",
         "σ đo từ ngày thường không mô tả đêm công bố kết quả — cú nhảy "
         "10–20% một đêm văng mọi dải hẹp và IL thành hiện thực ngay",
         NOI_RONG,
         lambda bc: (bc.gioToiSuKien is not None
                     and bc.gioToiSuKien <= bc.n("gioTruocSuKien", 24.0)),
         chan=True,
         lyDo=lambda bc: f"{bc.tenSuKien or 'sự kiện'} còn "
                         f"{bc.gioToiSuKien:.0f} giờ ≤ "
                         f"{bc.n('gioTruocSuKien', 24.0):.0f} giờ"),
    Luat("gap-mo-cua",
         "giá chuỗi lệch giá đóng cửa gốc quá 1,5% lúc SẮP mở: không vào, "
         "chờ 30 phút sau mở để arb «bắt kịp» xong",
         "cú bắt kịp lúc mở cửa là LVR dồn vào một khoảnh khắc — LP đứng "
         "đó là bên bán rẻ hoặc mua đắt cho arbitrageur",
         CHO,
         lambda bc: (bc.trangThaiPhien == TRUOC_MO
                     and bc.lechGiaChuoiSoGocPct is not None
                     and bc.lechGiaChuoiSoGocPct > 1.5),
         chan=True,
         lyDo=lambda bc: f"giá chuỗi lệch {bc.lechGiaChuoiSoGocPct:.2f}% so "
                         f"với giá gốc, sàn Mỹ sắp mở"),
    Luat("ngoai-gio-khong-doi-dai",
         "sàn Mỹ đóng: KHÔNG vào mới, không đổi dải — thanh khoản mỏng, "
         "giá chuỗi không phải giá",
         "τ theo ngày giao dịch bằng 0 qua cuối tuần nên mọi P(văng) và "
         "IL đều ra 0 — con số ấy chỉ đúng với phần cổ phiếu, còn phần "
         "trôi trên chuỗi thì chưa đo, và đổi dải lúc này là trả spread "
         "cho một cái giá không ai bảo đảm",
         GIU,
         lambda bc: (bool(bc.c("khongDoiDaiNgoaiGio", True))
                     and bc.trangThaiPhien in (CUOI_TUAN, SAU_DONG)),
         chan=True,
         lyDo=lambda bc: f"phiên đang {bc.trangThaiPhien}: đợi sàn Mỹ mở"),
    Luat("tvl-mong",
         "TVL dưới sàn: pool là ta, và ra không có ai mua",
         "SMCIx-USDG $14.810 TVL: rót $5.000 là chiếm một phần ba pool, và "
         "muốn rút thì chính mình là thanh khoản cho lệnh rút của mình",
         CHO,
         lambda bc: bc.tvlUsd is not None and bc.tvlUsd < float(
             bc.c("tvlToiThieuUsd", 5_000.0)),
         chan=True,
         lyDo=lambda bc: f"TVL ${bc.tvlUsd:,.0f} < sàn "
                         f"${float(bc.c('tvlToiThieuUsd', 5000)):,.0f}"),
    Luat("ngoai-dai",
         "giá ra ngoài dải: vị thế đông cứng, không thu phí — DOI_DAI khi "
         "phí/LVR còn tốt, RUT khi không",
         "một vị thế ngoài dải là 100% một token và 0 phí; giữ nó là giữ "
         "một vị thế giao ngay ngoài ý muốn, không phải LP",
         DOI_DAI,
         lambda bc: bc.dangGiu and bc.trongDai is False),
    Luat("phi-duoi-lvr",
         "(phí + thưởng)/LVR dưới ngưỡng: không VÀO; đang giữ thì RÚT",
         "LP có lãi khi và chỉ khi phí thu vượt σ²/8 × hiệu suất — đây là "
         "định lý, không phải ngưỡng chọn tay; ngưỡng chỉ là biên an toàn",
         RUT,
         lambda bc: (bc.tiLePhiTrenLvr is not None
                     and bc.tiLePhiTrenLvr < bc.n("tiLePhiTrenLvrToiThieu", 1.5)),
         chan=True,
         lyDo=lambda bc: f"phí/LVR {bc.tiLePhiTrenLvr:.2f} < "
                         f"{bc.n('tiLePhiTrenLvrToiThieu', 1.5):.2f}"),
    Luat("sap-het-thuong",
         "thưởng chiếm phần lớn và còn dưới 24 giờ: đừng VÀO mới; đang giữ "
         "thì lên lịch RÚT đúng giờ hết nếu phí gốc không đủ",
         "OKX 07/09/2026 14:00: sau giờ ấy APY 268% về đúng phí gốc, mà phí "
         "gốc chưa tách được — vào lúc này là mua một con số sắp biến mất",
         GIU,
         lambda bc: (bc.thuongChiemPhanLon and bc.gioToiHetThuong is not None
                     and 0 <= bc.gioToiHetThuong <= 24.0),
         chan=True,
         lyDo=lambda bc: f"thưởng hết sau {bc.gioToiHetThuong:.0f} giờ và "
                         f"đang là phần lớn lợi suất"),
    Luat("van-dai-cao",
         "P(văng) trong cửa sổ trên trần: NỚI dải",
         "dải ±5% NVDA σ 50% có P(văng) ≈ 55% trong 2 phiên — hơn nửa số "
         "lần vào là ra tay không kèm IL đã hiện thực",
         NOI_RONG,
         lambda bc: (bc.xacSuatVang is not None
                     and bc.xacSuatVang > bc.n("xacSuatVangToiDa", 0.6)),
         lyDo=lambda bc: f"P(văng) {bc.xacSuatVang:.0%} > trần "
                         f"{bc.n('xacSuatVangToiDa', 0.6):.0%}"),
    Luat("dai-qua-rong",
         "P(văng) rất thấp và phí/LVR rất cao: THU HẸP để ăn hiệu suất",
         "hiệu suất nhân cả phí lẫn LVR; khi phí/LVR ≥ 3 thì mỗi nấc hẹp "
         "hơn là thêm lãi ròng, còn khi ≈ 1,5 thì chỉ thêm rủi ro",
         THU_HEP,
         lambda bc: (bc.dangGiu and bc.xacSuatVang is not None
                     and bc.xacSuatVang < 0.15
                     and bc.tiLePhiTrenLvr is not None
                     and bc.tiLePhiTrenLvr >= 3.0)),
    Luat("vao-duoc",
         "đủ σ, phiên mở, không sự kiện, phí/LVR đủ, P(văng) trong trần: VÀO",
         "đây là luật mở duy nhất, và nó chỉ chạy được khi mọi luật chặn "
         "im — nên nó không cần tự kiểm lại gì",
         VAO,
         lambda bc: (not bc.dangGiu and bc.coSigma
                     and bc.tiLePhiTrenLvr is not None
                     and bc.netBps is not None and bc.netBps > 0)),
    Luat("giu",
         "đang giữ, trong dải, không luật nào kêu: GIỮ",
         "đổi vị thế lúc chụp ngẫu nhiên là mất thưởng giờ ấy — đứng yên "
         "có giá của nó, và giá ấy dương",
         GIU, lambda bc: bc.dangGiu and bc.trongDai is not False),
    Luat("chua-du-so",
         "không luật nào khớp: CHỜ và khai thiếu gì",
         "một máy quyết định im lặng khi thiếu số là máy đang đoán",
         CHO, lambda bc: True),
)

MA_LUAT = tuple(l.ma for l in SO_LUAT)


@dataclass(frozen=True)
class QuyetDinh:
    hanhDong: str
    luatQuyet: str
    lyDo: str
    luatKhop: tuple                # (ma, hanhDong, lyDo) mọi luật khớp
    biChan: bool

    def tom_tat(self) -> dict:
        return {"hanhDong": self.hanhDong, "luatQuyet": self.luatQuyet,
                "lyDo": self.lyDo,
                "luatKhop": [{"ma": a, "hanhDong": b, "lyDo": c}
                             for a, b, c in self.luatKhop],
                "biChan": self.biChan}


def quyet(bc: BoiCanh) -> QuyetDinh:
    """Chạy cả sổ luật. Luật chặn thắng luật mở; trong cùng nhóm thì luật
    đứng trước thắng."""
    khop = []
    for l in SO_LUAT:
        try:
            if l.khop(bc):
                khop.append((l, _ly(bc, l)))
        except Exception as e:                                # noqa: BLE001
            khop.append((l, f"luật lỗi: {type(e).__name__}: {e}"))
    chan = [x for x in khop if x[0].chan]
    if chan:
        l, ly = chan[0]
        hd = l.hanhDong
        # Luật chặn đề xuất một hành động ĐÓNG (RUT/NOI_RONG/GIU/CHO). Nếu
        # không đang giữ thì mọi hành động đóng đều quy về CHO.
        if not bc.dangGiu and hd in (RUT, NOI_RONG, GIU, DOI_DAI):
            hd = CHO
        elif bc.dangGiu and hd == CHO:
            # Đang giữ mà «chờ» nghĩa là ĐỪNG ĐỘNG — với người cầm vị thế,
            # câu ấy tên là GIỮ.
            hd = GIU
        return QuyetDinh(hd, l.ma, ly,
                         tuple((a.ma, a.hanhDong, b) for a, b in khop), True)
    l, ly = khop[0]
    hd = l.hanhDong
    if not bc.dangGiu and hd in (RUT, NOI_RONG, THU_HEP, GIU, DOI_DAI):
        # Không có vị thế thì không có gì để rút, nới hay giữ: luật ấy
        # đang nói về DẢI ĐỀ XUẤT, và câu trả lời đúng là «chưa vào».
        hd = CHO
    return QuyetDinh(hd, l.ma, ly,
                     tuple((a.ma, a.hanhDong, b) for a, b in khop), False)
