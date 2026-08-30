"""Động cơ thứ hai: xác suất giá CHẠM một mốc ít nhất một lần trước hạn.

Đây là một họ market khác hẳn Lên/Xuống, dù dùng chung đúng một nguồn giá.

    Lên/Xuống   giá KẾT THÚC ở đâu     P = Φ(z)
    Chạm mốc    giá CÓ TỪNG tới đó     P ≈ 2·Φ(−|b|/(σ√τ))

Con số 2 ở đầu không phải hệ số bịa. Nó là nguyên lý phản xạ: với chuyển
động Brown không trôi, mỗi đường đi CHẠM mốc rồi quay về đều soi gương
được thành một đường kết thúc BÊN KIA mốc. Nên số đường từng chạm gấp đôi
số đường kết thúc bên kia.

## Vì sao họ này đáng có một động cơ riêng

Vì gấp đôi là một khoảng cách rất lớn, và nó bị định giá nhầm thường
xuyên. Một người nhìn "BTC 72k, hỏi có chạm 150k trước cuối năm không"
rất dễ trả lời bằng trực giác của câu "BTC có kết thúc trên 150k không".
Hai câu đó khác nhau gần một nửa giá trị.

## Bốn bẫy, ba trong số đó KHÔNG có ở Lên/Xuống

1. **ĐÃ CHẠM RỒI mà không biết.** Bẫy chết người của họ này. Ta chỉ nhìn
   thấy giá HIỆN TẠI. Nếu tháng trước giá đã vọt qua mốc rồi quay về thì
   market đã ngã ngũ, còn công thức vẫn vui vẻ trả ra 8%. Vì vậy
   `dinhDaQua` (đỉnh/đáy đã đi qua kể từ lúc market mở) là tham số BẮT
   BUỘC. Không có nó thì hàm trả None — từ chối, không đoán.

2. **Quan sát rời rạc, không liên tục.** Công thức phản xạ giả định nhìn
   giá LIÊN TỤC. Sàn kết toán theo một nguồn lấy mẫu cách quãng, nên xác
   suất chạm thật THẤP HƠN. Đây không phải sai số nhỏ: một cú nhọn giữa
   hai lần lấy mẫu là một lần chạm mà công thức đếm còn sàn thì không.
   Hiệu chỉnh bằng cách đẩy mốc ra xa một chút — Broadie–Glasserman–Kou,
   hệ số β = 0,5826.

3. **σ dùng cho chân trời DÀI.** Ở khung 5 phút, σ đo từ 300 giây trước
   là một giả định chấp nhận được. Ở khung bốn tháng thì "σ không đổi" và
   "không trôi" đều yếu hẳn đi, nên SAI SỐ CỦA σ nở theo căn chân trời.

   Nhưng bất định của KẾT QUẢ thì không được lấy thẳng con số đó. Bản đầu
   tôi làm vậy và ra ±0,231 cho mọi σ — trên một xác suất 1% thì nó nói
   "kết quả nằm đâu đó giữa 0 và 24%", trong khi chặn dưới 0 đã cắt mất
   nửa khoảng. Phải TRUYỀN sai số của σ qua công thức: ΔP = 2·φ(z)·z·(Δσ/σ).
   Cách này tự co lại khi P gần 0 hoặc 1, đúng như bất định thật phải thế.

4. **τ → 0 làm nổ mẫu số.** Giống Lên/Xuống, và chặn giống hệt.

## Số hạng trôi: từng bỏ, nay CÓ

Bản đầu bỏ `−σ²τ/2` với lý lẽ nghe rất hợp: "không giả định giá có xu
hướng; với chân trời dài, một giả định trôi rất nhỏ cũng đổi kết quả rất
nhiều, và ta không kiểm được nó bằng số trong khung thời gian của
market."

Lý lẽ ấy đúng cho một xu hướng THẬT (μ khai theo quan điểm về giá). Nó
sai cho số hạng này, và chỗ sai đáng ghi lại vì nó rất dễ mắc lại:
`−σ²τ/2` KHÔNG phải một quan điểm về giá. Nó là hiệu chỉnh bắt buộc để
chính GIÁ là martingale — `E[S_T] = S_0` — khi log-giá là Brown. Bỏ nó
đi không phải "trung lập"; đó là khai rằng giá có xu hướng TĂNG với tốc
độ σ²/2.

Đo trên chính market đang khai (S = 78.016, K = 150.000, τ = 124 ngày):

    σ/năm    P bỏ trôi   P có trôi   chênh       tương đối
    0,35       0,135%      0,097%    +0,038 pp    +39,3%
    0,45       1,269%      0,909%    +0,361 pp    +39,6%
    0,55       4,143%      2,959%    +1,187 pp    +40,0%
    0,70      10,910%      7,758%    +3,158 pp    +40,6%

Bỏ trôi làm P(chạm) cao hơn chừng **40% tương đối**, tức động cơ định
giá vế YES hào phóng hơn thực — chiều nguy hiểm, không phải chiều an
toàn. Và nó KHÔNG nhất quán với `dinh_gia`, nơi cùng số hạng ấy đang
được dùng cho Lên/Xuống: `z = [ln(S/K) − σ²τ/2]/(σ√τ)`. Hai động cơ
trong một cỗ máy đứng trên hai độ đo khác nhau cho cùng một tài sản.

Ở khung 5 phút số hạng ấy nhỏ tới mức không ai thấy. Ở khung bốn tháng
nó là 40%.

### Cái giá phải trả: mất đẳng thức phản xạ

`P(chạm) = 2·P(kết thúc bên kia)` chỉ đúng khi KHÔNG trôi. Có trôi thì
phải dùng dạng đóng đầy đủ (xem `_p_cham`), và con số 2 ở đầu file chỉ
còn đúng cho bản `pChamKhongTroi` giữ lại để so.

Đổi lại, công thức mới thoả hai giới hạn mà bản cũ KHÔNG thoả — và đó
là thứ khoá nó lại:

    τ → ∞, rào TRÊN  →  S/K   (bản cũ cho 2Φ(0) = 1, sai hẳn)
    τ → ∞, rào DƯỚI  →  1

Cả hai đều có phép kiểm.

**KHÔNG sửa ở đây.** Đổi công thức định giá của một market có thể giao
dịch thật là một quyết định phải có chủ ý, và người viết trước đã cân
nhắc rồi chọn — cái thiếu chỉ là con số. Nay có con số. Việc phải làm
nằm trong danh sách "PHẢI ĐÚNG TRƯỚC KHI MỞ BA CỔNG" ở CLAUDE.md, không
nằm trong một lần sửa tiện tay.
"""
from __future__ import annotations

