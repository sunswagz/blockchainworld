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

    # ĐỔI TÊN MÃ đọc y hệt "biến mất + mới". Đã xảy ra: `that:TREND_UP` thành
    # `that:khung?:TREND_UP` trong một commit, và bản bàn giao báo 5 phát hiện
    # biến mất kèm câu "nguồn không còn đủ mẫu, hoặc vừa hỏng" — một lời giải
    # thích sai về một chuyện không xảy ra. Báo động sai dạy người ta bỏ qua
    # báo động.
    #
    # Không đoán bằng cách so nội dung câu: hai phát hiện khác nguồn có thể
    # trùng câu, và đoán sai còn tệ hơn không đoán. Chỉ soi phần ĐUÔI của mã —
    # quy ước đặt tên ở đây là `<loại>:<khung>:<chế độ>`, nên đổi tên thường
    # chỉ chèn thêm một đoạn mà giữ nguyên đuôi.
    duoi = lambda k: k.rsplit(":", 1)[-1]
    doi_ten = {duoi(k) for k in moi} & {duoi(k) for k in mat}

    if moi:
        ra.append(f"**Phát hiện MỚI ({len(moi)}):** " + " · ".join(moi))
    if mat:
        # LUÂN PHIÊN cũng đọc như biến mất. Lò chưng cất chỉ đưa 3 bác-bỏ gần
        # nhất thành phát hiện riêng; cái thứ tư rời bảng nhưng vẫn nằm trong
        # danh sách tóm tắt `da-thu-va-hong`. Nó không mất, nó nhường chỗ.
        con = set((a.get("da-thu-va-hong", {}).get("so") or {}).get("maDaBacBo") or [])
        xoay = [k for k in mat
                if k.startswith("bac-bo:") and k.split(":", 1)[1] in con]
        ngo = [k for k in mat if duoi(k) in doi_ten]
        ra.append(f"**Phát hiện BIẾN MẤT ({len(mat)}):** " + " · ".join(mat)
                  + " — nguồn của chúng không còn đủ mẫu, hoặc vừa hỏng."
                  + (f" {len(xoay)} trong số đó ({', '.join(sorted(xoay))}) vẫn"
                     f" nằm trong «da-thu-va-hong» — chúng LUÂN PHIÊN ra khỏi"
                     f" bảng cho bác bỏ mới hơn, không mất." if xoay else "")
                  + (f" NHƯNG {len(ngo)} trong số đó có một phát hiện MỚI trùng"
                     f" đuôi mã ({', '.join(sorted(ngo))}) — nhiều khả năng chỉ"
                     f" là ĐỔI TÊN MÃ, không phải mất phép đo." if ngo else ""))

    # Đổi DẤU là thứ đáng báo nhất: cùng một phép đo, kết luận ngược lại.
    doi_dau = []
    for k in set(a) & set(b):
        for truong in ("kyVongR", "expectancyUsd", "riskCv"):
            # Cả hai bên dùng `.get`: một bên `[...]` là chỗ nổ nếu có phát hiện
            # nào thiếu trường `so` — và mục này chạy trên dữ liệu của LẦN TRƯỚC,
            # tức dữ liệu sinh bởi một bản mã có thể đã khác.
            x, y = ((a[k].get("so") or {}).get(truong),
                    (b[k].get("so") or {}).get(truong))
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


