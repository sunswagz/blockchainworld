"""TY PHÁI SINH — cắm `bac/` vào khuôn `thi_bac_ty.Ty`.

File này **không** chứa logic mới. Nó là chỗ nối, và nó cố tình mỏng: mọi
việc đo đạc vẫn nằm trong `can_loi.py`, `rui_ro.py`, `xuat_to_trinh.py`. Nếu
một ngày file này dày lên thì đó là dấu hiệu logic đang trôi ra khỏi ty và
vào chỗ nối — sửa chỗ đó, đừng để nó ở đây.

## `quet()` KHÔNG gọi mạng

`Runtime.mot_vong()` đã hỏi bốn sàn và đã dựng `self.coHoi` xong. Nếu `quet()`
gọi mạng lần nữa thì mỗi vòng hỏi hai lượt, và tệ hơn: hai lượt ấy chụp hai
thời điểm khác nhau, nên báo giá dùng để tính lại không phải báo giá đã ghi
vào băng. Đúng lỗi ghép-hai-thời-điểm mà `dong_ho.py` sinh ra để chặn.

Nên `quet()` ở đây chỉ **đọc lại** lượt quét vừa xong.

## `quet()` trả về CẢ cơ hội bị loại, có chủ ý

Trả về mỗi cơ hội đã qua cổng thì `soCoHoi` bằng `soQuaCongTy`, và tỉ lệ sống
sót qua cổng ty vĩnh viễn là 100% — một con số luôn đẹp là một con số không
nói gì. Cái phễu chỉ có nghĩa khi mẫu số là số cơ hội THẬT SỰ nhìn thấy.
"""
from __future__ import annotations

from thi_bac_ty.khuon_ty import Ty

from .config import CONFIG, MA_CHIEN_LUOC
from .xuat_to_trinh import HO, _VON_TOI_THIEU, xuat_to_trinh


#: Báo giá cũ hơn ngần này thì THÔI kế toán. Nhịp quét chung là 30 giây,
#: nên 300 giây là mười nhịp liên tiếp không lấy được gì — lúc ấy nguồn
#: đang hỏng chứ không phải chỉ chậm.
TUOI_KE_TOAN_TOI_DA_GIAY = 300.0


