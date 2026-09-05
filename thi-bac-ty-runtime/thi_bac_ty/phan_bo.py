"""PHÂN BỔ VỐN — chia tiền, và chịu trách nhiệm về cái đã chia.

Rủi Ro Tổng nói *"tờ này cho tối đa $X"*. Phân Bổ nói *"trong tất cả những
tờ được phép, tôi rót thật vào đâu, bao nhiêu, và giữ lại bao nhiêu tiền
mặt"*.

    $1.000 có sẵn

    Perp     xin $300  ·  Rủi Ro Tổng cho tối đa $300
    Tín dụng xin $400  ·  cho tối đa $400
    Chênh lệch xin $500 ·  cho tối đa $200   ← đã bị cắt
    Cơ bản   xin $300  ·  cho tối đa $300

    tổng được phép = $1.200 > $1.000 có

              ↓  Phân Bổ quyết

    Perp        $200
    Tín dụng    $400
    Chênh lệch  $0
    Cơ bản      $300
    dự trữ      $100

## Cấp TUẦN TỰ, không cấp song song — và đây là chỗ dễ sai nhất

Rủi Ro Tổng xét từng tờ trên **danh mục hiện tại**. Hai tờ cùng chạm Binance,
xét riêng thì cả hai đều lọt; cấp cả hai cùng lúc thì vượt trần cảng.

Nên Phân Bổ cấp từng tờ một, và **xét lại** trên danh mục đã cập nhật sau
mỗi lần cấp. Chậm hơn, nhưng đó là cách duy nhất trần phơi nhiễm còn nghĩa.

Xét trước-cấp-sau hàng loạt là một lỗi kinh điển và nó im lặng: mọi tờ đều
"đã qua rủi ro", tổng lại thì vượt, và không dòng log nào báo.

## Xếp hạng theo cái gì

    điểm = netMoiGioBps × tinCay × (1 − diemRuiRo)

Ba thừa số, và mỗi thừa số chặn một cách tự lừa:

  * `netMoiGioBps` — không phải `netBps` trần. 20 bps giữ 24 giờ thua 6 bps
    giữ 2 giờ, vì vốn quay được mười hai lượt.
  * `tinCay` — một cơ hội đẹp dựng trên dữ liệu mù không đáng bằng một cơ
    hội vừa phải dựng trên dữ liệu chắc.
  * `1 − diemRuiRo` — lợi nhuận kỳ vọng phải chiết khấu theo rủi ro, nếu
    không thì cỗ máy luôn chọn thứ nguy hiểm nhất.

**NET âm thì không xếp hạng, loại thẳng.** Nhân một số âm với hai thừa số
trong [0,1] vẫn ra số âm, nhưng "âm ít" sẽ đứng trên "âm nhiều" và cỗ máy
vẫn rót tiền vào chỗ lỗ ít nhất. Lỗ ít vẫn là lỗ.

## Dự trữ tiền mặt là một quyết định, không phải phần thừa

`tiLeDuTru` giữ lại một phần NAV bằng tiền mặt kể cả khi còn cơ hội tốt. Lý
do: cơ hội tốt hơn có thể đến sau, và một danh mục dùng hết vốn thì không
vào được cơ hội ấy — chi phí cơ hội của việc **không còn tiền**.
"""
from __future__ import annotations

from dataclasses import dataclass, field

