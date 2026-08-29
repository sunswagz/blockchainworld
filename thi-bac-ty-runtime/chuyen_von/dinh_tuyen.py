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


#: Báo giá cầu quá tuổi này thì vẫn DÙNG, nhưng phải KHAI ra. Hai giờ là
#: bốn lượt nạp (nhịp 30 phút) — quá đó nghĩa là bốn lượt liên tiếp không
#: lấy được số mới, và đó là một trạng thái đáng nói.
TUOI_BAO_GIA_TOI_DA_GIAY = 7200.0


def _tuoi_giay(bg) -> float | None:
    import time
    t = getattr(bg, "docLucMs", None)
    if not t:
        return None
    return max(0.0, (time.time() * 1000.0 - float(t)) / 1000.0)


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
            if isinstance(bg, BaseException):
                continue
            k = _khoa(ts, a, b, v)
            cu = self.kho.get(k)
            # KHÔNG đè một báo giá TỐT bằng một báo giá MÙ.
            #
            # Đã cắn: một lần 429 làm cả chín tuyến thành "đang nghỉ", và
            # `nap()` ghi đè lên chín báo giá còn dùng được — cỗ máy đang
            # chạy hoá mù hoàn toàn suốt hai giờ, trong khi phí cầu đổi
            # chậm tới mức số cũ vẫn còn nghĩa.
            #
            # Đổi lại: số cũ phải KHAI TUỔI. Xem `chang_cau()`.
            if (not getattr(bg, "doDuoc", False)
                    and cu is not None and getattr(cu, "doDuoc", False)):
                continue
            self.kho[k] = bg
        return self.kho

    # ── kho sống qua lần khởi động lại ──────────────────────────────────

    def luu_kho(self, duong) -> int:
        """Ghi báo giá ĐO ĐƯỢC ra đĩa. Trả về số bản đã ghi.

        Chỉ ghi cái đo được: một báo giá mù ghi ra đĩa rồi nạp lại ở lần
        chạy sau là mang theo sự mù qua một ranh giới mà nó lẽ ra không
        vượt được.
        """
        import json
        from pathlib import Path
        ds = []
        for k, bg in self.kho.items():
            if not getattr(bg, "doDuoc", False):
                continue
            ds.append({"khoa": list(k), "taiSan": bg.taiSan,
                       "tuChuoi": bg.tuChuoi, "denChuoi": bg.denChuoi,
                       "vonUsd": bg.vonUsd, "phiTaiSan": bg.phiTaiSan,
                       "gasUsd": bg.gasUsd, "giayCho": bg.giayCho,
                       "congCu": bg.congCu, "docLucMs": bg.docLucMs})
        p = Path(duong)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({"baoGia": ds}, ensure_ascii=False),
                     encoding="utf-8")
        return len(ds)

    def nap_kho(self, duong) -> dict:
        """Nạp lại kho từ đĩa lúc khởi động. Trả về tóm tắt để nhật ký nói.

        Vì sao cần: LI.FI có hạn mức giờ, và mỗi lần khởi động nạp trước
        chín báo giá. Khởi động lại năm lần trong một giờ — chuyện thường
        khi đang sửa mã — là tự đẩy mình vào 429 và nghỉ 80 phút, tức là
        **mọi tuyến liên chuỗi mù** đúng lúc vừa bật máy lên. Đã xảy ra
        thật ngày 28/08/2026.

        Kho nằm trong RAM nên nó chết theo tiến trình, trong khi phí cầu
        đổi rất chậm — vứt nó đi ở ranh giới tiến trình là **thay tri thức
        bằng sự mù**, đúng cái luật `nap()` đã giữ trong một vòng chạy.

        Ba ràng buộc, và cả ba đều là điều kiện để việc này không thành
        nói dối:

        1. **Quá hạn thì BỎ.** `TUOI_BAO_GIA_TOI_DA_GIAY` là ngưỡng đã có;
           nạp lại một báo giá già hơn thế là lách chính ngưỡng ấy.
        2. **KHÔNG đè cái đang có trong RAM.** Bản trong bộ nhớ luôn mới
           hơn hoặc bằng bản trên đĩa.
        3. **Tuổi vẫn tính từ `docLucMs` gốc**, không đóng dấu lại lúc
           nạp. Đóng dấu lại là làm một báo giá hai tiếng trông như vừa
           đọc xong — `chang_cau()` sẽ thôi khai tuổi, và cái khai tuổi ấy
           mới là thứ khiến việc dùng số cũ trung thực.
        """
        import json
        import time
        from pathlib import Path
        from .cau_noi import BaoGiaCau
        p = Path(duong)
        if not p.is_file():
            return {"nap": 0, "boQuaCu": 0, "boQuaDaCo": 0, "co": False}
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            return {"nap": 0, "loi": f"{type(e).__name__}: {e}", "co": True}
        now = time.time() * 1000.0
        nap = cu = daCo = 0
        for x in (d.get("baoGia") or []):
            try:
                k = tuple(x["khoa"][:3]) + (x["khoa"][3],)
                tuoi = (now - float(x["docLucMs"])) / 1000.0
            except (KeyError, TypeError, ValueError):
                continue
            if tuoi > TUOI_BAO_GIA_TOI_DA_GIAY:
                cu += 1
                continue
            if k in self.kho:
                daCo += 1
                continue
            self.kho[k] = BaoGiaCau(
                taiSan=x["taiSan"], tuChuoi=x["tuChuoi"],
                denChuoi=x["denChuoi"], vonUsd=float(x["vonUsd"]),
                phiTaiSan=x["phiTaiSan"], gasUsd=x["gasUsd"],
                giayCho=x["giayCho"], congCu=x.get("congCu") or "?",
                docLucMs=float(x["docLucMs"]))
            nap += 1
        return {"nap": nap, "boQuaCu": cu, "boQuaDaCo": daCo, "co": True}

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
        thieu = ["rui-ro-cau-noi", "gas-limit-uoc-luong"]
        # Báo giá GIỮ LẠI thì phải khai tuổi. Giữ số cũ tốt hơn mù, nhưng
        # dùng số cũ mà im lặng thì tệ hơn cả hai.
        tuoi = _tuoi_giay(bg)
        if tuoi is not None and tuoi > TUOI_BAO_GIA_TOI_DA_GIAY:
            thieu.append(f"bao-gia-cau-cu:{tuoi / 60:.0f}phut")
        return ChangDuong(tu, den, "cau-noi", bg.tongUsd, bg.giayCho,
                          f"LI.FI qua {bg.congCu}"
                          + (f" · báo giá {tuoi / 60:.0f} phút tuổi"
                             if tuoi is not None
                             and tuoi > TUOI_BAO_GIA_TOI_DA_GIAY else ""),
                          tuple(thieu))

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
        mình còn thiếu gì, và cần `giayCho` để cộng vào `khoaVonDenGio`.
        """
        t = self.tuyen(tu, den, taiSan, vonUsd)
        return t.phi_bps(vonUsd), t

    def chuoi_dung_duoc(self) -> tuple:
        """Chuỗi thật sự tính được phí — có CẢ gas LẪN giá token gốc.

        Khác `chuoiCoGas`, và khác biệt ấy đã nói dối một lần: Polygon đọc
        được gas nhưng `POL` không có giá, nên `_gas_usd()` trả `None` và
        mọi tuyến Polygon mù — trong khi buồng lái báo "gas SỐNG trên 4
        chuỗi". Một đèn xanh cho thứ không chạy.

        Con số đáng báo là con số DÙNG ĐƯỢC, không phải con số ĐỌC ĐƯỢC.
        """
        return tuple(sorted(
            k for k in self.giaGas
            if self._gas_usd(k, "chuyen-erc20") is not None))

    def tom_tat(self) -> dict:
        dung = self.chuoi_dung_duoc()
        coGas = sorted(k for k, g in self.giaGas.items()
                       if getattr(g, "weiMoiGas", None) is not None)
        return {
            "chuoiDungDuoc": list(dung),
            # Đọc được gas nhưng THIẾU giá token gốc → vẫn mù. Tách riêng
            # vì hai trạng thái này đòi hai cách sửa khác nhau.
            "chuoiCoGasNhungThieuGia": sorted(set(coGas) - set(dung)),
            "chuoiCoGas": coGas,
            "chuoiThieuGas": sorted(k for k, g in self.giaGas.items()
                                    if getattr(g, "weiMoiGas", None) is None),
            "tokenCoGia": sorted(self.giaTokenGocUsd),
            "coNguonCauNoi": self.baoGiaCau is not None,
            "nha": NHA,
            "soBaoGiaTrongKho": len(self.kho),
            "uuTienTrungGian": list(UU_TIEN_TRUNG_GIAN),
            "gasLimitUocLuong": dict(GAS_LIMIT),
        }
