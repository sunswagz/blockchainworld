"""Dòng sống phía GIÁ NỀN — Binance qua WebSocket, mốc mili-giây.

Trước file này, hai phía của cỗ máy nhìn thế giới ở hai độ phân giải rất
khác nhau, và không ai để ý:

    Polymarket   WebSocket, mỗi tin một mốc mili-giây     ~ms
    Binance      REST `ticker/price`, hỏi vòng 2 giây     ~2000ms

Chênh lệch đó không phải chuyện làm cho đẹp. Nó quyết định **những gì cỗ
máy này có thể BIẾT**.

## Vì sao nó quan trọng đến thế

Toàn bộ luận điểm của loại bot này là: Polymarket cập nhật CHẬM hơn giá
gốc trên Binance, và khoảng trễ đó là chỗ có lợi thế. Nhưng các con số
được đưa ra chênh nhau rất xa:

    một bài viết lan truyền (4/2026)   ≈ 2.700 ms
    nghiên cứu OpenMarket (7/2026)     ≈   347 ms

Tám lần. Và với nhịp hỏi 2 giây, cỗ máy này **không đo được cái nào trong
hai con số đó** — nó thô hơn cả hai. Nghĩa là ta đang phải TIN một con số
thay vì đo nó, đúng thứ mà cả kiến trúc này được dựng để tránh.

Sau file này, ta tự đo. Xem `do_tre.py`.

## Vì sao `bookTicker` chứ không phải `trade`

`bookTicker` bắn ra mỗi khi giá mua/bán tốt nhất đổi — kể cả khi KHÔNG có
giao dịch nào khớp. Đó mới là thứ tương ứng với sổ lệnh bên Polymarket.
Dùng `trade` thì chỉ thấy lúc có người chịu bước qua spread, và sẽ đo ra
một độ trễ dài hơn thực tế vì mình bắt đầu bấm giờ muộn.

## Cái file này KHÔNG làm

Không thay `nguon.py`. Giá REST vẫn được giữ làm đường thứ hai, vì hai
đường độc lập là cách duy nhất để một đường hỏng lộ ra thành bất đồng
thay vì lộ ra thành tiền — cùng lý lẽ với `ket_toan.py` đọc kết quả bằng
hai nguồn.
"""
from __future__ import annotations

import json
import threading
import time
from collections import deque

from .bus import bus

WSS = "wss://stream.binance.com:9443/stream"

# Vòng đệm mỗi mã: đủ cho vài phút ở nhịp bookTicker của BTC.
SAU_VONG_DEM = 4096


class _ChuaCoMa(Exception):
    """Chưa đăng ký mã nào — không phải đứt kết nối, đừng đếm."""


