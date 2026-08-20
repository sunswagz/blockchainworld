"""Đài Chiêm — tính ra outcome ĐÁNG LẼ đáng giá bao nhiêu, độc lập với giá chợ.

Đây là chỗ phân biệt một *predictor* với một *quant trader*. Predictor hỏi
"42c có rẻ không?". Quant trader không hỏi câu đó — nó tự tính ra con số của
mình rồi mới nhìn sang chợ.

## Mô hình

Với market "giá X sau τ giây có cao hơn lúc mở không", coi log-giá là bước
ngẫu nhiên không xu hướng (giả định martingale — đúng với một thị trường
hiệu quả, và là giả định BẢO THỦ nhất vì nó không cho mô hình mượn một niềm
tin về hướng đi mà nó không có bằng chứng):

        z = [ln(S/K) - (sigma^2 * tau)/2] / (sigma * sqrt(tau))
        P(UP) = Phi(z)

    S     giá hiện tại
    K     giá lúc mở market (strike)
    tau   số giây còn lại
    sigma độ lệch chuẩn log-return MỖI GIÂY
    Phi   hàm phân phối tích luỹ chuẩn

Số hạng `-(sigma^2 * tau)/2` là hiệu chỉnh Ito. Ở khung 5 phút nó cực nhỏ —
cỡ 1e-6, tức khoảng 0,2% của tín hiệu ln(S/K) khi giá đã dịch 0,1%. Giữ lại
vì nó đúng, và vì bỏ đi thì người sau sẽ tưởng công thức này là Bachelier
chứ không phải GBM rồi hiệu chỉnh sai chỗ khác.

## Bốn cái bẫy, cả bốn đều hỏng im lặng

1. **tau tiến về 0 làm nổ mẫu số.** Còn 0,3 giây thì `sigma*sqrt(tau)` gần
   bằng 0, z nhảy ra vô cực, và P(UP) thành đúng 0 hoặc đúng 1. Mô hình khi
   đó tuyên bố "chắc chắn 100%" đúng vào lúc nó biết ít nhất, vì một tick
   cuối cùng vẫn lật được kết quả. Chặn bằng `sanNenGiay` VÀ bằng
   `matPhangCanKetQua` — hai lớp, vì lớp một chỉ chặn mẫu số còn lớp hai
   chặn cả kết quả.

2. **sigma ước lượng từ quá khứ, dùng cho tương lai.** Cửa sổ 300 giây trong
   một cú sập thì sigma đo được vẫn là sigma của lúc bình yên. Nên
   `batDinh` (uncertainty) phải đi kèm P, và Risk Engine trừ nó vào edge chứ
   không được coi P là con số chắc chắn.

3. **Năm dấu hiệu của cùng một nguyên nhân bị đếm thành năm bằng chứng.**
   BTC bật lên thì volume tăng, bid imbalance tăng, ETH tăng, SOL tăng, taker
   flow tăng — nhìn như năm xác nhận độc lập, thực ra là năm cái bóng của một
   cú. Cộng chúng như bằng chứng độc lập là thổi phồng xác suất. Xem
   `TinMoi` bên dưới.

4. **P chưa hiệu chỉnh mà đem cho Kelly là khuếch đại chính sai lầm.** Mô
   hình nói 60% mà thực tế những lần nói 60% chỉ thắng 52% thì Kelly phóng to
   đúng khoảng lệch đó. Nên `HieuChinh` phải đủ mẫu trước khi ai được phép
   dùng Kelly — xem `rui_ro.py`.
"""
from __future__ import annotations

import json
import math
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path

from .config import CONFIG, DATA_DIR

_DG = CONFIG["dinhGia"]


def phi(z: float) -> float:
    """Hàm phân phối tích luỹ chuẩn, viết bằng erf của thư viện chuẩn."""
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


# ══════════════════════════════════════════════════════════════════════════
#  NGUỒN GỐC TÍN HIỆU — chống đếm trùng bằng chứng
# ══════════════════════════════════════════════════════════════════════════

