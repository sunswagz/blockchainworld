"""TY TÍN DỤNG — engine thứ hai, và là PHÉP THỬ của cả kiến trúc.

Bản đồ chọn Lending làm engine #2 chứ không chọn Basis, và lý do là một
phép thử chứ không phải một sở thích:

    Perpetual  →  phái sinh, hai chân trên hai sàn, thu tại MỐC kết toán
    Lending    →  tín dụng, MỘT chân, lãi chảy liên tục, không mốc nào

Hai thứ gần như không giống nhau. Nếu cả hai cùng đi lọt qua Tờ Trình → Rủi
Ro Tổng → Danh Mục → Phân Bổ → Sổ Cái mà **không sửa một dòng nào trong
`thi_bac_ty/`**, thì lớp trừu tượng ấy là thật.

Làm Basis ngay sau Funding thì hai chiến lược quá giống nhau, và ta sẽ
*tưởng* abstraction tốt trong khi chưa kiểm được gì.

## Bảy điều ty này KHÔNG làm

    ✗ giữ tiền, biết NAV, biết ty khác đang giữ gì
    ✗ tự đặt trần vốn cho mình      ✗ dựng Rủi Ro Tổng riêng
    ✗ gọi thẳng một ty khác         ✗ đặt lệnh
    ✗ ghi thẳng vào Sổ Cái          ✗ đóng/mở cầu dao

Không có `von.py`, không có `so_cai.py`, không có `dat_lenh.py` trong thư
mục này — và sự vắng mặt ấy là điểm chính, không phải là thiếu sót.
"""
from __future__ import annotations

import asyncio

from chuoi_chung.thang import rui_ro_su_dung, rui_ro_tvl, thang
from thi_bac_ty.khuon_ty import Ty
from thi_bac_ty.to_trinh import Chan, RuiRo, ToTrinh

from .can_loi import tim_co_hoi
from .config import CONFIG, HO, MA_CHIEN_LUOC
from .nguon import DefiLlama
from .rui_ro import CongRuiRo

#: Ba khoản phí ty này CHƯA trừ được, khai tường minh vì `moHinhPhiDuChua`
#: mà rỗng danh sách là khai nửa vời: người đọc biết nó thiếu mà không biết
#: thiếu gì, nên không cân được với tờ trình của ty khác.
PHI_CON_THIEU = (
    "chuyen-von-giua-chuoi",   # chưa có Cross-chain Router
    "gia-token-thuong",        # không tính thưởng vào NET, cũng không bán được
    "thue",
    "truot-gia-khi-doi-stable",
)

SUC_CHUA_CON_THIEU = ("duong-cong-lai-suat", "do-sau-thi-truong-that")

#: Một nguồn duy nhất cho cả khai báo của ty lẫn
#: từng tờ trình nó xuất ra.
_VON_TOI_THIEU = 500.0


