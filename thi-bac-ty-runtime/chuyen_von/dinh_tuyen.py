"""ĐỊNH TUYẾN — ghép ba nguồn thành một tuyến, và trả lời cho ty.

Đây là cửa duy nhất ty nên gọi. Ba nguồn dưới nó (`gas`, `cau_noi`,
`bang_do`) là chi tiết cài đặt, và chúng có ba mức tin cậy rất khác nhau —
`dinh_tuyen` là chỗ ba mức ấy được gộp lại mà KHÔNG bị san bằng.

## Bốn dạng tuyến, và chỉ ba dạng đo được

    san  -> san     rút về chuỗi trung gian rồi nạp sang: 3 chặng
    san  -> chuoi   rút: 1 chặng            (bảng đo tay — có thể mù)
    chuoi-> san     nạp: 1 chặng            (chỉ gas)
    chuoi-> chuoi   cầu nối: 1 chặng        (LI.FI + gas)

Dạng `san -> san` là dạng `on_dinh/` cần, và nó là dạng tệ nhất: nó đi qua
chặng rút, tức là qua bảng đo tay. Bảng quá hạn thì cả tuyến mù, và ty
phải giữ nguyên `chuyen-von-giua-san` trong `phiConThieu`.

Đó không phải thất bại của Router. Đó là Router làm đúng việc: nói ra rằng
con số ấy không có, thay vì bịa một con số trông hợp lý.

## Router KHÔNG quyết định gì

Nó không nói "nên dời" hay "đừng dời". Nó trả về giá và thời gian; quyết
định là của ty (qua `xet()`) và của Rủi Ro Tổng (qua trần). Một hạ tầng tự
ý bỏ tuyến vì "thấy đắt quá" là một cửa rủi ro giấu trong một thư viện
tiện ích, và không ai soát được nó ở `CUA`.
"""
from __future__ import annotations

from .bang_do import chan_doan as _chan_doan_bang
from .bang_do import chuoi_cua_san as _chuoi_cua_san
from .bang_do import tra_cuu as _tra_cuu_bang
from .diem import ChangDuong, Diem, TuyenDuong, khong_co_tuyen
from .gas import GAS_LIMIT, TOKEN_GOC

#: Thứ tự ƯU TIÊN khi chọn chuỗi trung gian cho tuyến sàn -> sàn. Arbitrum
#: đứng đầu vì phí rút của cả ba sàn về đó rẻ hơn Ethereum khoảng một bậc,
#: và gas trên đó cũng rẻ hơn — hai khoản cùng chiều.
#:
#: Nhưng thứ tự này chỉ là ưu tiên, KHÔNG phải lựa chọn cứng: chuỗi được
#: chọn phải là chuỗi CẢ HAI sàn cùng dùng được. Bản nháp đầu ghim cứng
#: Arbitrum và không hỏi sàn đích có nhận không — nó chạy đúng với ba sàn
#: đang khai, và sẽ dựng ra một tuyến không tồn tại đúng vào ngày thêm sàn
#: thứ tư chỉ rút về Ethereum.
UU_TIEN_TRUNG_GIAN = ("arbitrum", "base", "polygon", "ethereum")

#: Chuỗi vốn NẰM khi không làm gì. Mọi phí vào một cơ hội liên chuỗi đo từ
#: đây. Arbitrum vì gas rẻ và cả ba sàn đều rút về được — nên nó vừa là nhà
#: vừa là chỗ trung chuyển, và hai vai ấy trùng nhau là điều may chứ không
#: phải một ràng buộc: đổi `NHA` mà `UU_TIEN_TRUNG_GIAN` giữ nguyên thì mọi
#: thứ vẫn đúng, chỉ đắt hơn.
NHA = "arbitrum"


def _khoa(taiSan, tuChuoi, denChuoi, vonUsd) -> tuple:
    # Làm tròn vốn về bậc $100: báo giá $997 và $1.003 khác nhau không đáng
    # kể, mà tra kho theo số lẻ thì không bao giờ trúng.
    return (str(taiSan).upper(), str(tuChuoi).strip().lower(),
            str(denChuoi).strip().lower(), round(float(vonUsd) / 100.0) * 100)


