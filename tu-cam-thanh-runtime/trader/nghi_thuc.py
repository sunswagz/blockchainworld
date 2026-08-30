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
from .config import CONFIG, DATA_DIR, ROOT

# 6 tiếng: nguồn của hai phép đo này là nến lịch sử và sổ chiến lược — thứ đổi
# theo ngày chứ không theo giờ. Chạy dày hơn chỉ tốn nhân mà ra cùng một số.
# Chu kỳ nghi thức. Nâng 6 → 8 tiếng khi thêm việc «đo hướng»: tổng hạn xấu
# nhất chạm 5,00h, tức 83% của chu kỳ 6 tiếng. Không vỡ, nhưng chật — và chật
# thì một lượt chậm bất thường sẽ ăn sang lượt sau, `dangChay` bỏ nhịp, rồi chu
# kỳ lặng lẽ thành gấp đôi mà không dòng nhật ký nào nói ra.
#
# 8 tiếng vẫn dày hơn mức cần rất nhiều: ngưỡng "kho đo đã cũ" của bàn giao là
# 48 giờ, nên chạy mỗi 8 tiếng là sáu lần dày hơn ngưỡng.
MOI_GIAY = 8 * 3600

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

# Danh sách chợ khung 4h — MỘT chỗ, dùng cho cả mẫu giá lẫn đấu nhiều chợ.
# Hai bảng riêng thì thêm coin là phải nhớ sửa hai nơi, và quên một nơi thì
# hai phép đo nói về hai tập chợ khác nhau mà không gì lộ ra.
# Nến tải bằng: python scripts/tai-lich-su.py --coin <ds> --khung 4h,1d
CHO_4H = (
    "BTCUSDT:4h,ETHUSDT:4h,SOLUSDT:4h,BNBUSDT:4h,XRPUSDT:4h,ADAUSDT:4h,"
    "DOGEUSDT:4h,AVAXUSDT:4h,LINKUSDT:4h,DOTUSDT:4h,ATOMUSDT:4h,"
    "NEARUSDT:4h,FILUSDT:4h,UNIUSDT:4h,LTCUSDT:4h"
)


