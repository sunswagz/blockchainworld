"""Champion / Challenger — cửa duy nhất để một chiến thuật được chạy thật.

Lấy đúng triết lý `chien_luoc.py` của Tử Cấm Thành, đổi số đo cho hợp thị
trường tiên đoán. Điểm cốt tử giống hệt: **không có `--force`**. Không có
đường tắt nào để một chiến thuật "trông đẹp" nhảy thẳng vào tiền thật.

## Vì sao cần cửa này, dù đã có Risk Engine

Risk Engine chặn theo TỪNG LỆNH: lệnh này quá to, nguồn này quá cũ, market
này chạm trần. Nó không trả lời được câu khác hẳn: *chiến thuật này, xét
trên hàng trăm lệnh, có thật sự tốt hơn cái đang chạy không?*

Không có cửa này thì cách một chiến thuật tồi bị loại là **mất tiền cho tới
khi ai đó để ý**. Với 5 phút một khung, "cho tới khi ai đó để ý" là rất
nhiều khung.

## Bốn cửa, phải qua CẢ BỐN

1. **Đủ mẫu ngoài mẫu.** Thắng 8/10 không nói lên gì.
2. **Kỳ vọng dương.** Không phải tỉ lệ thắng — kỳ vọng, đã trừ phí.
3. **Vượt đương kim.** Bằng thì giữ đương kim: đổi cũng tốn phí chuyển
   trạng thái, và cái đang chạy đã có lịch sử dài hơn.
4. **Đuôi không tệ hơn.** Đây là cửa mà thị trường tiên đoán cần hơn hẳn
   thị trường thường: ngón cận-kết-quả có thể vượt cả ba cửa trên rồi mất
   sạch trong một khung. Một thách đấu có kỳ vọng nhỉnh hơn nhưng thua lớn
   nhất gấp đôi thì KHÔNG được lên.
"""
from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .config import DATA_DIR
from .so import thong_ke


@dataclass
class HoSo:
    """Thành tích của một chiến thuật, tính từ các lệnh đã kết toán."""
    ma: str
    n: int = 0
    kyVong: float = 0.0
    tongLaiLo: float = 0.0
    tiLeThang: float = 0.0
    thuaLonNhat: float = 0.0
    duoi5pct: float = 0.0
    capNhatLuc: float = 0.0


# Ngưỡng cứng. Đổi ở đây, không rải ra chỗ khác.
TOI_THIEU_MAU = 120
BIEN_VUOT = 1.15          # thách đấu phải hơn đương kim ít nhất 15%
DUOI_TOI_DA = 1.25        # thua lớn nhất không được quá 1,25 lần đương kim


@dataclass
class PhanXu:
    cho: bool
    lyDo: list[str] = field(default_factory=list)


