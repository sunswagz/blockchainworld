"""Dòng sống — WebSocket CLOB, đường duy nhất thấy sổ của khung ĐANG CHẠY.

## Vì sao đây không phải "tối ưu tốc độ" mà là thứ mở khoá

Bản đầu của runtime hỏi Gamma + CLOB bằng HTTP mỗi 2 giây. Đo lúc 08:54:12
UTC, câu hỏi `active=true, closed=false, end_date_min=now` trả về:

    khung 09:00 (bắt đầu 08:55)  ->  chưa mở
    khung 09:05                  ->  chưa mở
    khung 09:10                  ->  chưa mở

    MỌI market kết thúc trong 300 giây tới: 0

Khung đáng lẽ đang chạy KHÔNG có trong danh sách. Và những khung thấy được
thì sổ của chúng là **thang chờ** trải từ 0,001 tới 0,999 — trông như hơn
một triệu cổ thanh khoản, thực chất không mức nào là báo giá thật.

Nên với REST, runtime không bao giờ chạm được vào một sổ thật. Không phải
chậm — là **không thấy**. WebSocket đăng ký theo `asset_id` và nhận đẩy mọi
thay đổi, kể cả của khung REST không liệt kê.

## Ba thứ phải làm đúng, cả ba đều hỏng im lặng

1. **`book` là ẢNH ĐẦY ĐỦ, `price_change` là VÁ.** Trộn hai loại như nhau
   thì sổ trôi dần khỏi sự thật mà không sai ở đâu rõ ràng. Mỗi `book`
   phải THAY hẳn sổ cũ; mỗi `price_change` chỉ sửa đúng mức nó nói.

2. **Khối lượng 0 nghĩa là XOÁ mức, không phải mức có 0 cổ.** Giữ lại mức
   rỗng thì `soMuc` đếm sai và mọi phép đo độ sâu lệch theo.

3. **Mất kết nối phải làm sổ THIU, không được giữ sổ cũ như thật.** Đây là
   chỗ nguy nhất: một sổ đứng yên trông y hệt một chợ đứng yên. Nên mỗi sổ
   mang dấu thời gian, và `rui_ro.py` từ chối mọi lệnh đặt trên sổ quá tuổi.
"""
from __future__ import annotations

import json
import threading
import time

from .bus import bus
from .so_lenh import Muc, SoLenh

WSS = "wss://ws-subscriptions-clob.polymarket.com/ws/market"


class _ChuaCoToken(Exception):
    """Chưa đăng ký token nào — khác hẳn với đứt kết nối."""


