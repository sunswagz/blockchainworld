"""Chẩn đoán — bệnh ĐO ĐƯỢC, không phải cảm giác.

Vòng tiến hoá không được phép vặn bừa. Nó chỉ được động vào một núm khi có
một triệu chứng **đo được từ băng** chỉ đúng vào núm ấy. Không triệu chứng
nào vượt ngưỡng thì **đứng yên là kết quả hợp lệ** — và đó là kết cục thường
gặp nhất, đúng như phải thế.

Mỗi triệu chứng mang theo `bangChung`: những con số dựng nên nó. Không có
bằng chứng thì người đọc không cãi lại được, mà một cỗ máy tự vặn tham số thì
phải cãi lại được.

## Vì sao "chưa đủ mẫu" là triệu chứng ĐẦU TIÊN

Với 5 cơ hội hậu kiểm được, mọi con số kỳ vọng đều là tiếng ồn. Vặn ngưỡng
dựa trên đó là học thuộc nhiễu — và tệ hơn, nó sẽ *trông như* đang tiến bộ,
vì lượt sau đo lại trên 5 mẫu khác cũng cho một con số khác.
"""
from __future__ import annotations

from dataclasses import dataclass, field

#: Dưới ngần này cơ hội hậu kiểm được thì không chẩn gì cả.
TOI_THIEU_MAU = 30

#: Dự đoán lệch thực nhận quá ngần này (bps, trung bình) là mô hình lạc quan
#: có hệ thống — không phải xui.
NGUONG_LECH_DU_DOAN_BPS = 2.0


@dataclass
class TrieuChung:
    ma: str
    nang: int                    # 1 nhẹ · 2 vừa · 3 nặng
    moTa: str
    bangChung: dict = field(default_factory=dict)
    nutGoiY: list[str] = field(default_factory=list)

    def tom_tat(self) -> dict:
        return {"ma": self.ma, "nang": self.nang, "moTa": self.moTa,
                "bangChung": self.bangChung, "nutGoiY": list(self.nutGoiY)}


