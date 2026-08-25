"""RỦI RO TỔNG — tầng thứ hai, và là quyền lực trung tâm.

Hai tầng rủi ro, và chúng trả lời hai câu KHÁC HẲN nhau:

    tầng 1 · CỔNG TY      "cơ hội này có hợp lệ không?"
                          chuyên môn: mốc kết toán, lệch mark, đồng hồ…
                          ty tự biết, trung ương không hiểu nổi

    tầng 2 · RỦI RO TỔNG  "cho tiền vào đây thì DANH MỤC ra sao?"
                          phơi nhiễm cảng, tài sản, chuỗi, đòn bẩy
                          trung ương thấy, KHÔNG ty nào thấy

Ty nói *"cơ hội ngon, xin $500"*. Trung ương nhìn danh mục thấy Binance đã
chiếm 45% vốn, và trả lời *"chỉ $100"*. Đó là chuyện không ty nào tự làm
được, vì không ty nào biết mười hai ty kia đang giữ gì.

## Không phải NHẬN/TỪ CHỐI — mà là CẮT BỚT

Đây là chỗ khác biệt quan trọng nhất so với cổng ty. Cổng ty nhị phân:
PASS/REJECT. Rủi Ro Tổng trả về một **trần**:

    xin $500 → cho $100    vì Binance sắp chạm trần phơi nhiễm
    xin $500 → cho $0      vì đã chạm trần rồi
    xin $500 → cho $500    vì còn rộng

Nhị phân ở tầng này là lãng phí: một cơ hội tốt bị từ chối sạch chỉ vì xin
hơi nhiều thì ta mất cả phần đáng lẽ nhận được.

## Trần tính trên NAV, không trên tiền mặt

Tiền mặt tụt dần khi cấp vốn, nên lấy tiền mặt làm mẫu số thì trần tự nới ra
theo mỗi lần cấp — cấp càng nhiều, trần càng lỏng. Đó là vòng phản hồi
dương, và nó chỉ dừng khi hết sạch tiền.

## `None` trong rủi ro là CHƯA BIẾT, và chưa biết thì phải TRỪ ĐIỂM

Tờ trình khai `giaoThuc = None` nghĩa là ty không đánh giá nổi mặt ấy. Coi
`None` như 0 là thưởng cho sự thiếu hiểu biết: một ty không biết gì sẽ có
điểm rủi ro thấp nhất và được cấp vốn nhiều nhất.

Nên ở đây `None` bị tính là `PHAT_CHUA_DO` — một mức phạt vừa phải, không
phải chặn hẳn. Chặn hẳn thì bản v0.1 nào cũng chết ngay lúc mới sinh; không
phạt gì thì cả hệ thống trôi về phía những ty mù nhất.
"""
from __future__ import annotations

from dataclasses import dataclass, field

#: Mỗi mặt rủi ro chưa đo được tính như mức này. Không phải 0 (thưởng cho
#: sự mù) và không phải 1 (chặn hẳn mọi bản đầu tiên).
PHAT_CHUA_DO = 0.35

MAC_DINH = {
    # ── trần phơi nhiễm, phần của NAV ────────────────────────────────────
    "tranMotCang": 0.35,        # một cảng sập không được cuốn quá 35% vốn
    "tranMotTaiSanRong": 0.25,  # phơi nhiễm RÒNG một tài sản
    "tranMotTaiSanTho": 0.60,   # phơi nhiễm THÔ một tài sản
    "tranMotChuoi": 0.40,
    "tranMotTy": 0.50,          # một ty không được ôm quá nửa danh mục
    "tranTongDungVon": 0.80,    # luôn giữ ≥20% tiền mặt
    "tranMotCoHoi": 0.15,       # một cơ hội đơn lẻ

    # ── chất lượng tờ trình ──────────────────────────────────────────────
    "ruiRoToiDa": 0.60,         # điểm rủi ro gộp
    "tinCayToiThieu": 0.50,
    "netMoiGioToiThieuBps": 0.0,
    "batBuocDuMoHinhPhi": False,   # v0.1 chưa ty nào đủ; xem README
    "batBuocDoDuocSucChua": True,  # không biết chứa bao nhiêu thì không rót
}


