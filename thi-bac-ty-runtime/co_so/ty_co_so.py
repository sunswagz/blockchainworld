"""TY CƠ SỞ — cash-and-carry: mua giao ngay, bán khống perp, CÙNG một sàn.

Cùng họ `phai-sinh` với ty chênh lệch funding, nhưng khác nhau ở đúng chỗ
đáng kể:

    bac/     LONG perp sàn A · SHORT perp sàn B  → ăn CHÊNH LỆCH funding
    co_so/   LONG giao ngay  · SHORT perp cùng sàn → ăn MỨC funding tuyệt đối

Khi cả bốn sàn cùng funding dương, chênh lệch giữa chúng mỏng và `bac/`
không thấy gì — trong khi mức tuyệt đối vẫn đáng ăn. Ngược lại khi funding
âm đều thì `co_so/` im còn `bac/` vẫn có việc. Hai ty nhìn hai mặt của cùng
một thị trường, và đó là lý do cả hai cùng đáng tồn tại.

Đây cũng chính là cơ chế Ethena chạy ở quy mô giao thức: tài sản bảo chứng
được phòng hộ delta-neutral bằng phái sinh, và một phần doanh thu đến từ
funding cộng basis.

## Cùng MỘT sàn, có chủ ý

Mua giao ngay ở sàn A rồi bán khống perp ở sàn B là thêm hai thứ ta chưa
làm được: chuyển vốn giữa hai sàn, và rủi ro một sàn sập trong khi chân kia
còn mở. Cùng sàn thì ký quỹ được bù trừ ngay trong tài khoản ấy, và
`phiConThieu` ngắn đi đúng một khoản.

## BASIS không phải THU NHẬP

Đây là chỗ dễ tự lừa nhất của ty này.

    mark perp 78.217 · giao ngay 78.237  →  basis −2,6 bps

Con số ấy KHÔNG phải lãi. Perp không có ngày đáo hạn nên không có gì bảo
đảm nó hội tụ về giao ngay — nó có thể rộng ra và ở đó hàng tháng. Cộng
basis vào NET là báo cáo một khoản lãi chưa ai trả.

Nên `netUocBps` ở đây CHỈ có funding đếm theo mốc. Basis vào `ruiRo` và vào
`bangChung`, không vào NET. Basis âm sâu còn là một cửa CHẶN, vì nó nghĩa
là ta phải mua giao ngay đắt hơn giá thanh lý của chân short.
"""
from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field, replace

from phai_sinh_chung.dong_ho import dong_ho
from phai_sinh_chung.dongho import dem_moc, moi_gio
from san_chung.giao_ngay import DinhSo, SanGiaoNgay
from thi_bac_ty.khuon_ty import Ty
from thi_bac_ty.to_trinh import Chan, RuiRo, ToTrinh

MA_CHIEN_LUOC = "basis.cash_carry.v1"
HO = "phai-sinh"

