"""Bộ giám sát — giữ runtime sống, ghi log xoay vòng, không hiện cửa sổ nào.

Task Scheduler gọi file này bằng `pythonw.exe` (không console), rồi nó tự sinh
`run.py` làm tiến trình con và trông chừng.

Vì sao cần một tầng riêng thay vì để Task Scheduler tự khởi động lại:

1. **Task Scheduler chỉ coi là hỏng khi mã thoát khác 0.** Uvicorn chết vì cổng
   bận vẫn có thể thoát 0, và khi đó không có gì khởi động lại cả — dịch vụ chết
   im lặng, đúng kiểu hỏng tệ nhất.

2. **Phải có nghỉ tăng dần và có điểm bỏ cuộc.** Cấu hình sai làm tiến trình
   chết trong một giây; khởi động lại ngay lập tức là một vòng quay tít, ăn CPU
   và nện API sàn hàng nghìn lượt một phút. Ở đây: chết nhanh thì giãn dần
   5→10→30→60→300 giây, và chết nhanh 10 lần liên tiếp thì DỪNG HẲN kèm một
   dòng nói rõ vì sao. Một dịch vụ dừng và giải thích thì sửa được; một dịch vụ
   quay tít thì chỉ làm máy nóng.

3. **Log phải xoay vòng liên tục.** Chuyển hướng stdout thẳng ra file thì sau
   vài tuần chạy nó thành file vài GB. Ở đây stdout của con được đọc từng dòng
   rồi ghi qua `RotatingFileHandler`, nên nó xoay ngay cả khi tiến trình con
   chạy liên tục hàng tháng.
"""
from __future__ import annotations

import json
import logging
import logging.handlers
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent      # tu-cam-thanh-runtime/

# HAI LÀN. `TCT_LAN` đặt tên làn; mọi file trạng thái của bộ giám sát mang hậu
# tố ấy, để hai làn không giẫm lên nhau.
#
# Làn demo hai chiều cần sống qua nhiều TUẦN — giả thuyết
# «keo-lui-short-tien-tuong» cần 30 lệnh SHORT, ước ~6 tuần trên 46 chợ. Chạy
# nó bằng một cửa sổ terminal là hẹn trước cái chết của phép đo: máy khởi động
# lại một lần là mất, và không ai biết nó mất lúc nào.
#
# Giữ NGUYÊN tên file cũ cho làn chính: `dung.ps1`, `trang-thai.ps1`,
# `cap-nhat.ps1` và `chuyen-nha.ps1` đều trỏ thẳng vào `dichvu/trang-thai.json`.
# `--lan demo` phải dựng được LÀN DEMO mà không cần ai đặt biến môi trường —
# lối tắt .lnk trong thư mục Startup không đặt được biến, và tự chạy lúc đăng
# nhập là thứ duy nhất giúp phép đo sống qua một lần khởi động lại máy.
#
# GÁN THẲNG, không `setdefault`. Cờ dòng lệnh phải THẮNG biến kế thừa: dùng
# `setdefault` ở đây là lặp lại đúng lỗi đã ba lần đưa dữ liệu giả vào sổ thật —
# một biến sót trong môi trường lặng lẽ đè lên thứ người gọi vừa yêu cầu.
if "--lan" in sys.argv:
    _l = sys.argv[sys.argv.index("--lan") + 1].strip()
    if _l == "demo":
        os.environ["TCT_LAN"] = "demo"
        os.environ["TCT_CONFIG"] = "config-hai-chieu.json"
        os.environ["TCT_DATA_DIR"] = str(GOC / "data-hai-chieu")
        os.environ["TCT_LAN_DEMO"] = "1"
        os.environ["BRAIN"] = "mock"
    elif _l != "chinh":
        raise SystemExit(f"--lan chỉ nhận 'chinh' hoặc 'demo', không phải {_l!r}")

LAN = (os.environ.get("TCT_LAN") or "chinh").strip() or "chinh"
_HAU = "" if LAN == "chinh" else f"-{LAN}"

# Nhật ký đi theo SỔ của làn, không theo gốc runtime: hai làn ghi chung một
# `runtime.log` thì hai dòng đời trộn vào nhau đúng lúc cần đọc nhất.
NHAT_KY = Path(os.environ.get("TCT_DATA_DIR") or (GOC / "data")) / "nhat-ky"
TRANG_THAI = GOC / "dichvu" / f"trang-thai{_HAU}.json"
CO_DUNG = GOC / "dichvu" / f"dung-lai{_HAU}"      # buồng lái xin dừng hẳn