@dataclass
class PhanQuyet:
    """Kết quả xét một tờ trình. `choToiDaUsd` là thứ Phân Bổ phải tôn trọng."""
    maToTrinh: str
    chienLuoc: str
    xinUsd: float
    choToiDaUsd: float
    diemRuiRo: float | None
    lyDo: tuple[str, ...] = ()
    lyDoCat: tuple[str, ...] = ()

    @property
    def duyet(self) -> bool:
        return self.choToiDaUsd > 0.0

    @property
    def biCat(self) -> bool:
        return 0.0 < self.choToiDaUsd < self.xinUsd - 1e-9

    def tom_tat(self) -> dict:
        return {"maToTrinh": self.maToTrinh, "chienLuoc": self.chienLuoc,
                "xinUsd": self.xinUsd, "choToiDaUsd": self.choToiDaUsd,
                "diemRuiRo": self.diemRuiRo, "duyet": self.duyet,
                "biCat": self.biCat, "lyDo": list(self.lyDo),
                "lyDoCat": list(self.lyDoCat)}


class RuiRoTong:
    def __init__(self, cau_hinh: dict | None = None) -> None:
        self.c = {**MAC_DINH, **(cau_hinh or {})}

    # ── điểm rủi ro gộp ───────────────────────────────────────────────────
    def diem(self, tt) -> tuple[float, tuple[str, ...]]:
        """Gộp sáu mặt rủi ro thành một điểm [0,1], kèm mặt nào phải đoán.

        Lấy MAX chứ không lấy trung bình — rủi ro không bù trừ. Một cơ hội an
        toàn năm mặt và chết ở mặt thứ sáu vẫn là một cơ hội chết.
        """
        from .to_trinh import MAT_RUI_RO
        cao, chua_do = 0.0, []
        for m in MAT_RUI_RO:
            v = getattr(tt.ruiRo, m)
            if v is None:
                chua_do.append(m)
                cao = max(cao, PHAT_CHUA_DO)
            else:
                cao = max(cao, float(v))
        return cao, tuple(chua_do)

    # ── xét một tờ trình ──────────────────────────────────────────────────
    def xet(self, tt, danh_muc) -> PhanQuyet:
        """Xét MỘT tờ trình trên nền danh mục HIỆN TẠI.

        Xét từng tờ một trên danh mục hiện tại có một hạn chế đã biết: hai tờ
        trình cùng chạm Binance, xét riêng thì cả hai đều lọt, cấp cả hai thì
        vượt trần. `Phân Bổ` xử chỗ đó bằng cách cấp TUẦN TỰ và cập nhật danh
        mục sau mỗi lần — xem `phan_bo.py`.
        """
        c = self.c
        nav = danh_muc.navUsd
        ly, cat = [], []

        # ── loại thẳng: tờ trình sai khuôn ───────────────────────────────
        if not tt.hop_le:
            return PhanQuyet(tt.ma, tt.chienLuoc, tt.vonCanUsd, 0.0, None,
                             ("tờ trình SAI KHUÔN: " + "; ".join(tt.kiem()),))

        d, chua_do = self.diem(tt)
        if d > float(c["ruiRoToiDa"]):
            ly.append(f"điểm rủi ro {d:.2f} > trần {float(c['ruiRoToiDa']):.2f}"
                      + (f" (chưa đo: {', '.join(chua_do)})" if chua_do else ""))

        if tt.tinCay is not None and tt.tinCay < float(c["tinCayToiThieu"]):
            ly.append(f"độ tin {tt.tinCay:.2f} < ngưỡng "
                      f"{float(c['tinCayToiThieu']):.2f}")

        if tt.net_moi_gio_bps < float(c["netMoiGioToiThieuBps"]):
            ly.append(f"NET {tt.net_moi_gio_bps:.3f} bps/giờ < ngưỡng "
                      f"{float(c['netMoiGioToiThieuBps']):.3f}")

        if c["batBuocDuMoHinhPhi"] and not tt.moHinhPhiDuChua:
            ly.append("mô hình phí chưa đủ: thiếu "
                      + ", ".join(tt.phiConThieu))

        if c["batBuocDoDuocSucChua"] and tt.sucChuaToiDaUsd is None:
            ly.append("chưa đo được sức chứa — không biết rót bao nhiêu thì "
                      "chính cơ hội tự giết mình")

        if ly:
            return PhanQuyet(tt.ma, tt.chienLuoc, tt.vonCanUsd, 0.0, d,
                             tuple(ly))

        # ── còn sống thì tính TRẦN, không trả nhị phân ───────────────────
        tran = tt.vonCanUsd

        chat_nhat = None

        def hep(moi: float, vi: str):
            """Siết trần xuống `moi` nếu chỗ ấy chật hơn. Nhớ chỗ chật NHẤT.

            Nhớ `chat_nhat` chứ không chỉ gom vào `cat`: khi trần bị siết về
            0 thì đây là một lần TỪ CHỐI, và nó phải chỉ đúng cái trần đã
            chặn. Đọc cả danh sách `cat` thì thấy năm dòng và không biết dòng
            nào mới là dòng quyết.
            """
            nonlocal tran, chat_nhat
            moi = max(0.0, moi)
            if moi < tran - 1e-9:
                cat.append(f"{vi}: còn {moi:.2f} USD")
                tran = moi
                chat_nhat = vi

        if tt.sucChuaToiDaUsd is not None:
            hep(tt.sucChuaToiDaUsd, "sức chứa thị trường")
        hep(nav * float(c["tranMotCoHoi"]), "trần một cơ hội")
        hep(danh_muc.tienMatUsd, "tiền mặt còn lại")
        hep(nav * float(c["tranTongDungVon"]) - danh_muc.daCamKetUsd,
            "trần tổng dùng vốn")

        # Phơi nhiễm: mỗi chân của tờ trình cộng thêm vào một cảng/chuỗi/tài
        # sản. Trần còn lại là chỗ CHẬT NHẤT trong các chân — chân nào đụng
        # trần trước thì chân ấy quyết, vì cả hai chân phải vào được.
        pn_cang = danh_muc.phoi_nhiem_cang()
        pn_tho = danh_muc.phoi_nhiem_tho()
        pn_rong = danh_muc.phoi_nhiem_rong()
        pn_chuoi = danh_muc.phoi_nhiem_chuoi()
        pn_ty = danh_muc.phoi_nhiem_ty()

        for ch in tt.chan:
            hep(nav * float(c["tranMotCang"]) - pn_cang.get(ch.cang, 0.0),
                f"trần cảng {ch.cang}")
            hep(nav * float(c["tranMotTaiSanTho"]) - pn_tho.get(ch.taiSan, 0.0),
                f"trần phơi nhiễm thô {ch.taiSan}")
            if ch.chuoi:
                hep(nav * float(c["tranMotChuoi"]) - pn_chuoi.get(ch.chuoi, 0.0),
                    f"trần chuỗi {ch.chuoi}")

        # Phơi nhiễm RÒNG: chỉ tính phần cơ hội này LÀM LỆCH thêm. Một cặp
        # delta-neutral (LONG + SHORT cùng tài sản) không làm lệch gì, nên
        # nó KHÔNG bị trần ròng chặn — đúng như phải thế.
        lech: dict[str, int] = {}
        for ch in tt.chan:
            lech[ch.taiSan] = lech.get(ch.taiSan, 0) + ch_dau(ch)
        for ts, hs in lech.items():
            if hs == 0:
                continue                       # trung tính, không chạm trần ròng
            hien = pn_rong.get(ts, 0.0)
            tran_ts = nav * float(c["tranMotTaiSanRong"])
            con = (tran_ts - hien) if hs > 0 else (tran_ts + hien)
            hep(con / abs(hs), f"trần phơi nhiễm ròng {ts}")

        hep(nav * float(c["tranMotTy"]) - pn_ty.get(tt.chienLuoc, 0.0),
            f"trần một ty {tt.chienLuoc}")

        tran = round(max(0.0, tran), 2)
        if tran <= 0.0:
            # Siết về 0 là TỪ CHỐI, không phải "duyệt 0 đồng". Phải trả về
            # `lyDo` chứ không chỉ `lyDoCat`: `duyet` đọc `choToiDaUsd`, nên
            # một phán quyết 0 đồng mà `lyDo` rỗng sẽ hiện trong phễu thành
            # một tờ bị từ chối với ô lý do trống — và ô trống thì không ai
            # đọc thành "trần cảng đã hết chỗ".
            return PhanQuyet(tt.ma, tt.chienLuoc, tt.vonCanUsd, 0.0, d,
                             (f"hết chỗ ở {chat_nhat}"
                              if chat_nhat else "hết chỗ, không rõ ở đâu",),
                             tuple(cat))
        return PhanQuyet(tt.ma, tt.chienLuoc, tt.vonCanUsd, tran, d, (),
                         tuple(cat))

    def tom_tat(self) -> dict:
        return {**dict(self.c), "phatChuaDo": PHAT_CHUA_DO}


def ch_dau(chan) -> int:
    """Dấu phơi nhiễm của một chân trong tờ trình (chưa vào danh mục)."""
    return -1 if chan.ben in ("SHORT", "DI_VAY") else 1
