"""ĐIỂM · CHẶNG · TUYẾN — và luật cộng trung thực.

Điểm là một chỗ vốn có thể NẰM: một chuỗi, hoặc một sàn tập trung. Tuyến là
dãy chặng nối hai điểm. Luật quan trọng nhất của file này nằm ở
`TuyenDuong.phiUsd`:

    một chặng không đo được thì CẢ TUYẾN không đo được.

Không cộng vòng qua một lỗ hổng. Cộng hai chặng biết giá rồi bỏ qua chặng
thứ ba cho ra một con số trông như đã đủ, và không gì trong con số ấy nói
rằng nó thiếu — sai theo đúng hướng nguy hiểm nhất, hào phóng với chính
mình.
"""
from __future__ import annotations

from dataclasses import dataclass

#: Hai loại điểm, và chúng KHÔNG thay thế nhau được. Vốn trên một chuỗi thì
#: tự mình ký được giao dịch; vốn trong một sàn thì nằm dưới quyền sàn, và
#: rút ra là một hành động sàn có thể từ chối hoặc trì hoãn.
LOAI_DIEM = ("chuoi", "san")

#: Cách một chặng được đi. Mỗi cách một nguồn giá, và ba trong bốn cách đọc
#: được không cần khoá.
CACH = {
    "cau-noi": "cầu nối liên chuỗi — LI.FI, đọc được",
    "gas-thuan": "chỉ tốn gas trên cùng một chuỗi — RPC, đọc được",
    "rut-cex": "rút khỏi sàn về chuỗi — CẦN KHOÁ, nên dùng bảng đo tay",
    "nap-cex": "nạp từ chuỗi vào sàn — chỉ tốn gas, sàn không thu phí nạp",
}


@dataclass(frozen=True)
class Diem:
    """Một chỗ vốn có thể nằm."""
    loai: str
    ten: str

    def __post_init__(self) -> None:
        if self.loai not in LOAI_DIEM:
            raise ValueError(f"loại điểm lạ: {self.loai!r}")
        if not self.ten:
            raise ValueError("điểm phải có tên")
        # Chuẩn hoá NGAY TẠI CỬA, không ở chỗ so sánh. `tin_dung` viết
        # "Ethereum", `chuyen_von` viết "ethereum", `on_dinh` viết
        # "binance" — ba lối viết của ba tác giả khác nhau, và để chúng
        # gặp nhau ở một phép `==` nào đó thì `Diem` này khác `Diem` kia
        # mà cả hai đều đúng chính tả.
        object.__setattr__(self, "ten", self.ten.strip().lower())

    def __str__(self) -> str:
        return f"{self.ten}({self.loai})"


@dataclass(frozen=True)
class ChangDuong:
    """Một chặng. `phiUsd is None` nghĩa là KHÔNG ĐO ĐƯỢC, không phải 0."""
    tu: Diem
    den: Diem
    cach: str
    phiUsd: float | None
    giayCho: float | None
    nguon: str
    #: Thứ chặng này biết là mình chưa tính. Rỗng KHÔNG có nghĩa là đã tính
    #: hết — nó có nghĩa là chặng này không biết mình thiếu gì, và đó là hai
    #: chuyện khác nhau.
    khongDoDuoc: tuple[str, ...] = ()

    @property
    def doDuoc(self) -> bool:
        return self.phiUsd is not None and self.giayCho is not None

    def tom_tat(self) -> str:
        p = "?" if self.phiUsd is None else f"${self.phiUsd:,.2f}"
        t = "?" if self.giayCho is None else f"{self.giayCho:,.0f}s"
        return f"{self.tu} -> {self.den} [{self.cach}] {p} · {t}"


@dataclass(frozen=True)
class TuyenDuong:
    """Dãy chặng nối hai điểm, và tổng đã cộng theo luật trung thực."""
    chang: tuple[ChangDuong, ...]
    #: Vì sao không có tuyến nào — chỉ khác rỗng khi `chang` rỗng.
    viSaoKhong: str = ""

    @property
    def tu(self) -> Diem | None:
        return self.chang[0].tu if self.chang else None

    @property
    def den(self) -> Diem | None:
        return self.chang[-1].den if self.chang else None

    @property
    def doDuoc(self) -> bool:
        """Cả tuyến đo được KHI VÀ CHỈ KHI mọi chặng đo được."""
        return bool(self.chang) and all(c.doDuoc for c in self.chang)

    @property
    def phiUsd(self) -> float | None:
        """None nếu BẤT KỲ chặng nào không đo được.

        Đây là luật, không phải một lựa chọn cài đặt.
        """
        if not self.doDuoc:
            return None
        return sum(c.phiUsd for c in self.chang)                # type: ignore

    @property
    def giayCho(self) -> float | None:
        """Thời gian CỘNG, không phải lấy max: các chặng đi nối tiếp nhau.

        Vốn đang trên cầu nối thì chưa nạp vào sàn được, nên hai chặng không
        chồng lên nhau được.
        """
        if not self.doDuoc:
            return None
        return sum(c.giayCho for c in self.chang)               # type: ignore

    @property
    def khongDoDuoc(self) -> tuple[str, ...]:
        """Gộp mọi thứ các chặng khai là chưa tính, cộng cả chặng nào mù."""
        ra: list[str] = []
        for c in self.chang:
            if not c.doDuoc:
                ra.append(f"chang-mu:{c.tu.ten}->{c.den.ten}:{c.cach}")
            ra.extend(c.khongDoDuoc)
        thay: set[str] = set()
        return tuple(x for x in ra if not (x in thay or thay.add(x)))

    def phi_bps(self, vonUsd: float) -> float | None:
        """Phí quy ra bps trên số vốn dời — đơn vị mọi ty đang dùng.

        Phí chuyển vốn là một khoản CỐ ĐỊNH, nên bps của nó phụ thuộc số
        vốn: $3 trên $200 là 150 bps, trên $50.000 là 0,6 bps. Đó là lý do
        ty nhỏ bị chặn bởi đúng khoản mà ty lớn không thấy.
        """
        if self.phiUsd is None or vonUsd <= 0:
            return None
        return self.phiUsd / vonUsd * 10_000.0

    def tom_tat(self) -> str:
        if not self.chang:
            return f"KHÔNG có tuyến — {self.viSaoKhong}"
        dau = " · ".join(c.tom_tat() for c in self.chang)
        if not self.doDuoc:
            return f"{dau} => TỔNG: KHÔNG ĐO ĐƯỢC ({len(self.khongDoDuoc)} lỗ)"
        return (f"{dau} => TỔNG ${self.phiUsd:,.2f} · "
                f"{self.giayCho / 3600.0:,.1f} giờ")

    def sach(self) -> dict:
        return {
            "tu": str(self.tu) if self.tu else None,
            "den": str(self.den) if self.den else None,
            "soChang": len(self.chang),
            "doDuoc": self.doDuoc,
            "phiUsd": self.phiUsd,
            "giayCho": self.giayCho,
            "khongDoDuoc": list(self.khongDoDuoc),
            "viSaoKhong": self.viSaoKhong,
            "chang": [{"tu": str(c.tu), "den": str(c.den), "cach": c.cach,
                       "phiUsd": c.phiUsd, "giayCho": c.giayCho,
                       "nguon": c.nguon,
                       "khongDoDuoc": list(c.khongDoDuoc)}
                      for c in self.chang],
        }


def khong_co_tuyen(vi: str) -> TuyenDuong:
    return TuyenDuong(chang=(), viSaoKhong=vi)
