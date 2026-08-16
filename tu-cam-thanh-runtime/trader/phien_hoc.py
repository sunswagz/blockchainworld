"""Phiên huấn luyện — chạy nền, có tiến độ, một phiên tại một thời điểm.

Lớp mỏng giữa HTTP và `huanluyen.py`. Tồn tại vì lần sinh chuỗi tín hiệu đầu
tiên mất khoảng sáu phút: giữ nó trong một request là trình duyệt hết giờ chờ,
người dùng bấm lại, và hai lượt tính cùng chạy đè nhau.

Chỉ cho MỘT phiên chạy một lúc. Không chặn thì mỗi lần bấm nút lại đẻ thêm một
luồng ăn CPU, và cỗ máy chạy lại vốn đã ăn hết một nhân.
"""
from __future__ import annotations

import threading
import time
import traceback
from typing import Any

from . import bai_hoc_lich_su, chien_luoc, huanluyen as HL
from .brain import THAM_MAC_DINH
from .bus import bus
from .config import CONFIG

_khoa = threading.Lock()
_phien: dict[str, Any] = {
    "trangThai": "chưa chạy", "viec": None, "phanTram": 0,
    "batDau": None, "xong": None, "ketQua": None, "loi": None,
}


def trang_thai() -> dict:
    return dict(_phien)


def dang_chay() -> bool:
    return _phien["trangThai"] == "đang chạy"


def _dat(**kw) -> None:
    _phien.update(kw)


def _chay(viec: str, tham: dict) -> None:
    try:
        nen = HL.nap_nen()
        if not nen:
            _dat(trangThai="lỗi", loi="chưa có nến lịch sử — chạy scripts/tai-lich-su.py trước",
                 xong=time.time())
            return

        symbol = CONFIG["symbol"]

        def tien_do_chuoi(a: int, b: int) -> None:
            # Sinh chuỗi chiếm gần hết thời gian nên nó lấy 0–80% thanh tiến độ.
            # Cho nó 0–100 rồi để phần chạy lại nhảy vọt là thanh đứng im sáu
            # phút rồi xong ngay — người xem sẽ tưởng máy treo.
            _dat(phanTram=round(a / max(1, b) * 80), viec=f"{viec} · đọc lịch sử {a}/{b} nến")

        chuoi, tu = HL.lay_chuoi(nen, symbol, bao_tien_do=tien_do_chuoi)
        _dat(phanTram=80, viec=f"{viec} · chuỗi tín hiệu ({len(chuoi)} điểm, từ {tu})")

        if viec == "chay-lai":
            kq = HL.chay_lai(nen, symbol=symbol, chuoi=chuoi,
                             tham=tham.get("tham"), rieng=tham.get("rieng"),
                             bo_qua_kill=bool(tham.get("boQuaKill")),
                             toi_da_nen_giu=int(tham.get("toiDaNenGiu", 48)))
            kq["baiHoc"] = HL.duc_bai_hoc(kq)
            kq["nguonChuoi"] = tu
            # Đổ vào TRÍ NHỚ NGỮ NGHĨA (kho riêng) để bộ não đọc được ở những
            # lượt sau. Không có bước này thì mọi thứ phòng huấn luyện tìm ra
            # chỉ nằm trên màn hình rồi bay mất khi đóng tab.
            kq["daDucVaoTriNho"] = bai_hoc_lich_su.duc(
                kq, tham=tham.get("tham") or {})
            # 133 lệnh × mỗi lệnh một dòng thì gửi hết được; nhưng đoạn dữ liệu
            # dài hơn sẽ ra hàng nghìn, và không ai đọc quá vài chục dòng cuối.
            kq["lenh"] = kq["lenh"][-120:]
            _dat(ketQua=kq)

        elif viec == "quet":
            def tien_do_quet(a: int, b: int, bo: dict) -> None:
                _dat(phanTram=80 + round(a / max(1, b) * 20),
                     viec=f"dò tham số {a}/{b}")

            kq = HL.quet(nen, symbol=symbol, chuoi=chuoi,
                         luoi=tham.get("luoi") or None,
                         ty_le_trong_mau=float(tham.get("tyLeTrongMau", 0.7)),
                         bao_tien_do=tien_do_quet)
            kq["nguonChuoi"] = tu
            _dat(ketQua=kq)
        elif viec == "danh-gia":
            # Đo challenger trên CÙNG đoạn ngoài mẫu với champion. Cắt ở đúng
            # mốc mà phép dò dùng, để con số so được với nhau.
            tf = CONFIG["timeframes"]["primary"]
            moc = int(len(nen[tf]) * float(tham.get("tyLeTrongMau", 0.7)))

            def chay(ma: str, th: dict) -> dict:
                trong = HL.chay_lai(nen, symbol=symbol, chuoi=chuoi, bo_luat=ma,
                                    tham=th, tu_nen=0, den_nen=moc, bo_qua_kill=True)
                ngoai = HL.chay_lai(nen, symbol=symbol, chuoi=chuoi, bo_luat=ma,
                                    tham=th, tu_nen=moc, bo_qua_kill=True)
                tk = dict(ngoai["thongKe"])
                tr = trong["thongKe"]["kyVongR"]
                # Khớp trội chỉ có nghĩa khi CẢ HAI đầu đều có số.
                tk["khopTroi"] = (round(tr - tk["kyVongR"], 3)
                                  if (tr is not None and tk["kyVongR"] is not None) else None)
                tk["trongMau"] = trong["thongKe"]
                tk["boLuat"] = ma
                return tk

            _dat(phanTram=90, viec="đo challenger và champion")
            kq = chien_luoc.danh_gia(tham.get("khoa", ""), chay)
            _dat(ketQua=kq)

        else:
            _dat(trangThai="lỗi", loi=f"việc lạ: {viec}", xong=time.time())
            return

        _dat(trangThai="xong", phanTram=100, viec=viec, xong=time.time())
        bus.emit("hoc", "phien-xong", f"phiên huấn luyện «{viec}» xong")

    except Exception as e:  # noqa: BLE001
        _dat(trangThai="lỗi", loi=f"{type(e).__name__}: {e}", xong=time.time())
        bus.log("hoc", "phien-loi", f"phiên huấn luyện hỏng: {e}")
        traceback.print_exc()


