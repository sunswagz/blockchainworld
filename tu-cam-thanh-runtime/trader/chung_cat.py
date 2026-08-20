"""LÒ CHƯNG CẤT — biến thứ ĐO ĐƯỢC thành thứ NHỚ ĐƯỢC.

Chỗ đứt của cả bộ máy nằm đúng ở đây. Ba cỗ máy đo chạy tốt và đo ra những điều
rất đáng biết:

    phòng huấn luyện   TREND_UP|none lỗ đều −0,422R qua 36 lệnh chạy lại
    đài quan sát       11 hồ sơ trader, chuyên gia theo chế độ, đồng thuận
    sổ thật            8 lệnh, rủi ro không đều, kỳ vọng lệch dấu với tiền

…và **không cái nào tới được bộ não.** Kết quả nằm trong `trader-ho-so.json`,
trong `lessons-chay-lai.jsonl`, trên bảng — rồi ở đó. Bộ não mỗi lượt lại bắt
đầu từ con số không, trong khi cách đó hai thư mục là câu trả lời.

Đo được mà không nhớ được thì không phải học. Đó là quan trắc.

CÁI LÒ NÀY LÀM GÌ

Đọc mọi kho đo, chưng ra **phát hiện** (`phat-hien.jsonl`) — mỗi phát hiện là
MỘT CÂU kèm số đo và **cỡ mẫu của chính nó**. `journal.recall()` kéo chúng vào
prompt cùng bài học, lọc theo chế độ hiện tại.

BA LUẬT CỦA LÒ

**1. Câu nào cũng phải mang theo cỡ mẫu.** "Chế độ này lỗ" là tin đồn. "Chế độ
này lỗ đều −0,422R qua 36 lệnh chạy lại" là một phát hiện. Cỡ mẫu nằm TRONG câu
chứ không nằm ở một trường bên cạnh, vì trường bên cạnh sẽ bị bỏ qua khi đọc.

**2. Từ chối phải đếm được.** Cửa lọc bỏ phát hiện thiếu mẫu — nhưng nếu bỏ im
lặng thì "không có phát hiện nào" trông giống hệt "chưa đo lần nào". Lò trả về
`daBo` kèm lý do cho từng cái, và số đó lên bảng.

**3. Chưng lại là ghi đè sạch, không cộng dồn.** Phát hiện là ẢNH CHỤP của số
liệu lúc này, không phải sự kiện đã xảy ra. Cộng dồn thì phát hiện cũ về một
chế độ nay đã khác sẽ nằm cạnh phát hiện mới và cả hai cùng trông có căn cứ.
Kho này vì thế sinh lại được, và `store.write_all` cho phép ghi đè.
"""
from __future__ import annotations

import datetime as _dt
import json
from collections import defaultdict

from . import store
from .config import DATA_DIR

# — Ngưỡng mẫu tối thiểu, theo NGUỒN —
# Không dùng chung một ngưỡng: lệnh chạy lại rẻ và nhiều nên đòi hỏi cao hơn;
# lệnh thật đắt và hiếm nên ngưỡng thấp hơn nhưng độ tin cũng thấp theo.
MAU_TOI_THIEU = {
    "chay-lai": 10,      # lệnh chạy lại: rẻ, nhiều, chỉ tin phần cấu trúc
    "so-that": 5,        # lệnh thật: đắt, hiếm, nhưng có nhảy giá và khớp một phần
    "dai-quan-sat": 5,   # vòng của một trader ngoài — dưới mức này không đọc ra kiểu
    "chien-luoc": 1,     # champion là một bản ghi, không phải mẫu thống kê
}


def _gio() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def _pd(ma, nguon, cau, mau, so=None, che_do=None, do_tin=None) -> dict:
    return {
        "ma": ma, "nguon": nguon, "cheDo": che_do, "cau": cau,
        "mau": mau, "doTin": do_tin or _do_tin(nguon, mau),
        "so": so or {}, "luc": _gio(),
    }


def _do_tin(nguon: str, mau: int) -> str:
    nguong = MAU_TOI_THIEU.get(nguon, 5)
    if mau >= nguong * 3:
        return "CAO"
    if mau >= nguong:
        return "VỪA"
    return "THẤP"


