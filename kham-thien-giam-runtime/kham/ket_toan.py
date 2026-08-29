"""Kết Toán — khép vòng học. Không có module này thì bot KHÔNG THỂ học.

## Vòng hở đã tồn tại và không ai thấy

Bản đầu có đủ `HieuChinh`, `So`, `thong_ke()`, `lai_lo_khi_ket_qua()` — và
**không dòng nào gọi chúng**. Hậu quả dây chuyền, im lặng hoàn toàn:

    không ai ghi kết toán
        -> HieuChinh.tong_mau mãi = 0
        -> du_de_dung_kelly() mãi = False   -> Kelly khoá vĩnh viễn
        -> thong_ke() mãi trả chuaCo=True   -> không kỳ vọng, không đuôi
        -> bot chạy bao lâu cũng không học được gì

Không phép kiểm nào đỏ, vì mỗi mảnh đều đúng khi kiểm riêng. Chỉ có cái
VÒNG là không khép. Đây là loại lỗi kiến trúc mà `selftest` không bắt được
— nó kiểm từng hàm, không kiểm rằng ai đó thật sự gọi hàm.

## Hai nguồn sự thật, và vì sao phải có cả hai

Tài liệu nêu bốn nguyên nhân thua KHÔNG phải rủi ro thị trường: sai nguồn
giá kết toán, sai giá mở, hiểu sai luật kết toán, không kịp huỷ lệnh. Ba
cái đầu đều là **bất đồng giữa cái mình tưởng và cái sàn trả tiền theo**.

Nên ở đây đọc kết quả bằng hai đường độc lập:

    SÀN     `outcomePrices` của Gamma sau khi market đóng — đây là thứ
            THẬT SỰ trả tiền, nên nó luôn thắng khi hai bên khác nhau
    TỰ TÍNH so giá đóng Binance với giá mở khung

Hai đường khớp nhau thì yên tâm. Lệch nhau là một tín hiệu rất đắt: hoặc
mình lấy sai giá mở, hoặc hiểu sai luật kết toán — và biết được điều đó
TRƯỚC khi chạy tiền thật đáng giá hơn nhiều so với biết sau.
"""
from __future__ import annotations

import datetime as dt
import json
import time
from dataclasses import dataclass, field

from . import nan_lai
from .ket_qua import so_ket_qua
from .bus import bus
from .dinh_gia import HieuChinh
from .kho_doi import Kho
from .nguon import nguon
from .so import GhiKetToan, So, bay_gio


@dataclass
class ChoKetToan:
    """Một khung đã đóng cửa, đang chờ biết kết quả."""
    ma: str
    slug: str
    ketThucMs: float
    giaMo: float
    capNen: str
    tokenUp: str
    tokenDown: str
    pDuDoanUp: float | None = None      # mô hình nói gì lúc gần đóng
    chienThuat: list[str] = field(default_factory=list)
    soLanHoi: int = 0
    hoiLanCuoiMs: float = 0.0


