"""BÀN GIAO — bản tóm tắt để lượt làm việc SAU biết ngay phải làm gì.

    python scripts/ban-giao.py            in ra màn hình
    python scripts/ban-giao.py --ghi      ghi data/BAN-GIAO.md

VÌ SAO CÓ FILE NÀY

Bộ máy này có hai loại trí tuệ, và chúng không thay thế nhau:

    trí tuệ LÚC QUYẾT ĐỊNH   bot gọi model mỗi vòng — cần khoá, tốn tiền theo lượt
    trí tuệ LÚC THIẾT KẾ     người/agent đọc số đo rồi sửa LUẬT, kỹ năng, mã nguồn

Loại thứ hai không cần khoá nào. Cầu dao chế độ, lò chưng cất, thước kích thước,
mười ba kỹ năng — tất cả ra đời từ loại thứ hai. Nhưng nó có một điểm yếu chết
người: **nó phụ thuộc vào việc người làm có nhớ hay không.**

File này gỡ chỗ phụ thuộc đó. Nó so trạng thái hôm nay với lần bàn giao trước và
chỉ nói những gì ĐÃ ĐỔI — cái gì mới, cái gì đổi dấu, cái gì vừa vượt ngưỡng để
kết luận được, cái gì vẫn đang kẹt. Đọc nó là biết ngay chỗ cần đụng vào, không
phải dò lại từ đầu.

MỘT LUẬT: KHÔNG KHEN

Bản bàn giao chỉ liệt kê chỗ ĐÁNG SỬA và chỗ VỪA ĐỦ DỮ LIỆU ĐỂ NÓI. Thêm phần
"những gì đang tốt" vào đây là tạo ra một tài liệu dễ chịu để đọc và vô dụng để
dùng — và rồi sẽ không ai đọc nó nữa.
"""
from __future__ import annotations

import datetime as _dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from trader import chung_cat, journal, store  # noqa: E402
from trader.brain import BO_LUAT, load_skills  # noqa: E402
from trader.config import DATA_DIR, ROOT  # noqa: E402

GHI = "--ghi" in sys.argv
LICH_SU = DATA_DIR / "ban-giao-lich-su.jsonl"

# So với ảnh chụp cũ ÍT NHẤT ngần này giờ. Không có ngưỡng ấy thì mỗi lần nghi
# thức tự chạy lại ghi đè mốc, và bản bàn giao kế tiếp luôn báo "không có gì
# đổi" — kể cả khi vừa có 21 lệnh mới và năm ngày chết.
#
# Đo được đúng chuyện đó: nghi thức chạy lúc 13:59, tôi mở bàn giao lúc 14:01,
# và nó nói "không có gì đổi" trong khi số lệnh thật vừa nhảy 17 → 38. Không sai
# một con số nào, và vô dụng hoàn toàn.
CACH_TOI_THIEU_GIO = 6.0


def _anh_chup() -> dict:
    """Trạng thái rút gọn, đủ để so hai lần bàn giao với nhau."""
    ds = store.read_all(store.PHAT_HIEN)
    perf = journal.performance()["overall"]
    try:
        cl = json.loads((DATA_DIR / "chien-luoc.json").read_text(encoding="utf-8"))
    except (ValueError, OSError, FileNotFoundError):
        cl = {}
    _, so_ky_nang = load_skills()
    return {
        "luc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "phatHien": {p["ma"]: {"mau": p["mau"], "doTin": p["doTin"],
                               "so": p.get("so") or {}} for p in ds},
        "soKyNang": so_ky_nang,
        "soBoLuat": len(BO_LUAT),
        "boLuat": sorted(BO_LUAT),
        "soLenhThat": perf.get("count") or 0,
        "kyVongUsd": perf.get("expectancyUsd"),
        "riskCv": perf.get("riskCv"),
        "champion": (cl.get("champion") or {}).get("ma"),
        "championKyVong": ((cl.get("champion") or {}).get("ketQua") or {}).get("kyVongR"),
    }


