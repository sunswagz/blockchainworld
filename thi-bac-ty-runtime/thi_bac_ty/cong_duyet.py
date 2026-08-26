"""CỔNG DUYỆT — chỗ một đề xuất tham số phải đi qua trước khi thành bản mới.

Vòng nguy hiểm mà cổng này tồn tại để chặn:

    kết quả thị trường → AI phân tích → AI sửa tham số → chạy tiền thật

Vòng ấy hỏng không phải vì AI dở, mà vì nó **không có chỗ nào để sai một
cách nhìn thấy được**. Mỗi lượt tự vặn đều có vẻ hợp lý, và sau ba mươi
lượt thì tham số đã trôi đi rất xa mà không lượt nào là lượt sai rõ ràng.

Đường đúng:

    RESULT → DIAGNOSIS → PROPOSAL → OFFLINE TEST/REPLAY
           → **ACCEPTANCE GATE** → VERSIONED PARAMETER → LIVE

## Bảy luật, và mỗi luật chặn một cách trôi khác nhau

**1. Không đo thì không duyệt.** Đề xuất không kèm phép chạy lại là một ý
kiến. Ý kiến không được đổi cách chia tiền.

**2. Chưa đủ mẫu thì không duyệt.** Dưới ngưỡng, mọi chênh lệch là nhiễu, và
vặn theo nhiễu sẽ *trông như* tiến bộ vì lượt sau đo trên nhiễu khác.

**3. Không núm nào chạm cửa AN TOÀN.** Kiểm hai lớp — `chan_doan_he` đã lọc
một lần, nhưng cổng này kiểm lại từ danh sách gốc. Một lớp lọc là một lớp
có thể bị sửa nhầm; đây là lớp thứ hai và nó không tin lớp thứ nhất.

**4. Bước không vượt trần.** Một lượt gặp nhiễu thuận không được phép đẩy
ngưỡng ra chỗ mà mọi cơ hội đều lọt.

**5. Không ra ngoài khuôn `[min, max]` của núm.**

**6. Hoà thì KHÔNG duyệt.** Đứng yên là kết quả hợp lệ, và là kết quả thường
gặp nhất. Duyệt một thay đổi không đo được cải thiện là thêm nhiễu vào hệ
thống rồi gọi nó là tiến hoá.

**7. Tốt hơn nhờ ÔM RỦI RO ĐẬM HƠN thì KHÔNG duyệt.** Đây là luật quan
trọng nhất. Nới hết mọi trần thì luôn rót được nhiều vốn hơn và lợi suất
bình quân gần như luôn đẹp hơn — nên nếu cổng nhận nhánh ấy, cả vòng tiến
hoá sẽ học đúng một bài: **tự tháo phanh**.

## Qua cổng KHÔNG có nghĩa là được áp dụng

Cổng chỉ trả lời *"đề xuất này ĐỦ TƯ CÁCH"*. Áp dụng vẫn cần một người ký
tên — xem `trung_uong.ap_dung()` và `ban_tham_so.KhoThamSo.dat()`. Máy đo,
máy đề xuất, máy chặn; máy không tự ký.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .chan_doan_he import BUOC_TOI_DA, CUA_AN_TOAN_HE, NUT_TRUNG_UONG


@dataclass
class PhanQuyetDuyet:
    duDieuKien: bool
    lyDo: tuple[str, ...] = ()          # vì sao KHÔNG đủ điều kiện
    ghiChu: tuple[str, ...] = ()        # điều đáng biết dù có qua
    nut: str = ""
    tu: float | None = None
    den: float | None = None

    def tom_tat(self) -> dict:
        return {"duDieuKien": self.duDieuKien, "lyDo": list(self.lyDo),
                "ghiChu": list(self.ghiChu), "nut": self.nut,
                "tu": self.tu, "den": self.den,
                "loiNhac": "Đủ điều kiện KHÔNG phải là đã áp dụng. Áp dụng "
                           "vẫn cần một người ký tên."}


#: Kết luận nào của `chay_lai_he.doi_chieu()` được phép qua. Đúng MỘT.
KET_LUAN_QUA = ("b-tot-hon",)


def xet_duyet(deXuat, doDuoc: dict | None) -> PhanQuyetDuyet:
    """Bảy luật ở đầu file. Trả về đủ-điều-kiện hay không, kèm lý do.

    `deXuat` là `chan_doan_he.DeXuatHe`. `doDuoc` là kết quả
    `chay_lai_he.doi_chieu()`.
    """
    ly: list[str] = []
    ghi: list[str] = []
    nut = getattr(deXuat, "nut", "") or ""
    tu = getattr(deXuat, "tu", None)
    den = getattr(deXuat, "den", None)

    # ── luật 1 · không đo thì không duyệt ────────────────────────────────
    if not doDuoc:
        ly.append("không có phép đo kèm theo — một đề xuất không đo được là "
                  "một ý kiến, và ý kiến không đổi được cách chia tiền")
        return PhanQuyetDuyet(False, tuple(ly), (), nut, tu, den)

    # ── luật 2 · chưa đủ mẫu ─────────────────────────────────────────────
    if not doDuoc.get("duDeKetLuan"):
        ly.append("phép đo tự khai chưa đủ để kết luận: "
                  + str(doDuoc.get("vi") or "không rõ"))

    # ── luật 3 · cửa an toàn, kiểm LẠI từ danh sách gốc ──────────────────
    if nut in CUA_AN_TOAN_HE:
        ly.append(f"{nut} là CỬA AN TOÀN — không núm nào ở đây được vặn bằng "
                  f"vòng tiến hoá, dù phép đo có đẹp đến đâu")

    # ── luật 5 · phải nằm trong khuôn ────────────────────────────────────
    khuon = NUT_TRUNG_UONG.get(nut)
    if khuon is None:
        ly.append(f"{nut!r} không có trong bảng núm vặn được")
    elif den is None or tu is None:
        ly.append("đề xuất thiếu giá trị cũ hoặc mới")
    else:
        if not (khuon["min"] <= den <= khuon["max"]):
            ly.append(f"{nut}={den:g} ra ngoài khuôn "
                      f"[{khuon['min']:g}, {khuon['max']:g}]")
        # ── luật 4 · bước có trần ────────────────────────────────────────
        buoc = abs(den - tu)
        tran = abs(tu) * BUOC_TOI_DA
        if tran <= 0:
            tran = (khuon["max"] - khuon["min"]) * BUOC_TOI_DA
        if buoc > tran + 1e-9:
            ly.append(f"bước {buoc:g} vượt trần {tran:g} "
                      f"({BUOC_TOI_DA:.0%} giá trị hiện tại)")

    # ── luật 6 và 7 · đọc kết luận của phép đo ───────────────────────────
    ket = doDuoc.get("ketLuan")
    if doDuoc.get("duDeKetLuan"):
        if ket == "hoa":
            ly.append("phép đo cho HOÀ — đứng yên là kết quả hợp lệ, và "
                      "duyệt một thay đổi không đo được cải thiện là thêm "
                      "nhiễu rồi gọi nó là tiến hoá")
        elif ket == "a-tot-hon":
            ly.append("phép đo nói bản ĐANG CHẠY tốt hơn đề xuất")
        elif ket == "b-tot-hon-NHUNG-dam-hon":
            ly.append("đề xuất chỉ hơn nhờ ÔM RỦI RO ĐẬM HƠN — đây là đổi "
                      "rủi ro lấy lợi suất, không phải cải thiện. Nhận nhánh "
                      "này là dạy vòng tiến hoá rằng đường lên điểm là tự "
                      "tháo phanh")
        elif ket not in KET_LUAN_QUA:
            ly.append(f"kết luận {ket!r} không nằm trong danh sách được qua "
                      f"{KET_LUAN_QUA}")

    # ── ghi chú: qua rồi vẫn nên biết ────────────────────────────────────
    b = doDuoc.get("B") or {}
    if b.get("soDongHong"):
        ghi.append(f"{b['soDongHong']} dòng trong sổ đăng ký đọc lại không "
                   f"được — phép đo chạy trên phần còn lại")
    if b.get("moPhongVongDoi") is False:
        ghi.append("phép đo KHÔNG mô phỏng vòng đời vị thế, và KHÔNG đo lãi "
                   "lỗ — nó chỉ đo hình dạng phân bổ")

    return PhanQuyetDuyet(not ly, tuple(ly), tuple(ghi), nut, tu, den)
