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
#: `cuc` = CAO LÊN thì NỚI RA (+1) hay SIẾT VÀO (−1).
#:
#: Trước lượt này hướng vặn được quyết bằng TÊN BỆNH: bệnh «chặn quá
#: nhiều» thì cộng bước, bệnh khác thì trừ bước. Điều đó chỉ đúng khi mọi
#: núm cùng cực, và chúng KHÔNG cùng cực: `tranMot*` và `ruiRoToiDa` cao
#: lên là nới ra, còn `tinCayToiThieu` cao lên là siết vào.
#:
#: Hậu quả đã nằm sẵn trong bảng: `tong-chan-het` («không cơ hội nào qua
#: cửa») gợi ý hai núm, và núm thứ hai là `tinCayToiThieu`. Khi
#: `ruiRoToiDa` chạm biên trên — tức đúng lúc bệnh nặng nhất — máy quay
#: sang núm thứ hai và NÂNG sàn tin cậy lên, chặn chặt hơn nữa. Chữa bệnh
#: nghẽn bằng cách bóp cổ họng.
#:
#: Và nó hỏng IM LẶNG: bước sau A/B thấy tệ hơn nên trả lại, sổ ghi «trả
#: lại», và một lượt vặn ngược hướng trông y hệt một quyết định thận
#: trọng đúng đắn.
#: Bao nhiêu lần đóng đối chiếu được thì mới dám nói một ty «hứa quá».
#: Dưới ngưỡng này thì con số lệch nói về vài lần đóng chứ không nói về
#: cái ty — và vặn theo nó là vặn theo tiếng ồn.
TOI_THIEU_DOI_CHIEU = 20

#: Lệch bao nhiêu bps mỗi giờ thì gọi là hứa quá. Không đặt 0: mọi phép đo
#: đều có sai số, và một cỗ máy báo bệnh ở lệch 0,001 bps là một cỗ máy
#: báo bệnh mỗi vòng.
NGUONG_HUA_QUA_BPS_GIO = 0.05

#: Đóng trên Vào từ ngưỡng này trở lên thì gọi là CHURN. 0,8 vì một danh
#: mục lành mạnh luôn có một phần vị thế đang mở: đóng bằng 100% số lần
#: vào nghĩa là không còn giữ gì, mà máy đang giữ 74 vị thế.
NGUONG_CHURN = 0.8

#: Dưới ngần này lần vào lệnh thì tỉ lệ đóng/vào là tiếng ồn, không phải
#: một tính chất của ty. Mười, vì một ty mới mở vài vị thế có thể tình cờ
#: đóng hết chúng mà không hề churn.
TOI_THIEU_LAN_VAO = 10

#: Bao nhiêu VỐN-GIỜ mới đủ để nói một ty «hứa quá». 100 USD-giờ là một
#: trăm đô chạy một tiếng — dưới ngần ấy thì tỉ suất năm quy ra từ nó chỉ
#: là tiếng ồn nhân lên 8.760 lần.
TOI_THIEU_VON_GIO = 100.0

#: Hứa cao hơn thực bao nhiêu ĐIỂM PHẦN TRĂM mỗi năm thì mới kêu. Hai
#: điểm, vì lời hứa dựng trên một ảnh chụp thị trường còn thực nhận là
#: trung bình của cả quãng — chúng lệch nhau chút ít là bình thường.
NGUONG_HUA_QUA_DIEM = 2.0

#: Bao nhiêu lần XOAY CHỖ mới đủ để nói lời hứa của nó không đứng vững.
#: Ba mươi lần: dưới ngần ấy thì trung vị số giờ giữ được còn là tiếng ồn,
#: và một lần xoay lẻ giữ ngắn có thể chỉ vì runtime khởi động lại.
TOI_THIEU_LAN_XOAY = 30

#: Vị thế mới phải sống được ít nhất chừng này PHẦN lời hứa. `xoay_cho`
#: cộng trước phần lãi hơn của cả `gioChung` giờ rồi trừ phí đổi một lần;
#: nếu vị thế mới chỉ sống 1% quãng ấy thì 99% lời hứa chưa bao giờ tới,
#: mà phí thì đã trả đủ. Để 0,20 — sống được một phần năm lời hứa là còn
#: cãi được; dưới nữa thì không.
NGUONG_SONG_TREN_HUA = 0.20