# Cùng 15 coin, khung 1d. Đo được: cùng champion không sửa dòng nào, khung 4h
# cho −0,047R gộp 193 lệnh (dương 2/8 chợ) còn 1d cho +0,117R gộp 230 lệnh
# (dương 11/15). Khung không chỉ đổi độ lớn — nó đổi cả kết luận về từng bộ
# luật: MOCK_KEO_LUI_V1 bị bác bỏ trên 4h (−0,248R) mà trên 1d là +0,164R.
#
# Nên hai khung phải đo SONG SONG và đều đặn. Đo một khung rồi suy ra khung kia
# là chỗ đã sai một lần hôm nay.
CHO_1D = CHO_4H.replace(":4h", ":1d")
# Phần tử thứ tư là KHO việc đó sinh ra. Không phải để chạy — để CANH.
#
# `lessons-soat-lai.jsonl` đứng im 9 ngày: việc soát lại chưa từng nằm trong
# nghi thức, nên phải gõ tay, nên không ai gõ. Và bàn giao cũng không kêu, vì
# danh sách kho-phải-canh của nó là một danh sách RIÊNG, viết tay, không dính
# gì tới bảng này. Hai danh sách rời nhau thì thêm việc mà quên khai bên kia là
# chuyện đương nhiên xảy ra — đã xảy ra.
#
# Khai ở ĐÂY, một chỗ. `selftest` bắt bàn giao phải canh đủ mọi kho trong bảng.
VIEC = (
    # MẪU GIÁ trên 15 chợ, không phải một. Đo trên riêng BTC thì 5 trong 12 mẫu
    # nằm dưới ngưỡng 15 lần xuất hiện và vĩnh viễn "chưa đủ dữ liệu" — đo thêm
    # 10 năm BTC cũng chỉ nhích chút, vì mẫu hiếm thì hiếm ở mọi độ dài. Trải
    # qua 15 chợ: 14/14 mẫu đủ cỡ mẫu, HAI_ĐỈNH từ 12 lần lên 701.
    #
    # Và nó lật một kết luận: NẾN_TRÙM_GIẢM là mẫu dương duy nhất hồi đo trên
    # một chợ, qua 15 chợ thành −0,107R trên 697 lần.
    #
    # Đo được ~9 phút cho 45.000 nến nên hạn nâng lên 1800s: 900s là vừa đủ
    # trong điều kiện tốt, và một lần quá giờ là mất cả kho đo của lượt đó.
    ("mẫu giá", [sys.executable, "scripts/do-mau-gia.py", "--ghi",
                 "--cho", CHO_4H], 1800,
     "mau-gia.json"),
    ("hình học khung", [sys.executable, "scripts/do-khung.py", "--ghi"], 900,
     "do-khung.json"),
    ("đấu chiến lược", [sys.executable, "scripts/dau-chien-luoc.py", "--tat-ca"], 900,
     "chien-luoc.json"),
    ("bộ phá", [sys.executable, "scripts/bo-pha.py", "--ghi"], 600, "bo-pha.json"),
    # SOÁT LẠI BÀI HỌC. Đứng im 9 ngày vì nó chưa từng nằm trong nghi thức —
    # phải gõ tay, nên không ai gõ. Bài học được đúc NGAY LÚC lệnh đóng, khi sổ
    # còn quá ít để trả lời "lệnh này cược lớn hơn mức thường bao nhiêu"; soát
    # lại là chạy hậu kiểm lần nữa với cả sổ trong tay. Bỏ nó ra khỏi vòng thì
    # `recall()` mãi rót vào prompt những câu đúc lúc chưa biết gì.
    #
    # Rẻ và an toàn để chạy mỗi 6 tiếng: dùng `mock_postmortem`, luật thuần,
    # không gọi model nên không tiêu lượt nào của trần `brain.cli`. Và nó ghi
    # sang file PHỦ chứ không đè `lessons.jsonl` — bản ghi bộ não đã nghĩ gì
    # lúc đó là bằng chứng, không được xoá.
    ("soát lại bài học", [sys.executable, "scripts/soat-lai-bai-hoc.py", "--ghi"], 300,
     "lessons-soat-lai.jsonl"),
    # ĐO HƯỚNG. Phải chạy đều, không phải một lần: nó trả lời "bot chạy thật có
    # đánh được thứ phép đo đang đo không", và câu trả lời đổi mỗi khi chiến
    # lược hoặc sàn đổi. Đo một lần rồi tin mãi là đúng cách đã sai bốn lần ở đây.
    ("đo hướng", [sys.executable, "scripts/do-huong.py", "--ghi",
                  "--cho", CHO_1D], 2400,
     "do-huong.json"),
    # LÒ LUYỆN. Rẻ khi chuỗi đã có cache — đo được 16 chợ × 4 lát × 21 biến thể
    # trong 138 giây. Đắt đúng một lần sau mỗi lần sửa mã sinh chuỗi, vì lúc đó
    # vân tay đổi và mọi chuỗi phải dựng lại.
    #
    # Đặt SAU «đo hướng»: hai việc dùng chung cache chuỗi, nên chạy sau là chạy
    # trên cache nóng.
    # `--chi-long`: lò dò trong không gian bot CHẠY ĐƯỢC.
    #
    # Lò sinh ra CHALLENGER, và challenger đi qua cửa duyệt rồi lên champion rồi
    # được bot chạy thật. Mà bot chạy sàn spot, nơi `risk.py` chặn SHORT. Dò
    # trong không gian hai chiều là tối ưu một chiến lược cho một cỗ máy khác.
    #
    # Không phải chuyện nhỏ: trên 33 chợ 1d chưa từng dùng, MOCK_KEO_LUI_V1 cho
    # SHORT +0,303R/226 lệnh và LONG −0,306R/44 lệnh. Một biến thể thắng ở bảng
    # gộp có thể thắng HOÀN TOÀN nhờ nửa short.
    #
    # Nửa hai chiều vẫn được đo, chỉ là ở chỗ khác: `do-huong.py` chạy ngay
    # trước việc này, và bảng đấu nhiều chợ nay có cột `chiLong` cạnh cột gộp.
    ("lò luyện", [sys.executable, "scripts/lo-luyen.py", "--ghi", "--chi-long",
                  "--cho", CHO_1D, "--bien", "20", "--lat", "4"], 1800,
     "lo-luyen.json"),
    # Đấu NHIỀU CHỢ. Nghi thức trước chỉ chạy `--tat-ca` trên một chợ, nên
    # `dau-nhieu-cho.json` đứng im 9 ngày và phát hiện "dương ở mấy chợ" nói về
    # một cấu hình đã đổi từ lâu. Ba coin cùng khung đang chạy: chuỗi tín hiệu
    # đã có cache nên lượt sau chỉ mất ~1 phút.
    ("đấu nhiều chợ", [sys.executable, "scripts/dau-chien-luoc.py", "--tat-ca",
    # 3600 → 5400 → 9000s. Đo được ở lượt thật: 2728s, tức 76% hạn 3600 — và đó
    # là lượt bị GIẾT giữa chừng, chưa phải lượt chạy hết. Chuỗi 4h vừa dài gấp
    # ba (3000 → 9000 nến, để phủ đúng quãng của 1d), nên biên cũ không còn.
    #
    # 9000s là hạn cho lượt CACHE LẠNH: đo được 8 chợ × 9000 nến mất 75 phút,
    # tức 15 chợ ≈ 140 phút. Cache lạnh nay chỉ xảy ra sau khi sửa mã sinh chuỗi
    # — từ bản "bồi thêm chuỗi", một lượt bình thường chỉ tính vài chục điểm mới
    # và mất vài phút. Nếu sáu tháng nữa không lượt nào chạm 2000s thì hạ lại;
    # để hạn rộng gấp bốn lần thực tế lâu dài là mời một việc treo đứng im.
    #
    # Quá giờ ở đây không chỉ mất một phép đo: `dau-nhieu-cho.json` giữ nguyên
    # bản cũ, và lò chưng cất đọc nó như số liệu hiện hành.
                       "--cho", CHO_4H], 9000,
     "dau-nhieu-cho.json"),
    # Khung 1d chạy SAU và ghi đè `dau-nhieu-cho.json`, nên kho đó luôn giữ kết
    # quả 1d. Cố ý: đó là khung có bằng chứng dương duy nhất, và lò chưng cất
    # chỉ đọc một file. Bảng 4h vẫn in ra nhật ký nghi thức để so.
    #
    # 1d rẻ hơn hẳn (1500 nến so với 3000) nên hạn 1800s là đủ rộng.
    ("đấu nhiều chợ 1d", [sys.executable, "scripts/dau-chien-luoc.py", "--tat-ca",
                          "--cho", CHO_1D], 1800,
     "dau-nhieu-cho.json"),
)

