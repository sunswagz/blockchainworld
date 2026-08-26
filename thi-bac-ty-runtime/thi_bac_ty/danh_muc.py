"""DANH MỤC — *bây giờ tôi có gì, và tiền đang nằm ở đâu.*

Một nguồn sự thật DUY NHẤT về vốn. Không ty nào được giữ con số này riêng —
đó là cả lý do Thị Bạc Ty tồn tại:

    Perp     tưởng nó có $300
    Lending  tưởng nó có $300
    DEX      tưởng nó có $300
    ...
    tổng thật: $1.500 đã cam kết, và không ty nào thấy con số ấy

## Phơi nhiễm phải tính theo TÀI SẢN GỐC, không chỉ theo đô la

Đây là chỗ dễ sai nhất, và nó im lặng.

Giả sử danh mục có:

    Perp   LONG  BTC hyperliquid  $500  ·  SHORT BTC binance  $500
    Basis  LONG  BTC spot         $500  ·  SHORT BTC perp     $500

Cộng theo đô la: $2.000 đã cam kết. Nghe như đã phân tán.

Nhưng cộng theo **phơi nhiễm ròng BTC**: mỗi cặp tự triệt tiêu, nên ròng ≈ 0
— danh mục này KHÔNG có rủi ro hướng giá BTC. Trong khi:

    Perp     LONG BTC  $500
    Lending  thế chấp BTC vay USDC  $500

cộng đô la cũng ra $1.000, nhưng phơi nhiễm ròng BTC là **+$1.000** — BTC
giảm 20% là mất $200, và không ty nào trong hai ty ấy nhìn thấy điều đó.

Nên Danh Mục giữ **ba** thước, không phải một:

    daCamKet      tổng đô la đã hứa ra — dùng cho trần vốn
    phoiNhiemRong theo tài sản, có dấu — dùng cho rủi ro hướng giá
    phoiNhiemTho  theo tài sản, trị tuyệt đối — dùng cho rủi ro thanh khoản

Ba thước trả lời ba câu khác nhau. Gộp chúng làm một là mất đúng cái nhìn mà
Thị Bạc Ty sinh ra để có.

## Phơi nhiễm theo CẢNG thì lấy trị tuyệt đối, không lấy ròng

Cảng sập thì cả hai chân trên cảng ấy đều kẹt — chân LONG không cứu chân
SHORT. Nên rủi ro đối tác cộng bằng trị tuyệt đối, khác hẳn rủi ro hướng giá.

## Chế độ mô phỏng

Chưa có lớp đặt lệnh nên chưa có số dư thật. Danh Mục khởi tạo từ `vonBanDau`
trong cấu hình và khai `nguonThat = False`. Buồng lái phải hiện cờ ấy: một
bảng NAV trông y như thật mà thực ra là số mô phỏng là kiểu nói dối tệ nhất
một bảng vốn có thể mắc.
"""
from __future__ import annotations

import threading
from dataclasses import dataclass, field


@dataclass
class ViThe:
    """Một chân đang mở. Danh Mục cộng từ đây ra mọi phơi nhiễm."""
    maToTrinh: str
    chienLuoc: str
    ben: str                     # LONG · SHORT · CHO_VAY · DI_VAY · …
    cang: str
    taiSan: str
    vonUsd: float
    chuoi: str | None = None
    loai: str = "perp"
    moLuc: str = ""

    @property
    def dau(self) -> int:
        """+1 nếu phơi nhiễm thuận chiều giá tài sản, −1 nếu ngược.

        `CHO_VAY` là +1: cho vay BTC thì vẫn giữ BTC, giá xuống vẫn thiệt.
        `DI_VAY` là −1: vay BTC ra bán là đang short nó.
        """
        return -1 if self.ben in ("SHORT", "DI_VAY") else 1

    def tom_tat(self) -> dict:
        return {"maToTrinh": self.maToTrinh, "chienLuoc": self.chienLuoc,
                "ben": self.ben, "cang": self.cang, "taiSan": self.taiSan,
                "vonUsd": self.vonUsd, "chuoi": self.chuoi,
                "loai": self.loai, "moLuc": self.moLuc}


