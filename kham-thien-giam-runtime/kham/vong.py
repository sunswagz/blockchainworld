"""Vòng lặp chính — và ba làn tốc độ.

Đây là chỗ quyết định kiến trúc quan trọng nhất của runtime, và là câu trả
lời cho "Claude nằm ở đâu":

    LÀN NHANH        0-1000 ms       KHÔNG có Claude
      giá Binance, sổ lệnh WebSocket, đồng hồ chợ, tồn kho, độ trễ
      -> toán thuần Python, quyết định trong vài mili-giây

    LÀN VỪA          1-60 giây       KHÔNG có Claude
      biến động thực nghiệm, đồ thị chợ, hiệu chỉnh lại fair value

    LÀN CHẬM         phút - giờ      CÓ Claude
      hậu kiểm, đọc lại băng, đề xuất giả thuyết, sinh chiến thuật mới

Nghiên cứu OpenMarket đo Polymarket phản ứng sau Binance với trung vị khoảng
347 ms. Một lượt gọi model không về kịp trong cửa sổ đó, và có kịp cũng
không nên: đường quyết định phải TẤT ĐỊNH thì mới chạy lại được, mà chạy lại
được mới biết một thay đổi là tốt hơn hay chỉ khác đi.

## Vòng đời khung — đọc `khung.py` trước khi sửa chỗ này

Bot làm việc trong CỬA ĐẶT CƯỢC `[eventStart − 300, eventStart]`, không phải
trong cửa quan sát. Bản đầu nhắm sai cửa và chỉ nhìn thấy thang chờ. Mọi
lựa chọn khung ở đây đi qua `khung.chon_dat_cuoc()`, không tự tính lại.
"""
from __future__ import annotations

import threading
import time

from .bang import may_ghi
from .bus import bus
from .can_loi import CoHoi, can
from .cap_token import CapSo
from .chan_rui_ro import quyet as quyet_chan
from .chien_thuat import BoiCanh, SO_DANG_KY, chay_tat_ca
from .config import CONFIG, che_hieu_luc
from .dat_lenh import CongLenh
from dataclasses import replace

from . import dong_co, nan_lai
from .ket_qua import so_ket_qua
from .dinh_gia import DoBienDong, HieuChinh
from .do_thi import Nut, do_thi, nhom_cua
from .do_tre import DoTre
from .dong_song import dong_song
from .dong_song_nen import dongSongNen
from .dongho import dong_ho
from .ket_toan import KetToan
from .kho_doi import Kho
from .khung import DAT_CUOC, Khung, chon_dat_cuoc, phan_giai, phan_giai_dai
from .nguon import nguon
from .rui_ro import RiskEngine, SucKhoeNguon
from .so import So, thong_ke
from .so_lenh import SoLenh
from .tien_hoa import doc_so as doc_so_tien_hoa
from .tien_hoa import duong_tien_hoa
from .tien_hoa import mot_luot as tien_hoa_mot_luot
from .vi import dai_quan_vi
from .vo_dich import so_vo_dich

#: Một lượt tiến hoá chết thì chờ bấy nhiêu giây rồi thử lại...
TIEN_HOA_THU_LAI_GIAY = 900.0
#: ...tối đa bấy nhiêu lượt một ngày. Có trần vì một lỗi CỐ ĐỊNH (băng hỏng,
#: thiếu quyền ghi) sẽ hỏng lại y như thế ở lượt sau; không trần thì thành
#: một vòng gọi lại theo nhịp vòng lặp, và nhật ký ngập đúng một dòng lỗi.
TIEN_HOA_TOI_DA_THU = 4


