"""Nắn lại xác suất theo sổ hiệu chỉnh — khép chỗ hở cuối của vòng học.

Cỗ máy này đo được chỗ nó sai từ lâu. Bảng hiệu chỉnh trên 2.542 mẫu nói
rất rõ, và nói cùng một chuyện ở CẢ HAI đuôi:

    mô hình nói 15%  →  thật  3,4%        nói 65%  →  thật 76,2%
    mô hình nói 25%  →  thật 10,3%        nói 75%  →  thật 93,0%
    mô hình nói 34%  →  thật 13,5%        nói 85%  →  thật 98,9%

Đơn điệu, hai phía đối xứng, sai số trung bình 6,4–7,4 điểm. Đó không
phải tiếng ồn — đó là mô hình **bị nén về 50%**: nó nhút nhát có hệ
thống, thực tế cực đoan hơn nó nghĩ.

Nhưng `HieuChinh` chỉ được dùng để mở/khoá Kelly và nuôi chẩn đoán.
**Không dòng nào đọc nó lại vào mô hình.** Đo mà không hồi tiếp thì vòng
học vẫn hở — cùng đúng hình dạng với chỗ hở đầu tiên đã vá hồi dựng cung,
chỉ là ở lớp sau.

## Vì sao nắn lại làm TĂNG lợi thế, không phải chỉ làm đẹp số

Lợi thế thô là |giá trị thật − giá chợ|. Mô hình bị nén về 50% thì nó tự
kéo mọi ước lượng về gần chợ, và lợi thế thô teo lại đúng ở những lần nó
tự tin nhất. Kéo giãn ra là trả lại phần lợi thế vốn có.

## Bốn chốt an toàn

1. **Đơn điệu tuyệt đối.** Dùng PAVA (gộp cặp vi phạm). Một phép nắn làm
   đảo thứ tự sẽ biến "tôi tin UP hơn" thành "tôi tin DOWN hơn" — hỏng
   nặng hơn hẳn sai số nó định chữa.
2. **Đủ mẫu mới nắn.** Nắn trên vài chục lượt là học thuộc tiếng ồn rồi
   đem tiếng ồn đi cược.
3. **GIẢM CHẤN.** Chỉ đi `HE_SO_GIAM_CHAN` phần đường. Ta CHƯA kiểm được
   ngoài mẫu — sổ chỉ lưu tổng theo ô, không lưu từng cặp — nên chưa có
   quyền tin hết. Từ nay ghi thêm từng cặp thô để lượt sau kiểm được
   đàng hoàng, và khi ấy mới nói chuyện bỏ giảm chấn.
4. **Trần dịch chuyển.** Không lần nào được dời quá `DOI_TOI_DA`. Một
   phép khớp hỏng thì cùng lắm lệch chừng ấy, không bao giờ thành một
   con số hoang dại chảy vào phép tính tiền.
"""
from __future__ import annotations

import json
from pathlib import Path

from .config import CONFIG, DATA_DIR

_NL = (CONFIG.get("nanLai") or {})

TOI_THIEU_MAU = int(_NL.get("toiThieuMau", 400))
TOI_THIEU_MOI_O = int(_NL.get("toiThieuMoiO", 20))
HE_SO_GIAM_CHAN = float(_NL.get("heSoGiamChan", 0.7))
DOI_TOI_DA = float(_NL.get("doiToiDa", 0.25))
DUONG_THO = DATA_DIR / "hieu-chinh-tho.jsonl"


def _pava(x: list[float], y: list[float], w: list[float]) -> list[float]:
    """Hồi quy đơn điệu: gộp các cặp vi phạm cho tới khi không còn.

    Đây là phần KHÔNG được thay bằng một phép làm mượt nào khác. Làm mượt
    giữ được hình dáng chung nhưng vẫn cho phép đảo thứ tự cục bộ, và một
    lần đảo là đủ để phép nắn nói ngược lại mô hình.
    """
    ra = list(y)
    can = list(w)
    i = 0
    while i < len(ra) - 1:
        if ra[i] <= ra[i + 1] + 1e-12:
            i += 1
            continue
        tong = can[i] + can[i + 1]
        gop = (ra[i] * can[i] + ra[i + 1] * can[i + 1]) / tong
        ra[i:i + 2] = [gop]
        can[i:i + 2] = [tong]
        x[i:i + 2] = [(x[i] + x[i + 1]) / 2.0]
        i = max(0, i - 1)
    return ra


