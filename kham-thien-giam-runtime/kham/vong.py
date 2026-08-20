"""Vòng lặp chính — và ba làn tốc độ.

Đây là chỗ quyết định kiến trúc quan trọng nhất của cả runtime, và nó là câu
trả lời cho "Claude nằm ở đâu":

    LÀN NHANH        0-1000 ms       KHÔNG có Claude
      giá Binance, sổ lệnh Polymarket, đồng hồ chợ, tồn kho, độ trễ
      -> toán thuần Python, quyết định trong vài mili-giây

    LÀN VỪA          1-60 giây       KHÔNG có Claude
      biến động thực nghiệm, quan hệ chéo market, hiệu chỉnh lại fair value

    LÀN CHẬM         phút - giờ      CÓ Claude
      hậu kiểm, đọc lại băng, đề xuất giả thuyết, sinh chiến thuật mới

Nghiên cứu OpenMarket đo được Polymarket phản ứng sau Binance với trung vị
khoảng 347 ms. Một lượt gọi model không bao giờ về kịp trong cửa sổ đó, và có
kịp cũng không nên: đường quyết định phải TẤT ĐỊNH thì mới chạy lại được, mà
chạy lại được mới biết một thay đổi là tốt hơn hay chỉ khác đi.

Nên Claude ở đây là NHÀ KHOA HỌC của cỗ máy, không phải phản xạ của nó. Runtime
này chạy kín vòng và đầy đủ mà không cần một lượt gọi model nào.
"""
from __future__ import annotations

import datetime as dt
import json
import threading
import time

from .bang import may_ghi
from .bus import bus
from .can_loi import CoHoi
from .chien_thuat import BoiCanh, SO_DANG_KY, chay_tat_ca
from .config import CONFIG, che_hieu_luc
from .dat_lenh import CongLenh
from .dinh_gia import DoBienDong, HieuChinh, dinh_gia
from .dongho import dong_ho
from .kho_doi import Kho
from .nguon import nguon
from .rui_ro import RiskEngine, SucKhoeNguon
from .so import So, thong_ke
from .so_lenh import SoLenh
from .vi import dai_quan_vi


