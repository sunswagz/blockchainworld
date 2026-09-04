"""SỔ PHÁN ĐOÁN — nơi mọi lời phán phải trả giá bằng điểm số.

Cung này sắp có một nguồn phán đoán không phải công thức: một mô hình
ngôn ngữ đọc tin rồi nói "market này nên ở 0,62". Câu hỏi không phải nó
nghe có hợp lý không — mà là **làm sao biết nó đúng hay chỉ nghe hay**.

File này là câu trả lời, và nó chỉ có một ý: **phán đoán nào cũng phải
ghi TRƯỚC, chấm SAU, và không được tiêu một đồng nào cho tới khi có
thành tích ĐO ĐƯỢC.**

## Vì sao không thể làm gọn hơn

Ba cái bẫy, cả ba đều đã cắn cung này ở chỗ khác:

1. **Quét rộng rồi chọn cái ngon nhất.** Cổng tiến hoá quét 49 ứng viên
   mỗi đêm và phải siết biên theo `log(số ứng viên)` — vì quán quân của
   một lượt quét gần như luôn dương và dấu của nó không đáng tin. Đọc
   500 market rồi chọn "hôm nay ngon nhất" là đúng cỗ máy ấy, to gấp
   mười, và không có gì bắt lại.

2. **Chấm sai mốc so.** Đánh bại tỉ lệ nền là chuyện dễ. Đánh bại GIÁ
   CHỢ mới là chuyện có tiền. Ở đây chấm CẢ HAI, và cổng chỉ mở theo
   cái thứ hai.

3. **Ghi sau khi biết kết quả.** Một phán đoán không có dấu thời gian
   và không có giá chợ LÚC PHÁN thì không chấm lại được — và cái sổ
   sinh ra chỉ để làm người ta yên tâm.

## Cổng: `du_de_dat_cuoc`

Một nguồn phán đoán được phép ảnh hưởng tới tiền khi VÀ CHỈ KHI:

    · đã có ít nhất `TOI_THIEU_NGA_NGU` phán đoán ngã ngũ, VÀ
    · điểm kỹ năng SO VỚI GIÁ CHỢ có khoảng tin 95% nằm HẲN bên dương

Chưa đủ thì trọng số bằng 0 — không phải "nhỏ", mà là 0. Cùng tinh thần
`HieuChinh.du_de_dung_kelly`: một xác suất chưa ai kiểm thì khuếch đại
chính sai lầm của mô hình.

Khoảng tin lấy lại theo KHỐI = TUẦN, không theo từng phán đoán: nhiều
phán đoán trong một tuần cùng đọc một dòng tin, nên chúng không phải
những quan sát độc lập. Đây là cái bẫy đã cắn cung này bốn lần ở chiều
khác (bốn lát τ của một khung).
"""
from __future__ import annotations

import json
import random
import statistics
import time
from dataclasses import dataclass, field
from pathlib import Path

from .config import DATA_DIR

#: Số phán đoán ĐÃ NGÃ NGŨ tối thiểu trước khi một nguồn được nói về
#: tiền. Không phải con số thiêng: nó là chỗ mà khoảng tin bootstrap
#: bắt đầu hẹp đủ để phân biệt kỹ năng thật với một chuỗi may mắn.
TOI_THIEU_NGA_NGU = 60

DUONG = DATA_DIR / "phan-doan.jsonl"


@dataclass
class PhanDoan:
    """Một lời phán, ghi TRƯỚC khi biết kết quả."""
    id: str
    nguon: str                  # ai phán: "claude", "mo-hinh", "nguoi"
    ho: str                     # họ market
    market: str
    cauHoi: str
    p: float                    # xác suất nguồn ấy nói
    lucMs: float
    hanMs: float                # bao giờ ngã ngũ
    #: Giá chợ LÚC PHÁN. Thiếu nó thì không bao giờ chấm được câu hỏi
    #: đáng giá duy nhất — "có hơn chợ không" — và cái sổ này thành đồ
    #: trang trí.
    giaCho: float | None = None
    lyLe: str = ""
    ketQua: bool | None = None  # None = chưa ngã ngũ
    nganNguLucMs: float | None = None

    def tom_tat(self) -> dict:
        return {k: getattr(self, k) for k in
                ("id", "nguon", "ho", "market", "cauHoi", "p", "lucMs",
                 "hanMs", "giaCho", "lyLe", "ketQua", "nganNguLucMs")}