def _doc_truoc() -> tuple[dict, float | None]:
    """Ảnh chụp cũ nhất còn dùng được, và nó cách đây mấy giờ.

    Chọn ảnh MỚI NHẤT trong số những ảnh đã đủ già (≥ `CACH_TOI_THIEU_GIO`).
    Không có cái nào đủ già thì lấy cái cũ nhất đang có — thà so với hai giờ
    trước còn hơn không so với gì.
    """
    if not LICH_SU.exists():
        return {}, None
    ds = []
    for dong in LICH_SU.read_text(encoding="utf-8").splitlines():
        if not dong.strip():
            continue
        try:
            ds.append(json.loads(dong))
        except ValueError:
            continue
    if not ds:
        return {}, None
    nay = _dt.datetime.now(_dt.timezone.utc)

    def _gio(x):
        try:
            return (nay - _dt.datetime.fromisoformat(x["luc"])).total_seconds() / 3600
        except (KeyError, ValueError):
            return None

    du_gia = [(x, g) for x in ds if (g := _gio(x)) is not None and g >= CACH_TOI_THIEU_GIO]
    if du_gia:
        return min(du_gia, key=lambda t: t[1])
    x = ds[0]
    return x, _gio(x)


def _so(nay: dict, truoc: dict) -> list[str]:
    """Chỉ những gì ĐỔI. Không đổi thì không nhắc — im lặng là một thông tin."""
    ra = []
    if not truoc:
        return ["Chưa có bản bàn giao trước — đây là lần đầu, mọi thứ đều là mới."]

    a, b = nay["phatHien"], truoc.get("phatHien") or {}
    moi = [k for k in a if k not in b]
    mat = [k for k in b if k not in a]
    if moi:
        ra.append(f"**Phát hiện MỚI ({len(moi)}):** " + " · ".join(moi))
    if mat:
        ra.append(f"**Phát hiện BIẾN MẤT ({len(mat)}):** " + " · ".join(mat)
                  + " — nguồn của chúng không còn đủ mẫu, hoặc vừa hỏng.")

    # Đổi DẤU là thứ đáng báo nhất: cùng một phép đo, kết luận ngược lại.
    doi_dau = []
    for k in set(a) & set(b):
        for truong in ("kyVongR", "expectancyUsd", "riskCv"):
            x, y = (a[k]["so"] or {}).get(truong), (b[k].get("so") or {}).get(truong)
            if isinstance(x, (int, float)) and isinstance(y, (int, float)) and x * y < 0:
                doi_dau.append(f"{k}.{truong}: {y:+.3f} → {x:+.3f}")
    if doi_dau:
        ra.append("**ĐỔI DẤU:** " + " · ".join(doi_dau))

    for ten, khoa, dv in (("số lệnh thật", "soLenhThat", ""), ("kỹ năng", "soKyNang", " file"),
                          ("bộ luật", "soBoLuat", "")):
        x, y = nay.get(khoa), truoc.get(khoa)
        if isinstance(x, int) and isinstance(y, int) and x != y:
            ra.append(f"**{ten}:** {y}{dv} → {x}{dv}")

    if nay.get("champion") != truoc.get("champion"):
        ra.append(f"**CHAMPION ĐÃ ĐỔI:** {truoc.get('champion')} → {nay.get('champion')}")
    return ra or ["Không có gì đổi kể từ lần bàn giao trước."]


# Ngưỡng "im lặng đáng báo động", tính bằng giờ. Vòng lặp chạy 20 giây một lượt,
# nên hơn một giờ không ghi gì là đã có chuyện.
IM_LANG_GIO = 1.0


# Kho đo + số giờ sau đó coi là CŨ. Ngưỡng khác nhau vì nhịp đổi khác nhau:
# nến lịch sử đổi từng giờ, hồ sơ trader ngoài thì vài ngày một lần là đủ.
KHO_DO = (
    ("mau-gia.json", "mẫu giá", 48),
    ("do-khung.json", "hình học khung", 48),
    ("bo-pha.json", "bộ phá", 48),
    ("dau-nhieu-cho.json", "đấu nhiều chợ", 48),
    ("chien-luoc.json", "sổ chiến lược", 72),
    ("trader-ho-so.json", "đài quan sát", 168),
)


def _kho_cu() -> list[str]:
    """Kho đo nào đã cũ.

    Nghi thức báo "đã khởi động ở luồng nền" là THÀNH CÔNG, nhưng luồng nền chết
    cùng tiến trình mỗi lần runtime dựng lại — và không có gì nhận ra. Đài quan
    sát đứng im 12 ngày trong khi nghi thức vẫn xanh.

    Đo TUỔI FILE thay vì tin lời báo cáo: kho cũ là kho cũ, bất kể vì sao. Đây
    là chỗ duy nhất trong bản bàn giao không quan tâm nguyên nhân.
    """
    import time as _t

    ra = []
    for ten, nhan, nguong in KHO_DO:
        f = DATA_DIR / ten
        if not f.exists():
            ra.append(f"`{ten}` — CHƯA CÓ, {nhan} chưa chạy lần nào")
            continue
        gio = (_t.time() - f.stat().st_mtime) / 3600
        if gio > nguong:
            ngay = gio / 24
            ra.append(f"`{ten}` — {nhan} cũ {gio:.0f} giờ"
                      + (f" ({ngay:.1f} ngày)" if ngay >= 1 else "")
                      + f", ngưỡng {nguong}h")
    return ra


