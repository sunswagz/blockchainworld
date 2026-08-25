"""Vòng lặp nền — hỏi bốn cảng, ghép cặp, cân lợi, ghi sổ.

Một vòng làm đúng năm việc, theo đúng thứ tự này:

    1. hỏi CẢ BỐN cảng song song, cùng một lúc
    2. bỏ báo giá quá cũ
    3. ghép mọi cặp sàn cho từng mã, tính NET
    4. cho qua cổng rủi ro
    5. ghi sổ — kể cả khi không cơ hội nào qua cửa

**Hỏi song song không phải để nhanh.** Bốn cảng hỏi tuần tự cách nhau vài trăm
mili giây là bốn ảnh chụp ở bốn thời điểm khác nhau, rồi đem so với nhau như
thể chúng cùng lúc. Trong một cú biến động, mark của cảng hỏi trước và cảng
hỏi sau lệch nhau chỉ vì thứ tự hỏi — và cổng `lechMarkToiDaBps` sẽ chặn một
cơ hội hoàn toàn lành, hoặc tệ hơn, thả một cơ hội đã hỏng.
"""
from __future__ import annotations

import asyncio
import threading
import time

import httpx

from .bang import may_ghi
from .bus import bus
from .can_loi import tim_co_hoi
from .config import CONFIG, DATA_DIR, MA_CHIEN_LUOC, che_hieu_luc
from .dong_ho import NGUONG_KEU_MS, do_lech, dong_ho
from .models import BaoGia
from .rui_ro import NHAN, CongRuiRo
from .san import TAT_CA
from .so import So


#: Bao lâu hỏi lại giờ máy chủ một lần. Lệch đồng hồ trôi chậm (NTP tắt thì
#: nó trôi cỡ giây mỗi giờ), nên hỏi mỗi 5 phút là quá đủ — ba lượt hỏi thêm
#: mỗi 30 giây chỉ tổ tốn hạn mức cho một con số gần như đứng yên.
NHIP_DO_DONG_HO_GIAY = 300.0