class Runtime:
    def __init__(self) -> None:
        self.kho = Kho()
        self.risk = RiskEngine(self.kho)
        self.cong = CongLenh(self.kho)
        self.hieuChinh = HieuChinh()
        self.so = So()

        self.bienDong: dict[str, DoBienDong] = {}
        self.soLenh: dict[str, dict[str, SoLenh]] = {}
        self.giaChuan: dict[str, object] = {}
        self.coHoi: list[CoHoi] = []
        self.thiTruong: list[dict] = []

        self.boQua: dict[str, str] = {}
        self._thanPhien: dict[str, str] = {}
        self.batTat = {ct.ma: True for ct in SO_DANG_KY}
        self.tamDung = False
        self.vong = 0
        self.batDauLuc = time.time()
        self._chay = False
        self._luong: threading.Thread | None = None
        self._lanHieuChinhDongHo = 0.0
        self._lanQuetChoMs = 0.0

    # ── điều khiển ────────────────────────────────────────────────────────
    def bat(self) -> None:
        if self._chay:
            return
        self._chay = True
        self._luong = threading.Thread(target=self._vong_lap, daemon=True)
        self._luong.start()
        bus.ghi(f"runtime khởi động — chế độ {che_hieu_luc()}", loai="he")

    def dung(self) -> None:
        self._chay = False
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
                # Một vòng hỏng KHÔNG được giết runtime. Nhưng cũng không
                # được nuốt im lặng — nó phải hiện lên buồng lái.
                bus.ghi(f"vòng {self.vong} lỗi: {type(e).__name__}: {e}", loai="loi")
            con = nhip - (time.time() - t0)
            if con > 0:
                time.sleep(con)

    def _mot_vong(self) -> None:
        self.vong += 1
        bay_gio_ms = time.time() * 1000.0

        # ── hiệu chỉnh đồng hồ, mỗi 60 giây ──────────────────────────────
        if bay_gio_ms - self._lanHieuChinhDongHo > 60_000:
            moc = nguon.moc_thoi_gian_binance()
            if moc:
                dong_ho.hieu_chinh(*moc)
            self._lanHieuChinhDongHo = bay_gio_ms

        # ── làn nhanh ────────────────────────────────────────────────────
        self.coHoi = []
        khung_coHoi: list[dict] = []

        for tt in CONFIG["thiTruong"]:
            if not tt.get("theo"):
                continue
            ma = tt["ma"]
            try:
                self._mot_thi_truong(tt, bay_gio_ms, khung_coHoi)
            except Exception as e:                  # noqa: BLE001
                bus.ghi(f"{ma}: {type(e).__name__}: {e}", loai="loi")

        # ── soát lệnh maker đang chờ ─────────────────────────────────────
        self.cong.soat_cho(self.soLenh)

        # ── làn chậm: quét ví, thưa hơn nhiều ────────────────────────────
        if dai_quan_vi.den_luot():
            threading.Thread(target=dai_quan_vi.quet, daemon=True).start()

        # ── ghi băng ─────────────────────────────────────────────────────
        may_ghi.ghi({
            "luc": bay_gio_ms, "vong": self.vong,
            "che": che_hieu_luc(),
            "coHoi": khung_coHoi,
            "kho": self.kho.tom_tat(),
            "risk": self.risk.tom_tat(),
        })

    def _mot_thi_truong(self, tt: dict, bayGioMs: float,
                        khungCoHoi: list[dict]) -> None:
        ma = tt["ma"]

        # 1. giá nền
        gia = nguon.gia_binance(tt["nen"])
        if gia is None:
            return
        bd = self.bienDong.setdefault(ma, DoBienDong())
        bd.them(gia, bayGioMs)
        sigma = bd.sigma_giay()
        if sigma is None:
            return                                   # chưa đủ mẫu, đừng đoán

        # 2. market đang sống + sổ lệnh
        ct = self._market_dang_song(tt)
        if not ct:
            return
        so_up = ct.get("soUp")
        so_down = ct.get("soDown")
        if so_up is None or so_down is None:
            return
        self.soLenh[ma] = {"UP": so_up, "DOWN": so_down}
        self.boQua.pop(ma, None)
        self._thanPhien.pop(ma, None)

        # 3. đồng hồ
        lc = dong_ho.lat_cat(ct["ketThucMs"], ct["tongGiay"],
                             tuoiDuLieuMs=bayGioMs - so_up.nhanLucMs)
        if lc.da_khoa:
            return

        # 4. fair value
        tin_hieu = self._tin_hieu(ma, so_up, so_down)
        gc = dinh_gia(ma, gia, ct["giaMo"], lc.conLaiGiay, sigma, tin_hieu)
        if gc is None:
            return
        self.giaChuan[ma] = gc

        # 5. chiến thuật đề xuất
        bc = BoiCanh(ma=ma, gia=gc, soUp=so_up, soDown=so_down, dongHo=lc,
                     viThe=self.kho.lay(ma))
        de_xuat = chay_tat_ca(bc, self.batTat)

        # 6. Risk Engine quyết
        suc_khoe = SucKhoeNguon(
            tuoiSoLenhMs=bayGioMs - so_up.nhanLucMs,
            tuoiGiaNenMs=0.0,
            lechDongHoMs=dong_ho.lech_ms,
            thieuNguon=[t.ten for t in nguon.trangThai.values() if t.soLoi >= 3],
        )
        du_kelly = self.hieuChinh.du_de_dung_kelly()

        for ch in de_xuat:
            pq = self.risk.duyet(ch, suc_khoe, lc.conLaiGiay, du_kelly)
            khungCoHoi.append({
                "ma": ch.ma, "ben": ch.ben, "ct": ch.chienThuat,
                "fair": ch.fairValue, "vwap": ch.vwap, "netEdge": ch.netEdge,
                "sucChua": ch.sucChua, "cho": pq.cho,
                "lyDo": pq.lyDo, "siet": pq.canhBao,
            })
            self.coHoi.append(ch)
            if pq.cho and pq.soCoChoPhep >= 1:
                so = so_up if ch.ben == "UP" else so_down
                self.cong.dat(ch, pq.soCoChoPhep, so)

    def _market_dang_song(self, tt: dict) -> dict | None:
        """Tìm khung ĐANG SỐNG của một market, kèm sổ lệnh hai bên.

        Bản này gọi Gamma mỗi vòng. Với nhịp 2 giây và vài market thì chấp
        nhận được, nhưng đúng ra phải là WebSocket đăng ký một lần — đó là
        việc của P1, ghi ở đây để không ai tưởng chỗ này đã xong.
        """
        ma = tt["ma"]
        ds = nguon.tim_theo_tien_to(tt["tienTo"])
        if not ds:
            self._than_phien(ma, f"không thấy market nào có tiền tố "
                                 f"`{tt['tienTo']}` đang mở")
            return None

        tong_giay = float(tt["phutSong"]) * 60.0
        bay_gio = dong_ho.bay_gio_ms()

        # Chọn khung ĐANG chạy: đã bắt đầu và chưa kết thúc. Lấy bừa `ds[0]`
        # là lấy khung sớm nhất, mà khung sớm nhất thường đã đóng.
        song = None
        gan_nhat = None
        for m in ds:
            ket = _doc_moc(m.get("endDate"))
            if ket is None:
                continue
            gan_nhat = max(gan_nhat or ket, ket)
            if ket - tong_giay * 1000.0 <= bay_gio < ket:
                song = (m, ket)
                break

        if song is None:
            # Không có khung nào phủ thời điểm hiện tại. Nói RÕ vì sao, kèm
            # số đo — đây đúng tình huống đã gặp lúc dựng: đồng hồ máy đi
            # trước dữ liệu sàn tám tháng, nên mọi market thấy được đều đã
            # đóng và mọi lời gọi /book trả 404. Không nói ra thì bảng điều
            # khiển chỉ trống trơn với toàn đèn xanh.
            if gan_nhat is not None:
                lech_gio = (bay_gio - gan_nhat) / 3_600_000.0
                self._than_phien(ma, (
                    f"{len(ds)} khung tìm thấy nhưng không khung nào đang chạy; "
                    f"khung xa nhất kết thúc cách đây {lech_gio:.1f} giờ theo "
                    f"đồng hồ máy — kiểm lại giờ hệ thống"))
            return None

        m, ket = song

        toks = m.get("clobTokenIds") or []
        if isinstance(toks, str):
            try:
                toks = json.loads(toks)
            except json.JSONDecodeError:
                return None
        if len(toks) < 2:
            self._than_phien(ma, "market thiếu clobTokenIds")
            return None

        bat_dau = ket - tong_giay * 1000.0
        gia_mo = m.get("openPrice") or m.get("startPrice")
        try:
            gia_mo = float(gia_mo) if gia_mo else None
        except (TypeError, ValueError):
            gia_mo = None
        if not gia_mo:
            gia_mo = nguon.gia_mo_khung(tt["nen"], bat_dau)
        if not gia_mo:
            self._than_phien(ma, "không lấy được giá mở khung (strike)")
            return None

        return {
            "ketThucMs": ket,
            "batDauMs": bat_dau,
            "tongGiay": tong_giay,
            "giaMo": gia_mo,
            "slug": m.get("slug"),
            "soUp": nguon.so_lenh(ma, "UP", toks[0]),
            "soDown": nguon.so_lenh(ma, "DOWN", toks[1]),
        }

    def _than_phien(self, ma: str, ly_do: str) -> None:
        """Ghi lý do một market bị bỏ qua — nhưng chỉ khi lý do ĐỔI.

        Nhịp 2 giây mà ghi mỗi vòng thì một lý do duy nhất đẻ ra 1.800 dòng
        mỗi giờ và đẩy mọi thứ khác ra khỏi sổ. Ghi một lần rồi im cho tới
        khi tình hình khác đi.
        """
        if getattr(self, "_thanPhien", None) is None:
            self._thanPhien = {}
        if self._thanPhien.get(ma) == ly_do:
            return
        self._thanPhien[ma] = ly_do
        bus.ghi(f"{ma}: {ly_do}", loai="canh")
        self.boQua[ma] = ly_do

    @staticmethod
    def _tin_hieu(ma: str, soUp: SoLenh, soDown: SoLenh) -> dict[str, float]:
        """Tín hiệu vi cấu trúc, đã gắn HỌ ở `dinh_gia.HO_TIN_HIEU`."""
        th: dict[str, float] = {}
        l = soUp.lech()
        if l is not None:
            th["poly_lech"] = l * 0.4
        vg, giua = soUp.vi_gia, soUp.giua
        if vg is not None and giua is not None and giua > 0:
            th["poly_vi_gia"] = (vg - giua) * 4.0
        return th

    # ── báo cáo ───────────────────────────────────────────────────────────
    def anh_chup(self) -> dict:
        ket = self.so.doc(500)
        return {
            "vong": self.vong,
            "batDauLuc": self.batDauLuc,
            "chayDuocGiay": time.time() - self.batDauLuc,
            "tamDung": self.tamDung,
            "che": che_hieu_luc(),
            "cheKhai": CONFIG.get("che"),
            "risk": self.risk.tom_tat(),
            "kho": self.kho.tom_tat(),
            "lenh": self.cong.tom_tat(),
            "nguon": nguon.tom_tat(),
            "hieuChinh": {
                "bang": self.hieuChinh.bang(),
                "tongMau": self.hieuChinh.tong_mau,
                "duDeDungKelly": self.hieuChinh.du_de_dung_kelly(),
                "saiSoTB": self.hieuChinh.sai_so_tuyet_doi_tb(),
            },
            "thongKe": thong_ke(ket),
            "vi": dai_quan_vi.tom_tat(),
            "chienThuat": [
                {"ma": c.ma, "ten": c.ten, "mota": c.mota,
                 "bat": self.batTat.get(c.ma, True)}
                for c in SO_DANG_KY
            ],
            "thiTruong": [
                {
                    "ma": t["ma"], "theo": bool(t.get("theo")),
                    "gia": _tom_gia(self.giaChuan.get(t["ma"])),
                    "so": _tom_so(self.soLenh.get(t["ma"])),
                }
                for t in CONFIG["thiTruong"]
            ],
            "coHoi": [
                {
                    "ma": c.ma, "ben": c.ben, "ct": c.chienThuat,
                    "fair": c.fairValue, "vwap": c.vwap,
                    "gross": c.grossEdge, "net": c.netEdge,
                    "phi": c.phi, "batDinh": c.batDinhMoHinh,
                    "sucChua": c.sucChua, "xacSuatKhop": c.xacSuatKhop,
                    "nuaDoiMs": c.nuaDoiMs, "maker": c.laMaker,
                    "dangLam": c.dang_lam, "ghiChu": c.ghiChu,
                }
                for c in self.coHoi[:40]
            ],
            "boQua": dict(self.boQua),
            "bang": {"soKhung": may_ghi.soKhung, "bat": may_ghi.bat},
            "nhatKy": bus.gan_day(80),
        }


