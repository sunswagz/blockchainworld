"""CHẨN ĐOÁN HỆ — bệnh của cả bộ máy, không phải bệnh của một ty.

`bac/chan_doan.py` hỏi *"ty này phát hiện có chuẩn không"*. File này hỏi một
câu khác hẳn: *"cả bộ máy có đang chuyển tiền tới chỗ đáng không"*.

Hai câu ấy tách nhau, và phải tách. Một ty có thể phát hiện rất giỏi mà cả
hệ vẫn không rót được đồng nào vì trần cảng đặt quá chặt — chẩn ở tầng ty
sẽ không bao giờ thấy chuyện đó, vì nhìn từ trong ty thì mọi thứ đều ổn.

## Nguồn: cái phễu và sổ cái, không phải cảm giác

    Sổ Đăng Ký  →  phễu: phát hiện → cổng ty → rủi ro tổng → cấp vốn
    Sổ Cái      →  tiền thật đã đi đâu, và bao nhiêu quyết định bị từ chối
    Cầu Dao     →  ngắt bao nhiêu lần, vì gì

## Hai luật giữ nguyên từ tầng ty

**Chưa đủ mẫu thì không chẩn.** Với 7 tờ trình thì mọi tỉ lệ đều là tiếng
ồn, và một cỗ máy tự vặn theo tiếng ồn sẽ *trông như* đang tiến bộ.

**Không núm nào chạm tới an toàn.** `NUT_TRUNG_UONG` cố ý KHÔNG chứa ngưỡng
cầu dao, `batBuocDoDuocSucChua`, hay `tiLeDuTru`. Ba thứ ấy không phải
ngưỡng hiệu năng — chúng là câu "ta không biết đủ để rót tiền". Cho vòng
tiến hoá nới chúng ra là dạy nó rằng đường ngắn nhất tới điểm cao là tắt
đèn báo, và nó sẽ tìm ra ngay.

Ở đây khác tầng ty một điểm quan trọng: **file này chỉ ĐỀ XUẤT, không vặn**.
Đổi tham số phân bổ là đổi cách chia tiền giữa các ty — không có băng nào
chạy lại được chuyện đó (chạy lại một quyết định phân bổ đòi biết cả những
cơ hội đã KHÔNG được cấp diễn biến ra sao, mà chúng không được mở nên không
có kết cục). Không A/B được thì không tự nhận được. Người duyệt.
"""
from __future__ import annotations

from dataclasses import dataclass, field

#: Dưới ngần này tờ trình đã phát hiện thì không chẩn gì cả.
TOI_THIEU_TO_TRINH = 50

#: Qua cổng ty rồi mà rủi ro tổng chặn quá tỉ lệ này là hai tầng đang cãi nhau.
NGUONG_TONG_CHAN = 0.90

#: Dùng vốn dưới ngần này suốt mà vẫn có tờ trình bị từ chối vì trần = trần
#: đặt sai chỗ, không phải hết tiền.
NGUONG_DUNG_VON_THAP = 0.15

#: Hỏng chân B quá tỉ lệ này trên số lần thực thi là legging có hệ thống.
NGUONG_PHANG_GAP = 0.10

#: Một MÃ từ chối chiếm quá phần này của mọi lần từ chối thì nó là thủ phạm
#: chính, không phải một trong nhiều nguyên nhân. Đặt ở 0,25 chứ không phải
#: 0,5: với năm sáu mã từ chối cùng hoạt động, một mã chiếm một phần tư đã
#: là áp đảo — đợi nó chiếm quá nửa là đợi một tình huống hiếm.
NGUONG_MA_AP_DAO = 0.25

#: Số lần từ chối tối thiểu để một mã được coi là thủ phạm. Ba lần trên tổng
#: bốn lần là 75% mà chẳng nói lên gì.
TOI_THIEU_TU_CHOI = 20