def chan_doan(kq, boQuaTong: dict | None = None) -> list[TrieuChung]:
    """Đọc kết quả chạy lại, trả về danh sách bệnh đo được.

    `kq` là `chay_lai.KetQua`. `boQuaTong` là bảng đếm lý do từ chối trên CẢ
    băng — nó nói cửa nào đang chặn, thứ mà `kq` một mình không nói được.
    """
    ra: list[TrieuChung] = []
    bq = dict(boQuaTong or kq.boQua)
    tong_bo = sum(bq.values()) or 1

    # ── 1. chưa đủ mẫu ───────────────────────────────────────────────────
    if kq.soDoDuoc < TOI_THIEU_MAU:
        ra.append(TrieuChung(
            "thieu-mau", 1,
            f"mới {kq.soDoDuoc} cơ hội hậu kiểm được — chưa đủ để chẩn gì. "
            f"Chạy thêm, đừng vặn.",
            {"soDoDuoc": kq.soDoDuoc, "canToiThieu": TOI_THIEU_MAU,
             "soKhung": kq.soKhung, "soQuaCua": kq.soQuaCua}))
        return ra                # dừng hẳn: mọi chẩn đoán khác đều vô nghĩa

    # ── 2. không cơ hội nào qua cửa suốt cả băng ─────────────────────────
    if kq.soQuaCua == 0 and kq.soCoHoi > 0:
        chan_chinh = max(bq, key=bq.get) if bq else "?"
        ra.append(TrieuChung(
            "cua-qua-chat", 2,
            f"{kq.soCoHoi} cặp đã cân, KHÔNG cặp nào qua cửa. Cửa chặn nhiều "
            f"nhất: {chan_chinh}.",
            {"soCoHoi": kq.soCoHoi, "chanChinh": chan_chinh,
             "tiLe": bq.get(chan_chinh, 0) / tong_bo, "boQua": bq},
            _nut_cho_cua(chan_chinh)))

    # ── 3. mô hình lạc quan có hệ thống ──────────────────────────────────
    lech = kq.sai_so_du_doan_bps
    if lech is not None and lech > NGUONG_LECH_DU_DOAN_BPS:
        ra.append(TrieuChung(
            "du-doan-lac-quan", 3,
            f"dự đoán thu cao hơn thực nhận trung bình {lech:.2f} bps mỗi cơ "
            f"hội — funding tụt trước khi tới mốc, không phải xui.",
            {"saiSoBps": lech, "soDoDuoc": kq.soDoDuoc,
             "tongDuDoanBps": kq.tongThuDuDoanBps,
             "tongThucBps": kq.tongThuThucBps},
            ["giuGio", "netToiThieuBps"]))

    # ── 4. kỳ vọng âm ────────────────────────────────────────────────────
    kv = kq.ky_vong_bps
    if kv is not None and kv < 0:
        ra.append(TrieuChung(
            "ky-vong-am", 3,
            f"kỳ vọng {kv:.2f} bps mỗi cơ hội — bộ tham số này LỖ, không phải "
            f"lãi ít.",
            {"kyVongBps": kv, "soLai": kq.soLai, "soLo": kq.soLo,
             "tiLeLai": kq.ti_le_lai, "tệNhấtBps": kq.netThucTeNhatBps},
            ["netToiThieuBps", "grossToiThieuBpsNgay", "giuGio"]))

    # ── 5. đuôi nặng: lãi đều nhưng một lần lỗ xoá sạch ──────────────────
    if kq.soDoDuoc >= TOI_THIEU_MAU and kq.ti_le_lai is not None \
            and kq.ti_le_lai > 0.7 and kv is not None and kv <= 0:
        ra.append(TrieuChung(
            "duoi-nang", 3,
            f"thắng {kq.ti_le_lai:.0%} số lần mà kỳ vọng vẫn {kv:.2f} bps — "
            f"lãi nhỏ đều đặn, lỗ lớn hiếm hoi. Tỉ lệ thắng đang nói dối.",
            {"tiLeLai": kq.ti_le_lai, "kyVongBps": kv,
             "tệNhấtBps": kq.netThucTeNhatBps},
            ["netToiThieuBps"]))

    # ── 6. cửa sổ giữ hụt mốc ────────────────────────────────────────────
    hut = bq.get("khong-moc", 0)
    if hut / tong_bo > 0.3:
        ra.append(TrieuChung(
            "cua-so-hut-moc", 2,
            f"{hut / tong_bo:.0%} số lần bị chặn vì KHÔNG mốc kết toán nào rơi "
            f"vào cửa sổ giữ — cửa sổ đang quá ngắn so với chu kỳ của sàn.",
            {"soLanHut": hut, "tongBoQua": tong_bo}, ["giuGio"]))

    # ── 7. đồng hồ lệch ──────────────────────────────────────────────────
    if bq.get("lech-dong-ho", 0) > 0:
        ra.append(TrieuChung(
            "dong-ho-lech", 3,
            f"{bq['lech-dong-ho']} lần bị chặn vì đồng hồ máy lệch giờ sàn. "
            f"Đây KHÔNG phải bệnh vặn tham số chữa được — chỉnh NTP.",
            {"soLan": bq["lech-dong-ho"]}, []))

    if not ra:
        ra.append(TrieuChung(
            "khoe", 0,
            f"không triệu chứng nào vượt ngưỡng — kỳ vọng {kv:.2f} bps trên "
            f"{kq.soDoDuoc} mẫu." if kv is not None else "không triệu chứng nào",
            {"kyVongBps": kv, "soDoDuoc": kq.soDoDuoc}))
    return ra


def _nut_cho_cua(ma_cua: str) -> list[str]:
    """Cửa nào chặn thì gợi ý núm nào — và có cửa KHÔNG có núm nào cả.

    `thieu-mark`, `lech-dong-ho`, `moc-uoc-luong` cố ý trả về danh sách rỗng:
    chúng là cửa AN TOÀN, không phải ngưỡng hiệu năng. Nới chúng ra để có
    thêm cơ hội là gỡ đúng thứ đang bảo vệ mình.
    """
    return {
        "gross-mong": ["grossToiThieuBpsNgay"],
        "net-am": ["netToiThieuBps", "giuGio"],
        "khong-moc": ["giuGio"],
        "lech-mark": ["lechMarkToiDaBps"],
        "du-lieu-cu": ["tuoiToiDaGiay"],
        "thieu-mark": [],
        "lech-dong-ho": [],
        "moc-uoc-luong": [],
        "khong-dau-thoi-gian": [],
    }.get(ma_cua, [])