class DongSong:
    """Giữ sổ lệnh sống cho một tập token, cập nhật bằng WebSocket."""

    def __init__(self, wss: str = WSS) -> None:
        self.wss = wss
        self.so: dict[str, SoLenh] = {}          # asset_id -> sổ
        self.nhan: dict[str, tuple[str, str]] = {}   # asset_id -> (mã, bên)
        self._khoa = threading.Lock()
        self._chay = False
        self._luong: threading.Thread | None = None
        self.noiLucMs = 0.0
        self.tinNhan = 0
        self.soLanNoiLai = 0
        self.loiCuoi = ""

    # ── đăng ký ───────────────────────────────────────────────────────────
    def dang_ky(self, assetId: str, ma: str, ben: str) -> None:
        with self._khoa:
            self.nhan[assetId] = (ma, ben)

    def bo_dang_ky(self, assetId: str) -> None:
        with self._khoa:
            self.nhan.pop(assetId, None)
            self.so.pop(assetId, None)

    def danh_sach(self) -> list[str]:
        with self._khoa:
            return list(self.nhan.keys())

    # ── vòng đời ──────────────────────────────────────────────────────────
    def bat(self) -> None:
        if self._chay:
            return
        self._chay = True
        self._luong = threading.Thread(target=self._vong, daemon=True)
        self._luong.start()

    def dung(self) -> None:
        self._chay = False

    def _vong(self) -> None:
        """Nối lại với thời gian chờ tăng dần. Không bao giờ bỏ cuộc hẳn."""
        cho = 1.0
        while self._chay:
            try:
                self._mot_phien()
                cho = 1.0                     # nối được thì đặt lại
            except _ChuaCoToken:
                continue                      # chưa có gì để nối, không đếm
            except Exception as e:            # noqa: BLE001
                self.loiCuoi = f"{type(e).__name__}: {e}"
                bus.ghi(f"dòng sống đứt: {self.loiCuoi}", loai="canh")
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
            # Chưa đăng ký token nào thì KHÔNG phải là đứt kết nối. Bản đầu
            # đếm chỗ này vào `soLanNoiLai`, nên buồng lái hiện "nối lại 13
            # lần" trong khi chưa từng có gì để nối — một con số báo động
            # giả, và báo động giả thì người ta tắt cả báo động thật.
            time.sleep(2.0)
            raise _ChuaCoToken()

        # `websockets` KHÔNG tự đọc HTTPS_PROXY như `httpx` — nên nếu
        # không truyền vào đây thì phần REST đi lối proxy còn phần dòng
        # sống vẫn đi đường thẳng, và ta được một cỗ máy nửa thấy nửa mù
        # mà không có gì báo.
        from .nguon import nguon as _ng
        _proxy = _ng.proxy
        with connect(self.wss, open_timeout=10, close_timeout=3,
                     **({"proxy": _proxy} if _proxy else {})) as ws:
            ws.send(json.dumps({"assets_ids": ds, "type": "market"}))
            self.noiLucMs = time.time() * 1000.0
            bus.ghi(f"dòng sống đã nối — {len(ds)} token", loai="he")

            while self._chay:
                # Token theo dõi đổi thì phải đăng ký lại: mỗi khung 5 phút
                # là một cặp asset_id MỚI, nên danh sách đổi liên tục.
                if set(self.danh_sach()) != set(ds):
                    return
                try:
                    tho = ws.recv(timeout=20)
                except TimeoutError:
                    continue
                self.tinNhan += 1
                self._nhan(tho)

    # ── xử lý tin ─────────────────────────────────────────────────────────
    def _nhan(self, tho) -> None:
        try:
            d = json.loads(tho)
        except (json.JSONDecodeError, TypeError):
            return
        for tin in (d if isinstance(d, list) else [d]):
            if not isinstance(tin, dict):
                continue
            loai = tin.get("event_type") or tin.get("type")
            if loai == "book":
                self._anh_day_du(tin)
            elif loai == "price_change":
                self._va(tin)

    def _anh_day_du(self, tin: dict) -> None:
        aid = tin.get("asset_id") or tin.get("market")
        if not aid:
            return
        with self._khoa:
            ma, ben = self.nhan.get(aid, ("?", "?"))
        self._dat(aid, SoLenh(
            ma=ma, ben=ben,
            bid=_muc(tin.get("bids") or tin.get("buys"), giam=True),
            ask=_muc(tin.get("asks") or tin.get("sells"), giam=False),
            nhanLucMs=time.time() * 1000.0,
        ))

    def _va(self, tin: dict) -> None:
        aid = tin.get("asset_id") or tin.get("market")
        if not aid:
            return
        with self._khoa:
            so = self.so.get(aid)
        if so is None:
            return       # chưa có ảnh đầy đủ thì vá vào đâu

        doi = tin.get("changes") or tin.get("price_changes") or []
        if isinstance(doi, dict):
            doi = [doi]
        for c in doi:
            try:
                gia = float(c.get("price"))
                luong = float(c.get("size"))
            except (TypeError, ValueError, AttributeError):
                continue
            ben = (c.get("side") or "").upper()
            day = so.bid if ben in ("BUY", "BID") else so.ask
            _va_muc(day, gia, luong, giam=(day is so.bid))
        so.nhanLucMs = time.time() * 1000.0

    def _dat(self, aid: str, so: SoLenh) -> None:
        with self._khoa:
            self.so[aid] = so

    # ── đọc ───────────────────────────────────────────────────────────────
    def lay(self, assetId: str) -> SoLenh | None:
        with self._khoa:
            return self.so.get(assetId)

    def tuoi_ms(self, assetId: str) -> float | None:
        so = self.lay(assetId)
        if so is None or so.nhanLucMs <= 0:
            return None
        return time.time() * 1000.0 - so.nhanLucMs

    def tom_tat(self) -> dict:
        with self._khoa:
            n = len(self.so)
            dk = len(self.nhan)
        return {
            "dangNoi": self._chay and self.noiLucMs > 0,
            "soToken": dk,
            "soSo": n,
            "tinNhan": self.tinNhan,
            "soLanNoiLai": self.soLanNoiLai,
            "loiCuoi": self.loiCuoi,
            "noiLucMs": self.noiLucMs,
        }


def _muc(ds, giam: bool) -> list[Muc]:
    ra: list[Muc] = []
    for m in (ds or []):
        try:
            g, l = float(m.get("price")), float(m.get("size"))
        except (TypeError, ValueError, AttributeError):
            continue
        if l > 0 and 0.0 <= g <= 1.0:
            ra.append(Muc(g, l))
    ra.sort(key=lambda x: x.gia, reverse=giam)
    return ra


def _va_muc(day: list[Muc], gia: float, luong: float, giam: bool) -> None:
    """Sửa một mức. Khối lượng 0 là XOÁ mức, không phải mức có 0 cổ."""
    for i, m in enumerate(day):
        if abs(m.gia - gia) < 1e-9:
            if luong <= 0:
                day.pop(i)
            else:
                day[i] = Muc(gia, luong)
            return
    if luong > 0:
        day.append(Muc(gia, luong))
        day.sort(key=lambda x: x.gia, reverse=giam)


dong_song = DongSong()