# Mỗi tín hiệu thuộc một HỌ. Trong cùng một họ, các tín hiệu gần như là biến
# thể của nhau, nên chỉ tín hiệu MẠNH NHẤT trong họ được tính trọn vẹn; phần
# còn lại bị chiết khấu nặng. Giữa các họ mới được cộng gần như độc lập.
HO_TIN_HIEU = {
    "btc_return":      "gia",
    "btc_momentum":    "gia",
    "btc_gia_lech":    "gia",
    "taker_flow":      "dong_lenh",
    "cex_imbalance":   "dong_lenh",
    "poly_lech":       "so_poly",
    "poly_vi_gia":     "so_poly",
    "eth_theo":        "cheo_tai_san",
    "sol_theo":        "cheo_tai_san",
}

# Trong cùng họ, tín hiệu thứ hai trở đi chỉ còn ngần này trọng số. Không đặt
# 0 vì hai phép đo cùng họ vẫn có chút thông tin riêng (nhiễu đo độc lập);
# không đặt 1 vì đó chính là cái bẫy số 3.
CHIET_KHAU_CUNG_HO = 0.25


@dataclass
class TinMoi:
    """Gộp nhiều tín hiệu thành một hệ số điều chỉnh, có trừ phần trùng lặp."""

    def gop(self, tinHieu: dict[str, float]) -> tuple[float, dict]:
        """Trả (tổng tín hiệu đã chiết khấu, bảng giải trình).

        Bảng giải trình quan trọng ngang kết quả: không có nó thì sáu tháng
        nữa không ai truy được vì sao một lệnh được vào.
        """
        theo_ho: dict[str, list[tuple[str, float]]] = {}
        for ten, gt in tinHieu.items():
            if gt is None or not math.isfinite(gt) or gt == 0:
                continue
            theo_ho.setdefault(HO_TIN_HIEU.get(ten, ten), []).append((ten, gt))

        tong = 0.0
        giai_trinh: list[dict] = []
        for ho, ds in theo_ho.items():
            # mạnh nhất trước, tính theo trị tuyệt đối
            ds.sort(key=lambda x: abs(x[1]), reverse=True)
            for i, (ten, gt) in enumerate(ds):
                w = 1.0 if i == 0 else CHIET_KHAU_CUNG_HO
                tong += gt * w
                giai_trinh.append({"ten": ten, "ho": ho, "tho": gt,
                                   "trongSo": w, "gop": gt * w})
        return tong, {"tong": tong, "soHo": len(theo_ho), "chiTiet": giai_trinh}


# ══════════════════════════════════════════════════════════════════════════
#  ĐO ĐỘ BIẾN ĐỘNG
# ══════════════════════════════════════════════════════════════════════════

@dataclass
class DoBienDong:
    """Ước lượng sigma mỗi giây từ một cửa sổ trượt các mẫu giá.

    Dùng log-return chuẩn hoá theo căn bậc hai của khoảng cách thời gian, vì
    các mẫu tới KHÔNG đều nhau — WebSocket đẩy khi có giao dịch, không phải
    theo nhịp. Chia cho `sqrt(dt)` là cách quy mọi mẫu về cùng một đơn vị
    "mỗi giây"; bỏ bước đó thì lúc chợ sôi động (mẫu dày, dt nhỏ) sigma đo
    được sẽ TỤT xuống thay vì tăng lên, tức là sai đúng chiều nguy hiểm nhất.
    """
    cuaSoGiay: float = float(_DG["bienDongCuaSoGiay"])
    _mau: deque = field(default_factory=lambda: deque(maxlen=4000))

    def them(self, gia: float, lucMs: float) -> None:
        if gia is None or gia <= 0 or not math.isfinite(gia):
            return
        self._mau.append((lucMs, gia))
        han = lucMs - self.cuaSoGiay * 1000.0
        while len(self._mau) > 2 and self._mau[0][0] < han:
            self._mau.popleft()

    @property
    def so_mau(self) -> int:
        return len(self._mau)

    def sigma_giay(self) -> float | None:
        """Độ lệch chuẩn log-return quy về mỗi giây. None nếu chưa đủ mẫu."""
        if len(self._mau) < 12:
            return None
        r: list[float] = []
        for (t0, p0), (t1, p1) in zip(self._mau, list(self._mau)[1:]):
            dt = (t1 - t0) / 1000.0
            if dt <= 1e-6 or p0 <= 0 or p1 <= 0:
                continue
            r.append(math.log(p1 / p0) / math.sqrt(dt))
        if len(r) < 8:
            return None
        tb = sum(r) / len(r)
        var = sum((x - tb) ** 2 for x in r) / (len(r) - 1)
        s = math.sqrt(max(0.0, var))
        return s if s > 0 else None