class TyTinDung(Ty):
    ma = MA_CHIEN_LUOC
    ho = HO
    moTa = ("xoay vốn giữa các thị trường cho vay stablecoin — một chân, "
            "lãi chảy liên tục, không mốc kết toán")

    #: Gas là chi phí CỐ ĐỊNH, nên ngưỡng kinh tế của engine này do gas
    #: quyết chứ không do lãi suất:
    #:
    #:     L2 (Base/Arbitrum)  gas khứ hồi ~$0,10 → ở $500 là 2 bps
    #:     Ethereum            gas khứ hồi ~$12   → ở $500 là 240 bps
    #:
    #: Ty khai MỘT ngưỡng cho cả engine, nên nó khai theo chuỗi RẺ; chuỗi
    #: đắt bị `netToiThieuBps` loại ở cổng ty, đúng chỗ nó thuộc về.
    vonToiThieuKinhTeUsd = _VON_TOI_THIEU

    def __init__(self, client_factory=None) -> None:
        super().__init__()
        self.nguon = DefiLlama()
        self.cong = CongRuiRo(CONFIG["ruiRo"])
        self.thiTruong: list = []
        self.coHoi: list = []
        self._client_factory = client_factory

    # ── ba việc, và chỉ ba ────────────────────────────────────────────────
    def quet(self) -> list:
        """Hỏi nguồn, dựng cơ hội. Trả CẢ cơ hội sẽ bị loại — xem `can_loi`."""
        q = CONFIG["quet"]
        self.thiTruong = _chay(self._doc())
        self.coHoi = tim_co_hoi(
            self.thiTruong,
            float(CONFIG["von"]["moiCoHoiUsd"]),
            float(q["giuGio"]),
            CONFIG["gasUsd"], CONFIG["sucChua"], self.cong)
        return list(self.coHoi)

    async def _doc(self):
        import httpx
        q = CONFIG["quet"]
        lam = self._client_factory or (lambda: httpx.AsyncClient(
            timeout=float(q["hetGioHoiGiay"]),
            headers={"User-Agent": "thi-bac-ty/0.1 (+public data only)"}))
        async with lam() as c:
            return await self.nguon.doc(c, q["taiSan"], q["chuoi"])

    def xet(self, co) -> tuple[bool, list[tuple[str, str]]]:
        """Cổng ty đã chạy trong `tim_co_hoi()`; ở đây chỉ đọc kết quả.

        Chạy lại sẽ cho cùng câu trả lời trên cùng dữ liệu, nhưng tạo ra hai
        chỗ cùng quyết một chuyện — và hai chỗ ấy sẽ lệch nhau đúng vào ngày
        ai đó sửa một chỗ.
        """
        return bool(co.duyet), list(co.lyDoMa or ())

    def trinh(self, co) -> ToTrinh:
        return xuat_to_trinh(co)


def _chay(coro):
    """Chạy một coroutine từ mã ĐỒNG BỘ, kể cả khi đang ở trong vòng lặp.

    `khuon_ty.Ty.quet()` là đồng bộ theo hợp đồng, nhưng `Runtime.mot_vong()`
    của ty phái sinh là `async` — nên khi Trung Ương gọi `quet()`, ta đang ở
    **bên trong** một vòng lặp sự kiện, và `asyncio.run()` ném thẳng:

        RuntimeError: asyncio.run() cannot be called from a running event loop

    Lỗi ấy đã xảy ra thật, và điều đáng nói là hệ thống chịu được: cổng chặn
    ngoại lệ trong `Ty.mot_luot()` giữ cho ty này không kéo theo vòng quét
    của ty kia, và `loiCuoi` nói ra chính xác chuyện gì hỏng. Nhưng chịu
    được không phải là đúng.

    ## Cái giá, nói rõ

    Chạy ở luồng riêng rồi CHỜ nó xong sẽ **khoá vòng lặp** vài giây. Với
    nhịp 900 giây và một lượt đọc ~3 giây, cứ ba mươi vòng quét thì một vòng
    bị chậm lại ngần ấy — và vòng bị chậm là vòng SAU, vì báo giá của vòng
    này đã lấy xong trước khi Trung Ương chạy.

    Đổi lại là không có luồng nền, không có trạng thái chia sẻ, không có
    cách nào để một lượt đọc dở dang lẫn vào lượt sau. Ngày ba giây ấy thành
    vấn đề thì cách sửa là đọc trước ở luồng nền và để `quet()` trả kết quả
    lượt đã xong — đắt hơn về độ phức tạp, nên chưa làm.
    """
    import concurrent.futures
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)         # không có vòng lặp nào, chạy thẳng
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
        return ex.submit(asyncio.run, coro).result()


#: Bí danh giữ cho phép kiểm cũ. Thân hàm ở `chuoi_chung/thang.py` —
#: một thang cho MỌI ty đọc chuỗi, không phải một bản cho mỗi ty.
_rui_ro_tvl = rui_ro_tvl
_rui_ro_su_dung = rui_ro_su_dung
_thang = thang


