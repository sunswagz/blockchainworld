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
    "mau-gia": 15,       # một mẫu biểu đồ dưới 15 lần xuất hiện chưa nói lên gì
    "do-khung": 500,     # hình học đo trên hàng nghìn điểm vào, ngưỡng cao theo
    "nhieu-cho": 20,     # lệnh ngoài mẫu mỗi chợ — cùng ngưỡng với cửa duyệt
    # Lệnh ngoài mẫu GỘP mọi chợ. Ngưỡng riêng vì nó trả lời câu hỏi khác:
    # "nhieu-cho" hỏi «chợ NÀY có nói được gì không», còn cái này hỏi «bộ luật
    # này, chạy khắp nơi, được bao nhiêu». Một setup hiếm không bao giờ đủ 20
    # lệnh ở MỘT chợ, nhưng 45 lệnh trải 8 chợ vẫn là 45 lệnh — và trải rộng
    # còn khó khớp trội hơn là dồn một chỗ.
    "nhieu-cho-gop": 40,
    # Sàn để một chợ được vào phép gộp. Dưới mức này thì con số của chợ đó là
    # nhiễu thuần, và gộp nhiễu vào vẫn ra nhiễu — chỉ là nhiễu có vẻ nhiều mẫu.
    "nhieu-cho-san": 3,
    "gia-thuyet": 1,     # một hướng đã hỏng là một hướng đã hỏng, không cần lặp lại
    "bo-pha": 20,        # lệnh ở lượt phá gốc
    # Lệnh của phép đo hướng. Thấp vì nó không kết luận về lợi thế — nó chỉ
    # nói ra rằng phép đo và bản chạy thật đang đo hai thứ khác nhau, và câu
    # đó đúng ngay cả với ít lệnh.
    "do-huong": 20,
    # Lệnh trong một lát của lò luyện. Bảng lò gộp nhiều chợ nên số lệnh lớn;
    # ngưỡng ở đây canh cái ĐÁNG ĐỌC chứ không canh cái đáng tin.
    "lo-luyen": 50,
}


def _khung_hien_tai() -> str:
    """Khung chính đang cấu hình — cũng là khung mà kho chạy lại vừa được đúc."""
    from .config import CONFIG
    return CONFIG["timeframes"]["primary"]


