"""ĐƯỜNG KHOÁ VỐN — cái trần 720 giờ đang chặn mất bao nhiêu.

## Câu hỏi nó trả lời

`ruiRoTong.khoaVonToiDaGio` mặc định 720 giờ (30 ngày), và lý do viết
trong `rui_ro_tong.py` là một câu đúng:

    khoá vốn ba tháng là từ chối mọi cơ hội tốt hơn xuất hiện trong ba
    tháng ấy, và chi phí đó không nằm trong APR của chính nó

Nhưng câu ấy nói về một CHI PHÍ, và hồi đặt trần thì chi phí ấy chưa đo
được — nên 720 là một con số chọn bằng suy luận, không phải bằng số.
Nay `xoay_cho.py` đo đúng cái chi phí đó: nó tính được đổi một chỗ đang
giữ sang một cơ hội tốt hơn thì lời ròng bao nhiêu, đã trừ phí hai đầu.

Nên câu hỏi đổi được thành một câu đo được: **nới trần khoá lên X giờ thì
rót thêm được bao nhiêu, ở lợi suất nào?**

Đo trên máy sống 30/08/2026, vốn ảo một triệu:

    ty                        vốn đang giữ    khoá
    lending.rate_rotation.v1      499.973 $   0 giờ    ← chạm trần tranMotTy
    yield.pendle_pt.v1                  0 $   —        ← 12 tờ trình, KHÔNG tờ nào qua

Mười hai tờ trình của Pendle PT đều khoá 2.116–3.292 giờ (88–137 ngày),
tức đều trên trần 720. Chúng khai `netUocBps` 65–449 bps, còn phần vốn
đang chạy thì 1,7 bps. Cả một động cơ đứng ngoài vì đúng một tham số.

## Bảng này KHÔNG đề xuất nới trần

Nới trần khoá vốn là đổi hành vi tiền bạc, và đó là cửa `dat_tham_so` —
cửa ĐÒI TÊN NGƯỜI. Bảng này chỉ đặt con số lên bàn để câu quyết định ấy
được quyết bằng số chứ không bằng cảm giác, và nó nói thẳng cả phần
NGƯỢC LẠI: khoá càng lâu thì càng nhiều cơ hội tốt hơn bị bỏ lỡ, và
`xoay_cho` đo được cái bỏ lỡ ấy.

Cùng ba cái bẫy của `duong_suc_chua.py`, và cả ba đều bị chặn ở đây theo
cùng một lối: cơ hội không khai lãi thì BỎ chứ không coi là 0; không
khai sức chứa thì cũng BỎ; và vốn không rót hết thì phần dư ăn lãi 0.
"""
from __future__ import annotations

from dataclasses import dataclass, field

#: Các mức trần khoá vốn đem ra thử, GIỜ. `None` = không trần.
#: 720 là mặc định đang chạy; 2160 = 90 ngày, đủ cho phần lớn PT Pendle.
MUC_MAC_DINH = (720.0, 1440.0, 2160.0, 4320.0, None)


@dataclass
class MotTran:
    tranGio: float | None
    soCoHoi: int              # bao nhiêu cơ hội LỌT qua trần này
    sucChuaUsd: float         # tổng sức chứa của chúng
    rotDuocUsd: float         # rót được bao nhiêu trong số vốn đưa vào
    aprTrenCaTuiUsd: float    # lãi bình quân trên CẢ vốn, dư ăn 0
    khoaBinhQuanGio: float | None   # vốn rót ra bị khoá bình quân bao lâu

    def tom_tat(self) -> dict:
        return {"tranGio": self.tranGio, "soCoHoi": self.soCoHoi,
                "sucChuaUsd": self.sucChuaUsd,
                "rotDuocUsd": self.rotDuocUsd,
                "aprTrenCaTui": self.aprTrenCaTuiUsd,
                "khoaBinhQuanGio": self.khoaBinhQuanGio}


@dataclass
class DuongKhoaVon:
    vonUsd: float = 0.0
    tranDangChayGio: float | None = None
    muc: list = field(default_factory=list)
    soBoViThieuLai: int = 0
    soBoViThieuSucChua: int = 0
    vi: str = ""

    def tom_tat(self) -> dict:
        return {"vonUsd": self.vonUsd,
                "tranDangChayGio": self.tranDangChayGio,
                "muc": [m.tom_tat() for m in self.muc],
                "soBoViThieuLai": self.soBoViThieuLai,
                "soBoViThieuSucChua": self.soBoViThieuSucChua,
                "vi": self.vi}