# Ngưỡng "im lặng đáng báo động", tính bằng giờ.
#
# Tiền đề cũ SAI: "vòng lặp chạy 20 giây một lượt nên hơn một giờ không ghi gì
# là đã có chuyện". Chỉ `bus.log` mới in ra stdout — `bus.emit` thì không — nên
# nhật ký chỉ nhận SỰ KIỆN ĐÁNG GHI: đổi chế độ, vào lệnh, bị chặn, lỗi. Bot giữ
# ba vị thế trong một phiên yên ắng thì im hàng giờ là bình thường.
#
# Đã báo động nhầm lúc 08:59 ngày 30/08: bàn giao in "⚠ BOT KHÔNG CHẠY — NHẬT KÝ
# IM 1,3 GIỜ" trong khi cả bộ giám sát lẫn runtime đều sống và cổng vẫn trả lời.
# Một ⚠ cho thứ không gãy là cách nhanh nhất dạy người ta bỏ qua ⚠.
#
# Nên nhật ký im KHÔNG còn là bằng chứng chết khi CỔNG CÒN TRẢ LỜI — lúc ấy nó
# chỉ là một dòng ghi chú, và ngưỡng rộng hơn hẳn.
IM_LANG_GIO = 1.0
IM_LANG_DU_SONG_GIO = 6.0


# Kho đo + số giờ sau đó coi là CŨ. Ngưỡng khác nhau vì nhịp đổi khác nhau:
# nến lịch sử đổi từng giờ, hồ sơ trader ngoài thì vài ngày một lần là đủ.
KHO_DO = (
    ("mau-gia.json", "mẫu giá", 48),
    ("do-khung.json", "hình học khung", 48),
    ("bo-pha.json", "bộ phá", 48),
    ("dau-nhieu-cho.json", "đấu nhiều chợ", 48),
    ("lessons-soat-lai.jsonl", "soát lại bài học", 48),
    ("do-huong.json", "đo hướng LONG/SHORT", 48),
    ("lo-luyen.json", "lò luyện", 48),
    ("chien-luoc.json", "sổ chiến lược", 72),
    ("trader-ho-so.json", "đài quan sát", 168),
)


# Ngân sách cho kho kỹ năng, tính bằng ký tự. Vượt là phải QUYẾT ĐỊNH, không
# phải trôi qua.
#
# Trước khi bộ não chạy thật, thêm một kỹ năng là miễn phí — nó chỉ nằm đó.
# Từ khi nối đường CLI, TOÀN BỘ kho đi vào lời nhắc hệ thống của MỌI lượt gọi:
# 46.652 ký tự ≈ 14.578 token, nhân với trần 8 lượt/ngày là ~117k token/ngày
# chỉ để chở kỹ năng.
#
# Nên kho kỹ năng không còn là chỗ chứa miễn phí. Ngưỡng này không cấm — nó
# bắt người thêm phải nhìn thấy cái giá và nói ra lý do.
NGAN_SACH_KY_NANG = 60_000


def _gia_kho_ky_nang() -> list[str]:
    """Kho kỹ năng đang tốn bao nhiêu mỗi lượt gọi."""
    try:
        from trader.brain import load_skills
        from trader.config import CONFIG, brain_mode
        sk, n = load_skills()
    except Exception:  # noqa: BLE001
        return []
    if brain_mode() == "mock":
        return []      # chưa gọi model thì kho chưa tốn gì
    tok = len(sk) / 3.2
    tran = CONFIG["brain"].get("maxCallsPerDay") or 0
    ra = [f"{n} kỹ năng · {len(sk):,} ký tự ≈ {tok:,.0f} token MỖI LƯỢT GỌI"
          f" · ~{tok * tran / 1000:,.0f}k token/ngày ở trần {tran} lượt"]
    if len(sk) > NGAN_SACH_KY_NANG:
        ra.append(f"**VƯỢT NGÂN SÁCH** {NGAN_SACH_KY_NANG:,} ký tự — mỗi kỹ năng thêm "
                  f"vào từ đây làm mọi lượt gọi đắt hơn. Gộp, cắt, hoặc nâng ngưỡng "
                  f"một cách có chủ ý.")
    return ra

# Bao nhiêu lượt NO_TRADE liên tiếp thì gọi là ĐỨNG IM, không phải thận trọng.
# Trên khung 4h, 12 lượt là khoảng hai ngày không vào lệnh nào.
DUNG_IM_LIEN_TIEP = 12