MAC_DINH = {
    "tiLeDuTru": 0.20,        # giữ lại phần NAV này bằng tiền mặt
    "toiThieuMotLanUsd": 25.0,  # rót ít hơn thì phí cố định ăn hết
    "toiDaSoViThe": 12,       # quá nhiều vị thế thì không theo dõi nổi

    #: Chưa đo được sức chứa thì coi như chỉ rót được ngần này phần số xin.
    #: Không phải 1 (thưởng cho sự mù) và không phải 0 (chặn hẳn — việc ấy
    #: là của `rui_ro_tong`, không phải của bảng xếp hạng).
    "phatChuaDoSucChua": 0.35,

    #: Trần `netMoiGioBps` dùng ĐỂ XẾP HẠNG. 0 = tắt.
    #:
    #: 0,1142 bps/giờ = 1.000%/năm — cùng ngưỡng với `xoay_cho.APR_TOI_DA`
    #: và `chan_doan_he.NET_QUY_NAM_VO_LY`. Trần này KHÔNG loại cơ hội: nó
    #: chỉ thôi cho một con số quy từ cửa sổ mười lăm phút đứng trên mọi
    #: thứ khác bằng ba bậc độ lớn.
    #:
    #: Lợi suất thật đo được trên máy này nằm ở 2,6%–24%/năm, tức 0,0003 –
    #: 0,0027 bps/giờ — cách trần này bốn mươi lần. Rác bắt đầu từ
    #: 16.252%/năm. Trần nằm giữa một khoảng trống rất rộng, không vặn cho
    #: vừa dữ liệu.
    "netMoiGioTranXepHangBps": 1000.0 * 100.0 / (365.0 * 24.0),

    # Vốn khoá 90 ngày ở 10%/năm THUA vốn rút được ngay ở 7%/năm, vì trong 90
    # ngày ấy có thể xuất hiện thứ tốt hơn mà ta không vào được. Chi phí đó
    # KHÔNG nằm trong APR của chính nó, nên phải trừ ở đây.
    "thamChieuKhoaGio": 168.0,     # 7 ngày
    "phatChuaDoKhoaVon": 0.70,
}

#: MÃ đứng đầu mỗi câu từ chối của tầng này.
#:
#: Câu thì để người đọc; mã để MÁY đọc. Chẩn đoán muốn biết «lý do chặn
#: nhiều nhất là gì» thì nó phải nhận ra được lý do, mà nhận bằng cách dò
#: chuỗi trong một câu có số nhúng bên trong (`đã đủ 12 vị thế…`) là dựng
#: một mối nối gãy ngay lần đầu ai đó sửa câu chữ.
#:
#: Cầu dao đã làm đúng thế từ trước (`CẦU DAO NGẮT: von-ngoai-mu: …`) —
#: đây chỉ là mang cùng kỷ luật ấy xuống tầng phân bổ.
MA_TU_CHOI = {
    "net-am":          "NET mỗi giờ ≤ 0 — lỗ ít vẫn là lỗ",
    "tran-vi-the":     "đã đủ {n} vị thế — quá nhiều thì không theo dõi nổi",
    "duoi-san-mot-lan": ("chỉ còn cấp được {cap:.2f} USD, dưới sàn {san} — "
                         "phí cố định ăn hết"),
    "het-tien-mat":    "Danh Mục từ chối — không đủ tiền mặt",
}


def ly_do(ma: str, **kw) -> str:
    """`"tran-vi-the: đã đủ 12 vị thế — …"`. Mã trước, câu sau.

    Mã lạ thì NÉM, không trả về một câu trống: một lý do từ chối không tên
    là một lý do không đếm được, và bảng «vì sao bị từ chối» sẽ có một cột
    rỗng mà không ai biết nó từ đâu ra.
    """
    return f"{ma}: {MA_TU_CHOI[ma].format(**kw)}"


@dataclass
class LatCatPhanBo:
    luc: str
    vonKhaDungUsd: float
    duTruUsd: float
    daCap: list = field(default_factory=list)
    tuChoi: list = field(default_factory=list)
    tongCapUsd: float = 0.0

    def tom_tat(self) -> dict:
        return {"luc": self.luc, "vonKhaDungUsd": self.vonKhaDungUsd,
                "duTruUsd": self.duTruUsd, "tongCapUsd": self.tongCapUsd,
                "soCap": len(self.daCap), "soTuChoi": len(self.tuChoi),
                "daCap": list(self.daCap), "tuChoi": list(self.tuChoi)}


