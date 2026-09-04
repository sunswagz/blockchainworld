"""Khám sức khoẻ: một lệnh, một trang, không chép logic của ai.

    python scripts/kham-suc-khoe.py

Tri thức về cỗ máy này nằm rải ở hơn mười công cụ. Ai muốn biết "nó có ổn
không" phải nhớ chạy những cái nào, theo thứ tự nào, và đọc con số nào
trong mỗi bảng. Trong thực tế điều đó nghĩa là: không ai kiểm.

Script này GỌI LẠI các công cụ ấy và gộp kết luận. Nó cố ý KHÔNG tự tính
bất cứ thứ gì — thêm một bản sao của một phép đo là thêm một chỗ để hai
bản lệch nhau, và cả repo này dành phần lớn công sức để gỡ đúng chuyện đó.

## Nó nói được gì

    bộ kiểm số học          scripts/selftest.py
    bộ kiểm giao diện       scripts/kiem-giao-dien.mjs, kiem-buong-lai.mjs
    sổ kết quả tái lập?     scripts/doi-chieu-ket-qua.py
    runtime đang sống?      /api/trang-thai

## Nó KHÔNG nói được gì

Không chạy các phép đo dài (`tu-nang-cap`, `chay-demo`, `thu-*`) — chúng
mất hàng phút và cần mạng Binance. Sức khoẻ khác với hiệu quả: script này
trả lời "cỗ máy có đang chạy đúng không", không trả lời "nó có lãi không".
Câu thứ hai nằm ở `chay-phat-lai.py`, và câu trả lời hiện tại của nó là
một khoảng tin CHỨA 0.
"""
from __future__ import annotations

import json
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

N = chr(10)
GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))

import kham  # noqa: F401,E402
from kham import tham_so  # noqa: E402

CO = tham_so.doc({
    "nhanh": tham_so.BAT,
}, ten='kham-suc-khoe.py')

from kham.config import CONFIG  # noqa: E402

PY = sys.executable
NHANH = CO.co("nhanh")


def chay(lenh: list[str], giay: float = 180.0) -> tuple[int, str]:
    """Chạy một công cụ, trả (mã thoát, đầu ra). Không bao giờ ném."""
    try:
        r = subprocess.run(lenh, cwd=str(GOC), capture_output=True,
                           timeout=giay, text=True, encoding="utf-8",
                           errors="replace")
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except subprocess.TimeoutExpired:
        return 124, f"quá {giay:.0f}s"
    except Exception as e:  # noqa: BLE001
        return 1, f"{type(e).__name__}: {e}"


def dong_cuoi(ra: str, chua: str) -> str:
    """Dòng CUỐI có chứa `chua`, đã cắt khoảng trắng."""
    for d in reversed(ra.splitlines()):
        if chua in d:
            return d.strip()
    return ""


def dong_bat_dau(ra: str, dau: str) -> str:
    """Dòng cuối BẮT ĐẦU bằng `dau` (sau khi cắt khoảng trắng).

    Khác `dong_cuoi`: dò "chứa" thì bắt nhầm câu văn xuôi. Đã cắn ngay
    lần chạy đầu — dòng bảng `khớp 1.935` bị câu cảnh báo *"vẫn báo khớp
    100% trong khi cả sổ sai"* cướp mất, và trang khám in ra một câu
    cảnh báo ở chỗ đáng lẽ là một con số.
    """
    for d in reversed(ra.splitlines()):
        t = d.strip()
        if t.startswith(dau):
            return t
    return ""


def hoi_runtime() -> dict | None:
    cong = CONFIG.get("port", 5186)
    try:
        with urllib.request.urlopen(
                f"http://127.0.0.1:{cong}/api/trang-thai", timeout=8) as f:
            return json.loads(f.read().decode("utf-8"))
    except (urllib.error.URLError, OSError, ValueError):
        return None


#: Cổng người canh gác giữ chỗ (`dichvu/canh-gac.py`).
CONG_CANH_GAC = 5187


