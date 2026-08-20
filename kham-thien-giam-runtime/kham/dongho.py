"""Đồng hồ chợ — thứ quan trọng nhất trong một market sống 5 phút.

Với một hợp đồng 5 phút, `còn bao nhiêu giây` không phải thông tin phụ: nó là
mẫu số của mô hình định giá (σ√τ), là thứ quyết định giai đoạn vòng đời, và là
thứ quyết định một chiến thuật có được phép mở vị thế mới hay không.

Ba cái bẫy ở đây, cả ba đều hỏng im lặng:

  1. **τ → 0 làm nổ mô hình.** `σ√τ` là mẫu số của z-score. Khi còn 0,3 giây
     thì mẫu số ≈ 0 và P(UP) nhảy về đúng 0 hoặc đúng 1. Mô hình khi đó nói
     "chắc chắn 100%" đúng vào lúc nó biết ít nhất — vì một tick cuối cùng vẫn
     lật được kết quả. Nên có `sanNenGiay`: τ không bao giờ nhỏ hơn ngần ấy.

  2. **Đồng hồ máy lệch đồng hồ sàn.** Mọi phép tính thời gian còn lại đều dựa
     trên `now()` của MÁY NÀY. Máy chạy nhanh 3 giây thì runtime tưởng market
     sắp đóng và ngừng vào lệnh sớm; chạy chậm 3 giây thì nó vào lệnh sau khi
     sổ đã khoá. Không lỗi nào báo. Nên phải ĐO độ lệch với máy chủ sàn và coi
     lệch quá ngưỡng là một lý do phủ quyết.

  3. **Trễ mạng cũng là thời gian.** Số τ đúng lúc gói tin rời sàn đã cũ đi
     một nửa vòng khứ hồi lúc nó tới đây.
"""
from __future__ import annotations

import time
from dataclasses import dataclass

# Vòng đời một market nhị phân ngắn hạn. Chiến thuật không giống nhau ở mọi
# giai đoạn, nên đặt tên rõ hơn là rải `if con_lai < 90` khắp nơi.
MO_MAN = "mo-man"          # vừa mở, sổ còn mỏng, giá còn loạn
GOM_THANH_KHOAN = "gom"    # sổ dày dần, spread hẹp lại
GIUA_KHUNG = "giua"        # ổn định nhất — chỗ mô hình đáng tin nhất
CUOI_KHUNG = "cuoi"        # τ nhỏ, biến động ngụ ý tăng vọt
CAN_KET_QUA = "can-ket"    # sát resolution, một tick lật cả trăm phần trăm
DA_KHOA = "da-khoa"

_CHUOI = [MO_MAN, GOM_THANH_KHOAN, GIUA_KHUNG, CUOI_KHUNG, CAN_KET_QUA, DA_KHOA]

NHAN = {
    MO_MAN: "mở màn",
    GOM_THANH_KHOAN: "gom thanh khoản",
    GIUA_KHUNG: "giữa khung",
    CUOI_KHUNG: "cuối khung",
    CAN_KET_QUA: "cận kết quả",
    DA_KHOA: "đã khoá",
}


@dataclass(frozen=True)
class LatCat:
    """Một lát cắt đồng hồ. Bất biến — để không ai sửa được τ giữa chừng."""
    conLaiGiay: float
    tongGiay: float
    giaiDoan: str
    troiQuaPct: float
    lechDongHoMs: float
    tuoiDuLieuMs: float

    @property
    def nhan(self) -> str:
        return NHAN.get(self.giaiDoan, self.giaiDoan)

    @property
    def da_khoa(self) -> bool:
        return self.giaiDoan == DA_KHOA