def _champion_so() -> str:
    """Con số đứng cạnh tên champion ở DÒNG ĐẦU bản bàn giao.

    Mặc định là `ketQua.kyVongR` — kết quả trên chợ trong cấu hình, tức MỘT chợ,
    đúng cái chợ mọi thứ ở đây từng được đo lên. Dòng đầu là dòng người ta đọc
    khi không đọc gì khác, nên để con số dễ dãi nhất ở đó là chọn sai chỗ.

    Có phép đo nhiều chợ thì lấy con số GỘP, và ghi cả hai để không ai tưởng
    con số đổi vì bộ luật đổi.
    """
    try:
        cl = json.loads((DATA_DIR / "chien-luoc.json").read_text(encoding="utf-8"))
    except (ValueError, OSError, FileNotFoundError):
        return "chưa có sổ chiến lược"
    ma = (cl.get("champion") or {}).get("ma")
    mot = ((cl.get("champion") or {}).get("ketQua") or {}).get("kyVongR")
    gop = next((p for p in store.read_all(store.PHAT_HIEN)
                if p["ma"] in (f"cho:{ma}", f"cho-gop:{ma}")), None)
    kv = (gop.get("so") or {}).get("kyVongR") if gop else None
    if kv is None:
        return f"{mot}R ngoài mẫu, MỘT chợ" if mot is not None else "chưa đo"
    return (f"{kv:+.3f}R gộp {(gop.get('so') or {}).get('soCho')} chợ / "
            f"{gop['mau']} lệnh"
            + (f", {mot:+.3f}R ở chợ đang chạy" if mot is not None else ""))

def _champion_bi_bac_bo() -> list[str]:
    """Champion có đang bị chính phép đo của mình bác bỏ không.

    Dòng tiêu đề của bản bàn giao ghi "champion MOCK_RULES_V1 (0.032R ngoài
    mẫu)". Con số đó là của MỘT chợ — BTCUSDT:4h, chợ mà cấu hình đang chạy.
    Đo trên 8 chợ thì cùng bộ luật ấy được −0,047R qua 193 lệnh, dương ở 2/8.
    Hai chợ dương là BTC và ETH: đúng hai chợ mọi thứ ở đây từng được đo lên.

    Và không có đường nào gỡ champion xuống. `chien_luoc.phan_quyet` là cửa
    DUYỆT — nó chặn kẻ thách đấu kém, nhưng không ai chặn kẻ đang ngồi. Một bộ
    luật lên champion rồi thì chỉ bị thay khi có cái tốt hơn, mà không cái nào
    tốt hơn, nên nó ngồi mãi dù phép đo đã bác bỏ nó.

    Mục này KHÔNG tự gỡ ai xuống — đưa một bộ luật vào hay ra khỏi tiền thật là
    việc bấm tay ở buồng lái. Nó chỉ không để con số đẹp của một chợ đứng một
    mình ở dòng tiêu đề.
    """
    try:
        cl = json.loads((DATA_DIR / "chien-luoc.json").read_text(encoding="utf-8"))
    except (ValueError, OSError, FileNotFoundError):
        return []
    ma = (cl.get("champion") or {}).get("ma")
    if not ma:
        return []
    mot_cho = ((cl.get("champion") or {}).get("ketQua") or {})
    kv_mot, cho_mot = mot_cho.get("kyVongR"), mot_cho.get("cho") or "chợ không rõ"

    gop = next((p for p in store.read_all(store.PHAT_HIEN)
                if p["ma"] in (f"cho:{ma}", f"cho-gop:{ma}")), None)
    if not gop:
        return []
    kv_gop = (gop.get("so") or {}).get("kyVongR")
    if kv_gop is None or kv_mot is None:
        return []
    if kv_gop > 0:
        return []

    ra = [f"Dòng tiêu đề ghi champion `{ma}` **{kv_mot:+.3f}R** — con số của MỘT "
          f"chợ ({cho_mot}). Gộp {(gop.get('so') or {}).get('soCho')} chợ thì cùng "
          f"bộ luật ấy được **{kv_gop:+.3f}R qua {gop['mau']} lệnh ngoài mẫu**, "
          f"dương ở {(gop.get('so') or {}).get('duong')}."]
    if kv_mot > 0:
        ra.append("Chợ đang chạy là một trong số ít chợ nó dương. Đó chính là chợ "
                  "mọi thứ ở đây từng được đo lên — nên đừng đọc nó như bằng chứng "
                  "độc lập.")
    ra.append("Và **không có đường nào gỡ champion xuống**: `phan_quyet` là cửa "
              "DUYỆT, nó chặn kẻ thách đấu kém chứ không chặn kẻ đang ngồi. Bộ luật "
              "này chỉ bị thay khi có cái tốt hơn — mà chưa cái nào tốt hơn. Gỡ hay "
              "giữ là việc bấm tay ở buồng lái, không phải việc của bản bàn giao.")
    return ra