class SoVoDich:
    """Sổ đương kim + thách đấu, ghi ra đĩa để sống qua lần khởi động lại."""

    def __init__(self, duong: Path | None = None) -> None:
        self.duong = duong or (DATA_DIR / "vo-dich.json")
        self.duongKim: dict[str, str] = {}      # nhóm -> mã chiến thuật
        self.hoSo: dict[str, HoSo] = {}
        self._doc()

    def _doc(self) -> None:
        if not self.duong.exists():
            return
        try:
            d = json.loads(self.duong.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return
        self.duongKim = d.get("duongKim") or {}
        self.hoSo = {k: HoSo(**v) for k, v in (d.get("hoSo") or {}).items()}

    def ghi(self) -> None:
        self.duong.parent.mkdir(parents=True, exist_ok=True)
        self.duong.write_text(json.dumps({
            "duongKim": self.duongKim,
            "hoSo": {k: asdict(v) for k, v in self.hoSo.items()},
        }, ensure_ascii=False, indent=2), encoding="utf-8")

    # ── cập nhật thành tích ───────────────────────────────────────────────
    def cap_nhat(self, ketToan: list[dict]) -> None:
        """Tính lại hồ sơ mọi chiến thuật từ sổ kết toán.

        Một lệnh có thể mang nhiều nhãn chiến thuật (ví dụ chân của một cặp
        vừa là `cap-theo-thoi` vừa được `phong-ho` đắp thêm). Tính lãi lỗ
        cho TỪNG nhãn là đếm trùng, nên chia đều cho số nhãn.
        """
        theo: dict[str, list[dict]] = {}
        for g in ketToan:
            cts = g.get("chienThuat") or ["khong-nhan"]
            phan = 1.0 / len(cts)
            for ct in cts:
                theo.setdefault(ct, []).append(
                    {**g, "laiLo": float(g.get("laiLo") or 0.0) * phan})

        for ct, ds in theo.items():
            tk = thong_ke(ds)
            if tk.get("chuaCo"):
                continue
            self.hoSo[ct] = HoSo(
                ma=ct, n=tk["n"], kyVong=tk["kyVong"],
                tongLaiLo=tk["tongLaiLo"], tiLeThang=tk["tiLeThang"],
                thuaLonNhat=tk["thuaLonNhat"], duoi5pct=tk["duoi5pct"],
                capNhatLuc=time.time(),
            )
        self.ghi()

    # ── cửa duyệt ─────────────────────────────────────────────────────────
    def xet(self, thachDau: str, nhom: str = "chung") -> PhanXu:
        """Thách đấu có được lên làm đương kim không. KHÔNG có đường tắt."""
        td = self.hoSo.get(thachDau)
        if td is None:
            return PhanXu(False, [f"chưa có hồ sơ cho `{thachDau}`"])

        ly: list[str] = []

        # cửa 1 — đủ mẫu
        if td.n < TOI_THIEU_MAU:
            ly.append(f"mới {td.n}/{TOI_THIEU_MAU} mẫu đã kết toán")

        # cửa 2 — kỳ vọng dương
        if td.kyVong <= 0:
            ly.append(f"kỳ vọng {td.kyVong:+.5f} không dương")

        dk_ma = self.duongKim.get(nhom)
        dk = self.hoSo.get(dk_ma) if dk_ma else None

        if dk is None:
            # Chưa có đương kim: qua được hai cửa đầu là lên.
            if ly:
                return PhanXu(False, ly)
            self.duongKim[nhom] = thachDau
            self.ghi()
            return PhanXu(True, [f"chưa có đương kim nhóm `{nhom}` → `{thachDau}` lên"])

        # cửa 3 — vượt đương kim đủ biên
        #
        # Biên tính trên ĐỘ LỚN. `td < dk * 1,15` đúng khi `dk` dương và
        # LẬT NGƯỢC khi âm: đương kim −$10 thì ngưỡng là −$11,5, nên một
        # thách đấu −$11 — TỆ HƠN đương kim — lên ngôi. Biên "phải hơn
        # 15%" thành "được phép kém tới 15%", và nó lật đúng vào lúc cần
        # cổng nhất: khi mọi chiến thuật đang lỗ.
        #
        # Cùng lỗi đã sửa ở `tien_hoa.thu_mot_de_xuat`. Hai chỗ, một
        # khuôn — nên chép cả cách sửa sang đây.
        can = dk.kyVong + abs(dk.kyVong) * (BIEN_VUOT - 1.0)
        if td.kyVong <= can:
            ly.append(f"kỳ vọng {td.kyVong:+.5f} chưa vượt đương kim "
                      f"`{dk.ma}` {dk.kyVong:+.5f} đủ biên {BIEN_VUOT:g}× "
                      f"(cần > {can:+.5f})")

        # cửa 4 — đuôi không tệ hơn
        if abs(td.thuaLonNhat) > abs(dk.thuaLonNhat) * DUOI_TOI_DA:
            ly.append(f"thua lớn nhất ${abs(td.thuaLonNhat):.2f} vượt "
                      f"{DUOI_TOI_DA:g}× đương kim ${abs(dk.thuaLonNhat):.2f}")
        # Ở đây NHÂN THẲNG là đúng, khác cửa 3: `duoi5pct` là phân vị 5%
        # của lãi lỗ, tức gần như luôn ÂM, và `dk × 1,15` âm hơn chính là
        # "cho phép đuôi xấu thêm 15%" — đúng ý. Chốt `td < 0` chặn nốt
        # phần còn lại.
        #
        # Còn một kẽ đã biết và cố ý để lại: nếu đương kim có `duoi5pct`
        # DƯƠNG (lãi cả ở 5% xấu nhất — hiếm), thì một thách đấu dương
        # nhưng thấp hơn nhiều vẫn qua cửa này. Ghi ra đây để người sau
        # biết đó là lựa chọn chứ không phải sót.
        if td.duoi5pct < dk.duoi5pct * DUOI_TOI_DA and td.duoi5pct < 0:
            ly.append(f"đuôi 5% ${td.duoi5pct:.2f} xấu hơn đương kim "
                      f"${dk.duoi5pct:.2f}")

        if ly:
            return PhanXu(False, ly)

        self.duongKim[nhom] = thachDau
        self.ghi()
        return PhanXu(True, [
            f"`{thachDau}` thay `{dk.ma}` làm đương kim nhóm `{nhom}`",
            f"kỳ vọng {td.kyVong:+.5f} vs {dk.kyVong:+.5f} · {td.n} mẫu",
        ])

    def tom_tat(self) -> dict:
        return {
            "duongKim": dict(self.duongKim),
            "nguong": {"toiThieuMau": TOI_THIEU_MAU, "bienVuot": BIEN_VUOT,
                       "duoiToiDa": DUOI_TOI_DA},
            "hoSo": [asdict(h) for h in sorted(
                self.hoSo.values(), key=lambda x: -x.kyVong)],
        }


so_vo_dich = SoVoDich()
