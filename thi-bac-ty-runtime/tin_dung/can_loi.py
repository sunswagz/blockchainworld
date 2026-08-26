"""Cân lợi: thị trường → cơ hội, sau khi đã TRỪ PHÍ.

## APY không phải lợi nhuận, và đây là chỗ dễ tự lừa nhất của ty này

    11% APY  ≠  11% risk-free

Bản đồ nói thẳng chuyện đó, và với cho vay thì cái bẫy có hình dạng riêng:
lãi chảy liên tục nên trông như không có phí, trong khi vào và ra đều tốn
gas — và gas là một khoản CỐ ĐỊNH, nên nó ăn theo tỉ lệ nghịch với cỡ vốn.

    $200 gửi Ethereum, gas vào+ra $12
        → 600 bps phí
        → ở 4%/năm, phải giữ hơn 5 THÁNG mới hoà

Cùng một thị trường ấy với $50.000 thì gas là 2,4 bps và hoà sau nửa ngày.
Nên **cùng một APY, hai cỡ vốn, hai kết luận ngược nhau** — và một scanner
chỉ xếp APY sẽ không bao giờ thấy điều đó.

Vì vậy mỗi cơ hội mang theo `hoaVonSauGio`: giữ bao lâu thì gas hoà. Con số
ấy là thứ trả lời được câu "cơ hội này có thật với TA không", trong khi APY
chỉ trả lời "thị trường đang trả bao nhiêu cho người khác".

## Token thưởng KHÔNG vào NET

`apyReward` là token phát thêm. Nó bốc hơi khi chương trình hết, giá token
thưởng thường rơi đúng lúc ai cũng bán, và ta không có đường bán nó trong
runtime này. Nên nó **không** cộng vào `netBps`; nó chỉ hiện như bằng chứng
và như một cửa cảnh báo (`tyLeThuongToiDa`).

Tính thưởng vào NET là cách nhanh nhất để mọi bảng xếp hạng bị chiếm bởi
những thị trường đang mua thanh khoản bằng token của chính mình.
"""
from __future__ import annotations

from .models import CoHoiVay, ThiTruongVay


def gas_khu_hoi_usd(chuoi: str, bang: dict) -> float:
    """Gas VÀO + RA. Nhân hai vì rút cũng là một giao dịch.

    Quên nhân hai là báo cáo một nửa chi phí, và với cỡ vốn nhỏ thì một nửa
    ấy chính là phần quyết định lỗ hay lãi.
    """
    return 2.0 * float(bang.get(chuoi, bang.get("_khac", 1.0)))


def phi_bps(vonUsd: float, chuoi: str, bang: dict) -> float:
    """Gas quy ra bps trên cỡ vốn. Vốn ≤ 0 thì phí là VÔ HẠN, không phải 0."""
    if vonUsd <= 0:
        return float("inf")
    return gas_khu_hoi_usd(chuoi, bang) / vonUsd * 10_000.0


def hoa_von_sau_gio(t: ThiTruongVay, vonUsd: float, chuoi: str,
                    bang: dict) -> float | None:
    """Giữ bao nhiêu giờ thì lãi gốc bù xong gas. `None` nếu không bao giờ."""
    if t.apyGocPhanTram <= 0 or vonUsd <= 0:
        return None
    gas = gas_khu_hoi_usd(chuoi, bang)
    lai_moi_gio = vonUsd * (t.apyGocPhanTram / 100.0) / (365.0 * 24.0)
    return gas / lai_moi_gio if lai_moi_gio > 0 else None


def suc_chua_usd(t: ThiTruongVay, cau_hinh: dict) -> float | None:
    """Rót được bao nhiêu mà không dìm chính lãi suất vừa thấy.

    Trả `None` khi chưa đo được thanh khoản rảnh — và None phải chảy tới tận
    `ToTrinh`, để Rủi Ro Tổng từ chối chứ không đoán hộ.

    Đây là PROXY THÔ: sức chứa thật đòi đường cong lãi suất của từng giao
    thức, mà runtime này không có. Mọi tờ trình khai `moHinhSucChuaDuChua =
    False` kèm đúng thứ còn thiếu.
    """
    ranh = t.thanhKhoanRanhUsd
    if ranh is None:
        return None
    return min(ranh * float(cau_hinh["phanThanhKhoanRanh"]),
               float(cau_hinh["tranUsd"]))


def mot_co_hoi(t: ThiTruongVay, vonXinUsd: float, giuGio: float,
               gasBang: dict, sucChuaCauHinh: dict) -> CoHoiVay:
    gross = t.bps_trong(giuGio)
    phi = phi_bps(vonXinUsd, t.chuoi, gasBang)
    net = gross - phi
    return CoHoiVay(
        thiTruong=t, vonXinUsd=vonXinUsd, giuGio=giuGio,
        grossBps=gross, phiBps=phi, netBps=net,
        sucChuaToiDaUsd=suc_chua_usd(t, sucChuaCauHinh),
        thanhKhoanThoatUsd=t.thanhKhoanRanhUsd,
        hoaVonSauGio=hoa_von_sau_gio(t, vonXinUsd, t.chuoi, gasBang))


def tim_co_hoi(thiTruong: list, vonXinUsd: float, giuGio: float,
               gasBang: dict, sucChuaCauHinh: dict, cong) -> list[CoHoiVay]:
    """Dựng cơ hội cho MỌI thị trường, kể cả thị trường sẽ bị loại.

    Trả cả cái bị loại có chủ ý: bỏ chúng ngay ở đây thì `soCoHoi` bằng
    `soQuaCongTy`, và tỉ lệ sống sót qua cổng ty vĩnh viễn là 100% — một
    con số luôn đẹp là một con số không nói gì.
    """
    from dataclasses import replace
    ra = []
    for t in thiTruong:
        co = mot_co_hoi(t, vonXinUsd, giuGio, gasBang, sucChuaCauHinh)
        qua, ly = cong.xet(co)
        ra.append(replace(co, duyet=qua, lyDoMa=tuple(ly),
                          lyDo=tuple(c for _, c in ly)))
    ra.sort(key=lambda c: -c.netMoiGioBps)
    return ra