#: Núm Trung Ương được phép ĐỀ XUẤT vặn. So với `bac/tien_hoa.NUT_VAN`, đây
#: là tầng phân bổ chứ không phải tầng phát hiện.
NUT_TRUNG_UONG = {
    "ruiRoTong.tranMotCang":       {"min": 0.10, "max": 0.60},
    "ruiRoTong.tranMotTy":         {"min": 0.15, "max": 0.80},
    "ruiRoTong.tranMotCoHoi":      {"min": 0.02, "max": 0.35},
    "ruiRoTong.tranMotTaiSanRong": {"min": 0.02, "max": 0.30},
    "ruiRoTong.ruiRoToiDa":        {"min": 0.30, "max": 0.85},
    "ruiRoTong.tinCayToiThieu":    {"min": 0.30, "max": 0.90},
    "phanBo.toiDaSoViThe":         {"min": 3,    "max": 40},
}

#: Cố ý KHÔNG vặn được. Liệt kê tường minh để phép kiểm bắt được nếu ai đó
#: lỡ đưa một trong số chúng vào `NUT_TRUNG_UONG`.
CUA_AN_TOAN_HE = (
    "nguongCauDao.lechDongHoToiDaGiay",
    "nguongCauDao.soCangChetToiDa",
    "nguongCauDao.tuoiToiDaGiay",
    "nguongCauDao.sutVonToiDaPct",
    "ruiRoTong.batBuocDoDuocSucChua",
    "ruiRoTong.tranTongDungVon",
    "phanBo.tiLeDuTru",
)

#: Mỗi lượt dịch tối đa bấy nhiêu phần giá trị hiện tại.
BUOC_TOI_DA = 0.25


@dataclass
class TrieuChungHe:
    ma: str
    nang: int                    # 1 nhẹ · 2 vừa · 3 nặng
    moTa: str
    bangChung: dict = field(default_factory=dict)
    nutGoiY: list[str] = field(default_factory=list)

    def tom_tat(self) -> dict:
        return {"ma": self.ma, "nang": self.nang, "moTa": self.moTa,
                "bangChung": self.bangChung, "nutGoiY": list(self.nutGoiY)}


