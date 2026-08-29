"""ĐƯỜNG SỨC CHỨA — cỗ máy này chạy nổi bao nhiêu tiền, và ở mức nào thì hết.

## Câu hỏi nó trả lời

*"Bỏ vào 10 nghìn thì lãi mấy phần trăm? 100 nghìn? Một triệu? Mười
triệu?"* — và đó là câu quyết định bao nhiêu tiền THẬT nên vào đây.

Câu ấy không trả lời được bằng một con số APR duy nhất, vì **lợi suất
tụt theo quy mô**. Đo trên máy sống 29/08/2026, vốn ảo một triệu:

    họ thanh-khoan (AMM)   21–39 %/năm   sức chứa chỉ ~7.000 USD
    họ tin-dung  (cho vay)  2–3  %/năm   sức chứa hàng trăm nghìn

Rót 10 nghìn thì gần như toàn bộ vào chỗ 30%. Rót một triệu thì 99% số
tiền ấy không còn chỗ nào ngoài 3%. **Cùng một cỗ máy, cùng một phút, hai
con số lợi suất khác hẳn nhau** — và cái khác nhau ấy không phải do máy
giỏi lên hay dở đi, mà do thị trường chỉ chứa được ngần ấy.

Một cỗ máy khoe «30%/năm» mà không nói con số ấy chỉ đúng tới 7.000 USD
là một cỗ máy nói dối bằng cách bỏ bớt.

## Cách đo

Xếp mọi cơ hội ĐANG có theo lãi giảm dần, rồi rót lần lượt cho tới hết
vốn — mỗi cơ hội nhận nhiều nhất bằng sức chứa của nó. Lãi bình quân gia
quyền của cái danh mục giả định ấy chính là lợi suất ở mức vốn đó.

    mức vốn   →   rót vào đâu           →   lãi bình quân
    10.000        toàn chỗ tốt nhất          cao
    1.000.000     tràn xuống chỗ tệ hơn      thấp

Ba chỗ phải cẩn thận, và cả ba đều bị chặn ở đây:

**Cơ hội không khai lãi thì BỎ, không coi là 0.** Một tờ trình im lặng
bị xếp cuối như thể nó tệ, trong khi ta chỉ đơn giản là chưa hỏi.

**Cơ hội không khai sức chứa thì cũng BỎ.** Không biết nó nuốt được bao
nhiêu thì không xếp nó vào một phép tính về sức nuốt. Cả hai số ấy đếm
riêng và khai ra, để người đọc biết đường cong này dựng trên bao nhiêu
phần của bức tranh.

**Vốn không rót hết thì phần dư ăn lãi 0.** Bỏ qua phần dư là khoe lợi
suất của phần đã rót và gọi đó là lợi suất của cả túi tiền — đúng cái
lỗi mà `vonDangDung` sinh ra để chặn, chỉ khác chỗ đứng.

## Bản này là ẢNH CHỤP, không phải lời hứa

Nó dựng trên cơ hội của ĐÚNG vòng này. Sức chứa đổi theo giờ, lãi đổi
theo giờ, và một đường cong đo lúc 3 giờ sáng không nói được gì về 9 giờ
tối. Đọc nó như đọc một nhiệt kế, không phải như đọc một hợp đồng.
"""
from __future__ import annotations

from dataclasses import dataclass, field

#: Các mức vốn đem ra thử, USD. Trải theo bậc mười vì câu hỏi thật là
#: «cùng cấp độ nào» chứ không phải «chính xác bao nhiêu».
MUC_MAC_DINH = (10_000.0, 50_000.0, 100_000.0, 500_000.0,
                1_000_000.0, 5_000_000.0, 10_000_000.0)


@dataclass
class MotMuc:
    vonUsd: float
    rotDuocUsd: float          # rót được bao nhiêu — phần dư nằm không
    soCoHoi: int               # dùng tới bao nhiêu cơ hội
    aprTrenVonRotUsd: float    # lãi bình quân trên phần ĐÃ rót
    aprTrenCaTuiUsd: float     # lãi bình quân trên CẢ vốn, dư ăn 0

    def tom_tat(self) -> dict:
        return {"vonUsd": self.vonUsd, "rotDuocUsd": self.rotDuocUsd,
                "soCoHoi": self.soCoHoi,
                "aprTrenVonRot": self.aprTrenVonRotUsd,
                "aprTrenCaTui": self.aprTrenCaTuiUsd}


