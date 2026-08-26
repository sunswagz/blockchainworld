"""CHẾ ĐỘ VẬN HÀNH của từng ty, và chi phí hạ tầng của cả bộ máy.

## Tách PHẦN MỀM ĐANG CHẠY khỏi VỐN ĐANG LÀM VIỆC

    $100 vốn
        ↓
    Thị Bạc Ty
        ↓
    mọi engine QUÉT          ← không phụ thuộc vốn
        ↓
    1000 cơ hội nhìn thấy
        ↓
    990 TỪ CHỐI
        ↓
    10 ứng viên
        ↓
    1–2 được cấp vốn         ← đây mới là chỗ vốn quyết
        ↓
    $100 làm việc

Toàn bộ hệ thống chạy được; toàn bộ vốn không cần chạy ở toàn bộ chiến
lược. Chia $100 cho mười engine là mỗi cái $10, và ở $10 thì phí, gas, cỡ
lệnh tối thiểu ăn sạch — mười engine cùng lỗ thay vì một engine có lãi.

## Ba chế độ, và máy KHÔNG được tự ép lên chế độ cao hơn

    QUAN_SAT   quét, trình, ghi sổ — nhưng KHÔNG BAO GIỜ được cấp vốn
    GIAY       được cấp vốn trên SỔ GIẤY, đo như thật, không lệnh nào rời máy
    THAT       tiền thật

Chế độ suy ra tất định từ hai con số, không ai gõ tay:

    trần một cơ hội (NAV × tranMotCoHoi)   ta rót được nhiều nhất bao nhiêu
    vonToiThieuKinhTeUsd của ty            engine ấy cần ít nhất bao nhiêu

Trần < ngưỡng thì QUAN_SAT. Đó là toàn bộ luật, và nó là luật của bản đồ:
*"engine nào không đủ minimum_economic_capital thì chỉ được OBSERVE/PAPER,
tuyệt đối không được ép LIVE"*.

`THAT` chưa với tới được ở bản này vì lớp ký lệnh chưa tồn tại — và đó là
một sự thật, không phải một cấu hình.

## Chi phí hạ tầng là một đối thủ THẬT của vốn nhỏ

    VPS + RPC + API   ~$10/tháng   =   $120/năm

$100 vốn kiếm 20%/năm là $20 — vẫn ÂM $100 sau hạ tầng. Nên ở giai đoạn
này, đánh giá bộ máy bằng số đô kiếm được là đánh giá sai thứ: cái đáng đo
là chất lượng quyết định, và `+$10` có thể là kết quả nghiên cứu rất đáng
giá nếu nó chứng minh được một engine có kỳ vọng dương.

`von_hoa_ha_tang()` in ra thẳng con số vốn cần để hoà hạ tầng ở vài mức lợi
suất. Không phải để nản, mà để không ai nhầm một con số phần trăm đẹp với
một đồng lãi thật.
"""
from __future__ import annotations

from dataclasses import dataclass

QUAN_SAT = "QUAN_SAT"
GIAY = "GIAY"
THAT = "THAT"

#: Thứ tự từ thấp lên cao. Máy chỉ được đi XUỐNG, không được tự đi lên.
BAC = (QUAN_SAT, GIAY, THAT)


@dataclass(frozen=True)
class CheTy:
    ma: str
    ho: str
    che: str
    vonToiThieuUsd: float | None
    tranMotCoHoiUsd: float
    vi: str

    @property
    def duocCapVon(self) -> bool:
        return self.che in (GIAY, THAT)

    def tom_tat(self) -> dict:
        return {"ma": self.ma, "ho": self.ho, "che": self.che,
                "vonToiThieuUsd": self.vonToiThieuUsd,
                "tranMotCoHoiUsd": round(self.tranMotCoHoiUsd, 2),
                "duocCapVon": self.duocCapVon, "vi": self.vi}


def che_cua_ty(ty, navUsd: float, tranMotCoHoi: float,
               lopKyLenhCoChua: bool = False) -> CheTy:
    """Chế độ của MỘT ty. Tất định, suy từ hai con số."""
    tran = max(0.0, float(navUsd) * float(tranMotCoHoi))
    v = getattr(ty, "vonToiThieuKinhTeUsd", None)
    ma = getattr(ty, "ma", "?")
    ho = getattr(ty, "ho", "?")

    if v is None:
        return CheTy(ma, ho, QUAN_SAT, None, tran,
                     "ty chưa khai vốn tối thiểu kinh tế — không biết ngưỡng "
                     "thì không được cấp vốn")
    if tran < float(v) - 1e-9:
        return CheTy(ma, ho, QUAN_SAT, float(v), tran,
                     f"rót được nhiều nhất ${tran:,.0f} < ngưỡng kinh tế "
                     f"${float(v):,.0f} — engine này QUAN SÁT cho tới khi vốn "
                     f"đủ lớn, và ép nó vào lệnh sớm là trả tiền để học một "
                     f"điều đã biết trước")
    if not lopKyLenhCoChua:
        return CheTy(ma, ho, GIAY, float(v), tran,
                     "đủ vốn để cấp — trên SỔ GIẤY. Lớp ký lệnh chưa tồn "
                     "tại, nên THẬT chưa với tới được")
    return CheTy(ma, ho, THAT, float(v), tran, "đủ vốn và có lớp ký lệnh")


def von_can_de_chay(ty_list, tranMotCoHoi: float) -> float | None:
    """NAV nhỏ nhất để engine RẺ NHẤT được cấp vốn.

    Con số này trả lời đúng câu người cầm $100 muốn hỏi: *"cần bao nhiêu thì
    có ít nhất một engine chạy được bằng tiền?"*
    """
    v = [float(getattr(t, "vonToiThieuKinhTeUsd", None) or 0.0)
         for t in ty_list if getattr(t, "vonToiThieuKinhTeUsd", None)]
    if not v or tranMotCoHoi <= 0:
        return None
    return min(v) / float(tranMotCoHoi)


def von_hoa_ha_tang(chiPhiThangUsd: float,
                    loiSuat=(0.10, 0.20, 0.50)) -> dict:
    """Cần bao nhiêu vốn thì lãi bù xong hạ tầng, ở vài mức lợi suất.

    Không phải để nản. Để không ai nhầm một con số phần trăm đẹp với một
    đồng lãi thật: $100 kiếm 20%/năm là $20, và hạ tầng $10/tháng là $120.
    """
    nam = float(chiPhiThangUsd) * 12.0
    return {
        "chiPhiThangUsd": float(chiPhiThangUsd),
        "chiPhiNamUsd": nam,
        "vonHoaVon": {f"{r:.0%}": (round(nam / r, 2) if r > 0 else None)
                      for r in loiSuat},
        "loiNhac": ("Ở giai đoạn này, đánh giá bộ máy bằng số đô kiếm được "
                    "là đánh giá sai thứ. Cái đáng đo là chất lượng quyết "
                    "định — +$10 có thể là kết quả rất đáng giá nếu nó "
                    "chứng minh được một engine có kỳ vọng dương."),
    }