def chan_doan_he(anh: dict) -> list[TrieuChungHe]:
    """Đọc `TrungUong.anh_chup()`, trả về bệnh ĐO ĐƯỢC của cả bộ máy."""
    ra: list[TrieuChungHe] = []
    sdk = anh.get("soDangKy") or {}
    pheu = sdk.get("pheu") or {}
    dm = anh.get("danhMuc") or {}
    cd = anh.get("cauDao") or {}
    tt = anh.get("thucThi") or {}
    sc = anh.get("soCai") or {}

    pd = int(pheu.get("phatHien") or 0)
    qua_ty = int(pheu.get("DUYET_TY") or 0)
    qua_rr = int(pheu.get("DUYET_RUI_RO") or 0)
    da_cap = int(pheu.get("DA_CAP_VON") or 0)

    # ── 0. một tầng đi tắt — nặng nhất, và không cần đủ mẫu ──────────────
    sai = int(sdk.get("soChuyenSai") or 0)
    if sai:
        ra.append(TrieuChungHe(
            "di-tat", 3,
            f"{sai} lần chuyển trạng thái KHÔNG hợp lệ bị chặn — có tầng nào "
            f"đó đang gọi thẳng tầng dưới, bỏ qua tầng trên nó. Đây là lỗi "
            f"kiến trúc, không phải lỗi tham số; đừng vặn núm nào cả.",
            {"soChuyenSai": sai, "ganNhat": sdk.get("chuyenSaiCuoi")}))

    # ── 0b. legging — cũng không chờ đủ mẫu, vì mỗi lần là tiền thật ─────
    so_phien = int(tt.get("soPhien") or 0)
    so_gap = int(tt.get("soPhangGap") or 0)
    if so_phien and so_gap / so_phien > NGUONG_PHANG_GAP:
        ra.append(TrieuChungHe(
            "legging-he-thong", 3,
            f"{so_gap}/{so_phien} lần thực thi phải ĐÓNG GẤP vì chân B không "
            f"khớp. Đây không phải xui — nó nói cỡ lệnh đang lớn hơn sổ lệnh "
            f"chịu được, hoặc hai cảng lệch nhau quá nhiều.",
            {"soPhangGap": so_gap, "soPhien": so_phien,
             "tiLe": so_gap / so_phien},
            ["ruiRoTong.tranMotCoHoi"]))

    # ── 1. chưa đủ mẫu — chẩn đầu tiên, và thường là chẩn duy nhất ───────
    if pd < TOI_THIEU_TO_TRINH:
        ra.append(TrieuChungHe(
            "thieu-to-trinh", 1,
            f"mới {pd} tờ trình — chưa đủ để chẩn tầng phân bổ. Chạy thêm, "
            f"đừng vặn.",
            {"phatHien": pd, "canToiThieu": TOI_THIEU_TO_TRINH}))
        return ra

    # ── 2. hai tầng rủi ro cãi nhau ──────────────────────────────────────
    if qua_ty and (qua_ty - qua_rr) / qua_ty > NGUONG_TONG_CHAN:
        ra.append(TrieuChungHe(
            "tong-chan-het", 2,
            f"{qua_ty} tờ qua cổng ty nhưng chỉ {qua_rr} qua Rủi Ro Tổng "
            f"({(qua_rr / qua_ty):.0%}). Hai tầng rủi ro đang nói ngược nhau: "
            f"hoặc cổng ty quá lỏng, hoặc trần tổng quá chặt.",
            {"quaCongTy": qua_ty, "quaRuiRoTong": qua_rr,
             "tiLe": qua_rr / qua_ty},
            ["ruiRoTong.ruiRoToiDa", "ruiRoTong.tinCayToiThieu"]))

    # ── 3. tiền nằm không, mà vẫn từ chối vì trần ────────────────────────
    ti_le_dung = float(dm.get("tiLeDungVon") or 0.0)
    if (ti_le_dung < NGUONG_DUNG_VON_THAP and qua_rr > 0
            and da_cap < qua_rr):
        ra.append(TrieuChungHe(
            "tran-dat-sai-cho", 2,
            f"dùng vốn mới {ti_le_dung:.0%} mà vẫn có tờ trình qua Rủi Ro "
            f"Tổng rồi không được cấp. Vốn nằm không KHÔNG phải vì hết tiền — "
            f"một trần nào đó đang chặn trước khi tiền cạn.",
            {"tiLeDungVon": ti_le_dung, "quaRuiRoTong": qua_rr,
             "daCapVon": da_cap},
            ["ruiRoTong.tranMotCang", "ruiRoTong.tranMotTy",
             "ruiRoTong.tranMotCoHoi"]))

    # ── 3b. TRẦN VỊ THẾ là thủ phạm chính ───────────────────────────────
    # Đọc MÃ, không dò chuỗi: `phan_bo.ly_do()` đặt mã đứng đầu mỗi câu đúng
    # để tầng này nhận ra được. Dò `"vị thế"` trong một câu có số nhúng bên
    # trong là dựng một mối nối gãy ngay lần đầu ai đó sửa câu chữ.
    #
    # Vì sao đáng có riêng một triệu chứng: `tran-dat-sai-cho` chỉ nổ khi
    # dùng vốn THẤP, mà trần vị thế chặn ở lúc vốn đã dùng gần hết — 12 vị
    # thế ăn hết tiền rồi thì tỉ lệ dùng vốn cao, và bệnh này núp ngay dưới
    # một con số trông rất khoẻ.
    dem: dict[str, int] = {}
    khong_ma = 0
    for h in ((anh.get("pheuDayDu") or {}).get("theoHo") or []):
        for x in (h.get("lyDoTuChoi") or []):
            so_x = int(x.get("so") or 0)
            ma_ly = _ma_ly_do(str(x.get("lyDo") or ""))
            if ma_ly is None:
                # Câu KHÔNG mang mã: hoặc là bản ghi cũ (trước 29/08 mọi lý
                # do đều là câu trần), hoặc một tầng khác chưa mang kỷ luật
                # mã sang. Không đếm vào mẫu số — chia cho một mẫu số có cả
                # thứ mình không phân loại nổi là tự pha loãng chính mình,
                # và cái loãng ấy giấu đúng thủ phạm ta đang tìm.
                khong_ma += so_x
                continue
            dem[ma_ly] = dem.get(ma_ly, 0) + so_x
    tong_tc = sum(dem.values())
    if tong_tc >= TOI_THIEU_TU_CHOI:
        ma_top, so_top = max(dem.items(), key=lambda kv: kv[1])
        phan = so_top / tong_tc
        if ma_top == "tran-vi-the" and phan >= NGUONG_MA_AP_DAO:
            ra.append(TrieuChungHe(
                "tran-vi-the-chan", 2,
                f"{so_top}/{tong_tc} lần từ chối ({phan:.0%}) là vì ĐỦ SỐ VỊ "
                f"THẾ, không phải vì hết tiền hay vì rủi ro. Trần ấy đặt ra "
                f"khi người phải tự theo dõi từng chân; nay mỗi vòng đều có "
                f"kế toán tự chạy, nên nó đang chặn nhiều hơn nó bảo vệ.",
                {"maTuChoi": ma_top, "so": so_top, "tongTuChoi": tong_tc,
                 "phan": phan, "dem": dem, "soKhongMa": khong_ma},
                ["phanBo.toiDaSoViThe"]))

    # ── 4. cấp vốn xong mà không mở được ─────────────────────────────────
    da_mo = int(pheu.get("DA_MO") or 0)
    if da_cap >= 10 and da_mo / da_cap < 0.5:
        ra.append(TrieuChungHe(
            "cap-roi-khong-mo", 2,
            f"{da_cap} tờ được cấp vốn nhưng chỉ {da_mo} mở được vị thế. Vốn "
            f"đã bị giữ chỗ cho những thứ không thành — đó là vốn chết, và "
            f"nó không hiện ra ở bất kỳ dòng lãi lỗ nào.",
            {"daCapVon": da_cap, "daMo": da_mo}))

    # ── 5. cầu dao ngắt liên miên ────────────────────────────────────────
    so_ngat = int(cd.get("soLanNgat") or 0)
    if so_ngat >= 5:
        ra.append(TrieuChungHe(
            "cau-dao-ngat-nhieu", 2,
            f"cầu dao đã ngắt {so_ngat} lần. Ngắt nhiều không phải dấu hiệu "
            f"cầu dao quá nhạy — nó là dấu hiệu môi trường chạy không ổn "
            f"định. Sửa môi trường, đừng nới ngưỡng.",
            {"soLanNgat": so_ngat,
             "dangNgat": bool(cd.get("dangNgat")),
             "lyDo": cd.get("lyDo")}))

    # ── 6. lỗ có hệ thống ở một ty ───────────────────────────────────────
    for ma, so in (sc.get("laiLoTheoTy") or {}).items():
        try:
            v = float((so or {}).get("laiLoUsd"))
        except (TypeError, ValueError):
            continue
        if v < 0:
            ra.append(TrieuChungHe(
                "ty-lo", 2,
                f"ty {ma} đang âm {abs(v):.2f} USD trên sổ cái. Đây là số đã "
                f"ghi sổ, không phải ước tính.",
                {"chienLuoc": ma, "laiLoUsd": v},
                ["ruiRoTong.tranMotTy"]))

    if not ra:
        ra.append(TrieuChungHe(
            "khoe", 1,
            "không triệu chứng nào vượt ngưỡng. Đứng yên là một kết quả hợp "
            "lệ, và là kết quả thường gặp nhất.",
            {"phatHien": pd, "daCapVon": da_cap,
             "tiLeDungVon": ti_le_dung}))
    return ra