@dataclass
class DuongSucChua:
    muc: list = field(default_factory=list)
    soCoHoiDung: int = 0
    soBoViThieuLai: int = 0
    soBoViThieuSucChua: int = 0
    tongSucChuaUsd: float = 0.0
    vi: str = ""

    def tom_tat(self) -> dict:
        return {
            "muc": [m.tom_tat() for m in self.muc],
            "soCoHoiDung": self.soCoHoiDung,
            "soBoViThieuLai": self.soBoViThieuLai,
            "soBoViThieuSucChua": self.soBoViThieuSucChua,
            "tongSucChuaUsd": self.tongSucChuaUsd,
            "vi": self.vi,
        }


def do_duong_suc_chua(toTrinh: list, muc=MUC_MAC_DINH) -> DuongSucChua:
    """Lợi suất ở từng mức vốn, dựng từ cơ hội của ĐÚNG vòng này."""
    from .xoay_cho import apr_tu_to_trinh

    ra = DuongSucChua()
    ds: list[tuple[float, float]] = []          # (apr, sức chứa)
    for tt in (toTrinh or []):
        t = tt if isinstance(tt, dict) else (
            tt.tom_tat() if hasattr(tt, "tom_tat") else {})
        apr = apr_tu_to_trinh(t)
        if apr is None:
            ra.soBoViThieuLai += 1
            continue
        sc = t.get("sucChuaToiDaUsd")
        if sc is None or float(sc) <= 0:
            ra.soBoViThieuSucChua += 1
            continue
        ds.append((apr, float(sc)))
    ds.sort(key=lambda x: -x[0])
    ra.soCoHoiDung = len(ds)
    ra.tongSucChuaUsd = sum(s for _, s in ds)

    for v in muc:
        con = float(v)
        rot = 0.0
        tong = 0.0
        dem = 0
        for apr, sc in ds:
            # `<=` và `<` cho cùng kết quả: `con == 0` thì `lay = min(0, sc)`
        # cũng bằng 0 và mọi phép cộng dưới đây cộng 0. TƯƠNG ĐƯƠNG — y
        # như dòng cùng dạng trong `duong_khoa_von.py`.
        if con <= 0:
                break
            lay = min(con, sc)
            rot += lay
            tong += lay * apr
            con -= lay
            dem += 1
        ra.muc.append(MotMuc(
            vonUsd=float(v), rotDuocUsd=rot, soCoHoi=dem,
            aprTrenVonRotUsd=(tong / rot) if rot > 0 else 0.0,
            # Phần dư ăn lãi 0. Bỏ qua nó là khoe lợi suất của phần đã rót
            # rồi gọi đó là lợi suất của cả túi tiền.
            aprTrenCaTuiUsd=(tong / float(v)) if v > 0 else 0.0))
    ra.vi = _vi(ra)
    return ra


def _vi(d: DuongSucChua) -> str:
    if not d.muc or d.soCoHoiDung == 0:
        return (f"chưa dựng được đường cong — {d.soBoViThieuLai} cơ hội "
                f"không khai lãi, {d.soBoViThieuSucChua} không khai sức "
                f"chứa. Không biết thì không xếp vào, chứ không coi là 0.")
    dau, cuoi = d.muc[0], d.muc[-1]
    return (f"tổng sức chứa đang thấy {d.tongSucChuaUsd:,.0f} USD trên "
            f"{d.soCoHoiDung} cơ hội. Ở {dau.vonUsd:,.0f} USD thì lãi "
            f"{dau.aprTrenCaTuiUsd:.2f}%/năm; ở {cuoi.vonUsd:,.0f} thì còn "
            f"{cuoi.aprTrenCaTuiUsd:.2f}%. Lợi suất TỤT theo quy mô, và một "
            f"con số APR không kèm mức vốn là một con số bỏ bớt.")