CONFIG = {
    "quet": {
        "ma": ["BTC", "ETH"],
        # Chỉ sàn có CẢ giao ngay lẫn perp, và ta đọc được cả hai.
        "san": ["binance", "okx", "bybit"],
        # Carry là chiến lược GIỮ, không phải giao dịch tám giờ.
        #
        # Phí khứ hồi bốn lần taker là ~20 bps, một khoản CỐ ĐỊNH trả một
        # lần. Giữ một chu kỳ funding thì thu 0,9 bps và lỗ 19 — giữ 21 chu
        # kỳ (7 ngày) thì thu ~18 bps và bắt đầu có nghĩa.
        #
        # Nhưng cửa sổ dài đổi lấy một GIẢ ĐỊNH MẠNH HƠN: gross tính bằng
        # cách nhân mức funding HIỆN TẠI cho số mốc trong cửa sổ, tức là
        # giả định nó giữ nguyên suốt bảy ngày. Nó không giữ nguyên. Nên
        # `_tin_cay()` hạ dần theo độ dài cửa sổ, và `bangChung` nói thẳng
        # giả định ấy ra.
        "giuGio": 168.0,
        "hetGioHoiGiay": 15.0,
    },
    "ruiRo": {
        "netToiThieuBps": 0.5,
        # Basis âm sâu = phải mua giao ngay ĐẮT hơn giá thanh lý chân short.
        # Không phải cơ hội; là một khoản lỗ trả trước.
        "basisAmToiDaBps": 25.0,
        # Basis dương quá rộng cũng đáng ngờ: hoặc một trong hai giá sai,
        # hoặc thị trường đang định giá một rủi ro ta chưa thấy.
        "basisDuongToiDaBps": 150.0,
        "doiHoiItNhatMotMoc": True,
        "tuoiToiDaGiay": 20.0,
        "lechDongHoToiDaGiay": 10.0,
    },
    # Taker giao ngay + taker perp, mỗi chiều, và ×2 cho khứ hồi.
    "phiTakerBps": {"binance": 5.0, "okx": 5.0, "bybit": 5.5, "_khac": 7.5},
    "von": {"moiCoHoiUsd": 200.0},
    "sucChua": {"phanOi": 0.0005, "tranUsd": 100_000.0, "sanUsd": 25.0},
}

_VON_TOI_THIEU = 200.0

PHI_CON_THIEU = (
    "vay-coin-neu-ban-khong-giao-ngay",
    "basis-luc-thoat",          # hai giá rời nhau lúc đóng
    "von-bi-khoa",              # chân giao ngay chiếm vốn, không đòn bẩy
    "thue",
)
SUC_CHUA_CON_THIEU = ("do-sau-so-lenh-perp",)

NHAN = {
    "thieu-giao-ngay": "sàn không có giá giao ngay đọc được",
    "thieu-perp": "sàn không có mark hoặc funding đọc được",
    "basis-am-qua-sau": "basis âm quá sâu — mua giao ngay đắt hơn giá thanh lý",
    "basis-duong-qua-rong": "basis dương quá rộng — một trong hai giá đáng ngờ",
    "khong-moc-nao": "cửa sổ giữ không chứa mốc kết toán nào",
    "net-duoi-nguong": "NET sau phí dưới ngưỡng",
    "du-lieu-cu": "dữ liệu quá cũ",
    "dong-ho-lech": "đồng hồ máy lệch quá xa giờ sàn",
}

CUA = ("netToiThieuBps", "basisAmToiDaBps", "basisDuongToiDaBps",
       "doiHoiItNhatMotMoc", "tuoiToiDaGiay", "lechDongHoToiDaGiay")


@dataclass(frozen=True)
class CoHoiCoSo:
    san: str
    ma: str
    giaoNgay: float          # giá ta MUA giao ngay (ask)
    mark: float              # mark perp
    fundingMoiGio: float     # đã chuẩn hoá
    intervalGio: float
    soMoc: int
    mocDauMs: int
    vonXinUsd: float
    giuGio: float
    grossBps: float
    phiBps: float
    netBps: float
    basisBps: float
    sucChuaToiDaUsd: float | None
    tuoiGiay: float
    duyet: bool = False
    lyDo: tuple = ()
    lyDoMa: tuple = ()

    @property
    def netMoiGioBps(self) -> float:
        return self.netBps / self.giuGio if self.giuGio else 0.0

    def tom_tat(self) -> dict:
        return {"san": self.san, "ma": self.ma, "giaoNgay": self.giaoNgay,
                "mark": self.mark, "basisBps": self.basisBps,
                "fundingMoiGio": self.fundingMoiGio,
                "intervalGio": self.intervalGio, "soMoc": self.soMoc,
                "vonXinUsd": self.vonXinUsd, "giuGio": self.giuGio,
                "grossBps": self.grossBps, "phiBps": self.phiBps,
                "netBps": self.netBps, "netMoiGioBps": self.netMoiGioBps,
                "sucChuaToiDaUsd": self.sucChuaToiDaUsd,
                "tuoiGiay": self.tuoiGiay, "duyet": self.duyet,
                "lyDo": list(self.lyDo),
                "lyDoMa": [list(x) for x in self.lyDoMa]}


