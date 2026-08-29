"""NGHI THỨC — những phép đo nặng, chạy định kỳ, không ai phải nhớ gõ lệnh.

Lò chưng cất đã tự chạy mỗi 20 phút, nhưng nó chỉ ĐỌC các kho đo. Những cỗ máy
SINH RA số cho nó thì vẫn phải gõ tay:

    do-mau-gia.py       ~4 phút   13 mẫu giá trên toàn bộ nến
    do-khung.py         ~2 phút   hình học từng khung, mọi coin
    dau-chien-luoc.py   ~1 phút   mọi bộ luật vs champion, ngoài mẫu
    ban-giao.py         ~5 giây   bản tóm tắt cho lượt làm việc sau

Gõ tay nghĩa là chúng chỉ chạy khi có người nhớ. Một hệ tiến hoá mà bước tiến hoá
phụ thuộc trí nhớ của người vận hành thì không phải hệ tiến hoá.

THỨ TỰ KHÔNG ĐƯỢC ĐỔI

Ba việc ĐO chạy trước, rồi mới chưng cất, rồi mới bàn giao. Chưng cất trước thì
lò đọc lại số của hôm qua; bàn giao trước thì bản tóm tắt mô tả trạng thái chưa
có kết quả đo mới — cả hai đều xanh, đều sai, và đều không báo gì.

VÌ SAO CHẠY BẰNG TIẾN TRÌNH RIÊNG, KHÔNG PHẢI LUỒNG

Đo mẫu giá ăn hết một nhân trong bốn phút. Chạy nó trong luồng của vòng giao
dịch thì GIL biến bốn phút ấy thành bốn phút vòng lặp bị bóp — nến trôi qua mà
bot không kịp phản ứng. Tiến trình riêng thì hệ điều hành tự chia nhân, và vòng
giao dịch không biết gì.

VÌ SAO CÓ CỜ TRÊN ĐĨA

Runtime được dựng lại thường xuyên (sửa `.py` là phải dựng lại mới có hiệu lực).
Giữ mốc thời gian trong RAM thì mỗi lần dựng lại là chạy lại từ đầu cả hai phép
đo nặng — vài lần dựng trong một buổi là máy không làm được việc gì khác.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import subprocess
import sys
import threading
import time
from typing import Any

from .bus import bus
from .config import DATA_DIR, ROOT

# 6 tiếng: nguồn của hai phép đo này là nến lịch sử và sổ chiến lược — thứ đổi
# theo ngày chứ không theo giờ. Chạy dày hơn chỉ tốn nhân mà ra cùng một số.
MOI_GIAY = 6 * 3600

# Đài quan sát gọi sàn ngoài và tự giới hạn tần suất, nên nó CHẬM: đo thật là
# ~3 hồ sơ trong 4 phút, tức 48 hồ sơ mất hơn một giờ.
#
# 20 phút là con số tôi đoán lúc đầu và nó sẽ cắt ngang giữa chừng — ghi "hỏng"
# cho một việc đang chạy đúng, rồi lần sau lại bắt đầu lại từ đầu. Một giờ rưỡi
# vẫn nằm gọn trong nhịp 6 tiếng của nghi thức, và luồng này không chặn vòng
# giao dịch.
QUAN_SAT_HET_GIAY = 5400
COC = DATA_DIR / "nghi-thuc.json"

_khoa = threading.Lock()
_trang_thai: dict[str, Any] = {
    "dangChay": False, "viec": None, "batDau": None, "xong": None,
    "ketQua": {}, "loi": None,
}

VIEC = (
    ("mẫu giá", [sys.executable, "scripts/do-mau-gia.py", "--ghi"], 900),
    ("hình học khung", [sys.executable, "scripts/do-khung.py", "--ghi"], 900),
    ("đấu chiến lược", [sys.executable, "scripts/dau-chien-luoc.py", "--tat-ca"], 900),
    ("bộ phá", [sys.executable, "scripts/bo-pha.py", "--ghi"], 600),
    # Đấu NHIỀU CHỢ. Nghi thức trước chỉ chạy `--tat-ca` trên một chợ, nên
    # `dau-nhieu-cho.json` đứng im 9 ngày và phát hiện "dương ở mấy chợ" nói về
    # một cấu hình đã đổi từ lâu. Ba coin cùng khung đang chạy: chuỗi tín hiệu
    # đã có cache nên lượt sau chỉ mất ~1 phút.
    ("đấu nhiều chợ", [sys.executable, "scripts/dau-chien-luoc.py", "--tat-ca",
                       "--cho", "BTCUSDT:4h,ETHUSDT:4h,SOLUSDT:4h"], 1200),
)

# Chạy SAU khi đã chưng cất — xem "THỨ TỰ KHÔNG ĐƯỢC ĐỔI" ở đầu file.
VIEC_CUOI = (("bàn giao", [sys.executable, "scripts/ban-giao.py", "--ghi"], 300),)


def trang_thai() -> dict:
    d = dict(_trang_thai)
    d["lanCuoi"] = _doc_coc().get("luc")
    d["conBaoLau"] = max(0, int(MOI_GIAY - (time.time() - (_doc_coc().get("mocGiay") or 0))))
    return d


def _doc_coc() -> dict:
    if not COC.exists():
        return {}
    try:
        return json.loads(COC.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return {}


def _ghi_coc(kq: dict) -> None:
    COC.write_text(json.dumps({
        "luc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "mocGiay": time.time(), "ketQua": kq,
    }, ensure_ascii=False, indent=1), encoding="utf-8")


def den_han() -> bool:
    return time.time() - (_doc_coc().get("mocGiay") or 0) >= MOI_GIAY


def _chay() -> None:
    kq: dict[str, Any] = {}
    try:
        # Sổ giao dịch của phép đo phải là sổ THẬT, nên truyền TCT_DATA_DIR
        # xuống tiến trình con. Thiếu nó thì script con tự tính DATA_DIR theo
        # thư mục của nó và có thể đọc một sổ khác — đúng loại lỗi đã từng trộn
        # 14 lệnh giả của selftest vào thống kê thật.
        moi = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1",
               "TCT_DATA_DIR": str(DATA_DIR)}
        def _mot(ten, lenh, han):
            _trang_thai.update(viec=ten)
            bus.emit("hoc", "nghi-thuc", f"đang chạy: {ten}…")
            t0 = time.time()
            try:
                r = subprocess.run(lenh, cwd=str(ROOT), env=moi, timeout=han,
                                   capture_output=True, text=True, encoding="utf-8",
                                   errors="replace")
                dong = [x for x in (r.stdout or "").strip().splitlines() if x.strip()]
                kq[ten] = {"ma": r.returncode, "giay": round(time.time() - t0, 1),
                           "cuoi": dong[-1] if dong else "(không có đầu ra)"}
                if r.returncode != 0:
                    # Không nuốt im: một phép đo hỏng mà bảng vẫn xanh là cách
                    # nhanh nhất để tin vào số cũ mà tưởng là số mới.
                    kq[ten]["loi"] = (r.stderr or "").strip()[-300:]
                    bus.log("hoc", "nghi-thuc-loi", f"{ten} thoát mã {r.returncode}")
                else:
                    bus.emit("hoc", "nghi-thuc-xong",
                             f"{ten} xong sau {kq[ten]['giay']}s · {kq[ten]['cuoi'][:120]}")
            except subprocess.TimeoutExpired:
                kq[ten] = {"ma": -1, "loi": f"quá {han}s", "giay": han}
                bus.log("hoc", "nghi-thuc-loi", f"{ten} quá giờ ({han}s)")

        for x in VIEC:
            _mot(*x)

        # ĐÀI QUAN SÁT chạy trong tiến trình này chứ không phải tiến trình con:
        # nó tự dựng luồng nền và tự giới hạn tần suất gọi sàn ngoài. Gọi bằng
        # subprocess là mở một bản thứ hai cùng nện API Hyperliquid/OKX, và cả
        # hai cùng ăn 429.
        #
        # `trader-ho-so.json` đã đứng im 12 ngày trước khi có dòng này — đúng
        # loại kho đo mà nghi thức sinh ra để không ai phải nhớ gõ lệnh.
        try:
            from . import phien_quan_sat
            t0 = time.time()
            r = phien_quan_sat.bat_dau()
            if not r.get("ok"):
                kq["đài quan sát"] = {"ma": 1, "cuoi": str(r.get("vi_sao"))}
            else:
                # CHỜ cho tới khi nó thật sự xong. Bản đầu ghi "đã khởi động ở
                # luồng nền" rồi coi là thành công — nhưng luồng nền chết cùng
                # tiến trình mỗi lần runtime dựng lại, nên `trader-ho-so.json`
                # đứng im 291 giờ trong khi nghi thức vẫn xanh suốt.
                #
                # Chờ ở đây an toàn: nghi thức đã chạy trong luồng riêng, và mọi
                # việc đo nặng khác đã xong trước dòng này.
                while time.time() - t0 < QUAN_SAT_HET_GIAY:
                    tt = phien_quan_sat.trang_thai().get("trangThai")
                    if tt in ("xong", "lỗi", "chưa chạy"):
                        break
                    time.sleep(5)
                tt = phien_quan_sat.trang_thai()
                xong = tt.get("trangThai")
                kq["đài quan sát"] = {
                    "ma": 0 if xong == "xong" else 1,
                    "giay": round(time.time() - t0, 1),
                    "cuoi": f"trạng thái cuối: {xong}",
                }
                if xong != "xong":
                    kq["đài quan sát"]["loi"] = str(tt.get("loi") or f"dừng ở «{xong}»")
            bus.emit("hoc", "nghi-thuc", "đài quan sát: " + str(kq["đài quan sát"]["cuoi"]))
        except Exception as e:  # noqa: BLE001
            kq["đài quan sát"] = {"ma": -1, "loi": f"{type(e).__name__}: {e}"}
            bus.log("hoc", "nghi-thuc-loi", f"đài quan sát: {type(e).__name__}: {e}")

        from . import chung_cat
        c = chung_cat.chung_cat()
        kq["chưng cất"] = {"soPhatHien": c["soPhatHien"], "soDaBo": c["soDaBo"]}
        bus.emit("hoc", "nghi-thuc-xong",
                 f"chưng cất lại: {c['soPhatHien']} phát hiện · bỏ {c['soDaBo']}")

        for x in VIEC_CUOI:
            _mot(*x)

        _ghi_coc(kq)
        _trang_thai.update(ketQua=kq, loi=None)
    except Exception as e:  # noqa: BLE001
        _trang_thai.update(loi=f"{type(e).__name__}: {e}")
        bus.log("hoc", "nghi-thuc-loi", f"{type(e).__name__}: {e}")
    finally:
        _trang_thai.update(dangChay=False, viec=None,
                           xong=_dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"))


def khoi_dong(ep: bool = False) -> dict:
    """Chạy nghi thức ở luồng nền. `ep=True` để bỏ qua hạn 6 tiếng."""
    with _khoa:
        if _trang_thai["dangChay"]:
            return {"ok": False, "viSao": "đang chạy rồi"}
        if not ep and not den_han():
            return {"ok": False, "viSao": f"chưa tới hạn, còn {trang_thai()['conBaoLau']}s"}
        _trang_thai.update(dangChay=True, batDau=_dt.datetime.now(
            _dt.timezone.utc).isoformat(timespec="seconds"), xong=None, loi=None)
    threading.Thread(target=_chay, daemon=True, name="nghi-thuc").start()
    return {"ok": True}