class DongHo:
    """Giữ độ lệch giữa đồng hồ máy này và đồng hồ máy chủ sàn."""

    def __init__(self) -> None:
        self._lech_ms = 0.0
        self._do_luc = 0.0

    def hieu_chinh(self, mocSanMs: float, guiLucMs: float, nhanLucMs: float) -> float:
        """Ước lượng độ lệch theo lối NTP đơn giản.

        Giả định trễ đi và trễ về bằng nhau — không đúng tuyệt đối, nhưng sai
        số còn lại nhỏ hơn nhiều so với việc bỏ qua hiệu chỉnh hoàn toàn.
        """
        khu_hoi = nhanLucMs - guiLucMs
        giua_may = (guiLucMs + nhanLucMs) / 2.0
        self._lech_ms = giua_may - (mocSanMs + khu_hoi / 2.0)
        self._do_luc = nhanLucMs
        return self._lech_ms

    @property
    def lech_ms(self) -> float:
        return self._lech_ms

    def bay_gio_ms(self) -> float:
        """Thời điểm hiện tại theo ĐỒNG HỒ SÀN, không phải đồng hồ máy."""
        return time.time() * 1000.0 - self._lech_ms

    def lat_cat(self, ketThucMs: float, tongGiay: float, tuoiDuLieuMs: float = 0.0) -> LatCat:
        con_lai = max(0.0, (ketThucMs - self.bay_gio_ms()) / 1000.0)
        tong = max(1e-9, float(tongGiay))
        troi_qua = min(1.0, max(0.0, 1.0 - con_lai / tong))
        return LatCat(
            conLaiGiay=con_lai,
            tongGiay=tong,
            giaiDoan=_giai_doan(con_lai, tong),
            troiQuaPct=troi_qua * 100.0,
            lechDongHoMs=self._lech_ms,
            tuoiDuLieuMs=tuoiDuLieuMs,
        )


def _giai_doan(conLaiGiay: float, tongGiay: float) -> str:
    """Giai đoạn = cái KHẨN HƠN trong hai lối đo, tỉ lệ và tuyệt đối.

    Vì sao phải có cả hai, và phải lấy max chứ không phải lấy một:

    · **Tỉ lệ** hợp với phần đầu. "Sổ đã dày chưa" phụ thuộc bao nhiêu phần
      khung đã trôi qua, và điều đó co giãn theo độ dài market.

    · **Tuyệt đối** hợp với phần cuối. "Một tick BTC lật được kết quả" là
      chuyện của mấy giây cuối cùng, không co giãn theo độ dài khung: 15 giây
      chót của market 15 phút cũng nguy hiểm y hệt 15 giây chót của market
      5 phút.

    Bản đầu tiên chỉ có tỉ lệ cho phần đầu và tuyệt đối cho 45 giây chót, rồi
    để `GIUA_KHUNG` hứng toàn bộ khoảng giữa. Hậu quả: market 15 phút còn 60
    giây vẫn bị gọi là "giữa khung" — tức là runtime tưởng mình đang ở chỗ mô
    hình đáng tin nhất trong khi biến động ngụ ý đã bốc lên, và các chiến
    thuật mở vị thế mới vẫn được phép chạy. Lệch một giai đoạn ở đúng chỗ đắt
    nhất, và không có lỗi nào báo.

    Lấy max theo thứ tự khẩn cấp thì cả hai lối đo đều nói được, và lối nào
    thấy nguy hơn thì lối đó thắng.
    """
    if conLaiGiay <= 0:
        return DA_KHOA

    # theo giây tuyệt đối
    if conLaiGiay <= 15:
        tuyet_doi = CAN_KET_QUA
    elif conLaiGiay <= 45:
        tuyet_doi = CUOI_KHUNG
    else:
        tuyet_doi = MO_MAN

    # theo tỉ lệ khung đã trôi
    con_lai_pct = conLaiGiay / max(1e-9, tongGiay)
    if con_lai_pct >= 0.85:
        ti_le = MO_MAN
    elif con_lai_pct >= 0.60:
        ti_le = GOM_THANH_KHOAN
    elif con_lai_pct >= 0.25:
        ti_le = GIUA_KHUNG
    else:
        ti_le = CUOI_KHUNG

    return max(tuyet_doi, ti_le, key=_CHUOI.index)


dong_ho = DongHo()