def basis_bps(mark: float, giaoNgay: float) -> float:
    """`(mark − giao ngay) / giao ngay`, tính bằng bps. Dương = perp đắt hơn."""
    if giaoNgay <= 0:
        return 0.0
    return (mark - giaoNgay) / giaoNgay * 10_000.0


def phi_khu_hoi_bps(san: str, bang: dict) -> float:
    """Hai chân, hai chiều, cùng một sàn.

    `× 2 chân × 2 chiều` = bốn lần phí taker. Tính một chân hay một chiều
    thôi là báo cáo một phần tư tới một nửa chi phí, và với edge tính bằng
    bps thì đó chính là phần quyết định lỗ hay lãi.
    """
    return 4.0 * float(bang.get(san, bang.get("_khac", 7.5)))


class CongRuiRo:
    def __init__(self, c: dict) -> None:
        self.c = dict(c)

    def xet(self, co: CoHoiCoSo) -> tuple[bool, list[tuple[str, str]]]:
        ly = []
        am = float(self.c["basisAmToiDaBps"])
        if co.basisBps < -am:
            ly.append(("basis-am-qua-sau",
                       f"basis {co.basisBps:.1f} bps < −{am:.0f} — mua giao "
                       f"ngay ĐẮT hơn giá thanh lý của chân short, đó là một "
                       f"khoản lỗ trả trước chứ không phải cơ hội"))
        duong = float(self.c["basisDuongToiDaBps"])
        if co.basisBps > duong:
            ly.append(("basis-duong-qua-rong",
                       f"basis {co.basisBps:.1f} bps > {duong:.0f} — hoặc một "
                       f"trong hai giá sai, hoặc thị trường đang định giá một "
                       f"rủi ro ta chưa thấy"))
        if self.c["doiHoiItNhatMotMoc"] and co.soMoc < 1:
            ly.append(("khong-moc-nao",
                       f"giữ {co.giuGio:g} giờ mà không chứa mốc kết toán nào "
                       f"— funding trả theo MỐC, nên thu đúng bằng KHÔNG"))
        net_min = float(self.c["netToiThieuBps"])
        if co.netBps < net_min:
            ly.append(("net-duoi-nguong",
                       f"NET {co.netBps:.2f} bps < {net_min:.2f}"))
        tuoi_max = float(self.c["tuoiToiDaGiay"])
        if co.tuoiGiay > tuoi_max:
            ly.append(("du-lieu-cu",
                       f"dữ liệu {co.tuoiGiay:.0f}s > {tuoi_max:.0f}s"))
        lech = dong_ho.lech_ms()
        tran_dh = float(self.c["lechDongHoToiDaGiay"])
        if lech is not None and abs(lech) / 1000.0 > tran_dh:
            ly.append(("dong-ho-lech",
                       f"đồng hồ máy lệch {abs(lech) / 1000:.0f}s > "
                       f"{tran_dh:.0f}s — đếm mốc trên giờ máy là đếm mù"))
        return (not ly), ly

    def tom_tat(self) -> dict:
        return {k: self.c[k] for k in CUA if k in self.c}


