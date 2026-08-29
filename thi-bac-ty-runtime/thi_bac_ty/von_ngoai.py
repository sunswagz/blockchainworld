"""VỐN NGOÀI — phần vốn Thị Bạc Ty KHÔNG quản, nhưng PHẢI THẤY.

Kho này có hai cỗ máy chứ không phải một. Khâm Thiên Giám (Polymarket) xây
trước Thị Bạc Ty, có ví riêng, sổ cái riêng và **lớp đặt lệnh riêng**. Bản
đồ nói nó lẽ ra là một engine nộp cơ hội vào cùng một Opportunity Bus, và
việc nó không phải thế là một món nợ kiến trúc đã ghi ở đầu README.

Viết lại nó bây giờ là vi phạm chính cái luật đã cứu `bac/` khỏi bị viết
lại: đừng chuyển cả kho sang kiến trúc mới, rất dễ phá thứ đang chạy.

## Nhưng mù thì không được

Rủi Ro Tổng tồn tại để trả lời *"cho tiền vào đây thì DANH MỤC ra sao"*. Nó
không trả lời được cho phần nó **không nhìn thấy**. Ngày bốn cửa đặt lệnh
của Khâm Thiên Giám mở ra, `tranMotCang` và `sutVonToiDaPct` sẽ là trần của
một nửa gia sản trong khi mọi bảng đọc chúng như trần của cả gia sản.

File này là bước đầu tiên, và là bước RẺ NHẤT, để gỡ món nợ ấy: **thấy
trước, quản sau**. Nó chỉ ĐỌC — không đặt lệnh, không đóng vị thế, không
chạm tới cỗ máy kia. Vốn ngoài vào Danh Mục dưới dạng phơi nhiễm CHỈ-ĐỌC,
nên NAV và mọi trần tính trên tổng thật.

## Đọc qua HTTP, không import

Cố ý không `import kham`: hai runtime là hai tiến trình, hai vòng đời, hai
lịch khởi động lại. Import là buộc chúng thành một, và là mở đúng cánh cửa
mà `thi_bac_ty` không được phép mở — nó không biết ty nào tồn tại, và cũng
không được biết cỗ máy nào tồn tại.

Cỗ máy kia tắt thì `docDuoc=False`, và đó là một trạng thái phải HIỆN RA
chứ không phải im lặng coi như bằng 0. Coi "không đọc được" thành "không có
gì" là đúng cách một trần biến thành trần giả.
"""
from __future__ import annotations

import json
import time
import urllib.request
from dataclasses import dataclass, field

#: Bao lâu hỏi lại một lần. Vốn ngoài không nhúc nhích theo giây.
NHIP_GIAY = 60.0
HET_GIO_GIAY = 4.0


@dataclass
class LatCatNgoai:
    """Một lần đọc vốn ngoài. `docDuoc=False` là một TRẠNG THÁI, không phải 0."""
    ten: str
    docDuoc: bool = False
    vi: str = ""
    daCamKetUsd: float = 0.0
    tienMatUsd: float = 0.0
    chuaPhongHoUsd: float = 0.0
    soViThe: int = 0
    che: str = ""
    lucMs: float = field(default_factory=lambda: time.time() * 1000.0)

    @property
    def tongUsd(self) -> float:
        return self.daCamKetUsd + self.tienMatUsd

    def tuoi_giay(self) -> float:
        return (time.time() * 1000.0 - self.lucMs) / 1000.0

    def tom_tat(self) -> dict:
        return {"ten": self.ten, "docDuoc": self.docDuoc, "vi": self.vi,
                "daCamKetUsd": self.daCamKetUsd, "tienMatUsd": self.tienMatUsd,
                "tongUsd": self.tongUsd,
                "chuaPhongHoUsd": self.chuaPhongHoUsd,
                "soViThe": self.soViThe, "che": self.che,
                "tuoiGiay": self.tuoi_giay()}


class DocVonNgoai:
    """Đọc một runtime khác qua HTTP. CHỈ ĐỌC."""

    def __init__(self, ten: str, url: str, nhipGiay: float = NHIP_GIAY) -> None:
        self.ten = ten
        self.url = url
        self.nhip = float(nhipGiay)
        self._lanCuoi = 0.0
        self.latCat = LatCatNgoai(ten=ten, vi="chưa đọc lần nào")
        self.soLoi = 0

    def doc(self, ep: bool = False) -> LatCatNgoai:
        now = time.monotonic()
        # `<` và `<=` chỉ khác nhau khi quãng trôi qua BẰNG ĐÚNG nhịp
        # tính theo `monotonic()` — TƯƠNG ĐƯƠNG trên mọi lần chạy thật.
        # Cái đáng kiểm là cửa `ep` luôn xuyên qua được, và phép kiểm ấy
        # đã có.
        if not ep and self._lanCuoi and (now - self._lanCuoi) < self.nhip:
            return self.latCat
        self._lanCuoi = now
        try:
            r = urllib.request.urlopen(
                urllib.request.Request(
                    self.url, headers={"User-Agent": "thi-bac-ty/0.1"}),
                timeout=HET_GIO_GIAY)
            d = json.load(r)
        except Exception as e:                            # noqa: BLE001
            self.soLoi += 1
            self.latCat = LatCatNgoai(
                ten=self.ten, docDuoc=False,
                vi=f"{type(e).__name__}: {str(e)[:80]}")
            return self.latCat
        self.latCat = _doc_kham(self.ten, d)
        return self.latCat

    def tom_tat(self) -> dict:
        return {**self.latCat.tom_tat(), "url": self.url,
                "nhipGiay": self.nhip, "soLoi": self.soLoi}


def _so(v, mac=0.0) -> float:
    try:
        f = float(v)
    except (TypeError, ValueError):
        return mac
    return f if f == f and abs(f) != float("inf") else mac


def _doc_kham(ten: str, d: dict) -> LatCatNgoai:
    """Dịch ảnh chụp Khâm Thiên Giám sang `LatCatNgoai`.

    Đọc phòng thủ: mọi khoá đều có thể vắng, vì đây là schema của một cỗ máy
    KHÁC và ta không có quyền bắt nó giữ nguyên. Khoá vắng thì phần ấy là 0
    và `vi` nói ra — chứ không ném, và cũng không im.
    """
    kho = d.get("kho") or {}
    vt = kho.get("viThe") or []
    risk = d.get("risk") or {}
    thieu = [k for k in ("kho", "risk") if k not in d]
    return LatCatNgoai(
        ten=ten, docDuoc=True,
        vi=("thiếu khoá: " + ", ".join(thieu)) if thieu else "",
        # Vốn đang nằm trong vị thế. `loKhoaUsd` là phần đã khoá lỗ; cộng
        # `chuaPhongHoUsd` vì một chân chưa phòng hộ VẪN là vốn đang phơi ra.
        daCamKetUsd=sum(_so(v.get("loKhoaUsd")) + _so(v.get("chuaPhongHoUsd"))
                        for v in vt),
        tienMatUsd=_so(risk.get("vonUsd")) or _so(risk.get("soDuUsd")),
        chuaPhongHoUsd=sum(_so(v.get("chuaPhongHoUsd")) for v in vt),
        soViThe=int(_so(kho.get("soThiTruong"))),
        che=str(d.get("che") or ""))