CHET_NHANH_GIAY = 30          # sống ngắn hơn ngần này thì coi là chết nhanh
NGHI = [5, 10, 30, 60, 120, 300]
TOI_DA_CHET_NHANH = 10

# Nghỉ giữa hai lần thử khi nghi mất mạng. Dài hơn hẳn thang thường: mạng rớt
# thì đo lại sau mười phút là đủ, còn thử mỗi năm giây chỉ đốt pin.
NGHI_MANG = 600

# Dấu hiệu trong nhật ký cho thấy nguyên nhân là MẠNG chứ không phải cấu hình.
# Cố ý chỉ nhận diện những thứ rõ ràng — đoán mò rồi thử lại mãi một lỗi cấu
# hình thật thì đúng vào cái bẫy mà luật "dừng hẳn" sinh ra để chặn.
DAU_HIEU_MANG = ("getaddrinfo failed", "Temporary failure in name resolution",
                 "ConnectError", "ConnectTimeout", "ReadTimeout",
                 "Network is unreachable", "Connection aborted",
                 "[Errno 11001]", "[Errno -3]", "WinError 10051")


def _co_ve_loi_mang(tu_byte: int) -> bool:
    """Nhật ký ghi TỪ `tu_byte` TRỞ ĐI có nói đây là lỗi mạng không?

    Bộ giám sát không thấy được ngoại lệ bên trong tiến trình con, nó chỉ thấy
    mã thoát — còn lý do thật thì con đã ghi ra log trước khi chết. Nên phải đọc
    lại chính file log ấy.

    `tu_byte` là mấu chốt, và bản đầu tôi bỏ quên nó: nó đọc 20KB cuối file, tức
    là gồm cả lỗi của những lượt chạy TRƯỚC. Hậu quả đo được ngay — máy này có
    514 dòng `getaddrinfo failed` từ tuần trước, nên một tiến trình chết vì cấu
    hình sai vẫn bị chẩn đoán là "mất mạng" và thử lại mãi, đúng cái vòng quay
    tít mà luật dừng-hẳn sinh ra để chặn. `dichvu/kiem-giam-sat.py` bắt được
    chuyện này: nó xanh khi chạy riêng và đỏ khi chạy sau một bộ kiểm khác, vì
    log lúc đó còn dấu vết cũ.

    Chỉ đọc phần ghi thêm KỂ TỪ lúc con này khởi động thì chẩn đoán mới nói về
    đúng lượt chạy vừa chết.
    """
    try:
        f = NHAT_KY / "runtime.log"
        if not f.exists():
            return False
        cuoi = f.stat().st_size
        if cuoi <= tu_byte:      # log vừa xoay vòng, hoặc con chưa ghi được gì
            return False
        with f.open("r", encoding="utf-8", errors="replace") as fh:
            fh.seek(tu_byte)
            moi = fh.read(200_000)
    except OSError:
        return False
    return any(x in moi for x in DAU_HIEU_MANG)


def _co_log() -> int:
    """Kích thước nhật ký lúc này — mốc để biết con sắp chạy ghi thêm những gì."""
    try:
        return (NHAT_KY / "runtime.log").stat().st_size
    except OSError:
        return 0


def _log() -> logging.Logger:
    NHAT_KY.mkdir(parents=True, exist_ok=True)
    lg = logging.getLogger("tct")
    lg.setLevel(logging.INFO)
    h = logging.handlers.RotatingFileHandler(
        NHAT_KY / "runtime.log", maxBytes=5_000_000, backupCount=5, encoding="utf-8")
    h.setFormatter(logging.Formatter("%(asctime)s %(message)s", "%Y-%m-%d %H:%M:%S"))
    lg.addHandler(h)
    return lg


def _cong() -> int:
    """Cổng của LÀN NÀY. Đọc `TCT_CONFIG` như `trader/config.py` đọc.

    Bỏ qua nó thì bộ giám sát đo cổng 5182 của làn chính, thấy bận, và im lặng
    thoát — làn demo trông như "đã có bản đang chạy" trong khi chưa hề lên.
    """
    tay = (os.environ.get("TCT_CONFIG") or "").strip()
    f = Path(tay) if tay else (GOC / "config.json")
    if not f.is_absolute():
        f = GOC / f
    try:
        return json.loads(f.read_text(encoding="utf-8-sig"))["port"]
    except Exception:  # noqa: BLE001
        return 5182