def mot_co_hoi(san: str, ma: str, dinh: DinhSo, bg, vonXinUsd: float,
               giuGio: float, phiBang: dict, sucChuaC: dict,
               nowMs: float | None = None) -> CoHoiCoSo | None:
    """Ghép một `DinhSo` giao ngay với một `BaoGia` perp CÙNG SÀN."""
    now = nowMs if nowMs is not None else dong_ho.bay_gio_ms()
    if bg.markPx is None or bg.rate is None or bg.intervalGio is None:
        return None
    lich = dem_moc(now, giuGio, bg.mocKeMs, bg.intervalGio)

    # SHORT perp: funding dương thì ta THU. Đếm theo MỐC, không nhân theo
    # giờ — giữ 4 giờ trên sàn kết toán 8 giờ có thể thu đúng bằng không.
    thu = lich.soMoc * bg.rate
    gross = thu * 10_000.0
    phi = phi_khu_hoi_bps(san, phiBang)

    oi = getattr(bg, "oiUsd", None)
    chua = None
    if oi:
        c = min(oi * float(sucChuaC["phanOi"]), float(sucChuaC["tranUsd"]))
        chua = c if c >= float(sucChuaC["sanUsd"]) else None

    return CoHoiCoSo(
        san=san, ma=ma, giaoNgay=dinh.ban, mark=bg.markPx,
        fundingMoiGio=moi_gio(bg.rate, bg.intervalGio),
        intervalGio=bg.intervalGio, soMoc=lich.soMoc, mocDauMs=lich.mocDauMs,
        vonXinUsd=vonXinUsd, giuGio=giuGio,
        grossBps=gross, phiBps=phi, netBps=gross - phi,
        basisBps=basis_bps(bg.markPx, dinh.ban),
        sucChuaToiDaUsd=chua,
        tuoiGiay=max(dinh.tuoi_giay(), bg.tuoi_giay(now) or 0.0))


def tim_co_hoi(dinh: list, baoGia: list, vonXinUsd: float, giuGio: float,
               phiBang: dict, sucChuaC: dict, cong,
               nowMs: float | None = None) -> list[CoHoiCoSo]:
    """Ghép theo (sàn, mã). Sàn nào thiếu một vế thì BỎ, không đoán vế kia."""
    gn = {(d.san, d.cap.split("/")[0]): d for d in dinh}
    ra = []
    for bg in baoGia:
        d = gn.get((bg.san, bg.ma))
        if d is None:
            continue
        co = mot_co_hoi(bg.san, bg.ma, d, bg, vonXinUsd, giuGio, phiBang,
                        sucChuaC, nowMs)
        if co is None:
            continue
        qua, ly = cong.xet(co)
        ra.append(replace(co, duyet=qua, lyDoMa=tuple(ly),
                          lyDo=tuple(c for _, c in ly)))
    ra.sort(key=lambda c: -c.netMoiGioBps)
    return ra