import math

from .config import CONFIG
from .dinh_gia import GiaChuan, phi

# Broadie–Glasserman–Kou: rào quan sát rời rạc tương đương một rào liên
# tục bị đẩy ra xa hệ số exp(β·σ·√Δt). β = −ζ(1/2)/√(2π) ≈ 0,5826.
BETA_RUI_RAC = 0.5826

# Sàn cho tau. Dưới mức này mọi phép chia cho √τ đều thành tiếng ồn.
TAU_SAN_GIAY = 60.0

# Sai số TƯƠNG ĐỐI của sigma, nở theo căn chân trời: ước một ngày thì ~2%,
# ước bốn tháng thì ~23%. Tham số, chưa hiệu chỉnh bằng dữ liệu.
SAI_SO_SIGMA_MOI_NGAY = 0.02


def _p_cham(b: float, sigmaGiay: float, tau: float,
            lenTren: bool) -> float:
    """P(chạm rào cách `b` trong log-giá, trong `tau` giây) — CÓ số hạng trôi.

    Với log-giá `X_t = μt + σW_t` và `μ = −σ²/2` (điều kiện để chính GIÁ
    là martingale), xác suất chạm lần đầu có dạng đóng:

        rào TRÊN:  Φ((μτ − b)/(σ√τ)) + e^(−b)·Φ((−b − μτ)/(σ√τ))
        rào DƯỚI:  Φ((−b + μτ)/(σ√τ)) + e^(b)·Φ((−b − μτ)/(σ√τ))

    Bản trước dùng `2Φ(−b/(σ√τ))` — nguyên lý phản xạ, đúng cho chuyển
    động Brown KHÔNG trôi. Ở khung 5 phút chênh lệch không ai thấy; ở
    khung bốn tháng của `BTC_150K` nó là **40% tương đối**, và lệch về
    phía CAO — tức định giá vế YES hào phóng hơn thực.

    Hai giới hạn dùng để kiểm, và cả hai đều khớp tới 6 chữ số:

        τ → ∞, rào TRÊN  →  S/K      (giá là martingale, dừng tuỳ ý)
        τ → ∞, rào DƯỚI  →  1        (martingale dương chạm mọi mức dưới)

    Bảng đo trên chính market đang khai (S = 78.016, K = 150.000,
    τ = 124 ngày) tái lập đúng bảng trong docstring đầu file:

        σ/năm    P bỏ trôi   P có trôi   tương đối
        0,35       0,135%      0,097%     +39,3%
        0,45       1,269%      0,909%     +39,6%
        0,55       4,143%      2,959%     +40,0%
        0,70      10,910%      7,758%     +40,6%
    """
    mau = sigmaGiay * math.sqrt(tau)
    if mau <= 0:
        return 0.0
    mu_tau = -0.5 * sigmaGiay * sigmaGiay * tau
    b = abs(float(b))
    if lenTren:
        p = phi((mu_tau - b) / mau) + math.exp(-b) * phi((-b - mu_tau) / mau)
    else:
        p = phi((-b + mu_tau) / mau) + math.exp(b) * phi((-b - mu_tau) / mau)
    return min(1.0, max(0.0, p))