def hoi_canh_gac() -> tuple[str, str]:
    """(trạng thái, câu giải thích) của người canh gác.

    Hai nguồn, và cần CẢ HAI:

      · CỔNG 5187 — người canh gác giữ chỗ ở đó suốt đời nó, nên cổng
        có người nghĩa là tiến trình còn sống;
      · NHỊP TIM — file `canh-gac-nhip.txt` ghi đè mỗi lượt hỏi, nên
        file cũ nghĩa là tiến trình còn đó mà vòng lặp đã đứng.

    Chỉ hỏi cổng thì không bắt được ca vòng lặp treo; chỉ đọc nhịp thì
    không phân biệt được "chưa bao giờ chạy" với "vừa mới chết".
    """
    # Dò bằng cách THỬ BIND, không phải bằng cách kết nối.
    #
    # `canh-gac.py` giữ cổng bằng `bind` + `listen(1)` và KHÔNG BAO GIỜ
    # `accept`. Nên mỗi lần khám kết nối vào là nhét thêm một kết nối
    # nằm mãi trong hàng đợi; vài lượt khám là hàng đầy, và từ đó lượt
    # khám nào cũng báo "cổng trống" về một người canh gác đang khoẻ.
    # Phép kiểm bắt được đúng chuyện này.
    #
    # Thử bind thì không đụng vào hàng đợi: bind hỏng nghĩa là có người
    # giữ, bind được nghĩa là không ai giữ — và ta trả lại ngay.
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("127.0.0.1", CONG_CANH_GAC))
        coCong = False
    except OSError:
        coCong = True
    finally:
        s.close()

    duong = GOC / "data" / "nhat-ky" / "canh-gac-nhip.txt"
    d = None
    if duong.exists():
        try:
            d = json.loads(duong.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            d = None

    if not coCong and d is None:
        return ("chet", f"KHÔNG CHẠY — cổng {CONG_CANH_GAC} trống và không có nhịp tim")
    if not coCong:
        tuoi = time.time() - float(d.get("luc") or 0)
        return ("chet", f"KHÔNG CHẠY — cổng {CONG_CANH_GAC} trống; nhịp cuối "
                        f"{_tuoi(tuoi)} trước")
    if d is None:
        return ("mo", f"cổng {CONG_CANH_GAC} CÓ người giữ, chưa có nhịp tim "
                      "(bản cũ chưa ghi nhịp?)")

    tuoi = time.time() - float(d.get("luc") or 0)
    nhip = float(d.get("nhipGiay") or 20.0)
    # Ba nhịp: một lượt lỡ vì máy bận thì đừng kêu, nhưng ba lượt liền
    # thì vòng lặp đã đứng chứ không phải chậm.
    if tuoi > max(90.0, nhip * 3):
        return ("treo", f"cổng {CONG_CANH_GAC} CÓ người, nhưng nhịp cuối {_tuoi(tuoi)} "
                        f"trước (nhịp {nhip:.0f}s) — vòng lặp ĐỨNG?")
    return ("song", f"ĐANG CANH · PID {d.get('pid')} · nhịp cuối "
                    f"{_tuoi(tuoi)} trước · đã dựng lại "
                    f"{d.get('soLanDung', 0)} lần")


def _tuoi(giay: float) -> str:
    if giay < 90:
        return f"{giay:.0f} giây"
    if giay < 5400:
        return f"{giay / 60:.0f} phút"
    if giay < 172800:
        return f"{giay / 3600:.1f} giờ"
    return f"{giay / 86400:.1f} ngày"


def main() -> int:
    t0 = time.time()
    print()
    print("=" * 76)
    print("  KHÁM SỨC KHOẺ — KHÂM THIÊN GIÁM")
    print("=" * 76)

    hong: list[str] = []
    nhac: list[str] = []

    # ── 1. bộ kiểm số học ────────────────────────────────────────────
    ma, ra = chay([PY, "scripts/selftest.py"], 300.0)
    d = dong_cuoi(ra, "đạt")
    print(f"  bộ kiểm số học      {'ĐẠT' if ma == 0 else 'HỎNG'}   {d}")
    if ma != 0:
        hong.append("selftest")
        for x in ra.splitlines():
            if x.strip().startswith("✗"):
                print(f"      {x.strip()[:96]}")

    # ── 2. bộ kiểm giao diện ─────────────────────────────────────────
    for ten, chua in (("kiem-giao-dien.mjs", "phép kiểm giao diện"),
                      ("kiem-buong-lai.mjs", "ô vẽ được")):
        ma2, ra2 = chay(["node", f"scripts/{ten}"], 120.0)
        print(f"  {ten:<20}{'ĐẠT' if ma2 == 0 else 'HỎNG'}   "
              f"{dong_cuoi(ra2, chua)}")
        if ma2 != 0:
            hong.append(ten)

    # ── 3. sổ kết quả có tái lập được không ──────────────────────────
    if NHANH:
        print("  sổ kết quả          BỎ QUA (--nhanh)")
    else:
        # CẢ BỐN chợ, không mỗi market mặc định. Bản trước chạy
        # `doi-chieu-ket-qua.py` không kèm `--ma`, nên nó chỉ soi BTC_5M
        # và ba sổ kia chưa từng được đối chiếu lần nào — chúng góp
        # 1.956 trên 4.523 dòng.
        #
        # Danh sách lấy từ `kham.ket_qua`, không tự dựng ở đây: hai lý
        # do loại một market (không `tienTo` = họ CHẠM MỐC; `theo:
        # false`) là một cái luật, và luật thì phải nằm một chỗ.
        from kham.ket_qua import thi_truong_doi_chieu_duoc
        tongKhop = tongLech = 0
        khongDo: list[str] = []
        for _tt in thi_truong_doi_chieu_duoc():
            _ma = str(_tt.get("ma"))
            ma3, ra3 = chay([PY, "scripts/doi-chieu-ket-qua.py",
                             f"--ma={_ma}", "--ngay=3"], 240.0)
            # Đọc DÒNG MÁY, không dò văn xuôi — xem ghi chú trong
            # `doi-chieu-ket-qua.py`.
            con = {}
            for _x in (dong_bat_dau(ra3, "KETLUAN") or "").split()[1:]:
                if "=" in _x:
                    _k, _v = _x.split("=", 1)
                    con[_k] = _v
            try:
                tongKhop += int(con.get("khop", 0))
                tongLech += int(con.get("lech", 0))
            except ValueError:
                pass
            if ma3 not in (0, 2):
                khongDo.append(_ma)
        if tongLech:
            print(f"  sổ kết quả          HỎNG   {tongLech:,} LỆCH trên "
                  f"{tongKhop + tongLech:,}")
            hong.append(f"sổ kết quả có {tongLech:,} dòng SAI")
        elif tongKhop:
            print(f"  sổ kết quả          ĐẠT    {tongKhop:,} dòng tái lập "
                  f"đúng · 0 lệch")
        if khongDo:
            print("  sổ kết quả          không đối chiếu được: "
                  + ", ".join(khongDo))
            nhac.append("chưa đối chiếu được " + ", ".join(khongDo))

    # ── 4. runtime ───────────────────────────────────────────────────
    print()
    tt = hoi_runtime()
    if tt is None:
        print("  runtime             KHÔNG CHẠY (cổng "
              f"{CONFIG.get('port', 5186)} không trả lời)")
        nhac.append("runtime không chạy")
    else:
        r = tt.get("risk") or {}
        b = tt.get("bang") or {}
        nga = tt.get("lanNga") or {}
        kq = tt.get("soKetQua") or {}
        print(f"  runtime             ĐANG CHẠY · vòng {tt.get('vong')} · "
              f"chế độ {tt.get('che')}"
              + ("  ⚠ ĐANG TẠM DỪNG" if tt.get("tamDung") else ""))
        print(f"    vốn {r.get('von', 0):,.2f} · đỉnh {r.get('dinhVon', 0):,.2f}"
              f" · lỗ ngày {r.get('loNgayUsd', 0):,.2f}"
              f"/{r.get('tranLoNgayUsd', 0):,.2f}"
              + ("  ⚠ CẦU DAO NGẮT" if r.get("ngatKhanCap") else ""))
        print(f"    băng {b.get('soKhung', 0):,} khung · lỗi ghi "
              f"{b.get('soLoiGhi', 0)} · làn ngã {len(nga)}")
        print(f"    sổ kết quả {kq.get('soSlug', 0):,} khung — "
              f"{kq.get('soTheoSan', 0)} do SÀN xác nhận, "
              f"{kq.get('soTuTinh', 0):,} tự tính")
        if nga:
            hong.append(f"{len(nga)} làn ngã: {', '.join(list(nga)[:3])}")

    # ── 4b. người canh gác ───────────────────────────────────────────
    #
    # Nó là thứ duy nhất dựng runtime dậy khi runtime chết. Bản trước
    # chỉ ghi nhật ký khi CÓ SỰ CỐ, nên một người canh gác khoẻ và một
    # người canh gác đã chết trông giống hệt nhau — và ngày 03/09/2026
    # nó chết trước, runtime chết theo chín tiếng sau, rồi cả hai nằm
    # im hai ngày.
    tt2, ly = hoi_canh_gac()
    print(f"  người canh gác      {ly}")
    if tt2 == "chet":
        hong.append("người canh gác KHÔNG chạy — runtime không ai dựng lại")
    elif tt2 in ("treo", "mo"):
        nhac.append(f"người canh gác: {ly}")
        if b.get("soLoiGhi"):
            hong.append(f"{b['soLoiGhi']} lỗi ghi băng")
        # Ngân sách lỗ ngày: cả phần ĐÃ MẤT lẫn phần ĐANG GÁNH.
        # Trang này từng chỉ kêu khi cầu dao đã ngắt, tức là chỉ kêu khi
        # đã muộn. `lỗ ngày 49,95/50,00` từng hiện ra dưới dòng chữ
        # "Không có gì hỏng".
        tran = float(r.get("tranLoNgayUsd") or 0.0)
        con = r.get("conNganSachNgayUsd")
        ganh = float(r.get("loXauNhatGopUsd") or 0.0)
        if tran > 0:
            print(f"    ngân sách ngày còn "
                  f"{(con if con is not None else 0.0):,.2f}/{tran:,.2f}"
                  f" · đang gánh (chưa kết toán) {ganh:,.2f}")
            if con is not None and con <= 0:
                nhac.append("ngân sách lỗ ngày ĐÃ CẠN — chỉ còn nhận lệnh "
                            "phòng hộ")
            elif con is not None and con < tran * 0.2:
                nhac.append(f"ngân sách lỗ ngày chỉ còn {con:,.2f}/"
                            f"{tran:,.2f} — dưới một phần năm")
        if r.get("ngatKhanCap"):
            nhac.append("cầu dao đang NGẮT — không lệnh nào đi qua")
        if tt.get("tamDung"):
            nhac.append("bot đang TẠM DỪNG theo lệnh người")
        mep = tt.get("nutOMep") or []
        if mep:
            nhac.append(f"{len(mep)} nút nằm ở MÉP dải vặn: "
                        + ", ".join(x["duong"] for x in mep[:3]))
        if kq.get("soTheoSan") == 0 and kq.get("soSlug"):
            nhac.append("chưa dòng kết quả nào được SÀN xác nhận — "
                        "mọi điểm chấm đứng trên sự thật tự tính")
        cua = (tt.get("lenh") or {}).get("cuaDangDong") or []
        print(f"    cửa lệnh thật: {len(cua)} cửa đang ĐÓNG"
              + ("  ⚠⚠ KHÔNG CÒN CỬA NÀO ĐÓNG" if not cua else ""))
        if not cua:
            nhac.append("MỌI CỬA LỆNH THẬT ĐANG MỞ")

    # ── kết ──────────────────────────────────────────────────────────
    print()
    print("-" * 76)
    if hong:
        print("  CÓ HỎNG:")
        for x in hong:
            print(f"    ✗ {x}")
    else:
        print("  Không có gì hỏng.")
    if nhac:
        print("  Đáng để mắt:")
        for x in nhac:
            print(f"    · {x}")
    print()
    print(f"  ({time.time() - t0:.0f} giây)")
    print("  Sức khoẻ KHÁC hiệu quả: trang này nói cỗ máy có chạy đúng")
    print("  không, KHÔNG nói nó có lãi không. Câu ấy ở `chay-phat-lai.py`,")
    print("  và câu trả lời hiện tại là một khoảng tin CHỨA 0.")
    print()
    return 1 if hong else 0


if __name__ == "__main__":
    raise SystemExit(main())