def _gia_thuyet_ket() -> list[str]:
    """Giả thuyết đang mở mà KHÔNG có lệnh thật nào kể từ lúc khai.

    `doi-khung-sang-4h` đo kỳ vọng tiền trên lệnh thật mở sau khi đổi khung;
    `bo-nao-that-hon-luat` so CLI_V1 với MOCK_RULES_V1 trên lệnh thật. Cả hai
    chốt được chỉ khi có lệnh mới — và bot đang đứng ngoài, có căn cứ.

    Không cần biết giả thuyết ĐO cái gì để nói được điều này: nếu từ lúc khai
    tới giờ chưa có lệnh thật nào, thì mọi giả thuyết cần lệnh thật đều đứng
    yên, và thời gian trôi thêm không đổi gì. Đếm được, nên không phải đoán.

    Nối với mục «bot đứng im»: đó là cùng một thế bí nhìn từ phía sổ giả thuyết.
    """
    try:
        from trader import so_gia_thuyet as G
        # Sổ không có trường "đang mở" — mở nghĩa là CHƯA có bản ghi chốt cho mã
        # đó, và `tom_tat()` là chỗ duy nhất tính điều ấy. Tự suy ra ở đây là dựng
        # bản sao thứ hai của cùng một luật, rồi hai bản lệch nhau.
        dang_mo = set(G.tom_tat().get("dangMo") or [])
        mo = [x for x in G.doc()
              if x.get("ma") in dang_mo and x.get("loai") == "khai"]
    except Exception:  # noqa: BLE001
        return []
    if not mo:
        return []
    trades = [t for t in store.read_all(store.TRADES) if t.get("openedAt")]
    ra = []
    for x in mo:
        luc = x.get("luc")
        if not luc:
            continue
        sau = [t for t in trades if (t.get("openedAt") or "") > luc]
        if not sau:
            ra.append(f"`{x['ma']}` — khai lúc {luc[:16].replace('T', ' ')}, "
                      f"CHƯA có lệnh thật nào mở kể từ đó")
    if not ra:
        return []
    return ra + ["Giả thuyết nào đo trên lệnh thật thì đứng yên cùng bot. Chờ thêm "
                 "không gỡ được — hoặc đổi thứ làm bot đứng ngoài, hoặc khai lại "
                 "một mã MỚI đo được bằng chạy lại thay vì lệnh thật."]