# ── Nguồn 1 · phòng huấn luyện (chạy lại lịch sử) ──────────────────────────
def _tu_chay_lai(bo: list) -> list[dict]:
    """Gộp bài học chạy lại theo CHẾ ĐỘ.

    36 bài học rời rạc về cùng một chế độ không nói được điều mà một câu gộp nói
    được, vì `journal._chon()` chỉ kéo tối đa 6 bài vào prompt — 30 bài còn lại
    có tồn tại cũng như không. Gộp lại thì cả 36 lệnh cùng đứng sau một câu.
    """
    ra = []
    g: dict[str, list] = defaultdict(list)
    for l in store.read_all(store.LESSONS_CHAY_LAI):
        g[l.get("regimeKey") or l.get("regime") or "?"].append(l)

    for ma, ds in sorted(g.items()):
        if ma == "?":
            continue
        if len(ds) < MAU_TOI_THIEU["chay-lai"]:
            bo.append({"ma": f"che-do:{ma}", "nguon": "chay-lai",
                       "viSao": f"{len(ds)} lệnh < ngưỡng {MAU_TOI_THIEU['chay-lai']}"})
            continue
        rs = [l.get("rMultiple") or 0 for l in ds]
        ky_vong = sum(rs) / len(rs)
        thang = sum(1 for r in rs if r > 0)
        ty_thang = thang / len(ds) * 100

        # Chỉ phát biểu khi hiệu ứng đủ rõ. Kỳ vọng ±0,1R trên vài chục lệnh là
        # tiếng ồn, và một câu chắc nịch về tiếng ồn còn tệ hơn im lặng.
        if abs(ky_vong) < 0.1:
            bo.append({"ma": f"che-do:{ma}", "nguon": "chay-lai",
                       "viSao": f"kỳ vọng {ky_vong:+.3f}R quá gần 0 — chưa phải hiệu ứng"})
            continue

        huong = "LỖ ĐỀU" if ky_vong < 0 else "ăn được"
        cau = (f"Chế độ {ma}: {huong} — kỳ vọng {ky_vong:+.3f}R, thắng {ty_thang:.1f}% "
               f"qua {len(ds)} lệnh CHẠY LẠI. Đây là phát biểu về CẤU TRÚC (chế độ nào "
               f"hợp chiến lược này), không phải về ĐỘ LỚN: lệnh chạy lại khớp đúng giá "
               f"đặt và không nhảy giá qua stop, nên số R thật sẽ xấu hơn.")
        if ky_vong < -0.25 and len(ds) >= 20:
            cau += " Ở mức lỗ này và cỡ mẫu này, đứng ngoài chế độ đó là quyết định có căn cứ."
        ra.append(_pd(f"che-do:{ma}", "chay-lai", cau, len(ds),
                      {"kyVongR": round(ky_vong, 3), "tyLeThang": round(ty_thang, 1)},
                      che_do=ma))
    return ra


# ── Nguồn 2 · sổ lệnh THẬT ────────────────────────────────────────────────
def _tu_so_that(bo: list) -> list[dict]:
    from . import journal

    ra = []
    perf = journal.performance()
    chung = perf["overall"]

    # Rủi ro có đều không — phát hiện quan trọng nhất của sổ này, và là thứ
    # không bài học lệnh-đơn-lẻ nào nói được.
    if chung.get("riskCv") is not None and chung["count"] >= MAU_TOI_THIEU["so-that"]:
        cv = chung["riskCv"]
        if cv > 0.35:
            cau = (f"Rủi ro mỗi lệnh KHÔNG đều (hệ số biến thiên {cv}) qua {chung['count']} "
                   f"lệnh thật. Khi rủi ro trôi, R không so sánh được giữa các lệnh — "
                   f"đọc con số TIỀN (kỳ vọng {chung['expectancyUsd']:+.2f}/lệnh) chứ đừng "
                   f"đọc R ({chung['expectancyR']:+.3f}R).")
            ra.append(_pd("rui-ro-deu", "so-that", cau, chung["count"],
                          {"riskCv": cv, "expectancyUsd": chung["expectancyUsd"],
                           "expectancyR": chung["expectancyR"]}))
        else:
            ra.append(_pd("rui-ro-deu", "so-that",
                          f"Rủi ro mỗi lệnh ĐỀU (hệ số biến thiên {cv}) qua {chung['count']} "
                          f"lệnh thật — R so sánh được giữa các lệnh.",
                          chung["count"], {"riskCv": cv}))
    else:
        bo.append({"ma": "rui-ro-deu", "nguon": "so-that",
                   "viSao": f"{chung.get('count', 0)} lệnh thật < ngưỡng {MAU_TOI_THIEU['so-that']}"})

    for che_do, p in perf["byRegime"].items():
        if che_do == "UNKNOWN":
            continue
        if p.get("count", 0) < MAU_TOI_THIEU["so-that"]:
            bo.append({"ma": f"that:{che_do}", "nguon": "so-that",
                       "viSao": f"{p.get('count', 0)} lệnh thật < ngưỡng {MAU_TOI_THIEU['so-that']}"})
            continue
        cau = (f"Chế độ {che_do} trên lệnh THẬT: {p['count']} lệnh, thắng {p['winRate']}%, "
               f"tiền {p['totalPnl']:+.2f} ({p['expectancyUsd']:+.2f}/lệnh). Lệnh thật ít "
               f"hơn lệnh chạy lại rất nhiều, nhưng nó có nhảy giá và khớp một phần — "
               f"khi hai nguồn nói khác nhau, nguồn này nói về ĐỘ LỚN.")
        ra.append(_pd(f"that:{che_do}", "so-that", cau, p["count"],
                      {"tyLeThang": p["winRate"], "tienMoiLenh": p["expectancyUsd"]},
                      che_do=che_do))
    return ra