def _cong_tra_loi(cong: int) -> bool:
    """Cổng có ai trả lời không.

    Tách khỏi `_con_song()` để phép kiểm thay được. Gộp chung thì mục [16] của
    selftest phụ thuộc vào việc runtime có TÌNH CỜ đang chạy hay không lúc chạy
    kiểm — và nó đã đỏ đúng một lần vì thế, trong khi mã hoàn toàn đúng.

    Một phép kiểm đọc trạng thái ngoài là một phép kiểm sẽ đỏ ngẫu nhiên, và
    phép kiểm đỏ ngẫu nhiên thì rồi sẽ bị bỏ qua.
    """
    import socket

    s = socket.socket()
    s.settimeout(1.5)
    try:
        s.connect(("127.0.0.1", cong))
        return True
    except OSError:
        return False
    finally:
        s.close()

def _con_song() -> list[str]:
    """Bot có đang chạy không — câu hỏi phải trả lời TRƯỚC mọi câu khác.

    Bản đầu của file này không hỏi câu đó. Hậu quả đo được: runtime chết lúc
    23/08 08:03 và không ai biết cho tới khi có người hỏi, **năm ngày rưỡi sau**.
    Trong suốt thời gian ấy bản bàn giao vẫn liệt kê phát hiện, vẫn xếp hạng
    bằng chứng, vẫn trông rất tử tế — về một bộ máy đã tắt.

    Một báo cáo đẹp về một cái xác là dạng nói dối tệ nhất trong cả hệ này, vì
    nó không sai một con số nào.
    """
    import time as _t

    ra = []
    nk = DATA_DIR / "nhat-ky" / "runtime.log"
    if nk.exists():
        gio = (_t.time() - nk.stat().st_mtime) / 3600
        if gio > IM_LANG_GIO:
            ngay = int(gio // 24)
            ra.append(f"**NHẬT KÝ IM {gio:.1f} GIỜ" + (f" ({ngay} ngày)" if ngay else "")
                      + f".** Dòng cuối lúc "
                      + _dt.datetime.fromtimestamp(nk.stat().st_mtime).isoformat(timespec="minutes")
                      + ". Vòng lặp chạy 20 giây một lượt, nên im quá một giờ là đã dừng.")
    else:
        ra.append("**KHÔNG CÓ NHẬT KÝ** — runtime chưa từng chạy trên máy này.")

    cong = 5182
    if not _cong_tra_loi(cong):
        ra.append(f"**CỔNG {cong} KHÔNG TRẢ LỜI.** Bot đang TẮT. Bật lại: "
                  f"`powershell -File dichvu/bat.ps1` hoặc bấm icon Tử Cấm Thành.")

    try:
        tt = json.loads((ROOT / "dichvu" / "trang-thai.json").read_text(encoding="utf-8"))
        if tt.get("dungHan"):
            ra.append(f"**BỘ GIÁM SÁT ĐÃ DỪNG HẲN** — lý do: {tt.get('lyDo')}. "
                      f"Nó sẽ KHÔNG tự dựng lại; phải sửa rồi bật tay.")
        if tt.get("choMang"):
            ra.append(f"Bộ giám sát đang chờ mạng — {tt.get('lyDo')}. Nó vẫn thử lại.")
    except (OSError, ValueError):
        pass
    return ra


def main() -> int:
    nay = _anh_chup()
    truoc, cach_gio = _doc_truoc()
    kq = chung_cat.chung_cat()

    d: list[str] = []
    W = d.append
    W(f"# Bàn giao — {nay['luc']}")
    W("")
    W(f"{nay['soLenhThat']} lệnh thật · {nay['soKyNang']} kỹ năng · {nay['soBoLuat']} bộ luật · "
      f"{kq['soPhatHien']} phát hiện · champion `{nay['champion']}` "
      f"({nay['championKyVong']}R ngoài mẫu)")
    W("")

    # ĐẶT TRƯỚC MỌI MỤC KHÁC. Nếu bot đang tắt thì mọi phần bên dưới là báo cáo
    # về quá khứ, và người đọc cần biết điều đó ở dòng đầu tiên chứ không phải
    # sau khi đã đọc hết bảng phát hiện.
    song = _con_song()
    if song:
        W("## ⚠ BOT KHÔNG CHẠY")
        W("")
        for x in song:
            W(f"- {x}")
        W("")
        W("Mọi con số bên dưới là ảnh chụp lúc nó còn chạy, không phải hiện tại.")
        W("")

    moc = (f"so với ảnh chụp cách đây {cach_gio:.1f} giờ" if cach_gio is not None
           else "chưa có ảnh chụp nào để so")
    W(f"## Đổi gì kể từ lần trước — {moc}")
    W("")
    for x in _so(nay, truoc):
        W(f"- {x}")
    W("")

    cu = _kho_cu()
    if cu:
        W("## Kho đo đã cũ")
        W("")
        W("Tuổi FILE, không phải lời báo cáo của nghi thức — luồng nền chết cùng")
        W("tiến trình mà không có gì nhận ra.")
        W("")
        for x in cu:
            W(f"- {x}")
        W("")

    W("## Chưa đủ dữ liệu để nói")
    W("")
    W("Mỗi dòng là một điều bộ máy ĐANG ĐO nhưng chưa đủ mẫu để kết luận. Phần lớn")
    W("gỡ được chỉ bằng cách có thêm dữ liệu, không cần mã mới.")
    W("")
    if kq["daBo"]:
        for b in kq["daBo"]:
            W(f"- `{b['ma']}` — {b['viSao']}")
    else:
        W("- (không có — mọi nguồn đều đủ mẫu)")
    W("")

    W("## Phát hiện mạnh nhất đang có")
    W("")
    ds = sorted(store.read_all(store.PHAT_HIEN),
                key=lambda p: (({"CAO": 0, "VỪA": 1, "THẤP": 2}).get(p["doTin"], 3),
                               -(p.get("mau") or 0)))
    for p in ds[:6]:
        W(f"- **[{p['doTin']} · mẫu {p['mau']:,}]** {p['cau']}")
    W("")

    W("## Chỗ vòng tuần hoàn đang đứt")
    W("")
    dut = []
    # `brain_mode()` là nguồn sự thật, và nó KHÔNG đọc nội dung khoá — chỉ xem có
    # hay không. Bản đầu tôi gọi `get_brain()` ở đây: nó là coroutine, nên câu
    # lệnh trả về một đối tượng chưa chạy, `getattr(..., "mode")` ra None, và
    # dòng cảnh báo hiện lên đúng vì lý do sai. Cùng loại lỗi với mọi thứ khác
    # trong hệ này: không báo lỗi, chỉ nói nhầm.
    from trader.config import brain_mode
    if brain_mode() != "claude":
        dut.append("Bộ não ở chế độ `mock` — kho kỹ năng và mọi phát hiện KHÔNG tới "
                   "được chỗ ra quyết định. Đây là chỗ đứt lớn nhất và nó không sửa "
                   "được bằng mã.")
    lenh = [t for t in store.read_all(store.TRADES) if t.get("status") == "CLOSED"]
    if lenh:
        cd = {t.get("regimeKey") for t in lenh[-10:]}
        if len(cd) == 1:
            ma = next(iter(cd))
            co = any(p.get("cheDo") == ma for p in ds)
            if not co:
                dut.append(f"10 lệnh gần nhất đều ở `{ma}` mà KHÔNG phát hiện nào phủ chế "
                           f"độ đó — bot đang giao dịch ở chỗ nó biết ít nhất.")
    if not dut:
        dut.append("(không phát hiện chỗ đứt nào ở lượt này)")
    for x in dut:
        W(f"- {x}")
    W("")

    ra = "\n".join(d)
    print(ra)
    if GHI:
        f = DATA_DIR / "BAN-GIAO.md"
        f.write_text(ra + "\n", encoding="utf-8")
        # CỘNG DỒN, không ghi đè. Mỗi lần chạy thêm một ảnh chụp; phần so sánh
        # tự chọn ảnh đủ già. Ghi đè là cách chắc chắn nhất để mất đúng khoảng
        # thời gian có chuyện xảy ra.
        with LICH_SU.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(nay, ensure_ascii=False) + "\n")
        print(f"\nđã ghi {f} và thêm một ảnh chụp vào {LICH_SU.name}")
    else:
        print("\n(chưa ghi — thêm --ghi để lưu và đặt mốc so sánh cho lần sau)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