# ══════════════════════════════════════════════════════════════════════════
#  KẾT QUẢ ĐỊNH GIÁ
# ══════════════════════════════════════════════════════════════════════════

@dataclass
class GiaChuan:
    ma: str
    pUp: float
    pDown: float
    batDinh: float          # tổng bất định = tham số + nhảy giá
    batDinhThamSo: float    # phần do sigma ước lượng có thể lệch
    ruiRoNhay: float        # phần do một cú nhảy có thể lật kết quả
    z: float
    sigmaGiay: float
    tauGiay: float
    tauDungSan: bool        # tau đã bị kẹp về sàn chưa
    daMatPhang: bool        # kết quả đã bị kéo khỏi 0/1 chưa
    giaHienTai: float
    giaMo: float
    oHieuChinh: str
    giaiTrinh: dict = field(default_factory=dict)

    @property
    def ro_rang(self) -> bool:
        """Mô hình có đang nói gì đáng nghe không.

        Bất định lớn hơn khoảng cách tới 50% nghĩa là mô hình đang nói "tôi
        không biết" bằng một con số trông như đang biết.
        """
        return abs(self.pUp - 0.5) > self.batDinh


def dinh_gia(
    ma: str,
    giaHienTai: float,
    giaMo: float,
    tauGiay: float,
    sigmaGiay: float | None,
    tinHieu: dict[str, float] | None = None,
) -> GiaChuan | None:
    """Tính P(UP). None khi thiếu nguyên liệu — KHÔNG bịa ra 0.5.

    Trả None chứ không trả 0.5 là có chủ ý: 0.5 trông như một câu trả lời và
    sẽ lặng lẽ chảy vào phép tính edge, còn None thì buộc chỗ gọi phải xử lý.
    """
    if not all(math.isfinite(x or 0) for x in (giaHienTai, giaMo, tauGiay)):
        return None
    if giaHienTai <= 0 or giaMo <= 0 or sigmaGiay is None or sigmaGiay <= 0:
        return None

    # ── bẫy 1, lớp một: sàn cho tau ───────────────────────────────────────
    san = float(_DG["sanNenGiay"])
    tau_that = max(0.0, float(tauGiay))
    tau = max(san, tau_that)
    dung_san = tau_that < san

    sig_tau = sigmaGiay * math.sqrt(tau)
    if sig_tau <= 0:
        return None

    z = (math.log(giaHienTai / giaMo) - 0.5 * sigmaGiay ** 2 * tau) / sig_tau

    # ── bẫy 3: gộp tín hiệu phụ, đã trừ phần trùng lặp ────────────────────
    giai_trinh: dict = {}
    if tinHieu:
        them, giai_trinh = TinMoi().gop(tinHieu)
        # Tín hiệu phụ chỉ được dịch z một lượng NHỎ và có trần. Chúng là
        # thông tin về vi cấu trúc, không phải về giá — cho chúng quyền dịch
        # z bao nhiêu tuỳ ý là để đuôi vẫy chó.
        z += max(-0.75, min(0.75, them))

    p_up = phi(z)

    # ── bẫy 1, lớp hai: làm phẳng ở cận kết quả ───────────────────────────
    # Ngay sát resolution, một tick vẫn lật được kết quả, nên không outcome
    # nào đáng giá đúng 0 hay đúng 1. Kéo về trong [eps, 1-eps].
    eps = float(_DG["matPhangCanKetQua"])
    da_phang = p_up < eps or p_up > 1.0 - eps
    p_up = min(1.0 - eps, max(eps, p_up))

    # ── bẫy 2: bất định phải đi kèm, không được rơi rớt ───────────────────
    bat_dinh = _bat_dinh(z, sigmaGiay, tau, tau_that)
    nhay = _rui_ro_nhay(z, tau)

    return GiaChuan(
        ma=ma, pUp=p_up, pDown=1.0 - p_up,
        batDinh=min(0.5, bat_dinh + nhay), batDinhThamSo=bat_dinh, ruiRoNhay=nhay,
        z=z, sigmaGiay=sigmaGiay, tauGiay=tau_that, tauDungSan=dung_san,
        daMatPhang=da_phang, giaHienTai=giaHienTai, giaMo=giaMo,
        oHieuChinh=o_hieu_chinh(p_up), giaiTrinh=giai_trinh,
    )