def _dung_im() -> list[str]:
    """Bot đứng ngoài liên tục có căn cứ — và vì thế sẽ đứng mãi.

    Đây KHÔNG phải lỗi. Bộ não đọc "chế độ này kỳ vọng âm qua 41 lệnh thật, 21
    bài học đòi đổi chiến lược" rồi ra NO_TRADE là quyết định đúng.

    Nhưng nó tạo một thế bí kín: đứng ngoài ⇒ không có lệnh mới ⇒ bằng chứng âm
    không bao giờ được cập nhật ⇒ đứng ngoài tiếp. Hệ dừng ở một trạng thái
    ĐÚNG và VÔ SINH, và không có gì trong bảng phân biệt nó với "đang chờ thời".

    Mục này không đề nghị nới lỏng gì. Nó chỉ nói ra rằng cái chờ ấy sẽ không tự
    kết thúc — thứ phải đổi là CHIẾN LƯỢC, không phải thời gian.
    """
    th = store.read_all(store.THESES)
    if not th:
        return []
    lien = 0
    for t in reversed(th):
        if t.get("action") == "NO_TRADE":
            lien += 1
        else:
            break
    if lien < DUNG_IM_LIEN_TIEP:
        return []
    ma = []
    for t in reversed(th[-lien:]):
        ma.extend(t.get("reason_codes") or [])
        if len(ma) > 6:
            break
    return [f"**{lien} lượt NO_TRADE liên tiếp.** Lý do gần nhất: "
            + " · ".join(dict.fromkeys(ma[:6]))
            + ". Nếu lý do là bằng chứng ÂM về chính chế độ đang chạy thì cái chờ "
            + "này không tự kết thúc: không vào lệnh nghĩa là không có dữ liệu mới, "
            + "nên bằng chứng âm đứng nguyên. Thứ phải đổi là CHIẾN LƯỢC hoặc CHỢ, "
            + "không phải thời gian."]

def _tuoi(f) -> tuple[float, str]:
    """Tuổi kho tính bằng giờ, và ĐO THEO CÁI GÌ.

    mtime nói "file bị chạm", không nói "số bên trong được đo lại". Một lượt đo
    hỏng nửa chừng vẫn ghi file, và kho trông tươi trong khi nội dung là của
    hôm kia. Nên ưu tiên dấu `luc` mà chính script đo đóng vào file.

    Rơi về mtime khi không có dấu — và NÓI RA là đang rơi về. Kho chưa kịp học
    đóng dấu vẫn phải đo được; cái không được phép là đo bằng thước yếu hơn mà
    không ai biết.
    """
    import time as _t

    mt = (_t.time() - f.stat().st_mtime) / 3600
    if f.suffix != ".json":
        return mt, "mtime"
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
        luc = d.get("luc") if isinstance(d, dict) else None
        if not luc:
            return mt, "mtime (kho không đóng dấu)"
        t = _dt.datetime.fromisoformat(luc)
        if t.tzinfo is None:
            t = t.replace(tzinfo=_dt.timezone.utc)
        return (_dt.datetime.now(_dt.timezone.utc) - t).total_seconds() / 3600, "dấu `luc`"
    except (ValueError, OSError, TypeError):
        return mt, "mtime (dấu hỏng)"

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
        gio, theo = _tuoi(f)
        if gio > nguong:
            ngay = gio / 24
            ra.append(f"`{ten}` — {nhan} cũ {gio:.0f} giờ"
                      + (f" ({ngay:.1f} ngày)" if ngay >= 1 else "")
                      + f", ngưỡng {nguong}h (đo theo {theo})")
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