class TyPerp(Ty):
    ma = MA_CHIEN_LUOC
    ho = HO
    moTa = ("chênh lệch funding perp giữa Hyperliquid · Binance · OKX · "
            "Bybit; delta-neutral hai chân, thu tại MỐC KẾT TOÁN")

    #: **Dưới ngần này thì kinh tế của engine không còn nghĩa.**
    #:
    #: Hai chân trên hai sàn, mỗi chân phải qua cỡ lệnh tối thiểu của sàn
    #: ấy. Dưới $100 thì một chân có thể bị sàn từ chối — và một chân bị từ
    #: chối là vị thế MỘT CHIỀU, loại rủi ro hoàn toàn khác với thứ vừa
    #: trình lên.
    #:
    #: Phí không phải ràng buộc chính ở đây: taker perp ~5 bps mỗi chiều,
    #: khứ hồi hai chân ~20 bps, và `netToiThieuBps` đã canh. Ràng buộc
    #: chính là CỠ LỆNH TỐI THIỂU.
    vonToiThieuKinhTeUsd = _VON_TOI_THIEU

    def __init__(self, runtime) -> None:
        super().__init__()
        self._rt = runtime

    # ── ba việc, và chỉ ba ────────────────────────────────────────────────
    def quet(self) -> list:
        """Đọc lại lượt quét vừa xong. Xem docstring đầu file."""
        return list(self._rt.coHoi)

    def xet(self, co) -> tuple[bool, list[tuple[str, str]]]:
        """Cổng ty đã chạy trong `tim_co_hoi()`; ở đây chỉ đọc kết quả.

        Chạy lại `cong.xet()` ở đây sẽ cho cùng một câu trả lời trên cùng dữ
        liệu, nhưng nó tạo ra hai chỗ cùng quyết một chuyện — và hai chỗ ấy
        sẽ lệch nhau đúng vào ngày ai đó sửa một chỗ.
        """
        # ZIP mã với CÂU. Bản cũ trả `list(co.lyDoMa)` — toàn mã trần,
        # đúng kiểu `list[str]` chứ không phải `list[tuple[str, str]]` mà
        # chữ ký khai. Không ai phát hiện suốt nhiều tháng vì `mot_luot()`
        # viết `qua, _ = self.xet(co)` và vứt luôn vế thứ hai; hai lỗi che
        # nhau. Lượt đầu tiên có người đọc vế ấy, bảng buồng lái hiện
        # «180× [net-am] » — mã có, câu rỗng.
        #
        # `can_loi.py` dựng `lyDo` và `lyDoMa` cùng một lượt, cùng thứ tự,
        # nên ghép lại là đúng cặp chứ không phải đoán.
        cau = list(co.lyDo or ())
        return bool(co.duyet), [
            (ma, cau[i] if i < len(cau) else "")
            for i, ma in enumerate(co.lyDoMa or ())]

    # ── kế toán: funding trả theo MỐC, không chảy liên tục ───────────────
    def ke_toan(self, viThe, toTrinh, tuGiay, denGiay):
        """Funding chỉ chảy TẠI MỐC KẾT TOÁN, nên kế toán ở đây khác hẳn
        lãi cho vay: không nhân thời gian, mà **đếm mốc đã đi qua**.

        Giữ bốn giờ trên sàn kết toán tám giờ có thể thu ĐÚNG BẰNG KHÔNG —
        câu ấy in ngay ở màn hình khởi động của runtime, và nó là lý do
        `thu_cap()` tồn tại. Cộng dồn `rate × giờ` ở đây là làm mất chính
        cái sự thật ấy: nó sẽ trả về một dòng tiền mượt trong khi tiền thật
        chảy thành từng cục, và mọi phép đo sụt vốn sẽ mượt theo.

        Dùng `phai_sinh_chung.dongho.thu_cap_qua()` — bản QUÁ KHỨ của
        cùng hàm `can_loi.py` dùng
        lúc quyết định, nên hai chỗ không thể lệch dấu. Quy ước dấu nằm
        trong đó: số trả về là phần một vị thế SHORT nhận được, chân LONG
        lấy số âm.

        Ba chỗ trả `doDuoc=False` thay vì 0, và cả ba đều là "không biết"
        chứ không phải "bằng không":

        1. không tra được báo giá của một trong hai chân trong lượt quét
           gần nhất — sàn rớt, hoặc mã bị gỡ;
        2. báo giá cũ hơn `TUOI_KE_TOAN_TOI_DA_GIAY`;
        3. sàn không công bố `mocKeMs` — `dem_moc` khi ấy phải ĐOÁN vị trí
           mốc (`uocLuong=True`), và một khoản tiền đoán ra thì không được
           ghi vào sổ cái như tiền đã nhận.
        """
        from phai_sinh_chung.dongho import thu_cap_qua

        from thi_bac_ty.ke_toan import KetToanVong

        dt = max(0.0, float(denGiay) - float(tuGiay))
        if dt <= 0.0:
            return KetToanVong(vi="chưa qua giây nào kể từ lần kế toán trước")

        ma = toTrinh.get("taiSan")
        sanLong = next((c.cang for c in viThe if c.ben == "LONG"), None)
        sanShort = next((c.cang for c in viThe if c.ben == "SHORT"), None)
        if not (ma and sanLong and sanShort):
            return KetToanVong(
                doDuoc=False,
                vi=f"vị thế không đủ hai chân LONG/SHORT để đếm mốc "
                   f"({sanLong} / {sanShort})")

        tra = {(b.ma, b.san): b for b in self._rt.baoGia}
        bL, bS = tra.get((ma, sanLong)), tra.get((ma, sanShort))
        thieu = [s for s, b in ((sanLong, bL), (sanShort, bS)) if b is None]
        if thieu:
            return KetToanVong(
                doDuoc=False,
                vi=f"KHÔNG có báo giá {ma} trên {', '.join(thieu)} trong "
                   f"lượt quét gần nhất — sàn rớt khác hẳn funding bằng 0")

        import time as _t
        nowMs = _t.time() * 1000.0
        cu = [s for s, b in ((sanLong, bL), (sanShort, bS))
              if b.nhanTsMs and (nowMs - b.nhanTsMs) / 1000.0
              > TUOI_KE_TOAN_TOI_DA_GIAY]
        if cu:
            return KetToanVong(
                doDuoc=False,
                vi=f"báo giá {ma} trên {', '.join(cu)} cũ hơn "
                   f"{TUOI_KE_TOAN_TOI_DA_GIAY:.0f}s")

        # Bản QUÁ KHỨ. Docstring trên nói "đếm mốc ĐÃ ĐI QUA" và đó
        # đúng là ý định, nhưng `thu_cap` đếm mốc SẮP TỚI — nên nó trả 0
        # ở mọi vòng kế toán, mãi mãi. Cùng lỗi với `ty_co_so`; ty này
        # chưa lộ ra vì chưa có vị thế nào mở trên làn thật.
        r = thu_cap_qua(float(tuGiay) * 1000.0, float(denGiay) * 1000.0,
                        bL.rate, bL.mocKeMs, bL.intervalGio,
                        bS.rate, bS.mocKeMs, bS.intervalGio)
        # MỘT cửa duy nhất cho "lịch mốc phải đoán", không hai.
        #
        # Bản đầu kiểm `mocKeMs is None` ở đây RỒI kiểm `uocLuong` sau. Hai
        # câu ấy nói cùng một điều — `dem_moc` đặt `uoc = mocKeMs is None`
        # và không còn đường nào khác bật cờ — nên cái sau không bao giờ
        # chạy khi cái trước đã chặn, và ngược lại. Phép cấy lỗi ngược lộ
        # ra ngay: bỏ MỖI cái đều KHÔNG làm phép kiểm nào đỏ, vì cái còn
        # lại che.
        #
        # Giữ `uocLuong` chứ không giữ `mocKeMs is None`: cờ ấy là lời khai
        # của `dem_moc` về chính nó. Ngày nào nó học được cách suy lịch mốc
        # từ nguồn khác, cửa này vẫn đúng; còn bản chép lại điều kiện thì
        # sai âm thầm.
        if r["uocLuong"]:
            return KetToanVong(
                doDuoc=False,
                vi=f"lịch mốc của {ma} phải ước lượng (sàn không công bố "
                   f"mốc kế tiếp) — tiền đoán ra không ghi vào sổ như tiền "
                   f"đã nhận")

        soMoc = int(r["soMocLong"]) + int(r["soMocShort"])
        von = sum(abs(float(getattr(c, "vonUsd", 0.0) or 0.0))
                  for c in viThe) / 2.0        # notional MỘT chân
        thu = von * float(r["thu"])
        return KetToanVong(
            thuUsd=thu,
            vi=(f"funding {ma}: {soMoc} mốc đi qua trong {dt / 3600:.4f}h "
                f"(short {sanShort} +{r['thuShort']:.6%}, long {sanLong} "
                f"−{r['traLong']:.6%}) trên {von:.2f} USD mỗi chân"
                if soMoc else
                f"funding {ma}: KHÔNG mốc nào rơi vào {dt / 3600:.4f}h vừa "
                f"qua — thu đúng bằng 0, và đây là 0 ĐO ĐƯỢC"))

    def trinh(self, co):
        """Dịch sang `ToTrinh`. `oiUsd` tra từ CHÍNH lượt quét này."""
        oi = {(b.ma, b.san): b.oiUsd for b in self._rt.baoGia}
        xin = float((CONFIG.get("von") or {}).get("moiCoHoiUsd", 100.0))
        return xuat_to_trinh(
            co, vonXinUsd=xin,
            oiLongUsd=oi.get((co.ma, co.sanLong)),
            oiShortUsd=oi.get((co.ma, co.sanShort)))