class Runtime:
    def __init__(self) -> None:
        self.kho = Kho()
        self.risk = RiskEngine(self.kho)
        self.cong = CongLenh(self.kho)
        self.hieuChinh = HieuChinh()
        self.so = So()
        self.ketToan = KetToan(self.kho, self.hieuChinh, self.so, self.risk)
        self.doTre = DoTre(dongSongNen, dong_song)
        self.phepNan = nan_lai.khop(self.hieuChinh)
        self._nanLucMs = 0.0

        self.bienDong: dict[str, DoBienDong] = {}
        self.khungHienTai: dict[str, Khung] = {}
        self.capSo: dict[str, CapSo] = {}
        self.giaChuan: dict[str, object] = {}
        self.giaNen: dict[str, float] = {}
        self.coHoi: list[CoHoi] = []
        self.quyetChan: dict[str, dict] = {}
        self.boQua: dict[str, str] = {}

        self._thanPhien: dict[str, str] = {}
        self.batTat = {ct.ma: True for ct in SO_DANG_KY}
        self.tamDung = False
        self.vong = 0
        self.batDauLuc = time.time()
        self._chay = False
        self._luong: threading.Thread | None = None
        self._lanHieuChinhDongHo = 0.0
        self._lanTimKhung = 0.0
        self._lanVoDich = 0.0
        self._ngayTienHoa = ""      # ngày đã XÉT vòng tiến hoá gần nhất
        self.tienHoaGanNhat: dict | None = None
        self._tienHoaXong = False           # lượt hôm nay đã chạy TRỌN chưa
        self._tienHoaDangChay = False
        self._tienHoaSoLanThu = 0
        self._tienHoaThuLai = 0.0           # mốc epoch, sớm nhất được thử lại
        self.tienHoaLoi: str | None = None

    # ── điều khiển ────────────────────────────────────────────────────────
    def bat(self) -> None:
        if self._chay:
            return
        self._chay = True
        # Dòng nền phải bật CÙNG dòng sổ. Đo độ trễ giữa hai sàn mà một
        # bên lấy bằng WebSocket còn bên kia hỏi vòng 2 giây thì thứ đo
        # được là nhịp hỏi của chính mình, không phải độ trễ của chợ.
        for tt in CONFIG["thiTruong"]:
            if tt.get("theo") and tt.get("nen"):
                dongSongNen.dang_ky(tt["nen"])
        dong_song.bat()
        dongSongNen.bat()
        self.doTre.bat()
        self._luong = threading.Thread(target=self._vong_lap, daemon=True)
        self._luong.start()
        bus.ghi(f"runtime khởi động — chế độ {che_hieu_luc()}", loai="he")

    def dung(self) -> None:
        self._chay = False
        dong_song.dung()
        dongSongNen.dung()
        self.doTre.dung()
        may_ghi.dong()
        nguon.dong()
        bus.ghi("runtime dừng", loai="he")

    # ── vòng lặp ──────────────────────────────────────────────────────────
    def _vong_lap(self) -> None:
        nhip = float(CONFIG["loopSeconds"])
        while self._chay:
            t0 = time.time()
            try:
                if not self.tamDung:
                    self._mot_vong()
            except Exception as e:                  # noqa: BLE001
                bus.ghi(f"vòng {self.vong} lỗi: {type(e).__name__}: {e}", loai="loi")
            con = nhip - (time.time() - t0)
            if con > 0:
                time.sleep(con)

    def _mot_vong(self) -> None:
        self.vong += 1
        now = time.time() * 1000.0

        # ── hiệu chỉnh đồng hồ, mỗi 60 giây ──────────────────────────────
        if now - self._lanHieuChinhDongHo > 60_000:
            moc = nguon.moc_thoi_gian_binance()
            if moc:
                dong_ho.hieu_chinh(*moc)
            self._lanHieuChinhDongHo = now

        # ── tìm khung mới, mỗi 20 giây (khung 5 phút nên không cần dày) ──
        if now - self._lanTimKhung > 20_000:
            self._tim_khung(now)
            self._lanTimKhung = now

        # ── làn nhanh ────────────────────────────────────────────────────
        self.coHoi = []
        khung_ghi: list[dict] = []
        for tt in CONFIG["thiTruong"]:
            if not tt.get("theo"):
                continue
            try:
                self._mot_thi_truong(tt, now, khung_ghi)
            except Exception as e:                  # noqa: BLE001
                bus.ghi(f"{tt['ma']}: {type(e).__name__}: {e}", loai="loi")

        # ── soát lệnh maker chờ + kết toán ───────────────────────────────
        self.cong.soat_cho({m: {"UP": c.up, "DOWN": c.down}
                            for m, c in self.capSo.items()})
        if self.ketToan.soat(now):
            so_vo_dich.cap_nhat(self.so.doc(2000))

        # ── làn chậm ─────────────────────────────────────────────────────
        if dai_quan_vi.den_luot():
            threading.Thread(target=dai_quan_vi.quet, daemon=True).start()
        if now - self._lanVoDich > 600_000:
            so_vo_dich.cap_nhat(self.so.doc(2000))
            self._lanVoDich = now

        # ── LÀN CHẬM NHẤT: vòng tiến hoá, mỗi ngày một lượt ──────────────
        # Chạy TRONG runtime chứ không qua Task Scheduler: dịch vụ đó trên
        # máy này đang tắt và bật lại cần quyền quản trị — đã ghi trong
        # `tu-cam-thanh-runtime/dichvu/cai-dat.ps1`. Runtime vốn sống 24/7
        # nên nó là chỗ đáng tin hơn một bộ lịch có thể không tồn tại.
        self._soat_nan_lai()
        self._soat_tien_hoa()

        may_ghi.ghi({
            "luc": now, "vong": self.vong, "che": che_hieu_luc(),
            "thiTruong": khung_ghi,
            "kho": self.kho.tom_tat(), "risk": self.risk.tom_tat(),
        })

    def _soat_nan_lai(self) -> None:
        """Khớp lại đường nắn mỗi 10 phút.

        Không khớp mỗi vòng: sổ hiệu chỉnh chỉ dày thêm khi có market kết
        toán, tức vài phút một lần, nên khớp mỗi 2 giây là tính lại y hệt
        con số cũ hàng trăm lần. Cũng không khớp một lần rồi thôi: cỗ máy
        này chạy nhiều ngày, và một đường nắn khớp từ 300 mẫu mà dùng mãi
        cho 30.000 mẫu thì chính nó thành thứ lạc hậu nhất trong hệ.
        """
        now = time.time() * 1000.0
        if now - self._nanLucMs < 600_000.0:
            return
        self._nanLucMs = now
        cu = self.phepNan
        self.phepNan = nan_lai.khop(self.hieuChinh)
        m = self.phepNan
        if m.dung_duoc and abs(m.saiSau - cu.saiSau) > 1e-4:
            bus.ghi(f"nắn lại: {m.tongMau} mẫu · sai số "
                    f"{m.saiTruoc*100:.2f} → {m.saiSau*100:.2f} điểm", loai="he")

    def _soat_tien_hoa(self) -> None:
        """Chạy vòng tiến hoá đúng MỘT lượt THÀNH CÔNG mỗi ngày, sau giờ hẹn.

        Mốc theo ngày UTC chứ không theo "đủ 24 giờ kể từ lượt trước": nếu
        runtime bị tắt bật vài lần trong ngày thì cách sau sẽ chạy nhiều
        lượt, và mỗi lượt lại vặn một nút. Tiến hoá phải chậm hơn tốc độ
        một người kịp nhìn — đúng lý do repo đặt nhịp 24 giờ cho vòng tiến
        hoá giao diện.

        **Một lượt CHẾT không được tính là đã chạy.** Bản đầu đặt
        `self._ngayTienHoa = ngay` ngay trước khi phóng luồng, nên một lượt
        ném ra lỗi vẫn tiêu mất suất của cả ngày. Đã xảy ra thật 21/08/2026:
        băng hỏng làm `doc_bang()` ném `zlib.error` ở dòng đầu của
        `tien_hoa.mot_luot()`, và từ đó buồng lái hiện `ngayDaChay` của hôm
        nay với `ganNhat: null` — đọc y hệt "hôm nay chưa tới lượt", trong khi
        sự thật là "đã chạy và đã chết". Vòng tự tiến hoá đứng hẳn.

        Nên nay tách hai chuyện: `_ngayTienHoa` là ngày đã XÉT (để đặt lại bộ
        đếm), `_tienHoaXong` mới là đã chạy trọn. Chết thì lùi lại `THU_LAI_GIAY`
        rồi thử tiếp, tối đa `TOI_DA_THU` lượt một ngày — có trần để một lỗi
        cố định không thành vòng lặp gọi lại mỗi 2 giây.
        """
        th = CONFIG.get("tienHoa") or {}
        if not th.get("bat", True):
            return
        gio = time.gmtime()
        ngay = time.strftime("%Y-%m-%d", gio)
        if ngay != self._ngayTienHoa:
            self._ngayTienHoa = ngay
            self._tienHoaXong = False
            self._tienHoaSoLanThu = 0
            self._tienHoaThuLai = 0.0
            self.tienHoaLoi = None
        if self._tienHoaXong or self._tienHoaDangChay:
            return
        if gio.tm_hour < int(th.get("gioUTC", 2)):
            return
        if self._tienHoaSoLanThu >= TIEN_HOA_TOI_DA_THU:
            return
        if time.time() < self._tienHoaThuLai:
            return
        self._tienHoaSoLanThu += 1
        self._tienHoaDangChay = True
        threading.Thread(target=self._chay_tien_hoa, daemon=True).start()

    def _chay_tien_hoa(self) -> None:
        try:
            kq = tien_hoa_mot_luot()
            self.tienHoaGanNhat = kq.tom_tat()
            self._tienHoaXong = True
            self.tienHoaLoi = None
            bus.ghi(f"vòng tiến hoá: {kq.ghiChu}", loai="he")
        except Exception as e:                      # noqa: BLE001
            self.tienHoaLoi = f"{type(e).__name__}: {e}"
            self._tienHoaThuLai = time.time() + TIEN_HOA_THU_LAI_GIAY
            con = TIEN_HOA_TOI_DA_THU - self._tienHoaSoLanThu
            bus.ghi(
                f"vòng tiến hoá lỗi (lượt {self._tienHoaSoLanThu}"
                f"/{TIEN_HOA_TOI_DA_THU}): {self.tienHoaLoi} — "
                + (f"thử lại sau {TIEN_HOA_THU_LAI_GIAY / 60:.0f} phút"
                   if con > 0 else "HẾT lượt thử hôm nay"),
                loai="loi")
        finally:
            self._tienHoaDangChay = False

    # ── tìm và đăng ký khung ──────────────────────────────────────────────
    def _tim_khung(self, now: float) -> None:
        for tt in CONFIG["thiTruong"]:
            if not tt.get("theo"):
                continue
            ma = tt["ma"]
            hs = dong_co.lay(tt.get("dongCo") or "updown-crypto")
            if hs is not None and hs.hoKhung == "khung-dai":
                self._tim_khung_dai(tt, now)
                continue
            dai = float(tt["phutSong"]) * 60.0
            # Dựng thẳng slug — Gamma chặn cứng 100 kết quả nên quét theo
            # tiền tố có lúc không chạm tới cặp mình cần. Giữ đường quét làm
            # lưới đỡ phòng khi Polymarket đổi quy luật đặt slug.
            ds = nguon.tim_khung_dung_slug(tt["tienTo"], dai)
            if not ds:
                ds = nguon.tim_theo_tien_to(tt["tienTo"])
            ks = [k for k in (phan_giai(m, ma, tt["nen"], dai) for m in ds) if k]
            if not ks:
                self._than_phien(ma, f"không thấy khung nào có tiền tố `{tt['tienTo']}`")
                continue
            k = chon_dat_cuoc(ks, now)
            if k is None:
                gan = min(ks, key=lambda x: abs(x.batDauDatCuocMs - now))
                cho = (gan.batDauDatCuocMs - now) / 1000.0
                self._than_phien(ma, f"{len(ks)} khung nhưng chưa khung nào trong "
                                     f"cửa đặt cược; cửa gần nhất mở sau {cho:.0f}s")
                continue

            cu = self.khungHienTai.get(ma)
            if cu is None or cu.slug != k.slug:
                if cu is not None:
                    dong_song.bo_dang_ky(cu.tokenUp)
                    dong_song.bo_dang_ky(cu.tokenDown)
                dong_song.dang_ky(k.tokenUp, ma, "UP")
                dong_song.dang_ky(k.tokenDown, ma, "DOWN")
                # Thước đo trễ bám token UP: nền tăng thì P(UP) phải tăng,
                # nên hướng hàm ý đọc thẳng được, không cần quy đổi.
                nenMa = next((t.get("nen") for t in CONFIG["thiTruong"]
                              if t.get("ma") == ma), None)
                if nenMa:
                    self.doTre.lien_ket(ma, nenMa, k.tokenUp)
                self.khungHienTai[ma] = k
                bus.ghi(f"{ma}: vào cửa đặt cược {k.slug} "
                        f"(còn {k.con_lai_giay(now):.0f}s)", loai="tin")

    def _tim_khung_dai(self, tt: dict, now: float) -> None:
        """Họ khung DÀI: một market sống hàng tháng, slug khai thẳng.

        Không dựng slug từ mốc thời gian như họ Lên/Xuống — ở đây không có
        gì để dựng, market là một và cố định. Cũng không quét theo tiền tố:
        Gamma chặn cứng 100 kết quả, và một market lẻ nằm giữa hàng nghìn
        market khác thì không có lý do gì lọt vào 100 cái đầu.
        """
        ma = tt["ma"]
        slug = tt.get("slug")
        if not slug:
            self._than_phien(ma, "họ khung dài phải khai `slug` trong config")
            return
        if self.khungHienTai.get(ma) is not None:
            return                      # market sống hàng tháng, hỏi lại làm gì
        m = nguon.tim_theo_slug(slug)
        if not m:
            self._than_phien(ma, f"không thấy market `{slug}`")
            return
        k = phan_giai_dai(m, ma, tt["nen"])
        if k is None:
            self._than_phien(ma, f"market `{slug}` thiếu mốc thời gian hoặc token")
            return
        dong_song.dang_ky(k.tokenUp, ma, "UP")
        dong_song.dang_ky(k.tokenDown, ma, "DOWN")
        self.khungHienTai[ma] = k
        bus.ghi(f"{ma}: theo khung dài {k.slug} "
                f"(còn {k.con_lai_giay(now)/86400:.0f} ngày)", loai="tin")

    # ── một thị trường, một vòng ──────────────────────────────────────────
    def _mot_thi_truong(self, tt: dict, now: float, ghi: list[dict]) -> None:
        ma = tt["ma"]
        k = self.khungHienTai.get(ma)
        if k is None:
            return
        if k.giai_doan(now) != DAT_CUOC:
            return          # ra khỏi cửa rồi; `_tim_khung` sẽ đổi khung

        # 1. giá nền + biến động
        gia = nguon.gia_binance(tt["nen"])
        if gia is None:
            return
        self.giaNen[ma] = gia
        bd = self.bienDong.setdefault(ma, DoBienDong())
        bd.them(gia, now)
        sigma = bd.sigma_giay()
        if sigma is None:
            self._than_phien(ma, f"chưa đủ mẫu ước lượng σ ({bd.so_mau}/12)")
            return

        # 2. sổ lệnh — WebSocket trước, REST là lưới đỡ
        su = dong_song.lay(k.tokenUp) or nguon.so_lenh(ma, "UP", k.tokenUp)
        sd = dong_song.lay(k.tokenDown) or nguon.so_lenh(ma, "DOWN", k.tokenDown)
        if su is None or sd is None:
            self._than_phien(ma, "chưa nhận được sổ lệnh")
            return
        cap = CapSo(ma, su, sd)
        self.capSo[ma] = cap
        if not cap.dung_duoc:
            self._than_phien(ma, cap.ly_do_khong_dung() or "sổ không dùng được")
            return

        # 3. strike + định giá
        mo = nguon.gia_mo_khung(tt["nen"], k.batDauDatCuocMs)
        if not mo:
            self._than_phien(ma, "không lấy được giá mở cửa đặt cược (strike)")
            return
        tau = k.con_lai_giay(now)
        # Qua SỔ ĐĂNG KÝ chứ không gọi thẳng `dinh_gia`. Đây là mối nối
        # duy nhất trong cả hệ biết "market này thuộc họ nào" — mọi thứ
        # phía sau (sổ lệnh, cân lợi, kho, rủi ro, kết toán) không quan
        # tâm. Thêm một họ market là khai thêm một động cơ, không phải
        # dựng một bot khác.
        maDC = tt.get("dongCo") or "updown-crypto"
        hs = dong_co.lay(maDC)
        if hs is not None and hs.hoKhung == "khung-dai":
            # Họ chạm mốc cần thứ họ Lên/Xuống không cần: ĐỈNH ĐÃ ĐI QUA.
            # Chỉ nhìn giá hiện tại thì một market đã ngã ngũ từ tháng
            # trước vẫn ra một xác suất nhỏ xinh.
            dinh = nguon.dinh_da_qua(tt["nen"], k.batDauDatCuocMs,
                                     bool(tt.get("lenTren", True)))
            if dinh is None:
                self._than_phien(ma, "không lấy được đỉnh đã đi qua — "
                                     "động cơ chạm mốc từ chối đoán khi thiếu")
                return
            gc, viSao = dong_co.goi(
                maDC, ma, giaHienTai=gia, moc=float(tt["moc"]), tauGiay=tau,
                dinhDaQua=dinh, sigmaGiay=sigma,
                lenTren=bool(tt.get("lenTren", True)))
        else:
            gc, viSao = dong_co.goi(
                maDC, ma, giaHienTai=gia, giaMo=mo, tauGiay=tau,
                sigmaGiay=sigma, tinHieu=self._tin_hieu(su))
        # NẮN LẠI trước khi ai dùng con số này. Sổ hiệu chỉnh đo được mô
        # hình bị nén về 50%; không nắn thì lợi thế thô tự teo lại đúng ở
        # những lần mô hình tự tin nhất.
        if gc is not None and self.phepNan.dung_duoc:
            pNan = self.phepNan.nan(gc.pUp)
            if abs(pNan - gc.pUp) > 1e-9:
                gt = dict(gc.giaiTrinh or {})
                gt["pTruocNan"] = gc.pUp
                gt["nanLai"] = {"saiTruoc": self.phepNan.saiTruoc,
                                "saiSau": self.phepNan.saiSau,
                                "tongMau": self.phepNan.tongMau}
                gc = replace(gc, pUp=pNan, pDown=1.0 - pNan, giaiTrinh=gt)
        if gc is None:
            # "Không định giá được" có nhiều lý do rất khác nhau. Khai sai
            # tên động cơ mà lặng lẽ bỏ qua thì market biến mất khỏi bảng
            # và không ai biết vì sao.
            if viSao and "từ chối" not in viSao:
                self._than_phien(ma, f"động cơ '{maDC}': {viSao}")
            return
        self.giaChuan[ma] = gc
        self.boQua.pop(ma, None)
        self._thanPhien.pop(ma, None)

        # 4. ghi danh kết toán — CẢ khi không vào lệnh, xem ket_toan.ghi_danh
        self.ketToan.ghi_danh(ma, k.slug, k.endMs, mo, tt["nen"],
                              k.tokenUp, k.tokenDown, pUp=gc.pUp)

        # 5. đồ thị chợ
        do_thi.dat(Nut(ma=ma, slug=k.slug, nhom=nhom_cua(ma), conLaiGiay=tau,
                       fairUp=gc.pUp, giaChoUp=cap.gia_mua("UP"),
                       batDinh=gc.batDinh))

        # 6. chân lệch — quyết TRƯỚC khi mở thêm
        v = self.kho.lay(ma)
        qc = quyet_chan(v, cap, tau, now)
        self.quyetChan[ma] = (
            {"loi": qc.loi, "nhan": qc.nhan, "ben": qc.ben, "soCo": qc.soCo,
             "khoaLoUsd": qc.khoaLoUsd, "lyDo": qc.lyDo} if qc else {})

        # 7. chiến thuật đề xuất
        lc = dong_ho.lat_cat(k.eventStartMs, k.daiSongGiay,
                             tuoiDuLieuMs=now - su.nhanLucMs)
        bc = BoiCanh(ma=ma, gia=gc, soUp=su, soDown=sd, dongHo=lc, viThe=v)
        de_xuat = chay_tat_ca(bc, self.batTat)

        # 8. Risk Engine quyết
        suc_khoe = SucKhoeNguon(
            tuoiSoLenhMs=now - su.nhanLucMs, tuoiGiaNenMs=0.0,
            lechDongHoMs=dong_ho.lech_ms,
            thieuNguon=[t.ten for t in nguon.trangThai.values() if t.soLoi >= 3],
        )
        du_kelly = self.hieuChinh.du_de_dung_kelly()
        for ch in de_xuat:
            pq = self.risk.duyet(ch, suc_khoe, tau, du_kelly)
            self.coHoi.append(ch)
            if pq.cho and pq.soCoChoPhep >= 1:
                self.cong.dat(ch, pq.soCoChoPhep, su if ch.ben == "UP" else sd)

        # 9. băng ghi — đủ để CHẠY LẠI, không chỉ để nhìn
        ghi.append({
            "ma": ma, "slug": k.slug, "giaNen": gia, "giaMo": mo,
            "sigmaGiay": sigma, "conLaiGiay": tau,
            "pUp": gc.pUp, "batDinh": gc.batDinh,
            "so": {
                "UP": {"luc": su.nhanLucMs,
                       "bid": [{"gia": m.gia, "luong": m.luong} for m in su.bid[:30]],
                       "ask": [{"gia": m.gia, "luong": m.luong} for m in su.ask[:30]]},
                "DOWN": {"luc": sd.nhanLucMs,
                         "bid": [{"gia": m.gia, "luong": m.luong} for m in sd.bid[:30]],
                         "ask": [{"gia": m.gia, "luong": m.luong} for m in sd.ask[:30]]},
            },
        })

    def _than_phien(self, ma: str, ly_do: str) -> None:
        """Ghi lý do bỏ qua — nhưng chỉ khi lý do ĐỔI.

        Nhịp 2 giây mà ghi mỗi vòng thì một lý do đẻ 1.800 dòng mỗi giờ và
        đẩy mọi thứ khác ra khỏi sổ.
        """
        if self._thanPhien.get(ma) == ly_do:
            return
        self._thanPhien[ma] = ly_do
        self.boQua[ma] = ly_do
        bus.ghi(f"{ma}: {ly_do}", loai="canh")

    @staticmethod
    def _tin_hieu(so: SoLenh) -> dict[str, float]:
        th: dict[str, float] = {}
        l = so.lech()
        if l is not None:
            th["poly_lech"] = l * 0.4
        vg, giua = so.vi_gia, so.giua
        if vg is not None and giua is not None:
            th["poly_vi_gia"] = (vg - giua) * 4.0
        return th

    # ── báo cáo ───────────────────────────────────────────────────────────
    def anh_chup(self) -> dict:
        now = time.time() * 1000.0
        ket = self.so.doc(500)
        return {
            "vong": self.vong, "batDauLuc": self.batDauLuc,
            "chayDuocGiay": time.time() - self.batDauLuc,
            "tamDung": self.tamDung,
            "che": che_hieu_luc(), "cheKhai": CONFIG.get("che"),
            "risk": self.risk.tom_tat(), "kho": self.kho.tom_tat(),
            "lenh": self.cong.tom_tat(), "nguon": nguon.tom_tat(),
            "dongSong": dong_song.tom_tat(),
            "dongNen": dongSongNen.tom_tat(),
            "doTre": self.doTre.tom_tat(),
            "nanLai": self.phepNan.tom_tat(),
            "duongRa": nguon.duong_ra(),
            "soKetQua": so_ket_qua.tom_tat(),
            "ketToan": self.ketToan.tom_tat(),
            "doThi": do_thi.tom_tat(),
            "voDich": so_vo_dich.tom_tat(),
            "tienHoa": {
                "ganNhat": self.tienHoaGanNhat,
                "duong": duong_tien_hoa(),
                # `ngayDaXet` chứ không phải `ngayDaChay`: có ngày ở đây mà
                # `xong` vẫn false nghĩa là ĐÃ THỬ và ĐÃ CHẾT, không phải
                # "chưa tới lượt". Hai chuyện đó trước đây không phân biệt
                # được từ ngoài, nên một vòng tiến hoá chết trông y hệt một
                # vòng chưa chạy.
                "ngayDaXet": self._ngayTienHoa,
                "ngayDaChay": self._ngayTienHoa if self._tienHoaXong else "",
                "xong": self._tienHoaXong,
                "dangChay": self._tienHoaDangChay,
                "loi": self.tienHoaLoi,
                "soLanThu": self._tienHoaSoLanThu,
                "toiDaThu": TIEN_HOA_TOI_DA_THU,
                "thuLaiSauGiay": (max(0.0, self._tienHoaThuLai - time.time())
                                  if self.tienHoaLoi and not self._tienHoaXong
                                  else None),
                "bat": bool((CONFIG.get("tienHoa") or {}).get("bat", True)),
                "gioUTC": int((CONFIG.get("tienHoa") or {}).get("gioUTC", 2)),
            },
            "quyetChan": dict(self.quyetChan),
            "hieuChinh": {
                "bang": self.hieuChinh.bang(),
                "tongMau": self.hieuChinh.tong_mau,
                "duDeDungKelly": self.hieuChinh.du_de_dung_kelly(),
                "saiSoTB": self.hieuChinh.sai_so_tuyet_doi_tb(),
            },
            "thongKe": thong_ke(ket),
            "vi": dai_quan_vi.tom_tat(),
            "dongCo": dong_co.tom_tat(),
            "chienThuat": [
                {"ma": c.ma, "ten": c.ten, "mota": c.mota,
                 "bat": self.batTat.get(c.ma, True)} for c in SO_DANG_KY],
            "thiTruong": [
                {
                    "ma": t["ma"], "theo": bool(t.get("theo")),
                    "dongCo": t.get("dongCo") or "updown-crypto",
                    "khung": (self.khungHienTai[t["ma"]].tom_tat(now)
                              if t["ma"] in self.khungHienTai else None),
                    "gia": _tom_gia(self.giaChuan.get(t["ma"])),
                    "giaNen": self.giaNen.get(t["ma"]),
                    "cap": (self.capSo[t["ma"]].tom_tat()
                            if t["ma"] in self.capSo else None),
                    "so": _tom_so(self.capSo.get(t["ma"])),
                } for t in CONFIG["thiTruong"]],
            "coHoi": [
                {"ma": c.ma, "ben": c.ben, "ct": c.chienThuat,
                 "fair": c.fairValue, "vwap": c.vwap, "gross": c.grossEdge,
                 "net": c.netEdge, "phi": c.phi, "batDinh": c.batDinhMoHinh,
                 "sucChua": c.sucChua, "xacSuatKhop": c.xacSuatKhop,
                 "nuaDoiMs": c.nuaDoiMs, "maker": c.laMaker,
                 "dangLam": c.dang_lam, "ghiChu": c.ghiChu}
                for c in self.coHoi[:40]],
            "boQua": dict(self.boQua),
            "bang": may_ghi.tom_tat(),
            "nhatKy": bus.gan_day(80),
        }