def _rui_ro_nhay(z: float, tau: float) -> float:
    """Bất định RIÊNG của binary ngắn hạn: một cú nhảy lật được kết quả.

    `_bat_dinh` ở trên chỉ đo sai số THAM SỐ — sigma ước lượng có thể lệch.
    Nó không đo được thứ nguy hiểm nhất của một hợp đồng 5 phút, và bản đầu
    tiên của module này vì thế cho ra một bảng nói ngược sự thật: bất định
    TỤT dần khi tới gần kết quả, vì trong đuôi phân phối thì mật độ phi(z)
    nhỏ nên đạo hàm theo sigma cũng nhỏ.

    Sự thật là: gần kết quả, cái quyết định không còn là sigma ước lượng
    đúng hay sai, mà là GIÁ ĐANG CÁCH LẰN RANH BAO XA so với thứ một cú
    nhảy đơn lẻ dịch được. Đo bằng đúng câu đó:

        dz  =  sqrt(buocNhayGiay / tau)      một cú nhảy dịch z bao nhiêu
        nhay = phi_mat_do(z) * dz            dịch z ngần ấy thì P đổi bao nhiêu

    Công thức này tự phân biệt được hai tình huống mà một hằng số không phân
    biệt nổi, và đó là lý do chọn nó:

      · z ~ 0, còn 3 giây  ->  phi(0)=0.399, dz=0.577  ->  bất định ~0.23.
        Đúng: giá đang nằm ngay lằn ranh thì đó là tung đồng xu, bất kể mô
        hình khuếch tán nói gì. Đây chính là cú "UP 95c -> 5c" trong tài liệu.

      · z ~ 3, còn 3 giây  ->  phi(3)=0.004, dz=0.577  ->  bất định ~0.003.
        Cũng đúng: cách lằn ranh 3 sigma với 3 giây còn lại thì một cú nhảy
        cỡ một giây không với tới. Vị thế này thật sự an toàn, và phạt nó
        cũng chỉ làm hệ thống bỏ lỡ đúng những chỗ nó nên vào.
    """
    buoc = float(_DG.get("buocNhayGiay", 1.0))
    dz = math.sqrt(max(1e-9, buoc) / max(1e-9, tau))
    mat_do = math.exp(-0.5 * z * z) / math.sqrt(2.0 * math.pi)
    return min(0.5, mat_do * dz)