class DinhTuyen:
    """Trả lời "dời vốn từ đâu tới đâu thì tốn gì".

    Nhận sẵn các số đã đọc thay vì tự đi đọc: `gia_gas` và `bao_gia_cau` do
    lượt quét của runtime đưa vào. Cùng lý do ty Cơ Sở nhận `runtime.baoGia`
    thay vì tự hỏi perp — hai lượt hỏi là hai ảnh chụp ở hai thời điểm rồi
    ghép như thể cùng lúc.
    """

    def __init__(self, giaGas: dict | None = None,
                 giaTokenGocUsd: dict | None = None,
                 baoGiaCau=None) -> None:
        #: {chuoi: GiaGas}
        self.giaGas = dict(giaGas or {})
        #: {"ETH": 2461.0, "POL": 0.31} — do bên ngoài đưa vào. Thiếu thì
        #: chặng gas mù, và cái mù ấy chảy lên tận tổng.
        self.giaTokenGocUsd = dict(giaTokenGocUsd or {})
        #: callable(taiSan, tuChuoi, denChuoi, vonUsd) -> BaoGiaCau | None
        #: Mặc định đọc `self.kho` — kho do `nap()` đổ đầy TRƯỚC lượt quét.
        self.kho: dict = {}
        self.baoGiaCau = baoGiaCau or self._tu_kho

    def _tu_kho(self, taiSan, tuChuoi, denChuoi, vonUsd):
        return self.kho.get(_khoa(taiSan, tuChuoi, denChuoi, vonUsd))

    async def nap(self, client, nguonCau, can) -> dict:
        """Đổ đầy kho báo giá cầu nối cho những tuyến sắp dùng.

        Ty gọi `phi_bps()` một cách ĐỒNG BỘ, giữa vòng quét, và không được
        đợi mạng ở đó — một lượt quét 91 cơ hội mà mỗi cơ hội một lời gọi
        HTTP là 91 lần chờ nối tiếp nhau. Nên mạng xảy ra ở đây, một lần,
        song song, trước khi quét.

        Cùng lối ty Cơ Sở nhận `runtime.baoGia` thay vì tự hỏi perp: một ảnh
        chụp, một thời điểm.
        """
        import asyncio
        can = list(dict.fromkeys(can))          # bỏ trùng, giữ thứ tự
        ra = await asyncio.gather(
            *(nguonCau.doc(client, ts, a, b, v) for ts, a, b, v in can),
            return_exceptions=True)
        for (ts, a, b, v), bg in zip(can, ra):
            if not isinstance(bg, BaseException):
                self.kho[_khoa(ts, a, b, v)] = bg
        return self.kho

    # ── ba chặng nguyên tố ──────────────────────────────────────────────

    def _gas_usd(self, chuoi: str, viec: str) -> float | None:
        g = self.giaGas.get(chuoi)
        if g is None:
            return None
        return g.usd(viec, self.giaTokenGocUsd.get(TOKEN_GOC.get(chuoi, "?")))

    def chang_rut(self, san: str, taiSan: str, chuoi: str) -> ChangDuong:
        """Rút khỏi sàn về chuỗi. Nguồn DUY NHẤT là bảng đo tay."""
        d = _tra_cuu_bang(san, taiSan, chuoi)
        tu, den = Diem("san", san), Diem("chuoi", chuoi)
        if d is None:
            return ChangDuong(tu, den, "rut-cex", None, None,
                              "bang_do (không dùng được)",
                              (f"phi-rut-cex:{_chan_doan_bang(san, taiSan, chuoi)}",))
        return ChangDuong(tu, den, "rut-cex", d.phiUsd, d.giayCho,
                          f"bang_do đo {d.ngayDo} · {d.nguon}",
                          ("phi-rut-do-tay-khong-doc-bang-may",))

    def chang_nap(self, chuoi: str, san: str, taiSan: str) -> ChangDuong:
        """Nạp từ chuỗi vào sàn. Sàn không thu phí nạp, nên chỉ tốn gas —
        nhưng vẫn mất thời gian chờ xác nhận, và thời gian ấy là vốn kẹt."""
        tu, den = Diem("chuoi", chuoi), Diem("san", san)
        g = self._gas_usd(chuoi, "chuyen-erc20")
        if g is None:
            return ChangDuong(tu, den, "nap-cex", None, None,
                              "gas RPC (thiếu gas hoặc thiếu giá token gốc)",
                              (f"gas-chuoi:{chuoi}",))
        return ChangDuong(tu, den, "nap-cex", g, 600.0, f"gas RPC {chuoi}",
                          ("gas-limit-uoc-luong", "so-xac-nhan-san-doi"))

    def chang_cau(self, taiSan: str, tuChuoi: str, denChuoi: str,
                  vonUsd: float) -> ChangDuong:
        """Cầu nối giữa hai chuỗi. LI.FI đã gồm cả gas gửi vào cầu."""
        tu, den = Diem("chuoi", tuChuoi), Diem("chuoi", denChuoi)
        if tuChuoi == denChuoi:
            return ChangDuong(tu, den, "gas-thuan", 0.0, 0.0,
                              "cùng một chuỗi, không phải dời")
        bg = self.baoGiaCau(taiSan, tuChuoi, denChuoi, vonUsd) \
            if self.baoGiaCau else None
        if bg is None or not bg.doDuoc:
            vi = (bg.loi if bg is not None else "chưa nối nguồn cầu nối")
            return ChangDuong(tu, den, "cau-noi", None, None,
                              "LI.FI (không đo được)",
                              (f"cau-noi:{vi}"[:120],))
        return ChangDuong(tu, den, "cau-noi", bg.tongUsd, bg.giayCho,
                          f"LI.FI qua {bg.congCu}",
                          ("rui-ro-cau-noi", "gas-limit-uoc-luong"))

    # ── ghép tuyến ──────────────────────────────────────────────────────

    def tuyen(self, tu: Diem, den: Diem, taiSan: str,
              vonUsd: float) -> TuyenDuong:
        if tu == den:
            return khong_co_tuyen("hai điểm trùng nhau, không phải một tuyến")
        if vonUsd <= 0:
            return khong_co_tuyen(f"vốn phải dương, nhận {vonUsd}")

        if tu.loai == "chuoi" and den.loai == "chuoi":
            return TuyenDuong((self.chang_cau(taiSan, tu.ten, den.ten,
                                              vonUsd),))
        if tu.loai == "san" and den.loai == "chuoi":
            return TuyenDuong((self.chang_rut(tu.ten, taiSan, den.ten),))
        if tu.loai == "chuoi" and den.loai == "san":
            return TuyenDuong((self.chang_nap(tu.ten, den.ten, taiSan),))

        # san -> san: rút về một chuỗi CẢ HAI sàn cùng dùng được, rồi nạp
        # sang. Không có chuỗi chung thì đây không phải tuyến đắt — nó là
        # tuyến KHÔNG TỒN TẠI, và hai chuyện ấy phải nói khác nhau.
        c = self.chuoi_chung(tu.ten, den.ten, taiSan)
        if c is None:
            return khong_co_tuyen(
                f"{tu.ten} và {den.ten} không có chuỗi nào cùng dùng được cho "
                f"{taiSan} trong bảng còn hạn — rút {tu.ten}: "
                f"{_chuoi_cua_san(tu.ten, taiSan) or 'không có'}; nạp "
                f"{den.ten}: {_chuoi_cua_san(den.ten, taiSan) or 'không có'}")
        return TuyenDuong((self.chang_rut(tu.ten, taiSan, c),
                           self.chang_nap(c, den.ten, taiSan)))

    def chuoi_chung(self, sanA: str, sanB: str, taiSan: str) -> str | None:
        """Chuỗi đầu tiên theo ƯU TIÊN mà cả hai sàn cùng dùng được."""
        a = set(_chuoi_cua_san(sanA, taiSan))
        b = set(_chuoi_cua_san(sanB, taiSan))
        for c in UU_TIEN_TRUNG_GIAN:
            if c in a and c in b:
                return c
        return None

    # ── câu trả lời cho ty ──────────────────────────────────────────────

    def phi_bps(self, tu: Diem, den: Diem, taiSan: str,
                vonUsd: float) -> tuple[float | None, TuyenDuong]:
        """(bps, tuyến). `None` nghĩa là ty PHẢI giữ khai báo `phiConThieu`.

        Trả về cả tuyến chứ không chỉ con số: ty cần `khongDoDuoc` để biết
        mình còn thiếu gì, và cần `giayCho` để cộng vào `khoaVonDenGiay`.
        """
        t = self.tuyen(tu, den, taiSan, vonUsd)
        return t.phi_bps(vonUsd), t

    def tom_tat(self) -> dict:
        return {
            "chuoiCoGas": sorted(k for k, g in self.giaGas.items()
                                 if getattr(g, "weiMoiGas", None) is not None),
            "chuoiThieuGas": sorted(k for k, g in self.giaGas.items()
                                    if getattr(g, "weiMoiGas", None) is None),
            "tokenCoGia": sorted(self.giaTokenGocUsd),
            "coNguonCauNoi": self.baoGiaCau is not None,
            "nha": NHA,
            "soBaoGiaTrongKho": len(self.kho),
            "uuTienTrungGian": list(UU_TIEN_TRUNG_GIAN),
            "gasLimitUocLuong": dict(GAS_LIMIT),
        }