class TyCoSo(Ty):
    ma = MA_CHIEN_LUOC
    ho = HO
    moTa = ("cash-and-carry: mua giao ngay, bán khống perp CÙNG một sàn — "
            "ăn MỨC funding tuyệt đối, không phải chênh lệch giữa hai sàn")

    #: Hai chân, mỗi chân phải qua cỡ lệnh tối thiểu của sàn; và chân giao
    #: ngay chiếm vốn ĐẦY ĐỦ vì không có đòn bẩy. Cao gấp đôi ty chênh lệch
    #: funding, nơi cả hai chân đều là perp có ký quỹ.
    vonToiThieuKinhTeUsd = _VON_TOI_THIEU

    def __init__(self, runtime=None, client_factory=None) -> None:
        super().__init__()
        self._rt = runtime
        self._cf = client_factory
        self.nguonGiaoNgay = SanGiaoNgay()
        self.cong = CongRuiRo(CONFIG["ruiRo"])
        self.dinh: list = []
        self.coHoi: list = []

    def quet(self) -> list:
        """Giao ngay hỏi ở đây; perp ĐỌC LẠI từ lượt quét của runtime.

        Không tự hỏi perp lần nữa: hai lượt hỏi là hai ảnh chụp ở hai thời
        điểm, rồi đem ghép như thể cùng lúc — đúng lỗi mà `dong_ho.py` sinh
        ra để chặn, chỉ khác là lần này giữa hai TY chứ không giữa hai cảng.
        """
        q = CONFIG["quet"]
        self.dinh = _chay(self._doc_giao_ngay())
        bg = list(getattr(self._rt, "baoGia", []) or [])
        self.coHoi = tim_co_hoi(
            self.dinh, bg, float(CONFIG["von"]["moiCoHoiUsd"]),
            float(q["giuGio"]), CONFIG["phiTakerBps"], CONFIG["sucChua"],
            self.cong)
        return list(self.coHoi)

    async def _doc_giao_ngay(self):
        import httpx
        q = CONFIG["quet"]
        cap = [m + "/USDT" for m in q["ma"]]
        lam = self._cf or (lambda: httpx.AsyncClient(
            timeout=float(q["hetGioHoiGiay"]),
            headers={"User-Agent": "thi-bac-ty/0.1 (+public data only)"}))
        async with lam() as c:
            return await self.nguonGiaoNgay.doc(c, cap, q["san"])

    def xet(self, co):
        return bool(co.duyet), list(co.lyDoMa or ())

    def trinh(self, co) -> ToTrinh:
        return xuat_to_trinh(co)

    # ── kế toán: chỉ chân PERP sinh dòng tiền, chân giao ngay thì KHÔNG ──
    def ke_toan(self, viThe, toTrinh, tuGiay, denGiay):
        """Cash-and-carry giữ giao ngay + short perp trên CÙNG một sàn.

        Chỉ chân perp sinh dòng tiền: nó nhận funding tại mốc kết toán. Chân
        giao ngay không trả lãi gì cả — nó chỉ nằm đó để trung hoà giá.

        **Phần hội tụ basis KHÔNG kế toán ở đây, và phải nói ra.** Chênh
        lệch giao ngay ↔ perp co lại theo thời gian và đó là nửa còn lại của
        lợi nhuận chiến lược này; đo nó cần giá hai chân tại hai thời điểm,
        thứ vòng quét không giữ. Nên con số trả về là phần ĐO ĐƯỢC, và câu
        `vi` khai phần chưa đo — gộp hai thứ ấy vào một số 0 là nói dối.

        Dùng `thu_thuc()` cho MỘT chân chứ không `thu_cap()`: cặp ở đây
        không phải hai perp đối nhau mà là giao ngay + perp, nên công thức
        hai chân của chênh funding không áp được.
        """
        from phai_sinh_chung.dongho import thu_thuc

        from thi_bac_ty.ke_toan import KetToanVong

        dt = max(0.0, float(denGiay) - float(tuGiay))
        if dt <= 0.0:
            return KetToanVong(vi="chưa qua giây nào kể từ lần kế toán trước")

        ma = toTrinh.get("taiSan")
        chanPerp = next((c for c in viThe
                         if getattr(c, "loai", "") == "perp"), None)
        if chanPerp is None:
            return KetToanVong(
                doDuoc=False,
                vi="vị thế không có chân perp — không biết đếm mốc ở đâu")

        bg = next((b for b in getattr(self._rt, "baoGia", []) or []
                   if b.ma == ma and b.san == chanPerp.cang), None)
        if bg is None:
            return KetToanVong(
                doDuoc=False,
                vi=f"KHÔNG có báo giá perp {ma} trên {chanPerp.cang} trong "
                   f"lượt quét gần nhất — sàn rớt khác hẳn funding bằng 0")

        thu1, lich = thu_thuc(float(tuGiay) * 1000.0, dt / 3600.0,
                              bg.rate, bg.mocKeMs, bg.intervalGio)
        if lich.uocLuong:
            return KetToanVong(
                doDuoc=False,
                vi=f"lịch mốc của {ma} trên {chanPerp.cang} phải ước lượng "
                   f"— tiền đoán ra không ghi vào sổ")

        von = abs(float(getattr(chanPerp, "vonUsd", 0.0) or 0.0))
        thu = von * thu1                     # chân SHORT perp: nhận `thu1`
        return KetToanVong(
            thuUsd=thu,
            vi=(f"cash-and-carry {ma} trên {chanPerp.cang}: {lich.soMoc} mốc "
                f"funding trong {dt / 3600:.4f}h trên {von:.2f} USD chân "
                f"perp (chân giao ngay không sinh dòng tiền; phần HỘI TỤ "
                f"BASIS chưa đo)"))


def _chay(coro):
    """Xem `tin_dung/ty_vay._chay` — cùng lý do, cùng cái giá."""
    import concurrent.futures
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
        return ex.submit(asyncio.run, coro).result()