def _lan_demo() -> list[str]:
    """Làn demo hai chiều còn sống không, và nó đã đi được bao xa.

    Bản bàn giao là thứ phiên sau ĐỌC. Một phép đo tiến tướng kéo ~6 tuần mà
    không có dòng nào trong bàn giao thì nó sẽ chết lặng lẽ: sổ ngừng lớn, và
    "chưa có lệnh SHORT nào" đọc y hệt "chưa tới lúc".

    Cùng bài học với `_con_song`: runtime từng chết 5 ngày rưỡi mà bản bàn giao
    vẫn đẹp. Ở đây rủi ro còn dễ sót hơn, vì làn demo KHÔNG có vị thế thật nào
    để ai đó tình cờ nhận ra.
    """
    import time as _t

    so = ROOT / "data-hai-chieu"
    if not so.exists():
        return []
    ra = []
    # Cùng một luật với `_con_song`, và cùng một cái bẫy: nhật ký chỉ nhận sự
    # kiện ĐÁNG GHI (`bus.log`), không nhận mỗi vòng. Bản đầu của hàm này chép
    # lại logic cũ và báo "**LÀN DEMO IM 1,5 GIỜ**" ngay TRÊN dòng in ra khung,
    # bộ luật và chế độ nó đang chạy — hai dòng liền nhau, một dòng nói dối.
    #
    # Làn demo còn im hơn làn chính: khung 1d, một nến mỗi ngày, và bộ luật
    # kéo-lùi rất kén. Im vài giờ ở đây là chuyện thường ngày.
    #
    # Gọi cổng ĐÚNG MỘT LẦN: mỗi lần là một lần chờ timeout, và bản trước gọi
    # tới ba lần cho cùng một câu hỏi.
    song = _cong_tra_loi(5282)
    nk = so / "nhat-ky" / "runtime.log"
    if not nk.exists():
        if not song:
            ra.append("**LÀN DEMO CHƯA TỪNG CHẠY** trên máy này.")
    else:
        gio = (_t.time() - nk.stat().st_mtime) / 3600
        if not song and gio > IM_LANG_GIO:
            ra.append(f"**LÀN DEMO IM {gio:.1f} GIỜ.** Bật lại: "
                      f"`powershell -File dichvu/bat.ps1 -Demo`.")
        elif song and gio > IM_LANG_DU_SONG_GIO:
            ra.append(f"Làn demo im {gio:.1f} giờ nhưng cổng 5282 vẫn trả lời — "
                      f"đang chạy, chỉ là không có sự kiện đáng ghi. Khung 1d thì "
                      f"một nến mỗi ngày, im lâu là bình thường.")
    if not song:
        ra.append("**CỔNG 5282 KHÔNG TRẢ LỜI** — làn demo đang TẮT. Bật lại: "
                  "`powershell -File dichvu/bat.ps1 -Demo`.")

    # Đi được bao xa: đếm lệnh SHORT đã đóng, so với 30 lệnh mà giả thuyết cần.
    try:
        ds = [json.loads(x) for x in (so / "trades.jsonl").read_text(
            encoding="utf-8").splitlines() if x.strip()]
    except (OSError, ValueError):
        ds = []
    n_s = sum(1 for t in ds if t.get("side") == "SHORT" and t.get("closedAt"))
    n_l = sum(1 for t in ds if t.get("side") == "LONG" and t.get("closedAt"))
    ra.append(f"Làn demo (hai chiều, sàn giấy, cổng 5282): {n_s} lệnh SHORT đã "
              f"đóng / 30 cần cho «keo-lui-short-tien-tuong» · {n_l} lệnh LONG. "
              f"Xem cả hai làn: `python scripts/so-hai-lan.py`.")

    # CẤU HÌNH ĐANG CHẠY, hỏi thẳng buồng lái chứ không đọc file. Phép đo này
    # kéo hàng tuần; trong ngần ấy thời gian cấu hình có thể trôi mà không ai
    # thấy — và đã trôi một lần: hai giờ đầu làn demo chạy khung 4h vì kế thừa
    # làn chính, tức đo đúng cái khung đã bị bác bỏ.
    #
    # Đọc file thì chỉ biết file nói gì. Tiến trình đang chạy có thể đã nạp một
    # bản khác từ lâu.
    try:
        import urllib.request

        with urllib.request.urlopen("http://localhost:5282/api/state",
                                    timeout=4) as r:
            st = json.loads(r.read().decode("utf-8"))
        tf = (st.get("timeframes") or {}).get("primary")
        luat = (st.get("thesis") or {}).get("strategy")
        canh = ""
        if tf != "1d":
            canh = ("  ⚠ SAI KHUNG — phép đo làm nên làn này đo trên 1d; cùng bộ "
                    "luật trên 4h là −0,248R và đã bị bác bỏ.")
        if st.get("spotOnly"):
            canh += "  ⚠ spotOnly BẬT — làn demo sẽ không short được."
        ra.append(f"Đang chạy: khung `{tf}` · bộ luật `{luat or 'chưa có luận điểm'}`"
                  f" · chế độ `{st.get('mode')}`.{canh}")
    except Exception:  # noqa: BLE001 — không gọi được thì đã có dòng cổng ở trên
        pass
    return ra


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
    cong = 5182
    song = _cong_tra_loi(cong)
    nk = DATA_DIR / "nhat-ky" / "runtime.log"
    if not nk.exists():
        ra.append("**KHÔNG CÓ NHẬT KÝ** — runtime chưa từng chạy trên máy này.")
    else:
        gio = (_t.time() - nk.stat().st_mtime) / 3600
        ngay = int(gio // 24)
        _luc = _dt.datetime.fromtimestamp(
            nk.stat().st_mtime).isoformat(timespec="minutes")
        if not song and gio > IM_LANG_GIO:
            ra.append(f"**NHẬT KÝ IM {gio:.1f} GIỜ"
                      + (f" ({ngay} ngày)" if ngay else "")
                      + f".** Dòng cuối lúc {_luc}.")
        elif song and gio > IM_LANG_DU_SONG_GIO:
            ra.append(f"Nhật ký im {gio:.1f} giờ"
                      + (f" ({ngay} ngày)" if ngay else "")
                      + f" (dòng cuối {_luc}) NHƯNG cổng "
                      f"{cong} vẫn trả lời — bot đang chạy. Chỉ `bus.log` mới ra "
                      f"nhật ký, nên im lâu nghĩa là không có sự kiện đáng ghi, "
                      f"không phải đã dừng. Đáng ngó qua, không đáng báo động.")

    if not song:
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
      f"({_champion_so()})")
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

    demo = _lan_demo()
    if demo:
        W("## Làn demo hai chiều")
        W("")
        for x in demo:
            W(f"- {x}")
        W("")

    moc = (f"so với ảnh chụp cách đây {cach_gio:.1f} giờ" if cach_gio is not None
           else "chưa có ảnh chụp nào để so")
    W(f"## Đổi gì kể từ lần trước — {moc}")
    W("")
    for x in _so(nay, truoc):
        W(f"- {x}")
    W("")

    gia = _gia_kho_ky_nang()
    if gia:
        W("## Giá của kho kỹ năng")
        W("")
        for x in gia:
            W(f"- {x}")
        W("")

    bb = _champion_bi_bac_bo()
    if bb:
        W("## Champion đang bị chính phép đo của mình bác bỏ")
        W("")
        for x in bb:
            W(f"- {x}")
        W("")

    im = _dung_im()
    if im:
        W("## Bot đang đứng im — có căn cứ, và sẽ đứng mãi")
        W("")
        for x in im:
            W(f"- {x}")
        for x in _gia_thuyet_ket():
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
    # `!= "claude"` là phép so của thời chỉ có HAI chế độ. Sau khi thêm `cli`,
    # nó khiến bản bàn giao báo "bộ não ở chế độ mock" trong khi bộ não thật
    # đang chạy — chính tài liệu sinh ra để phát hiện nói dối lại đi nói dối.
    if brain_mode() == "mock":
        dut.append("Bộ não ở chế độ `mock` — kho kỹ năng và mọi phát hiện KHÔNG tới "
                   "được chỗ ra quyết định. Nối bằng khoá API, hoặc bằng claude CLI "
                   "nếu máy đã đăng nhập gói tháng (`BRAIN=cli`).")
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
        # KHÔNG viết "không phát hiện chỗ đứt nào". Mục này chỉ soi đúng hai
        # thứ, và một câu như thế nghe như đã soát hết — cùng loại trấn an sai
        # với dòng log "CLI (không tốn tiền)". Im lặng không phải bằng chứng.
        dut.append("Hai phép soi ở mục này đều sạch: bộ não KHÔNG ở chế độ mock, "
                   "và các lệnh gần nhất không dồn vào một chế độ chưa có phát hiện "
                   "nào phủ. Đó là TẤT CẢ những gì mục này biết soi — chỗ đứt kiểu "
                   "khác vẫn có thể đang mở.")
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
