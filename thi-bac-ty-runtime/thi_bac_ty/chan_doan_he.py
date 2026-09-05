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

import datetime as _dt
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

#: Cả hệ phải có ngần này lần ĐÓNG thì mới nói được gì về tỉ lệ đối
#: chiếu. Năm mươi — dưới mức ấy, một tỉ lệ thấp chỉ là máy mới chạy.
TOI_THIEU_DONG_DE_CHAN = 50

#: Dưới ngần này phần số lần đóng đối chiếu được thì vòng phản hồi ĐÓI.
#: Một phần tư.
NGUONG_DOI_CHIEU_DUOC = 0.25

#: Phí vào lệnh ăn quá ngần này phần THU GỘP thì thành triệu chứng.
#: Một phần ba — dưới mức ấy còn là chi phí vận hành bình thường.
NGUONG_PHI_TREN_THU = 0.35

#: Phải có ngần này bút toán PHÍ thì tỉ lệ mới nói được gì. Năm mươi.
TOI_THIEU_BUT_TOAN_PHI = 50

#: NET quy năm cao hơn ngần này (%/năm) thì con số ấy không còn là lợi
#: suất. Cùng giá trị với `xoay_cho.APR_TOI_DA`, và cố ý không import:
#: đây là NGƯỠNG ĐỌC của bảng chẩn, còn bên kia là ngưỡng HÀNH ĐỘNG của
#: máy xoay chỗ. Hai vai khác nhau thì được phép rời nhau.
NET_QUY_NAM_VO_LY = 1000.0

#: Bao nhiêu vòng LIÊN TIẾP còn ghế trống mà số vị thế không tăng thì lời
#: hứa «Phân Bổ sẽ lấp chỗ» coi như KHÔNG được giữ.
#:
#: Ba, cùng giá trị `trung_uong.VONG_GHE_TRONG_DANG_NGO` và cùng ngưỡng
#: buồng lái tô đỏ (`web/app.js`). Một vòng có thể là chưa có cơ hội nào,
#: hai vòng có thể là trùng hợp; ba vòng liên tiếp là một trạng thái.
VONG_GHE_TRONG_DANG_NGO = 3

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

#: Bao nhiêu PHẦN số lần đóng phải do xoay chỗ thì mới gọi xoay chỗ là
#: thủ phạm. Một nửa: dưới ngần ấy thì hết hạn giữ và khởi động lại còn
#: đóng góp nhiều hơn, và chỉ sang xoay chỗ là chỉ nhầm chỗ.
NGUONG_DONG_DO_XOAY = 0.5

#: Bao nhiêu PHẦN vốn KHẢ DỤNG nằm không thì mới kêu. Mẫu số là vốn khả
#: dụng chứ không phải NAV: dự trữ là một lựa chọn có chủ ý, tính nó vào
#: phần «nằm không» là buộc tội cỗ máy vì chính luật ta đặt ra.
#:
#: Một phần tư. `tran-dat-sai-cho` canh `tiLeDungVon < 0,15` trên NAV, và
#: làn thật 30/08 dùng vốn 56% nên nó im — trong khi 56% trên NAV chính
#: là 70% của phần khả dụng, và 239.071 USD còn lại đang ăn 0%. Lợi suất
#: 4,30%/năm trên vốn đang dùng, quy về NAV còn 2,41%. Gần một nửa lợi
#: suất mất ở đó, không cảnh báo nào kêu.
NGUONG_RANH_TREN_KHA_DUNG = 0.25


#: Bao nhiêu VỐN-GIỜ mà thu ròng vẫn ĐÚNG BẰNG 0 thì mới gọi là «engine
#: chưa kiếm được đồng nào». Mười nghìn USD-giờ — cỡ 200 USD chạy hai
#: ngày, hoặc 1.000 USD chạy mười giờ. Dưới ngần ấy thì «chưa thu được»
#: chỉ nghĩa là chưa tới kỳ trả.
TOI_THIEU_VON_GIO_THU_KHONG = 10_000.0

#: Cầu dao ngắt liên tục quá ngần này GIỜ thì tự nó là một triệu chứng.
#:
#: Một giờ. Mọi lý do `tuMo=True` đều tự đóng khi điều kiện hết, và điều
#: kiện lâu nhất trong nhóm ấy là tuổi nguồn vốn ngoài — `nhipGiay` 60,
#: `tuoiToiDaGiay` 300. Một giờ là mười hai lần cái cửa sổ ấy: đủ xa để
#: không kêu vì một lần mạng chập, đủ gần để một cỗ máy đứng hình được
#: khai ra trong cùng buổi làm việc chứ không phải sáng hôm sau.
NGUONG_NGAT_LAU_GIO = 1.0

#: Lệch lợi suất giữa ty ÔM NHIỀU VỐN NHẤT và ty LÃI CAO NHẤT, tính bằng
#: ĐIỂM phần trăm, quá ngần này thì thành triệu chứng.
#:
#: Ba điểm. Dưới mức ấy thì chênh lệch nằm trong sai số của một cửa sổ kế
#: toán ngắn, và đổi chỗ vốn tốn phí vào lệnh — thứ đã có tiền lệ ăn sạch
#: phần lãi (xem `phi-vao-an-het`).
NGUONG_LECH_LOI_SUAT_DIEM = 3.0