NUT_TRUNG_UONG = {
    "ruiRoTong.tranMotCang":       {"min": 0.10, "max": 0.60, "cuc": +1},
    "ruiRoTong.tranMotTy":         {"min": 0.15, "max": 0.80, "cuc": +1},
    "ruiRoTong.tranMotCoHoi":      {"min": 0.02, "max": 0.35, "cuc": +1},
    "ruiRoTong.tranMotTaiSanRong": {"min": 0.02, "max": 0.30, "cuc": +1},
    "ruiRoTong.ruiRoToiDa":        {"min": 0.30, "max": 0.85, "cuc": +1},
    "ruiRoTong.tinCayToiThieu":    {"min": 0.30, "max": 0.90, "cuc": -1},
    # Sàn NET mỗi giờ: cao lên là siết. Núm này vào bảng cùng lượt với
    # triệu chứng `hua-qua-he` — nó là núm duy nhất chữa đúng bệnh «hứa
    # nhiều hơn thực nhận»: đòi thêm ngần ấy khoảng hở trước khi nhận.
    "ruiRoTong.netMoiGioToiThieuBps": {"min": 0.0, "max": 5.0, "cuc": -1},
    # Trần trên nới từ 40 lên 300 ngày 29/08. Lý do đặt ra con số 40 là
    # «quá nhiều vị thế thì không theo dõi nổi» — lý do của thời chưa có
    # kế toán tự động, mà nay mỗi vòng đều kế toán từng vị thế và khai ra
    # cái nào không kế toán được. Người theo dõi đã được thay bằng máy
    # theo dõi, nên ràng buộc cũ hết hiệu lực; giữ nó là để một lý do đã
    # chết tiếp tục chặn tiền.
    "phanBo.toiDaSoViThe":         {"min": 3,    "max": 300, "cuc": +1},
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

#: SÀN của bước, theo bề rộng khuôn — xem `bac/tien_hoa.SAN_BUOC_KHUON`.
#: Không có sàn thì núm nào đang ở gần 0 sẽ đứng yên mãi mãi.
SAN_BUOC_KHUON = 0.05


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

    # ── 6. lỗ có hệ thống ở một ty — đọc CỘT CHIẾN LƯỢC, không đọc gộp ──
    #
    # Con số gộp trộn hai thứ khác hẳn nhau, và trộn theo hướng nguy hiểm.
    # Đo 30/08 trên máy sống:
    #
    #     lending.rate_rotation.v1   gộp −82,26   CHIẾN LƯỢC  +2,03
    #     amm.fee_farming.v1         gộp  −1,32   CHIẾN LƯỢC  +1,88
    #
    # Hai ty ấy đang KIẾM được tiền bằng chính việc của mình. Cái kéo con
    # số gộp xuống là phí VÀO LỆNH trả 289 lần và 50 lần — mà phần lớn
    # những lần vào lệnh ấy không do chiến lược sinh ra: vị thế mô phỏng
    # phải mở lại sau mỗi lần runtime khởi động lại. Đó là chi phí VẬN
    # HÀNH, chuyện của người vận hành.
    #
    # Đọc con số gộp thì vòng tiến hoá kết luận «bốn ty đang lỗ» và đề
    # xuất duy nhất của nó là siết `tranMotTy` 0,5 → 0,375: rút vốn khỏi
    # đúng những ty đang làm ra tiền, vì một buổi chiều deploy nhiều lần.
    # `lai_lo_tach_khoan()` sinh ra để chặn đúng cái đọc nhầm này, và
    # người đọc nhầm hoá ra là chính vòng tiến hoá.
    tach = anh.get("laiLoTachKhoan") or {}
    for ma, so in (sc.get("laiLoTheoTy") or {}).items():
        try:
            gop = float((so or {}).get("laiLoUsd"))
        except (TypeError, ValueError):
            continue
        t6 = tach.get(ma) or {}
        cl = t6.get("laiLoChienLuocUsd")
        # Chưa tách được thì đọc gộp, và NÓI RA là đang đọc gộp — im lặng
        # rơi về số gộp là quay lại đúng lỗi vừa sửa.
        if cl is None:
            if gop < 0:
                ra.append(TrieuChungHe(
                    "ty-lo", 2,
                    f"ty {ma} đang âm {abs(gop):.2f} USD trên sổ cái. CHƯA "
                    f"tách được phí vào lệnh ra khỏi con số này, nên nó có "
                    f"thể đang đổ lỗi cho chiến lược vì một chuyện của "
                    f"người vận hành.",
                    {"chienLuoc": ma, "laiLoUsd": gop,
                     "laiLoChienLuocUsd": None},
                    ["ruiRoTong.tranMotTy"]))
            continue
        cl = float(cl)
        if cl < 0:
            ra.append(TrieuChungHe(
                "ty-lo", 2,
                f"ty {ma} âm {abs(cl):.2f} USD Ở CỘT CHIẾN LƯỢC — đã trừ "
                f"riêng phí vào lệnh. Đây là số đã ghi sổ, không phải ước "
                f"tính, và nó nói về chính chiến lược.",
                {"chienLuoc": ma, "laiLoUsd": gop, "laiLoChienLuocUsd": cl},
                ["ruiRoTong.tranMotTy"]))
        elif gop < 0:
            # Chiến lược dương mà gộp âm: phí vào lệnh ăn hết. KHÔNG có
            # núm nào chữa — vặn trần vốn ở đây là phạt nhầm người.
            n = int(t6.get("soLanVaoLenh") or 0)
            dg = int(t6.get("soLanDong") or 0)
            ti = t6.get("tiLeDongTrenVao")
            # VÀO bao nhiêu lần rồi ĐÓNG bao nhiêu lần — hai con số cạnh
            # nhau phân biệt hai thứ khác hẳn nhau mà cùng trả phí vào:
            # mở-rồi-đóng-rồi-mở-lại (churn, chi phí vận hành) và mở vị
            # thế MỚI (chi phí bình thường của việc rót vốn).
            #
            # Không có mẫu số ấy thì triệu chứng này kêu bằng một con số
            # cộng dồn cả đời và KHÔNG BAO GIỜ TẮT được, kể cả sau khi
            # churn đã hết hẳn — đo 30/08: ba giờ liền 48 lần mở, 0 lần
            # đóng, mà con số 289 vẫn nguyên. Một cảnh báo không tắt được
            # là một cảnh báo người ta học cách bỏ qua.
            # ĐỦ MẪU rồi mới dám gọi là churn. Một tỉ lệ dựng trên
            # MỘT lần vào lệnh không nói gì — đo 30/08 ngay sau khi
            # dựng con số này: ty tiên đoán «vào 1 · đóng 1 · tỉ lệ
            # 1,00» và bị gắn mức NẶNG như một ty churn 289 lần.
            # Cùng bài học `hua-qua-he` đã học ở trên, cùng một
            # phiên, và tôi vẫn quên nó ở đây.
            cao = (ti is not None and ti >= NGUONG_CHURN
                   and n >= TOI_THIEU_LAN_VAO)
            vi = (f"gần như mọi vị thế đã đóng rồi mở lại — CHURN"
                  if cao else
                  f"phần lớn là vị thế MỚI, không phải mở lại")
            ra.append(TrieuChungHe(
                "phi-vao-an-het", 2 if cao else 1,
                f"ty {ma} lãi {cl:+.2f} USD bằng chiến lược nhưng gộp lại "
                f"vẫn âm {abs(gop):.2f} USD: phí vào lệnh {n} lần đã ăn hết. "
                f"Vào {n} · đóng {dg} ({vi}). Phí vào lệnh do mở lại là chi "
                f"phí VẬN HÀNH, không phải chi phí chiến lược. Không núm "
                f"nào chữa được: giữ vị thế lâu hơn, hoặc khởi động lại ít "
                f"đi.",
                {"chienLuoc": ma, "laiLoUsd": gop, "laiLoChienLuocUsd": cl,
                 "soLanVaoLenh": n, "soLanDong": dg, "tiLeDongTrenVao": ti,
                 "phiMoiLanVaoUsd": t6.get("phiMoiLanVaoUsd")}))

    # ── 7b. THU VƯỢT TRẦN — không cần đủ mẫu, vì mỗi lần là NAV sai ─────
    #
    # Trung Ương nhận `thuUsd` từ ty và ghi thẳng vào Sổ Cái. Một ty quên
    # chia cho 8.760 giờ sẽ IN RA TIỀN: NAV phồng lên, và `lechTien` vẫn
    # khớp vì sổ ghi đúng con số bịa ấy. Không núm nào chữa được — đây là
    # lỗi mã, không phải tham số.
    kt = anh.get("keToan") or {}
    vuot = int(kt.get("soThuVuotTran") or 0)
    if vuot:
        ds = kt.get("thuVuotTran") or []
        x0 = ds[0] if ds else {}
        ra.append(TrieuChungHe(
            "thu-vuot-tran", 3,
            f"{vuot} vòng kế toán thu VƯỢT XA mức chính tờ trình của nó "
            f"hứa — nặng nhất là {x0.get('chienLuoc', '?')} thu "
            f"{float(x0.get('thuUsd') or 0):.6f} USD trên trần "
            f"{float(x0.get('tranUsd') or 0):.6f}. Trần đã nhân biên rộng "
            f"gấp mười, nên vượt nó thường là lỗi ĐƠN VỊ (quên chia 8.760 "
            f"giờ, 365 ngày, 24 giờ) chứ không phải chợ biến động. Đây là "
            f"lỗi mã: NAV đang phồng lên, và sổ vẫn cân vì nó ghi đúng con "
            f"số bịa ấy.",
            {"soThuVuotTran": vuot, "nangNhat": x0}))

    # ── 7bb. XOAY CHỖ hứa dài hơn đời thật của vị thế ──────────────────
    #
    # `xoay_cho` tính lợi ròng bằng `vốn × (aprMới − aprCũ) × giờChung /
    # 8.760` — nó CỘNG TRƯỚC phần lãi hơn của cả quãng `giờChung`, có thể
    # tới 167 giờ, rồi trừ phí đổi MỘT lần. Phép tính ấy chỉ đúng nếu vị
    # thế mới thật sự sống hết chừng ấy giờ.
    #
    # Đo làn thật 30/08: 267 lần xoay trong 39 phút, tổng lời hứa
    # +11.136 USD trên sổ 10.000 USD, trong khi chính ty được xoay nhiều
    # nhất đang âm 77,51 USD. Trung vị số giờ giữ được trước lần xoay kế:
    # 0,008 giờ — chưa tới ba mươi giây.
    #
    # Đây KHÔNG phải bệnh của tham số, và cũng không phải bệnh của người
    # vận hành: nó là một lời hứa tính trên quãng thời gian mà chính cỗ
    # máy không cho vị thế sống tới. Nên nó khai núm rỗng — cùng lý do
    # với `phi-vao-an-het`.
    # Đọc CỬA SỔ GẦN ĐÂY, không đọc tổng cộng dồn cả đời. Cửa chặn «còn
    # ghế trống thì không đuổi ai» vào 29/08 đã dừng hẳn vòng xoay ấy,
    # nhưng 267 bút toán cũ nằm lại trong sổ mãi mãi — đọc số cộng dồn là
    # dựng một cảnh báo kêu đúng một lần rồi kêu mãi, kể cả sau khi bệnh
    # đã khỏi. Cùng bài học mà `phi-vao-an-het` đã học bằng mẫu số «vào
    # bao nhiêu · đóng bao nhiêu», và tôi suýt quên nó lần nữa ở đây.
    xc = ((anh.get("soCai") or {}).get("xoayChoHuaVaThuc") or {})
    xc = xc.get("ganDay") or {}
    n_xoay = int(xc.get("soLan") or 0)
    ti_song = xc.get("tiLeSongTrenHua")
    if n_xoay >= TOI_THIEU_LAN_XOAY and ti_song is not None:
        if ti_song < NGUONG_SONG_TREN_HUA:
            gGiu = xc.get("gioGiuTrungVi")
            gHua = xc.get("gioHuaTrungVi")
            ra.append(TrieuChungHe(
                "xoay-cho-hua-qua", 3,
                f"{n_xoay} lần xoay chỗ trong "
                f"{float(xc.get('gioCuaSo') or 0):.0f} giờ qua hứa tổng cộng "
                f"{float(xc.get('huaLoiRongUsd') or 0.0):+.2f} USD lợi "
                f"ròng, nhưng lời hứa ấy tính trên trung vị {gHua:.2f} giờ "
                f"trong khi vị thế mới chỉ sống trung vị {gGiu:.3f} giờ — "
                f"{ti_song * 100:.1f}% quãng đã hứa. Phần lãi hơn chưa bao "
                f"giờ tới, còn phí đổi thì trả đủ mỗi lần. Không núm nào "
                f"chữa được: đây là công thức cộng trước lãi của một quãng "
                f"mà cỗ máy không cho vị thế sống tới.",
                {"soLanXoay": n_xoay, "huaLoiRongUsd": xc.get("huaLoiRongUsd"),
                 "gioHuaTrungVi": gHua, "gioGiuTrungVi": gGiu,
                 "tiLeSongTrenHua": ti_song,
                 "capLapNhieuNhat": xc.get("capLapNhieuNhat"),
                 "soCapDiLaiNhieuLan": xc.get("soCapDiLaiNhieuLan")}))
    elif n_xoay >= TOI_THIEU_LAN_XOAY and xc.get("soThieuGioHua"):
        # KHAI RA chỗ không đo được, đừng im. Bút toán xoay cũ không ghi
        # `gioChungHua`, nên tỉ lệ sống/hứa chưa tính được — và im lặng ở
        # đây đọc y hệt như «đã đo, và không sao cả».
        ra.append(TrieuChungHe(
            "xoay-cho-chua-doi-chieu", 1,
            f"{n_xoay} lần xoay chỗ trong "
            f"{float(xc.get('gioCuaSo') or 0):.0f} giờ qua, nhưng "
            f"{int(xc.get('soThieuGioHua') or 0)} lần trong đó không ghi "
            f"lại quãng giờ mà lời hứa được tính trên — bút toán dựng "
            f"trước khi trường ấy có. Chưa đối chiếu được lời hứa với đời "
            f"thật của vị thế; những lần xoay từ nay sẽ ghi đủ.",
            {"soLanXoay": n_xoay, "soThieuGioHua": xc.get("soThieuGioHua"),
             "huaLoiRongUsd": xc.get("huaLoiRongUsd")}))

    # ── 7c. HỨA QUÁ, đo trên VỊ THẾ ĐANG MỞ ─────────────────────────────
    #
    # Bảng hứa-vs-thực (mục 8 dưới) chỉ nói về những lần ĐÃ ĐÓNG, và đòi
    # 20 mẫu mỗi ty. Máy sống 30/08: ty cao nhất mới có 8 mẫu sau nhiều
    # ngày, trong khi ba giờ gần nhất có 48 lần MỞ và 0 lần đóng. Tín
    # hiệu ấy quá thưa để dạy được ai.
    #
    # Cùng câu hỏi, nguồn khác: lợi suất THỰC trên vốn-giờ (cộng mỗi 30
    # giây) so với LỜI HỨA của chính những vị thế đang mở, có trọng số
    # theo vốn. Cùng một tập vị thế, cùng một quãng — không trộn cửa sổ.
    vdd = ((anh.get("vonDangDung") or {}).get("theoTy")) or {}
    # Đọc bản GỘP của Trung Ương, KHÔNG tự gộp từ `soViThe` — danh sách ấy
    # bị CẮT ở 40 cái cho payload khỏi phình, trong khi lợi suất thực tính
    # trên toàn bộ. Máy sống 30/08 giữ 101 vị thế; gộp từ 40 cái rồi đem so
    # với thực nhận của 101 cái là so hai tập khác nhau — đúng cái bẫy
    # chính triệu chứng này sinh ra để tránh, và 40 cái ấy lại còn chọn
    # theo thứ tự từ điển nên là một mẫu thiên lệch không ai khai.
    hua = anh.get("huaTheoTy") or {}
    for ma, o in sorted(hua.items()):
        thuc = (vdd.get(ma) or {}).get("loiSuatNamPhanTram")
        vg = float((vdd.get(ma) or {}).get("vonGioUsd") or 0.0)
        aprHua = o.get("aprHuaPhanTram")
        if (thuc is None or aprHua is None
                or float(o.get("vonUsd") or 0.0) <= 0
                or vg < TOI_THIEU_VON_GIO):
            continue
        aprHua = float(aprHua)
        if aprHua - float(thuc) <= NGUONG_HUA_QUA_DIEM:
            continue
        ra.append(TrieuChungHe(
            "hua-qua-dang-mo", 2,
            f"ty {ma} đang chạy THỰC {float(thuc):+.2f}%/năm trên "
            f"{vg:,.0f} vốn-giờ, trong khi chính những vị thế đang mở của "
            f"nó HỨA {aprHua:+.2f}%/năm (bình quân theo vốn). Lệch "
            f"{aprHua - float(thuc):+.2f} điểm. Đây là cùng một tập vị "
            f"thế và cùng một quãng — không phải hai cửa sổ khác nhau.",
            {"chienLuoc": ma, "aprHuaPhanTram": aprHua,
             "aprThucPhanTram": float(thuc), "vonGioUsd": vg,
             "soViThe": o.get("soViThe"),
             "soKhongKhai": o.get("soKhongKhai")},
            ["ruiRoTong.netMoiGioToiThieuBps"]))

    # ── 8. HỨA QUÁ — tín hiệu duy nhất mà tám ty KHÔNG có băng vẫn cho ──
    #
    # Chỉ ty chênh funding ghi băng, nên chỉ nó chạy lại được. Tám ty còn
    # lại — và chúng đang giữ gần hết vốn — chỉ có một tín hiệu học được:
    # tờ trình lúc mở đã hứa `netUocBps` trong `giuGio` giờ, sổ lúc đóng
    # biết thu thật bao nhiêu trong bao lâu.
    #
    # Bảng ấy đã có, đã hiện trên buồng lái, và trước lượt này KHÔNG AI
    # ĐỌC. Lần thứ tư trong cùng cây mã: có mã, có phép kiểm, có ô trên
    # buồng lái, và vòng tiến hoá không biết nó tồn tại — nên vòng ấy chỉ
    # học được về đúng cái ty mà chính nó đã tắt.
    dvt = anh.get("duDoanVaThuc") or {}
    for ma, o in sorted(dvt.items()):
        try:
            k = int(o.get("soDoiChieuDuoc") or 0)
            lech = o.get("lechBpsGio")
        except (TypeError, ValueError, AttributeError):
            continue
        # `None` là chưa đo được, KHÔNG phải 0 — bỏ qua, đừng đọc thành
        # "hứa đúng".
        if lech is None or k < TOI_THIEU_DOI_CHIEU:
            continue
        if float(lech) <= NGUONG_HUA_QUA_BPS_GIO:
            continue
        ra.append(TrieuChungHe(
            "hua-qua-he", 2,
            f"ty {ma} hứa cao hơn thực nhận {float(lech):.3f} bps mỗi giờ "
            f"trên {k} lần đóng đối chiếu được. Lệch DƯƠNG nghĩa là lạc "
            f"quan — và một cỗ máy lạc quan sai theo hướng nguy hiểm nhất: "
            f"hào phóng với chính mình.",
            {"chienLuoc": ma, "soDoiChieuDuoc": k,
             "duDoanBpsGio": o.get("duDoanBpsGio"),
             "thucBpsGio": o.get("thucBpsGio"), "lechBpsGio": lech},
            ["ruiRoTong.netMoiGioToiThieuBps"]))

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
        if t.ma in ("thieu-to-trinh", "khoe", "di-tat", "phi-vao-an-het",
                    "thu-vuot-tran", "xoay-cho-hua-qua",
                    "xoay-cho-chua-doi-chieu"):
            # BẢY cái này không vặn được bằng núm. `phi-vao-an-het` là
            # chuyện của người vận hành: siết trần vốn ở đây là rút vốn
            # khỏi một ty ĐANG làm ra tiền vì một buổi chiều deploy nhiều
            # lần.
            continue
        for nut in t.nutGoiY:
            khuon = NUT_TRUNG_UONG.get(nut)
            if khuon is None:
                continue
            hien = _lay(cau_hinh, nut)
            if hien is None:
                continue
            # Hướng vặn = Ý ĐỊNH của bệnh × CỰC của núm.
            #
            # Ý định là chuyện của bệnh: "chặn quá nhiều" thì muốn NỚI,
            # "legging" hay "hứa quá" thì muốn SIẾT. Nhưng cộng hay trừ
            # bước lại là chuyện của NÚM: `tranMot*` cao lên là nới, còn
            # `tinCayToiThieu` và `netMoiGioToiThieuBps` cao lên là siết.
            #
            # Trộn hai chuyện ấy vào một cờ là chỗ đã sai: `tong-chan-het`
            # gợi ý `tinCayToiThieu`, và máy NÂNG sàn tin cậy để chữa bệnh
            # nghẽn. Bước có trần, và không bao giờ ra ngoài khuôn.
            noi = t.ma in ("tong-chan-het", "tran-dat-sai-cho",
                           "tran-vi-the-chan")
            huong = (1 if noi else -1) * int(khuon.get("cuc", 1))
            # `or` chỉ cứu đúng trường hợp `hien == 0`, mà chỗ chết không
            # nằm ở 0 — nó nằm ở MỌI giá trị nhỏ so với khuôn. `hien = 0,5`
            # cho bước 0,125 và núm ấy đứng yên vĩnh viễn, vì mỗi lượt đổi
            # quá ít để tạo ra khác biệt đo được, nên lượt nào cũng bị trả
            # lại. Cỗ máy đo được đích mà không bước tới được, và nó im
            # lặng — mỗi lượt trả lại trông y hệt một quyết định thận
            # trọng đúng đắn. `max`, không phải `or`.
            buoc = max(abs(hien) * BUOC_TOI_DA,
                       (khuon["max"] - khuon["min"]) * SAN_BUOC_KHUON)
            moi = hien + huong * buoc
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