@dataclass
class DeXuatHe:
    nut: str
    tu: float
    den: float
    vi: str                      # mã triệu chứng đẻ ra đề xuất này

    def tom_tat(self) -> dict:
        return {"nut": self.nut, "tu": self.tu, "den": self.den, "vi": self.vi}


def _ma_ly_do(cau: str) -> str | None:
    """`"tran-vi-the: đã đủ 12…"` → `"tran-vi-the"`. Không có mã → `None`.

    Nhận mã bằng HÌNH DẠNG, không bằng danh sách: chữ thường, số, gạch nối,
    không dấu cách. Danh sách thì mỗi lần thêm một mã lại phải nhớ sửa hai
    chỗ, và chỗ quên sửa sẽ im lặng biến mã mới thành «không phân loại
    được».

    Câu trần trả `None` chứ không trả chính nó: một câu không phải một mã,
    và để nó lọt vào bảng đếm là để một câu dài trở thành «thủ phạm chính»
    chỉ vì nó lặp lại nguyên văn.
    """
    dau = cau.split(":", 1)[0].strip()
    # Không có bẫy ĐỘ DÀI ở đây, dù bản đầu có: mọi câu trần đều mang dấu
    # cách hoặc chữ hoa nên phép soát hình dạng đã loại chúng rồi, và đột
    # biến gỡ bẫy độ dài KHÔNG phép kiểm nào giết được. Một nhánh không phép
    # kiểm nào giết được thì hoặc thiếu phép kiểm, hoặc thừa nhánh — ở đây
    # là thừa, nên gỡ.
    if not all(k.islower() or k.isdigit() or k == "-" for k in dau):
        return None
    return dau if any(k.isalpha() for k in dau) else None