class PhanBo:
    def __init__(self, cau_hinh: dict | None = None) -> None:
        self.c = {**MAC_DINH, **(cau_hinh or {})}

    def diem_chi_tiet(self, tt, diemRuiRo: float | None,
                      tranUsd: float | None = None) -> dict:
        """Điểm xếp hạng, MỔ RA từng thừa số.

        Trả cả các thừa số chứ không chỉ con số cuối, vì một quyết định phân
        bổ phải cãi lại được. Nhìn một con số trần thì không ai biết cơ hội
        ấy thua vì rủi ro cao hay vì sức chứa mỏng.

        ## Điểm là ĐÔ-LA MỖI GIỜ, không phải phần trăm

        Đây là chỗ bản đầu làm sai, và nó sai đúng theo cách §13 cảnh báo:

            DEX arb    lãi 0,40%    nhưng chỉ rót nổi $80
            Lending    lãi 7%/năm   nhưng rót được $100.000

        Xếp theo phần trăm thì DEX thắng tuyệt đối. Xếp theo tiền thì không.
        Nhân thêm một *hệ số* sức chứa cũng không cứu: hệ số chỉ làm DEX
        thắng ít hơn, chứ vẫn thắng.

        Nên điểm phải là lợi suất nhân với số vốn RÓT ĐƯỢC THẬT:

            netMoiGioBps × rotDuocUsd     xấp xỉ đô-la mỗi giờ
            × tinCay                       ty tự chấm mình tin bao nhiêu
            × (1 − rủi ro)                 rủi ro không bù trừ, lấy mặt cao nhất
            × heSoKhoaVon                  §14: khoá lâu là từ chối cơ hội khác

        `rotDuocUsd` là chỗ CHẬT NHẤT trong ba con số: ty xin bao nhiêu, thị
        trường chứa bao nhiêu, và lúc này còn cho rót bao nhiêu.

        Hệ quả đúng như phải thế: cùng một trần khả dụng, cơ hội chứa được
        nhiều hơn xếp trên; nhưng khi trần khả dụng nhỏ hơn cả hai thì hai
        cơ hội quay về so bằng lợi suất — vì lúc ấy phần sức chứa thừa không
        dùng tới được, và một thước tính công cho phần thừa ấy là thước nói
        dối.
        """
        net = tt.net_moi_gio_bps
        # ── KẸP TRẦN cho việc XẾP HẠNG, không loại cơ hội ────────────────
        #
        # `net_moi_gio_bps` = `netUocBps / giuGio`. Với một cửa sổ mười lăm
        # phút, 555 bps thành 2.220 bps/giờ — 194.598%/năm — và tờ trình ấy
        # KHÔNG lọt qua bảng này: nó đứng ĐẦU.
        #
        # `kham_ngoai/ty_tien_doan.py` biết trước chuyện này và đã khai:
        # «`giuGio` là nửa đời, và đó là PROXY… khai
        # `giu-gio-la-nua-doi-khong-phai-ky-han` trong `phiConThieu` để
        # không ai đọc `netMoiGioBps` của ty này như đọc của ty funding.»
        # Lời khai có, bộ kiểm canh rằng nó ĐƯỢC KHAI — và file này chưa
        # bao giờ đọc `phiConThieu`. Cờ tính rồi bỏ qua.
        #
        # Đo sổ đăng ký làn thật 05/09/2026: bảy tờ trình trên 1.000%/năm,
        # NĂM trong đó đã cấp vốn và mở vị thế; kết cục thực nhận −261,06
        # bps/giờ trên lời hứa 1.889,78.
        #
        # KẸP chứ không LOẠI, và đó là chỗ bản trước của tôi sai: chặn ở
        # `ToTrinh.kiem()` cũng chặn luôn 100 bps giữ 2 giờ — một cơ hội
        # chênh lệch ngắn hạn hợp lệ. Kẹp thì cơ hội vẫn được xét, chỉ
        # thôi đứng trên mọi thứ khác bằng ba bậc độ lớn.
        _tran = float(self.c.get("netMoiGioTranXepHangBps") or 0.0)
        netXep = min(net, _tran) if _tran > 0 else net
        if net <= 0:
            # Lỗ ít vẫn là lỗ. Loại thẳng, không để các thừa số kia cứu.
            return {"diem": float("-inf"), "netMoiGioBps": net,
                    "vi": "NET mỗi giờ <= 0"}

        tin = 1.0 if tt.tinCay is None else max(0.0, min(1.0, tt.tinCay))
        rr = 0.5 if diemRuiRo is None else max(0.0, min(1.0, diemRuiRo))

        # ── §13 · rót được bao nhiêu THẬT ───────────────────────────────
        rot = float(tt.vonCanUsd)
        if tt.sucChuaToiDaUsd is None:
            # Mù sức chứa thì coi như rót được ít hơn — không phải cấm, và
            # cũng không phải cho qua như thể đã đo.
            rot *= float(self.c["phatChuaDoSucChua"])
        else:
            rot = min(rot, float(tt.sucChuaToiDaUsd))
        if tranUsd is not None:
            rot = min(rot, max(0.0, float(tranUsd)))

        # ── §14 · khoá vốn ──────────────────────────────────────────────
        tc = float(self.c["thamChieuKhoaGio"])
        if tt.khoaVonDenGio is None:
            hs_khoa = float(self.c["phatChuaDoKhoaVon"])
        elif tc <= 0:
            hs_khoa = 1.0
        else:
            # 1/(1+x): khoá 0 giờ ra 1,00 · khoá đúng tham chiếu ra 0,50 ·
            # khoá gấp mười ra 0,09. Giảm dần, không bao giờ chạm 0 — khoá
            # lâu là bất lợi chứ không phải phạm luật; phạm luật thì
            # `rui_ro_tong.khoaVonToiDaGio` đã chặn từ trước.
            hs_khoa = 1.0 / (1.0 + tt.khoaVonDenGio / tc)

        d = netXep * rot * tin * (1.0 - rr) * hs_khoa
        return {"diem": d, "netMoiGioBps": net,
                # Khai cả con số ĐÃ KẸP: giấu nó đi thì một tờ trình bị
                # kẹp trông y hệt một tờ không bị, và không ai biết thứ tự
                # vừa đổi vì cái gì.
                "netMoiGioXepBps": netXep,
                "biKepXepHang": netXep < net,
                "rotDuocUsd": rot,
                "tinCay": tin, "motTruRuiRo": 1.0 - rr,
                "heSoKhoaVon": hs_khoa, "tranXepHangUsd": tranUsd,
                "gioVonBiGiu": tt.gio_von_bi_giu}

    def diem(self, tt, diemRuiRo: float | None,
             tranUsd: float | None = None) -> float:
        """Chỉ con số. Muốn biết vì sao thì gọi `diem_chi_tiet()`."""
        return self.diem_chi_tiet(tt, diemRuiRo, tranUsd)["diem"]

    def chia(self, toTrinh: list, rui_ro_tong, danh_muc, so_cai=None,
             luc: str = "") -> LatCatPhanBo:
        """Chia vốn cho một lô tờ trình. **Thay đổi `danh_muc` tại chỗ.**

        Trả về lát cắt ghi lại đã cấp gì và từ chối gì — kèm lý do, luôn kèm
        lý do. Một quyết định phân bổ không giải thích được thì không kiểm
        toán được, và cái không kiểm toán được thì không sửa được.
        """
        from .so_cai import ButToan
        from .danh_muc import ViThe

        nav = danh_muc.navUsd
        du_tru = nav * float(self.c["tiLeDuTru"])
        lat = LatCatPhanBo(luc=luc or _bay_gio(),
                           vonKhaDungUsd=max(0.0, danh_muc.tienMatUsd - du_tru),
                           duTruUsd=du_tru)

        # Xếp hạng TRƯỚC, cấp SAU. Xếp hạng dùng điểm rủi ro sơ bộ (chưa xét
        # danh mục) chỉ để định thứ tự; trần thật vẫn do `xet()` quyết ở
        # từng bước cấp.
        # Trần dùng để XẾP HẠNG: chỗ chật nhất giữa "còn bao nhiêu tiền để
        # rót" và "một cơ hội đơn lẻ được ôm bao nhiêu". Dùng chung một trần
        # cho mọi tờ trình nên nó không thiên vị ai — nó chỉ cắt phần sức
        # chứa THỪA mà lúc này không dùng tới được.
        tran_xep = lat.vonKhaDungUsd
        try:
            tran_xep = min(tran_xep, nav * float(rui_ro_tong.c["tranMotCoHoi"]))
        except (AttributeError, KeyError, TypeError):
            pass

        xep = []
        for tt in toTrinh:
            d, _ = rui_ro_tong.diem(tt)
            ct = self.diem_chi_tiet(tt, d, tran_xep)
            xep.append((ct["diem"], ct, tt))
        xep.sort(key=lambda x: x[0], reverse=True)

        for diem, chiTiet, tt in xep:
            if diem == float("-inf"):
                lat.tuChoi.append({"maToTrinh": tt.ma, "chienLuoc": tt.chienLuoc,
                                   "lyDo": ly_do("net-am")})
                continue
            if len(danh_muc.viThe) >= int(self.c["toiDaSoViThe"]):
                lat.tuChoi.append({"maToTrinh": tt.ma, "chienLuoc": tt.chienLuoc,
                                   "lyDo": ly_do(
                                       "tran-vi-the",
                                       n=self.c["toiDaSoViThe"])})
                continue

            # XÉT LẠI trên danh mục ĐÃ CẬP NHẬT — xem docstring đầu file.
            pq = rui_ro_tong.xet(tt, danh_muc)
            if not pq.duyet:
                lat.tuChoi.append({**pq.tom_tat(), "diemXep": diem})
                if so_cai:
                    so_cai.ghi(ButToan(
                        "TU_CHOI", "; ".join(pq.lyDo) or "Rủi Ro Tổng từ chối",
                        0.0, tt.chienLuoc, tt.ma,
                        {"xinUsd": tt.vonCanUsd, "diemXep": diem}))
                continue

            con = danh_muc.tienMatUsd - du_tru
            cap = min(pq.choToiDaUsd, con)
            if cap < float(self.c["toiThieuMotLanUsd"]):
                lat.tuChoi.append({
                    "maToTrinh": tt.ma, "chienLuoc": tt.chienLuoc,
                    "lyDo": ly_do("duoi-san-mot-lan", cap=cap,
                                  san=self.c["toiThieuMotLanUsd"]),
                    "choToiDaUsd": pq.choToiDaUsd})
                continue

            # Chia đều cho các chân: mỗi chân cần đúng phần vốn của nó.
            moi_chan = cap / len(tt.chan)
            chan = [ViThe(tt.ma, tt.chienLuoc, c.ben, c.cang, c.taiSan,
                          moi_chan, c.chuoi, c.loai, lat.luc)
                    for c in tt.chan]
            if not danh_muc.cam_ket(tt.ma, chan):
                lat.tuChoi.append({"maToTrinh": tt.ma, "chienLuoc": tt.chienLuoc,
                                   "lyDo": ly_do("het-tien-mat")})
                continue

            lat.daCap.append({
                "maToTrinh": tt.ma, "chienLuoc": tt.chienLuoc,
                "taiSan": tt.taiSan, "xinUsd": tt.vonCanUsd,
                "choToiDaUsd": pq.choToiDaUsd, "capUsd": cap,
                "diemXep": diem, "diemXepChiTiet": chiTiet,
                "diemRuiRo": pq.diemRuiRo,
                "khoaVonDenGio": tt.khoaVonDenGio,
                "thanhKhoanThoatUsd": tt.thanhKhoanThoatUsd,
                "biCat": pq.biCat, "lyDoCat": list(pq.lyDoCat),
                "netMoiGioBps": tt.net_moi_gio_bps})
            lat.tongCapUsd += cap
            if so_cai:
                so_cai.ghi(ButToan(
                    "CAP_VON",
                    (f"xếp hạng {diem:.4f} · xin {tt.vonCanUsd:.0f} · "
                     f"trần {pq.choToiDaUsd:.0f} · cấp {cap:.0f}"
                     + (" (BỊ CẮT: " + "; ".join(pq.lyDoCat) + ")"
                        if pq.biCat else "")),
                    cap, tt.chienLuoc, tt.ma,
                    {"netMoiGioBps": tt.net_moi_gio_bps,
                     "diemRuiRo": pq.diemRuiRo, "tinCay": tt.tinCay,
                     "chan": [c.tom_tat() for c in tt.chan],
                     "bangChung": list(tt.bangChung)}))
        return lat

    def tom_tat(self) -> dict:
        return dict(self.c)


def _bay_gio() -> str:
    import datetime as dt
    return dt.datetime.now(dt.timezone.utc).isoformat(
        timespec="milliseconds").replace("+00:00", "Z")