def do_duong_khoa_von(toTrinh: list, vonUsd: float,
                      tranDangChayGio: float | None = None,
                      muc=MUC_MAC_DINH) -> DuongKhoaVon:
    """Nới trần khoá lên từng mức thì rót thêm được bao nhiêu, lãi bao nhiêu."""
    from .xoay_cho import apr_tu_to_trinh

    ra = DuongKhoaVon(vonUsd=float(vonUsd),
                      tranDangChayGio=tranDangChayGio)
    ds: list[tuple[float, float, float]] = []      # (apr, sức chứa, khoá giờ)
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
        # Không khai khoá thì đọc là 0 — và ở đây `0` là đúng nghĩa «không
        # khoá», không phải «chưa đo». `to_trinh.kiem()` đã chặn giá trị
        # âm, còn `None` nghĩa là ty không có khái niệm khoá vốn.
        kh = t.get("khoaVonDenGio")
        ds.append((apr, float(sc), 0.0 if kh is None else float(kh)))
    ds.sort(key=lambda x: -x[0])

    for tran in muc:
        con, rot, tong, dem, khoaVon = float(vonUsd), 0.0, 0.0, 0, 0.0
        chua = 0.0
        for apr, sc, kh in ds:
            if tran is not None and kh > float(tran):
                continue
            dem += 1
            chua += sc
            if con <= 0:
                continue
            lay = min(con, sc)
            rot += lay
            tong += lay * apr
            khoaVon += lay * kh
            con -= lay
        ra.muc.append(MotTran(
            tranGio=tran, soCoHoi=dem, sucChuaUsd=chua, rotDuocUsd=rot,
            # Phần dư ăn lãi 0 — cùng lý do `duong_suc_chua.py`.
            aprTrenCaTuiUsd=(tong / float(vonUsd)) if vonUsd > 0 else 0.0,
            khoaBinhQuanGio=(khoaVon / rot) if rot > 0 else None))
    ra.vi = _vi(ra)
    return ra


def _vi(d: DuongKhoaVon) -> str:
    if not d.muc:
        return ("chưa dựng được đường cong — không cơ hội nào khai đủ lãi "
                "và sức chứa")
    hien = next((m for m in d.muc if m.tranGio == d.tranDangChayGio), None)
    rong = d.muc[-1]
    if hien is None or hien is rong:
        return (f"{rong.soCoHoi} cơ hội, rót được "
                f"{rong.rotDuocUsd:,.0f} USD, lãi "
                f"{rong.aprTrenCaTuiUsd:.2f}%/năm trên cả túi.")
    themApr = rong.aprTrenCaTuiUsd - hien.aprTrenCaTuiUsd
    themChua = rong.sucChuaUsd - hien.sucChuaUsd
    if abs(themApr) < 1e-9 and themChua <= 0:
        return (f"trần khoá {d.tranDangChayGio:.0f} giờ KHÔNG chặn gì ở lượt "
                f"này — bỏ trần đi cũng không đổi được gì.")
    # Cái đổi KHÔNG phải số tiền rót ra — tiền mặt vẫn ngần ấy. Cái đổi là
    # tiền ấy được rót vào ĐÂU. Nói "thêm 0 USD" là đúng số mà sai câu
    # chuyện, nên câu này dẫn bằng lợi suất.
    return (f"cùng {d.vonUsd:,.0f} USD tiền mặt: trần khoá đang chạy "
            f"{d.tranDangChayGio:.0f} giờ cho {hien.soCoHoi} cơ hội và "
            f"{hien.aprTrenCaTuiUsd:.2f}%/năm; BỎ trần thì {rong.soCoHoi} "
            f"cơ hội và {rong.aprTrenCaTuiUsd:.2f}%/năm — hơn "
            f"{themApr:+.2f} điểm phần trăm, đổi lại vốn bị khoá bình quân "
            f"{rong.khoaBinhQuanGio:,.0f} giờ. Sức chứa cũng nới từ "
            f"{hien.sucChuaUsd:,.0f} lên {rong.sucChuaUsd:,.0f} USD, nên ở "
            f"mức vốn lớn hơn thì trần này còn chặn nhiều hơn nữa. "
            f"Đây là phép ĐO, KHÔNG phải đề xuất: nới trần là cửa "
            f"`dat_tham_so`, đòi tên người — và cái giá của khoá lâu, tức "
            f"bỏ lỡ cơ hội tốt hơn xuất hiện trong ngần ấy giờ, thì bảng "
            f"Xoay Chỗ đo chứ bảng này không đo.")