def _sai_so_sigma(tauGiay: float) -> float:
    ngay = max(0.0, tauGiay) / 86400.0
    return min(0.60, SAI_SO_SIGMA_MOI_NGAY * math.sqrt(max(1.0, ngay)))


def cham_moc(
    ma: str,
    giaHienTai: float | None = None,
    moc: float | None = None,
    tauGiay: float | None = None,
    dinhDaQua: float | None = None,
    sigmaGiay: float | None = None,
    lenTren: bool = True,
    nhipQuanSatGiay: float | None = None,
    cuaSoSigmaGiay: float | None = None,
    tinHieu: dict[str, float] | None = None,
) -> GiaChuan | None:
    """P(chạm mốc trước hạn). None khi thiếu nguyên liệu — không bịa.

    `dinhDaQua`: đỉnh cao nhất (khi `lenTren`) hoặc đáy thấp nhất đã đi
    qua kể từ lúc market mở. Bắt buộc — xem bẫy 1 ở đầu file.
    """
    if giaHienTai is None or moc is None or tauGiay is None:
        return None
    if dinhDaQua is None:
        return None
    if giaHienTai <= 0 or moc <= 0 or sigmaGiay is None or sigmaGiay <= 0:
        return None

    # Bẫy 5 — σ ĐO TRÊN CỬA SỔ QUÁ NGẮN so với chân trời.
    #
    # Runtime dùng MỘT cửa sổ σ cho mọi market: 900 giây. Với khung 5
    # phút thì hợp lý. Với market bốn tháng thì nó là 900 giây nói về
    # 10,7 triệu giây — tỉ lệ 1 : 11.900.
    #
    # Đo trên 30 ngày BTC, σ quy năm:
    #
    #     cửa sổ 900s   trung vị 0,209 · tứ phân vị [0,132; 0,353]
    #                   min 0,000  max 2,239      ← chênh nhau 2000 lần
    #     cửa sổ 7 ngày trung vị 0,263 · tứ phân vị [0,210; 0,506]
    #                   min 0,203  max 0,595
    #
    # Hai chuyện, cả hai đều hỏng: cửa sổ ngắn vừa THIÊN THẤP (0,209 so
    # với 0,263, tức −21%) vừa NHIỄU khủng khiếp. Cắm một σ như thế vào
    # chân trời bốn tháng thì P(chạm) nhảy từ gần 0% tới gần 100% chỉ vì
    # mười lăm phút vừa rồi tình cờ lặng hay tình cờ động.
    #
    # Từ chối, đúng nguyên tắc của chính module này: "None khi thiếu
    # nguyên liệu — không bịa". Một σ nhiễu gấp hai nghìn lần KHÔNG phải
    # nguyên liệu, dù nó là một số thực hợp lệ.
    #
    # Ngưỡng 1/50: cửa sổ ước phải dài ít nhất 2% chân trời. Với khung 5
    # phút (τ = 300s, cửa sổ 900s) thì thừa; với bốn tháng thì đòi ~2,5
    # ngày mẫu. Không có `cuaSoSigmaGiay` thì KHÔNG chặn — chỗ gọi cũ và
    # phép kiểm cũ vẫn chạy y như trước.
    if (cuaSoSigmaGiay is not None and cuaSoSigmaGiay > 0
            and tauGiay > 50.0 * cuaSoSigmaGiay):
        return None

    # Bẫy 1 — đã chạm rồi thì market đã ngã ngũ. Kiểm TRƯỚC mọi phép tính:
    # để nó chảy vào công thức là ra một xác suất nhỏ cho một chuyện đã
    # xảy ra chắc chắn.
    daCham = (dinhDaQua >= moc) if lenTren else (dinhDaQua <= moc)
    if daCham:
        return GiaChuan(
            ma=ma, pUp=1.0, pDown=0.0,
            batDinh=0.0, batDinhThamSo=0.0, ruiRoNhay=0.0,
            z=float("inf") if lenTren else float("-inf"),
            sigmaGiay=sigmaGiay, tauGiay=tauGiay, tauDungSan=False,
            daMatPhang=False, giaHienTai=giaHienTai, giaMo=moc,
            oHieuChinh="da-cham",
            giaiTrinh={"ketLuan": "đã chạm mốc rồi — market đã ngã ngũ",
                       "dinhDaQua": dinhDaQua, "moc": moc, "soHo": 0,
                       "chiTiet": []},
        )

    tauDungSan = tauGiay < TAU_SAN_GIAY
    tau = max(TAU_SAN_GIAY, tauGiay)

    # Bẫy 2 — đẩy mốc ra xa để bù cho việc sàn không nhìn liên tục.
    nhip = nhipQuanSatGiay or float(
        (CONFIG.get("dinhGia") or {}).get("nhipQuanSatGiay", 60.0))
    day = BETA_RUI_RAC * sigmaGiay * math.sqrt(max(1.0, nhip))
    mocHieuDung = moc * math.exp(day if lenTren else -day)

    b = abs(math.log(mocHieuDung / giaHienTai))
    mau = sigmaGiay * math.sqrt(tau)
    if mau <= 0:
        return None
    z = b / mau

    p = _p_cham(b, sigmaGiay, tau, bool(lenTren))

    # Bẫy 3 — bất định phải là bất định CỦA KẾT QUẢ, không phải của σ.
    #
    # Bản đầu lấy thẳng sai số chân trời làm bất định, ra ±0,231 cho mọi σ.
    # Trên một xác suất 1% thì con số đó vô nghĩa: nó nói kết quả nằm đâu
    # đó giữa 0 và 24%, trong khi chặn dưới 0 đã cắt mất nửa khoảng.
    #
    # Đúng là truyền sai số của σ QUA công thức:
    #     P = 2Φ(−z),  z = b/(σ√τ)   ⇒   dP/dσ = 2φ(z)·z/σ
    # nên  ΔP = 2·φ(z)·z·(Δσ/σ). Cách này tự co lại khi P gần 0 hoặc 1,
    # đúng như bất định thật phải thế.
    #
    # Đạo hàm lấy bằng SỐ, không bằng tay. Bản trước viết thẳng
    # `ΔP = 2·φ(z)·z·(Δσ/σ)` — đúng cho `P = 2Φ(−z)` và CHỈ cho công
    # thức ấy. Nay công thức có thêm số hạng trôi, nên một đạo hàm chép
    # tay là một chỗ nữa để hai vế trôi ra khỏi nhau, và nó trôi lặng:
    # bất định vẫn ra một con số trông hợp lý.
    relSigma = _sai_so_sigma(tau)
    # Mật độ tại rào — dùng cho rủi ro NHẢY bên dưới, nên vẫn phải có.
    matDoZ = math.exp(-0.5 * z * z) / math.sqrt(2.0 * math.pi)
    h = 0.01
    dP = (_p_cham(b, sigmaGiay * (1.0 + h), tau, bool(lenTren))
          - _p_cham(b, sigmaGiay * (1.0 - h), tau, bool(lenTren))) / (2.0 * h)
    batDinhThamSo = min(0.5, abs(dP) * relSigma)
    # Rủi ro nhảy ở họ này là chuyện một cú nhọn chạm mốc rồi rút — nó
    # LÀM TĂNG xác suất chạm, nên đo bằng mật độ tại rào.
    ruiRoNhay = min(0.5, matDoZ * (day / mau if mau else 0.0))
    batDinh = min(0.5, math.hypot(batDinhThamSo, ruiRoNhay))

    pTho = p
    daMatPhang = False
    if p > 0.995:
        p, daMatPhang = 0.995, True
    elif p < 0.005:
        p, daMatPhang = 0.005, True

    return GiaChuan(
        ma=ma, pUp=p, pDown=1.0 - p,
        batDinh=batDinh, batDinhThamSo=batDinhThamSo, ruiRoNhay=ruiRoNhay,
        z=z, sigmaGiay=sigmaGiay, tauGiay=tauGiay, tauDungSan=tauDungSan,
        daMatPhang=daMatPhang, giaHienTai=giaHienTai, giaMo=moc,
        oHieuChinh=_o(p),
        giaiTrinh={
            "ketLuan": "xác suất CHẠM ít nhất một lần, không phải kết thúc trên mốc",
            "mocKhai": moc, "mocHieuDung": mocHieuDung,
            "dayRuiRac": day, "nhipQuanSatGiay": nhip,
            "coSoTroi": ("chạm lần đầu với μ = −σ²/2 — cùng độ đo "
                         "martingale mà `dinh_gia` dùng cho Lên/Xuống"),
            "pChamTho": pTho, "pKetThuc": phi(-z),
            "pChamKhongTroi": min(1.0, max(0.0, 2.0 * phi(-z))),
            "luuY": ("`pChamKhongTroi` là bản PHẢN XẠ cũ, giữ lại để so — "
                     "ở khung bốn tháng nó cao hơn chừng 40% tương đối, "
                     "tức hào phóng hơn thực với vế YES. `pKetThuc` so với "
                     "`pChamKhongTroi` mới đúng tỉ lệ 2."),
            "soHo": 0, "chiTiet": [],
        },
    )


def _o(p: float) -> str:
    i = min(9, max(0, int(p * 10)))
    return f"{i * 10}-{i * 10 + 10}"