#: Ty ôm nhiều vốn nhất phải giữ ít nhất ngần này phần vốn đang dùng thì
#: mới đáng gọi là «vốn dồn một chỗ». Một nửa.
NGUONG_VON_DON_MOT_CHO = 0.5

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
    #: Bệnh này muốn NỚI hay SIẾT — `"noi"` / `"siet"`.
    #:
    #: Ý định là chuyện của BỆNH, còn cộng hay trừ bước là chuyện của NÚM
    #: (xem `cuc` trong `NUT_TRUNG_UONG`). Trước lượt này ý định nằm trong
    #: một tuple tên bệnh chép tay bên trong `de_xuat()`, cách chỗ khai
    #: bệnh hơn năm trăm dòng — nên một bệnh thêm sau mà không ai nhớ
    #: thêm tên vào đó sẽ lặng lẽ nhận chiều NGƯỢC.
    #:
    #: Đúng chuyện ấy đã xảy ra với `von-ranh-an-khong`. Nó khai «222.905
    #: USD nằm không, ăn 0%» rồi đề xuất SIẾT `tranMotCang` 0,35 → 0,26 —
    #: tức làm cho ít vốn rót được hơn nữa, ngược hẳn ý định ghi ngay
    #: trong chú thích của chính nó. Và có đường tự áp
    #: (`/api/ap-dung-tham-so`), nên lời khuyên ấy không chỉ nằm trên
    #: giấy.
    yDinh: str = ""

    def tom_tat(self) -> dict:
        return {"ma": self.ma, "nang": self.nang, "moTa": self.moTa,
                "bangChung": self.bangChung, "nutGoiY": list(self.nutGoiY),
                "yDinh": self.yDinh}


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
            ["ruiRoTong.tranMotCoHoi"], yDinh="siet"))

    # ── 0c. cầu dao ngắt LIÊN TỤC — cỗ máy còn thở mà không làm gì ──────
    #
    # Một cầu dao đúng nghĩa thì ngắt rồi ĐÓNG LẠI. Cái ngắt liên tục
    # hàng chục giờ không còn là cầu dao nữa mà là một BỨC TƯỜNG — và
    # bức tường ấy trước lượt này không có triệu chứng nào của riêng nó.
    # `von-ranh-an-khong` chỉ NHẮC tới nó như một ghi chú phụ, và chỉ khi
    # vốn rảnh vượt ngưỡng; im lặng nếu tiền đã kẹt sẵn trong vị thế cũ.
    #
    # Đo làn thật 04/09: ngắt lúc 03/09 01:26 vì `von-ngoai-mu`, chưa
    # đóng lại lần nào trong suốt 39,1 giờ — trọn đời tiến trình. 4.697
    # vòng, 50,2 triệu cơ hội thô, 98.109 tờ qua cổng ty, cấp vốn 0 đồng.
    # Buồng lái vẫn xanh: nhịp đều, không lỗi nào ném, `chayDuocGiay`
    # tăng đẹp.
    #
    # Đây là vết cũ tái diễn dưới dạng khó thấy hơn. Lần trước cỗ máy
    # CHẾT ba ngày không ai hay; lần này nó SỐNG mà không làm gì, và mọi
    # dấu hiệu sinh tồn đều bình thường.
    #
    # Triệu chứng này KHÔNG nói cầu dao ngắt đúng hay sai — nó không biết,
    # và `von-ngoai-mu` rất có thể đang ngắt hoàn toàn đúng. Nó chỉ nói
    # một điều ĐO ĐƯỢC: đã ngần này giờ, và chưa ai được báo. Nên nó khai
    # núm RỖNG: vặn trần lúc tường đang dựng là nới một cửa trong khi cửa
    # khác khoá có chủ ý.
    if cd.get("dangNgat"):
        _moc = []
        for _l in (cd.get("lyDo") or []):
            if _l.get("luc"):
                _moc.append(str(_l["luc"]))
        # `lichSu` cũng được soi, và lấy mốc SỚM NHẤT trong hai nguồn:
        # bản `cau_dao.py` cũ làm mới `luc` mỗi vòng, nên ảnh chụp của một
        # tiến trình chưa khởi động lại vẫn mang mốc sai. Thà tính thiếu
        # giờ còn hơn khai một con số trẻ hơn sự thật.
        _macs = {str(_l.get("ma")) for _l in (cd.get("lyDo") or [])}
        for _h in (cd.get("lichSu") or []):
            if _h.get("viec") == "NGAT" and str(_h.get("ma")) in _macs:
                if _h.get("luc"):
                    _moc.append(str(_h["luc"]))
        _gio = None
        if _moc:
            try:
                _t0 = min(_dt.datetime.fromisoformat(x.replace("Z", "+00:00"))
                          for x in _moc)
                _gio = ((_dt.datetime.now(_dt.timezone.utc) - _t0)
                        .total_seconds() / 3600.0)
            except (ValueError, TypeError):
                _gio = None
        if _gio is not None and _gio >= NGUONG_NGAT_LAU_GIO:
            _ma = ", ".join(str(x.get("ma")) for x in (cd.get("lyDo") or [])
                            if x.get("ma")) or "không rõ mã"
            # Chỉ đúng NGUỒN đang mù, không nói chung chung. Người đọc cần
            # biết bấm vào đâu, và `vonNgoai` có sẵn tên lẫn URL lẫn số lần
            # lỗi — thiếu nó thì lời khuyên duy nhất rút ra được là «xem
            # lại cầu dao», thứ không giúp được ai.
            _mu = [d for d in (anh.get("vonNgoai") or [])
                   if not d.get("docDuoc")]
            _vi = ""
            if _mu:
                _vi = " Nguồn KHÔNG đọc được: " + "; ".join(
                    f"{d.get('ten')} ({d.get('url')}) — {int(d.get('soLoi') or 0)} lần lỗi"
                    for d in _mu) + "."
            ra.append(TrieuChungHe(
                "cau-dao-ngat-lau", 3,
                f"cầu dao đã NGẮT LIÊN TỤC {_gio:.1f} giờ ({_ma}) — cỗ máy "
                f"vẫn quét, vẫn xét, nhưng KHÔNG cam kết được đồng nào suốt "
                f"quãng ấy. Một cầu dao không đóng lại được nữa thì là một "
                f"bức tường, và nó không hiện ra ở đâu ngoài chỗ này."
                + _vi +
                f" Gỡ lý do ngắt, hoặc bỏ khai nguồn ấy đi nếu nó vốn không "
                f"định chạy — đừng vặn trần nào cả.",
                {"soGioNgat": round(_gio, 2), "ma": [
                    str(x.get("ma")) for x in (cd.get("lyDo") or [])],
                 "tuMo": [bool(x.get("tuMo"))
                          for x in (cd.get("lyDo") or [])],
                 "soLanNgat": cd.get("soLanNgat"),
                 "nguongGio": NGUONG_NGAT_LAU_GIO,
                 "nguonMu": [d.get("ten") for d in _mu]},
                []))

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
            ["ruiRoTong.ruiRoToiDa", "ruiRoTong.tinCayToiThieu"], yDinh="noi"))

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
             "ruiRoTong.tranMotCoHoi"], yDinh="noi"))

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
            # GHẾ ĐANG GIỮ BAO NHIÊU, và cổng của chính ty ấy còn thả ra
            # được mấy cơ hội. Hai con số này quyết cả hướng đọc, và
            # trước lượt này không có cái nào.
            #
            # Câu chẩn cũ kết luận thẳng «trần đang chặn nhiều hơn nó bảo
            # vệ». Đó là một phán xét, không phải một phép đo, và nó bỏ
            # sót đúng nửa còn lại: đo làn thật 30/08 thì 99 trên 120 ghế
            # giữ dưới 1.667 USD — cộng lại chỉ 13,4% vốn đang dùng,
            # trong khi 222.757 USD nằm ngoài dự trữ ăn 0%. **Ghế đầy
            # KHÔNG có nghĩa vốn đã vào việc.**
            #
            # Và nó không nói được «nâng trần thì tiền sẽ vào». Ty giữ
            # nhiều ghế bé nhất là `amm.fee_farming.v1`: 78.120 cơ hội
            # thô, **16** qua nổi cổng của chính nó. Thêm ghế chỉ giúp
            # tới mức ấy. Nên chỗ này khai đủ ba con số rồi dừng — nâng
            # trần, nới sức chứa mỗi cơ hội, hay nới cổng ty, đều là
            # quyết định của chủ, và cả ba đều cần biết ba con số này.
            _gv = anh.get("gheVaVon") or {}
            _soBe = _gv.get("soGheBe")
            _nBe = _gv.get("soDangDung") or 0
            _viGhe = ""
            if _soBe is not None and _nBe:
                _tv = _gv.get("vonTrungViMotGheUsd")
                _pc = _gv.get("phanChiaMoiGheUsd")
                _tiVon = _gv.get("tiLeVonTrongGheBe")
                _viGhe = (
                    f" Nhưng ghế đầy KHÔNG có nghĩa vốn đã vào việc: "
                    f"{_soBe}/{_nBe} ghế giữ dưới "
                    f"{float(_gv.get('nguongGheBeUsd') or 0):,.0f} USD, cộng "
                    f"lại {float(_gv.get('vonTrongGheBeUsd') or 0):,.0f} USD"
                    + ("" if _tiVon is None else f" ({_tiVon:.1%} vốn đang "
                                                 f"dùng)")
                    + (f"; trung vị một ghế {float(_tv):,.0f} USD trên phần "
                       f"chia công bằng {float(_pc):,.0f} USD."
                       if (_tv is not None and _pc) else "."))
                # THÊM GHẾ SẼ NHẬN VÀO THỨ GÌ — câu hỏi đúng, và nó
                # KHÔNG phải câu «ty nào giữ nhiều ghế bé nhất».
                #
                # Bản đầu tôi chỉ sang ty giữ nhiều ghế bé nhất
                # (`amm.fee_farming.v1`) rồi khai cổng của nó. Sai chỗ:
                # cái quyết định là họ nào có tờ trình ĐÃ QUA CỔNG TY mà
                # KHÔNG được cấp đồng nào — đó đúng là thứ một cái ghế
                # trống sẽ nhận. Đo làn thật 30/08: họ `tin-dung` có 160
                # tờ qua cổng ty và 0 được cấp vốn, trong khi họ
                # `thanh-khoan` chỉ có 16. Chỉ sang AMM là chỉ sang chỗ
                # HẸP nhất trong khi chỗ RỘNG đang mở ngay cạnh.
                #
                # Và nó lật cả cách đọc «ghế bé». Dưới ràng buộc GHẾ, mỗi
                # cơ hội chiếm đúng một chỗ, nên xếp hạng theo ĐÔ-LA MỖI
                # GIỜ là xếp đúng: một vị thế cho vay 25.000 USD ở
                # 2,4%/năm sinh ~0,068 USD/giờ, còn một vị thế AMM 1.100
                # USD ở 19,3%/năm chỉ sinh ~0,024. Máy đang chọn ĐÚNG.
                # Ghế bé không phải lỗi phân bổ — nó là dấu hiệu rằng
                # phần lớn ghế đang bị chiếm bởi những cơ hội nhỏ, và
                # thêm ghế sẽ đi vào họ có sức chứa.
                _ho = sorted(
                    ((h.get("ho"), int(h.get("quaCongTy") or 0))
                     for h in ((anh.get("pheuDayDu") or {}).get("theoHo")
                               or [])
                     if int(h.get("quaCongTy") or 0) > 0
                     and int(h.get("daCapVon") or 0) == 0),
                    key=lambda kv: -kv[1])
                if _ho:
                    _viGhe += (
                        f" Thêm ghế sẽ nhận vào thứ gì thì phễu nói: họ "
                        f"`{_ho[0][0]}` có {_ho[0][1]:,} tờ ĐÃ QUA cổng ty "
                        f"mà KHÔNG được cấp đồng nào"
                        + (f" (kế đó `{_ho[1][0]}`: {_ho[1][1]:,})"
                           if len(_ho) > 1 else "")
                        + ". Đó là hàng đang chờ ghế, không phải hàng đang "
                          "chờ tiền.")
            ra.append(TrieuChungHe(
                "tran-vi-the-chan", 2,
                f"{so_top}/{tong_tc} lần từ chối ({phan:.0%}) là vì ĐỦ SỐ VỊ "
                f"THẾ, không phải vì hết tiền hay vì rủi ro. Trần ấy đặt ra "
                f"khi người phải tự theo dõi từng chân; nay mỗi vòng đều có "
                f"kế toán tự chạy." + _viGhe,
                {"maTuChoi": ma_top, "so": so_top, "tongTuChoi": tong_tc,
                 "phan": phan, "dem": dem, "soKhongMa": khong_ma,
                 "soGheBe": _soBe, "soDangDung": _gv.get("soDangDung"),
                 "vonTrongGheBeUsd": _gv.get("vonTrongGheBeUsd"),
                 "tiLeVonTrongGheBe": _gv.get("tiLeVonTrongGheBe"),
                 "vonTrungViMotGheUsd": _gv.get("vonTrungViMotGheUsd"),
                 "phanChiaMoiGheUsd": _gv.get("phanChiaMoiGheUsd")},
                ["phanBo.toiDaSoViThe"], yDinh="noi"))

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
                    ["ruiRoTong.tranMotTy"], yDinh="siet"))
            continue
        cl = float(cl)
        if cl < 0:
            ra.append(TrieuChungHe(
                "ty-lo", 2,
                f"ty {ma} âm {abs(cl):.2f} USD Ở CỘT CHIẾN LƯỢC — đã trừ "
                f"riêng phí vào lệnh. Đây là số đã ghi sổ, không phải ước "
                f"tính, và nó nói về chính chiến lược.",
                {"chienLuoc": ma, "laiLoUsd": gop, "laiLoChienLuocUsd": cl},
                ["ruiRoTong.tranMotTy"], yDinh="siet"))
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
            # ĐÓNG VÌ ĐÂU. Câu khuyên cũ — «giữ vị thế lâu hơn, hoặc khởi
            # động lại ít đi» — chỉ đúng khi thủ phạm là khởi động lại. Đo
            # làn thật 30/08: 217 trong 282 lần đóng của ty cho vay là
            # XOAY CHỖ, và 29/29 của ty basis cũng thế. Chỉ người vận hành
            # sang một cái nút họ không hề chạm vào là gửi họ đi sai
            # đường, và đường sai ấy nghe rất hợp lý.
            dx = t6.get("soLanDongXoayCho")
            px = t6.get("phanDongDoXoayCho")
            if px is not None and px >= NGUONG_DONG_DO_XOAY:
                khuyen = (f"{dx}/{dg} lần đóng là do XOAY CHỖ, không phải "
                          f"do khởi động lại — xem `xoay-cho-hua-qua`: mỗi "
                          f"lần xoay cộng trước phần lãi hơn của cả trăm "
                          f"giờ rồi trừ phí một lần, còn vị thế mới thì "
                          f"sống vài phút.")
            elif px is not None:
                khuyen = (f"chỉ {dx}/{dg} lần đóng là do xoay chỗ, nên "
                          f"phần còn lại là hết hạn giữ hoặc khởi động "
                          f"lại. Không núm nào chữa được: giữ vị thế lâu "
                          f"hơn, hoặc khởi động lại ít đi.")
            else:
                # `None` nghĩa là CHƯA ĐÓNG lần nào, nên chưa chia được.
                # Nói «0% do xoay chỗ» ở đây là bịa ra một phép đo.
                khuyen = ("chưa đóng lần nào nên chưa tách được đóng vì "
                          "đâu. Phí vào lệnh này là của những vị thế đang "
                          "còn mở.")
            ra.append(TrieuChungHe(
                "phi-vao-an-het", 2 if cao else 1,
                f"ty {ma} lãi {cl:+.2f} USD bằng chiến lược nhưng gộp lại "
                f"vẫn âm {abs(gop):.2f} USD: phí vào lệnh {n} lần đã ăn hết. "
                f"Vào {n} · đóng {dg} ({vi}). Phí vào lệnh do mở lại là chi "
                f"phí VẬN HÀNH, không phải chi phí chiến lược. " + khuyen,
                {"chienLuoc": ma, "laiLoUsd": gop, "laiLoChienLuocUsd": cl,
                 "soLanVaoLenh": n, "soLanDong": dg, "tiLeDongTrenVao": ti,
                 "soLanDongXoayCho": dx, "phanDongDoXoayCho": px,
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

    # ── 7b0. TY chưa thu được ĐỒNG NÀO, và nó ĐO ĐƯỢC điều đó ──────────
    #
    # Khác `ty-lo` ở chỗ: lỗ là số ÂM, còn đây là số KHÔNG. Điều
    # `khong-do-bang-so-do` cấm đọc số 0 thành «chưa đo», nhưng cũng cấm
    # đọc nó thành «huề vốn» — số 0 ở đây có nghĩa riêng của nó, và nó
    # rơi lọt qua mọi lưới hiện có: `ty-lo` đòi âm, `hua-qua-dang-mo` đòi
    # có lời hứa để so, `phi-vao-an-het` đòi gộp âm VÀ chiến lược dương.
    #
    # Đo làn thật 30/08: `basis.cash_carry.v1` chạy 5.222 vòng kế toán,
    # KHÔNG vòng nào mù, 23.042 vốn-giờ — và thu ròng đúng 0,0000 USD,
    # trong khi đã trả 25,60 USD phí vào lệnh. Nguyên nhân đo được: thu
    # nhập của nó tới theo MỐC funding 8 giờ một lần, mà 29/29 vị thế của
    # nó bị xoay chỗ đóng sau chừng ba mươi giây — không cái nào sống tới
    # mốc đầu tiên. Cả một engine bị chính cỗ máy chặn không cho kiếm.
    #
    # Phân biệt hai câu, và bằng chứng để phân biệt nằm sẵn trong ảnh
    # chụp: `soVongKhongDoDuoc`. Bằng 0 nghĩa là kế toán CHẠY ĐƯỢC và nó
    # nói không có gì; khác hẳn một engine mù.
    _vdd0 = ((anh.get("vonDangDung") or {}).get("theoTy")) or {}
    for ma, o in sorted(_vdd0.items()):
        try:
            thu = o.get("thuRongUsd")
            vg = float(o.get("vonGioUsd") or 0.0)
        except (TypeError, ValueError, AttributeError):
            continue
        if thu is None or float(thu) != 0.0:
            continue
        if vg < TOI_THIEU_VON_GIO_THU_KHONG:
            continue
        # CÁCH ĐỌC THỨ BA — «mốc rơi vào một cửa sổ bị vứt» — nay ĐO
        # ĐƯỢC, và nó là cách đọc DUY NHẤT chỉ về phía cỗ máy chứ không
        # về phía thị trường. Cả hai đường vứt cửa sổ đều đã được đếm:
        # ty mù quá `TRAN_CUA_SO_MU_GIAY`, và khởi động lại mà quãng tắt
        # dài quá cùng cái trần ấy. Quãng ngắn hơn thì NỐI LẠI, không
        # vứt.
        #
        # Một câu KHÔNG được nói: «đã loại hẳn». `soCuaSoMuBoQuaTong` gộp
        # từ những vị thế ĐANG MỞ; vị thế đã đóng mang lịch sử của nó đi
        # theo. Nên câu đúng là «không vị thế đang mở nào», và cái khác
        # nhau ấy đáng một mệnh đề chứ không đáng bỏ đi.
        ld = anh.get("luuDanhMuc") or {}
        n_kd = int(ld.get("soLanKhoiDong") or 0)
        g_tat = float(ld.get("tongGiayTatMay") or 0.0)
        vi_kd = (f" Cỗ máy đã khởi động lại {n_kd} lần (tổng "
                 f"{g_tat / 60.0:.1f} phút tắt) — quãng tắt NGẮN thì cửa "
                 f"sổ kế toán nối lại được, nên nó chỉ vứt cửa sổ khi tắt "
                 f"lâu, và những lần ấy đã nằm trong con số trên."
                 if n_kd > 1 else "")
        _kt0 = anh.get("keToan") or {}
        _mbq = _kt0.get("soCuaSoMuBoQuaTong")
        _gbq = _kt0.get("gioMuBoQuaTong")
        if _mbq is None:
            vi_mu = ""
        elif _mbq:
            vi_mu = (f" Cỗ máy ĐÃ bỏ hẳn {_mbq} cửa sổ kế toán "
                     f"({_gbq:.2f} giờ) — cách đọc thứ ba có bằng chứng, "
                     f"hãy xem trước.")
        else:
            vi_mu = (" KHÔNG vị thế ĐANG MỞ nào có cửa sổ kế toán bị bỏ, "
                     "nên với chúng cách đọc thứ ba đã LOẠI (vị thế đã "
                     "đóng thì mang lịch sử ấy đi theo).")
        ra.append(TrieuChungHe(
            "ty-thu-bang-khong", 2,
            f"ty {ma} chạy {vg:,.0f} vốn-giờ mà thu ròng ĐÚNG BẰNG 0. Đây "
            f"KHÔNG phải «chưa đo được» — kế toán của nó chạy được và nói "
            f"không có gì. Ba cách đọc: engine này không kiếm được trong "
            f"điều kiện hiện tại; hoặc thu nhập của nó tới theo MỐC "
            f"(funding 8 giờ, đáo hạn) mà vị thế không sống tới mốc nào; "
            f"hoặc mốc có đi qua nhưng rơi vào một cửa sổ bị vứt. Xem "
            f"`daGiuGio` của chính nó so với nhịp trả." + vi_mu + vi_kd,
            {"chienLuoc": ma, "vonGioUsd": vg, "thuRongUsd": thu,
             "soCuaSoMuBoQua": _mbq, "gioMuBoQua": _gbq,
             "soLanKhoiDong": n_kd, "tongGiayTatMay": g_tat}))

    # ── 7b1. VỐN dồn vào ty LÃI THẤP, trong khi ty LÃI CAO hết chỗ ──────
    #
    # Mọi triệu chứng trước đây hỏi về MỘT ty (`ty-lo`, `ty-thu-bang-khong`,
    # `hua-qua-dang-mo`) hoặc về CẢ hệ (`von-ranh-an-khong`). Không cái nào
    # hỏi câu đắt nhất: **vốn có đang nằm đúng chỗ không.**
    #
    # Đo làn thật 05/09/2026:
    #
    #     ty                      vốn USD   %vốn  ghế  APR thực
    #     lending.rate_rotation   499.967  86,6%   21     2,63%
    #     amm.fee_farming          70.194  12,2%   64    13,61%
    #     basis.cash_carry          7.000   1,2%   35     3,05%
    #     ─ bình quân theo vốn                            3,97%
    #
    # Ty lãi cao gấp 5,2 lần giữ một phần tám số vốn. Và hai cửa chặn đúng
    # hai đầu: `lending` đang ở 499.967/1.000.085 = **49,99% NAV**, tức
    # chạm đúng `ruiRoTong.tranMotTy` = 0,5; còn `amm` hết GHẾ (64 trong
    # 120, và cả 64 đều là ghế bé). Nên đồng vốn tiếp theo không đi được
    # đâu và nằm không ở 0% — 222.905 USD.
    #
    # Sức chứa KHÔNG phải chỗ nghẽn: `duongSucChua.tongSucChuaUsd` =
    # 1.010.428 USD và `soBoViThieuSucChua` = 0. Phải kiểm điều đó trước
    # khi mở miệng, vì nếu chợ hết chỗ thì «dồn vốn sang ty lãi cao» là
    # một lời khuyên không thực hiện được.
    _vdd1 = ((anh.get("vonDangDung") or {}).get("theoTy")) or {}
    _hua1 = anh.get("huaTheoTy") or {}
    _co = []
    for _ma, _o in _hua1.items():
        _e = _vdd1.get(_ma) or {}
        _ls = _e.get("loiSuatNamPhanTram")
        if _ls is None:
            continue
        if float(_e.get("vonGioUsd") or 0.0) < TOI_THIEU_VON_GIO:
            continue
        _von = float(_o.get("vonUsd") or 0.0)
        if _von <= 0:
            continue
        _co.append((_ma, _von, float(_ls), int(_o.get("soViThe") or 0)))
    _tong = sum(x[1] for x in _co)
    if len(_co) >= 2 and _tong > 0:
        _omNhat = max(_co, key=lambda x: x[1])
        _laiNhat = max(_co, key=lambda x: x[2])
        _lech = _laiNhat[2] - _omNhat[2]
        _phan = _omNhat[1] / _tong
        _sc = anh.get("duongSucChua") or {}
        _conCho = int(_sc.get("soBoViThieuSucChua") or 0) == 0
        if (_omNhat[0] != _laiNhat[0]
                and _lech >= NGUONG_LECH_LOI_SUAT_DIEM
                and _phan >= NGUONG_VON_DON_MOT_CHO
                and _conCho):
            _bq = sum(x[1] * x[2] for x in _co) / _tong
            _gv1 = anh.get("gheVaVon") or {}
            _het = _gv1.get("conGhe") == 0
            # BA đường đi, và triệu chứng này KHÔNG chọn hộ: nâng trần
            # ghế · nới sức chứa mỗi cơ hội · ít ghế mà mỗi ghế nặng hơn.
            # Vị thế của ty lãi cao nhỏ vì SỨC CHỨA pool nhỏ — sự thật của
            # thị trường, không phải lỗi cấu hình; và 120 vị thế đã nhiều
            # hơn mức người ta theo dõi nổi, nên trần ghế cũng có lý.
            _viG = (f" Và {_laiNhat[0]} HẾT GHẾ ({_gv1.get('soDangDung')}/"
                    f"{_gv1.get('soGhe')} ghế đã đầy), nên đồng vốn tiếp "
                    f"theo không đi được đâu. BA đường, và không đường nào "
                    f"hiển nhiên đúng: nâng trần ghế · nới sức chứa mỗi cơ "
                    f"hội · ít ghế mà mỗi ghế nặng hơn." if _het else "")
            ra.append(TrieuChungHe(
                "von-o-ty-loi-thap", 2,
                f"{_phan:.0%} vốn đang dùng nằm ở {_omNhat[0]} — ăn "
                f"{_omNhat[2]:.2f}%/năm, trong khi {_laiNhat[0]} ăn "
                f"{_laiNhat[2]:.2f}%/năm trên {_laiNhat[3]} vị thế. Lệch "
                f"{_lech:.2f} điểm; bình quân theo vốn của cả danh mục là "
                f"{_bq:.2f}%/năm. Chợ KHÔNG hết chỗ: sức chứa đang có "
                f"{float(_sc.get('tongSucChuaUsd') or 0):,.0f} USD và "
                f"không cơ hội nào bị bỏ vì thiếu sức chứa." + _viG
                + " Đây là câu hỏi vốn NẰM ĐÚNG CHỖ chưa — không phải câu "
                  "hỏi ty nào hỏng.",
                {"tyOmNhieuNhat": _omNhat[0], "vonUsd": _omNhat[1],
                 "phanVon": _phan, "loiSuatOmNhatPhanTram": _omNhat[2],
                 "tyLaiCaoNhat": _laiNhat[0],
                 "loiSuatCaoNhatPhanTram": _laiNhat[2],
                 "soViTheLaiCaoNhat": _laiNhat[3],
                 "lechDiem": _lech, "loiSuatBinhQuanPhanTram": _bq,
                 "tongSucChuaUsd": _sc.get("tongSucChuaUsd"),
                 "conGhe": _gv1.get("conGhe")},
                # Núm RỖNG, và đó là một lựa chọn chứ không phải thiếu
                # sót. Hai lý do, cả hai đều đã có tiền lệ:
                #
                # 1. Ba đường đi đều là núm ĐÒI TÊN NGƯỜI. Khai một núm là
                #    chọn hộ chủ một đường bằng cách làm hai đường kia vô
                #    hình.
                # 2. `tran-vi-the-chan` ĐÃ tồn tại, nổ cùng lúc khi ghế
                #    đầy, và đã khai đúng núm ấy. Khai lại là hai cảnh báo
                #    cho một chuyện — đúng thứ làm người ta thôi đọc cảnh
                #    báo, và đúng lỗi đã khiến `ghe-khan-hon-tien` bị gộp
                #    vào `tran-vi-the-chan` một lần rồi.
                #
                # Triệu chứng này đóng góp thứ KHÁC: hai con số lợi suất
                # đặt cạnh nhau. Đó là thông tin `tran-vi-the-chan` không
                # có, và nó không cần một cái núm để đáng đọc.
                [],
                yDinh="noi"))

    # ── 7ba. VỐN KHẢ DỤNG nằm không ────────────────────────────────────
    #
    # Khác `tran-dat-sai-cho` ở MẪU SỐ, và mẫu số là cả vấn đề. Cái kia
    # canh `tiLeDungVon` trên NAV; cái này canh phần KHẢ DỤNG — NAV trừ
    # dự trữ. Dự trữ là lựa chọn có chủ ý, phần ngoài dự trữ mà nằm im
    # thì không ai chọn cả.
    vr = anh.get("vonRanh") or {}
    ti_ranh = vr.get("tiLeRanhTrenKhaDung")
    if ti_ranh is not None and ti_ranh >= NGUONG_RANH_TREN_KHA_DUNG:
        ls_d = vr.get("loiSuatTrenVonDungPhanTram")
        ls_n = vr.get("loiSuatQuyVeNavPhanTram")
        ls_l = vr.get("loiSuatNeuLapDayPhanTram")
        # Câu về lợi suất chỉ nói khi ĐO ĐƯỢC. Ghép «0,00%/năm» vào đây
        # lúc chưa có vốn-giờ nào là bịa ra một cỗ máy đang huề vốn.
        them = ("" if ls_d is None or ls_n is None else
                f" Lợi suất trên vốn ĐANG DÙNG là {ls_d:.2f}%/năm, quy về "
                f"NAV còn {ls_n:.2f}%"
                + ("" if ls_l is None else
                   f"; nếu phần rảnh chạy được như phần đang chạy thì NAV "
                   f"sẽ là {ls_l:.2f}%")
                + ". Con số sau là TRẦN TRÊN của phần đang bỏ lỡ, không "
                  "phải số sẽ thu được: phần rảnh nằm im thường vì những "
                  "cơ hội còn lại tệ hơn, hoặc vì một trần đang chặn.")
        # CẦU DAO ĐANG NGẮT thì tiền nằm không LÀ ĐÚNG, và chỉ sang trần
        # vốn là chỉ sai chỗ. Đo làn thật 30/08: cầu dao ngắt vì
        # `von-ngoai-mu` (runtime Khâm Thiên Giám không chạy), nên KHÔNG
        # tờ trình nào qua nổi Rủi Ro Tổng — 27,8% vốn khả dụng nằm im vì
        # một lớp an toàn đang làm đúng việc của nó, không vì một cái
        # trần đặt sai. Cùng lỗi mà lời khuyên cũ của `phi-vao-an-het` đã
        # mắc: chỉ người vận hành sang cái nút họ không hề chạm vào.
        _cdN = anh.get("cauDao") or {}
        _viCd = ""
        if _cdN.get("dangNgat"):
            _ma = ", ".join(str(x.get("ma")) for x in (_cdN.get("lyDo") or [])
                            if x.get("ma")) or "không rõ mã"
            _viCd = (f" NHƯNG CẦU DAO ĐANG NGẮT ({_ma}) — nên tiền nằm "
                     f"không ở đây là ĐÚNG, và trần vốn KHÔNG phải chỗ "
                     f"đáng nhìn. Gỡ lý do ngắt trước; đo lại sau đó mới "
                     f"nói được gì về trần.")

        # GHẾ ĐÃ ĐẦY thì nới trần vốn KHÔNG rót thêm được đồng nào: một vị
        # thế mới cần một CHỖ NGỒI trước khi cần tiền. Chỉ sang trần lúc
        # ấy là đúng cái lỗi vừa gỡ cho cầu dao, lặp lại ở một cửa khác.
        #
        # Đo làn thật 05/09/2026: 120/120 ghế đầy, 222.905 USD nằm ngoài
        # dự trữ, và lý do từ chối duy nhất còn lại là `tran-vi-the`.
        #
        # Và câu quan trọng hơn nằm ở PHÂN BỐ chứ không ở SỐ LƯỢNG ghế:
        # 100 trong 120 ghế giữ đúng 14% vốn, trung vị một ghế 1.136 USD
        # trên phần chia công bằng 6.667 USD. Nên nới thêm ghế chưa chắc
        # là câu trả lời — có thể ghế đang ngồi sai người. Triệu chứng
        # này KHÔNG chọn hộ; nó bày cả hai con số ra.
        _gvR = anh.get("gheVaVon") or {}
        _conGhe = _gvR.get("conGhe")
        _viGhe = ""
        _ghetDay = (_conGhe == 0 and not _cdN.get("dangNgat"))
        if _ghetDay:
            _soGhe = _gvR.get("soGhe")
            _be = _gvR.get("soGheBe")
            _tiBe = _gvR.get("tiLeVonTrongGheBe")
            _tv = _gvR.get("vonTrungViMotGheUsd")
            _pc = _gvR.get("phanChiaMoiGheUsd")
            _viGhe = (f" NHƯNG GHẾ ĐÃ ĐẦY ({_soGhe}/{_soGhe}) — nới trần "
                      f"vốn KHÔNG rót thêm được đồng nào, vì một vị thế "
                      f"mới cần một CHỖ NGỒI trước khi cần tiền.")
            if _be is not None and _tiBe is not None:
                _viGhe += (f" Và {_be}/{_soGhe} ghế đang giữ "
                           f"{float(_tiBe):.0%} vốn")
                if _tv and _pc:
                    _viGhe += (f" (trung vị {float(_tv):,.0f} USD một ghế "
                               f"trên phần chia {float(_pc):,.0f})")
                _viGhe += (". Nên câu hỏi là ghế đang ngồi ĐÚNG người "
                           "chưa, chứ không hẳn là thiếu ghế.")
        ra.append(TrieuChungHe(
            "von-ranh-an-khong", 2,
            f"{float(vr.get('ranhNgoaiDuTruUsd') or 0):,.0f} USD nằm NGOÀI "
            f"dự trữ mà không làm gì — {ti_ranh:.0%} phần vốn khả dụng, ăn "
            f"0%. Dự trữ {float(vr.get('tiLeDuTru') or 0):.0%} đã trừ ra "
            f"rồi, nên đây không phải chỗ tiền được cố ý để yên."
            + them + _viCd + _viGhe,
            {"ranhNgoaiDuTruUsd": vr.get("ranhNgoaiDuTruUsd"),
             "tiLeRanhTrenKhaDung": ti_ranh,
             "khaDungUsd": vr.get("khaDungUsd"),
             "dangDungUsd": vr.get("dangDungUsd"),
             "loiSuatTrenVonDungPhanTram": ls_d,
             "loiSuatQuyVeNavPhanTram": ls_n,
             "loiSuatNeuLapDayPhanTram": ls_l,
             "conGhe": _conGhe, "soGheBe": _gvR.get("soGheBe"),
             "tiLeVonTrongGheBe": _gvR.get("tiLeVonTrongGheBe")},
            # Cùng bộ núm với `tran-dat-sai-cho`: tiền nằm không mà cơ hội
            # vẫn đi qua nghĩa là một cái trần chặn trước khi tiền cạn.
            # NHƯNG khi cầu dao đang ngắt thì KHÔNG khai núm nào — vặn
            # trần lúc ấy là nới một cái cửa trong khi cửa khác đang khoá
            # có chủ ý, và người vặn sẽ tưởng mình vừa chữa được gì đó.
            [] if _cdN.get("dangNgat")
            # Ghế đầy thì núm đáng nhìn là SỐ GHẾ, không phải trần vốn.
            else ["phanBo.toiDaSoViThe"] if _ghetDay
            else ["ruiRoTong.tranMotCang", "ruiRoTong.tranMotTy"], yDinh="noi"))

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
            ["ruiRoTong.netMoiGioToiThieuBps"], yDinh="siet"))

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

    # ── 8x. GHẾ TRỐNG mà không ai ngồi vào — lời hứa không được giữ ─────
    #
    # `trung_uong` ĐÃ đếm chuyện này (`_vongGheTrongKhongLap`), ĐÃ đưa ra
    # ảnh chụp (`xoayCho.soVongGheTrongKhongLap`), và buồng lái ĐÃ tô đỏ
    # nó từ mức 3 (`web/app.js:1453`). Bảng chẩn thì đọc nó **0 lần** —
    # nên vòng học, thứ chỉ đọc bảng chẩn, không biết nó tồn tại.
    #
    # Đúng vết file này đã tự ghi ở mục 8 ngay dưới: «Bảng ấy đã có, đã
    # hiện trên buồng lái, và trước lượt này KHÔNG AI ĐỌC.» Lần thứ năm.
    #
    # Đo làn thật 05/09/2026: 3 ghế trống, **35 vòng liên tiếp** số vị thế
    # không tăng.
    #
    # Và đây là chỗ nó nối vào một bài lớn hơn. `phan_bo.chia()` xếp hạng
    # bằng `netMoiGioBps` — docstring của chính nó nói rõ vì sao: «20 bps
    # giữ 24 giờ THUA 6 bps giữ 2 giờ, vì vốn quay được mười hai lượt.»
    # Thước ấy GIẢ ĐỊNH vốn quay vòng. Con số 35 là phép đo nói giả định
    # ấy đang sai: ghế trống suốt 35 vòng mà không ai ngồi vào.
    _xc0 = anh.get("xoayCho") or {}
    _gv0 = anh.get("gheVaVon") or {}
    try:
        _kVong = int(_xc0.get("soVongGheTrongKhongLap") or 0)
    except (TypeError, ValueError):
        _kVong = 0
    _conGhe0 = _gv0.get("conGhe")
    if _kVong >= VONG_GHE_TRONG_DANG_NGO and _conGhe0:
        ra.append(TrieuChungHe(
            "ghe-trong-khong-ai-ngoi", 2,
            f"{_kVong} vòng LIÊN TIẾP còn {_conGhe0} ghế trống mà số vị thế "
            f"KHÔNG tăng — lời hứa «Phân Bổ sẽ lấp chỗ» không được giữ. "
            f"Đây không chỉ là mấy cái ghế: bảng xếp hạng vốn dùng "
            f"`netMoiGioBps`, và thước ấy GIẢ ĐỊNH vốn quay vòng được "
            f"(«20 bps giữ 24 giờ thua 6 bps giữ 2 giờ, vì vốn quay được "
            f"mười hai lượt» — docstring `phan_bo`). {_kVong} vòng ghế "
            f"trống là phép đo nói giả định ấy đang SAI, nên mọi thứ hạng "
            f"dựng trên nó đang nghiêng về phía cơ hội kỳ hạn ngắn. Xem "
            f"phễu: cơ hội tốt hơn có đang kẹt ở một trần nào không.",
            {"soVongGheTrongKhongLap": _kVong, "conGhe": _conGhe0,
             "soGhe": _gv0.get("soGhe"),
             "soDangDung": _gv0.get("soDangDung"),
             "nguong": VONG_GHE_TRONG_DANG_NGO},
            # Núm RỖNG. Máy KHÔNG tự đuổi ai vì chuyện này — `trung_uong`
            # đã ghi đúng lý do: «đóng một vị thế mà Phân Bổ không mở lại
            # được là đẩy vốn về tiền mặt ăn 0%». Và nới trần ghế lúc ghế
            # đang TRỐNG thì càng vô nghĩa.
            []))

    # ── 8y. NET quy năm VÔ LÝ, và nó đứng ĐẦU bảng xếp hạng ─────────────
    #
    # `phan_bo.chia()` xếp hạng bằng `netMoiGioBps` — `netUocBps / giuGio`.
    # Với một cửa sổ 15 phút, 555 bps thành 194.598%/năm, và tờ trình ấy
    # KHÔNG lọt qua: nó được ƯU TIÊN, vì bảng xếp theo đúng con số đó.
    #
    # Đo sổ đăng ký làn thật 05/09/2026 — bảy tờ trình trên 1.000%/năm
    # trong 6.000 tờ gần nhất, và NĂM trong đó đã CẤP VỐN và MỞ VỊ THẾ:
    #
    #     544.997 %/năm  prediction.polymarket.v1  DA_DONG
    #     212.900 %/năm  prediction.polymarket.v1  DA_DONG
    #      96.710 %/năm  prediction.polymarket.v1  DA_DONG
    #      16.252 %/năm  dex.round_trip.v1         TU_CHOI
    #
    # Kết cục đo được của chính chúng: hứa 1.889,78 bps/giờ, thực nhận
    # **−261,06**. `CAP_VON` cho ty ấy: 5 lần, 1.426 USD.
    #
    # Đây là TRIỆU CHỨNG, không phải cổng chặn — và đó là một lựa chọn.
    # Bản đầu tôi chặn thẳng ở `ToTrinh.kiem()`, và bộ kiểm bác ngay: đồ
    # gá dùng 100 bps giữ 2 giờ, một cơ hội chênh lệch ngắn hạn HỢP LỆ mà
    # trần cũng chặn luôn. Lẫn «con số quy năm này vô nghĩa» với «cơ hội
    # này không hợp lệ» là chặn nhầm. Nên chỗ này chỉ NÓI RA.
    #
    # Cửa duy nhất từng canh chuyện này là `apy-cao-bat-thuong` của RIÊNG
    # ty Pendle. `rui_ro_tong` chỉ có SÀN (`netMoiGioToiThieuBps`), không
    # có trần; `phan_bo` không có gì.
    _tts = anh.get("toTrinh") or []
    _voLy = []
    for _t in _tts:
        if not isinstance(_t, dict):
            continue
        try:
            _g = float(_t.get("giuGio") or 0.0)
            _n = _t.get("netMoiGioBps")
            if _n is None:
                _nu = _t.get("netUocBps")
                if _nu is None or _g <= 0:
                    continue
                _n = float(_nu) / _g
            _apr = float(_n) * 8760.0 / 100.0
        except (TypeError, ValueError):
            continue
        if _apr > NET_QUY_NAM_VO_LY:
            _voLy.append((_apr, str(_t.get("chienLuoc") or "?"), _g))
    if _voLy:
        _voLy.sort(reverse=True)
        _tong = len(_tts)
        # Hạng của cái cao nhất: đếm xem có bao nhiêu tờ trình khác vượt
        # nó. Bằng 0 nghĩa là nó đang ĐỨNG ĐẦU bảng chia tiền.
        _ten = ", ".join(sorted({c for _, c, _ in _voLy}))
        ra.append(TrieuChungHe(
            "net-quy-nam-vo-ly", 2,
            f"{len(_voLy)}/{_tong} tờ trình vòng này khai NET quy năm trên "
            f"{NET_QUY_NAM_VO_LY:,.0f}% — cao nhất {_voLy[0][0]:,.0f}%/năm "
            f"trên cửa sổ giữ {_voLy[0][2]:g} giờ ({_ten}). Phân bổ xếp "
            f"hạng bằng `netMoiGioBps`, nên những tờ này KHÔNG lọt qua — "
            f"chúng được ƯU TIÊN. Một con số quy năm từ một quãng mười lăm "
            f"phút không phải lợi suất; nó giả định vốn quay lại được ngần "
            f"ấy lượt, mà không ai kiểm điều đó.",
            {"soVoLy": len(_voLy), "soToTrinh": _tong,
             "aprCaoNhat": _voLy[0][0], "giuGioCaoNhat": _voLy[0][2],
             "chienLuoc": sorted({c for _, c, _ in _voLy}),
             "nguong": NET_QUY_NAM_VO_LY},
            # Núm RỖNG. `netMoiGioToiThieuBps` là SÀN, nới nó không chạm
            # tới trần; và không núm nào trong bảng đặt được trần.
            []))

    # ── 8z. PHÍ VÀO LỆNH ăn phần lớn THU GỘP của CẢ HỆ ──────────────────
    #
    # Khác `phi-vao-an-het` ở HAI chỗ, và cả hai đều quan trọng:
    #
    #   · cái kia đo TỪNG TY và đòi ty ấy LỖ GỘP mới nổi. Một hệ mà mọi ty
    #     đều lãi vẫn có thể đốt phần lớn thu nhập vào phí, và lúc ấy không
    #     câu nào được nói ra;
    #   · cái kia đọc `laiLoTachKhoan`; cái này đọc thẳng SỔ CÁI, nên nó là
    #     con số của cả cỗ máy chứ không phải tổng của mấy con số theo ty.
    #
    # Đo làn thật 05/09/2026 (`soCai.theoLoai`):
    #
    #     FUNDING  887.506 bút toán   +223,88 USD   ← toàn bộ thu
    #     PHÍ          457 bút toán   −136,54 USD   ← 61,0% thu gộp
    #     ròng                          +87,34 USD
    #
    # Nguyên nhân đo được nằm ngay cạnh: `lending.rate_rotation` vào 296 ·
    # đóng 289 (97,6%), và 224 trong 289 lần đóng là do XOAY CHỖ. Ty ấy
    # lãi +120,61 nên `phi-vao-an-het` không nổ, còn `NGUONG_CHURN` thì
    # chỉ đổi một chữ trong câu chẩn của bệnh khác — không có triệu chứng
    # nào của riêng nó.
    _sc0 = anh.get("soCai") or {}
    _tl = _sc0.get("theoLoai") or {}
    _phi = _tl.get("PHI") or {}
    _fun = _tl.get("FUNDING") or {}
    try:
        _soPhi = int(_phi.get("so") or 0)
        _tienPhi = abs(float(_phi.get("tongUsd") or 0.0))
        _thu = float(_fun.get("tongUsd") or 0.0)
    except (TypeError, ValueError):
        _soPhi = _tienPhi = _thu = 0
    # Thu ÂM hoặc bằng 0 thì tỉ lệ vô nghĩa — chia cho nó là bịa ra một
    # phần trăm. Ca ấy thuộc `ty-lo`, không thuộc đây.
    if _soPhi >= TOI_THIEU_BUT_TOAN_PHI and _thu > 0:
        _tiPhi = _tienPhi / _thu
        if _tiPhi >= NGUONG_PHI_TREN_THU:
            _tk0 = anh.get("laiLoTachKhoan") or {}
            _xau0 = None
            for _m, _o in _tk0.items():
                if not isinstance(_o, dict):
                    continue
                _v = int(_o.get("soLanVaoLenh") or 0)
                _dg = int(_o.get("soLanDong") or 0)
                _dx = int(_o.get("soLanDongXoayCho") or 0)
                if _v >= TOI_THIEU_LAN_VAO and (_xau0 is None or _dx > _xau0[3]):
                    _xau0 = (_m, _v, _dg, _dx)
            _viX = ""
            if _xau0 and _xau0[2]:
                _viX = (f" Nhiều lần đóng nhất là {_xau0[0]}: vào {_xau0[1]} · "
                        f"đóng {_xau0[2]}, trong đó {_xau0[3]} lần do XOAY CHỖ "
                        f"— tức phần lớn phí ấy là chi phí VẬN HÀNH, không "
                        f"phải chi phí của chiến lược.")
            ra.append(TrieuChungHe(
                "phi-an-phan-lon-thu", 2,
                f"phí vào lệnh {_tienPhi:,.2f} USD trên thu gộp "
                f"{_thu:,.2f} USD — {_tiPhi:.1%}, còn lại ròng "
                f"{_thu - _tienPhi:+,.2f} USD. Đây là con số của CẢ HỆ đọc "
                f"thẳng từ sổ cái, nên nó nói được cả khi mọi ty đều đang "
                f"lãi và `phi-vao-an-het` im." + _viX,
                {"phiUsd": _tienPhi, "thuGopUsd": _thu, "tiLe": _tiPhi,
                 "soButToanPhi": _soPhi, "rongUsd": _thu - _tienPhi,
                 "tyDongNhieuNhat": _xau0[0] if _xau0 else None,
                 "soLanDongXoayCho": _xau0[3] if _xau0 else None},
                # Núm RỖNG. Phí cao vì vị thế bị ĐÓNG SỚM, mà chuyện đóng
                # sớm do xoay chỗ quyết — không trần nào trong bảng núm
                # chạm tới nó. Khai một núm ở đây là chỉ sang chỗ không
                # chữa được gì.
                []))

    # ── 8a. KHÔNG ĐỐI CHIẾU ĐƯỢC — vòng phản hồi đói ────────────────────
    #
    # Vòng bên dưới bỏ qua IM LẶNG mọi ty có dưới `TOI_THIEU_DOI_CHIEU`
    # lần đối chiếu. Đúng — dưới ngần ấy thì lệch là tiếng ồn. Nhưng im
    # lặng ở đây đọc y hệt «đã đo, và không sao cả», trong khi sự thật là
    # KHÔNG ĐO ĐƯỢC GÌ.
    #
    # Và chuyện ấy đắt hơn nó trông. `phan_bo.chia()` xếp hạng bằng
    # `netMoiGioBps` — con số ty HỨA lúc trình. Không đối chiếu được thì
    # lời hứa ấy chưa ai kiểm, tức cả thứ tự chia tiền chưa ai kiểm.
    # Khâm Thiên Giám có `HieuChinh` đứng TRƯỚC Kelly đúng vì lý do này;
    # Thị Bạc Ty thì chưa có lớp nào tương đương.
    #
    # Đo làn thật 05/09/2026:
    #
    #     ty                     đóng  đối chiếu  giữ quá ngắn  thiếu vế
    #     lending.rate_rotation   289      13         211          65
    #     amm.fee_farming          37       4          20          13
    #     basis.cash_carry         29       0          29           0
    #
    # 17 quan sát dùng được trên 355 lần đóng — 4,8%. Không ty nào chạm
    # nổi ngưỡng 20, nên `hua-qua-he` im hoàn toàn.
    _dong = _dc = _ngan = _thieu = 0
    _xau = None
    for _ma, _o in dvt.items():
        try:
            _d = int(_o.get("soDong") or 0)
            _k = int(_o.get("soDoiChieuDuoc") or 0)
        except (TypeError, ValueError, AttributeError):
            continue
        _dong += _d
        _dc += _k
        _ngan += int(_o.get("soGiuQuaNgan") or 0)
        _thieu += int(_o.get("soThieuVe") or 0)
        if _d and (_xau is None or _k / _d < _xau[1]):
            _xau = (_ma, _k / _d, _d, _k)
    if _dong >= TOI_THIEU_DONG_DE_CHAN:
        _ti = _dc / _dong
        if _ti < NGUONG_DOI_CHIEU_DUOC:
            # Gọi tên nguyên nhân ÁP ĐẢO, đừng nói chung chung: «giữ quá
            # ngắn» và «thiếu vế» đòi hai cách chữa khác hẳn nhau.
            _vi = ""
            if _ngan > _thieu and _dong:
                _vi = (f" Nguyên nhân áp đảo là GIỮ QUÁ NGẮN "
                       f"({_ngan}/{_dong} lần đóng) — vị thế chết trước khi "
                       f"tới mốc thu đầu tiên, nên không có gì để đối chiếu.")
            elif _thieu:
                _vi = (f" Nguyên nhân áp đảo là THIẾU VẾ THU "
                       f"({_thieu}/{_dong} lần đóng) — đã đóng mà không ghi "
                       f"lại thu được bao nhiêu.")
            ra.append(TrieuChungHe(
                "khong-doi-chieu-duoc", 2,
                f"chỉ {_dc}/{_dong} lần đóng ({_ti:.1%}) đối chiếu được lời "
                f"hứa với thực nhận. Phân bổ xếp hạng bằng `netMoiGioBps` — "
                f"con số ty HỨA lúc trình — nên không đối chiếu được nghĩa "
                f"là THỨ TỰ CHIA TIỀN chưa ai kiểm." + _vi
                + (f" Tệ nhất: {_xau[0]} với {_xau[3]}/{_xau[2]}."
                   if _xau else "")
                + " Và `hua-qua-he` IM ở đây chứ không kêu, vì nó đòi "
                  f"{TOI_THIEU_DOI_CHIEU} lần đối chiếu mới nói — im lặng ấy "
                  "đọc y hệt «đã đo, và không sao cả».",
                {"soDong": _dong, "soDoiChieuDuoc": _dc, "tiLe": _ti,
                 "soGiuQuaNgan": _ngan, "soThieuVe": _thieu,
                 "tyTeNhat": _xau[0] if _xau else None,
                 "nguong": NGUONG_DOI_CHIEU_DUOC},
                # Núm RỖNG. Không đo được lời hứa KHÔNG phải bệnh của một
                # cái trần — vặn trần lúc này là vặn theo một bảng xếp
                # hạng mà chính triệu chứng này vừa nói là chưa ai kiểm.
                []))

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
            ["ruiRoTong.netMoiGioToiThieuBps"], yDinh="siet"))

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