def de_xuat(trieu: list[TrieuChungHe], cau_hinh: dict) -> list[DeXuatHe]:
    """Từ triệu chứng ra đề xuất vặn — **chỉ đề xuất, không vặn**.

    Trả về nhiều nhất MỘT đề xuất, từ triệu chứng nặng nhất. Cùng lý do với
    tầng ty: vặn hai núm rồi thấy khá lên thì không biết núm nào có công.
    """
    for t in sorted(trieu, key=lambda x: -x.nang):
        if t.ma in ("thieu-to-trinh", "khoe", "di-tat"):
            continue             # ba cái này không vặn được bằng núm
        for nut in t.nutGoiY:
            khuon = NUT_TRUNG_UONG.get(nut)
            if khuon is None:
                continue
            hien = _lay(cau_hinh, nut)
            if hien is None:
                continue
            # Hướng: bệnh "chặn quá nhiều" thì nới ra, bệnh "legging" thì
            # siết vào. Bước có trần, và không bao giờ ra ngoài khuôn.
            noi = t.ma in ("tong-chan-het", "tran-dat-sai-cho",
                           "tran-vi-the-chan")
            buoc = abs(hien) * BUOC_TOI_DA or (khuon["max"] - khuon["min"]) * 0.1
            moi = hien + buoc if noi else hien - buoc
            moi = max(khuon["min"], min(khuon["max"], moi))
            if abs(moi - hien) < 1e-9:
                continue         # đã chạm biên, núm này hết đường
            if isinstance(khuon["min"], int) and isinstance(khuon["max"], int):
                moi = round(moi)
                if moi == hien:
                    continue
            return [DeXuatHe(nut, hien, moi, t.ma)]
    return []


def _lay(cau_hinh: dict, duong: str):
    """`"ruiRoTong.tranMotCang"` → giá trị, hoặc None nếu không có."""
    o = cau_hinh
    for phan in duong.split("."):
        if not isinstance(o, dict) or phan not in o:
            return None
        o = o[phan]
    return o if isinstance(o, (int, float)) and not isinstance(o, bool) else None