# Chạy SAU khi đã chưng cất — xem "THỨ TỰ KHÔNG ĐƯỢC ĐỔI" ở đầu file.
VIEC_CUOI = (("bàn giao", [sys.executable, "scripts/ban-giao.py", "--ghi"], 300,
              "BAN-GIAO.md"),)


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


KHOA_FILE = DATA_DIR / "nghi-thuc-khoa.json"

# Nghi thức chạy tối đa ngần này thì coi khoá là RÁC dù tiến trình còn sống.
# Tổng hạn giờ của mọi việc cộng lại ~5,5 tiếng; 8 tiếng là biên an toàn.
KHOA_QUA_HAN_GIAY = 8 * 3600


def _con_song(pid: int | None) -> bool:
    """Tiến trình ấy còn sống không? KHÔNG được dùng `os.kill(pid, 0)`.

    Trên Windows `os.kill` gọi thẳng `TerminateProcess`, kể cả với tín hiệu 0 —
    tức phép "hỏi xem còn sống không" sẽ GIẾT chính tiến trình đang hỏi thăm.
    Đây là cái bẫy kinh điển của mã viết cho POSIX rồi chạy trên Windows.
    """
    if not pid:
        return False
    if sys.platform == "win32":
        import ctypes

        SYNCHRONIZE = 0x00100000
        h = ctypes.windll.kernel32.OpenProcess(SYNCHRONIZE, False, int(pid))
        if not h:
            return False
        # 0 = WAIT_OBJECT_0, tức tiến trình đã kết thúc (handle đã báo hiệu).
        con = ctypes.windll.kernel32.WaitForSingleObject(h, 0) != 0
        ctypes.windll.kernel32.CloseHandle(h)
        return con
    try:
        os.kill(int(pid), 0)
        return True
    except (OSError, ValueError):
        return False