class PhepNan:
    """Một đường nắn đã khớp xong, kèm mọi số để người khác kiểm lại."""

    def __init__(self, moc: list[tuple[float, float]], tongMau: int,
                 saiTruoc: float, saiSau: float) -> None:
        self.moc = moc
        self.tongMau = tongMau
        self.saiTruoc = saiTruoc
        self.saiSau = saiSau

    @property
    def dung_duoc(self) -> bool:
        # Không khá hơn thì KHÔNG dùng. Một phép nắn không cải thiện gì mà
        # vẫn áp vào là thêm một tầng phức tạp đổi lấy đúng không gì.
        return len(self.moc) >= 2 and self.saiSau < self.saiTruoc

    def nan(self, p: float) -> float:
        if not self.dung_duoc:
            return p
        m = self.moc
        if p <= m[0][0]:
            q = m[0][1]
        elif p >= m[-1][0]:
            q = m[-1][1]
        else:
            q = m[-1][1]
            for i in range(len(m) - 1):
                a, b = m[i], m[i + 1]
                if a[0] <= p <= b[0]:
                    t = 0.0 if b[0] == a[0] else (p - a[0]) / (b[0] - a[0])
                    q = a[1] + t * (b[1] - a[1])
                    break
        # Chốt 3 — giảm chấn: mới đi một phần đường.
        q = p + (q - p) * HE_SO_GIAM_CHAN
        # Chốt 4 — trần dịch chuyển.
        q = max(p - DOI_TOI_DA, min(p + DOI_TOI_DA, q))
        return max(0.001, min(0.999, q))

    def tom_tat(self) -> dict:
        return {
            "dungDuoc": self.dung_duoc, "tongMau": self.tongMau,
            "soMoc": len(self.moc),
            "saiTruoc": self.saiTruoc, "saiSau": self.saiSau,
            "caiThien": (self.saiTruoc - self.saiSau) if self.moc else 0.0,
            "heSoGiamChan": HE_SO_GIAM_CHAN, "doiToiDa": DOI_TOI_DA,
            "moc": [{"tu": round(a, 4), "toi": round(b, 4)} for a, b in self.moc],
        }


def khop(hieuChinh) -> PhepNan:
    """Khớp đường nắn từ sổ hiệu chỉnh. Thiếu mẫu thì trả một phép RỖNG."""
    o = getattr(hieuChinh, "o", {}) or {}
    diem: list[tuple[float, float, float]] = []
    tong = 0
    for _ten, d in sorted(o.items(), key=lambda kv: kv[1].get("tongP", 0)):
        n = int(d.get("n", 0))
        tong += n
        if n < TOI_THIEU_MOI_O:
            continue
        duDoan = float(d.get("tongP", 0.0)) / n
        thucTe = float(d.get("thang", 0)) / n
        diem.append((duDoan, thucTe, float(n)))

    if tong < TOI_THIEU_MAU or len(diem) < 3:
        return PhepNan([], tong, 0.0, 0.0)

    diem.sort(key=lambda t: t[0])
    x = [a for a, _b, _w in diem]
    y = [b for _a, b, _w in diem]
    w = [c for _a, _b, c in diem]

    saiTruoc = sum(abs(a - b) * c for a, b, c in diem) / sum(w)
    xn = list(x)
    yn = _pava(xn, y, list(w))
    moc = list(zip(xn, yn))

    tam = PhepNan(moc, tong, saiTruoc, 0.0)
    tam.saiSau = 0.0            # tạm cho phép nan() chạy để đo
    tam.saiSau = sum(abs(tam.nan(a) - b) * c for a, b, c in diem) / sum(w)
    return tam


def ghi_tho(pDuDoan: float, thangThat: bool, ma: str = "") -> None:
    """Ghi TỪNG CẶP thô, để lượt sau kiểm được ngoài mẫu.

    Sổ hiệu chỉnh chỉ lưu tổng theo ô. Từ tổng thì khớp được một đường
    nhưng KHÔNG kiểm được nó trên dữ liệu chưa từng thấy — mà đó mới là
    phép kiểm duy nhất phân biệt "học được quy luật" với "học thuộc bảng".
    File này là để lần sau không còn phải giảm chấn vì thiếu bằng chứng.
    """
    try:
        DUONG_THO.parent.mkdir(parents=True, exist_ok=True)
        with DUONG_THO.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"p": round(pDuDoan, 6),
                                "thang": bool(thangThat), "ma": ma},
                               ensure_ascii=False) + "\n")
    except OSError:
        pass


def doc_tho(duong: Path | None = None) -> list[tuple[float, bool]]:
    d = duong or DUONG_THO
    if not d.exists():
        return []
    ra = []
    for dong in d.read_text(encoding="utf-8").splitlines():
        try:
            j = json.loads(dong)
            ra.append((float(j["p"]), bool(j["thang"])))
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            continue
    return ra