def _gio() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def _pd(ma, nguon, cau, mau, so=None, che_do=None, do_tin=None, khung=None) -> dict:
    """Một phát hiện. `khung` là khung thời gian nó được ĐO TRÊN.

    Thiếu trường này là một cái bẫy đã sập một lần: phát hiện «TREND_UP|none lỗ
    đều −0,422R» đo trên khung 1h, và khi bản chạy thật chuyển sang 4h thì cầu
    dao vẫn lấy nó ra chặn — cùng tên chế độ, khác hẳn thị trường. Bot sẽ đứng
    im ở đúng chế độ mà bằng chứng 4h nói là được, và không có gì báo sai.

    `None` = phát hiện không phụ thuộc khung (kích thước vị thế, mẫu số rủi ro,
    kết quả âm đã lưu). Những cái đó vẫn áp cho mọi khung.
    """
    return {
        "ma": ma, "nguon": nguon, "cheDo": che_do, "cau": cau,
        "mau": mau, "doTin": do_tin or _do_tin(nguon, mau),
        "khung": khung, "so": so or {}, "luc": _gio(),
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
    # Gom theo (KHUNG, chế độ). Gom theo mình chế độ là trộn hai thị trường khác
    # hẳn nhau dưới một cái tên — và bài học 1h sẽ đi chặn lệnh 4h.
    # `khung=None` là bài học đúc TRƯỚC khi thêm trường này; giữ lại làm bối
    # cảnh nhưng không bao giờ cho cầu dao dùng.
    g: dict[tuple, list] = defaultdict(list)
    for l in store.read_all(store.LESSONS_CHAY_LAI):
        g[(l.get("khung"), l.get("regimeKey") or l.get("regime") or "?")].append(l)

    for (khung, ma), ds in sorted(g.items(), key=lambda x: (str(x[0][0]), x[0][1])):
        if ma == "?":
            continue
        if len(ds) < MAU_TOI_THIEU["chay-lai"]:
            bo.append({"ma": f"che-do:{khung or 'khung?'}:{ma}", "nguon": "chay-lai",
                       "viSao": f"{len(ds)} lệnh < ngưỡng {MAU_TOI_THIEU['chay-lai']}"})
            continue
        rs = [l.get("rMultiple") or 0 for l in ds]
        ky_vong = sum(rs) / len(rs)
        thang = sum(1 for r in rs if r > 0)
        ty_thang = thang / len(ds) * 100

        # Chỉ phát biểu khi hiệu ứng đủ rõ. Kỳ vọng ±0,1R trên vài chục lệnh là
        # tiếng ồn, và một câu chắc nịch về tiếng ồn còn tệ hơn im lặng.
        if abs(ky_vong) < 0.1:
            bo.append({"ma": f"che-do:{khung or 'khung?'}:{ma}", "nguon": "chay-lai",
                       "viSao": f"kỳ vọng {ky_vong:+.3f}R quá gần 0 — chưa phải hiệu ứng"})
            continue

        huong = "LỖ ĐỀU" if ky_vong < 0 else "ăn được"
        cau = (f"Chế độ {ma} (khung {khung or 'không rõ'}): {huong} — "
               f"kỳ vọng {ky_vong:+.3f}R, thắng {ty_thang:.1f}% "
               f"qua {len(ds)} lệnh CHẠY LẠI. Đây là phát biểu về CẤU TRÚC (chế độ nào "
               f"hợp chiến lược này), không phải về ĐỘ LỚN: lệnh chạy lại khớp đúng giá "
               f"đặt và không nhảy giá qua stop, nên số R thật sẽ xấu hơn.")
        if ky_vong < -0.25 and len(ds) >= 20:
            cau += " Ở mức lỗ này và cỡ mẫu này, đứng ngoài chế độ đó là quyết định có căn cứ."
        ra.append(_pd(f"che-do:{khung or 'khung?'}:{ma}", "chay-lai", cau, len(ds),
                      {"kyVongR": round(ky_vong, 3), "tyLeThang": round(ty_thang, 1)},
                      che_do=ma, khung=khung))
    return ra


# ── Nguồn 2 · sổ lệnh THẬT ────────────────────────────────────────────────
def _tu_so_that(bo: list) -> list[dict]:
    from . import journal

    ra = []
    perf = journal.performance()
    chung = perf["overall"]
    # Lệnh đóng KỸ THUẬT phải hiện ra, không nằm im ngoài bảng: chúng không nói
    # về chiến lược nhưng có làm đổi số dư, và người đọc cần biết chênh lệch ấy
    # từ đâu ra. Một lệnh kỹ thuật vừa làm kỳ vọng biểu kiến đi từ −13,60 lên
    # −6,83 mỗi lệnh.
    kt = perf.get("kyThuat") or {}
    if kt.get("so"):
        ra.append(_pd("lenh-ky-thuat", "so-that",
                      f"{kt['so']} lệnh đóng KỸ THUẬT ({', '.join(kt.get('lyDo') or [])}) "
                      f"với {kt['tien']:+.2f} đô — KHÔNG tính vào kỳ vọng chiến lược "
                      f"vì chúng nói về hệ thống chứ không về chiến lược. Tiền vẫn "
                      f"vào tài khoản thật, nên tổng số dư và tổng lãi/lỗ chiến lược "
                      f"lệch nhau đúng ngần ấy.",
                      kt["so"], {"tien": kt["tien"]}))
    trades = store.read_all(store.TRADES)
    bai_hoc, _ = journal._phu_soat_lai(store.read_all(store.LESSONS))

    # Rủi ro có đều không — phát hiện quan trọng nhất của sổ này, và là thứ
    # không bài học lệnh-đơn-lẻ nào nói được.
    if chung.get("riskCv") is not None and chung["count"] >= MAU_TOI_THIEU["so-that"]:
        cv = chung["riskCv"]
        if cv > 0.35:
            cau = (f"Rủi ro mỗi lệnh KHÔNG đều (hệ số biến thiên {cv}) qua {chung['count']} "
                   f"lệnh thật. Khi rủi ro trôi, R không so sánh được giữa các lệnh — "
                   f"đọc con số TIỀN (kỳ vọng {chung['expectancyUsd']:+.2f}/lệnh) chứ đừng "
                   f"đọc R ({chung['expectancyR']:+.3f}R).")
            # CŨ hay ĐANG XẢY RA — hai chuyện khác nhau, và câu trên nói y hệt cho
            # cả hai. Đo được: cv 0,357 trên 40 lệnh, nhưng gần hết nằm ở 3 lệnh
            # ngày 19/08 có cùng riskPct 0,5 mà số tiền gấp 2,5× — đúng lỗi MẪU SỐ
            # (tính trên vốn giấy thay vì tiền mua được) đã sửa từ lâu. 20 lệnh gần
            # nhất có cv 0,02.
            #
            # Khác biệt này đổi hẳn việc phải làm: lệch CŨ nghĩa là R vẫn đọc được
            # cho phần gần đây và chỉ cần cẩn thận khi gộp cả sổ; lệch ĐANG XẢY RA
            # nghĩa là có một chỗ hỏng phải tìm ngay.
            gan = [t.get("riskAmount") for t in trades[-20:] if t.get("riskAmount")]
            if len(gan) >= 10:
                tb = sum(gan) / len(gan)
                cv_gan = (sum((x - tb) ** 2 for x in gan) / len(gan)) ** 0.5 / tb if tb else None
                if cv_gan is not None and cv_gan <= 0.35:
                    cau += (f" NHƯNG {len(gan)} lệnh GẦN NHẤT có hệ số biến thiên "
                            f"{cv_gan:.3f} — chỗ lệch nằm ở phần CŨ của sổ, không phải "
                            f"đang xảy ra. R vẫn đọc được cho phần gần đây; cẩn thận "
                            f"khi gộp cả sổ.")
                elif cv_gan is not None:
                    cau += (f" Và {len(gan)} lệnh gần nhất vẫn lệch ({cv_gan:.3f}) — "
                            f"đây là chuyện ĐANG XẢY RA, có một chỗ hỏng phải tìm.")
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
            bo.append({"ma": f"that:khung?:{che_do}", "nguon": "so-that",
                       "viSao": f"{p.get('count', 0)} lệnh thật < ngưỡng {MAU_TOI_THIEU['so-that']}"})
            continue
        # Lệnh KHÔNG khai khung phải được ĐẾM, không được lọc bỏ. Bản trước lọc
        # chúng ra (`and t.get("khung")`), nên một lệnh 4h mới là đủ để tập còn
        # đúng {"4h"} và cả 40 lệnh cũ không rõ khung bị dán nhãn "4h" — trong
        # khi câu vẫn đọc "41 lệnh". Lần thứ sáu của cùng một lỗi, bắt được lúc
        # nó chưa kịp xảy ra: hai bên môi giới mới ghi khung từ commit trước, sổ
        # thật thì toàn lệnh cũ, nên bẫy sập ngay ở lệnh thật kế tiếp.
        khung_ds = {t.get("khung") for t in trades
                    if (t.get("regimeAtEntry") or "UNKNOWN") == che_do}
        khung = (next(iter(khung_ds))
                 if len(khung_ds) == 1 and None not in khung_ds else None)
        cau = (f"Chế độ {che_do} trên lệnh THẬT: {p['count']} lệnh, thắng {p['winRate']}%, "
               f"tiền {p['totalPnl']:+.2f} ({p['expectancyUsd']:+.2f}/lệnh). Lệnh thật ít "
               f"hơn lệnh chạy lại rất nhiều, nhưng nó có nhảy giá và khớp một phần — "
               f"khi hai nguồn nói khác nhau, nguồn này nói về ĐỘ LỚN.")
        # Khung lấy TỪ CHÍNH các lệnh, không từ cấu hình hiện tại: sổ có thể
        # chứa lệnh của khung cũ, và gán nhãn khung mới lên chúng là đúng loại
        # lỗi đã sập một lần với bài học chạy lại.
        doi_cl = sum(1 for l in bai_hoc
                     if l.get("change_strategy") and l.get("regime") == che_do)
        if doi_cl:
            cau += (f" Và {doi_cl} bài học từ chính các lệnh này ĐÒI ĐỔI CHIẾN LƯỢC.")
        ra.append(_pd(f"that:{khung or 'khung?'}:{che_do}", "so-that", cau, p["count"],
                      {"tyLeThang": p["winRate"], "tienMoiLenh": p["expectancyUsd"],
                       "tongTien": p["totalPnl"], "soDoiChienLuoc": doi_cl},
                      che_do=che_do, khung=khung))
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

    # Mã mang "khung?" chứ không mang khung: người trong nhóm quan sát giao dịch
    # trên khung của HỌ, và dữ liệu không nói khung nào. Đây không phải chỗ thiếu
    # sót chờ vá — nó là điều vĩnh viễn không biết được, nên phải khai vĩnh viễn.
    # Cầu dao không bao giờ ngắt dựa trên phát hiện mang "khung?".
    # — Chuyên gia theo chế độ —
    for che_do, v in (d.get("chuyenGiaTheoCheDo") or {}).items():
        ds = v.get("chuyenGia") or []
        if not ds:
            bo.append({"ma": f"chuyen-gia:khung?:{che_do}", "nguon": "dai-quan-sat",
                       "viSao": f"0 trader đủ mẫu ở chế độ {che_do}"})
            continue
        top = ds[0]
        vong = top.get("soVong") or 0
        if vong < MAU_TOI_THIEU["dai-quan-sat"]:
            bo.append({"ma": f"chuyen-gia:khung?:{che_do}", "nguon": "dai-quan-sat",
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
        ra.append(_pd(f"chuyen-gia:khung?:{che_do}", "dai-quan-sat", cau, vong,
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
    khung_cl = kq.get("khung")
    if kq.get("cho"):
        cau += f" (đo trên {kq['cho']})"
    ra.append(_pd("champion", "chien-luoc", cau, so,
                  {"kyVongR": ky_vong, "tyLeThang": kq.get("tyLeThang"),
                   "heSoLoiNhuan": kq.get("heSoLoiNhuan"), "cho": kq.get("cho"),
                   "sutGiamToiDaPct": kq.get("sutGiamToiDaPct"), "tham": ch.get("tham")},
                  khung=khung_cl))

    chuoi = kq.get("chuoiThuaDaiNhat")
    if chuoi:
        ra.append(_pd("chuoi-thua", "chien-luoc",
                      f"Chuỗi thua dài nhất đo được: {chuoi} lệnh liên tiếp qua {so} lệnh "
                      f"chạy lại. Đây mới là con số quyết định mức rủi ro mỗi lệnh — không "
                      f"phải kỳ vọng. Sống sót qua chuỗi thua là điều kiện để kỳ vọng có "
                      f"cơ hội hiện ra.",
                      so, {"chuoiThuaDaiNhat": chuoi}, khung=khung_cl))

    kt = kq.get("khopTroi")
    if kt is not None:
        ra.append(_pd("khop-troi", "chien-luoc",
                      f"Khớp trội {kt}: chênh lệch giữa điểm TRONG mẫu và điểm NGOÀI mẫu "
                      f"của bộ tham số cầm quyền. Càng lớn thì nó càng học thuộc quá khứ "
                      f"thay vì học quy luật — và phần học thuộc sẽ không lặp lại.",
                      so, {"khopTroi": kt}, khung=khung_cl))

    # — Đấu trường: các bộ luật đã đem ra thi và kết quả —
    #
    # Một challenger thua là tin về challenger đó. NHIỀU challenger khác hẳn nhau
    # cùng thua là tin về thứ chúng dùng CHUNG, và đó mới là tin đáng nhớ.
    thu = [c for c in (d.get("challengers") or []) if (c.get("ketQua") or {}).get("so")]
    if len(thu) >= 2:
        thua = [c for c in thu if (c["ketQua"].get("kyVongR") or 0) <= 0]
        ten = " · ".join(f"{c['ma']} {c['ketQua'].get('kyVongR')}R/{c['ketQua']['so']} lệnh"
                         for c in thu)
        if len(thua) == len(thu):
            ra.append(_pd("dau-truong", "chien-luoc",
                          f"Đã đem {len(thu)} bộ luật KHÁC HẲN NHAU ra đấu ngoài mẫu và cả "
                          f"{len(thu)} đều kỳ vọng âm ({ten}), cùng với champion "
                          f"{ky_vong:+.3f}R. Điểm vào khác nhau hoàn toàn mà kết quả cùng âm "
                          f"⇒ vấn đề nằm ở thứ chúng dùng CHUNG (cách đặt stop, mục tiêu, "
                          f"khung thời gian), không nằm ở lúc bấm nút vào lệnh.",
                          sum(c["ketQua"]["so"] for c in thu) + so,
                          {"soThu": len(thu), "soThua": len(thua)}))
        else:
            tot = max(thu, key=lambda c: c["ketQua"].get("kyVongR") or -99)
            ra.append(_pd("dau-truong", "chien-luoc",
                          f"{len(thu)} bộ luật đã đấu ngoài mẫu ({ten}); tốt nhất là "
                          f"{tot['ma']} với {tot['ketQua'].get('kyVongR')}R qua "
                          f"{tot['ketQua']['so']} lệnh. Đọc kèm cỡ mẫu — cửa duyệt đòi ≥20 "
                          f"lệnh ngoài mẫu vì dưới ngần đó mọi con số là nhiễu.",
                          tot["ketQua"]["so"], {"totNhat": tot["ma"]}))

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
                          tong, {"theoLyDoThoat": ly_do}, khung=khung_cl))
    return ra


# ── Nguồn 5 · mẫu giá kinh điển, đã đem đo ────────────────────────────────
def _tu_mau_gia(bo: list) -> list[dict]:
    """Mười ba mẫu biểu đồ kinh điển, đo trên chính cây nến bot sẽ giao dịch.

    Đây là nguồn DUY NHẤT trong lò mà kết quả gần như toàn âm — và chính vì thế
    nó đáng nhớ nhất. Không có nó, bộ não gặp một cái vai-đầu-vai sẽ mang theo
    niềm tin mặc định "mẫu này đúng 83%" học từ sách, và không gì trong hệ thống
    cãi lại được.
    """
    f = DATA_DIR / "mau-gia.json"
    if not f.exists():
        bo.append({"ma": "mau-gia", "nguon": "mau-gia",
                   "viSao": "chưa chạy scripts/do-mau-gia.py --ghi lần nào"})
        return []
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
    except (ValueError, OSError) as e:
        bo.append({"ma": "mau-gia", "nguon": "mau-gia", "viSao": f"đọc hỏng: {e}"})
        return []

    # BỘ DÒ HỎNG phải tới được bộ não, không chỉ ra màn hình lúc chạy tay.
    #
    # Một bộ dò ném lỗi cho ra 0 lần xuất hiện; bảng vẫn đủ dòng, vẫn có cỡ mẫu.
    # "Mẫu này hiếm" và "bộ dò mẫu này hỏng" đọc giống hệt nhau, và chỉ một
    # trong hai là sự thật về thị trường.
    loi = d.get("loiDo") or {}
    if loi:
        bo.append({"ma": "mau-gia-bo-do-hong", "nguon": "mau-gia",
                   "viSao": (f"{len(loi)} bộ dò ném lỗi trong lượt đo gần nhất "
                             f"({sorted(loi)}) — số lần xuất hiện của chúng "
                             f"đang THIẾU, đừng đọc như «mẫu hiếm»")})
    ds = [m for m in (d.get("mau") or []) if m.get("duMau")]
    thieu = [m for m in (d.get("mau") or []) if not m.get("duMau")]
    for m in thieu:
        bo.append({"ma": f"mau:{m['ten']}", "nguon": "mau-gia",
                   "viSao": f"{m['so']} lần xuất hiện < ngưỡng {d.get('toiThieu')}"})
    if not ds:
        return []

    ra = []
    tong = sum(m["so"] for m in ds)
    am = [m for m in ds if m["kyVongR"] <= 0]
    # SỐ CHỢ vào câu. "45.000 nến khung 4h" và "45.000 nến khung 4h trên 15 chợ"
    # là hai mức bằng chứng khác hẳn: một chợ dài chỉ là một quan sát kéo dài,
    # còn 15 chợ độc lập là thứ khớp trội khó bịa ra. Thiếu con số ấy thì đúng
    # cái làm phép đo đáng tin lại là thứ không được nói.
    n_cho = len(d.get("cho") or [])
    noi = (f"{d.get('nen')} nến khung {d.get('khung') or 'không rõ'}"
           + (f" trên {n_cho} chợ độc lập" if n_cho > 1
              else (f" của {(d.get('cho') or ['chợ không rõ'])[0]}" if n_cho
                    else " (chợ KHÔNG RÕ — kho đo cũ, chưa khai chợ)")))
    ra.append(_pd("mau-gia-tong", "mau-gia",
                  f"{len(ds)} mẫu giá kinh điển đã đem đo trên {noi} "
                  f"({tong} lần xuất hiện, đã gộp trùng): {len(am)}/{len(ds)} có kỳ vọng ÂM "
                  f"sau phí, dùng đúng điểm vào/stop/mục tiêu mà chính mẫu khai. "
                  f"Mẫu giá ở đây là BỐI CẢNH để đọc, không phải tín hiệu để bấm.",
                  tong, {"soMau": len(ds), "soAm": len(am), "soCho": n_cho},
                  khung=d.get("khung")))

    # PHẠM VI đi kèm TỪNG câu, không chỉ câu tổng.
    #
    # "NẾN_TRONG_TĂNG: −0,184R qua 5.126 lần" là phát hiện cỡ mẫu lớn thứ ba
    # trong kho, và nó không nói đo ở khung nào, chợ nào. Câu tổng có nói, nhưng
    # ba câu này được đọc RIÊNG — chúng vào prompt riêng, lên bảng riêng, và
    # được trích dẫn riêng.
    pv = (f" (đo trên {noi})" if noi else "")

    # Mẫu tệ nhất — cái đáng nhớ hơn mẫu tốt nhất, vì nó là cái sẽ bị dùng nhầm
    xau = min(ds, key=lambda m: m["kyVongR"])
    ra.append(_pd("mau-gia-xau", "mau-gia",
                  f"{xau['ten']}{pv}: kỳ vọng {xau['kyVongR']:+.3f}R qua {xau['so']} lần, "
                  f"thắng {xau['tyLeThang']}%, MFE trung vị chỉ {xau['mfeTrungVi']}R — "
                  f"một nửa số lần nó còn không đi nổi {xau['mfeTrungVi']}R về phía mình "
                  f"trước khi kết thúc. Thấy mẫu này thì đừng coi là lý do vào lệnh.",
                  xau["so"], {"ten": xau["ten"], "kyVongR": xau["kyVongR"]},
                  khung=d.get("khung")))

    # Mẫu hay bị đọc sai nhất: thắng NHIỀU mà vẫn lỗ vì RR dưới 1
    hay = [m for m in ds if m["tyLeThang"] >= 45 and m["kyVongR"] < 0 and m["rrTrungBinh"] < 1]
    if hay:
        m = max(hay, key=lambda x: x["so"])
        ra.append(_pd("mau-gia-rr-thap", "mau-gia",
                      f"{m['ten']}{pv}: thắng {m['tyLeThang']}% và chạm đích {m['chamDich']}% — "
                      f"nghe rất tốt — nhưng kỳ vọng vẫn {m['kyVongR']:+.3f}R qua {m['so']} lần, "
                      f"vì luật đặt mục tiêu kinh điển của nó cho RR chỉ {m['rrTrungBinh']}. "
                      f"Đích gần hơn cả stop thì thắng bao nhiêu cũng không đủ.",
                      m["so"], {"ten": m["ten"], "rr": m["rrTrungBinh"],
                                "tyLeThang": m["tyLeThang"]}, khung=d.get("khung")))
    return ra


def _quang_khung(ket: dict) -> str:
    """Cảnh báo khi các khung trong bảng phủ những QUÃNG khác nhau.

    Bảng hình học so các khung với nhau, mà chúng phủ những quãng hoàn toàn
    khác: 5m có 42 ngày (07–08/2026) còn 1d có 1499 ngày (2022–2026). Kết luận
    "khung càng dài càng gần hoà vốn" vì thế có thể là kết luận về BỐN NĂM so
    với BỐN MƯƠI HAI NGÀY.

    Không sửa được bằng cách tải thêm — 5m phủ 1499 ngày là 431.000 nến. Cái
    sửa được là nói ra, để không ai đọc bảng như thể cùng kỳ. Chính bảng này đã
    dẫn tới quyết định đổi khung chạy thật từ 1h sang 4h.
    """
    ng = {}
    for _sym, theo_tf in ket.items():
        for tf, k in (theo_tf or {}).items():
            q = (k or {}).get("quang") or {}
            if q.get("soNgay"):
                ng[tf] = max(ng.get(tf, 0), q["soNgay"])
    if len(ng) < 2:
        return ""
    it, nhieu = min(ng.values()), max(ng.values())
    if nhieu < it * 3:
        return ""
    ds = " · ".join(f"{tf} {n}ng" for tf, n in sorted(ng.items(), key=lambda x: x[1]))
    return (f"CÁC KHUNG KHÔNG PHỦ CÙNG QUÃNG ({ds}), nên bảng này so BỐN NĂM với "
            f"BỐN MƯƠI NGÀY chứ không chỉ so khung với khung. Dùng nó để LOẠI "
            f"khung ngắn — chỗ chi phí ăn hết thì đúng ở mọi quãng — chứ đừng "
            f"xếp hạng mấy khung còn lại. ")

# ── Nguồn 6 · hình học của từng khung thời gian ───────────────────────────
def _tu_do_khung(bo: list) -> list[dict]:
    """Khung nào ĐỠ NỔI mức RR đang đòi — đo bằng hình học, không bằng chiến lược.

    Phát hiện quan trọng nhất mà nguồn này sinh ra: nó tách được "thị trường
    không có lợi thế" khỏi "khung này không đỡ nổi mức RR đó". Trước khi có nó,
    bốn chiến lược cùng thua trên 1h chỉ nói được câu thứ nhất.
    """
    f = DATA_DIR / "do-khung.json"
    if not f.exists():
        bo.append({"ma": "do-khung", "nguon": "do-khung",
                   "viSao": "chưa chạy scripts/do-khung.py --ghi lần nào"})
        return []
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
    except (ValueError, OSError) as e:
        bo.append({"ma": "do-khung", "nguon": "do-khung", "viSao": f"đọc hỏng: {e}"})
        return []

    ket = d.get("ket") or {}
    if not ket:
        return []
    ra = []

    # Xếp hạng khung theo khoảng cách tới hoà vốn ở 2R, gộp mọi coin.
    khoang: dict[str, list] = defaultdict(list)
    diem = 0
    for sym, tfs in ket.items():
        for tf, k in tfs.items():
            v = (k.get("muc") or {}).get("2.0")
            if not v:
                continue
            khoang[tf].append(v["tyLeCham"] - v["hoaVonCanTyLe"])
            diem += k.get("soDiem") or 0
    if not khoang:
        return []

    tb = {tf: sum(xs) / len(xs) for tf, xs in khoang.items()}
    xep = sorted(tb.items(), key=lambda x: -x[1])
    tot, te = xep[0], xep[-1]
    bang = " · ".join(f"{tf} {v:+.1f}đ" for tf, v in xep)
    ra.append(_pd("khung-nao-do-noi", "do-khung",
                  f"Khoảng cách tới hoà vốn ở mục tiêu 2R, đo bằng CÁCH VÀO NGẪU NHIÊN "
                  f"trên {len(ket)} coin ({diem:,} điểm vào): {bang}. Khung càng dài càng "
                  f"gần hoà vốn. Ở {tot[0]} chỉ cần bộ chọn điểm vào thêm {abs(tot[1]):.1f} "
                  f"điểm phần trăm là dương; ở {te[0]} cần thêm {abs(te[1]):.1f} điểm — "
                  f"khoảng cách đó không điểm vào nào lấp nổi. Đây là TRẦN TRÊN lạc quan "
                  f"(khi mục tiêu và stop cùng nằm trong một nến, phần thắng tính cho mục "
                  f"tiêu), nên thực tế còn thấp hơn. "
                  + _quang_khung(ket) +
                  f"ĐỪNG DÙNG CON SỐ NÀY ĐỂ ĐOÁN MỘT BỘ LUẬT SẼ KHÁ LÊN BAO NHIÊU. "
                  f"Nó đo bằng cách vào NGẪU NHIÊN, tức đo cái NỀN của thị trường — "
                  f"không đo phân bố điểm vào của một bộ luật có hướng. Hai thứ khác "
                  f"nhau: bảng này nói 1d chỉ hơn 4h {abs(tb.get('1d', 0) - tb.get('4h', 0)):.1f} "
                  f"điểm phần trăm, mà đo thật thì cùng một champion đi từ −0,047R (4h) "
                  f"lên +0,117R (1d) trên 15 chợ. Bảng này dùng để LOẠI khung (5m thì "
                  f"không cách nào bù nổi), không dùng để xếp hạng mấy khung còn lại.",
                  diem, {"theoKhung": {k: round(v, 1) for k, v in tb.items()},
                         "totNhat": tot[0], "teNhat": te[0]}))

    # Khung ngắn: chi phí cố định ăn hết — nói riêng vì đây là cám dỗ thường trực
    ngan = [tf for tf, v in tb.items() if tf in ("1m", "3m", "5m") and v < -15]
    if ngan:
        ra.append(_pd("khung-ngan-chet-vi-phi", "do-khung",
                      f"Khung {', '.join(ngan)} kém hoà vốn tới "
                      f"{min(tb[t] for t in ngan):.0f} điểm phần trăm ở 2R. Nguyên nhân là "
                      f"chi phí: phí và trượt giá tính theo % GIÁ nên không đổi, còn biên độ "
                      f"mỗi nến thì nhỏ dần theo khung — cùng một khoản phí ăn phần R ngày "
                      f"càng lớn. Không chiến lược nào bù được chỗ đó.",
                      diem, {"khung": ngan}))
    return ra


# ── Nguồn 7 · đấu nhiều chợ ───────────────────────────────────────────────
def _tu_nhieu_cho(bo: list) -> list[dict]:
    """Cùng một bộ luật, đo trên nhiều coin và nhiều khung.

    Phát hiện đáng giá nhất mà nguồn này sinh ra không phải "bộ luật nào tốt" mà
    là **cùng một bộ luật thắng hay thua tuỳ chợ** — thứ chỉ nhìn thấy khi đo hơn
    một chợ, và là thứ phân biệt "có lợi thế" với "khớp với lịch sử của một chợ".
    """
    f = DATA_DIR / "dau-nhieu-cho.json"
    if not f.exists():
        bo.append({"ma": "nhieu-cho", "nguon": "nhieu-cho",
                   "viSao": "chưa chạy dau-chien-luoc.py --cho lần nào"})
        return []
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
    except (ValueError, OSError) as e:
        bo.append({"ma": "nhieu-cho", "nguon": "nhieu-cho", "viSao": f"đọc hỏng: {e}"})
        return []

    cho, ket = d.get("cho") or [], d.get("ket") or {}
    # QUÃNG THỜI GIAN vào câu, ngang hàng với số chợ.
    #
    # "MOCK_RULES_V1 trên 8 chợ, gộp −0,047R" đọc như một sự thật về bộ luật.
    # Nó là sự thật về bộ luật TRONG 150 ngày cuối — vì chuỗi 4h chỉ có 500 ngày
    # nên cửa sổ ngoài mẫu là 150 ngày, trong khi cùng bảng ấy trên 1d là 450
    # ngày. Hai con số trông so được với nhau và không phải.
    q = d.get("quang") or {}
    doan = (f" (dữ liệu {q['tu']} → {q['den']}; ngoài mẫu là ~30% cuối quãng đó)"
            if q.get("tu") else " (QUÃNG THỜI GIAN không rõ — kho đo cũ)")

    if len(cho) < 2 or not ket:
        bo.append({"ma": "nhieu-cho", "nguon": "nhieu-cho",
                   "viSao": f"chỉ {len(cho)} chợ — cần ≥2 mới nói được gì"})
        return []

    ra = []
    for ma, v in ket.items():
        o = [x for x in v.values() if x.get("kyVongR") is not None]
        if len(o) < 2:
            continue
        du = [x for x in o if (x.get("so") or 0) >= MAU_TOI_THIEU["nhieu-cho"]]
        if not du:
            # Không chợ nào đủ mẫu RIÊNG — nhưng cộng lại thì có thể đủ.
            #
            # Cổng cũ đòi mỗi chợ ≥20 lệnh. Với một setup hiếm, điều đó không bao
            # giờ xảy ra dù dữ liệu về bao nhiêu: MOCK_BUNG_NEN_V1 có 45 lệnh
            # trải 8 chợ, nhiều nhất một chợ là 8, nên nó ở mãi trong mục "chưa
            # đủ dữ liệu để nói". Bộ máy đang vứt đi bằng chứng tốt nhất nó có,
            # và vứt một cách IM LẶNG — dòng "chưa đủ mẫu" đọc giống hệt lúc
            # thật sự chưa có gì.
            #
            # 45 lệnh trải 8 chợ độc lập khó khớp trội hơn 45 lệnh dồn một chợ.
            # Cái phải nói kèm là: KHÔNG chợ nào riêng lẻ kết luận được.
            gop = [x for x in o if (x.get("so") or 0) >= MAU_TOI_THIEU["nhieu-cho-san"]]
            n_gop = sum(x["so"] for x in gop)
            if n_gop < MAU_TOI_THIEU["nhieu-cho-gop"]:
                bo.append({"ma": f"cho:{ma}", "nguon": "nhieu-cho",
                           "viSao": (f"mọi chợ dưới {MAU_TOI_THIEU['nhieu-cho']} lệnh, "
                                     f"và gộp lại cũng chỉ {n_gop} < "
                                     f"{MAU_TOI_THIEU['nhieu-cho-gop']}")})
                continue
            kv_g = sum(x["kyVongR"] * x["so"] for x in gop) / n_gop
            _ktg = _khoang_tin([x["kyVongR"] for x in gop])
            d_g = sum(1 for x in gop if x["kyVongR"] > 0)
            ra.append(_pd(
                f"cho-gop:{ma}", "nhieu-cho",
                f"{ma}{doan}: KHÔNG chợ nào đủ {MAU_TOI_THIEU['nhieu-cho']} lệnh ngoài mẫu "
                f"để nói riêng, nhưng GỘP {len(gop)} chợ được {n_gop} lệnh: kỳ vọng "
                f"{kv_g:+.3f}R, dương ở {d_g}/{len(gop)} chợ. Đọc đây là câu về BỘ "
                f"LUẬT chạy khắp nơi, không phải câu về chợ nào cả — và setup thưa "
                f"tới mức này thì mỗi chợ chỉ ~{n_gop // len(gop)} lệnh, nên đừng "
                f"đọc con số của bất kỳ chợ đơn lẻ nào."
                + (f" Khoảng tin 95% theo chợ [{_ktg[0]:+.3f}; {_ktg[1]:+.3f}]"
                   + (" — CHỨA 0." if _ktg[0] <= 0 <= _ktg[1] else ".")
                   if _ktg else ""),
                n_gop, {"kyVongR": round(kv_g, 3), "duong": d_g, "soCho": len(gop),
                        "khoangTin": ([round(v, 3) for v in _ktg] if _ktg else None)}))
            continue
        duong = sum(1 for x in du if x["kyVongR"] > 0)
        tong_lenh = sum(x["so"] for x in du)
        chi = " · ".join(f"{c} {v[c]['kyVongR']:+.3f}R/{v[c]['so']}"
                         for c in cho if c in v and (v[c].get("so") or 0) >= MAU_TOI_THIEU["nhieu-cho"])
        # KỲ VỌNG GỘP theo trọng số số lệnh — con số đáy, và nó thiếu suốt.
        #
        # "dương ở 2/9 chợ" đếm ĐẦU CHỢ, nên một chợ 3 lệnh nặng bằng một chợ
        # 26 lệnh. Câu hỏi thật là "nếu chạy bộ luật này ở mọi chợ thì được bao
        # nhiêu", và đó là trung bình có trọng số. Đo được: champion dương 2/9
        # chợ, gộp lại −0,045R qua 203 lệnh — hai con số cùng hướng, nhưng chỉ
        # con số thứ hai nói ĐỘ LỚN.
        #
        # Gộp R được vì R đã chuẩn hoá theo rủi ro mỗi lệnh nên so được giữa
        # các chợ. Cái KHÔNG gộp được là tiền — mỗi chợ một cỡ vị thế.
        kv_gop = sum(x["kyVongR"] * x["so"] for x in du) / tong_lenh
        _kt = _khoang_tin([x["kyVongR"] for x in du])
        cau = (f"{ma} trên {len(du)} chợ đủ mẫu{doan}: {chi} — dương ở {duong}/{len(du)}, "
               f"kỳ vọng GỘP {kv_gop:+.3f}R qua {tong_lenh} lệnh ngoài mẫu.")
        if _kt:
            cau += (f" Khoảng tin 95% theo chợ [{_kt[0]:+.3f}; {_kt[1]:+.3f}]"
                    + (" — CHỨA 0, chưa phân biệt được với «không có gì»."
                       if _kt[0] <= 0 <= _kt[1] else "."))
        # "Dương ở MỌI chợ" chỉ có nghĩa khi có NHIỀU chợ. Với đúng một chợ đủ
        # mẫu, câu đó vẫn đúng về mặt chữ và hoàn toàn rỗng về mặt bằng chứng —
        # mà nó lại là câu mạnh nhất trong cả nguồn này.
        #
        # Đã in ra thật: "dương ở 1/1 … Dương ở MỌI chợ đo được: đây là dấu hiệu
        # của lợi thế thật" — dựa trên đúng 21 lệnh của một coin.
        if duong == len(du) and len(du) >= 3:
            cau += (f" Dương ở MỌI {len(du)} chợ đo được: đây là dấu hiệu của lợi "
                    f"thế thật, không phải khớp với lịch sử của một chợ.")
        elif duong == len(du):
            cau += (f" Dương ở cả {len(du)} chợ — nhưng {len(du)} chợ thì «dương ở "
                    f"mọi chợ» chưa nói được gì; cần ≥3 chợ đủ mẫu mới đọc được "
                    f"như một dấu hiệu.")
        elif duong == 0:
            cau += " Âm ở mọi chợ — vấn đề nằm ở chính bộ luật, không ở chợ nào."
        else:
            cau += (" Thắng chợ này thua chợ kia ⇒ chưa phân biệt được lợi thế với "
                    "may rủi; cần thêm chợ hoặc thêm lệnh trước khi tin.")
        # Hai thước nói ngược nhau thì phải NÓI RA, chứ đừng để người đọc tự
        # chọn thước hợp ý mình.
        if duong > len(du) / 2 and kv_gop <= 0:
            cau += (f" LƯU Ý HAI THƯỚC NGƯỢC NHAU: dương ở đa số chợ nhưng gộp lại "
                    f"vẫn {kv_gop:+.3f}R — mấy chợ thua thua ĐẬM hơn mấy chợ thắng "
                    f"thắng. Đếm đầu chợ đang nói đẹp hơn sự thật.")
        elif duong <= len(du) / 2 and kv_gop > 0:
            cau += (f" LƯU Ý HAI THƯỚC NGƯỢC NHAU: âm ở đa số chợ nhưng gộp lại "
                    f"{kv_gop:+.3f}R — con số dương này đang dựa vào ít chợ; kiểm "
                    f"chợ nào đang gánh trước khi tin.")
        # `kyVongR` vào ô số chứ không chỉ nằm trong câu: mục "đổi DẤU" của bàn
        # giao soi đúng trường này, nên thiếu nó thì một bộ luật lật từ dương
        # sang âm mà không ai được báo.
        ra.append(_pd(f"cho:{ma}", "nhieu-cho", cau, tong_lenh,
                      {"kyVongR": round(kv_gop, 3), "duong": duong,
                       "khoangTin": ([round(v, 3) for v in _kt] if _kt else None),
                       "soCho": len(du)}))
    return ra


# ── Nguồn 8 · sổ giả thuyết (KẾT QUẢ ÂM) ──────────────────────────────────
def _tu_gia_thuyet(bo: list) -> list[dict]:
    """Những gì đã thử VÀ THẤT BẠI — thứ không kho nào khác trong hệ này giữ.

    `phat-hien.jsonl` là ảnh chụp, chỉ giữ cái đang đúng. Nên nếu không có nguồn
    này thì bộ não không có cách nào biết một hướng đã được thử và đã hỏng, và
    nó sẽ đề xuất lại đúng hướng đó.

    Kết quả âm tốn đúng bằng kết quả dương để mua. Khác nhau ở chỗ gần như không
    ai cất chúng.
    """
    from . import so_gia_thuyet as G

    ds = G.doc()
    if not ds:
        bo.append({"ma": "gia-thuyet", "nguon": "gia-thuyet",
                   "viSao": "sổ giả thuyết còn rỗng — chưa khai cái nào"})
        return []

    ra = []
    bac = [g for g in ds if g["phanQuyet"] == "BÁC_BỎ"]
    xac = [g for g in ds if g["phanQuyet"] == "XÁC_NHẬN"]
    mo = [g for g in ds if not g["daChot"]]

    if bac:
        # `bac` theo thứ tự SỔ, tức cũ trước. Cắt đầu danh sách là giữ lại cái
        # cũ nhất và vứt cái vừa đo xong — nên càng học nhiều, bài học mới càng
        # không tới được bộ não. Cắt từ ĐUÔI.
        chi = " · ".join(f"«{g['ma']}» {(g.get('moTa') or '')[:60]}" for g in bac[-4:])
        ra.append(_pd("da-thu-va-hong", "gia-thuyet",
                      f"{len(bac)} hướng ĐÃ THỬ VÀ HỎNG, đừng đề xuất lại: {chi}. "
                      f"Mỗi cái đã tốn một phép đo đầy đủ; tra sổ giả thuyết trước khi "
                      f"dựng phép đo mới.",
                      len(bac), {"maDaBacBo": [g["ma"] for g in bac]}))
        # Ba cái GẦN NHẤT, không phải ba cái đầu sổ: cái vừa đo xong là cái đắt
        # nhất và hợp thời nhất, còn cái cũ đã nằm trong câu tóm tắt ở trên.
        for g in bac[-3:]:
            ra.append(_pd(f"bac-bo:{g['ma']}", "gia-thuyet",
                          f"BÁC BỎ — {g['cauHoi']} Dự đoán lúc chưa biết: {g['duDoan']} "
                          f"Đo được: {g.get('moTa')}. "
                          f"{(g.get('doDuoc') or {}).get('ghiChu') or ''}",
                          (g.get("doDuoc") or {}).get("mau") or 1,
                          {"phanQuyet": "BÁC_BỎ"}))
    if xac:
        ra.append(_pd("da-xac-nhan", "gia-thuyet",
                      f"{len(xac)} hướng đã XÁC NHẬN: "
                      + " · ".join(f"«{g['ma']}»" for g in xac)
                      + ". Xác nhận không phải vĩnh viễn — mỗi cái chỉ đúng trong bối "
                        "cảnh nó được đo, và bối cảnh thì đổi.",
                      len(xac), {"maDaXacNhan": [g["ma"] for g in xac]}))
    if mo:
        ra.append(_pd("dang-mo", "gia-thuyet",
                      f"{len(mo)} giả thuyết ĐÃ KHAI NHƯNG CHƯA CHỐT: "
                      + " · ".join(f"«{g['ma']}»" for g in mo)
                      + ". Khai mà không chốt là cách êm nhất để tránh một câu trả lời "
                        "mình không muốn nghe.",
                      len(mo), {"maDangMo": [g["ma"] for g in mo]}, do_tin="THẤP"))
    return ra


# ── Nguồn 9 · bộ phá ──────────────────────────────────────────────────────
def _tu_bo_pha(bo: list) -> list[dict]:
    """Cần điều kiện tệ tới đâu thì chiến lược mới hỏng."""
    f = DATA_DIR / "bo-pha.json"
    if not f.exists():
        bo.append({"ma": "bo-pha", "nguon": "bo-pha",
                   "viSao": "chưa chạy scripts/bo-pha.py --ghi lần nào"})
        return []
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
    except (ValueError, OSError) as e:
        bo.append({"ma": "bo-pha", "nguon": "bo-pha", "viSao": f"đọc hỏng: {e}"})
        return []

    goc, don = d.get("ket", {}).get("goc") or {}, d.get("ket", {}).get("don") or {}
    n = goc.get("so") or 0
    if not n or goc.get("kyVongR") is None:
        bo.append({"ma": "bo-pha", "nguon": "bo-pha", "viSao": "lượt phá gốc không có lệnh nào"})
        return []

    tat = [k for k, v in don.items() if (v.get("so") or 0) < n * 0.2]
    thua = [k for k, v in don.items()
            if (v.get("so") or 0) >= n * 0.2 and (v.get("kyVongR") or -9) <= 0]
    cau = (f"{d.get('ma')} trên {d.get('cho')}: gốc {goc['kyVongR']:+.3f}R qua {n} lệnh. ")
    if tat:
        cau += (f"TẮT TIẾNG khi {', '.join(tat)} — không phải thua, mà là không còn lệnh "
                f"nào qua nổi cửa RR khi chi phí đội lên. Lợi thế (nếu có) nằm GỌN trong "
                f"giả định chi phí, nên mọi con số dương chỉ đúng chừng nào phí đúng bằng "
                f"mức đã giả định. ")
    if thua:
        cau += f"THUA khi {', '.join(thua)}. "
    if not tat and not thua:
        cau += "Sống qua mọi đòn — hiếm, và đáng đem đi kiểm lại trên chợ khác. "
    ra = [_pd("bo-pha", "bo-pha", cau, n, {"tat": tat, "thua": thua})]
    return ra


# ── Lò ────────────────────────────────────────────────────────────────────
def _khoang_tin(xs: list[float]) -> tuple[float, float] | None:
    """Khoảng tin 95% của trung bình, mỗi CHỢ là một quan sát.

    Không tính theo lệnh: 193 lệnh của 8 chợ tương quan cao không phải 193 quan
    sát độc lập, và khoảng tin theo lệnh sẽ hẹp giả. Câu hỏi ở đây là "bộ luật
    này có chạy được ở chợ khác không" — đơn vị quan sát là một chợ.
    """
    if len(xs) < 3:
        return None
    tb = sum(xs) / len(xs)
    var = sum((x - tb) ** 2 for x in xs) / (len(xs) - 1)
    se = (var / len(xs)) ** 0.5
    return (tb - 1.96 * se, tb + 1.96 * se)

# ── Nguồn 10 · HƯỚNG: nửa LONG và nửa SHORT ──────────────────────────────
def _tu_do_huong(bo: list) -> list[dict]:
    """Bot chạy thật có đánh được thứ mà phép đo đang đo không.

    Sổ lệnh THẬT: 41 LONG, 0 SHORT. Bản chạy lại thì có cả hai. Nghĩa là mọi
    con số về champion đều nói về một chiến lược mà bot không chạy nổi — sàn
    spot chỉ bán được thứ đang giữ.

    Nguồn này tồn tại để bộ não ĐỌC ĐƯỢC khoảng cách đó ở mỗi lượt gọi, chứ
    không phải để đóng nó lại. Con số short đến từ chạy lại: khớp đúng giá đặt,
    không có phí vay, không có rủi ro bị ép đóng.
    """
    f = DATA_DIR / "do-huong.json"
    if not f.exists():
        bo.append({"ma": "huong", "nguon": "do-huong",
                   "viSao": "chưa chạy scripts/do-huong.py --ghi lần nào"})
        return []
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
    except (ValueError, OSError) as e:
        bo.append({"ma": "huong", "nguon": "do-huong", "viSao": f"đọc hỏng: {e}"})
        return []

    hai, mot = d.get("caHai") or {}, d.get("chiLong") or {}
    rl, rs = d.get("riengLong") or {}, d.get("riengShort") or {}
    if hai.get("kyVongR") is None or mot.get("kyVongR") is None:
        bo.append({"ma": "huong", "nguon": "do-huong",
                   "viSao": "chưa đủ lệnh để tách hai nửa"})
        return []
    q = d.get("quang") or {}
    doan = (f", dữ liệu {q['tu']} → {q['den']}" if q.get("tu") else "")
    cau = (f"Chiến lược có HAI NỬA và bot chạy thật chỉ chạy được một. Trên "
           f"{d.get('soCho')} chợ{doan}: cả hai chiều {hai['kyVongR']:+.4f}R qua "
           f"{hai['so']} lệnh · CHỈ LONG {mot['kyVongR']:+.4f}R qua {mot['so']} lệnh")
    if rs.get("kyVongR") is not None and rl.get("kyVongR") is not None:
        cau += (f" · riêng LONG {rl['kyVongR']:+.4f}R/{rl['so']} · riêng SHORT "
                f"{rs['kyVongR']:+.4f}R/{rs['so']}")
    chenh = d.get("chenhDoShort")
    if chenh is not None and chenh > 0:
        cau += (f". Nửa SHORT đóng góp {chenh:+.4f}R mỗi lệnh, và sàn SPOT không "
                f"đánh được nửa đó — nên mọi con số «cả hai chiều» ở các phát hiện "
                f"khác nói về một chiến lược bot không chạy nổi. Đọc chúng bằng "
                f"cột CHỈ LONG.")
    elif chenh is not None:
        cau += (f". Nửa SHORT làm kỳ vọng {chenh:+.4f}R mỗi lệnh — bị chặn ở sàn "
                f"spot lại là may.")
    cau += (" Con số short đến từ CHẠY LẠI: khớp đúng giá đặt, không phí vay, "
            "không rủi ro bị ép đóng — thực tế sẽ xấu hơn.")
    return [_pd("huong", "do-huong", cau, hai["so"],
                {"kyVongR": mot["kyVongR"], "caHaiR": hai["kyVongR"],
                 "chenhDoShort": chenh, "soCho": d.get("soCho")})]

# ── Nguồn 11 · LÒ LUYỆN: nhiều chợ × nhiều lát × nhiều biến thể ──────────
def _tu_lo_luyen(bo: list) -> list[dict]:
    """Kết quả dò tham số theo LÁT thời gian, kèm số lần đã thử.

    Hai câu, và câu thứ hai quan trọng hơn:

    1. Champion dương ở mấy lát trên tổng số lát. Một con số gộp che mất chuyện
       này: đo được ở lượt đầu là MỌI biến thể đều âm ở lát 1 và dương ở lát
       2–4, tức phụ thuộc chế độ thị trường chứ không phải chuyện tham số.

    2. ĐÃ THỬ BAO NHIÊU BIẾN THỂ. Thử 20 rồi lấy cái tốt nhất thì cái tốt nhất
       ấy đẹp lên một phần chỉ vì đã thử 20 lần. Không có con số đó thì "+0,08R"
       là một câu vô nghĩa, và bộ não sẽ đọc nó như một lợi thế.
    """
    f = DATA_DIR / "lo-luyen.json"
    if not f.exists():
        bo.append({"ma": "lo-luyen", "nguon": "lo-luyen",
                   "viSao": "chưa chạy scripts/lo-luyen.py --ghi lần nào"})
        return []
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
    except (ValueError, OSError) as e:
        bo.append({"ma": "lo-luyen", "nguon": "lo-luyen", "viSao": f"đọc hỏng: {e}"})
        return []

    bang = d.get("bang") or []
    cha = next((x for x in bang if x.get("i") == 0), None)
    if not cha or cha.get("kyVongGop") is None:
        bo.append({"ma": "lo-luyen", "nguon": "lo-luyen",
                   "viSao": "chưa có hàng champion trong bảng"})
        return []

    n_thu = d.get("soLanThu") or 0
    kt = cha.get("khoangTin")
    doan_kt = ""
    if kt:
        doan_kt = (f" Khoảng tin 95% [{kt[0]:+.4f}; {kt[1]:+.4f}]"
                   + (" — CHỨA 0, tức chưa phân biệt được với «không có gì»."
                      if cha.get("chuaKhong") else "."))
    lat = " ".join(f"{x:+.2f}" if x is not None else "—" for x in (cha.get("theoLat") or []))
    # KHÔNG GIAN đã dò phải nằm trong câu. "champion −0,15R" của bảng chỉ-LONG
    # và của bảng cả-hai-chiều là hai con số về hai thứ khác nhau, và chênh nhau
    # 0,13R — đem so nhau là sai hẳn. Kho cũ chưa có cờ thì khai KHÔNG RÕ.
    kg = d.get("chiLong")
    doan_kg = (" (CHỈ LONG — đúng không gian sàn spot cho phép)" if kg is True
               else " (cả hai chiều — gồm cả SHORT mà sàn spot KHÔNG đánh được)"
               if kg is False else " (không rõ dò chiều nào — kho đo cũ)")
    ra = [_pd("lo-luyen-champion", "lo-luyen",
              f"Champion đo trên {d.get('soCho')} chợ × {d.get('soLat')} lát thời gian" + doan_kg + ": "
              f"dương {cha['soLatDuong']}/{cha['soLatCo']} lát, gộp "
              f"{cha['kyVongGop']:+.4f}R qua {cha['soLenh']} lệnh. Từng lát: {lat}. "
              f"Lát là quãng thời gian LIÊN TIẾP — dương ở một lát và âm ở lát khác "
              f"nghĩa là kết quả phụ thuộc chế độ thị trường, không phải lợi thế."
              + doan_kt,
              cha["soLenh"], {"kyVongR": cha["kyVongGop"], "soLatDuong": cha["soLatDuong"],
                              "soLat": cha["soLatCo"]})]

    can = (cha.get("soLatCo") or 0) // 2 + 1
    tot = [x for x in bang if x.get("i") and x.get("soLatDuong", 0) >= can
           and (x.get("kyVongGop") or -9) > cha["kyVongGop"]]
    if tot:
        t = tot[0]
        ra.append(_pd("lo-luyen-dan-dau", "lo-luyen",
                      f"{len(tot)}/{n_thu} biến thể tham số{doan_kg} vừa vượt champion vừa dương "
                      f"≥{can}/{cha['soLatCo']} lát. Dẫn đầu: {json.dumps(t.get('tham') or {}, ensure_ascii=False)} "
                      f"— {t['kyVongGop']:+.4f}R qua {t['soLenh']} lệnh, dương "
                      f"{t['soLatDuong']}/{t['soLatCo']} lát. ĐÃ THỬ {n_thu} BIẾN THỂ: "
                      f"cái tốt nhất trong ngần ấy lần thử đẹp lên một phần chỉ vì đã "
                      f"thử ngần ấy lần. Đây là ỨNG VIÊN để đo lại trên chợ chưa dùng, "
                      f"KHÔNG phải một bộ tham số đáng đổi sang.",
                      t["soLenh"], {"kyVongR": t["kyVongGop"], "soLanThu": n_thu,
                                    "soVuot": len(tot)}))
    else:
        ra.append(_pd("lo-luyen-dan-dau", "lo-luyen",
                      f"Thử {n_thu} biến thể tham số, KHÔNG cái nào vừa vượt champion "
                      f"vừa dương ở đa số lát. Đó là một kết quả: chỗ dễ tìm quanh bộ "
                      f"tham số hiện tại đã dò rồi và không có gì.",
                      max(n_thu, 1), {"soLanThu": n_thu, "soVuot": 0}))
    return ra

def chung_cat() -> dict:
    """Chưng lại toàn bộ phát hiện. Ghi đè sạch kho, không cộng dồn."""
    bo: list[dict] = []
    ra: list[dict] = []
    for ten, ham in (("chay-lai", _tu_chay_lai), ("so-that", _tu_so_that),
                     ("dai-quan-sat", _tu_dai_quan_sat), ("chien-luoc", _tu_chien_luoc),
                     ("mau-gia", _tu_mau_gia), ("do-khung", _tu_do_khung),
                     ("nhieu-cho", _tu_nhieu_cho), ("gia-thuyet", _tu_gia_thuyet),
                     ("bo-pha", _tu_bo_pha), ("do-huong", _tu_do_huong),
                     ("lo-luyen", _tu_lo_luyen)):
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
    ds2 = (sorted(hop, key=khoa) + sorted(chung, key=khoa))[:gioi_han]

    # Đánh dấu phát hiện đo trên khung KHÁC. Vẫn đưa vào prompt — nó là bối
    # cảnh có ích — nhưng bộ não phải biết nó không nói về thị trường đang xem.
    nay = _khung_hien_tai()
    ra = []
    for p in ds2:
        k = p.get("khung")
        if k and k != nay:
            p = {**p, "cau": f"[đo trên khung {k}, hiện đang chạy {nay}] " + p["cau"]}
        ra.append(p)
    return ra

# — Ngưỡng cầu dao: chỉ chế độ đã ĐO ĐỦ và lỗ ĐỦ SÂU mới bị ngắt —
CAU_DAO_KY_VONG = -0.25   # R
CAU_DAO_MAU = 30          # lệnh chạy lại


# Ngưỡng cho bằng chứng từ LỆNH THẬT. Thấp hơn hẳn nguồn chạy lại về số lượng
# (10 thay vì 30) vì lệnh thật đắt và hiếm — nhưng đòi thêm hai điều kiện mà
# lệnh mô phỏng không có: tiền thật phải ÂM, và chính hậu kiểm phải đòi đổi
# chiến lược ở đa số lệnh. Lệnh thật có nhảy giá, khớp một phần, phí thật; khi
# nó nói lỗ thì đó là lỗ, không phải một giả định về khớp lệnh.
THAT_TOI_THIEU_LENH = 10
THAT_TY_LE_DOI = 0.5

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
    khung = _khung_hien_tai()
    for pd in store.read_all(store.PHAT_HIEN):
        # BẰNG CHỨNG TỪ LỆNH THẬT cũng được ngắt. Trước đây cầu dao chỉ đọc
        # nguồn `chay-lai`, nên 18 bài học từ lệnh thật đòi đổi chiến lược ở
        # một chế độ mà không có đường nào tới đây — chính bộ não phát hiện ra
        # chỗ đứt đó khi được hỏi "điểm yếu lớn nhất là gì".
        if pd.get("nguon") == "so-that" and pd.get("khung") == khung:
            so = pd.get("so") or {}
            n = pd.get("mau") or 0
            doi = so.get("soDoiChienLuoc") or 0
            if (n >= THAT_TOI_THIEU_LENH and (so.get("tongTien") or 0) < 0
                    and doi >= n * THAT_TY_LE_DOI):
                return pd
            continue
        if pd.get("nguon") != "chay-lai" or pd.get("doTin") != "CAO":
            continue
        if pd.get("cheDo") not in (che_do_key, che_do):
            continue
        # KHUNG PHẢI KHỚP. «TREND_UP|none» trên 1h và trên 4h là hai thị trường
        # khác nhau mang cùng một cái tên; chặn cái này bằng bằng chứng của cái
        # kia là đóng băng bot mà không ai thấy vì sao.
        #
        # Phát hiện cũ không có trường `khung` (đúc trước khi thêm) cũng bị bỏ
        # qua: thà không chặn còn hơn chặn nhầm — cầu dao là thứ DUY NHẤT ở đây
        # tự ý ngăn bot giao dịch, nên nó phải chắc chắn hơn mọi thứ khác.
        if pd.get("khung") != khung:
            continue
        ky_vong = (pd.get("so") or {}).get("kyVongR")
        if ky_vong is not None and ky_vong <= CAU_DAO_KY_VONG and (pd.get("mau") or 0) >= CAU_DAO_MAU:
            return pd
    return None
