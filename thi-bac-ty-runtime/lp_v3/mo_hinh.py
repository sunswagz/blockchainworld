"""Toán của một vị thế Uniswap V3 — KHÔNG mạng, KHÔNG ngẫu nhiên.

Mọi con số ty này trình lên đều đi qua đây, và mọi hàm ở đây đều kiểm được
bằng tay với một máy tính bỏ túi. Đó là chủ ý: `lp_amm/` từ chối cặp biến
động vì «IL không đo được từ một ảnh chụp». Đúng — nhưng IL đo được từ một
ảnh chụp CỘNG một σ. File này là phần «cộng một σ».

## Ký hiệu

    P         giá token0 tính bằng token1 (NVDAx tính bằng USDG)
    Pa, Pb    hai mép dải, Pa < P < Pb khi đang trong dải
    L         thanh khoản của vị thế (đơn vị Uniswap)
    D         đô la rót vào lúc mở
    σ         biến động NĂM của log-giá (0,50 = 50%/năm)
    τ         chân trời, tính bằng NĂM GIAO DỊCH (ngày giao dịch / 252)

## Ba lời thật phải nói kèm mọi con số ở đây

1. **Hiệu suất vốn** so với dải toàn phần là `1/(1 − (Pa/Pb)^¼)`. Nó khuếch
   đại CẢ phí LẪN LVR cùng một hệ số — nên thu hẹp dải không làm tỉ lệ
   phí/LVR khá lên, nó chỉ làm cả hai to lên. Cái quyết định lời hay lỗ là
   phí của POOL so với σ²/8, và dải chỉ chọn CỠ của ván cược.

2. **Xác suất văng dải là CẬN TRÊN.** Cộng xác suất chạm mép trên với chạm
   mép dưới thì đường đi chạm cả hai bị đếm hai lần. Sai theo hướng thận
   trọng, và khai rõ là cận trên.

3. **Trôi `−σ²τ/2` KHÔNG được bỏ.** Khâm Thiên Giám từng bỏ số hạng này
   với lý lẽ «không giả định xu hướng» và định giá sai ~40% ở chân trời
   dài. Nó là hiệu chỉnh để chính GIÁ là martingale, không phải một dự báo.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

#: Số ngày giao dịch một năm của thị trường cổ phiếu Mỹ. Token cổ phiếu
#: giao dịch 24/7 trên chuỗi, nhưng GIÁ của nó chỉ được «khám phá» khi sàn
#: gốc mở — ngoài giờ nó trôi trên thanh khoản mỏng. Nên σ đo từ giá đóng
#: cửa hằng ngày và τ đếm theo NGÀY GIAO DỊCH, không theo ngày lịch.
NGAY_GIAO_DICH_NAM = 252.0

GIO_NAM = 365.0 * 24.0


# ── phân phối chuẩn ─────────────────────────────────────────────────────

def phi_chuan(z: float) -> float:
    """Φ(z) — hàm phân phối tích luỹ chuẩn, bằng `erfc` cho đuôi chính xác."""
    return 0.5 * math.erfc(-z / math.sqrt(2.0))


# ── tick ↔ giá ───────────────────────────────────────────────────────────

def tick_tu_gia(p: float) -> int:
    """Tick GẦN NHẤT dưới giá `p`. `p = 1.0001^tick`."""
    if not (p > 0):
        raise ValueError(f"giá phải > 0, đang là {p}")
    return int(math.floor(math.log(p) / math.log(1.0001)))


def gia_tu_tick(t: int) -> float:
    return 1.0001 ** t


def lam_tron_tick(t: int, khoangTick: int) -> int:
    """Tick hợp lệ của một mức phí: 0,05% → 10 · 0,3% → 60 · 1% → 200."""
    return int(math.floor(t / khoangTick)) * khoangTick


KHOANG_TICK = {1: 1, 5: 10, 30: 60, 100: 200}     # phí bps → khoảng tick


def dai_theo_tick(Pa: float, Pb: float, phiBps: float,
                  thapPhan0: int, thapPhan1: int) -> tuple[float, float]:
    """Kéo hai mép về tick HỢP LỆ của mức phí: mép dưới xuống, mép trên
    lên — dải chỉ rộng ra, không hẹp lại.

    Tick sống trên giá THÔ (token1 thô / token0 thô), nên phải đổi thập
    phân trước rồi đổi lại. Không biết thập phân thì đừng gọi: kéo tick
    trên giá người là kéo về một lưới KHÔNG tồn tại trên chuỗi.
    """
    kt = KHOANG_TICK.get(int(round(phiBps)), 1)
    he = 10 ** (thapPhan1 - thapPhan0)
    ta = lam_tron_tick(tick_tu_gia(Pa * he), kt)
    tb = lam_tron_tick(tick_tu_gia(Pb * he), kt)
    # Dung sai TƯƠNG ĐỐI: giá thô cỡ 1e-10 (thập phân 18/6) thì 1e-12 tuyệt
    # đối là 1% — mép trên từng bị KÉO XUỐNG vì thế, và phép kiểm bắt được.
    if gia_tu_tick(tb) < Pb * he * (1.0 - 1e-12):
        tb += kt
    return gia_tu_tick(ta) / he, gia_tu_tick(tb) / he


# ── thanh khoản và số lượng ─────────────────────────────────────────────

def thanh_khoan_tu_do_la(D: float, P: float, Pa: float, Pb: float) -> float:
    """L sao cho giá trị vị thế bằng `D` đô la khi mở tại giá `P`.

    Trong dải: x·P + y = L·[(√Pb − √P)·√P/√Pb + (√P − √Pa)].
    Ngoài dải thì vị thế chỉ có MỘT loại token, và công thức rút gọn.
    """
    _soat_dai(P, Pa, Pb)
    if D <= 0:
        return 0.0
    sa, sb, sp = math.sqrt(Pa), math.sqrt(Pb), math.sqrt(P)
    if P <= Pa:              # toàn token0, trị giá x·P
        return D / ((sb - sa) / (sa * sb) * P)
    if P >= Pb:              # toàn token1
        return D / (sb - sa)
    return D / ((sb - sp) * sp / sb + (sp - sa))


def so_luong(L: float, P: float, Pa: float, Pb: float) -> tuple[float, float]:
    """`(x, y)` — token0 và token1 mà vị thế L đang cầm ở giá P.

    Kẹp ở hai mép: ra ngoài dải là vị thế đông cứng thành một loại token,
    và đó chính là cơ chế sinh ra tổn thất vô thường ở V3.
    """
    _soat_dai(P, Pa, Pb)
    sa, sb = math.sqrt(Pa), math.sqrt(Pb)
    if P <= Pa:
        return L * (sb - sa) / (sa * sb), 0.0
    if P >= Pb:
        return 0.0, L * (sb - sa)
    sp = math.sqrt(P)
    return L * (sb - sp) / (sp * sb), L * (sp - sa)


def gia_tri(L: float, P: float, Pa: float, Pb: float) -> float:
    """Giá trị vị thế tính bằng token1 (USDG ≈ đô la) ở giá P."""
    x, y = so_luong(L, P, Pa, Pb)
    return x * P + y


def hieu_suat_von(Pa: float, Pb: float) -> float:
    """Vị thế trong dải [Pa, Pb] có thanh khoản gấp bao nhiêu lần một vị thế
    toàn dải cùng giá trị: `1 / (1 − (Pa/Pb)^¼)`.

    Dải ±5% cho ~41×, ±1% cho ~200×. Đây là cả cái hay lẫn cái nguy của V3
    trong MỘT con số: phí nhân 41, LVR cũng nhân 41.
    """
    if not (0 < Pa < Pb):
        raise ValueError(f"cần 0 < Pa < Pb, đang là {Pa}, {Pb}")
    return 1.0 / (1.0 - (Pa / Pb) ** 0.25)


def dai_doi_xung(P: float, rong: float) -> tuple[float, float]:
    """Dải đối xứng theo LOG quanh P: `[P/(1+rong), P·(1+rong)]`.

    Đối xứng theo log chứ không theo đô la, vì log-giá mới là thứ khuếch
    tán đối xứng; dải `[P−5%, P+5%]` theo đô la lệch về phía dưới.
    """
    if rong <= 0:
        raise ValueError("bề rộng dải phải > 0")
    return P / (1.0 + rong), P * (1.0 + rong)


def rong_theo_sigma(sigma: float, tauNam: float, heSo: float) -> float:
    """Bề rộng dải = `heSo × σ√τ`, đổi từ log sang tỉ lệ: `exp(k·σ√τ) − 1`.

    `heSo` là NÚM tiến hoá vặn được (xem `tien_hoa.NUT_VAN`); σ và τ là sự
    thật về thế giới, không phải núm.
    """
    if sigma < 0 or tauNam < 0 or heSo <= 0:
        raise ValueError("σ, τ không âm và hệ số > 0")
    return math.exp(heSo * sigma * math.sqrt(tauNam)) - 1.0


# ── σ từ giá đóng cửa ────────────────────────────────────────────────────

def sigma_nam(giaDong: list, toiThieu: int = 10) -> float | None:
    """σ năm từ dãy giá đóng cửa hằng ngày. `None` khi thiếu mẫu.

    Độ lệch chuẩn của log-return ngày, nhân √252. Không trừ trung bình theo
    kiểu «giả định trôi bằng 0»: với ≤ 60 mẫu, ước trung bình còn nhiễu hơn
    chính nó, nên dùng phương sai quanh 0 là ước THẬN TRỌNG hơn một chút.
    """
    g = [float(x) for x in giaDong if x is not None and float(x) > 0]
    if len(g) < toiThieu + 1:
        return None
    r = [math.log(g[i] / g[i - 1]) for i in range(1, len(g))]
    ms = sum(x * x for x in r) / len(r)
    return math.sqrt(ms) * math.sqrt(NGAY_GIAO_DICH_NAM)


# ── xác suất văng dải ────────────────────────────────────────────────────

def xac_suat_cham(a: float, sigma: float, tauNam: float,
                  mu: float | None = None) -> float:
    """Xác suất log-giá chạm rào ở khoảng cách `a` (>0, cùng chiều trôi
    hoặc ngược chiều đều được — dấu của `a` nói chiều) trong τ.

    Dạng đóng của xác suất chạm lần đầu cho chuyển động Brown có trôi μ:

        P = Φ((−a + μτ)/(σ√τ)) + exp(2μa/σ²) · Φ((−a − μτ)/(σ√τ))

    với a > 0 là rào TRÊN. Rào dưới ở khoảng cách b > 0 là cùng công thức
    với (a, μ) → (b, −μ). Mặc định μ = −σ²/2, tức giá là martingale.
    """
    if sigma <= 0 or tauNam <= 0:
        return 0.0
    if a <= 0:
        return 1.0
    mu = -0.5 * sigma * sigma if mu is None else mu
    s = sigma * math.sqrt(tauNam)
    mu_tau = mu * tauNam
    he = 2.0 * mu * a / (sigma * sigma)
    # `exp(he)` với he rất âm là 0, với he dương lớn thì Φ(…) đã về 0 —
    # kẹp để không tràn.
    he = max(-700.0, min(700.0, he))
    return min(1.0, phi_chuan((-a + mu_tau) / s)
               + math.exp(he) * phi_chuan((-a - mu_tau) / s))


def xac_suat_vang_dai(P: float, Pa: float, Pb: float, sigma: float,
                      tauNam: float) -> dict:
    """Xác suất văng khỏi dải trong τ — CẬN TRÊN, và nói rõ từng mép.

    Trả `tren`, `duoi`, và `tong = min(1, tren + duoi)`. Tổng là cận trên
    vì đường đi chạm cả hai mép bị đếm hai lần; với dải hẹp và τ dài, cận
    này thô — nhưng thô theo hướng thận trọng.

    Giá đã ở ngoài dải thì xác suất là 1 ở mép ấy, và câu hỏi đúng lúc đó
    không còn là «có văng không» mà là «có QUAY LẠI không» — việc của
    `quyet_dinh.py`.
    """
    _soat_dai(P, Pa, Pb)
    if P >= Pb:
        return {"tren": 1.0, "duoi": 0.0, "tong": 1.0, "canTren": True}
    if P <= Pa:
        return {"tren": 0.0, "duoi": 1.0, "tong": 1.0, "canTren": True}
    mu = -0.5 * sigma * sigma
    tren = xac_suat_cham(math.log(Pb / P), sigma, tauNam, mu)
    duoi = xac_suat_cham(math.log(P / Pa), sigma, tauNam, -mu)
    return {"tren": tren, "duoi": duoi, "tong": min(1.0, tren + duoi),
            "canTren": True}


# ── tổn thất vô thường và LVR ────────────────────────────────────────────

def il_tai_gia(L: float, P0: float, P1: float, Pa: float, Pb: float) -> float:
    """IL so với HODL khi giá đi từ P0 tới P1: `V(P1)/H(P1) − 1`, ≤ 0.

    HODL là cầm nguyên (x0, y0) lúc mở. Ở V3, ra ngoài dải thì vị thế đông
    cứng thành một token và IL không tăng nữa — nhưng cũng không giảm.
    """
    x0, y0 = so_luong(L, P0, Pa, Pb)
    hodl = x0 * P1 + y0
    if hodl <= 0:
        return 0.0
    return gia_tri(L, P1, Pa, Pb) / hodl - 1.0


#: Lưới cầu phương cho kỳ vọng theo phân phối chuẩn: 81 điểm trên ±4σ, bước
#: 0,1. Tất định — không có `random` ở đâu trong ty này.
_LUOI_Z = [(-4.0 + 0.1 * i) for i in range(81)]
_TRONG_SO = [math.exp(-0.5 * z * z) for z in _LUOI_Z]
_TONG_TRONG_SO = sum(_TRONG_SO)


def il_ky_vong(P: float, Pa: float, Pb: float, sigma: float,
               tauNam: float) -> float:
    """Kỳ vọng IL tại chân trời τ dưới lognormal trôi −σ²/2, ≤ 0.

    Cầu phương tất định trên lưới z; không mô phỏng Monte Carlo vì hai lượt
    chạy phải ra cùng một con số tới từng chữ số — cổng tiến hoá so hai
    con số ấy với nhau.

    Đây là IL ĐIỂM CUỐI, không phải LVR: nó bỏ qua đường đi. Với người
    KHÔNG phòng hộ (đúng người dùng của ty này) thì điểm cuối là thứ họ
    thấy trong ví.
    """
    if sigma <= 0 or tauNam <= 0:
        return 0.0
    L = thanh_khoan_tu_do_la(1.0, P, Pa, Pb)
    s = sigma * math.sqrt(tauNam)
    tong = 0.0
    for z, w in zip(_LUOI_Z, _TRONG_SO):
        P1 = P * math.exp(-0.5 * s * s + s * z)
        tong += w * il_tai_gia(L, P, P1, Pa, Pb)
    return tong / _TONG_TRONG_SO


def lvr_moi_nam(sigma: float, hieuSuat: float) -> float:
    """LVR (loss-versus-rebalancing) mỗi năm, tỉ lệ trên giá trị vị thế:
    `σ²/8 × hiệu suất` — trong lúc CÒN trong dải.

    σ²/8 là LVR của dải toàn phần (Milionis–Moallemi–Roughgarden–Zhang);
    vị thế tập trung là cùng đường cong với thanh khoản nhân `hiệu suất`,
    nên LVR nhân theo. Đây là chi phí so với người phòng hộ hoàn hảo; với
    người không phòng hộ nó là «phí trả cho arbitrageur», và pool cổ phiếu
    có một arbitrageur RẤT rõ: giá đóng cửa hôm sau.
    """
    return sigma * sigma / 8.0 * hieuSuat


# ── kiểm toán năm hoá (Bài 4) ───────────────────────────────────────────
#
# «Tăng 400% trong 4 năm» là ×5 → CAGR = 5^(1/4) − 1 ≈ 49,5%/năm, KHÔNG phải
# 100%/năm (100%/năm ×4 là ×16). Khoá học nói sai ở mốc 2:20 — phép kiểm
# `kiem_lp_v3` giữ phép tính ấy; ở đây chỉ giữ phép quy đổi máy đang DÙNG.

def apr_tu_apy(apy: float) -> float:
    """APR (cộng đơn, liên tục) tương đương với một APY lãi kép: `ln(1 + APY)`.

    OKX ghi chữ «APY». Nếu đó thật là lãi kép thì 423% APY chỉ tương đương
    APR 165% — phí và thưởng tính theo APR đơn 423% là lạc quan 2,5 lần.
    Không biết OKX kép hay đơn thì coi là KÉP (số nhỏ hơn) và khai ra.
    """
    if apy <= -1.0:
        raise ValueError("APY phải > −100%")
    return math.log(1.0 + apy)


# ── phí và thưởng ────────────────────────────────────────────────────────

def phan_chia_thanh_khoan(Lta: float, LhoatDongPool: float | None) -> float | None:
    """Phần phí ta hưởng = L của ta / (L đang hoạt động của pool + L của ta).
    `None` khi chưa đọc được L của pool — KHÔNG đoán bằng TVL.
    """
    if LhoatDongPool is None or LhoatDongPool < 0 or Lta <= 0:
        return None
    return Lta / (LhoatDongPool + Lta)


def apr_phi_tu_khoi_luong(khoiLuongNgayUsd: float, tvlUsd: float,
                          phiBps: float) -> float | None:
    """APR phí gốc của POOL: `khối lượng ngày × phí × 365 / TVL`. Tỉ lệ."""
    if tvlUsd is None or tvlUsd <= 0 or khoiLuongNgayUsd is None:
        return None
    return khoiLuongNgayUsd * (phiBps / 10_000.0) * 365.0 / tvlUsd


@dataclass(frozen=True)
class KetQuaDai:
    """Một dải đề xuất, cùng mọi con số đi kèm — không con số nào đứng
    một mình mà không có câu nói nó tin được tới đâu."""
    Pa: float
    Pb: float
    rong: float
    hieuSuat: float
    tauNam: float
    xacSuatVang: dict
    ilKyVongBps: float          # ≤ 0, tính trên vốn rót
    lvrBps: float               # ≥ 0, trên vốn rót, trong τ
    phiBps: float | None        # phí gốc kỳ vọng trong τ
    thuongBps: float | None     # thưởng kỳ vọng trong τ (tới hết chương trình)
    gasBps: float | None
    netBps: float | None        # phí + thưởng + IL − gas ; None khi mù
    tiLePhiTrenLvr: float | None
    phanTrongDai: float         # tỉ lệ thời gian kỳ vọng còn trong dải
    ghiChu: tuple = ()
    #: Bài 8 §27 — ĐỘ PHỦ PHÍ = (phí + thưởng) / (|IL kỳ vọng| + gas). Dưới 1
    #: là phí không trả nổi lực cản. LVR KHÔNG cộng thêm vào mẫu: nó và IL kỳ
    #: vọng đo cùng một mất mát bằng hai cách, cộng cả hai là đếm đôi.
    doPhuPhi: float | None = None

    def tom_tat(self) -> dict:
        return {"Pa": self.Pa, "Pb": self.Pb, "rong": self.rong,
                "hieuSuat": self.hieuSuat, "tauNam": self.tauNam,
                "xacSuatVang": self.xacSuatVang,
                "ilKyVongBps": self.ilKyVongBps, "lvrBps": self.lvrBps,
                "phiBps": self.phiBps, "thuongBps": self.thuongBps,
                "gasBps": self.gasBps, "netBps": self.netBps,
                "tiLePhiTrenLvr": self.tiLePhiTrenLvr,
                "phanTrongDai": self.phanTrongDai,
                "doPhuPhi": self.doPhuPhi,
                "ghiChu": list(self.ghiChu)}


def can_dai(P: float, Pa: float, Pb: float, sigma: float, tauNam: float,
            gioGiu: float, aprPhiPool: float | None,
            aprThuongPool: float | None, gioThuongConLai: float | None,
            heSoTapTrungPool: float = 1.0, gasUsd: float | None = None,
            vonUsd: float = 1.0) -> KetQuaDai:
    """Cân một dải cụ thể: mọi con số trên VỐN RÓT, trong cửa sổ `gioGiu`.

    `aprPhiPool` là APR phí gốc của POOL (phí/TVL). Phí của VỊ THẾ = APR
    pool × (hiệu suất của ta / hiệu suất của pool). `heSoTapTrungPool` là
    ước lượng pool đang tập trung cỡ nào — 1,0 nghĩa là «coi pool như
    toàn dải», CỰC lạc quan cho một pool V3 nơi ai cũng tập trung; hàm
    gọi mặc định truyền ĐÚNG hiệu suất của ta (phép nhân thành 1: «pool
    tập trung như ta»). Đường đúng là đọc `liquidity()` qua RPC và chia
    thật; khi có, APR đã chia được đưa vào đây cùng `heSoTapTrungPool =
    hiệu suất của ta`.

    `phanTrongDai` = 1 − ½·P(văng): giả định nếu văng thì văng ở giữa cửa
    sổ. Thô, có khai.
    """
    _soat_dai(P, Pa, Pb)
    hs = hieu_suat_von(Pa, Pb)
    vang = xac_suat_vang_dai(P, Pa, Pb, sigma, tauNam)
    trongDai = 1.0 - 0.5 * vang["tong"]
    il = il_ky_vong(P, Pa, Pb, sigma, tauNam) * 10_000.0
    lvr = lvr_moi_nam(sigma, hs) * tauNam * trongDai * 10_000.0
    ghi = []
    nhan = hs / max(heSoTapTrungPool, 1e-9)
    phi = None
    if aprPhiPool is not None:
        phi = aprPhiPool * nhan * (gioGiu / GIO_NAM) * trongDai * 10_000.0
        if abs(nhan - 1.0) > 1e-9:
            ghi.append(f"phi-nhan-{nhan:.2f}x-theo-gia-dinh-pool-tap-trung")
        else:
            ghi.append("phi-KHONG-nhan-hieu-suat-gia-dinh-pool-tap-trung-nhu-ta")
    thuong = None
    if aprThuongPool is not None:
        gioThuong = gioGiu if gioThuongConLai is None else max(
            0.0, min(gioGiu, gioThuongConLai))
        thuong = (aprThuongPool * nhan * (gioThuong / GIO_NAM) * trongDai
                  * 10_000.0)
        if gioThuong < gioGiu:
            ghi.append(f"thuong-het-sau-{gioThuong:.0f}h-trong-cua-so-{gioGiu:.0f}h")
    gas = None if (gasUsd is None or vonUsd <= 0) else gasUsd / vonUsd * 10_000.0
    net = None
    if phi is not None and gas is not None:
        net = phi + (thuong or 0.0) + il - gas
    phu = None
    if phi is not None and gas is not None:
        canTru = abs(il) + gas
        phu = ((phi + (thuong or 0.0)) / canTru) if canTru > 0 else None
    tile = None
    if aprPhiPool is not None and sigma > 0:
        # Cùng chân trời, cùng hệ số trong-dải, nên chúng giản ước; còn lại
        # là phí pool (đã nhân tập trung) so với σ²/8 × hiệu suất.
        mau = lvr_moi_nam(sigma, hs)
        tu = (aprPhiPool + (aprThuongPool or 0.0) * (
            1.0 if gioThuongConLai is None else
            min(1.0, max(0.0, gioThuongConLai) / max(gioGiu, 1e-9)))) * nhan
        tile = tu / mau if mau > 0 else None
    return KetQuaDai(Pa=Pa, Pb=Pb, rong=math.sqrt(Pb / Pa) - 1.0,
                     hieuSuat=hs, tauNam=tauNam, xacSuatVang=vang,
                     ilKyVongBps=il, lvrBps=lvr, phiBps=phi, thuongBps=thuong,
                     gasBps=gas, netBps=net, tiLePhiTrenLvr=tile,
                     phanTrongDai=trongDai, ghiChu=tuple(ghi), doPhuPhi=phu)


def _soat_dai(P: float, Pa: float, Pb: float) -> None:
    if not (P > 0 and 0 < Pa < Pb):
        raise ValueError(f"giá {P}, dải [{Pa}, {Pb}] không hợp lệ")