def _tom_gia(g) -> dict | None:
    if g is None:
        return None
    return {"pUp": g.pUp, "pDown": g.pDown, "batDinh": g.batDinh,
            "batDinhThamSo": g.batDinhThamSo, "ruiRoNhay": g.ruiRoNhay,
            "z": g.z, "sigmaGiay": g.sigmaGiay, "tauGiay": g.tauGiay,
            "tauDungSan": g.tauDungSan, "daMatPhang": g.daMatPhang,
            "roRang": g.ro_rang, "giaHienTai": g.giaHienTai, "giaMo": g.giaMo,
            "oHieuChinh": g.oHieuChinh, "giaiTrinh": g.giaiTrinh}


def _tom_so(cap: CapSo | None) -> dict | None:
    if cap is None:
        return None
    ra = {}
    for ben, s in (("UP", cap.up), ("DOWN", cap.down)):
        ra[ben] = {
            "bestBid": s.best_bid, "bestAsk": s.best_ask, "spread": s.spread,
            "viGia": s.vi_gia, "lech": s.lech(), "doSau": s.do_sau(),
            "thangCho": s.trai_ca_bang, "dungDuoc": s.dung_duoc,
            "bid": [{"gia": m.gia, "luong": m.luong} for m in s.bid[:12]],
            "ask": [{"gia": m.gia, "luong": m.luong} for m in s.ask[:12]],
        }
    return ra


runtime = Runtime()
