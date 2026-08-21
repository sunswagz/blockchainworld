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

from .bus import bus
from .can_loi import tim_co_hoi
from .config import CONFIG, DATA_DIR, che_hieu_luc
from .models import BaoGia
from .rui_ro import CongRuiRo
from .san import TAT_CA
from .so import So


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

    # ── một vòng ──────────────────────────────────────────────────────────
    async def mot_vong(self) -> None:
        self.vong += 1
        t0 = time.perf_counter()
        q = CONFIG["quet"]

        async with httpx.AsyncClient(
                timeout=float(q["hetGioHoiGiay"]),
                headers={"User-Agent": "thi-bac-ty/0.1 (+public data only)"}) as client:
            ds = list(self.cang.values())
            goi = await asyncio.gather(*(c.bao_gia(client, list(q["ma"])) for c in ds))

        now = time.time() * 1000.0
        tho: list[BaoGia] = [b for lo in goi for b in lo]

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
        if n:
            bus.ghi(f"dọn sổ: xoá {n} bản ghi quá {CONFIG['so']['giuNgay']} ngày",
                    loai="he")

    # ── ảnh chụp cho buồng lái và cho lát cắt ─────────────────────────────
    def anh_chup(self) -> dict:
        now = time.time() * 1000.0
        q = CONFIG["quet"]
        duyet = [c for c in self.coHoi if c.duyet]

        # Đếm lý do từ chối. Đây là số liệu ĐÁNG GIÁ NHẤT của cả bảng: không
        # cơ hội nào qua cửa thì câu hỏi tiếp theo luôn là "vì sao", và không
        # có bảng này thì người vận hành đi nới bừa từng ngưỡng một.
        vi_sao: dict[str, int] = {}
        for c in self.coHoi:
            for l in c.lyDo:
                khoa = l.split("—")[0].split("<")[0].split(">")[0].strip()
                vi_sao[khoa] = vi_sao.get(khoa, 0) + 1

        return {
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
            "phiSan": {k: v for k, v in CONFIG["san"].items()
                       if (v or {}).get("bat")},
            "ruiRo": self.cong.tom_tat(),
            "baoGia": [b.tom_tat(now) for b in self.baoGia],
            "coHoi": [c.tom_tat() for c in self.coHoi[:60]],
            "soDuyet": len(duyet),
            "viSaoTuChoi": vi_sao,
            "so": self.so.thong_ke(),
            "doDai": [
                {**self.so.do_dai(c.ma, c.sanLong, c.sanShort),
                 "ma": c.ma, "sanLong": c.sanLong, "sanShort": c.sanShort}
                for c in self.coHoi[:12]
            ],
            "duongSo": str(DATA_DIR),
            "nhatKy": bus.gan_day(80),
        }


runtime = Runtime()
