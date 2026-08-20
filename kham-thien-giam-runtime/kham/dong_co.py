"""Sổ đăng ký ĐỘNG CƠ ĐỊNH GIÁ — một họ market, một động cơ.

Trước file này, chỗ duy nhất trong cả hệ biết "mình đang định giá crypto"
là một dòng ở `vong.py`. Đó là một mối nối tốt, nhưng nó chỉ giữ được MỘT
động cơ. File này biến nó thành một sổ đăng ký.

## Vì sao tách ở ĐÂY mà không tách chỗ khác

Đã đo bằng cách đọc import: `can_loi.py` — nơi tính lợi thế ăn được — chỉ
phụ thuộc `config` và `so_lenh`, không một dòng nào biết crypto là gì. Sổ
lệnh, VWAP, sức chứa, giá cặp, tồn kho, rủi ro chân lẻ, hiệu chỉnh, chạy
lại, vô địch, tiến hoá cũng vậy.

Nói cách khác, **phần "market này là gì" đã tự gom sẵn vào một chỗ**. Việc
ở đây chỉ là đặt tên cho chỗ đó và cho phép có nhiều hơn một.

Hệ quả thực tế: thêm một họ market không phải viết bot mới. Nó là viết
MỘT hàm định giá rồi khai vào sổ này.

## Cái KHÔNG được tách: vốn và rủi ro

Mỗi động cơ một cuốn sổ rủi ro riêng là hỏng, dù nghe có vẻ gọn hơn. Nếu
động cơ crypto giữ trần lỗ riêng và động cơ tài chính cũng giữ trần lỗ
riêng, thì một tin làm chạy cả hai sẽ khiến bạn lỗ gấp đôi trong lúc MỖI
động cơ đều báo "tôi vẫn trong hạn mức". Không cái nào sai, và không cái
nào thấy.

Nên `nhom` ở đây không phải nhãn cho đẹp — nó là khoá mà rủi ro trung tâm
dùng để gộp phơi nhiễm. Động cơ đề xuất; trung tâm quyết.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol

from .dinh_gia import GiaChuan


class HamDinhGia(Protocol):
    def __call__(self, ma: str, **thamSo) -> GiaChuan | None: ...


@dataclass(frozen=True)
class HoSoDongCo:
    """Một họ market và cách định giá nó.

    `canGi` là danh sách tên tham số BẮT BUỘC. Nó không phải tài liệu —
    `goi()` kiểm nó trước khi gọi, nên một động cơ khai thiếu nguyên liệu
    sẽ chết ngay ở đây với câu nói rõ thiếu gì, thay vì chết sâu bên trong
    bằng một `TypeError` không ai lần được.
    """

    ma: str
    ten: str
    nhom: str                 # khoá gộp phơi nhiễm ở rủi ro trung tâm
    mota: str
    nguonGia: str             # nguồn tham chiếu mà động cơ này cần
    canGi: tuple[str, ...]
    dinhGia: HamDinhGia
    nhipGiay: float = 2.0     # nhịp hợp lý cho họ này

    def thieu_gi(self, thamSo: dict) -> list[str]:
        return [t for t in self.canGi if thamSo.get(t) is None]


_SO: dict[str, HoSoDongCo] = {}


def khai(hs: HoSoDongCo) -> HoSoDongCo:
    if hs.ma in _SO:
        raise ValueError(f"động cơ '{hs.ma}' đã khai rồi")
    _SO[hs.ma] = hs
    return hs


def lay(ma: str) -> HoSoDongCo | None:
    return _SO.get(ma)


def danh_sach() -> list[HoSoDongCo]:
    return sorted(_SO.values(), key=lambda h: h.ma)


def goi(maDongCo: str, ma: str, **thamSo) -> tuple[GiaChuan | None, str | None]:
    """Gọi một động cơ. Trả (kết quả, lý do không có kết quả).

    Hai giá trị chứ không phải một, vì "không định giá được" có nhiều lý
    do rất khác nhau và người vận hành cần biết là lý do nào: khai sai tên
    động cơ, thiếu nguyên liệu, hay động cơ chạy rồi mà từ chối kết luận.
    Gộp cả ba thành `None` là vứt đi đúng phần thông tin đáng giá nhất.
    """
    hs = _SO.get(maDongCo)
    if hs is None:
        return None, f"không có động cơ '{maDongCo}' trong sổ đăng ký"
    thieu = hs.thieu_gi(thamSo)
    if thieu:
        return None, "thiếu nguyên liệu: " + ", ".join(thieu)
    gc = hs.dinhGia(ma, **thamSo)
    if gc is None:
        return None, "động cơ từ chối kết luận"
    return gc, None


def tom_tat() -> list[dict]:
    return [{"ma": h.ma, "ten": h.ten, "nhom": h.nhom, "mota": h.mota,
             "nguonGia": h.nguonGia, "canGi": list(h.canGi),
             "nhipGiay": h.nhipGiay} for h in danh_sach()]


# ── khai các động cơ ─────────────────────────────────────────────────
# Đặt ở cuối file và import trong hàm để tránh vòng import: `dinh_gia` và
# `cham_moc` đều import `GiaChuan` từ `dinh_gia`.

def _khai_san() -> None:
    from .dinh_gia import dinh_gia as _updown

    khai(HoSoDongCo(
        ma="updown-crypto",
        ten="Lên/Xuống cuối khung",
        nhom="crypto",
        mota=("Xác suất giá KẾT THÚC trên mốc. Khuếch tán log-chuẩn: "
              "z = [ln(S/K) − σ²τ/2] / (σ√τ), P = Φ(z)."),
        nguonGia="binance",
        canGi=("giaHienTai", "giaMo", "tauGiay"),
        dinhGia=_updown,
        nhipGiay=2.0,
    ))

    from .cham_moc import cham_moc as _cham

    khai(HoSoDongCo(
        ma="cham-moc-crypto",
        ten="Chạm mốc trước hạn",
        nhom="crypto",
        mota=("Xác suất giá CHẠM mốc ít nhất một lần trước hạn. Nguyên lý "
              "phản xạ: P ≈ 2·Φ(−|ln(K/S)|/(σ√τ)) — gần GẤP ĐÔI xác suất "
              "kết thúc trên mốc, và đó là chỗ hay bị định giá nhầm."),
        nguonGia="binance",
        canGi=("giaHienTai", "moc", "tauGiay", "dinhDaQua"),
        dinhGia=_cham,
        nhipGiay=30.0,
    ))


_khai_san()