class DanhMuc:
    def __init__(self, vonBanDauUsd: float, nguonThat: bool = False) -> None:
        self._khoa = threading.Lock()
        self.vonBanDauUsd = float(vonBanDauUsd)
        #: **Cờ trung thực.** False = mọi con số dưới đây là MÔ PHỎNG, không
        #: đọc từ sàn. Buồng lái phải hiện cờ này.
        self.nguonThat = bool(nguonThat)
        self.tienMatUsd = float(vonBanDauUsd)
        self.viThe: dict[str, list[ViThe]] = {}       # maToTrinh → các chân
        self.laiLoDaThucHienUsd = 0.0
        #: Vốn nằm ở cỗ máy KHÁC — thấy được, KHÔNG quản được. Xem
        #: `thi_bac_ty/von_ngoai.py`. Rỗng là bình thường; rỗng vì KHÔNG
        #: ĐỌC ĐƯỢC thì `ngoaiDocDuoc` nói ra.
        self.ngoai: dict[str, dict] = {}
        self.ngoaiDocDuoc: dict[str, bool] = {}

    # ── thay đổi ──────────────────────────────────────────────────────────
    def cam_ket(self, maToTrinh: str, chan: list[ViThe]) -> bool:
        """Ghi nhận vốn đã cấp cho một tờ trình. False nếu không đủ tiền mặt.

        Kiểm tiền mặt Ở ĐÂY chứ không tin tầng trên đã kiểm: Danh Mục là
        nguồn sự thật, nên nó phải là chỗ cuối cùng nói được "không đủ". Tin
        tầng trên là mở đường cho hai tầng cùng tưởng tầng kia đã kiểm.
        """
        with self._khoa:
            if maToTrinh in self.viThe:
                return False                          # đã cấp rồi, không cấp hai lần
            can = sum(abs(c.vonUsd) for c in chan)
            if can > self.tienMatUsd + 1e-9:
                return False
            self.tienMatUsd -= can
            self.viThe[maToTrinh] = list(chan)
            return True

    def dong(self, maToTrinh: str, laiLoUsd: float = 0.0) -> bool:
        """Đóng một vị thế, hoàn vốn về tiền mặt kèm lãi lỗ."""
        with self._khoa:
            chan = self.viThe.pop(maToTrinh, None)
            if chan is None:
                return False
            self.tienMatUsd += sum(abs(c.vonUsd) for c in chan) + laiLoUsd
            self.laiLoDaThucHienUsd += laiLoUsd
            return True

    def ghi_dong_tien(self, soTienUsd: float) -> None:
        """Dòng tiền phát sinh khi vị thế còn mở (funding, phí)."""
        with self._khoa:
            self.tienMatUsd += soTienUsd
            self.laiLoDaThucHienUsd += soTienUsd

    def ghi_von_ngoai(self, lat) -> None:
        """Ghi nhận một lát cắt vốn ngoài. CHỈ ĐỌC — không cam kết, không đóng.

        Vốn ngoài vào NAV nhưng KHÔNG vào `viThe`: Thị Bạc Ty không mở nó,
        không đóng được nó, và không được phép giả vờ ngược lại. Nó vào đây
        vì mọi trần của Rủi Ro Tổng tính theo NAV, và một NAV thiếu mất phần
        vốn đang phơi ra ở nơi khác là một NAV nói dối theo hướng nguy hiểm:
        trần rộng hơn sự thật.
        """
        self.ngoai[lat.ten] = lat.tom_tat()
        self.ngoaiDocDuoc[lat.ten] = bool(lat.docDuoc)

    @property
    def ngoaiUsd(self) -> float:
        """Tổng vốn ngoài ĐỌC ĐƯỢC. Không đọc được thì không cộng — và
        `ngoaiDayDu` là chỗ nói ra rằng con số này đang thiếu."""
        return sum(x.get("tongUsd") or 0.0 for t, x in self.ngoai.items()
                   if self.ngoaiDocDuoc.get(t))

    @property
    def ngoaiDayDu(self) -> bool:
        """Mọi nguồn vốn ngoài đã khai đều đọc được chưa.

        `False` nghĩa là NAV đang THIẾU một phần chưa biết bao nhiêu, nên
        mọi trần tính theo NAV đang rộng hơn sự thật. Buồng lái phải hiện
        cờ này cạnh NAV, không nhét cuối bảng.
        """
        return all(self.ngoaiDocDuoc.values()) if self.ngoai else True

    # ── đọc ───────────────────────────────────────────────────────────────
    @property
    def daCamKetUsd(self) -> float:
        return sum(abs(c.vonUsd) for ds in self.viThe.values() for c in ds)

    @property
    def navUsd(self) -> float:
        """Tổng giá trị. Vị thế tính theo vốn đã bỏ, CHƯA đánh giá lại.

        Chưa có giá thị trường của vị thế đang mở nên NAV này là **vốn gốc +
        tiền mặt**, không phải NAV thật. Khai ở `tom_tat()` để không ai nhầm.
        """
        return self.tienMatUsd + self.daCamKetUsd + self.ngoaiUsd

    @property
    def tuQuanUsd(self) -> float:
        """Phần NAV Thị Bạc Ty THẬT SỰ điều khiển được.

        Tách khỏi `navUsd` vì hai câu hỏi khác nhau: "trần rủi ro tính trên
        bao nhiêu" dùng NAV (gồm cả vốn ngoài, vì rủi ro là của cả gia sản),
        còn "còn bao nhiêu để rót" dùng con số này.
        """
        return self.tienMatUsd + self.daCamKetUsd

    def phoi_nhiem_rong(self) -> dict[str, float]:
        """Theo tài sản, CÓ DẤU. Trả lời rủi ro hướng giá."""
        ra: dict[str, float] = {}
        for ds in self.viThe.values():
            for c in ds:
                ra[c.taiSan] = ra.get(c.taiSan, 0.0) + c.dau * abs(c.vonUsd)
        return ra

    def phoi_nhiem_tho(self) -> dict[str, float]:
        """Theo tài sản, TRỊ TUYỆT ĐỐI. Trả lời rủi ro thanh khoản."""
        ra: dict[str, float] = {}
        for ds in self.viThe.values():
            for c in ds:
                ra[c.taiSan] = ra.get(c.taiSan, 0.0) + abs(c.vonUsd)
        return ra

    def phoi_nhiem_cang(self) -> dict[str, float]:
        """Theo cảng, TRỊ TUYỆT ĐỐI — cảng sập thì cả hai chân đều kẹt."""
        ra: dict[str, float] = {}
        for ds in self.viThe.values():
            for c in ds:
                ra[c.cang] = ra.get(c.cang, 0.0) + abs(c.vonUsd)
        return ra

    def phoi_nhiem_chuoi(self) -> dict[str, float]:
        ra: dict[str, float] = {}
        for ds in self.viThe.values():
            for c in ds:
                if c.chuoi:
                    ra[c.chuoi] = ra.get(c.chuoi, 0.0) + abs(c.vonUsd)
        return ra

    def phoi_nhiem_ty(self) -> dict[str, float]:
        ra: dict[str, float] = {}
        for ds in self.viThe.values():
            for c in ds:
                ra[c.chienLuoc] = ra.get(c.chienLuoc, 0.0) + abs(c.vonUsd)
        return ra

    def tom_tat(self) -> dict:
        nav = self.navUsd
        return {
            # Cờ trung thực đứng ĐẦU, không nhét cuối bảng: người đọc phải
            # gặp nó trước khi gặp con số.
            "nguonThat": self.nguonThat,
            "loiNhac": (None if self.nguonThat else
                        "MÔ PHỎNG — không đọc số dư từ sàn nào. Chưa có lớp "
                        "đặt lệnh nên chưa có vị thế thật để mà đọc."),
            "navUsd": nav,
            "navLaVonGoc": True,
            "tuQuanUsd": self.tuQuanUsd,
            "ngoaiUsd": self.ngoaiUsd,
            "ngoaiDayDu": self.ngoaiDayDu,
            "ngoai": list(self.ngoai.values()),
            "loiNhacNgoai": (None if self.ngoaiDayDu else
                             "KHÔNG đọc được một nguồn vốn ngoài — NAV đang "
                             "thiếu một phần chưa biết bao nhiêu, nên mọi "
                             "trần tính theo NAV đang RỘNG HƠN sự thật"),
            "tienMatUsd": self.tienMatUsd,
            "daCamKetUsd": self.daCamKetUsd,
            "tiLeDungVon": (self.daCamKetUsd / nav) if nav else 0.0,
            "vonBanDauUsd": self.vonBanDauUsd,
            "laiLoDaThucHienUsd": self.laiLoDaThucHienUsd,
            "soViThe": len(self.viThe),
            "phoiNhiemRong": self.phoi_nhiem_rong(),
            "phoiNhiemTho": self.phoi_nhiem_tho(),
            "phoiNhiemCang": self.phoi_nhiem_cang(),
            "phoiNhiemChuoi": self.phoi_nhiem_chuoi(),
            "phoiNhiemTy": self.phoi_nhiem_ty(),
            "viThe": {k: [c.tom_tat() for c in v]
                      for k, v in list(self.viThe.items())[:40]},
        }
