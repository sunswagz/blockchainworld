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


def gas_khu_hoi_usd(chuoi: str, bang: dict, dinhTuyen=None) -> float:
    """Gas VÀO + RA. Nhân hai vì rút cũng là một giao dịch.

    Quên nhân hai là báo cáo một nửa chi phí, và với cỡ vốn nhỏ thì một nửa
    ấy chính là phần quyết định lỗ hay lãi.

    Có Router thì dùng gas SỐNG đọc từ RPC; không có thì rơi về bảng ước
    trong `config.py`. Bảng ấy từng là thứ duy nhất, và chú thích của nó
    viết "không có oracle gas nào trong runtime này" — câu đó đúng cho tới
    ngày `chuyen_von/gas.py` ra đời.

    Rơi về bảng chứ không trả `None`: gas là khoản ta biết chắc có, chỉ
    không biết chính xác bao nhiêu. Đó khác hẳn phí cầu nối — khoản có thể
    KHÔNG TỒN TẠI vì không có tuyến nào.
    """
    song = _gas_song_usd(chuoi, dinhTuyen)
    if song is not None:
        return 2.0 * song
    return 2.0 * float(bang.get(chuoi, bang.get("_khac", 1.0)))


def _gas_song_usd(chuoi: str, dinhTuyen) -> float | None:
    """Một giao dịch ERC-20 trên chuỗi này tốn bao nhiêu, theo gas hiện tại."""
    if dinhTuyen is None:
        return None
    try:
        return dinhTuyen._gas_usd(str(chuoi).strip().lower(), "chuyen-erc20")
    except Exception:                                         # noqa: BLE001
        return None


def phi_vao_lien_chuoi(chuoi: str, taiSan: str, vonUsd: float,
                       dinhTuyen=None) -> tuple:
    """(usd, giây, thứ-chưa-tính) để đưa vốn TỪ NHÀ tới chuỗi này rồi về.

    Đây chính là khoản `chuyen-von-giua-chuoi` ty này khai thiếu từ đầu.
    Nhân hai vì vốn phải quay về — một cơ hội bắt ta bắc cầu sang rồi bỏ
    vốn ở đó vĩnh viễn thì không phải một cơ hội, nó là một lần dời nhà.

    Cùng chuỗi với NHÀ thì không có gì để bắc: trả `(0.0, 0.0, ())`, và số
    0 ấy là số ĐÃ ĐO chứ không phải chỗ trống.
    """
    if dinhTuyen is None:
        return None, None, ()
    try:
        from chuyen_von.diem import Diem
        from chuyen_von.dinh_tuyen import NHA
        c = str(chuoi).strip().lower()
        if c == NHA:
            return 0.0, 0.0, ()
        _, t = dinhTuyen.phi_bps(Diem("chuoi", NHA), Diem("chuoi", c),
                                 taiSan, vonUsd)
        if t.phiUsd is None:
            return None, None, ()
        return 2.0 * t.phiUsd, 2.0 * (t.giayCho or 0.0), tuple(t.khongDoDuoc)
    except Exception as e:                                    # noqa: BLE001
        return None, None, (f"router-no:{type(e).__name__}",)


def phi_bps(vonUsd: float, chuoi: str, bang: dict, dinhTuyen=None,
            phiCauUsd: float | None = None) -> float:
    """Gas quy ra bps trên cỡ vốn. Vốn ≤ 0 thì phí là VÔ HẠN, không phải 0.

    `phiCauUsd` cộng thêm khi Router đo được đường bắc cầu tới chuỗi ấy.
    `None` thì KHÔNG cộng gì — và cơ hội giữ nguyên khai báo
    `chuyen-von-giua-chuoi`, chứ không lặng lẽ coi như bằng 0.
    """
    if vonUsd <= 0:
        return float("inf")
    tong = gas_khu_hoi_usd(chuoi, bang, dinhTuyen) + (phiCauUsd or 0.0)
    return tong / vonUsd * 10_000.0


def hoa_von_sau_gio(t: ThiTruongVay, vonUsd: float, chuoi: str,
                    bang: dict, dinhTuyen=None,
                    phiCauUsd: float | None = None) -> float | None:
    """Giữ bao nhiêu giờ thì lãi gốc bù xong CHI PHÍ VÀO. `None` nếu không.

    Đây là chỗ Router đổi kết luận rõ nhất: gas một chiều trên Base là vài
    xu, nhưng bắc cầu $500 từ Arbitrum sang Base rồi về là vài đô — và vài
    đô ấy biến "hoà sau nửa ngày" thành "hoà sau vài tuần".
    """
    if t.apyGocPhanTram <= 0 or vonUsd <= 0:
        return None
    gas = gas_khu_hoi_usd(chuoi, bang, dinhTuyen) + (phiCauUsd or 0.0)
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
               gasBang: dict, sucChuaCauHinh: dict,
               dinhTuyen=None) -> CoHoiVay:
    cauUsd, cauGiay, cauThieu = phi_vao_lien_chuoi(
        t.chuoi, t.taiSan, vonXinUsd, dinhTuyen)
    gross = t.bps_trong(giuGio)
    phi = phi_bps(vonXinUsd, t.chuoi, gasBang, dinhTuyen, cauUsd)
    net = gross - phi
    return CoHoiVay(
        thiTruong=t, vonXinUsd=vonXinUsd, giuGio=giuGio,
        grossBps=gross, phiBps=phi, netBps=net,
        sucChuaToiDaUsd=suc_chua_usd(t, sucChuaCauHinh),
        thanhKhoanThoatUsd=t.thanhKhoanRanhUsd,
        hoaVonSauGio=hoa_von_sau_gio(t, vonXinUsd, t.chuoi, gasBang,
                                     dinhTuyen, cauUsd),
        phiCauUsd=cauUsd, giayCauNoi=cauGiay, routerConThieu=cauThieu,
        gasSong=_gas_song_usd(t.chuoi, dinhTuyen) is not None)


def tim_co_hoi(thiTruong: list, vonXinUsd: float, giuGio: float,
               gasBang: dict, sucChuaCauHinh: dict, cong,
               dinhTuyen=None) -> list[CoHoiVay]:
    """Dựng cơ hội cho MỌI thị trường, kể cả thị trường sẽ bị loại.

    Trả cả cái bị loại có chủ ý: bỏ chúng ngay ở đây thì `soCoHoi` bằng
    `soQuaCongTy`, và tỉ lệ sống sót qua cổng ty vĩnh viễn là 100% — một
    con số luôn đẹp là một con số không nói gì.
    """
    from dataclasses import replace
    ra = []
    for t in thiTruong:
        co = mot_co_hoi(t, vonXinUsd, giuGio, gasBang,
                        sucChuaCauHinh, dinhTuyen)
        qua, ly = cong.xet(co)
        ra.append(replace(co, duyet=qua, lyDoMa=tuple(ly),
                          lyDo=tuple(c for _, c in ly)))
    ra.sort(key=lambda c: -c.netMoiGioBps)
    return ra