# ── Nguồn 3 · đài quan sát (trader ngoài) ─────────────────────────────────
def _ho_so() -> dict:
    f = DATA_DIR / "trader-ho-so.json"
    if not f.exists():
        return {}
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return {}


def _tu_dai_quan_sat(bo: list) -> list[dict]:
    d = _ho_so()
    if not d:
        bo.append({"ma": "dai-quan-sat", "nguon": "dai-quan-sat",
                   "viSao": "chưa có trader-ho-so.json — đài quan sát chưa chạy lần nào"})
        return []

    ra = []

    # — Chuyên gia theo chế độ —
    for che_do, v in (d.get("chuyenGiaTheoCheDo") or {}).items():
        ds = v.get("chuyenGia") or []
        if not ds:
            bo.append({"ma": f"chuyen-gia:{che_do}", "nguon": "dai-quan-sat",
                       "viSao": f"0 trader đủ mẫu ở chế độ {che_do}"})
            continue
        top = ds[0]
        vong = top.get("soVong") or 0
        if vong < MAU_TOI_THIEU["dai-quan-sat"]:
            bo.append({"ma": f"chuyen-gia:{che_do}", "nguon": "dai-quan-sat",
                       "viSao": f"chuyên gia đầu bảng chỉ {vong} vòng ở chế độ này"})
            continue
        yeu = top.get("hang") in ("BO_QUA", "WEAK")
        cau = (f"Chế độ {che_do}: người giao dịch nhiều nhất trong nhóm quan sát dùng phong "
               f"cách {top.get('phongCach') or '—'}, {vong} vòng, thắng {top.get('tyLeThang')}%, "
               f"lãi {top.get('pnl'):+,.0f}.")
        if yeu:
            cau += (f" NHƯNG điểm chất lượng của người này chỉ {top.get('diemTong')} "
                    f"(hạng {top.get('hang')}) — đây là dữ kiện về PHONG CÁCH nào tồn tại "
                    f"trong chế độ đó, không phải một người đáng bắt chước.")
        if len(ds) < 3:
            cau += (f" Cả chế độ chỉ có {len(ds)} người đủ mẫu, nên chưa so được ai với ai.")
        ra.append(_pd(f"chuyen-gia:{che_do}", "dai-quan-sat", cau, vong,
                      {"phongCach": top.get("phongCach"), "hang": top.get("hang"),
                       "diemTong": top.get("diemTong"), "soUngVien": len(ds)},
                      che_do=che_do, do_tin="THẤP" if (yeu or len(ds) < 3) else None))

    # — Đồng thuận: đầu người và vốn có thể nói ngược nhau —
    dt = d.get("dongThuan") or {}
    dau = (dt.get("theoDauNguoi") or {}).get("phanTramLong")
    von = (dt.get("theoVon") or {}).get("phanTramLong")
    so_vt = dt.get("soViThe") or 0
    if dau is not None and von is not None and so_vt >= 10:
        lech = abs(dau - von)
        if lech >= 25:
            cau = (f"{dt.get('coin')}: {dau:.1f}% số ĐẦU NGƯỜI đang LONG nhưng chỉ "
                   f"{von:.1f}% số VỐN đang LONG, trên {so_vt} vị thế. Đám đông và tiền lớn "
                   f"đang đứng hai phía. Đây là BỐI CẢNH, không phải lệnh: nó nói chỗ đông "
                   f"người ở đâu, không nói ai đúng.")
            ra.append(_pd("dong-thuan-lech", "dai-quan-sat", cau, so_vt,
                          {"phanTramLongDauNguoi": dau, "phanTramLongVon": von}))
        else:
            bo.append({"ma": "dong-thuan-lech", "nguon": "dai-quan-sat",
                       "viSao": f"đầu người và vốn lệch {lech:.1f}% < 25% — chưa đáng nói"})
    else:
        bo.append({"ma": "dong-thuan-lech", "nguon": "dai-quan-sat",
                   "viSao": f"chỉ {so_vt} vị thế đọc được, hoặc thiếu số theo vốn"})

    # — Thời gian giữ: nhóm đỉnh so với nhóm đang lỗ —
    giu: dict[str, list] = defaultdict(list)
    for t in d.get("traders") or []:
        g = (t.get("giaiPhau") or {}).get("phongCach") or {}
        bc = g.get("bangChung") or {}
        h = bc.get("giuTrungVi_gio")
        if h and t.get("nhom"):
            giu[t["nhom"]].append(h)
    if len(giu.get("dinh", [])) >= 1 and len(giu.get("dangLo", []) or giu.get("daChay", [])) >= 1:
        kem = giu.get("dangLo") or giu.get("daChay")
        tb_d = sum(giu["dinh"]) / len(giu["dinh"])
        tb_k = sum(kem) / len(kem)
        n = len(giu["dinh"]) + len(kem)
        cau = (f"Thời gian giữ trung vị: nhóm đỉnh {tb_d:.1f} giờ, nhóm kém {tb_k:.1f} giờ "
               f"— đo trên {n} hồ sơ. Cỡ mẫu này quá nhỏ để kết luận; nó chỉ đủ để đặt câu "
               f"hỏi 'mình đang thoát quá sớm hay quá muộn' chứ không đủ để trả lời.")
        ra.append(_pd("thoi-gian-giu", "dai-quan-sat", cau, n,
                      {"dinh_gio": round(tb_d, 1), "kem_gio": round(tb_k, 1)},
                      do_tin="THẤP"))
    else:
        bo.append({"ma": "thoi-gian-giu", "nguon": "dai-quan-sat",
                   "viSao": "không đủ hồ sơ có giải phẫu ở cả nhóm đỉnh lẫn nhóm kém"})

    # — Bao nhiêu hồ sơ thực sự ĐỌC RA ĐƯỢC GÌ —
    #
    # Đếm hồ sơ có khoá `giaiPhau` thì ra 11/11 và nghe như phủ kín. Nhưng 3 hồ
    # sơ trong đó có `soVong: 0` — khoá tồn tại, bên trong rỗng, vì sàn chặn tần
    # suất giữa chừng. Đếm sự TỒN TẠI của một trường thay vì đếm nội dung của nó
    # là đúng loại phép đo đã từng báo "phủ 100%" khi độ phủ thật là 0%.
    ts = d.get("traders") or []
    co_vong = sum(1 for t in ts if ((t.get("giaiPhau") or {}).get("soVong") or 0) > 0)
    if ts and co_vong < len(ts):
        ra.append(_pd("do-phu-quan-sat", "dai-quan-sat",
                      f"Đài quan sát đọc ra vòng giao dịch của {co_vong}/{len(ts)} hồ sơ "
                      f"({len(ts) - co_vong} hồ sơ rỗng, phần lớn do sàn chặn tần suất). "
                      f"Mọi phát hiện từ nguồn này đứng trên {co_vong} người, không phải "
                      f"{d.get('tongLeaderboard', '?')} người trên bảng xếp hạng.",
                      co_vong, {"docDuocVong": co_vong, "tongHoSo": len(ts)}, do_tin="THẤP"))
    return ra