def _bat_dinh(z: float, sigmaGiay: float, tau: float, tauThat: float) -> float:
    """Sai số chuẩn của P(UP), lan truyền từ sai số của sigma.

    Nguồn bất định lớn nhất không phải giá — giá thì đo được — mà là sigma.
    Với n mẫu, sai số tương đối của độ lệch chuẩn cỡ `1/sqrt(2n)`. Ở đây lấy
    thẳng một mức thận trọng 20%, rồi lan qua đạo hàm:

        dP/dsigma = phi_mat_do(z) * (-z/sigma)

    Cộng thêm một sàn, và cộng thêm phạt khi tau đã phải kẹp — lúc đó mô
    hình đang ngoại suy ra ngoài vùng nó còn ý nghĩa.
    """
    mat_do = math.exp(-0.5 * z * z) / math.sqrt(2.0 * math.pi)
    sai_sigma = 0.20
    lan = abs(mat_do * z) * sai_sigma
    san = float(_DG["batDinhToiThieu"])
    phat = 0.0
    if tauThat < tau:
        # càng ngoại suy sâu càng phạt nặng; tối đa gấp đôi sàn
        phat = san * min(2.0, (tau - tauThat) / max(1e-9, tau))
    return min(0.5, san + lan + phat)


# ══════════════════════════════════════════════════════════════════════════
#  HIỆU CHỈNH — mô hình nói 60% thì thực tế thắng bao nhiêu phần trăm
# ══════════════════════════════════════════════════════════════════════════

O_HIEU_CHINH = [(0.0, 0.1), (0.1, 0.2), (0.2, 0.3), (0.3, 0.4), (0.4, 0.5),
                (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 0.9), (0.9, 1.0)]


def o_hieu_chinh(p: float) -> str:
    for lo, hi in O_HIEU_CHINH:
        if lo <= p < hi:
            return f"{int(lo*100)}-{int(hi*100)}"
    return "90-100"


class HieuChinh:
    """Sổ đối chiếu: mô hình đoán bao nhiêu, thực tế ra sao.

    Đây là thứ đứng TRƯỚC Kelly. Không có nó thì `kichThuoc()` đang nhân một
    con số chưa ai kiểm với vốn thật.
    """

    def __init__(self, duong: Path | None = None) -> None:
        self.duong = duong or (DATA_DIR / "hieu-chinh.json")
        self.o: dict[str, dict] = {}
        self._doc()

    def _doc(self) -> None:
        if self.duong.exists():
            try:
                self.o = json.loads(self.duong.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                self.o = {}

    def ghi(self) -> None:
        self.duong.parent.mkdir(parents=True, exist_ok=True)
        self.duong.write_text(json.dumps(self.o, ensure_ascii=False, indent=2),
                              encoding="utf-8")

    def them(self, pDuDoan: float, thangThat: bool) -> None:
        o = o_hieu_chinh(pDuDoan)
        d = self.o.setdefault(o, {"n": 0, "thang": 0, "tongP": 0.0})
        d["n"] += 1
        d["thang"] += 1 if thangThat else 0
        d["tongP"] += pDuDoan

    def bang(self) -> list[dict]:
        ra = []
        for lo, hi in O_HIEU_CHINH:
            ten = f"{int(lo*100)}-{int(hi*100)}"
            d = self.o.get(ten)
            if not d or d["n"] <= 0:
                ra.append({"o": ten, "n": 0, "duDoan": None, "thucTe": None, "lech": None})
                continue
            du = d["tongP"] / d["n"]
            that = d["thang"] / d["n"]
            ra.append({"o": ten, "n": d["n"], "duDoan": du, "thucTe": that,
                       "lech": that - du})
        return ra

    @property
    def tong_mau(self) -> int:
        return sum(d.get("n", 0) for d in self.o.values())

    def du_de_dung_kelly(self) -> bool:
        """Kelly bị khoá cho tới khi có đủ mẫu đã đối chiếu.

        Không có cửa này thì hệ thống lấy một xác suất chưa ai kiểm nhân với
        vốn thật — và càng tự tin sai thì càng đặt to.
        """
        return self.tong_mau >= int(_DG["toiThieuMauHieuChinh"])

    def sai_so_tuyet_doi_tb(self) -> float | None:
        """Trung bình |thực tế - dự đoán| theo trọng số mẫu. None nếu chưa có."""
        tong_n = 0
        tich = 0.0
        for h in self.bang():
            if h["n"] and h["lech"] is not None:
                tong_n += h["n"]
                tich += abs(h["lech"]) * h["n"]
        return (tich / tong_n) if tong_n else None
