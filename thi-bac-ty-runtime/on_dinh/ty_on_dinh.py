"""TY CHÊNH LỆCH — nhánh stablecoin. Họ THỨ BA của Thị Bạc Ty.

Ba họ, ba nguồn alpha khác hẳn nhau:

    phai-sinh   chênh funding perp     hai chân, thu tại MỐC kết toán
    tin-dung    xoay vốn cho vay        một chân, lãi chảy liên tục
    chenh-lech  stablecoin chéo sàn     hai chân, ăn ngay rồi kẹt tồn kho

Bản đồ nói đúng lúc có ba loại việc khác hẳn nhau thì Người Phân Bổ Vốn mới
thật sự có việc để làm — trước đó nó chỉ đang xếp hạng những thứ giống nhau.

## Hai chỗ ty này rất dễ nói dối, và cả hai đều được chặn

**1. `$0,97` KHÔNG phải arbitrage.** Nó có thể là DEPEG. Bên đứng ra "ăn
chênh lệch" sẽ là bên ôm đồng đang chết. Cửa `lechNeoToiDaBps` chặn đúng
chỗ ấy, và nó là cửa quan trọng nhất của ty này.

**2. Thời gian giao dịch ≠ chu kỳ vốn.** Lệnh xong trong vài giây. Nhưng
sau một lượt, tồn kho lệch: sàn rẻ hết USDT, sàn đắt đầy USDC. Muốn làm
lượt nữa phải chờ chênh lệch đảo chiều, hoặc chuyển vốn giữa hai sàn — mà
chuyển vốn thì tốn phí, tốn thời gian, và runtime này chưa làm được.

Khai `giuGio` bằng vài giây là cho NET mỗi giờ nhảy lên hàng nghìn bps và
chiếm sạch bảng xếp hạng của mọi ty khác — bằng một con số mình không đạt
được. Nên `giuGio` ở đây là **chu kỳ vốn**, và `chuyen-von-giua-san` nằm
tường minh trong `phiConThieu`.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, replace

from thi_bac_ty.khoang_nguong import khoang_cach, vi_tri
from thi_bac_ty.khuon_ty import Ty
from thi_bac_ty.to_trinh import Chan, RuiRo, ToTrinh

from .config import CONFIG, HO, MA_CHIEN_LUOC
from .nguon import DinhSo, SanGiaoNgay

#: Khai báo NỀN — thứ ty này không đo được, dù có Router hay không.
PHI_CON_THIEU = (
    "chuyen-von-giua-san",      # Router gỡ được — xem `_phi_con_thieu()`
    "rut-tien-va-thoi-gian-cho",  # Router gỡ được — cùng một tuyến
    "truot-gia-duoi-dinh-so",
    "thue",
)

#: Hai khoản Router TRẢ LỜI ĐƯỢC, nếu nó có số. Tách ra thành hằng số riêng
#: vì cả hai đều mô tả cùng một chuyện — dời tồn kho từ sàn này sang sàn kia
#: — và chúng phải cùng biến mất hoặc cùng ở lại, không được rời nhau.
ROUTER_GO_DUOC = ("chuyen-von-giua-san", "rut-tien-va-thoi-gian-cho")


def _phi_con_thieu(daDoChuyenVon: bool, routerConThieu: tuple = ()) -> tuple:
    """Khai báo thiếu của MỘT cơ hội, không phải của cả ty.

    Trước khi có Router thì mọi cơ hội khai giống hệt nhau, và hằng số
    module là đủ. Nay hai cơ hội cùng một lượt quét có thể khác nhau: cặp
    binance/okx có tuyến đo được, cặp có một sàn lạ thì không.

    Router đo được thì hai khoản kia biến mất — NHƯNG thay bằng những khoản
    chính Router khai là nó chưa tính (`rui-ro-cau-noi`,
    `gas-limit-uoc-luong`, `phi-rut-do-tay-...`). Đổi một lỗ hổng lấy một
    lỗ hổng nhỏ hơn ĐÃ ĐƯỢC ĐẶT TÊN, chứ không phải xoá lỗ hổng.
    """
    if not daDoChuyenVon:
        return PHI_CON_THIEU
    con = tuple(x for x in PHI_CON_THIEU if x not in ROUTER_GO_DUOC)
    them = tuple(f"router:{x}" for x in routerConThieu)
    return con + them
SUC_CHUA_CON_THIEU = ("do-sau-so-lenh-duoi-dinh",)

#: Một nguồn duy nhất cho cả khai báo của ty lẫn
#: từng tờ trình nó xuất ra.
_VON_TOI_THIEU = 200.0

NHAN = {
    "lech-neo-qua-lon": "lệch neo quá lớn — có thể là DEPEG, không phải cơ hội",
    "chenh-tho-qua-mong": "chênh lệch thô quá mỏng",
    "net-duoi-nguong": "NET sau phí dưới ngưỡng",
    "so-lenh-mong": "sổ lệnh trên đỉnh quá mỏng",
    "du-lieu-cu": "dữ liệu quá cũ",
    "thieu-san": "không đủ hai sàn cùng sống",
}

CUA = ("lechNeoToiDaBps", "chenhThoToiThieuBps", "netToiThieuBps",
       "sauSoLenhToiThieuUsd", "tuoiToiDaGiay", "doiHoiHaiSanSong")


@dataclass(frozen=True)
class CoHoiChenh:
    cap: str
    mua: DinhSo          # sàn ta MUA (ask thấp nhất)
    ban: DinhSo          # sàn ta BÁN (bid cao nhất)
    vonXinUsd: float
    giuGio: float
    grossBps: float
    phiBps: float
    netBps: float
    sucChuaToiDaUsd: float | None
    sauSoLenhUsd: float | None
    #: Phí dời tồn kho từ sàn BÁN về sàn MUA, do Router đo. `None` = Router
    #: không đo được, và khi ấy `phiBps` KHÔNG gồm nó — cơ hội giữ nguyên
    #: khai báo `chuyen-von-giua-san`.
    phiChuyenBps: float | None = None
    giayChuyen: float | None = None
    #: Thứ chính Router khai là nó chưa tính.
    routerConThieu: tuple = ()
    duyet: bool = False
    lyDo: tuple = ()
    lyDoMa: tuple = ()

    @property
    def netMoiGioBps(self) -> float:
        return self.netBps / self.giuGio if self.giuGio else 0.0

    @property
    def lechNeoBps(self) -> float:
        return max(self.mua.lechNeoBps, self.ban.lechNeoBps)

    def tom_tat(self) -> dict:
        return {"cap": self.cap, "sanMua": self.mua.san, "sanBan": self.ban.san,
                "giaMua": self.mua.ban, "giaBan": self.ban.mua,
                "vonXinUsd": self.vonXinUsd, "giuGio": self.giuGio,
                "grossBps": self.grossBps, "phiBps": self.phiBps,
                "netBps": self.netBps, "netMoiGioBps": self.netMoiGioBps,
                "lechNeoBps": self.lechNeoBps,
                "sucChuaToiDaUsd": self.sucChuaToiDaUsd,
                "sauSoLenhUsd": self.sauSoLenhUsd,
                "phiChuyenBps": self.phiChuyenBps,
                "giayChuyen": self.giayChuyen,
                "routerConThieu": list(self.routerConThieu),
                "duyet": self.duyet, "lyDo": list(self.lyDo),
                "lyDoMa": [list(x) for x in self.lyDoMa]}


def phi_khu_hoi_bps(sanMua: str, sanBan: str, bang: dict) -> float:
    """Taker ở CẢ HAI sàn. Một chiều thôi là báo cáo nửa chi phí."""
    m = float(bang.get(sanMua, bang.get("_khac", 10.0)))
    b = float(bang.get(sanBan, bang.get("_khac", 10.0)))
    return m + b


def sau_so_lenh_usd(mua: DinhSo, ban: DinhSo) -> float | None:
    """Chỗ CHẬT NHẤT của hai chân, quy ra USD. `None` nếu sàn giấu khối lượng."""
    if mua.banLuong is None or ban.muaLuong is None:
        return None
    return min(mua.banLuong * mua.ban, ban.muaLuong * ban.mua)


class CongRuiRo:
    def __init__(self, c: dict) -> None:
        self.c = dict(c)

    def xet(self, co: CoHoiChenh) -> tuple[bool, list[tuple[str, str]]]:
        ly: list[tuple[str, str]] = []
        tran_neo = float(self.c["lechNeoToiDaBps"])
        if co.lechNeoBps > tran_neo:
            ly.append(("lech-neo-qua-lon",
                       f"lệch neo {co.lechNeoBps:.0f} bps > trần "
                       f"{tran_neo:.0f} — chênh lệch càng lớn thì càng có "
                       f"khả năng đây không phải sai giá tạm thời mà là thị "
                       f"trường đang định giá lại rủi ro của chính đồng ấy"))

        tho_min = float(self.c["chenhThoToiThieuBps"])
        if co.grossBps < tho_min:
            ly.append(("chenh-tho-qua-mong",
                       f"chênh thô {co.grossBps:.2f} bps < {tho_min:.2f}"))

        net_min = float(self.c["netToiThieuBps"])
        if co.netBps < net_min:
            ly.append(("net-duoi-nguong",
                       f"NET {co.netBps:.2f} bps < {net_min:.2f}"))

        sau_min = float(self.c["sauSoLenhToiThieuUsd"])
        if co.sauSoLenhUsd is None:
            ly.append(("so-lenh-mong", "sàn không công bố khối lượng đỉnh sổ "
                                       "— không biết chênh lệch này có thật "
                                       "được bao nhiêu"))
        elif co.sauSoLenhUsd < sau_min:
            ly.append(("so-lenh-mong",
                       f"đỉnh sổ chỉ ${co.sauSoLenhUsd:,.0f} < "
                       f"${sau_min:,.0f} — chênh lệch trên một sổ mỏng là ảo"))

        tuoi_max = float(self.c["tuoiToiDaGiay"])
        tuoi = max(co.mua.tuoi_giay(), co.ban.tuoi_giay())
        if tuoi > tuoi_max:
            ly.append(("du-lieu-cu", f"dữ liệu {tuoi:.0f}s > {tuoi_max:.0f}s"))

        if self.c["doiHoiHaiSanSong"] and co.mua.san == co.ban.san:
            ly.append(("thieu-san", "mua và bán rơi vào cùng một sàn — đây là "
                                    "spread nội sàn, không phải chênh lệch "
                                    "chéo sàn"))
        return (not ly), ly

    def tom_tat(self) -> dict:
        return {k: self.c[k] for k in CUA if k in self.c}


def tim_co_hoi(dinh: list[DinhSo], vonXinUsd: float, giuGio: float,
               phiBang: dict, sucChuaC: dict, cong,
               dinhTuyen=None) -> list[CoHoiChenh]:
    """Với mỗi cặp: mua ở ask thấp nhất, bán ở bid cao nhất.

    `dinhTuyen` là tuỳ chọn, và mặc định KHÔNG có. Ty này chạy đúng như
    trước khi thiếu nó — chỉ là `phiBps` thiếu khoản dời tồn kho, và cơ hội
    tự khai điều đó ra. Bắt buộc phải có Router mới quét được là biến một
    hạ tầng thành điểm chết chung.
    """
    theo_cap: dict[str, list[DinhSo]] = {}
    for d in dinh:
        theo_cap.setdefault(d.cap, []).append(d)

    ra = []
    for cap, ds in theo_cap.items():
        if not ds:
            continue
        mua = min(ds, key=lambda x: x.ban)      # ask thấp nhất
        ban = max(ds, key=lambda x: x.mua)      # bid cao nhất
        giua = (mua.ban + ban.mua) / 2.0
        gross = ((ban.mua - mua.ban) / giua) * 10_000.0 if giua > 0 else 0.0
        phi = phi_khu_hoi_bps(mua.san, ban.san, phiBang)
        sau = sau_so_lenh_usd(mua, ban)
        chua = (None if sau is None
                else min(sau * float(sucChuaC["phanDinhSo"]),
                         float(sucChuaC["tranUsd"])))
        # Dời tồn kho: sau khi mua ở A và bán ở B, tồn kho lệch đi — phải
        # dời từ B về A mới quay lại được vị thế ban đầu. Đó chính là khoản
        # `chuyen-von-giua-san` mà ty này khai thiếu từ đầu.
        chuyenBps, giayChuyen, rct = _hoi_router(
            dinhTuyen, ban.san, mua.san, cap.split("/")[0], vonXinUsd)
        phiDu = phi + (chuyenBps or 0.0)

        co = CoHoiChenh(cap=cap, mua=mua, ban=ban, vonXinUsd=vonXinUsd,
                        giuGio=giuGio, grossBps=gross, phiBps=phiDu,
                        netBps=gross - phiDu, sucChuaToiDaUsd=chua,
                        sauSoLenhUsd=sau, phiChuyenBps=chuyenBps,
                        giayChuyen=giayChuyen, routerConThieu=rct)
        qua, ly = cong.xet(co)
        ra.append(replace(co, duyet=qua, lyDoMa=tuple(ly),
                          lyDo=tuple(c for _, c in ly)))
    ra.sort(key=lambda c: -c.netMoiGioBps)
    return ra


def _hoi_router(dinhTuyen, tuSan: str, denSan: str, taiSan: str,
                vonUsd: float) -> tuple:
    """(bps, giây, thứ-router-chưa-tính). Ba `None`/rỗng khi không đo được.

    Nuốt mọi ngoại lệ và trả về "không đo được": một hạ tầng phụ trợ nổ
    KHÔNG được giết lượt quét của ty. Nhưng nó cũng không được nổ trong im
    lặng — lỗi đi vào `routerConThieu` nên nó hiện lên tận tờ trình.
    """
    if dinhTuyen is None or tuSan == denSan:
        return None, None, ()
    try:
        from chuyen_von.diem import Diem
        bps, t = dinhTuyen.phi_bps(Diem("san", tuSan), Diem("san", denSan),
                                   taiSan, vonUsd)
    except Exception as e:                                    # noqa: BLE001
        return None, None, (f"router-no:{type(e).__name__}",)
    if bps is None:
        return None, None, ()
    return bps, t.giayCho, tuple(t.khongDoDuoc)


class TyOnDinh(Ty):
    ma = MA_CHIEN_LUOC
    ho = HO
    moTa = ("chênh lệch stablecoin chéo sàn — hai chân, ăn ngay rồi kẹt "
            "tồn kho cho tới khi chênh lệch đảo chiều")

    #: Edge ở đây tính bằng VÀI BPS, nên đây là engine nhạy phí nhất trong
    #: cả bốn. Phí taker khứ hồi hai sàn ~9–20 bps là khoản cố định theo TỈ
    #: LỆ, nên cỡ vốn không cứu được phí.
    #:
    #: Thứ cỡ vốn cứu được là cỡ lệnh tối thiểu của sàn giao ngay và phần
    #: vụn không khớp hết. $200 là chỗ hai thứ ấy còn nhỏ so với vài bps.
    vonToiThieuKinhTeUsd = _VON_TOI_THIEU

    def __init__(self, client_factory=None, dinhTuyen=None) -> None:
        super().__init__()
        self.dinhTuyen = dinhTuyen
        self.nguon = SanGiaoNgay()
        self.cong = CongRuiRo(CONFIG["ruiRo"])
        self.dinh: list = []
        self.coHoi: list = []
        self._cf = client_factory

    def quet(self) -> list:
        q = CONFIG["quet"]
        self.dinh = _chay(self._doc())
        self.coHoi = tim_co_hoi(
            self.dinh, float(CONFIG["von"]["moiCoHoiUsd"]),
            float(q["chuKyVonGio"]), CONFIG["phiTakerBps"],
            CONFIG["sucChua"], self.cong, self.dinhTuyen)
        return list(self.coHoi)

    def tom_tat(self) -> dict:
        # Phân bố phải LÊN ẢNH CHỤP. Ba lần trong một ngày tôi phải viết
        # script rời để phân biệt «cổng đặt sai» với «chợ trống», và cả
        # ba lần câu trả lời nằm trong dữ liệu ty vốn đã có trong tay.
        return {"nguon": self.nguon.tom_tat(), "cua": self.cong.tom_tat(),
                "soCoHoi": len(self.coHoi),
                "soQua": sum(1 for c in self.coHoi if c.duyet),
                "phanBoChenh": _phan_bo_chenh(self.coHoi, self.cong)}

    async def _doc(self):
        import httpx
        q = CONFIG["quet"]
        lam = self._cf or (lambda: httpx.AsyncClient(
            timeout=float(q["hetGioHoiGiay"]),
            headers={"User-Agent": "thi-bac-ty/0.1 (+public data only)"}))
        async with lam() as c:
            return await self.nguon.doc(c, q["cap"], q["san"])

    def xet(self, co):
        return bool(co.duyet), list(co.lyDoMa or ())

    def trinh(self, co) -> ToTrinh:
        return xuat_to_trinh(co)

    # ── kế toán: chiến lược HỘI TỤ, lãi lỗ chỉ có thật LÚC ĐÓNG ──────────
    def ke_toan(self, viThe, toTrinh, tuGiay, denGiay):
        """Chênh stablecoin không sinh dòng tiền lúc giữ, và đó là điểm
        khác căn bản với bốn ty đã có kế toán.

        Cho vay và AMM có tiền CHẢY VÀO mỗi giây; funding có tiền chảy tại
        mốc. Ở đây thì không: ta mua rẻ ở sàn này, bán đắt ở sàn kia, và
        cả lãi lẫn lỗ chỉ thành thật **lúc gỡ hai chân ra**. Trong lúc
        giữ, thứ duy nhất đổi là giá — mà giá đổi không phải tiền vào túi.

        Nên `thuUsd` là **0 ĐO ĐƯỢC** suốt thời gian giữ, không phải
        "không đo được". Cộng chênh lệch hiện tại vào như một khoản thu là
        đánh giá lại theo giá rồi ghi nó vào sổ như tiền mặt — hai lỗi
        chồng nhau, và đường NAV sẽ nhấp nhô theo một thứ chưa ai nhận.

        Lãi lỗ THẬT trả về đúng một lần, kèm `dongLai=True`, khi:

        · chênh lệch đã hội tụ (còn dưới ngưỡng NET của chính ty) — ăn
          xong, gỡ ra;
        · hoặc chênh lệch ĐẢO DẤU — giữ tiếp là lỗ thêm.

        Số trả về đo bằng chính hai đỉnh sổ lệnh của lượt quét này: bán
        chân đang giữ ở sàn MUA, mua lại ở sàn BÁN. Đó là giá thoát THẬT
        chứ không phải giá giữa.
        """
        from thi_bac_ty.ke_toan import KetToanVong

        cap = toTrinh.get("dinhGiaBang")
        ma = toTrinh.get("taiSan")
        sanMua = next((c.cang for c in viThe if c.ben == "LONG"), None)
        sanBan = next((c.cang for c in viThe if c.ben == "SHORT"), None)
        if not (sanMua and sanBan):
            return KetToanVong(
                doDuoc=False,
                vi="vị thế không đủ hai chân mua/bán để đo hội tụ")

        tra = {(d.san, d.cap): d for d in getattr(self, "dinh", []) or []}
        capTen = next((k[1] for k in tra if k[1].split("/")[0] == ma), cap)
        dMua, dBan = tra.get((sanMua, capTen)), tra.get((sanBan, capTen))
        thieu = [x for x, d in ((sanMua, dMua), (sanBan, dBan)) if d is None]
        if thieu:
            return KetToanVong(
                doDuoc=False,
                vi=f"KHÔNG có đỉnh sổ lệnh {capTen} trên {', '.join(thieu)} "
                   f"trong lượt quét gần nhất — sàn rớt khác hẳn chênh lệch "
                   f"bằng 0")

        # Thoát: BÁN chân đang giữ ở sàn mua (giá bid), MUA lại ở sàn bán
        # (giá ask). Dùng bid/ask chứ không dùng giá giữa — giá giữa là
        # một con số không ai khớp được.
        raBps = (dMua.mua - dBan.ban) / dBan.ban * 10_000.0
        von = sum(abs(float(getattr(c, "vonUsd", 0.0) or 0.0))
                  for c in viThe) / 2.0
        nguong = float(self.cong.c["netToiThieuBps"])
        vi = (f"chênh {capTen} {sanMua}↔{sanBan}: thoát được {raBps:+.2f} "
              f"bps trên {von:.2f} USD mỗi chân. Chiến lược HỘI TỤ — không "
              f"có dòng tiền lúc giữ, lãi lỗ chỉ thật lúc gỡ hai chân")
        if raBps <= 0.0:
            return KetToanVong(
                thuUsd=von * raBps / 10_000.0, dongLai=True,
                lyDoDong=f"chênh lệch ĐẢO DẤU còn {raBps:+.2f} bps — giữ "
                         f"tiếp là lỗ thêm", vi=vi)
        if raBps < nguong:
            return KetToanVong(
                thuUsd=von * raBps / 10_000.0, dongLai=True,
                lyDoDong=f"đã hội tụ: {raBps:.2f} bps < ngưỡng NET "
                         f"{nguong:.2f} bps của chính ty — ăn xong thì gỡ",
                vi=vi)
        return KetToanVong(thuUsd=0.0, vi=vi)


def _phan_bo_chenh(coHoi, cong) -> dict:
    """Chênh thô và NET nằm ở đâu so với ngưỡng — không chỉ đếm bao nhiêu
    trượt.

    Đo làn thật 05/09/2026: chênh thô ĐÚNG BẰNG 0,00 bps trên ngưỡng
    1,00, và phí khứ hồi 9 bps. Ba sàn quote USDC/USDT ở năm chữ số và
    khác nhau thật (binance bid 0,99979 · okx 0,9997 · bybit 0,9998) —
    nên con số 0 kia là CHỢ PHẲNG, không phải nguồn hỏng hay dấu sai.

    Câu ấy đọc được từ `cach`: muốn NET qua ngưỡng thì chênh thô phải
    tới 9,5 bps, tức một cú depeg. Một con số ĐẾM «9 lần trượt» thì nói
    y hệt nhau dù chợ phẳng hay chợ đang sát ngưỡng.
    """
    return {
        "chenhTho": khoang_cach([c.grossBps for c in coHoi],
                                float(cong.c["chenhThoToiThieuBps"])),
        "net": khoang_cach([c.netBps for c in coHoi],
                           float(cong.c["netToiThieuBps"])),
        "phi": vi_tri([c.phiBps for c in coHoi]),
    }


def _chay(coro):
    """Xem `tin_dung/ty_vay._chay` — cùng lý do, cùng cái giá."""
    import concurrent.futures
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
        return ex.submit(asyncio.run, coro).result()


def _rui_ro(co: CoHoiChenh) -> RuiRo:
    """Sáu mặt. `thiTruong` ở đây CHÍNH LÀ rủi ro depeg, nên nó bám vào
    độ lệch neo chứ không phải một hằng số."""
    return RuiRo(
        # Lệch neo 60 bps → 1,0. Đây là mặt rủi ro chính của cả ty.
        thiTruong=max(0.05, min(1.0, co.lechNeoBps / 60.0)),
        thanhKhoan=(None if co.sauSoLenhUsd is None
                    else max(0.05, min(1.0, 50_000.0 / max(co.sauSoLenhUsd, 1.0)))),
        # Sàn tập trung, không hợp đồng thông minh nào trong đường đi.
        giaoThuc=0.05,
        cang=0.20,          # hai sàn tập trung giữ tiền hộ ta
        # Hai chân trên hai sàn = legging risk thật, cao hơn một chân.
        thucThi=0.30,
        cauNoi=0.0,         # không bắc cầu — đã ĐO, nên 0
    )


def _tin_cay(co: CoHoiChenh) -> float:
    """Bắt đầu 1,0 rồi TRỪ. Cùng một luật với `tin_dung`.

    Hai sàn khác nhau mà chưa đo được phí dời tồn kho thì `netBps` đang
    thiếu một khoản chỉ có thể làm nó tệ đi — không trừ ở đây là thưởng cho
    sự thiếu hiểu biết.
    """
    d = 1.0
    if co.sauSoLenhUsd is None:
        d -= 0.40
    if co.mua.san != co.ban.san and co.phiChuyenBps is None:
        d -= 0.25
    return max(0.0, min(1.0, d))


def xuat_to_trinh(co: CoHoiChenh) -> ToTrinh:
    a, b = co.cap.split("/")
    return ToTrinh(
        chienLuoc=MA_CHIEN_LUOC, ho=HO, taiSan=a,
        chan=(Chan("LONG", co.mua.san, a, co.vonXinUsd / 2.0, "spot"),
              Chan("SHORT", co.ban.san, a, co.vonXinUsd / 2.0, "spot")),
        vonCanUsd=co.vonXinUsd,
        vonToiThieuKinhTeUsd=_VON_TOI_THIEU,
        sucChuaToiDaUsd=co.sucChuaToiDaUsd,
        grossBps=co.grossBps, phiUocBps=co.phiBps, netUocBps=co.netBps,
        giuGio=co.giuGio,
        # Không khoá theo hợp đồng — nhưng vốn KẸT cho tới khi chênh lệch
        # đảo chiều, và chuyện ấy đã nằm trong `giuGio` (chu kỳ vốn).
        # Không khoá theo hợp đồng — nhưng nếu phải dời tồn kho thì vốn
        # KẸT suốt chặng ấy, và đó là khoá thật dù không ai ký gì.
        khoaVonDenGio=(co.giayChuyen or 0.0),
        thanhKhoanThoatUsd=co.sauSoLenhUsd,
        ruiRo=_rui_ro(co),
        tuoiDuLieuGiay=max(co.mua.tuoi_giay(), co.ban.tuoi_giay()),
        tinCay=_tin_cay(co),
        moHinhPhiDuChua=False,
        phiConThieu=_phi_con_thieu(co.phiChuyenBps is not None,
                                   co.routerConThieu),
        moHinhSucChuaDuChua=False, sucChuaConThieu=SUC_CHUA_CON_THIEU,
        dinhGiaBang=b,
        cang=(co.mua.san, co.ban.san),
        bangChung=(
            f"mua {co.mua.san} @ {co.mua.ban:.5f} · bán {co.ban.san} @ "
            f"{co.ban.mua:.5f}",
            f"chênh thô {co.grossBps:.2f} bps − phí {co.phiBps:.2f} = "
            f"NET {co.netBps:.2f} bps",
            (f"trong đó dời tồn kho {co.ban.san}→{co.mua.san} tốn "
             f"{co.phiChuyenBps:.2f} bps, chờ {(co.giayChuyen or 0)/60:.0f} "
             f"phút (Router đo)"
             if co.phiChuyenBps is not None else
             "dời tồn kho giữa hai sàn: CHƯA đo được — xem phiConThieu"),
            f"lệch neo {co.lechNeoBps:.1f} bps (trần depeg "
            f"{CONFIG['ruiRo']['lechNeoToiDaBps']:.0f})",
            ("đỉnh sổ $" + f"{co.sauSoLenhUsd:,.0f}") if co.sauSoLenhUsd
            else "sàn KHÔNG công bố khối lượng đỉnh sổ",
            f"chu kỳ vốn {co.giuGio:g} giờ — lệnh xong trong vài giây, nhưng "
            f"tồn kho kẹt cho tới khi chênh lệch đảo chiều",
        ))