# ── Nguồn 4 · Champion / Challenger ───────────────────────────────────────
def _tu_chien_luoc(bo: list) -> list[dict]:
    f = DATA_DIR / "chien-luoc.json"
    if not f.exists():
        bo.append({"ma": "champion", "nguon": "chien-luoc", "viSao": "chưa có chien-luoc.json"})
        return []
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
    except (ValueError, OSError) as e:
        bo.append({"ma": "champion", "nguon": "chien-luoc", "viSao": f"đọc hỏng: {e}"})
        return []

    ch = d.get("champion") or {}
    kq = ch.get("ketQua") or {}
    # Khoá theo KẾT QUẢ, không theo `tham`. Bản đầu gác trên `tham` và vì champion
    # hiện tại có `tham: {}` (chiến lược luật, không tham số), nó vứt đi phát hiện
    # quan trọng nhất trong cả hệ: chiến lược đang cầm quyền có kỳ vọng ÂM.
    # Cửa lọc mà chặn nhầm thứ đáng giá nhất thì tệ hơn không có cửa.
    if not kq.get("so"):
        bo.append({"ma": "champion", "nguon": "chien-luoc",
                   "viSao": "champion chưa có kết quả chạy lại"})
        return []

    ra = []
    ky_vong = kq.get("kyVongR")
    so = kq["so"]
    cau = (f"Chiến lược đang cầm quyền ({ch.get('ma')} · {ch.get('ten')}): kỳ vọng "
           f"{ky_vong:+.3f}R qua {so} lệnh chạy lại, thắng {kq.get('tyLeThang')}%, "
           f"hệ số lợi nhuận {kq.get('heSoLoiNhuan')}, sụt giảm tối đa "
           f"{kq.get('sutGiamToiDaPct')}%.")
    if ky_vong is not None and ky_vong < 0:
        cau += (" KỲ VỌNG ÂM: chính bản chiến lược đang chạy đã lỗ trên lịch sử. "
                "Mọi lệnh nó đề xuất đều xuất phát từ đây — kết quả tốt lẻ tẻ là "
                "phương sai, không phải bằng chứng ngược lại.")
    ra.append(_pd("champion", "chien-luoc", cau, so,
                  {"kyVongR": ky_vong, "tyLeThang": kq.get("tyLeThang"),
                   "heSoLoiNhuan": kq.get("heSoLoiNhuan"),
                   "sutGiamToiDaPct": kq.get("sutGiamToiDaPct"), "tham": ch.get("tham")}))

    chuoi = kq.get("chuoiThuaDaiNhat")
    if chuoi:
        ra.append(_pd("chuoi-thua", "chien-luoc",
                      f"Chuỗi thua dài nhất đo được: {chuoi} lệnh liên tiếp qua {so} lệnh "
                      f"chạy lại. Đây mới là con số quyết định mức rủi ro mỗi lệnh — không "
                      f"phải kỳ vọng. Sống sót qua chuỗi thua là điều kiện để kỳ vọng có "
                      f"cơ hội hiện ra.",
                      so, {"chuoiThuaDaiNhat": chuoi}))

    kt = kq.get("khopTroi")
    if kt is not None:
        ra.append(_pd("khop-troi", "chien-luoc",
                      f"Khớp trội {kt}: chênh lệch giữa điểm TRONG mẫu và điểm NGOÀI mẫu "
                      f"của bộ tham số cầm quyền. Càng lớn thì nó càng học thuộc quá khứ "
                      f"thay vì học quy luật — và phần học thuộc sẽ không lặp lại.",
                      so, {"khopTroi": kt}))

    ly_do = kq.get("theoLyDoThoat") or {}
    if ly_do and sum(ly_do.values()):
        tong = sum(ly_do.values())
        sl = ly_do.get("SL", 0)
        if sl / tong >= 0.6:
            ra.append(_pd("cua-thoat", "chien-luoc",
                          f"{sl}/{tong} lệnh chạy lại thoát bằng STOP LOSS "
                          f"({sl / tong * 100:.0f}%), chỉ {ly_do.get('TP', 0)} lệnh chạm mục "
                          f"tiêu. Tỉ lệ này nói vấn đề nằm ở điểm VÀO hoặc ở chỗ đặt stop, "
                          f"không nằm ở mục tiêu.",
                          tong, {"theoLyDoThoat": ly_do}))
    return ra