def _doc_moc(iso) -> float | None:
    """ISO 8601 -> mili-giây epoch. None nếu không đọc được."""
    try:
        return dt.datetime.fromisoformat(
            str(iso).replace("Z", "+00:00")).timestamp() * 1000.0
    except (ValueError, TypeError, AttributeError):
        return None


def _tom_gia(g) -> dict | None:
    if g is None:
        return None
    return {
        "pUp": g.pUp, "pDown": g.pDown, "batDinh": g.batDinh,
        "batDinhThamSo": g.batDinhThamSo, "ruiRoNhay": g.ruiRoNhay,
        "z": g.z, "sigmaGiay": g.sigmaGiay, "tauGiay": g.tauGiay,
        "tauDungSan": g.tauDungSan, "daMatPhang": g.daMatPhang,
        "roRang": g.ro_rang, "giaHienTai": g.giaHienTai, "giaMo": g.giaMo,
        "oHieuChinh": g.oHieuChinh, "giaiTrinh": g.giaiTrinh,
    }


def _tom_so(d) -> dict | None:
    if not d:
        return None
    ra = {}
    for ben, s in d.items():
        if s is None:
            continue
        ra[ben] = {
            "bestBid": s.best_bid, "bestAsk": s.best_ask,
            "spread": s.spread, "viGia": s.vi_gia, "lech": s.lech(),
            "doSau": s.do_sau(),
            "bid": [{"gia": m.gia, "luong": m.luong} for m in s.bid[:12]],
            "ask": [{"gia": m.gia, "luong": m.luong} for m in s.ask[:12]],
        }
    return ra


runtime = Runtime()