def _doc_khoa() -> dict:
    try:
        return json.loads(KHOA_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _ai_giu_khoa() -> dict | None:
    """Trả bản khoá nếu MỘT nghi thức khác đang thật sự chạy, None nếu không.

    VÌ SAO PHẢI LÀ KHOÁ LIÊN TIẾN TRÌNH

    Cọc 6 tiếng chỉ được ghi khi nghi thức CHẠY XONG, còn khoá chống trùng thì
    nằm trong `_trang_thai` của một tiến trình. Runtime khởi động lại giữa chừng
    — 31 lượt trong một ngày, đo được — là tiến trình mới thấy cọc vẫn cũ và mở
    một nghi thức nữa, trong khi việc con của lượt trước còn sống mồ côi.

    Bắt được lúc 07:05 ngày 30/08: HAI `dau-chien-luoc.py --tat-ca` chạy song
    song, cách nhau 4 phút, cùng ghi vào kho chính thức. Và nó tự nuôi nó: càng
    nhiều việc chạy chồng thì máy càng chậm, nghi thức càng lâu, càng dễ dính
    thêm một lượt khởi động lại nữa.

    Đếm cả TIẾN TRÌNH CON: khi runtime bị giết, việc con thành mồ côi và vẫn
    ghi vào kho. Chủ khoá chết mà con còn sống thì vẫn là "đang chạy".
    """
    k = _doc_khoa()
    if not k:
        return None
    if time.time() - (k.get("mocGiay") or 0) > KHOA_QUA_HAN_GIAY:
        return None
    if _con_song(k.get("pid")) or _con_song(k.get("conPid")):
        return k
    return None


def _giu_khoa(**them) -> None:
    """Ghi/cập nhật khoá. Gọi lúc bắt đầu và mỗi lần đổi việc con."""
    k = {**_doc_khoa(), **them}
    k.setdefault("pid", os.getpid())
    k.setdefault("mocGiay", time.time())
    k["luc"] = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")
    try:
        KHOA_FILE.parent.mkdir(parents=True, exist_ok=True)
        tam = KHOA_FILE.with_suffix(f".{os.getpid()}.tmp")
        tam.write_text(json.dumps(k, ensure_ascii=False, indent=1), encoding="utf-8")
        os.replace(tam, KHOA_FILE)
    except OSError:
        pass          # không ghi được khoá thì vẫn chạy, chỉ mất lớp chống trùng


def _tha_khoa() -> None:
    try:
        KHOA_FILE.unlink()
    except OSError:
        pass


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
        def _mot(ten, lenh, han, _kho=None):
            _trang_thai.update(viec=ten)
            bus.emit("hoc", "nghi-thuc", f"đang chạy: {ten}…")
            t0 = time.time()
            try:
                # Popen chứ không `subprocess.run`: cần biết PID của việc con để
                # ghi vào khoá. Runtime bị giết giữa chừng thì việc con thành mồ
                # côi và vẫn ghi vào kho chính thức — lượt nghi thức sau phải
                # thấy nó còn sống mà đứng lại, chứ không mở thêm một bản nữa.
                with subprocess.Popen(
                        lenh, cwd=str(ROOT), env=moi, stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE, text=True, encoding="utf-8",
                        errors="replace") as pr:
                    _giu_khoa(viec=ten, conPid=pr.pid)
                    try:
                        _out, _err = pr.communicate(timeout=han)
                    except subprocess.TimeoutExpired:
                        pr.kill()
                        pr.communicate()
                        raise
                r = subprocess.CompletedProcess(lenh, pr.returncode, _out, _err)
                _giu_khoa(conPid=None)
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
        _tha_khoa()
        _trang_thai.update(dangChay=False, viec=None,
                           xong=_dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"))


def khoi_dong(ep: bool = False) -> dict:
    """Chạy nghi thức ở luồng nền. `ep=True` để bỏ qua hạn 6 tiếng."""
    # LÀN DEMO không chạy nghi thức. Khoá liên tiến trình nằm trong DATA_DIR, mà
    # mỗi làn có DATA_DIR riêng — nên hai làn KHÔNG thấy khoá của nhau và cùng
    # mở nghi thức. Chúng lại dùng chung `data/lich-su` và `data/chuoi`, tức hai
    # bộ việc nặng giẫm lên đúng một kho chuỗi.
    #
    # Xảy ra 07:32 ngày 30/08: làn demo vừa bật là bốn việc nghi thức chạy song
    # song với việc của làn chính. Làn demo tồn tại để GIAO DỊCH tiến tướng, còn
    # đo đạc là việc của làn chính — chạy hai lần cùng một phép đo không cho
    # thêm thông tin nào.
    if CONFIG.get("lanDemo"):
        return {"ok": False, "viSao": "làn demo không chạy nghi thức"}
    with _khoa:
        if _trang_thai["dangChay"]:
            return {"ok": False, "viSao": "đang chạy rồi"}
        # Khoá LIÊN TIẾN TRÌNH. `_trang_thai` chỉ biết tiến trình này; một
        # runtime vừa khởi động lại thì `dangChay` luôn False, còn nghi thức của
        # lượt trước có thể vẫn đang chạy dở với việc con mồ côi.
        #
        # Kiểm cả khi `ep=True`: ép là "bỏ qua hạn 6 tiếng", không phải "chạy
        # thêm một bản song song".
        ai = _ai_giu_khoa()
        if ai:
            return {"ok": False,
                    "viSao": (f"một nghi thức khác đang chạy (pid {ai.get('pid')}"
                              f"{', việc ' + ai['viec'] if ai.get('viec') else ''}"
                              f", từ {ai.get('luc')})")}
        if not ep and not den_han():
            return {"ok": False, "viSao": f"chưa tới hạn, còn {trang_thai()['conBaoLau']}s"}
        _giu_khoa(pid=os.getpid(), mocGiay=time.time(), viec=None, conPid=None)
        _trang_thai.update(dangChay=True, batDau=_dt.datetime.now(
            _dt.timezone.utc).isoformat(timespec="seconds"), xong=None, loi=None)
    threading.Thread(target=_chay, daemon=True, name="nghi-thuc").start()
    return {"ok": True}