def _tuan(lucMs: float) -> str:
    """Khối bootstrap = TUẦN. Nhiều phán đoán một tuần cùng đọc một tin."""
    t = time.gmtime(lucMs / 1000.0)
    return f"{t.tm_year}-{(t.tm_yday - 1) // 7:02d}"


@dataclass
class SoPhanDoan:
    duong: Path = field(default_factory=lambda: DUONG)
    ds: list[PhanDoan] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.doc()

    # ── đọc/ghi ───────────────────────────────────────────────────────
    def doc(self) -> None:
        self.ds = []
        if not self.duong.exists():
            return
        for dong in self.duong.read_text(encoding="utf-8").splitlines():
            if not dong.strip():
                continue
            try:
                self.ds.append(PhanDoan(**json.loads(dong)))
            except (json.JSONDecodeError, TypeError):
                continue

    def _ghi_het(self) -> None:
        self.duong.parent.mkdir(parents=True, exist_ok=True)
        self.duong.write_text(
            "".join(json.dumps(p.tom_tat(), ensure_ascii=False) + "\n"
                    for p in self.ds), encoding="utf-8")

    def them(self, pd: PhanDoan) -> bool:
        """Ghi một phán đoán MỚI. Từ chối nếu nó đã biết kết quả.

        Một phán đoán mang sẵn `ketQua` là một phán đoán ghi SAU khi
        biết đáp án. Nhận nó vào sổ là tự tay làm hỏng thứ duy nhất
        khiến cái sổ này có nghĩa.
        """
        if pd.ketQua is not None:
            raise ValueError(
                "phán đoán MỚI không được mang sẵn `ketQua` — ghi trước, "
                "chấm sau; ngược lại thì cái sổ này vô nghĩa")
        if not (0.0 < pd.p < 1.0):
            raise ValueError(f"p phải nằm trong (0, 1), nhận {pd.p}")
        if any(x.id == pd.id for x in self.ds):
            return False
        self.ds.append(pd)
        self._ghi_het()
        return True

    def nga_ngu(self, ma_id: str, ketQua: bool,
                lucMs: float | None = None) -> bool:
        """Ghi kết quả cho một phán đoán. Không cho sửa lại lần hai."""
        for p in self.ds:
            if p.id != ma_id:
                continue
            if p.ketQua is not None:
                raise ValueError(
                    f"`{ma_id}` đã ngã ngũ rồi — sửa kết quả sau khi đã "
                    "chấm là cách dễ nhất để một thành tích tồi trông đẹp")
            p.ketQua = bool(ketQua)
            p.nganNguLucMs = lucMs if lucMs is not None else time.time() * 1000.0
            self._ghi_het()
            return True
        return False

    # ── chấm ──────────────────────────────────────────────────────────
    def cham(self, nguon: str | None = None, ho: str | None = None) -> dict:
        """Chấm một nguồn phán đoán. Hai mốc so, và mốc thứ hai mới đáng.

        · so với TỈ LỆ NỀN — dễ, và gần như vô nghĩa;
        · so với GIÁ CHỢ lúc phán — khó, và là thứ duy nhất thành tiền.
        """
        ds = [p for p in self.ds if p.ketQua is not None
              and (nguon is None or p.nguon == nguon)
              and (ho is None or p.ho == ho)]
        ra: dict = {"nguon": nguon, "ho": ho, "soNgaNgu": len(ds)}
        if len(ds) < 5:
            ra["lyDo"] = "chưa đủ phán đoán ngã ngũ để chấm"
            return ra

        that = [1.0 if p.ketQua else 0.0 for p in ds]
        nen = statistics.fmean(that)
        bMH = statistics.fmean((p.p - t) ** 2 for p, t in zip(ds, that))
        bNen = statistics.fmean((nen - t) ** 2 for t in that)
        ra.update({"tiLeNen": nen, "brier": bMH, "brierNen": bNen,
                   "kyNangSoNen": (1 - bMH / bNen) if bNen > 0 else None})

        coCho = [(p, t) for p, t in zip(ds, that) if p.giaCho is not None]
        ra["soCoGiaCho"] = len(coCho)
        if len(coCho) >= 5:
            bCho = statistics.fmean((p.giaCho - t) ** 2 for p, t in coCho)
            bMH2 = statistics.fmean((p.p - t) ** 2 for p, t in coCho)
            ra["brierCho"] = bCho
            ra["brierMoHinhTrenCungMau"] = bMH2
            ra["kyNangSoCho"] = (1 - bMH2 / bCho) if bCho > 0 else None
            hieu = [(p.p - t) ** 2 - (p.giaCho - t) ** 2 for p, t in coCho]
            khoi = [_tuan(p.lucMs) for p, _ in coCho]
            ra["tin95SoCho"] = _khoang_tin(hieu, khoi)
        return ra

    def du_de_dat_cuoc(self, nguon: str) -> tuple[bool, str]:
        """CỔNG: nguồn này đã được phép ảnh hưởng tới tiền chưa.

        Trả (cho, lý do). Lý do luôn có, kể cả khi cho — vì "vì sao mở"
        cũng đáng đọc như "vì sao đóng".
        """
        d = self.cham(nguon)
        n = d.get("soNgaNgu", 0)
        if n < TOI_THIEU_NGA_NGU:
            return (False, f"mới {n}/{TOI_THIEU_NGA_NGU} phán đoán ngã ngũ "
                           "— chưa đủ để phân biệt kỹ năng với may mắn")
        tin = d.get("tin95SoCho")
        if not tin:
            return (False, "chưa có phán đoán nào kèm GIÁ CHỢ lúc phán — "
                           "không chấm được câu hỏi 'có hơn chợ không'")
        thap, cao, soK = tin
        # ── KHOẢNG TIN RỘNG BẰNG 0 KHÔNG PHẢI LÀ CHẮC CHẮN ────────────
        #
        # Bootstrap lấy lại theo khối; nếu MỌI khối cho cùng một trung
        # bình thì khoảng tin sụp thành một điểm. Đó không phải bằng
        # chứng hoàn hảo — đó là dấu hiệu dữ liệu suy biến: một khối
        # duy nhất, hoặc mọi tuần giống hệt nhau (thường là dữ liệu
        # dựng, hoặc một giá trị lặp lại).
        #
        # Mở cổng theo một khoảng tin sụp là mở theo thứ chắc chắn
        # NHẤT trông giống chắc chắn nhất mà lại rỗng nhất.
        if soK < 4:
            return (False, f"chỉ {soK} khối tuần — quá ít để khoảng tin "
                           "nói được gì")
        if cao - thap <= 1e-12:
            return (False, f"khoảng tin rộng bằng 0 ({soK} khối) — mọi tuần "
                           "cho cùng một kết quả, đó là dữ liệu suy biến "
                           "chứ không phải bằng chứng hoàn hảo")
        if cao >= 0:
            return (False, f"kỹ năng so với GIÁ CHỢ có khoảng tin "
                           f"[{thap:+.5f}, {cao:+.5f}] ({soK} tuần) — "
                           "chưa nằm hẳn bên dương")
        return (True, f"đã {n} phán đoán ngã ngũ, kỹ năng so với giá chợ "
                      f"[{thap:+.5f}, {cao:+.5f}] ({soK} tuần) — hẳn bên dương")

    def tom_tat(self) -> dict:
        chua = sum(1 for p in self.ds if p.ketQua is None)
        nguon = sorted({p.nguon for p in self.ds})
        return {
            "tong": len(self.ds), "chuaNgaNgu": chua,
            "nguon": {n: self.cham(n) for n in nguon},
            "cong": {n: dict(zip(("cho", "lyDo"), self.du_de_dat_cuoc(n)))
                     for n in nguon},
        }


def _khoang_tin(hieu: list[float], khoi: list[str], soLan: int = 2000):
    """Khoảng tin 95% cho trung bình `hieu`, lấy lại theo KHỐI."""
    if not hieu:
        return None
    nhom: dict = {}
    for h, k in zip(hieu, khoi):
        nhom.setdefault(k, []).append(h)
    ds = list(nhom.values())
    rd = random.Random(20260903)
    lan = []
    for _ in range(soLan):
        t = c = 0.0
        for _k in range(len(ds)):
            b = ds[rd.randrange(len(ds))]
            t += sum(b)
            c += len(b)
        lan.append(t / max(1.0, c))
    lan.sort()
    return (lan[int(0.025 * soLan)], lan[int(0.975 * soLan)], len(ds))
