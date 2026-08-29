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

## Cái động cơ này KHÔNG làm

Không giả định giá có xu hướng. Với chân trời dài, một giả định trôi rất
nhỏ cũng đổi kết quả rất nhiều, và ta không có cách nào kiểm nó bằng số
trong khung thời gian của market. Bỏ trôi là chấp nhận sai lệch có hướng
đã biết — an toàn hơn là đưa vào một con số không ai kiểm được.

### Nhưng "hướng đã biết" thì phải BIẾT LÀ BAO NHIÊU

Câu trên đúng về nguyên tắc và rỗng về thực hành: nó nói có sai lệch mà
không nói chiều nào, lớn cỡ nào. Đo (S = 78.016, K = 150.000, τ = 124
ngày — đúng market `BTC_150K` đang khai trong config):

    σ/năm    P bỏ trôi   P có trôi   chênh       tương đối
    0,35       0,136%      0,098%    +0,038 pp    +39,3%
    0,45       1,274%      0,912%    +0,361 pp    +39,6%
    0,55       4,154%      2,967%    +1,187 pp    +40,0%
    0,70      10,929%      7,771%    +3,158 pp    +40,6%

**Bỏ trôi làm P(chạm) CAO HƠN chừng 40% tương đối**, và tỉ lệ ấy gần như
không đổi theo σ. Cao hơn nghĩa là động cơ định giá "có chạm" hào phóng
hơn thực — tức nó sẵn sàng MUA vế YES đắt hơn mức đáng. Đó là chiều
nguy hiểm, không phải chiều an toàn.

### Và nó KHÔNG nhất quán với động cơ Lên/Xuống

Số hạng bỏ đi ở đây — `−σ²τ/2` trong log-giá — chính là số hạng mà
`dinh_gia` ĐANG DÙNG cho Lên/Xuống: `z = [ln(S/K) − σ²τ/2]/(σ√τ)`. Nó
không phải một "giả định xu hướng" ai đó thêm vào; nó là hiệu chỉnh bắt
buộc để chính GIÁ là martingale. Hai động cơ trong cùng một cỗ máy đang
đứng trên hai độ đo khác nhau cho cùng một tài sản.

Ở khung 5 phút số hạng ấy nhỏ tới mức không ai thấy. Ở khung bốn tháng
nó là 40%.

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

    p = 2.0 * phi(-z)
    p = min(1.0, max(0.0, p))

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
    relSigma = _sai_so_sigma(tau)
    matDoZ = math.exp(-0.5 * z * z) / math.sqrt(2.0 * math.pi)
    batDinhThamSo = min(0.5, 2.0 * matDoZ * z * relSigma)
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
            "gapDoi": "nguyên lý phản xạ: P(chạm) ≈ 2·P(kết thúc bên kia)",
            "pChamTho": pTho, "pKetThuc": phi(-z),
            "luuY": ("pKetThuc so với pChamTho mới đúng tỉ lệ 2; so với pUp "
                     "thì sai khi P đã bị làm phẳng ở cận."),
            "soHo": 0, "chiTiet": [],
        },
    )


def _o(p: float) -> str:
    i = min(9, max(0, int(p * 10)))
    return f"{i * 10}-{i * 10 + 10}"