class KetToan:
    """Theo dõi khung đã đóng, lấy kết quả, rồi ghi vào sổ và sổ hiệu chỉnh."""

    # Đợi một lát sau khi đóng rồi mới hỏi: sàn cần thời gian để chốt.
    CHO_TRUOC_KHI_HOI_GIAY = 20.0
    CACH_HAI_LAN_HOI_GIAY = 30.0
    TOI_DA_HOI = 40                      # ~20 phút rồi bỏ

    def __init__(self, kho: Kho, hieuChinh: HieuChinh, so: So, risk=None) -> None:
        self.kho = kho
        self.hieuChinh = hieuChinh
        self.so = so
        self.risk = risk
        self.cho: dict[str, ChoKetToan] = {}
        self.xong: list[dict] = []
        self.soBatDong = 0
        self.soTreo = 0
        self.tienTreoUsd = 0.0

    # ── ghi danh ──────────────────────────────────────────────────────────
    def ghi_danh(self, ma: str, slug: str, ketThucMs: float, giaMo: float,
                 capNen: str, tokenUp: str, tokenDown: str,
                 pUp: float | None = None, chienThuat: list[str] | None = None) -> None:
        """Nhớ một khung để sau còn hỏi kết quả.

        Gọi ở MỖI vòng cho khung đang chạy, không phải chỉ khi có vị thế:
        hiệu chỉnh cần cả những lần mô hình đoán mà không vào lệnh, nếu
        không thì sổ hiệu chỉnh chỉ có những ca mình đã tự chọn — thiên
        lệch đúng chiều làm mô hình trông giỏi hơn thực tế.
        """
        c = self.cho.get(slug)
        if c is None:
            c = ChoKetToan(ma=ma, slug=slug, ketThucMs=ketThucMs, giaMo=giaMo,
                           capNen=capNen, tokenUp=tokenUp, tokenDown=tokenDown)
            self.cho[slug] = c
        # giữ dự đoán GẦN LÚC ĐÓNG nhất — đó là lúc mô hình biết nhiều nhất
        if pUp is not None:
            c.pDuDoanUp = pUp
        if chienThuat:
            for x in chienThuat:
                if x not in c.chienThuat:
                    c.chienThuat.append(x)

    # ── vòng soát ─────────────────────────────────────────────────────────
    def soat(self, bayGioMs: float | None = None) -> int:
        """Soát các khung đã đóng, lấy kết quả. Trả số khung vừa kết toán."""
        now = bayGioMs or time.time() * 1000.0
        xong = 0
        for slug, c in list(self.cho.items()):
            if now < c.ketThucMs + self.CHO_TRUOC_KHI_HOI_GIAY * 1000.0:
                continue
            if now - c.hoiLanCuoiMs < self.CACH_HAI_LAN_HOI_GIAY * 1000.0:
                continue
            c.hoiLanCuoiMs = now
            c.soLanHoi += 1
            if c.soLanHoi > self.TOI_DA_HOI:
                self._bo_theo_doi(slug, c)
                continue
            if self._thu_ket_toan(c):
                del self.cho[slug]
                xong += 1
        return xong

    def _bo_theo_doi(self, slug: str, c: ChoKetToan) -> None:
        """Thôi hỏi kết quả — nhưng phải TRẢ LẠI hạn mức, và khai ra.

        Bản đầu chỉ `del self.cho[slug]`. Vị thế trong `Kho` thì nằm lại
        mãi mãi, và `RiskEngine` đọc chính chỗ đó để tính "market này đã
        dùng bao nhiêu trên trần". Nên một khung không ra kết quả là
        market ấy **chết cho tới lúc khởi động lại**: mọi lệnh sau đều bị
        từ chối vì "đã dùng $X, chạm trần", trong khi tiền ấy không còn
        làm việc gì nữa. Không lỗi nào báo, không con số nào đỏ.

        Đã thấy tận mắt trên phiên phát lại: khớp đứng hẳn ở 398 lệnh
        trong khi cửa sổ vẫn mở thêm hàng nghìn — 12 khung thiếu kết quả
        là đủ khoá cả bốn market.

        Nhưng KHÔNG được ghi nó thành lỗ. Cổ phần vẫn nằm trên sàn và
        vẫn sẽ ngã ngũ; thứ mất là khả năng CHẤM ĐIỂM nó, không phải
        tiền. Nên: trả hạn mức, cộng vào sổ TREO, và nói to.
        """
        v = self.kho.viThe.get(c.ma)
        treo = 0.0
        if v is not None and (v.coUp > 0 or v.coDown > 0):
            treo = v.tienUp + v.tienDown
            v.don()
        self.tienTreoUsd += treo
        self.soTreo += 1
        bus.ghi(
            f"bỏ theo dõi {slug}: hỏi {c.soLanHoi} lần không ra kết quả"
            + (f" — TREO ${treo:.2f}, đã trả lại hạn mức cho {c.ma} "
               "(không tính là lỗ: cổ phần vẫn trên sàn, thứ mất là khả "
               "năng chấm điểm)" if treo > 0 else ""),
            loai="canh")
        del self.cho[slug]

    def _thu_ket_toan(self, c: ChoKetToan) -> bool:
        san = self._hoi_san(c)
        tu_tinh = self._tu_tinh(c)

        if san is None and tu_tinh is None:
            return False

        # Sàn luôn thắng: nó là thứ THẬT SỰ trả tiền.
        up_thang = san if san is not None else tu_tinh
        bat_dong = (san is not None and tu_tinh is not None and san != tu_tinh)
        if bat_dong:
            self.soBatDong += 1
            bus.ghi(
                f"BẤT ĐỒNG kết toán {c.slug}: sàn nói UP={san}, tự tính nói "
                f"UP={tu_tinh} — kiểm lại giá mở hoặc luật kết toán", loai="loi")

        self._ghi_so(c, up_thang, san, tu_tinh, bat_dong)
        return True

    def _hoi_san(self, c: ChoKetToan) -> bool | None:
        """Kết quả theo Gamma. None nếu chưa chốt."""
        d = nguon.market_theo_slug(c.slug)
        if not d:
            return None
        gia = d.get("outcomePrices")
        if isinstance(gia, str):
            try:
                gia = json.loads(gia)
            except json.JSONDecodeError:
                return None
        if not isinstance(gia, list) or len(gia) < 2:
            return None
        try:
            up, down = float(gia[0]), float(gia[1])
        except (TypeError, ValueError):
            return None
        # Chưa chốt thì hai giá còn ở giữa. Chỉ nhận khi đã về 0/1 rõ ràng.
        if abs(up - down) < 0.9:
            return None
        return up > down

    def _tu_tinh(self, c: ChoKetToan) -> bool | None:
        """Kết quả tự suy từ nến Binance đóng tại thời điểm khung kết thúc."""
        dong = nguon.gia_dong_khung(c.capNen, c.ketThucMs)
        if dong is None or not c.giaMo:
            return None
        if abs(dong - c.giaMo) < 1e-9:
            return None      # đúng bằng nhau thì luật kết toán quyết, đừng đoán
        return dong > c.giaMo

    # ── ghi sổ ────────────────────────────────────────────────────────────
    def _ghi_so(self, c: ChoKetToan, upThang: bool, san: bool | None,
                tuTinh: bool | None, batDong: bool) -> None:
        v = self.kho.viThe.get(c.ma)

        if v is not None and (v.coUp > 0 or v.coDown > 0):
            lai_lo = v.lai_lo_khi_ket_qua(upThang)
            g = GhiKetToan(
                luc=bay_gio(), ma=c.ma, upThang=upThang,
                coUp=v.coUp, coDown=v.coDown,
                tienVao=v.tienUp + v.tienDown,
                tienRa=v.gia_tri_khi_ket_qua(upThang),
                phiUsd=v.phiUsd, laiLo=lai_lo, giaCap=v.giaCap,
                chienThuat=list(c.chienThuat), pDuDoan=c.pDuDoanUp,
                pLucVao=v.pVaoTb, giaVaoTb=v.giaVaoTb,
            )
            self.so.ghi(g)
            if self.risk is not None:
                self.risk.ghi_lai_lo(lai_lo)
            v.don()          # khung đã kết toán, tồn kho về 0
            bus.ghi(f"kết toán {c.slug}: UP {'thắng' if upThang else 'thua'} · "
                    f"lãi lỗ ${lai_lo:+.4f}", loai="khop")
        else:
            bus.ghi(f"kết toán {c.slug}: UP {'thắng' if upThang else 'thua'} "
                    f"(không có vị thế)", loai="tin")

        # SỔ KẾT QUẢ ghi VÔ ĐIỀU KIỆN — kể cả khi mình không dự đoán gì.
        #
        # Kết quả một khung là sự thật về thế giới, không phải sản phẩm
        # của mình. Trước bản này nó nằm trong nhánh `pDuDoanUp is not
        # None`, nên khung nào thiếu nguyên liệu định giá là mất kết quả
        # luôn — trong khi băng vẫn ghi đủ khung hình của nó, và `chay_lai`
        # thì chấm bằng cách tra SỔ NÀY. Mất một dòng ở đây là mất vĩnh
        # viễn khả năng chấm điểm cả một cửa sổ, cho mọi bộ tham số về
        # sau. Sổ kết quả là hạ tầng, không phải phụ phẩm của một lượt đoán.
        so_ket_qua.them(c.slug, upThang, c.giaMo,
                        nguon="san" if san is not None else "tu-tinh")

        # Hiệu chỉnh thì NGƯỢC LẠI: nó chấm điểm chính mình, nên không có
        # dự đoán thì không có gì để chấm. Xem ghi_danh().
        if c.pDuDoanUp is not None:
            self.hieuChinh.them(c.pDuDoanUp, upThang)
            # Ghi thêm TỪNG CẶP thô. Sổ hiệu chỉnh chỉ lưu tổng theo ô;
            # từ tổng thì khớp được đường nắn nhưng KHÔNG kiểm được nó
            # ngoài mẫu — mà đó mới là phép phân biệt "học được quy luật"
            # với "học thuộc bảng".
            nan_lai.ghi_tho(c.pDuDoanUp, upThang, getattr(c, "ma", ""))
            self.hieuChinh.ghi()

        self.xong.append({
            "luc": bay_gio(), "slug": c.slug, "ma": c.ma, "upThang": upThang,
            "theoSan": san, "tuTinh": tuTinh, "batDong": batDong,
            "pDuDoan": c.pDuDoanUp, "coViThe": bool(v and (v.coUp or v.coDown)),
        })
        del self.xong[:-200]

    def tom_tat(self) -> dict:
        return {
            "dangCho": len(self.cho),
            "daKetToan": len(self.xong),
            "soBatDong": self.soBatDong,
            # Khung bỏ theo dõi vì không ra kết quả. Tiền treo KHÔNG
            # phải lỗ — cổ phần vẫn trên sàn — nhưng nó phải hiện ra:
            # con số này lớn lên nghĩa là ta đang mù dần về chính
            # những lệnh mình đã đặt.
            "soTreo": self.soTreo,
            "tienTreoUsd": self.tienTreoUsd,
            "ganDay": self.xong[-12:],
            "cho": [
                {"slug": c.slug, "conMs": c.ketThucMs - time.time() * 1000.0,
                 "pDuDoan": c.pDuDoanUp, "soLanHoi": c.soLanHoi}
                for c in list(self.cho.values())[:12]
            ],
        }
