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
from thi_bac_ty.khuon_ty import Ty

from .so import So
from .ty_perp import TyPerp
from .xuat_to_trinh import xuat_to_trinh


#: Bao lâu hỏi lại giờ máy chủ một lần. Lệch đồng hồ trôi chậm (NTP tắt thì
#: nó trôi cỡ giây mỗi giờ), nên hỏi mỗi 5 phút là quá đủ — ba lượt hỏi thêm
#: mỗi 30 giây chỉ tổ tốn hạn mức cho một con số gần như đứng yên.
NHIP_DO_DONG_HO_GIAY = 300.0


class _NhipRieng(Ty):
    """Bọc một ty để nó quét THƯA hơn nhịp chung.

    Vòng quét chạy mỗi 30 giây vì funding đổi theo giây. Lãi cho vay thì đổi
    theo giờ, mà một lượt quét nó là kéo về hai bảng ~17.000 dòng — nên bám
    nhịp chung là đốt băng thông cho một con số gần như đứng yên, và làm
    phiền một nguồn công cộng miễn phí.

    Giữa hai lượt, `quet()` trả lại **kết quả lượt trước** chứ không trả
    rỗng. Trả rỗng thì cơ hội biến mất rồi hiện lại, và cửa chống trùng ở
    Trung Ương ghi nhận chúng như cơ hội MỚI — vòng nào cũng đẻ một loạt tờ
    trình trùng, và cái phễu lại nói dối.

    ## Kế thừa `Ty`, KHÔNG vá nóng

    Bản đầu bọc bằng cách gán đè `ty.quet` rồi gọi `ty.mot_luot()`. Nó tự
    đệ quy: `mot_luot` gọi `self.quet` — nay chính là hàm của lớp bọc — và
    hàm ấy gọi lại `self._ty.quet`, cũng chính nó. Không có `RecursionError`
    vì lần gọi thứ hai rơi đúng vào nhánh "chưa tới nhịp" và trả rỗng, nên
    ty quét được **không lần nào** trong khi mọi thứ vẫn xanh.

    Đúng loại hỏng im lặng mà cả runtime này sinh ra để bắt, và nó lọt vì
    lớp bọc thông minh hơn mức cần thiết. Nay nó là một `Ty` bình thường:
    ba hàm, `quet()` có nhịp, hai hàm kia uỷ quyền thẳng.
    """

    def __init__(self, ty, nhipGiay: float) -> None:
        super().__init__()
        self._ty = ty
        self._nhip = float(nhipGiay)
        self._lanCuoi = 0.0
        self._cu: list = []
        self.soLuotBoQua = 0

    # ── khai báo là của ty THẬT, không của lớp bọc ───────────────────────
    #
    # Phải viết TAY từng thuộc tính, không dựa được vào `__getattr__`:
    # `Ty` đã khai sẵn `ma`/`ho`/`moTa`/`vonToiThieuKinhTeUsd` ở tầng lớp,
    # nên tra thuộc tính THÀNH CÔNG (ra giá trị rỗng của lớp bọc) và
    # `__getattr__` không bao giờ được gọi.
    #
    # Lỗi này đã xảy ra hai lần: một lần với `kiem_khai`, một lần với
    # `vonToiThieuKinhTeUsd` — lần thứ hai làm ba ty tụt xuống QUAN_SAT vì
    # trung ương đọc ra "chưa khai ngưỡng". Có phép kiểm canh: mọi thuộc
    # tính KHAI BÁO của lớp bọc phải khớp ty thật.
    @property
    def ma(self): return self._ty.ma

    @property
    def ho(self): return self._ty.ho

    @property
    def moTa(self): return self._ty.moTa

    @property
    def vonToiThieuKinhTeUsd(self): return self._ty.vonToiThieuKinhTeUsd

    def kiem_khai(self):
        """Soi khai báo của ty THẬT. Bọc không phải đường vòng qua cổng."""
        return type(self._ty).kiem_khai()

    # ── ba việc ───────────────────────────────────────────────────────────
    def quet(self):
        now = time.monotonic()
        if self._lanCuoi and (now - self._lanCuoi) < self._nhip:
            self.soLuotBoQua += 1
            return list(self._cu)
        self._lanCuoi = now
        self._cu = list(self._ty.quet())
        return list(self._cu)

    def xet(self, co):
        return self._ty.xet(co)

    def trinh(self, co):
        return self._ty.trinh(co)

    # Tiện đọc `._nguon`, `.coHoi`… của ty thật từ buồng lái.
    def __getattr__(self, ten):
        return getattr(self.__dict__["_ty"], ten)

    def tom_tat(self) -> dict:
        return {**super().tom_tat(), "nhipGiay": self._nhip,
                "soLuotBoQua": self.soLuotBoQua}


