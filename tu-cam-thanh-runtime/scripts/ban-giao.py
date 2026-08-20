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
from trader.config import DATA_DIR  # noqa: E402

GHI = "--ghi" in sys.argv
TRUOC = DATA_DIR / "ban-giao-truoc.json"


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


def _doc_truoc() -> dict:
    if not TRUOC.exists():
        return {}
    try:
        return json.loads(TRUOC.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return {}


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


def main() -> int:
    nay = _anh_chup()
    truoc = _doc_truoc()
    kq = chung_cat.chung_cat()

    d: list[str] = []
    W = d.append
    W(f"# Bàn giao — {nay['luc']}")
    W("")
    W(f"{nay['soLenhThat']} lệnh thật · {nay['soKyNang']} kỹ năng · {nay['soBoLuat']} bộ luật · "
      f"{kq['soPhatHien']} phát hiện · champion `{nay['champion']}` "
      f"({nay['championKyVong']}R ngoài mẫu)")
    W("")

    W("## Đổi gì kể từ lần trước")
    W("")
    for x in _so(nay, truoc):
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
        TRUOC.write_text(json.dumps(nay, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\nđã ghi {f} và mốc so sánh {TRUOC.name}")
    else:
        print("\n(chưa ghi — thêm --ghi để lưu và đặt mốc so sánh cho lần sau)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