# ── Lò ────────────────────────────────────────────────────────────────────
def chung_cat() -> dict:
    """Chưng lại toàn bộ phát hiện. Ghi đè sạch kho, không cộng dồn."""
    bo: list[dict] = []
    ra: list[dict] = []
    for ten, ham in (("chay-lai", _tu_chay_lai), ("so-that", _tu_so_that),
                     ("dai-quan-sat", _tu_dai_quan_sat), ("chien-luoc", _tu_chien_luoc)):
        try:
            ra.extend(ham(bo))
        except Exception as e:  # một nguồn hỏng không được kéo sập cả lò
            bo.append({"ma": ten, "nguon": ten, "viSao": f"nguồn lỗi: {type(e).__name__}: {e}"})

    store.write_all(store.PHAT_HIEN, ra)
    theo_nguon: dict[str, int] = defaultdict(int)
    for p in ra:
        theo_nguon[p["nguon"]] += 1
    return {"soPhatHien": len(ra), "theoNguon": dict(theo_nguon),
            "daBo": bo, "soDaBo": len(bo), "luc": _gio()}


def doc(che_do_key: str | None = None, che_do: str | None = None,
        gioi_han: int = 8) -> list[dict]:
    """Phát hiện hợp chế độ hiện tại trước, phát hiện chung sau.

    Cắt bớt là bắt buộc: nhét mọi phát hiện vào mọi prompt thì phát hiện đúng
    chìm giữa phát hiện lạc đề, đúng lỗi mà `journal.recall()` đã tránh cho bài
    học. Phát hiện chung (không gắn chế độ) luôn được giữ — chúng nói về CÁCH
    ĐỌC SỐ, đúng ở mọi chế độ.
    """
    ds = store.read_all(store.PHAT_HIEN)
    hop = [p for p in ds if p.get("cheDo") and p["cheDo"] in (che_do_key, che_do)]
    chung = [p for p in ds if not p.get("cheDo")]
    # Trong mỗi nhóm, xếp theo BẰNG CHỨNG chứ không theo thứ tự chưng ra. Bản đầu
    # trả về đúng thứ tự các nguồn chạy, nên khi cắt còn 8 câu thì "thời gian giữ
    # đo trên 2 hồ sơ" lọt vào còn "chuỗi thua 8 lệnh liên tiếp qua 44 lệnh" bị
    # cắt. Cắt theo thứ tự ngẫu nhiên là bỏ đi phần đắt nhất mà không ai thấy.
    hang = {"CAO": 0, "VỪA": 1, "THẤP": 2}
    khoa = lambda p: (hang.get(p.get("doTin"), 3), -(p.get("mau") or 0))
    return (sorted(hop, key=khoa) + sorted(chung, key=khoa))[:gioi_han]

