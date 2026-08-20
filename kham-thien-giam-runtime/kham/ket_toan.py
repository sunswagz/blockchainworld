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
                bus.ghi(f"bỏ theo dõi {slug}: hỏ�i {c.soLanHoi} lần không ra kết quả",
                        loai="canh")
                del self.cho[slug]
                continue
            if self._thu_ket_toan(c):
                del self.cho[slug]
                xong += 1
        return xong

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
                phiUsd=0.0, laiLo=lai_lo, giaCap=v.giaCap,
                chienThuat=list(c.chienThuat), pDuDoan=c.pDuDoanUp,
            )
            self.so.ghi(g)
            if self.risk is not None:
                self.risk.ghi_lai_lo(lai_lo)
            # dọn vị thế: khung đã kết toán, tồn kho về 0
            v.coUp = v.coDown = 0.0
            v.tienUp = v.tienDown = 0.0
            v.choCap.clear()
            bus.ghi(f"kết toán {c.slug}: UP {'thắng' if upThang else 'thua'} · "
                    f"lãi lỗ ${lai_lo:+.4f}", loai="khop")
        else:
            bus.ghi(f"kết toán {c.slug}: UP {'thắng' if upThang else 'thua'} "
                    f"(không có vị thế)", loai="tin")

        # Hiệu chỉnh ghi CẢ khi không có vị thế — xem ghi_danh().
        if c.pDuDoanUp is not None:
            self.hieuChinh.them(c.pDuDoanUp, upThang)
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
            "ganDay": self.xong[-12:],
            "cho": [
                {"slug": c.slug, "conMs": c.ketThucMs - time.time() * 1000.0,
                 "pDuDoan": c.pDuDoanUp, "soLanHoi": c.soLanHoi}
                for c in list(self.cho.values())[:12]
            ],
        }