def de_xuat(trieu: list[TrieuChungHe], cau_hinh: dict,
            boQua=()) -> list[DeXuatHe]:
    """Từ triệu chứng ra đề xuất vặn — **chỉ đề xuất, không vặn**.

    Trả về nhiều nhất MỘT đề xuất, từ triệu chứng nặng nhất. Cùng lý do với
    tầng ty: vặn hai núm rồi thấy khá lên thì không biết núm nào có công.

    `boQua` là những núm ĐÃ THỬ và đo ra KHÔNG ĐỔI GÌ trong chính vòng
    học này. Không có nó thì một núm bất động làm đứt cả vòng: `hoc()`
    lấy đúng một đề xuất, đo, cổng duyệt trả «hoà», và vòng ấy kết thúc
    tay trắng — trong khi một triệu chứng khác có thể đang khai một núm
    vặn được.

    Đo làn thật 05/09/2026: `ruiRoTong.tranMotCoHoi` quét 0,05 → 0,35 cho
    ĐÚNG một con số, vì trần ấy là 150.000 USD trong khi vị thế lớn nhất
    25.000 — cao gấp sáu lần chỗ nó đáng chặn. Hai triệu chứng khai đúng
    núm ấy.

    **`boQua` KHÔNG phải cửa để đi xin cho tới lúc được gật.** Nó chỉ
    nhận núm mà phép đo nói là không đổi gì. Núm bị từ chối vì «bản đang
    chạy tốt hơn» hay «chỉ hơn nhờ ôm rủi ro đậm hơn» thì KHÔNG được bỏ
    qua — đó là câu trả lời thật, và thử tiếp là mài cho qua cổng.
    """
    boQua = set(boQua or ())
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
            if nut in boQua:
                continue
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
            # Ý ĐỊNH do chính bệnh khai. Không khai thì KHÔNG đề xuất gì
            # — im lặng còn hơn vặn nhầm chiều, và `kiem_chan_doan_he`
            # bắt mọi bệnh có núm mà quên khai.
            if t.yDinh not in ("noi", "siet"):
                continue
            noi = t.yDinh == "noi"
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