class Runtime:
    def __init__(self) -> None:
        self.cang = {}
        for ten, lop in TAT_CA.items():
            if (CONFIG["san"].get(ten) or {}).get("bat", False):
                self.cang[ten] = lop()

        self.cong = CongRuiRo(CONFIG["ruiRo"])
        self.so = So()

        # ── Thị Bạc Ty đứng TRÊN ty này ──────────────────────────────────
        # Chiều phụ thuộc chỉ đi một hướng: `bac` biết `thi_bac_ty`, không
        # bao giờ ngược lại. Ngày trung ương phải import một ty để xử một
        # trường hợp riêng là ngày hợp đồng đã hỏng — `scripts/selftest.py`
        # canh đúng chuyện đó.
        tu = CONFIG.get("trungUong") or {}
        self.trungUong = None
        self.tyTinDung = None
        self.tyPhu = {}
        if tu.get("bat", True):
            from thi_bac_ty.trung_uong import TrungUong
            self.trungUong = TrungUong(
                DATA_DIR, {k: v for k, v in tu.items()
                           if k not in ("bat", "tyTinDung", "tyOnDinh",
                                        "tyLaiSuat")})
            self.trungUong.dang_ky(TyPerp(self))

            # Ty thứ hai — TÍN DỤNG. Nó cắm vào cùng `khuon_ty.Ty`, không
            # dựng runtime riêng, và đó là toàn bộ điểm của nó: hai chiến
            # lược khác hẳn nhau sống dưới một Thị Bạc Ty.
            #
            # Bọc try vì một ty mới không được phép làm chết vòng quét của
            # ty đang chạy. Hỏng thì `loiVongCuoi` nói ra, không im.
            # Ba ty còn lại, cùng một lối: bọc nhịp riêng, bọc try riêng.
            # Một ty mới hỏng KHÔNG được làm chết vòng quét của ty đang
            # chạy, và cũng không được kéo theo hai ty mới còn lại — nên
            # mỗi cái một `try`, không gộp.
            self.tyPhu = {}
            for khoa, nap, nhip in (
                    ("tyTinDung",
                     lambda: __import__("tin_dung.ty_vay",
                                        fromlist=["TyTinDung"]).TyTinDung(),
                     900.0),
                    ("tyOnDinh",
                     lambda: __import__("on_dinh.ty_on_dinh",
                                        fromlist=["TyOnDinh"]).TyOnDinh(),
                     120.0),
                    ("tyLaiSuat",
                     lambda: __import__("lai_suat.ty_lai_suat",
                                        fromlist=["TyLaiSuat"]).TyLaiSuat(),
                     3600.0)):
                cf = (tu.get(khoa) or {})
                if not cf.get("bat", True):
                    continue
                try:
                    t = _NhipRieng(nap(), float(cf.get("nhipGiay", nhip)))
                    if self.trungUong.dang_ky(t):
                        self.tyPhu[khoa] = t
                except Exception as e:                   # noqa: BLE001
                    self.loiVongCuoi = f"{khoa}: {type(e).__name__}: {e}"
            self.tyTinDung = self.tyPhu.get("tyTinDung")
        self.latCatTrungUong = None

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

        # ── giao lại cho Trung Ương ──────────────────────────────────────
        # Đặt SAU khi đã ghi băng: băng là nguyên liệu, phải còn nguyên kể cả
        # khi trung ương nổ. Và bọc try vì một lỗi ở tầng phân bổ không được
        # phép làm chết vòng quét — mất một vòng phân bổ là mất một cơ hội,
        # mất vòng quét là mất cả khả năng nhìn.
        if self.trungUong is not None:
            try:
                self.latCatTrungUong = self.trungUong.mot_vong(
                    lechDongHoGiay=(None if lech is None else lech / 1000.0),
                    cangChet=loi,
                    tuoiXauNhatGiay=max(
                        (t for t in (b.tuoi_giay(now) for b in self.baoGia)
                         if t is not None), default=None))
                l = self.latCatTrungUong
                if l.cauDaoNgat:
                    bus.ghi("CẦU DAO NGẮT — không cam kết vốn: "
                            + "; ".join(l.lyDoNgat), loai="canh")
                elif l.phanBo and l.phanBo["soCap"]:
                    bus.ghi(f"Thị Bạc Ty cấp {l.phanBo['tongCapUsd']:.0f} USD "
                            f"cho {l.phanBo['soCap']} tờ trình "
                            f"[SỔ GIẤY]", loai="tin")
            except Exception as e:                       # noqa: BLE001
                self.loiVongCuoi = f"trung ương: {type(e).__name__}: {e}"
                bus.ghi(f"Trung Ương lỗi: {e}", loai="canh")

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

    # ── xuất tờ trình lên Thị Bạc Ty ──────────────────────────────────────
    def to_trinh(self) -> list:
        """Tờ trình ĐÃ NỘP lên Thông Chính Ty trong vòng gần nhất.

        Đọc lại từ Trung Ương chứ **không dựng lại**. Dựng lại thì mỗi lần
        sinh một `ma` mới (uuid), nên tờ trên màn hình và tờ trong sổ đăng ký
        mang hai mã khác nhau cho cùng một cơ hội — người đọc không nối được
        hai bảng, và cả sổ đăng ký mất tác dụng truy nguyên.

        Trung Ương tắt thì dựng tại chỗ, để buồng lái vẫn xem được ty đang
        định trình gì.
        """
        if self.trungUong is not None:
            return list(self.trungUong.toTrinhVongNay)
        oi = {(b.ma, b.san): b.oiUsd for b in self.baoGia}
        xin = float((CONFIG.get("von") or {}).get("moiCoHoiUsd", 100.0))
        return [xuat_to_trinh(c, vonXinUsd=xin,
                              oiLongUsd=oi.get((c.ma, c.sanLong)),
                              oiShortUsd=oi.get((c.ma, c.sanShort)))
                for c in self.coHoi if c.duyet]

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

            # TỜ TRÌNH — cùng những cơ hội ấy, viết bằng ngôn ngữ chung của
            # Thị Bạc Ty. `coHoi` là ngôn ngữ NỘI BỘ của ty (có `soMocLong`,
            # `intervalShortGio` — ty Tín Dụng không hiểu và không cần hiểu);
            # `toTrinh` là thứ trung ương đọc được.
            #
            # Chỉ trình cơ hội đã QUA cổng ty. Cổng ty là tầng rủi ro thứ
            # nhất; trình cả thứ chính mình đã chặn là đẩy việc sang trung
            # ương và làm loãng sổ đăng ký.
            "toTrinh": [t.tom_tat() for t in self.to_trinh()],
            "soDuyet": len(duyet),
            "viSaoTuChoi": vi_sao,
            "so": self.so.thong_ke(),
            "bang": may_ghi.tom_tat(),
            "doDai": [
                {**self.so.do_dai(c.ma, c.sanLong, c.sanShort),
                 "ma": c.ma, "sanLong": c.sanLong, "sanShort": c.sanShort}
                for c in self.coHoi[:12]
            ],
            # THỊ BẠC TY — bộ máy đứng trên ty này. Cả chín tầng trong một
            # khối, để buồng lái không phải ghép từ nhiều đường API.
            "trungUong": (self.trungUong.anh_chup()
                          if self.trungUong is not None else
                          {"tat": True,
                           "loiNhac": "Trung Ương đang TẮT — ty vẫn quét và "
                                      "vẫn trình, nhưng không tầng nào cấp "
                                      "vốn. Bật ở CONFIG['trungUong']['bat']."}),
            "duongSo": str(DATA_DIR),
            "nhatKy": bus.gan_day(80),
        }


runtime = Runtime()