def _rui_ro(co: CoHoiCoSo) -> RuiRo:
    return RuiRo(
        # Delta gần 0 (long giao ngay + short perp cùng cỡ), nên rủi ro giá
        # còn lại chính là BASIS rời ra lúc thoát — và nó bám vào basis hiện
        # tại chứ không phải một hằng số.
        thiTruong=max(0.05, min(1.0, abs(co.basisBps) / 100.0)),
        thanhKhoan=(None if co.sucChuaToiDaUsd is None else 0.20),
        giaoThuc=0.05,          # sàn tập trung, không hợp đồng thông minh
        cang=0.25,              # một sàn giữ CẢ HAI chân — sập là kẹt cả hai
        thucThi=0.25,           # hai chân, có legging risk
        cauNoi=0.0,             # cùng sàn, không bắc cầu — đã ĐO
    )


def _tin_cay(co: CoHoiCoSo) -> float:
    """Bắt đầu 1,0 rồi TRỪ. Cửa sổ càng dài, giả định càng mạnh.

    `grossBps` = mức funding HIỆN TẠI × số mốc trong cửa sổ. Với một mốc thì
    đó gần như một sự thật; với chín mươi mốc thì đó là một dự báo ba tháng
    đội lốt một phép nhân.
    """
    d = 1.0
    if co.sucChuaToiDaUsd is None:
        d -= 0.35
    if co.soMoc > 3:
        # −0,05 mỗi lần gấp đôi số mốc, tối đa −0,30.
        import math
        d -= min(0.30, 0.05 * math.log2(co.soMoc / 3.0))
    if abs(co.basisBps) > 10.0:
        d -= 0.10
    return max(0.0, min(1.0, d))


def xuat_to_trinh(co: CoHoiCoSo) -> ToTrinh:
    return ToTrinh(
        chienLuoc=MA_CHIEN_LUOC, ho=HO, taiSan=co.ma,
        chan=(Chan("LONG", co.san, co.ma, co.vonXinUsd / 2.0, "spot"),
              Chan("SHORT", co.san, co.ma, co.vonXinUsd / 2.0, "perp")),
        vonCanUsd=co.vonXinUsd,
        vonToiThieuKinhTeUsd=_VON_TOI_THIEU,
        sucChuaToiDaUsd=co.sucChuaToiDaUsd,
        grossBps=co.grossBps, phiUocBps=co.phiBps, netUocBps=co.netBps,
        giuGio=co.giuGio,
        khoaVonDenGio=0.0,          # thoát được bất cứ lúc nào
        thanhKhoanThoatUsd=co.sucChuaToiDaUsd,
        ruiRo=_rui_ro(co),
        tuoiDuLieuGiay=co.tuoiGiay,
        tinCay=_tin_cay(co),
        moHinhPhiDuChua=False, phiConThieu=PHI_CON_THIEU,
        moHinhSucChuaDuChua=False, sucChuaConThieu=SUC_CHUA_CON_THIEU,
        cang=(co.san,),
        bangChung=(
            f"{co.san}: mua giao ngay {co.giaoNgay:,.2f} · bán khống perp "
            f"mark {co.mark:,.2f}",
            f"basis {co.basisBps:+.1f} bps — KHÔNG tính vào NET, perp không "
            f"đáo hạn nên không có gì bảo đảm nó hội tụ",
            f"funding {co.fundingMoiGio * 100:+.4f}%/giờ · chu kỳ "
            f"{co.intervalGio:g}h · giữ {co.giuGio:g}h chứa {co.soMoc} MỐC",
            f"gross {co.grossBps:+.2f} − phí {co.phiBps:.2f} (4 lần taker) "
            f"= NET {co.netBps:+.2f} bps",
            f"GIẢ ĐỊNH: mức funding hiện tại giữ nguyên suốt {co.soMoc} mốc "
            f"({co.giuGio:g} giờ). Nó không giữ nguyên — độ tin đã hạ theo "
            f"độ dài cửa sổ.",
        ))