class Runtime:
    def __init__(self) -> None:
        self.cang = {}
        for ten, lop in TAT_CA.items():
            if (CONFIG["san"].get(ten) or {}).get("bat", False):
                self.cang[ten] = lop()

        self.cong = CongRuiRo(CONFIG["ruiRo"])
        self.so = So()

        self.vong = 0
        self.batDauLuc = time.time()
        self.tamDung = False
        self.baoGia: list[BaoGia] = []
        self.coHoi = []
        self.loiVongCuoi: str | None = None
        self.quetCuoiMs: float = 0.0
        self.quetLauNhatMs: float = 0.0

        self._chay = False
        self._luong: threading.Thread | None = None
        self._ngayDonSo = ""
        self._daKeuLech = False
        self._lanDoDongHo = 0.0
        self._doDongHoHong = False

    # ── điều khiển ────────────────────────────────────────────────────────
    def bat(self) -> None:
        if self._chay:
            return
        self._chay = True
        self._luong = threading.Thread(target=self._vong_lap, daemon=True)
        self._luong.start()
        bus.ghi(f"Thị Bạc Ty chạy — {len(self.cang)} cảng, "
                f"{len(CONFIG['quet']['ma'])} mã, chế độ {che_hieu_luc()}", loai="he")

    def dung(self) -> None:
        self._chay = False
        may_ghi.dong()
        bus.ghi("runtime dừng", loai="he")

    def _vong_lap(self) -> None:
        nhip = float(CONFIG["nhipGiay"])
        while self._chay:
            t0 = time.time()
            try:
                if not self.tamDung:
                    asyncio.run(self.mot_vong())
            except Exception as e:                  # noqa: BLE001
                self.loiVongCuoi = f"{type(e).__name__}: {e}"
                bus.ghi(f"vòng {self.vong} lỗi: {self.loiVongCuoi}", loai="loi")
            con = nhip - (time.time() - t0)
            if con > 0:
                time.sleep(con)

    def _hen_do_dong_ho(self) -> float:
        """Đo hỏng thì thử lại sớm, đừng khoá trọn 5 phút.

        Bản đầu đặt mốc hẹn TRƯỚC khi gọi, nên một lượt đo hỏng vẫn khoá
        tiếp 5 phút: lỗi báo đúng một lần rồi im, và runtime chạy tiếp trên
        giờ MÁY chưa bù trong khi bảng không nói gì. Đã cắn thật lúc dựng —
        `NameError` ở vòng 1, rồi ba vòng sau xanh trơn.
        """
        return 30.0 if self._doDongHoHong else NHIP_DO_DONG_HO_GIAY

    # ── một vòng ──────────────────────────────────────────────────────────
    async def mot_vong(self) -> None:
        self.vong += 1
        t0 = time.perf_counter()
        q = CONFIG["quet"]

        async with httpx.AsyncClient(
                timeout=float(q["hetGioHoiGiay"]),
                headers={"User-Agent": "thi-bac-ty/0.1 (+public data only)"}) as client:
            # Đo lệch đồng hồ TRƯỚC khi hỏi báo giá: adapter đóng dấu bằng
            # `bay_gio_ms()`, nên phần bù phải sẵn sàng trước lúc chúng chạy.
            if time.time() - self._lanDoDongHo > self._hen_do_dong_ho():
                soMau = await do_lech(client, dong_ho)
                self._lanDoDongHo = time.time()
                self._doDongHoHong = soMau == 0
                if soMau == 0:
                    bus.ghi("KHÔNG đo được lệch đồng hồ — mọi phép đếm mốc "
                            "đang chạy trên giờ MÁY, thử lại sau 30s", loai="canh")

            ds = list(self.cang.values())
            goi = await asyncio.gather(*(c.bao_gia(client, list(q["ma"])) for c in ds))

        tho: list[BaoGia] = [b for lo in goi for b in lo]

        now = dong_ho.bay_gio_ms()

        lech = dong_ho.lech_ms()
        if lech is not None and abs(lech) > NGUONG_KEU_MS and not self._daKeuLech:
            self._daKeuLech = True
            bus.ghi(f"ĐỒNG HỒ MÁY lệch {lech / 1000:+.0f}s so với sàn — đã bù "
                    f"khi đếm mốc, nhưng nên chỉnh lại NTP", loai="canh")

        # Lọc báo giá quá cũ TRƯỚC khi ghép cặp. Lọc sau thì một báo giá chết
        # vẫn kịp sinh ra ba cặp, và cả ba đều mang lý do từ chối giống hệt
        # nhau — nhật ký ngập ba dòng nói cùng một chuyện.
        tran = float(CONFIG["ruiRo"]["tuoiToiDaGiay"])
        self.baoGia = []
        bo_cu = 0
        for b in tho:
            t = b.tuoi_giay(now)
            if t is not None and t > tran:
                bo_cu += 1
                continue
            self.baoGia.append(b)
        if bo_cu:
            bus.ghi(f"bỏ {bo_cu} báo giá cũ hơn {tran:.0f}s", loai="canh")

        self.coHoi = tim_co_hoi(self.baoGia, now, float(q["giuGio"]),
                                CONFIG["san"], self.cong)

        loi = [c.ten for c in self.cang.values() if c.suc_khoe.loiCuoi
               and (c.suc_khoe.tuoi_giay() or 1e9) > float(CONFIG["nhipGiay"]) * 2]
        self.so.ghi_luot(self.coHoi, len(self.baoGia), loi)

        # Băng ghi NGUYÊN LIỆU, sổ ghi KẾT LUẬN. Thiếu băng thì không chạy
        # lại được, và không chạy lại được thì mọi lần vặn ngưỡng đều là đổi
        # số cho vui — không cách nào biết tốt hơn hay chỉ khác đi.
        may_ghi.ghi({
            "luc": now,
            "vong": self.vong,
            "giuGio": float(q["giuGio"]),
            "lechDongHoMs": dong_ho.lech_ms(),
            "baoGia": [b.tom_tat(now) for b in self.baoGia],
        })

        duyet = [c for c in self.coHoi if c.duyet]
        for c in duyet:
            bus.ghi(f"{c.ma}: LONG {c.sanLong} / SHORT {c.sanShort} · "
                    f"NET {c.netBps:+.2f} bps trong {c.giuGio:g}h "
                    f"({c.soMocLong}+{c.soMocShort} mốc)", loai="tin")

        self._don_so_moi_ngay()
        d = (time.perf_counter() - t0) * 1000.0
        self.quetCuoiMs = d
        self.quetLauNhatMs = max(self.quetLauNhatMs, d)

    def _don_so_moi_ngay(self) -> None:
        ngay = time.strftime("%Y-%m-%d", time.gmtime())
        if ngay == self._ngayDonSo:
            return
        self._ngayDonSo = ngay
        n = self.so.don_cu(int(CONFIG["so"]["giuNgay"]))
        nb = may_ghi.don_cu()
        if n or nb:
            bus.ghi(f"dọn: xoá {n} bản ghi sổ và {nb} file băng quá "
                    f"{CONFIG['so']['giuNgay']} ngày", loai="he")

    # ── ảnh chụp cho buồng lái và cho lát cắt ─────────────────────────────
    def anh_chup(self) -> dict:
        now = dong_ho.bay_gio_ms()
        q = CONFIG["quet"]
        duyet = [c for c in self.coHoi if c.duyet]

        # Đếm lý do từ chối. Đây là số liệu ĐÁNG GIÁ NHẤT của cả bảng: không
        # cơ hội nào qua cửa thì câu hỏi tiếp theo luôn là "vì sao", và không
        # có bảng này thì người vận hành đi nới bừa từng ngưỡng một.
        #
        # Gộp theo MÃ, không theo câu. Bản đầu cắt chuỗi câu để lấy khoá, mà
        # câu có mang con số — nên "NET sau phí" vỡ thành sáu dòng nói cùng
        # một chuyện, và bảng mất đúng công dụng của nó.
        vi_sao: dict[str, int] = {}
        for c in self.coHoi:
            for ma in c.lyDoMa:
                vi_sao[NHAN.get(ma, ma)] = vi_sao.get(NHAN.get(ma, ma), 0) + 1

        return {
            "maChienLuoc": MA_CHIEN_LUOC,
            "vong": self.vong,
            "batDauLuc": self.batDauLuc,
            "chayDuocGiay": time.time() - self.batDauLuc,
            "tamDung": self.tamDung,
            "che": che_hieu_luc(), "cheKhai": CONFIG.get("che"),
            "nhipGiay": CONFIG["nhipGiay"],
            "giuGio": q["giuGio"],
            "ma": list(q["ma"]),
            "quetCuoiMs": self.quetCuoiMs,
            "quetLauNhatMs": self.quetLauNhatMs,
            "loiVongCuoi": self.loiVongCuoi,
            "cang": [c.suc_khoe.tom_tat() for c in self.cang.values()],
            "dongHo": dong_ho.tom_tat(),
            "phiSan": {k: v for k, v in CONFIG["san"].items()
                       if (v or {}).get("bat")},
            "ruiRo": self.cong.tom_tat(),
            # Tách hẳn khỏi `ruiRo`: đây là trần vốn CHƯA có hiệu lực, không
            # phải cửa rủi ro. Gộp chung là bày ba con số không chặn gì dưới
            # nhãn "đang có hiệu lực" — đúng lỗi vừa gỡ.
            "von": dict(CONFIG.get("von") or {}),
            "baoGia": [b.tom_tat(now) for b in self.baoGia],
            "coHoi": [c.tom_tat() for c in self.coHoi[:60]],
            "soDuyet": len(duyet),
            "viSaoTuChoi": vi_sao,
            "so": self.so.thong_ke(),
            "bang": may_ghi.tom_tat(),
            "doDai": [
                {**self.so.do_dai(c.ma, c.sanLong, c.sanShort),
                 "ma": c.ma, "sanLong": c.sanLong, "sanShort": c.sanShort}
                for c in self.coHoi[:12]
            ],
            "duongSo": str(DATA_DIR),
            "nhatKy": bus.gan_day(80),
        }


runtime = Runtime()