def _rui_ro(co) -> RuiRo:
    """Sáu mặt rủi ro. Mặt nào chưa đo được thì `None`, KHÔNG phải 0.

    `giaoThuc` suy từ TVL là một PROXY THÔ — TVL lớn nghĩa là đã sống lâu và
    đã bị soi nhiều, không có nghĩa là an toàn. Ghi rõ ở đây để người sau
    không đọc con số ấy như một kết quả kiểm toán.
    """
    t = co.thiTruong
    # TVL CỦA GIAO THỨC, không của pool. Thiếu thì rơi về TVL pool và chịu
    # bị chấm nặng hơn — đoán rộng lượng khi thiếu số là thưởng cho sự mù.
    gt = rui_ro_tvl(t.tvlGiaoThucUsd or t.tvlUsd)
    return RuiRo(
        # Stablecoin: rủi ro hướng giá gần như chỉ còn DEPEG. Không phải 0.
        thiTruong=0.10,
        thanhKhoan=rui_ro_su_dung(t.suDung),
        giaoThuc=gt,
        cang=gt,                    # giao thức CHÍNH LÀ đối tác ở đây
        thucThi=0.10,               # gas tăng vọt, giao dịch trượt
        cauNoi=0.0,                 # cùng chuỗi, không bắc cầu — đã ĐO, nên 0
    )


def _tin_cay(co) -> float:
    """Bắt đầu từ 1,0 rồi TRỪ dần. Cộng dồn từ 0 dễ ra những con số đẹp
    không ai giải thích được."""
    t = co.thiTruong
    d = 1.0
    if t.thanhKhoanRanhUsd is None or t.suDung is None:
        d -= 0.35
    if t.tyLeThuong > 0.25:
        d -= 0.15
    if t.tuoi_giay() > 300.0:
        d -= 0.10
    if t.tvlUsd < 20_000_000.0:
        d -= 0.10
    return max(0.0, min(1.0, d))


def xuat_to_trinh(co) -> ToTrinh:
    """`CoHoiVay` → `ToTrinh`. Không logic mới, chỉ dịch ngôn ngữ."""
    t = co.thiTruong
    hoa = ("không bao giờ hoà" if co.hoaVonSauGio is None
           else f"hoà gas sau {co.hoaVonSauGio:.1f} giờ")
    return ToTrinh(
        chienLuoc=MA_CHIEN_LUOC, ho=HO, taiSan=t.taiSan,
        chan=(Chan("CHO_VAY", t.giaoThuc, t.taiSan, co.vonXinUsd,
                   "lending", t.chuoi),),
        vonCanUsd=co.vonXinUsd,
        vonToiThieuKinhTeUsd=_VON_TOI_THIEU,
        sucChuaToiDaUsd=co.sucChuaToiDaUsd,
        grossBps=co.grossBps, phiUocBps=co.phiBps, netUocBps=co.netBps,
        giuGio=co.giuGio,
        # Rút được bất cứ lúc nào — CHỪNG NÀO còn thanh khoản rảnh. Nên khoá
        # là 0 (đã đo, không phải chưa biết), và ràng buộc thật nằm ở
        # `thanhKhoanThoatUsd` chứ không ở thời gian.
        khoaVonDenGiay=0.0,
        thanhKhoanThoatUsd=co.thanhKhoanThoatUsd,
        ruiRo=_rui_ro(co),
        tuoiDuLieuGiay=t.tuoi_giay(),
        tinCay=_tin_cay(co),
        moHinhPhiDuChua=False, phiConThieu=PHI_CON_THIEU,
        moHinhSucChuaDuChua=False, sucChuaConThieu=SUC_CHUA_CON_THIEU,
        dinhGiaBang=t.taiSan,
        cang=(t.giaoThuc,), chuoi=(t.chuoi,),
        bangChung=(
            f"{t.giaoThuc} trên {t.chuoi}",
            f"APY gốc {t.apyGocPhanTram:.2f}% (thưởng {t.apyThuongPhanTram:.2f}% "
            f"KHÔNG tính vào NET)",
            f"TVL ${t.tvlUsd / 1e6:.1f}M · dùng vốn "
            f"{'—' if t.suDung is None else format(t.suDung, '.0%')}",
            f"rút ra được $" + ("—" if t.thanhKhoanRanhUsd is None
                                else f"{t.thanhKhoanRanhUsd / 1e6:.1f}M"),
            f"gas khứ hồi {co.phiBps:.1f} bps trên ${co.vonXinUsd:.0f} · {hoa}",
        ))