# — Ngưỡng cầu dao: chỉ chế độ đã ĐO ĐỦ và lỗ ĐỦ SÂU mới bị ngắt —
CAU_DAO_KY_VONG = -0.25   # R
CAU_DAO_MAU = 30          # lệnh chạy lại


def cau_dao(che_do_key: str | None, che_do: str | None) -> dict | None:
    """Chế độ này đã được ĐO là lỗ đều chưa? Nếu rồi, trả phát hiện đó về.

    Đây là chỗ vòng tuần hoàn KHÉP LẠI. Trước đó phòng huấn luyện đo được
    "TREND_UP|none lỗ đều −0,422R qua 36 lệnh" rồi con số ấy nằm yên trong một
    file JSONL: không ai đọc, không gì đổi, và lượt sau bộ máy lại vào lệnh ở
    đúng chế độ đó. Đo mà không đổi hành vi thì đo để làm gì.

    HAI RÀNG BUỘC, cả hai đều cần thiết:

    **Chỉ dùng ở đường CHẠY THẬT.** `huanluyen.py` không đi qua `loop.py`, nên
    cầu dao không bao giờ chạm vào vòng chạy lại. Để nó chạm vào là tự tạo vòng
    lặp nhìn trước: phát hiện đúc TỪ chạy lại quay lại chặn chính chạy lại, và
    lần chạy sau sẽ ra kết quả đẹp hơn mà không có gì thật sự tốt lên.

    **Ngưỡng phải cao.** Chặn cả một chế độ là quyết định lớn, và bằng chứng chỉ
    đến từ lệnh mô phỏng. Đòi ≥30 lệnh (gấp ba ngưỡng phát hiện) và kỳ vọng dưới
    −0,25R. Ngưỡng thấp hơn thì một chế độ xui vài lệnh cũng đủ bị khai tử vĩnh
    viễn, mà chế độ bị khai tử thì không bao giờ tự thu thêm dữ liệu để cãi lại.
    """
    for pd in store.read_all(store.PHAT_HIEN):
        if pd.get("nguon") != "chay-lai" or pd.get("doTin") != "CAO":
            continue
        if pd.get("cheDo") not in (che_do_key, che_do):
            continue
        ky_vong = (pd.get("so") or {}).get("kyVongR")
        if ky_vong is not None and ky_vong <= CAU_DAO_KY_VONG and (pd.get("mau") or 0) >= CAU_DAO_MAU:
            return pd
    return None