def bat_dau(viec: str, tham: dict | None = None) -> dict:
    """Khởi động một phiên. Trả về trạng thái ngay, không chờ."""
    with _khoa:
        if dang_chay():
            return {"ok": False, "vi_sao": "đang có một phiên chạy", **trang_thai()}
        _phien.update({"trangThai": "đang chạy", "viec": viec, "phanTram": 0,
                       "batDau": time.time(), "xong": None, "ketQua": None, "loi": None})
    threading.Thread(target=_chay, args=(viec, tham or {}),
                     name=f"phien-hoc-{viec}", daemon=True).start()
    bus.emit("hoc", "phien-bat-dau", f"bắt đầu phiên huấn luyện «{viec}»")
    return {"ok": True, **trang_thai()}


def san_sang() -> dict:
    """Có đủ dữ liệu để chạy chưa, và chuỗi đã dựng sẵn chưa."""
    nen = HL.nap_nen()
    if not nen:
        return {"coNen": False, "goiY": "chạy: python scripts/tai-lich-su.py --so 4000"}
    tf = CONFIG["timeframes"]["primary"]
    ctx = CONFIG["timeframes"]["context"]
    vt = HL._van_tay(nen, CONFIG["symbol"])
    f = HL.ROOT / "data" / "chuoi" / f"{CONFIG['symbol']}-{vt}.json"
    return {
        "coNen": True, "symbol": CONFIG["symbol"],
        "soNen": {tf: len(nen[tf]), ctx: len(nen[ctx])},
        "tu": nen[tf][0]["t"], "den": nen[tf][-1]["t"],
        "coChuoiSan": vt in HL._bo_nho or f.exists(),
        "vanTay": vt,
        "luoiMacDinh": HL.LUOI_MAC_DINH,
        "thamMacDinh": THAM_MAC_DINH,
    }