def _dang_ban(cong: int) -> bool:
    with socket.socket() as s:
        s.settimeout(1.0)
        return s.connect_ex(("127.0.0.1", cong)) == 0


def _ghi_trang_thai(**kw) -> None:
    TRANG_THAI.parent.mkdir(parents=True, exist_ok=True)
    TRANG_THAI.write_text(json.dumps(kw, ensure_ascii=False, indent=1), encoding="utf-8")


def main() -> int:
    lg = _log()
    cong = _cong()

    # Một bản một lúc. Cổng đã bận nghĩa là đã có runtime chạy — dựng thêm bản
    # nữa thì hai vòng lặp cùng đặt lệnh trên một tài khoản.
    if _dang_ban(cong):
        lg.info(f"[giám sát] cổng {cong} đã bận — đã có bản đang chạy, thoát")
        return 0

    py = Path(sys.executable)
    # pythonw.exe không có console; tiến trình con cần python.exe để stdout chảy
    # được vào pipe. Cùng thư mục nên chỉ đổi tên file.
    py_con = py.with_name("python.exe") if py.name.lower() == "pythonw.exe" else py

    moi = os.environ.copy()
    # Không có hai dòng này thì tiếng Việt trong log thành ký tự vỡ trên Windows
    # — console mặc định là cp1252, và log là thứ người ta chỉ đọc lúc đang hỏng.
    moi["PYTHONUTF8"] = "1"
    moi["PYTHONIOENCODING"] = "utf-8"

    # Cờ dừng còn sót từ lượt trước phải xoá trước khi chạy, nếu không lượt này
    # vừa lên đã tự tắt — và trông y hệt như runtime chết ngay khi khởi động.
    CO_DUNG.unlink(missing_ok=True)

    lg.info("=" * 62)
    lg.info(f"[giám sát] bắt đầu · làn {LAN} · {GOC} · cổng {cong} · "
            f"pid {os.getpid()}")

    chet_nhanh = 0
    lan = 0
    while True:
        lan += 1
        t0 = time.time()
        moc_log = _co_log()      # mọi dòng sau mốc này là của riêng lượt chạy sắp tới
        try:
            con = subprocess.Popen(
                [str(py_con), "run.py"], cwd=str(GOC), env=moi,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="replace", bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
        except Exception as e:  # noqa: BLE001
            lg.info(f"[giám sát] không sinh được tiến trình con: {e}")
            return 1

        _ghi_trang_thai(giamSatPid=os.getpid(), conPid=con.pid, cong=cong,
                        batDau=time.time(), lanChay=lan, goc=str(GOC))
        lg.info(f"[giám sát] lượt {lan}: runtime pid {con.pid}")

        # Đọc từng dòng cho tới khi pipe đóng = tiến trình con thoát. Nhờ đi qua
        # đây, log xoay vòng liên tục thay vì chỉ xoay lúc khởi động lại.
        try:
            for dong in con.stdout:  # type: ignore[union-attr]
                d = dong.rstrip()
                if d:
                    lg.info(d)
        except Exception as e:  # noqa: BLE001
            lg.info(f"[giám sát] lỗi khi đọc log con: {e}")

        ma = con.wait()
        song = time.time() - t0
        lg.info(f"[giám sát] runtime thoát mã {ma} sau {song:.0f}s")

        # Buồng lái xin dừng hẳn: nghỉ, đừng dựng lại. Không kiểm cờ này thì nút
        # "dừng hẳn" thành vô dụng — tiến trình chết, bộ giám sát làm đúng việc
        # của nó và dựng lại sau vài giây, người dùng tưởng nút hỏng.
        if CO_DUNG.exists():
            CO_DUNG.unlink(missing_ok=True)
            lg.info("[giám sát] buồng lái xin dừng hẳn — nghỉ, không dựng lại")
            _ghi_trang_thai(giamSatPid=None, conPid=None, cong=cong,
                            dungTheoYeuCau=True, luc=time.time(), goc=str(GOC))
            return 0

        if song >= CHET_NHANH_GIAY:
            chet_nhanh = 0            # sống được một lúc = coi như lành
        else:
            chet_nhanh += 1

        if chet_nhanh >= TOI_DA_CHET_NHANH:
            # MẤT MẠNG KHÔNG PHẢI LỖI CẤU HÌNH.
            #
            # Luật "chết nhanh 10 lần thì dừng hẳn" đúng cho lỗi cấu hình: sửa
            # xong mới chạy lại được, và cứ dựng lại chỉ nện API sàn. Nhưng mất
            # mạng trông y hệt như vậy với bộ giám sát — và nó thì tự khỏi.
            #
            # Nhật ký ở đây có 514 dòng `getaddrinfo failed`: máy này rớt mạng
            # thường xuyên. Dừng hẳn vì một cú rớt mạng nghĩa là bot nằm chết
            # cho tới khi có người để ý — mà lần gần nhất, không ai để ý trong
            # năm ngày rưỡi.
            #
            # Nên tách hai loại: lỗi MẠNG thì nghỉ dài rồi thử lại mãi; lỗi
            # KHÁC thì vẫn dừng hẳn như cũ.
            if _co_ve_loi_mang(moc_log):
                lg.info(f"[giám sát] chết nhanh {chet_nhanh} lần, nhưng dấu hiệu là "
                        f"MẤT MẠNG chứ không phải lỗi cấu hình — nghỉ {NGHI_MANG}s "
                        f"rồi thử lại. Sẽ thử mãi: mạng thì tự khỏi, còn dừng hẳn "
                        f"thì phải có người bật lại.")
                _ghi_trang_thai(giamSatPid=os.getpid(), conPid=None, cong=cong,
                                choMang=True, lyDo="nghi mất mạng — vẫn đang thử lại",
                                luc=time.time(), goc=str(GOC))
                chet_nhanh = 0
                time.sleep(NGHI_MANG)
                continue

            lg.info(f"[giám sát] DỪNG HẲN — chết nhanh {chet_nhanh} lần liên tiếp. "
                    f"Đây gần như luôn là lỗi cấu hình chứ không phải trục trặc "
                    f"tạm thời: xem mấy dòng ngay trên đây, sửa, rồi chạy "
                    f"dichvu\\bat.ps1. Cứ khởi động lại tiếp chỉ nện API sàn "
                    f"và làm nóng máy.")
            _ghi_trang_thai(giamSatPid=os.getpid(), conPid=None, cong=cong,
                            dungHan=True, lyDo=f"chết nhanh {chet_nhanh} lần liên tiếp",
                            luc=time.time(), goc=str(GOC))
            return 1

        nghi = NGHI[min(chet_nhanh, len(NGHI) - 1)] if chet_nhanh else 3
        lg.info(f"[giám sát] khởi động lại sau {nghi}s"
                + (f" (chết nhanh {chet_nhanh}/{TOI_DA_CHET_NHANH})" if chet_nhanh else ""))
        time.sleep(nghi)


def _chay_va_ghi_loi() -> int:
    """Chạy `main()`, và NGOẠI LỆ NÀO CŨNG PHẢI ĐỂ LẠI MỘT DÒNG.

    Bộ giám sát chạy bằng `pythonw.exe` — không console, stderr không đi đâu cả.
    Một ngoại lệ không ai bắt ở đây làm tiến trình biến mất KHÔNG dấu vết: nhật
    ký ngừng giữa câu, tiến trình con vẫn chạy mồ côi, và không có gì để đọc.

    Xảy ra 30/08: cả hai bộ giám sát mất lúc 12:56, mọi đường thoát bình thường
    đều có ghi lý do nhưng nhật ký không có dòng nào. Không cách nào biết vì sao.
    Sau bản này thì biết — hoặc nếu vẫn không có dòng nào, ta biết chắc nó bị
    GIẾT từ bên ngoài chứ không phải tự chết.
    """
    try:
        return main()
    except BaseException as e:      # noqa: BLE001 — kể cả KeyboardInterrupt/SystemExit
        try:
            _log().exception(f"[giám sát] CHẾT VÌ NGOẠI LỆ: {type(e).__name__}: {e}")
            _ghi_trang_thai(giamSatPid=os.getpid(), conPid=None, cong=_cong(),
                            dungHan=True, lyDo=f"ngoại lệ {type(e).__name__}: {e}",
                            luc=time.time(), goc=str(GOC))
        except Exception:  # noqa: BLE001 — ghi log hỏng thì cũng đừng nuốt gốc
            pass
        raise


if __name__ == "__main__":
    sys.exit(_chay_va_ghi_loi())
