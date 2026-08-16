"""Biến hồ sơ trader thành KỸ NĂNG đọc được — `skills/traders/<sàn>/<mã>/`.

Tài liệu thiết kế muốn mỗi trader thành một thư mục kỹ năng để bộ não "hỏi ý
kiến" như hỏi một chuyên gia. Ở đây làm đúng vậy, với hai ràng buộc:

**1. Không cho vào prompt tự động.** `brain.load_skills()` nạp mọi `SKILL.md`
trong `skills/`, nên nếu ghi thẳng vào đó thì mỗi lượt gọi model sẽ kéo theo
hàng chục hồ sơ trader — prompt phình ra, tiền tăng, và tệ nhất là bộ não bị
dìm trong dữ liệu chưa qua kiểm chứng. Nên chúng nằm ở `skills/traders/` và
`load_skills()` **cố tình bỏ qua** thư mục đó. Ai muốn dùng thì truy hồi có
chọn lọc — đúng như `recall()` làm với bài học.

**2. Ghi rõ đây là QUAN SÁT, không phải lời khuyên.** Mỗi file mở đầu bằng một
đoạn nói thẳng: đây là hành vi đo được của một người lạ trên internet, chưa qua
backtest, và không được dùng làm lý do vào lệnh.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .bus import bus
from .config import SKILLS_DIR

GOC = SKILLS_DIR / "traders"

DAU = """<!-- SINH TỰ ĐỘNG từ dữ liệu công khai. ĐỪNG SỬA TAY. -->

> **Đây là QUAN SÁT, không phải lời khuyên.** Hồ sơ dưới đây là hành vi đo được
> của một tài khoản công khai trên sàn — không phải một chiến lược đã kiểm
> chứng. Không được dùng nó làm lý do vào lệnh. Mọi mẫu hành vi rút ra từ đây
> phải đi qua backtest rồi cửa duyệt champion như mọi ý tưởng khác.
>
> Mục đích của hồ sơ này là **giải phẫu cách người ta giao dịch**, không phải
> sao chép họ.
"""


def _dong(k: str, v: Any) -> str:
    return f"- **{k}**: {v}\n"


def viet_mot(t: dict) -> Path | None:
    san = t.get("san", "khac")
    ma = (t.get("diaChi") or "")[:16]
    if not ma:
        return None
    d = GOC / san / ma
    d.mkdir(parents=True, exist_ok=True)

    hs = t.get("hoSo") or {}
    gp = t.get("giaiPhau") or {}
    diem = t.get("diem") or {}
    pc = gp.get("phongCach") or {}
    cl = gp.get("catLo") or {}
    dd = gp.get("daDangCheDo") or {}
    ml = gp.get("mauLapLai") or {}

    md = [DAU, f"\n# Trader `{ma}` · {san}\n\n"]
    md.append(f"**Điểm chất lượng {diem.get('diem')} · hạng {diem.get('hang')}** "
              f"(đo được {diem.get('doPhu')}% trọng số)\n\n")
    if t.get("anMay", {}).get("nghiNgo"):
        md.append("> ⚠ **Nghi thành tích do may**: "
                  + " · ".join(t["anMay"]["lyDo"]) + "\n\n")

    md.append("## Hành vi\n\n")
    md.append(_dong("phong cách", f"{pc.get('phongCach') or '—'} "
                                  f"(độ tin {pc.get('doTin')})"))
    md.append(_dong("giữ lệnh (trung vị)", f"{hs.get('giuTrungVi_gio')} giờ"))
    md.append(_dong("tỉ lệ LONG", hs.get("tyLeLong")))
    md.append(_dong("vào chủ động (taker)", hs.get("tyLeChuDong")))
    md.append(_dong("coin hay đánh", ", ".join(f"{c} ({n})" for c, n in
                                               (hs.get("coinHayDanh") or [])[:5])))
    md.append(_dong("tỉ lệ thắng", f"{hs.get('tyLeThang')}%"))
    md.append(_dong("lãi từ một lệnh lớn nhất",
                    f"{hs.get('phanTramLaiTuLenhLonNhat')}% tổng lãi"))

    md.append("\n## Cách cắt lỗ\n\n")
    md.append(_dong("kiểu", cl.get("kieu") or "chưa đọc được"))
    md.append(_dong("vì sao kết luận vậy", cl.get("viSao")))
    md.append(_dong("mất trung bình", f"{cl.get('matTrungBinhPct')}% "
                                      f"/ {cl.get('matTrungBinhAtr')}×ATR"))
    md.append(_dong("bị thanh lý", f"{cl.get('tyLeThanhLy')}"))

    md.append("\n## Ăn được ở chế độ nào\n\n")
    if dd.get("chiTiet"):
        md.append("| chế độ | vòng | thắng | pnl |\n|---|---|---|---|\n")
        for cd, g in sorted(dd["chiTiet"].items(), key=lambda x: -x[1]["so"]):
            md.append(f"| {cd} | {g['so']} | {g['tyLeThang']}% | {g['pnl']} |\n")
    else:
        md.append("_chưa đủ dữ liệu._\n")

    md.append("\n## Mẫu hành vi lặp lại\n\n")
    if ml.get("co"):
        md.append("| mẫu | loại | số lần | phủ | thắng | lãi TB |\n|---|---|---|---|---|---|\n")
        for m in ml["mau"][:10]:
            md.append(f"| {m['mau']} | {m['loai']} | {m['soLan']} | {m['tyLePhu']}% "
                      f"| {m['tyLeThang']}% | {m['laiTrungBinh']} |\n")
        md.append(f"\n_{ml.get('ghiChu', '')}_\n")
    else:
        md.append(f"_{ml.get('viSao', 'chưa đủ dữ liệu')}._\n")

    (d / "SKILL.md").write_text("".join(md), encoding="utf-8")
    (d / "ho-so.json").write_text(
        json.dumps({k: v for k, v in t.items() if not k.startswith("_")},
                   ensure_ascii=False, indent=1), encoding="utf-8")
    return d


def viet_tat_ca(traders: list[dict]) -> dict:
    n = 0
    for t in traders:
        if viet_mot(t):
            n += 1
    (GOC / "README.md").write_text(
        DAU + "\n# Kho hồ sơ trader\n\n"
        "Thư mục này **KHÔNG** được `brain.load_skills()` nạp vào prompt tự động —\n"
        "xem `trader_thanh_ky_nang.py` để biết vì sao. Truy hồi có chọn lọc thay vì\n"
        "nhét tất cả vào mỗi lượt gọi.\n\n"
        f"Hiện có **{n}** hồ sơ.\n", encoding="utf-8")
    bus.emit("hoc", "trader-thanh-ky-nang", f"ghi {n} hồ sơ trader ra skills/traders/")
    return {"so": n, "thuMuc": str(GOC)}