class DongSongNen:
    def __init__(self, wss: str = WSS) -> None:
        self.wss = wss
        self._ma: set[str] = set()                     # 'btcusdt'
        self._bang: dict[str, deque] = {}              # ma → [(tMs, mid)]
        self._khoa = threading.Lock()
        self._chay = False
        self._luong: threading.Thread | None = None
        self.tinNhan = 0
        self.soLanNoiLai = 0
        self.loiCuoi = ""
        self.noiLucMs = 0.0

    # ── đăng ký ───────────────────────────────────────────────────────
    def dang_ky(self, cap: str) -> None:
        with self._khoa:
            m = cap.lower()
            self._ma.add(m)
            self._bang.setdefault(m, deque(maxlen=SAU_VONG_DEM))

    def danh_sach(self) -> list[str]:
        with self._khoa:
            return sorted(self._ma)

    # ── vòng đời ──────────────────────────────────────────────────────
    def bat(self) -> None:
        if self._chay:
            return
        self._chay = True
        self._luong = threading.Thread(target=self._vong, daemon=True)
        self._luong.start()

    def dung(self) -> None:
        self._chay = False

    def _vong(self) -> None:
        cho = 1.0
        while self._chay:
            try:
                self._mot_phien()
                cho = 1.0
            except _ChuaCoMa:
                continue
            except Exception as e:                      # noqa: BLE001
                self.loiCuoi = f"{type(e).__name__}: {e}"
                bus.ghi(f"dòng nền đứt: {self.loiCuoi}", loai="canh")
            if not self._chay:
                break
            self.soLanNoiLai += 1
            time.sleep(cho)
            cho = min(30.0, cho * 1.8)

    def _mot_phien(self) -> None:
        try:
            from websockets.sync.client import connect
        except ImportError as e:
            raise RuntimeError("thiếu gói `websockets` — pip install websockets") from e

        ds = self.danh_sach()
        if not ds:
            time.sleep(2.0)
            raise _ChuaCoMa()

        duong = "/".join(f"{m}@bookTicker" for m in ds)
        with connect(f"{self.wss}?streams={duong}",
                     open_timeout=10, close_timeout=3) as ws:
            self.noiLucMs = time.time() * 1000.0
            bus.ghi(f"dòng nền đã nối — {len(ds)} mã (bookTicker)", loai="he")
            while self._chay:
                if set(self.danh_sach()) != set(ds):
                    return
                try:
                    tho = ws.recv(timeout=20)
                except TimeoutError:
                    continue
                self.tinNhan += 1
                self._nhan(tho)

    def _nhan(self, tho) -> None:
        try:
            goi = json.loads(tho)
        except (TypeError, ValueError):
            return
        d = goi.get("data") or goi
        cap = (d.get("s") or "").lower()
        if not cap:
            return
        try:
            mua, ban = float(d["b"]), float(d["a"])
        except (KeyError, TypeError, ValueError):
            return
        if mua <= 0 or ban <= 0:
            return
        # Dùng GIỮA hai giá tốt nhất, không dùng giá khớp cuối. Giá khớp
        # cuối nhảy qua lại giữa mua và bán theo phía người chủ động, tạo
        # ra một dao động giả bằng đúng bề rộng spread — ở nhịp mili-giây
        # thì dao động giả đó lớn hơn hẳn tín hiệu mình đang tìm.
        giua = (mua + ban) / 2.0
        t = time.time() * 1000.0
        with self._khoa:
            b = self._bang.get(cap)
            if b is not None:
                b.append((t, giua))

    # ── đọc ───────────────────────────────────────────────────────────
    def gia(self, cap: str) -> float | None:
        with self._khoa:
            b = self._bang.get(cap.lower())
            return b[-1][1] if b else None

    def tuoi_ms(self, cap: str) -> float | None:
        with self._khoa:
            b = self._bang.get(cap.lower())
            if not b:
                return None
            return time.time() * 1000.0 - b[-1][0]

    def lat(self, cap: str, tuMs: float, denMs: float) -> list[tuple[float, float]]:
        """Các mẫu trong một khoảng thời gian, để `do_tre.py` dùng."""
        with self._khoa:
            b = self._bang.get(cap.lower())
            if not b:
                return []
            return [(t, g) for t, g in b if tuMs <= t <= denMs]

    def gan_nhat_truoc(self, cap: str, tMs: float) -> tuple[float, float] | None:
        with self._khoa:
            b = self._bang.get(cap.lower())
            if not b:
                return None
            ra = None
            for t, g in b:
                if t <= tMs:
                    ra = (t, g)
                else:
                    break
            return ra

    def tom_tat(self) -> dict:
        with self._khoa:
            ma = sorted(self._ma)
            sau = {m: len(self._bang.get(m) or ()) for m in ma}
        return {
            "dangNoi": bool(self.noiLucMs) and self._chay,
            "soMa": len(ma), "ma": ma, "tinNhan": self.tinNhan,
            "soLanNoiLai": self.soLanNoiLai, "loiCuoi": self.loiCuoi,
            "noiLucMs": self.noiLucMs, "sauVongDem": sau,
        }


dongSongNen = DongSongNen()
