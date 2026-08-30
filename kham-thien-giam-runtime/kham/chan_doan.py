"""Chẩn Đoán — tìm chỗ yếu bằng SỐ, trước khi cho model nói câu nào.

Đây là lớp số học thứ NHẤT trong vòng tiến hoá. Vòng của repo này là:

    ĐO  →  [model đề xuất]  →  CỔNG CHẶN

Model bị kẹp giữa hai lớp nó không viết. Bỏ một lớp là còn một cái máy tự
làm hỏng mình.

## Vì sao chẩn đoán phải đi TRƯỚC model

Đưa cả sổ nhật ký cho model rồi hỏi "cải thiện gì" là mời nó bịa. Nó sẽ
tìm ra một mẫu hình trong bất cứ đống số nào — đó là việc nó giỏi, và ở
đây đó là điều tệ nhất.

Nên chỗ này tính sẵn các triệu chứng ĐO ĐƯỢC, và chỉ đưa cho model một
danh sách ngắn kèm bằng chứng. Model không đi tìm bệnh; nó chỉ được hỏi
"trong mấy bệnh đã đo này, nên chữa cái nào trước và bằng cách nào".

## Mỗi triệu chứng phải kèm ba thứ

    do duoc     con số cụ thể, không phải cảm giác
    nguong      mốc để nói "đây là bệnh", đặt trước khi nhìn dữ liệu
    nut van     THAM SỐ nào có thể vặn — nếu không vặn được thì không
                phải việc của vòng tiến hoá, mà là việc của người viết code
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .config import CONFIG
from .so import thong_ke


# ══════════════════════════════════════════════════════════════════════════
#  NÚT VẶN — toàn bộ bề mặt model được phép đụng vào
#
#  Cố ý HẸP. Model không sửa code, không thêm chiến thuật, không đổi kiến
#  trúc. Nó chỉ được đề nghị vặn những con số dưới đây, và mỗi con số có
#  trần cứng mà nó không vượt được dù đề nghị thế nào.
#
#  Vì sao hẹp tới vậy: một đề xuất sửa code thì cổng chặn không kiểm được
#  bằng số. Một đề xuất vặn tham số thì chạy lại băng là biết ngay tốt hơn
#  hay chỉ khác đi. Bề mặt nào không kiểm được bằng số thì không mở.
# ══════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class NutVan:
    duong: str            # "canLoi.netEdgeToiThieu"
    thap: float
    cao: float
    buoc: float
    y: str


NUT_VAN: list[NutVan] = [
    NutVan("canLoi.netEdgeToiThieu", 0.005, 0.060, 0.0025,
           "ngưỡng lợi thế tối thiểu để một cơ hội được coi là đáng làm"),
    NutVan("canLoi.bienAnToan", 0.002, 0.030, 0.001,
           "chỗ trả giá cho những thứ chưa nghĩ ra; nới là tự tin hơn"),
    NutVan("canLoi.sucChuaToiThieu", 10, 200, 5,
           "lô nhỏ nhất đáng vào; nhỏ quá thì phí ăn hết"),
    NutVan("canLoi.xacSuatKhopToiThieu", 0.30, 0.85, 0.05,
           "khớp khó tới đâu thì thôi không đặt"),
    NutVan("khoDoi.giaCapToiDa", 0.960, 0.999, 0.005,
           "giá cặp trần; càng thấp càng kỹ tính khi bù chân"),
    NutVan("khoDoi.giayChoChanHai", 5, 60, 5,
           "chờ chân hai bao lâu trước khi dứt điểm"),
    # Khoá đô cũ nay là khoá RƠI VỀ, không phải khoá đang sống — vặn nó
    # thì không có gì đổi. Một nút vặn không đổi gì là tệ hơn không có
    # nút: vòng tiến hoá vẫn tốn lượt đo nó và vẫn báo "không cải thiện".
    NutVan("khoDoi.phanTramChuaPhongHo", 1, 20, 1,
           "phần trăm vốn được phép nằm trần một chân"),
    NutVan("ruiRo.kellyPhan", 0.05, 0.40, 0.05,
           "phần Kelly; cao là đặt to hơn khi mô hình tự tin"),
    # Mép trên nới 900 → 3600. Lý do: mép cũ BẰNG ĐÚNG giá trị đang dùng,
    # và một cái nút như thế thì không bao giờ tăng được — cái MÉP đang
    # quyết định chứ không phải dữ liệu. `tien-hoa-mo-hinh` đã tự dò ra
    # ngoài dải và khai: tối ưu thật nằm quanh 2.700–3.600s.
    #
    # Đo lại độc lập bằng ba tập tách theo thời gian (20 ngày BTC):
    #
    #      900s  CHỐT 0.15759   ← trần cũ
    #     1800s       0.15742   Δ 95% [-0.001037, +0.000865]
    #     2700s       0.15706   Δ 95% [-0.001459, +0.000761]
    #     3600s       0.15676   Δ 95% [-0.001821, +0.000569]
    #     5400s       0.15660   Δ 95% [-0.002028, +0.000500]
    #
    # Điểm ước lượng cải thiện ĐƠN ĐIỆU qua năm mức, và cận trên của
    # khoảng tin co đều — nhưng MỌI khoảng tin vẫn CHỨA 0. Nên đây KHÔNG
    # phải "đã chứng minh tốt hơn"; nó là "cái lồng đang chặn, và bên
    # ngoài lồng có thứ đáng nhìn".
    #
    # Nới MÉP chứ không đặt GIÁ TRỊ: quyền quyết vẫn ở cổng tiến hoá với
    # ba tập và biên đa so sánh của nó. Tôi gỡ cái lồng, cổng chọn số.
    NutVan("dinhGia.bienDongCuaSoGiay", 60, 3600, 300,
           "cửa sổ ước lượng σ; ngắn thì nhạy, dài thì mượt"),
    NutVan("dinhGia.batDinhToiThieu", 0.005, 0.050, 0.005,
           "sàn bất định; cao là bảo thủ hơn"),
    # Hai nút dưới đây CHẠM THẲNG vào `pUp`, nên chúng chấm được bằng độ
    # chuẩn của dự báo trên kết quả thật, không cần giá chợ. Trước đây
    # chúng không có trong bảng vặn — tức là hai tham số đi thẳng vào
    # công thức mà không ai từng đo xem chúng đặt đúng chưa.
    NutVan("dinhGia.sanNenGiay", 1.0, 15.0, 1.0,
           "sàn cho τ; giây chót thì một tick vẫn lật được kết quả"),
    NutVan("dinhGia.matPhangCanKetQua", 0.005, 0.060, 0.005,
           "kéo p về trong [eps, 1−eps]; không outcome nào đáng giá đúng 0"),
    # Giảm chấn của phép nắn. Thêm vào bảng này thay vì tự chọn một con
    # số mới, vì đã có bằng chứng NGOÀI MẪU và bằng chứng ấy nói "nới
    # được" chứ không nói "nới bao nhiêu":
    #
    #     phần đầu (đã thấy)     thô 5,62 → nắn 2,77 điểm   giảm 51%
    #     phần đuôi (chưa thấy)  thô 6,52 → nắn 4,68 điểm   giảm 28%
    #
    # Khoảng cách 51% với 28% chính là phần khớp quá — đo được. Chọn tay
    # một hệ số từ một lần chia đôi là thay một phỏng đoán bằng một phỏng
    # đoán khác. Để cổng chạy lại quyết, đó là việc nó sinh ra để làm.
    # ── HÀNG RÀO DỰNG RỒI HẠ, cùng ngày 30/08/2026 ────────────────
    #
    # Sáng 30/08 mép dưới bị siết 0,30 → 0,80, vì `do-giam-chan.py` đo
    # được (4 chợ × 20 ngày, tập CHỐT, bootstrap chia khối theo KHUNG,
    # 1.440 khối) rằng so với 0,70 thì 0,30 cho [+0,000539, +0,001005]
    # và 0,50 cho [+0,000207, +0,000440] — TỆ HƠN có ý nghĩa.
    #
    # Chiều 30/08 phép đo ấy HỎNG. `hoc_offline.sigma_tai` nhớ lại theo
    # khoá thiếu MÃ CHỢ, nên trong `tu-nang-cap.cap_du_doan` — thước mà
    # cả hai script kia dùng — ba chợ sau nhận σ của chợ đầu. Đo trên
    # dữ liệu thật: SOL và XRP nhận σ bằng ~40% σ thật của chúng, và
    # 85,5% số mốc lệch quá ±25%.
    #
    # Đo lại sau khi vá, CÙNG script CÙNG tham số: mọi trị 0,30 → 1,00
    # đều cho khoảng tin CHỨA 0. Trục PHẲNG. Kết luận cũ không sống sót.
    #
    # Nên hạ mép về 0,30. Giữ hàng rào là giữ một cái lồng dựng bằng
    # bằng chứng đã rút — và một cái lồng thì im lặng: vòng tiến hoá cứ
    # kết luận "giữ nguyên", nghe như dữ liệu đã nói.
    #
    # KHÔNG trả trị về 0,70: không có bằng chứng nào nói 0,85 tệ hơn,
    # và đổi đi đổi lại theo một trục đã đo là phẳng chỉ thêm nhiễu.
    # Trục phẳng nghĩa là nút này không đáng vặn nữa cho tới khi có
    # THƯỚC KHÁC — thước ở đây là Brier, mà giảm chấn chỉ hiện ra ở chỗ
    # bảng hiệu chỉnh lệch nhiều.
    NutVan("nanLai.heSoGiamChan", 0.30, 1.00, 0.05,
           "đi bao nhiêu phần đường mà bảng hiệu chỉnh chỉ ra"),
]

NUT_THEO_DUONG = {n.duong: n for n in NUT_VAN}


def doc_tham_so(duong: str, goc: dict | None = None) -> float | None:
    d = goc if goc is not None else CONFIG
    for k in duong.split("."):
        if not isinstance(d, dict) or k not in d:
            return None
        d = d[k]
    return d if isinstance(d, (int, float)) else None


def kep(duong: str, gt: float) -> float | None:
    """Kẹp một giá trị vào trần cứng của nút. None nếu không phải nút hợp lệ.

    Đây là chốt chặn cuối: model đề nghị `kellyPhan = 5.0` thì nó thành
    0.40, không thành 5.0. Và model đề nghị vặn một đường không có trong
    bảng thì đề nghị ấy bị bỏ hẳn, không phải bị kẹp.
    """
    n = NUT_THEO_DUONG.get(duong)
    if n is None:
        return None
    gt = max(n.thap, min(n.cao, float(gt)))
    # Bám LƯỚI BƯỚC, và làm tròn theo số chữ số của chính bước.
    #
    # `0.015 - 0.005` trong dấu phẩy động ra `0.009999999999999998`. Con
    # số ấy chảy thẳng vào đề xuất, vào sổ tiến hoá, và nếu cổng nhận thì
    # vào cả `config.json`. Nó không sai về giá trị nhưng nó phá thứ khác:
    # hai lượt đề xuất "cùng một chỗ" lại ra hai chuỗi khác nhau, nên phép
    # nhớ-đã-thử-gì không nhận ra chúng là một.
    thap, buoc = float(n.thap), float(n.buoc)
    if buoc > 0:
        gt = thap + round((gt - thap) / buoc) * buoc
        gt = max(n.thap, min(n.cao, gt))
    # Số chữ số thập phân lấy từ bước, không đặt cứng: bước 0.0025 cần 4
    # chữ số, bước 5 cần 0.
    le = 0
    b = buoc
    while b > 0 and abs(b - round(b)) > 1e-12 and le < 10:
        b *= 10
        le += 1
    return round(gt, le)


# ══════════════════════════════════════════════════════════════════════════
#  TRIỆU CHỨNG
# ══════════════════════════════════════════════════════════════════════════

@dataclass
class TrieuChung:
    ma: str
    nang: int                      # 1 nhẹ · 2 vừa · 3 nặng
    mo_ta: str
    bangChung: dict = field(default_factory=dict)
    nutGoiY: list[str] = field(default_factory=list)

    def tom_tat(self) -> dict:
        return {"ma": self.ma, "nang": self.nang, "moTa": self.mo_ta,
                "bangChung": self.bangChung, "nutGoiY": self.nutGoiY}


def nut_o_mep() -> list[dict]:
    """Nút nào đang nằm ĐÚNG mép dải cho phép.

    Một nút nằm ở mép nghĩa là **cái mép đang quyết định, không phải dữ
    liệu**. Nó có thể vô hại (mép là giới hạn cứng thật, như
    `heSoGiamChan = 1,0` nghĩa là nắn trọn phần đường) hoặc là một cái
    lồng che mất chỗ tốt hơn ở ngoài.

    Đã cắn thật: `dinhGia.bienDongCuaSoGiay` có mép trên BẰNG ĐÚNG giá
    trị đang dùng (900). Một nút như thế không bao giờ tăng được, và
    mọi lượt tiến hoá đều kết luận "giữ nguyên" — nghe như dữ liệu đã
    nói, thật ra là cái lồng đã nói.

    `tien-hoa-mo-hinh` có phát hiện chuyện này, nhưng chỉ khi ai đó chạy
    tay. Đưa ra buồng lái thì nó tự lộ.
    """
    ra = []
    for n in NUT_VAN:
        v = doc_tham_so(n.duong)
        if v is None:
            continue
        try:
            v = float(v)
        except (TypeError, ValueError):
            continue
        ben = None
        if abs(v - float(n.cao)) < 1e-12:
            ben = "trên"
        elif abs(v - float(n.thap)) < 1e-12:
            ben = "dưới"
        if ben:
            ra.append({"duong": n.duong, "giaTri": v, "ben": ben,
                       "thap": float(n.thap), "cao": float(n.cao)})
    return ra

def _benh_mo_hinh(hieuChinh: dict, ra: list) -> None:
    """Bệnh của MÔ HÌNH — đọc thẳng từ bảng hiệu chỉnh, không cần lệnh nào.

    Tách riêng vì nó KHÔNG phụ thuộc sổ kết toán. Trước đây nó nằm sau
    cửa "chưa đủ 20 lệnh thì return", nên một bảng hiệu chỉnh 40.276 mẫu
    — đo được, kiểm được ngoài mẫu — bị vứt đi chỉ vì chưa lệnh nào kết
    toán. Mà "mô hình đoán chuẩn tới đâu" và "bot kiếm được bao nhiêu" là
    hai câu hỏi khác nhau, cần hai bộ dữ liệu khác nhau, và câu đầu trả
    lời được mà không cần chạm vào chợ (`scripts/hoc-tu-binance.py`).
    """
    sai = hieuChinh.get("saiSoTB")
    if sai is not None and sai > 0.06:
        chieu = _chieu_lech(hieuChinh.get("bang") or [])
        ra.append(TrieuChung(
            "mo-hinh-lech", 2,
            f"mô hình lệch trung bình {sai:.3f} so với thực tế, thiên "
            f"{chieu} — bất định đang bị khai quá thấp",
            {"saiSoTB": sai, "chieu": chieu, "tongMau": hieuChinh.get("tongMau")},
            # `nanLai.heSoGiamChan` nằm ĐẦU danh sách vì nó là nút
            # nhắm thẳng vào bệnh này: bảng hiệu chỉnh đã ĐO được mô
            # hình lệch đi đâu, giảm chấn quyết đi bao nhiêu phần
            # đường ấy. Hai nút kia chỉ nới bất định chung chung.
            #
            # Trước bản này nút giảm chấn có mặt trong bảng vặn mà
            # KHÔNG triệu chứng nào trỏ tới, nên người đề xuất tất
            # định không bao giờ với tới được nó — chỉ model mới đề
            # nghị nổi, mà cung này chạy không cần model. Một nút
            # nằm trong bảng mà không ai vặn được thì bằng không có.
            ["nanLai.heSoGiamChan", "dinhGia.batDinhToiThieu",
             "dinhGia.bienDongCuaSoGiay"]))



def chan_doan(ketToan: list[dict], hieuChinh: dict,
              boQua: dict[str, int] | None = None,
              nguonMau: str = "that") -> list[TrieuChung]:
    """Đọc sổ kết toán + sổ hiệu chỉnh, trả về danh sách bệnh ĐO ĐƯỢC.

    `nguonMau` — "that" là lệnh đã đặt và đã kết toán; "chay-lai" là lệnh
    MÔ PHỎNG dựng từ băng ghi. Hai thứ đó không được lẫn vào nhau:

    · lệnh thật mang theo trượt giá thật, khớp một phần thật, chọn lọc
      bất lợi thật — những thứ mô hình khớp lệnh của chạy lại không có;
    · nên một chẩn đoán dựng trên mẫu mô phỏng LẠC QUAN có hệ thống, và
      người đọc phải biết điều đó ngay chỗ đọc, không phải đi tra.

    Vậy vì sao vẫn cho dùng? Vì cỗ máy này có thể chạy hàng tuần mà chưa
    đặt lệnh nào — và lúc đó "chưa đủ để chẩn gì" là câu đúng nhưng vô
    dụng, nó khoá luôn vòng tiến hoá. Mẫu mô phỏng có dán nhãn tốt hơn
    KHÔNG có mẫu, miễn là cái nhãn không bao giờ rơi ra.
    """
    ra: list[TrieuChung] = []
    tk = thong_ke(ketToan)

    # ── chưa đủ dữ liệu thì nói thế, đừng chẩn bừa ───────────────────────
    if tk.get("chuaCo") or tk.get("n", 0) < 20:
        ra.append(TrieuChung(
            "thieu-mau", 1,
            f"mới {tk.get('n', 0)} lệnh đã kết toán — chưa đủ để chẩn gì. "
            f"Chạy thêm, đừng vặn.",
            {"n": tk.get("n", 0), "canToiThieu": 20, "nguonMau": nguonMau}))
        # Nhưng KHÔNG trả về ngay: bệnh của mô hình đọc từ bảng hiệu
        # chỉnh, và bảng ấy dựng được mà không cần một lệnh nào. "Chưa đủ
        # lệnh để chẩn CHIẾN THUẬT" không có nghĩa là "chưa biết gì về MÔ
        # HÌNH".
        _benh_mo_hinh(hieuChinh, ra)
        return ra

    # ── 1. kỳ vọng âm ────────────────────────────────────────────────────
    if tk["kyVong"] < 0:
        ra.append(TrieuChung(
            "ky-vong-am", 3,
            f"kỳ vọng {tk['kyVong']:+.5f}$/lệnh — đang lỗ đều, không phải xui",
            {"kyVong": tk["kyVong"], "n": tk["n"],
             "tiLeThang": tk["tiLeThang"], "tongLaiLo": tk["tongLaiLo"]},
            ["canLoi.netEdgeToiThieu", "canLoi.bienAnToan"]))

    # ── 2. đuôi lệch ─────────────────────────────────────────────────────
    if tk.get("canhBaoDuoi"):
        ra.append(TrieuChung(
            "duoi-lech", 3,
            f"MỘT lần thua lớn nhất xoá {tk['xoaBaoNhieuLanThang']:.0f} lần "
            f"thắng — tỉ lệ thắng {tk['tiLeThang']:.1%} không nói lên an toàn",
            {"thuaLonNhat": tk["thuaLonNhat"], "duoi5pct": tk["duoi5pct"],
             "xoa": tk["xoaBaoNhieuLanThang"]},
            ["ruiRo.kellyPhan", "canLoi.sucChuaToiThieu",
             "khoDoi.phanTramChuaPhongHo"]))

    _benh_mo_hinh(hieuChinh, ra)

    # ── 4. cặp khoá lỗ nhiều ─────────────────────────────────────────────
    khoa = [g for g in ketToan if (g.get("giaCap") or 0) > 1.0]
    if len(khoa) > len(ketToan) * 0.25:
        tb = sum((g["giaCap"] - 1.0) for g in khoa) / len(khoa)
        ra.append(TrieuChung(
            "cap-khoa-lo", 2,
            f"{len(khoa)}/{len(ketToan)} cặp có giá vốn trên $1 — trung bình "
            f"khoá sẵn {tb*100:.2f}¢ mỗi cặp trước khi bàn tới lãi",
            {"soKhoaLo": len(khoa), "tong": len(ketToan), "khoaTrungBinh": tb},
            ["khoDoi.giaCapToiDa", "khoDoi.giayChoChanHai"]))

    # ── 5. đứng ngoài quá nhiều ──────────────────────────────────────────
    if boQua:
        tong_bo = sum(boQua.values())
        thang_cho = sum(v for k, v in boQua.items() if "thang" in k.lower())
        if tong_bo > 0 and thang_cho / tong_bo < 0.5 and tong_bo > 100:
            ra.append(TrieuChung(
                "dung-ngoai", 1,
                f"bỏ qua {tong_bo} lượt mà phần lớn KHÔNG phải vì thang chờ — "
                f"ngưỡng có thể đang quá chặt",
                {"tongBoQua": tong_bo, "viThangCho": thang_cho, "chiTiet": dict(boQua)},
                ["canLoi.netEdgeToiThieu", "canLoi.xacSuatKhopToiThieu"]))

    # ── 6. khoẻ mạnh ─────────────────────────────────────────────────────
    if not ra:
        ra.append(TrieuChung(
            "khoe", 0,
            f"không triệu chứng nào vượt ngưỡng: kỳ vọng {tk['kyVong']:+.5f}, "
            f"{tk['n']} lệnh, đuôi trong hạn",
            {"kyVong": tk["kyVong"], "n": tk["n"]}))
    return ra


def _chieu_lech(bang: list[dict]) -> str:
    """Mô hình đang TỰ TIN QUÁ hay RỤT RÈ QUÁ."""
    tren = duoi = 0
    for h in bang:
        if not h.get("n") or h.get("lech") is None:
            continue
        # ô xác suất cao mà thực tế thấp hơn => tự tin quá
        if h["duDoan"] > 0.5:
            if h["lech"] < 0:
                tren += h["n"]
            else:
                duoi += h["n"]
        else:
            if h["lech"] > 0:
                tren += h["n"]
            else:
                duoi += h["n"]
    if tren > duoi * 1.3:
        return "TỰ TIN QUÁ"
    if duoi > tren * 1.3:
        return "RỤT RÈ QUÁ"
    return "hai chiều lẫn lộn"


def de_bai(trieuChung: list[TrieuChung], thamSoHienTai: dict) -> dict:
    """Gói chẩn đoán thành đề bài cho model. KHÔNG kèm sổ thô.

    Chỉ đưa triệu chứng đã đo, bảng nút vặn kèm trần, và tham số hiện tại.
    Không đưa toàn bộ nhật ký — đưa là mời nó đi tìm mẫu hình trong nhiễu.
    """
    return {
        "trieuChung": [t.tom_tat() for t in
                       sorted(trieuChung, key=lambda x: -x.nang)],
        "thamSoHienTai": thamSoHienTai,
        "nutVanChoPhep": [
            {"duong": n.duong, "thap": n.thap, "cao": n.cao,
             "buoc": n.buoc, "y": n.y} for n in NUT_VAN],
        "luat": [
            "Chỉ được đề nghị vặn các đường trong `nutVanChoPhep`.",
            "Mỗi lượt đề nghị TỐI ĐA 2 nút — vặn nhiều thì không biết nút nào có tác dụng.",
            "Phải nói rõ đề nghị này chữa triệu chứng nào.",
            "Đề nghị sẽ được chạy lại trên băng thật; tốt hơn mới được nhận.",
        ],
    }
