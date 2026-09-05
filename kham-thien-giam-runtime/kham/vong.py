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
import datetime as _dt
import time

from .bang import bao_cao_doc_cuoi, may_ghi
from .chan_doan import nut_o_mep
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
from .khung import (DAT_CUOC, QUAN_SAT, Khung, chon_dat_cuoc,
                    chon_quan_sat, phan_giai, phan_giai_dai)
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

        # Dựng lại trạng thái rủi ro TỪ SỔ. Không có dòng này thì mỗi lần
        # khởi động lại là quên sạch vốn, đỉnh vốn và lỗ ngày — nên một
        # bot vừa chạm trần lỗ ngày, bị khởi động lại, có ngay ngân sách
        # lỗ mới nguyên. Xem `RiskEngine.nap_tu_so`.
        try:
            nap = self.risk.nap_tu_so(self.so.doc())
            if nap["soDong"]:
                bus.ghi(
                    f"dựng lại rủi ro từ sổ: {nap['soDong']} lệnh · "
                    f"vốn ${nap['von']:,.2f} · đỉnh ${nap['dinhVon']:,.2f} · "
                    f"ngày ròng ${nap['laiRongNgayUsd']:+,.2f}"
                    + (f" · CẦU DAO NGẮT: {nap['lyDoNgat']}"
                       if nap["ngatKhanCap"] else ""),
                    loai="he")
        except Exception as e:      # noqa: BLE001
            # Không dựng lại được thì phải KÊU, đừng lặng lẽ chạy tiếp với
            # vốn khai sinh — chạy tiếp im lặng chính là cái lỗi đang sửa.
            bus.ghi(f"KHÔNG dựng lại được rủi ro từ sổ: {type(e).__name__}: {e}"
                    " — đang chạy bằng vốn khai sinh, cầu dao ngày đã QUÊN "
                    "mọi khoản lỗ trước đó", loai="loi")
        self.doTre = DoTre(dongSongNen, dong_song)
        self.phepNan = nan_lai.khop(self.hieuChinh)
        self._nanLucMs = 0.0
        #: Ngày UTC đã dọn băng. Rỗng = chưa dọn lần nào phiên này.
        self._ngayDonBang = ""

        self.bienDong: dict[str, DoBienDong] = {}
        self.khungHienTai: dict[str, Khung] = {}
        # Khung ĐANG ăn thua [T, T+300]. Chỉ để ghi băng —
        # chưa ai đo được có tiền trong cửa ấy không.
        self.khungQuanSat: dict[str, Khung] = {}
        self.capSo: dict[str, CapSo] = {}
        self.giaChuan: dict[str, object] = {}
        self.giaNen: dict[str, float] = {}
        self.coHoi: list[CoHoi] = []
        self.quyetChan: dict[str, dict] = {}
        self.boQua: dict[str, str] = {}

        self._thanPhien: dict[str, str] = {}
        self.batTat = {ct.ma: True for ct in SO_DANG_KY}
        self.tamDung = False
        self._nap_dieu_khien()
        self.vong = 0
        self.batDauLuc = time.time()
        self._chay = False
        self._luong: threading.Thread | None = None
        self._lanHieuChinhDongHo = 0.0
        self._lanTimKhung = 0.0
        self._lanVoDich = 0.0
        self._ngayTienHoa = ""      # ngày đã XÉT vòng tiến hoá gần nhất
        # Làn nào ngã trong vòng vừa rồi, và ngã vì gì. Rỗng = trọn vẹn.
        self.lanNga: dict[str, str] = {}
        #: ĐẾM DỒN số lần mỗi làn ngã, không xoá mỗi vòng.
        #:
        #: `lanNga` xoá đầu mỗi vòng — đúng, vì nó trả lời "ngay bây giờ
        #: có gì hỏng không". Nhưng nó mù với kiểu hỏng THỈNH THOẢNG: một
        #: làn ngã 20% số vòng chỉ đỏ 20% số lần nhìn, mà buồng lái hỏi
        #: mỗi 2 giây và người trực thì liếc một cái. Bốn trong năm lần
        #: liếc ấy thấy xanh.
        #:
        #: Hỏng thỉnh thoảng là kiểu khó thấy nhất và cũng đắt nhất —
        #: nó không giết cỗ máy, nó chỉ lặng lẽ ăn mất một phần công
        #: việc. Con số cộng dồn làm nó hiện ra.
        self.lanNgaTong: dict[str, int] = {}
        # Lượt học/tiến hoá MÔ HÌNH gần nhất — nửa vòng ngày
        # chạy được cả khi đường tới chợ đứt.
        self.hocGanNhat: dict | None = None
        self.tienHoaMoHinh: dict | None = None
        self.tienHoaGanNhat: dict | None = None
        self._tienHoaXong = False           # lượt hôm nay đã chạy TRỌN chưa

        # HỎI SỔ xem hôm nay đã chạy lượt tiến hoá chưa.
        #
        # Hai cờ trên chỉ nằm trong bộ nhớ, nên MỖI LẦN KHỞI ĐỘNG LẠI là
        # một lượt tiến hoá mới. Đo được trên sổ: **31 lượt riêng ngày
        # 29/08**, so với 1–7 ở các ngày khác — gần như toàn bộ là do khởi
        # động lại.
        #
        # Không chỉ tốn hai phút CPU mỗi lượt. Nặng hơn nhiều: nhịp "mỗi
        # ngày MỘT lượt" là một quyết định có chủ ý, ghi thẳng trong
        # config — *"cổng chặn bắt được tệ hơn nhưng không bắt được khác
        # đi mà rối hơn, nên tốc độ tiến hoá phải chậm hơn tốc độ một
        # người kịp nhìn"*. Chạy 31 lượt trong một ngày là cho cái cổng ấy
        # 31 lần rút thay vì 1, tức thổi tỉ lệ NHẬN NHẦM lên 31 lần.
        #
        # Sổ đã có sẵn trên đĩa. Hỏi nó.
        try:
            _ds = doc_so_tien_hoa(5)
            _hn = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d")
            if _ds and str(_ds[-1].get("luc") or "")[:10] == _hn:
                self._ngayTienHoa = _hn
                self._tienHoaXong = True
                bus.ghi(f"lượt tiến hoá ngày {_hn} đã chạy rồi (đọc từ sổ)"
                        " — không chạy lại vì khởi động lại", loai="he")
        except Exception as e:      # noqa: BLE001
            bus.ghi(f"không đọc được sổ tiến hoá: {type(e).__name__}: {e}"
                    " — có thể chạy lại một lượt thừa", loai="canh")
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

    def _lan(self, ten: str, viec) -> bool:
        """Chạy MỘT làn. Nó ngã thì kêu tên nó ra, và các làn sau vẫn chạy.

        Vì sao phải tách: các làn trong một vòng là những việc ĐỘC LẬP —
        tìm khung, cân lợi, kết toán, ghi băng, vòng tiến hoá ngày. Bản
        đầu xâu tất cả trên một mạch thẳng, nên làn đầu ngã là mất sạch
        các làn sau.

        Đã cắn thật, và cắn to. `nguon.tim_theo_slug()` gõ nhầm khoá
        config (`_NG['gamma']` trong khi khoá là `polymarketGamma`), nên
        MỌI vòng ném `KeyError: 'gamma'` ngay ở làn tìm khung. Hậu quả
        không phải "họ khung dài không chạy" mà là:

            không ghi được khung nào vào băng
            không kết toán được khung nào  → sổ kết quả đứng
            không khớp lại được phép nắn
            không lượt tiến hoá nào chạy   → vòng tự tiến hoá đứng HẲN

        Và buồng lái vẫn đếm `vòng 21590`, vẫn xanh. Một cỗ máy chết mà
        trông y hệt một cỗ máy đang chạy. Nhật ký có ghi `vòng N lỗi`
        mỗi hai giây, nhưng nó không nói mất những gì, và không ai đọc
        nhật ký của một cái bảng đang xanh.
        """
        try:
            viec()
            return True
        except Exception as e:                      # noqa: BLE001
            self.lanNga[ten] = f"{type(e).__name__}: {e}"
            self.lanNgaTong[ten] = self.lanNgaTong.get(ten, 0) + 1
            bus.ghi(f"làn `{ten}` ngã: {type(e).__name__}: {e} — "
                    "các làn sau vẫn chạy", loai="loi")
            return False

    #: Nơi giữ hai quyết định của NGƯỜI: tạm dừng, và bật/tắt chiến thuật.
    @property
    def _duong_dieu_khien(self):
        from .config import DATA_DIR
        return DATA_DIR / "dieu-khien.json"

    def _nap_dieu_khien(self) -> None:
        """Đọc lại hai quyết định của NGƯỜI sau khi khởi động lại.

        `tamDung` và `batTat` là những thứ một người CỐ Ý bấm — thường là
        vì vừa thấy cái gì đó không ổn. Chúng chỉ nằm trong bộ nhớ, nên
        một lần khởi động lại là bot chạy tiếp và mọi chiến thuật bật lại,
        im lặng.

        Chiều hỏng là chiều NGUY HIỂM: thứ người ta tắt đi thì bật lên,
        chứ không phải ngược lại. Và khởi động lại xảy ra vì đủ thứ lý do
        chẳng liên quan gì tới quyết định ấy — cập nhật, sập, người bấm.

        Cùng họ với `RiskEngine.nap_tu_so` và cờ ngày tiến hoá: trạng
        thái sống trong bộ nhớ mà sự thật phải nằm trên đĩa.
        """
        import json as _js
        try:
            f = self._duong_dieu_khien
            if not f.exists():
                return
            d = _js.loads(f.read_text(encoding="utf-8"))
        except Exception as e:      # noqa: BLE001
            bus.ghi(f"không đọc được sổ điều khiển: {type(e).__name__}: {e}"
                    " — chạy bằng mặc định (chạy tiếp, mọi chiến thuật bật)",
                    loai="canh")
            return
        if d.get("tamDung"):
            self.tamDung = True
        bt = d.get("batTat") or {}
        tat = [m for m in self.batTat if bt.get(m) is False]
        for m in tat:
            self.batTat[m] = False
        if self.tamDung or tat:
            bus.ghi("khôi phục quyết định của người: "
                    + ("ĐANG TẠM DỪNG" if self.tamDung else "chạy tiếp")
                    + (f" · tắt {len(tat)} chiến thuật: {chr(44).join(tat)}"
                       if tat else ""), loai="he")

    def ghi_dieu_khien(self) -> None:
        """Ghi ngay khi người bấm. Không đợi, không gom."""
        import json as _js
        try:
            f = self._duong_dieu_khien
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(_js.dumps(
                {"tamDung": bool(self.tamDung),
                 "batTat": dict(self.batTat)},
                ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:      # noqa: BLE001
            bus.ghi(f"KHÔNG ghi được sổ điều khiển: {type(e).__name__}: {e}"
                    " — quyết định này sẽ MẤT khi khởi động lại", loai="loi")
    def _mot_vong(self) -> None:
        self.vong += 1
        now = time.time() * 1000.0
        self.lanNga = {}

        # ── hiệu chỉnh đồng hồ, mỗi 60 giây ──────────────────────────────
        if now - self._lanHieuChinhDongHo > 60_000:
            def _dong_ho() -> None:
                moc = nguon.moc_thoi_gian_binance()
                if moc:
                    dong_ho.hieu_chinh(*moc)
            self._lan("đồng hồ", _dong_ho)
            self._lanHieuChinhDongHo = now

        # ── dọn băng quá hạn, MỖI NGÀY một lần ───────────────────────────
        #
        # `MayGhi.don_cu` có từ đầu, thực thi đúng hạn giữ `bang.ngayGiuLai`
        # khai trong config, và KHÔNG AI GỌI NÓ. Một chính sách nằm trong
        # config và trong mã mà không bao giờ chạy là một lời hứa hệ thống
        # không giữ: băng lớn mãi (29 MB sau mười ngày), trong khi `doc_bang`
        # trên tám ngày băng đã là 77 giây và 3,4 GB thường trú.
        #
        # Mỗi ngày một lần chứ không mỗi vòng: nó quét cả thư mục, và không
        # có gì đáng quét lại sau hai giây.
        ngay = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d")
        if ngay != self._ngayDonBang:
            self._ngayDonBang = ngay

            def _don() -> None:
                n = may_ghi.don_cu()
                if n:
                    bus.ghi(f"dọn băng quá hạn: xoá {n} file "
                            f"(giữ {(CONFIG.get('bang') or {}).get('ngayGiuLai', 30)}"
                            " ngày)", loai="he")
            self._lan("dọn băng", _don)

        # ── tìm khung mới, mỗi 20 giây (khung 5 phút nên không cần dày) ──
        if now - self._lanTimKhung > 20_000:
            self._lan("tìm khung", lambda: self._tim_khung(now))
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
            # Ghi băng cho CỬA ĐẶT CƯỢC. Tách khỏi lời gọi trên vì
            # bot không còn quyết định ở đó, nhưng nó vẫn là dữ liệu —
            # và là cách duy nhất kiểm lại kết luận nhắm-sai-cửa.
            try:
                self._ghi_dat_cuoc(tt, now, khung_ghi)
            except Exception as e:                  # noqa: BLE001
                bus.ghi(f"{tt['ma']} (ghi cửa đặt cược): {type(e).__name__}: {e}",
                        loai="loi")

        # ── soát lệnh maker chờ + kết toán ───────────────────────────────
        self._lan("soát lệnh chờ", lambda: self.cong.soat_cho(
            {m: {"UP": c.up, "DOWN": c.down} for m, c in self.capSo.items()}))

        def _ket_toan() -> None:
            if self.ketToan.soat(now):
                so_vo_dich.cap_nhat(self.so.doc(2000))
        self._lan("kết toán", _ket_toan)

        # ── làn chậm ─────────────────────────────────────────────────────
        if dai_quan_vi.den_luot():
            threading.Thread(target=dai_quan_vi.quet, daemon=True).start()
        if now - self._lanVoDich > 600_000:
            self._lan("vô địch", lambda: so_vo_dich.cap_nhat(self.so.doc(2000)))
            self._lanVoDich = now

        # ── LÀN CHẬM NHẤT: vòng tiến hoá, mỗi ngày một lượt ──────────────
        # Chạy TRONG runtime chứ không qua Task Scheduler: dịch vụ đó trên
        # máy này đang tắt và bật lại cần quyền quản trị — đã ghi trong
        # `tu-cam-thanh-runtime/dichvu/cai-dat.ps1`. Runtime vốn sống 24/7
        # nên nó là chỗ đáng tin hơn một bộ lịch có thể không tồn tại.
        self._lan("nắn lại", self._soat_nan_lai)
        self._lan("vòng tiến hoá", self._soat_tien_hoa)

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

    def _hoc_offline(self) -> None:
        """Dựng lại sổ hiệu chỉnh, rồi vặn một nút mô hình. Không cần chợ.

        Đây là nửa vòng ngày CHẠY ĐƯỢC khi đường tới chợ đứt. Nó không
        trả lời "bot kiếm được bao nhiêu" — chỉ trả lời "mô hình đoán
        chuẩn hơn hay kém đi", và câu ấy đo được bằng nến Binance cùng
        kết quả thật, không cần một giá chợ nào.
        """
        from . import hoc_offline as HO

        soNgay = int((CONFIG.get("tienHoa") or {}).get("soNgayHoc", 7))
        ma = next((t["ma"] for t in CONFIG["thiTruong"] if t.get("theo")),
                  "BTC_5M")

        # Sổ hiệu chỉnh dựng trên MỌI chợ, không phải chợ đầu tiên.
        #
        # `ma` (một chợ) vẫn dùng cho phần VẶN NÚT bên dưới — vặn một
        # nút thì chấm trên một chợ là đủ và nhanh hơn nhiều. Nhưng sổ
        # hiệu chỉnh thì được áp cho CẢ BỐN chợ khi chạy, nên khớp nó
        # trên riêng BTC là lấy đường cong của một chợ đi nắn ba chợ
        # khác — mà σ của SOL và XRP cỡ 2,4 lần BTC.
        #
        # Đã cắn: `dung_so_hieu_chinh` xoá sổ thô trước khi ghi, nên mỗi
        # vòng ngày thu sổ từ 228.156 dòng bốn chợ về 40.336 dòng một
        # chợ. Không có gì đỏ — sai số trung bình vẫn đẹp, vì nó là sai
        # số của BTC chấm trên BTC.
        r = HO.dung_so_hieu_chinh(soNgay=soNgay)
        if r.get("loi"):
            bus.ghi(f"học từ Binance: {r['loi']}", loai="canh")
            return
        self.hieuChinh = HieuChinh()
        self.phepNan = nan_lai.khop(self.hieuChinh)
        self._nanLucMs = time.time() * 1000.0
        self.hocGanNhat = r
        bus.ghi(f"sổ hiệu chỉnh dựng lại: {r['tongMau']:,} mẫu · "
                f"{r.get('soCho', 1)} chợ · sai "
                f"{(r['saiSoTB'] or 0)*100:.2f} điểm · Kelly "
                f"{'mở' if r['duKelly'] else 'khoá'}", loai="he")
        _hut = [m for m, v in (r.get("theoCho") or {}).items() if "loi" in v]
        if _hut:
            bus.ghi(f"sổ hiệu chỉnh: {len(_hut)} chợ hụt nến — "
                    + "; ".join(f"{m}: {r['theoCho'][m]['loi']}"
                               for m in _hut[:3]), loai="canh")

        v = HO.mot_luot_mo_hinh(soNgay=max(soNgay, 10), ma=ma)
        self.tienHoaMoHinh = v
        if v.get("loi"):
            bus.ghi(f"tiến hoá mô hình: {v['loi']}", loai="canh")
        elif v.get("nhan"):
            # Không còn hậu tố "⚠ nằm trong tiếng ồn" ở đây: nhánh NHẬN
            # nay không thể mang cờ ấy nữa, vì cổng đã chặn trước khi
            # ghi. Một cảnh báo dán lên thay đổi ĐÃ xảy ra không phải
            # cảnh báo — nó là lời thú nhận.
            n = v["nhan"]
            bus.ghi(f"tiến hoá MÔ HÌNH NHẬN: {n['nut']} {n['tu']:g} → "
                    f"{n['den']:g} · Brier CHỐT {v['chotGoc']:.5f} → "
                    f"{v['chotMoi']:.5f}", loai="he")
        elif v.get("trongTiengOn"):
            # Lượt SUÝT vặn là tin đáng thấy nhất trong cả vòng ngày:
            # hai cổng CHỌN/CHỐT đều gật mà khoảng tin vẫn chứa 0 nghĩa
            # là trục ấy đang PHẲNG quanh trị đang dùng. Đừng để nó lẫn
            # vào đống "giữ nguyên".
            t = v.get("tin95") or [0.0, 0.0]
            bus.ghi(f"tiến hoá mô hình CHẶN theo tiếng ồn: "
                    f"{v.get('nut')} {v.get('tu'):g} → {v.get('den'):g} — "
                    f"khoảng tin [{t[0]:+.6f}, {t[1]:+.6f}] chứa 0 "
                    f"({v.get('soKhoiChot')} khối)", loai="canh")
        else:
            bus.ghi(f"tiến hoá mô hình: giữ nguyên — {v.get('lyDo','')}",
                    loai="tin")

    def _chay_tien_hoa(self) -> None:
        try:
            # CỬA SỔ BĂNG, không phải cả băng.
            #
            # Đo hôm nay: cả băng là 115.779 khung, nạp mất ~90 giây và
            # giữ chừng ấy dict trong bộ nhớ. Một tháng nữa là nhiều phút
            # và hàng gigabyte — và đây là việc chạy MỖI NGÀY.
            #
            # Nhưng lý do chính không phải tốc độ. Vòng tiến hoá vặn tham
            # số theo hành vi GẦN ĐÂY của chợ; một tham số khớp với dữ
            # liệu một tháng trước là khớp với một cái chợ không còn tồn
            # tại. Nạp cả băng vừa chậm vừa SAI HƯỚNG.
            soNgay = int((CONFIG.get("tienHoa") or {}).get("soNgayBang", 7))
            tuNgay = time.strftime(
                "%Y-%m-%d", time.gmtime(time.time() - soNgay * 86400))

            # ── HỌC KHÔNG CẦN CHỢ, chạy TRƯỚC ────────────────────────
            #
            # Cổng tiền bên dưới cần giá chợ. Chợ đứt thì nó đứng yên với
            # lý do "thiếu mẫu" — đúng, nhưng nó sẽ đứng yên MÃI, và một
            # vòng ngày chỉ biết một cổng không chạy được thì bằng không
            # có vòng ngày.
            #
            # Hai việc dưới đây chỉ cần Binance:
            #   1. dựng lại sổ hiệu chỉnh — bảng cũ đi thì Kelly khoá
            #   2. vặn một nút mô hình nếu đáng
            # Việc 2 chấm bằng phép nắn khớp từ chính sổ ở việc 1, nên
            # thứ tự này bắt buộc.
            self._lan("học từ Binance", self._hoc_offline)

            kq = tien_hoa_mot_luot(tuNgay=tuNgay)
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
            self._bam_quan_sat(ma, ks, now)
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
                # Thước đo trễ bám token UP của CỬA ĐẶT CƯỢC — cố ý.
                #
                # Trong cửa ấy strike chưa tồn tại, nên chợ KHÔNG phản ứng
                # với giá nền vì lý do định giá. Nếu nó vẫn phản ứng thì
                # đó là dòng lệnh, và đó chính là thứ thước này đi tìm.
                # Nền tăng thì P(UP) phải tăng, nên hướng hàm ý đọc thẳng
                # được, không cần quy đổi.
                nenMa = next((t.get("nen") for t in CONFIG["thiTruong"]
                              if t.get("ma") == ma), None)
                if nenMa:
                    self.doTre.lien_ket(ma, nenMa, k.tokenUp)
                self.khungHienTai[ma] = k
                bus.ghi(f"{ma}: vào cửa đặt cược {k.slug} "
                        f"(còn {k.con_lai_giay(now):.0f}s)", loai="tin")

    def _bam_quan_sat(self, ma: str, ks: list, now: float) -> None:
        """Đăng ký sổ lệnh của khung ĐANG ăn thua, chỉ để GHI BĂNG.

        Băng tám ngày, 115.779 khung hình, và KHÔNG một dòng nào là sổ
        lệnh trong cửa ăn thua — vì `_tim_khung` chỉ từng chọn khung đang
        đặt cược. Nên câu hỏi đắt nhất của cung này chưa từng trả lời
        được: cửa ấy có báo giá thật không, hay chỉ có thang chờ.

        Không đặt lệnh ở đây. Dữ liệu trước, quyết định sau.
        """
        k = chon_quan_sat(ks, now)
        cu = self.khungQuanSat.get(ma)
        if k is None:
            if cu is not None:
                dong_song.bo_dang_ky(cu.tokenUp)
                dong_song.bo_dang_ky(cu.tokenDown)
                self.khungQuanSat.pop(ma, None)
            return
        if cu is not None and cu.slug == k.slug:
            return
        if cu is not None:
            dong_song.bo_dang_ky(cu.tokenUp)
            dong_song.bo_dang_ky(cu.tokenDown)
        dong_song.dang_ky(k.tokenUp, ma, "UP")
        dong_song.dang_ky(k.tokenDown, ma, "DOWN")
        self.khungQuanSat[ma] = k
        bus.ghi(f"{ma}: bám khung ăn thua {k.slug} để ghi băng "
                f"(còn {(k.endMs - now)/1000.0:.0f}s)", loai="tin")

    def _ghi_dat_cuoc(self, tt: dict, now: float, ghi: list[dict]) -> None:
        """Một dòng băng cho CỬA ĐẶT CƯỢC. Chỉ ghi, không quyết gì.

        Bot không còn ra quyết định ở cửa này — mô hình không làm việc
        được ở đó vì strike chưa tồn tại. Nhưng nó vẫn là dữ liệu: thước
        đo độ trễ bám nó, và đối chiếu hai cửa là cách duy nhất kiểm lại
        chính kết luận "nhắm sai cửa".

        `giaMo` ở đây là giá lúc mở cửa đặt cược và nó KHÔNG phải strike —
        giữ tên cũ để băng cũ đọc được, nhưng đừng nhầm.
        """
        ma = tt["ma"]
        k = self.khungHienTai.get(ma)
        if k is None:
            return
        su = dong_song.lay(k.tokenUp)
        sd = dong_song.lay(k.tokenDown)
        if su is None or sd is None:
            return
        gia = self.giaNen.get(ma)
        mo = nguon.gia_mo_khung(tt["nen"], k.batDauDatCuocMs)
        if gia is None or not mo:
            return
        bd = self.bienDong.get(ma)
        sigma = bd.sigma_giay() if bd is not None else None
        ghi.append({
            "ma": ma, "slug": k.slug, "giaiDoan": DAT_CUOC,
            "giaNen": gia, "giaMo": mo,
            "sigmaGiay": sigma,
            "conLaiGiay": k.con_lai_giay(now),
            "so": {
                "UP": {"luc": su.nhanLucMs,
                       "bid": [{"gia": m.gia, "luong": m.luong} for m in su.bid[:30]],
                       "ask": [{"gia": m.gia, "luong": m.luong} for m in su.ask[:30]]},
                "DOWN": {"luc": sd.nhanLucMs,
                         "bid": [{"gia": m.gia, "luong": m.luong} for m in sd.bid[:30]],
                         "ask": [{"gia": m.gia, "luong": m.luong} for m in sd.ask[:30]]},
            },
        })

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
        """Một lượt quyết định cho một market — TRONG KHUNG ĂN THUA.

        ## Vì sao đổi cửa

        Trước bản này hàm chỉ chạy khi `giai_doan == DAT_CUOC`, tức cửa
        [T−300, T]. Đo ra rằng đó là cửa mô hình KHÔNG làm việc được:
        strike là giá lúc T (`scripts/do-strike.py`, điểm kỹ năng của chợ
        +6,6% cho định nghĩa ấy, −38,7% cho định nghĩa cũ), nên trong cửa
        đặt cược strike CHƯA TỒN TẠI. Số gia từ T tới T+300 độc lập với
        mọi thứ quan sát được lúc t < T ⇒ giá trị thật đúng 0,5, bất kể
        giá đang ở đâu.

        Cùng mô hình, cùng τ=60s, cùng tỉ lệ nền, khác đúng chỗ đứng
        (`scripts/do-cua-nao.py`, 199 mốc):

            đứng ở cửa đặt cược,    K = giá(T−300)   kỹ năng  −74,3%
            đứng trong khung ăn thua, K = giá(T)     kỹ năng  +43,5%

        Nên bot làm việc ở [T, T+300] và ĐỨNG NGOÀI [T−300, T]. Cửa đặt
        cược vẫn được ghi băng — nó là dữ liệu, chỉ không phải chỗ ra
        quyết định.

        ## Điều này chưa chứng minh có tiền ở đây

        Chợ cũng biết strike và cũng thấy đồng hồ. Nếu sổ lệnh trong khung
        ăn thua chỉ là thang chờ thì `cap.dung_duoc` sẽ False và bot đứng
        ngoài, có khai lý do — đúng hành vi cần có khi chưa biết.
        """
        ma = tt["ma"]
        k = self.khungQuanSat.get(ma)
        if k is None:
            self._than_phien(ma, "chưa bám được khung nào đang ăn thua")
            return
        if k.giai_doan(now) != QUAN_SAT:
            return          # ra khỏi khung rồi; `_tim_khung` sẽ đổi

        # 1. giá nền + biến động
        gia = nguon.gia_binance(tt["nen"])
        if gia is None:
            return
        self.giaNen[ma] = gia
        bd = self.bienDong.get(ma)
        if bd is None:
            # NẠP MỒI ngay: lưới phút cần vài phút mẫu mới có nghĩa, và
            # chờ là mù mất mấy phút đầu sau mỗi lần khởi động. Đường tới
            # chợ chập chờn nên những phút ấy đắt.
            bd = DoBienDong()
            try:
                bd.mo_dau(nguon.nen_gan_day(
                    tt["nen"], int(bd.cuaSoGiay / 60.0) + 2))
            except Exception as e:                  # noqa: BLE001
                bus.ghi(f"{ma}: nạp mồi σ hỏng: {type(e).__name__}: {e}",
                        loai="canh")
            self.bienDong[ma] = bd
        bd.them(gia, now)
        sigma = bd.sigma_giay()
        if sigma is None:
            self._than_phien(
                ma, f"chưa đủ mẫu ước lượng σ ({bd.so_mau}/"
                    f"{DoBienDong.TOI_THIEU_PHUT} nến phút)")
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
        #
        # STRIKE = giá lúc `eventStartMs`, không phải lúc mở cửa đặt cược.
        # Đây là chỗ sai gốc của cả cung, và nó im lặng: lấy nhầm mốc thì
        # mô hình vẫn ra một xác suất trông rất hợp lý, chỉ là về một câu
        # hỏi khác. 25,7% kết quả lật ngược giữa hai định nghĩa.
        mo = nguon.gia_mo_khung(tt["nen"], k.eventStartMs)
        if not mo:
            self._than_phien(ma, "không lấy được strike (giá lúc mở khung)")
            return
        tau = k.con_lai_an_thua_giay(now)
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
            # Cổng cứng nằm trong `cham_moc` (bẫy 5) để không ai đi vòng
            # được. Câu GIẢI THÍCH thì nói ở đây, vì đây là chỗ đối diện
            # người vận hành — `dong_co.goi` chỉ trả được "động cơ từ chối
            # kết luận", mà gộp mọi lý do vào một câu chính là thứ chính
            # docstring của nó cảnh báo.
            cs = bd.cuaSoGiay if bd is not None else None
            if cs and tau > 50.0 * cs:
                self._than_phien(
                    ma, f"σ đo trên {cs:.0f}s mà chân trời {tau / 86400.0:.0f} "
                        f"ngày — lệch {tau / cs:,.0f} lần. Từ chối định giá: "
                        "σ 900s quy năm có trung vị 0,209 nhưng min 0,000 và "
                        "max 2,239, cắm vào đây thì P(chạm) nhảy từ ~0% tới "
                        "~100% chỉ vì mười lăm phút vừa rồi tình cờ lặng hay "
                        "tình cờ động")
                return
            gc, viSao = dong_co.goi(
                maDC, ma, giaHienTai=gia, moc=float(tt["moc"]), tauGiay=tau,
                dinhDaQua=dinh, sigmaGiay=sigma,
                # Cho động cơ biết σ này đo trên cửa sổ dài bao nhiêu. Nó
                # cần con số ấy để TỪ CHỐI khi cửa sổ quá ngắn so với chân
                # trời — xem bẫy 5 ở `cham_moc`. Không truyền thì nó định
                # giá bằng một σ nhiễu gấp hai nghìn lần mà không ai biết.
                cuaSoSigmaGiay=bd.cuaSoGiay if bd is not None else None,
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

        # 6. chân lệch — LỜI KHUYÊN, không phải hành động
        #
        # `qc` chỉ đi vào buồng lái. Không chỗ nào trong vòng lặp huỷ lệnh,
        # nâng giá, vượt spread hay đóng chân theo nó. Ghi ở đây vì cái
        # tên `quyet_chan` đọc như thể có ai đó thi hành — xem docstring
        # của `chan_rui_ro.quyet` để biết ba lớp nào đã che phần nguy
        # hiểm, và ca nào thì KHÔNG được che.
        v = self.kho.lay(ma)
        qc = quyet_chan(v, cap, tau, now,
                        tranTranUsd=self.risk.tranChuaPhongHoUsd)
        self.quyetChan[ma] = (
            {"loi": qc.loi, "nhan": qc.nhan, "ben": qc.ben, "soCo": qc.soCo,
             "khoaLoUsd": qc.khoaLoUsd, "lyDo": qc.lyDo} if qc else {})

        # 7. chiến thuật đề xuất
        #
        # Lát cắt đếm tới `endMs`, KHÔNG tới `eventStartMs`. Chỗ này bị bỏ
        # sót lúc đổi cửa và nó hỏng rất lặng: với `eventStartMs` thì trong
        # khung ăn thua `conLaiGiay` luôn bằng 0, giai đoạn luôn là ĐÃ
        # KHOÁ, và mọi chiến thuật soi `bc.dongHo.giaiDoan` — `tao-lap`
        # đòi GOM_THANH_KHOAN/GIUA_KHUNG, `can-ket-qua` đòi CUOI_KHUNG —
        # đều lặng lẽ trả về rỗng. Bot vẫn chạy, vẫn ghi băng, chỉ là bốn
        # trong sáu ngón nghề không bao giờ được gọi tới.
        lc = dong_ho.lat_cat(k.endMs, k.daiSongGiay,
                             tuoiDuLieuMs=now - su.nhanLucMs)
        bc = BoiCanh(ma=ma, gia=gc, soUp=su, soDown=sd, dongHo=lc,
                     viThe=v,
                     tranLechHuongUsd=self.risk.tranLechHuongUsd)
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
            "ma": ma, "slug": k.slug, "giaiDoan": QUAN_SAT,
            "giaNen": gia, "giaMo": mo,
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
        # ĐO từng mảnh. `/api/trang-thai` đo được **21–35 giây** trên làn
        # thật 05/09/2026, trong khi `/api/cau-hinh` và `/api/nhat-ky` chỉ
        # 0,10–0,15s — nên server KHÔNG đói luồng, chính `anh_chup()` nặng.
        #
        # Dựng lại từng mảnh ngoài tiến trình thì mảnh nào cũng dưới 10ms:
        # cái chậm phụ thuộc TRẠNG THÁI TÍCH LUỸ của tiến trình sống, và
        # không tái hiện được từ ngoài. Nên nó phải tự khai.
        #
        # Thị Bạc Ty đọc đường này với timeout 4 giây; chậm quá thì nó coi
        # như KHÔNG ĐỌC ĐƯỢC và ngắt cầu dao `von-ngoai-mu`, dừng cấp vốn
        # cho cả cỗ máy bên ấy. Nên đây không phải chuyện thẩm mỹ.
        _dong_ho: dict[str, float] = {}

        def _do(ten, fn):
            _t0 = time.perf_counter()
            try:
                return fn()
            finally:
                _dong_ho[ten] = round((time.perf_counter() - _t0) * 1000.0, 1)

        ket = _do("so.doc", lambda: self.so.doc(500))
        return {
            "thoiGianAnhChupMs": _dong_ho,
            "vong": self.vong, "batDauLuc": self.batDauLuc,
            "chayDuocGiay": time.time() - self.batDauLuc,
            "tamDung": self.tamDung,
            "che": che_hieu_luc(), "cheKhai": CONFIG.get("che"),
            "risk": _do("risk", self.risk.tom_tat),
            "kho": _do("kho", self.kho.tom_tat),
            "lenh": _do("lenh", self.cong.tom_tat),
            "nguon": _do("nguon", nguon.tom_tat),
            "dongSong": _do("dongSong", dong_song.tom_tat),
            "dongNen": _do("dongNen", dongSongNen.tom_tat),
            "doTre": _do("doTre", self.doTre.tom_tat),
            "nanLai": _do("nanLai", self.phepNan.tom_tat),
            "duongRa": _do("duongRa", nguon.duong_ra),
            "soKetQua": _do("soKetQua", so_ket_qua.tom_tat),
            "ketToan": _do("ketToan", self.ketToan.tom_tat),
            "doThi": _do("doThi", do_thi.tom_tat),
            "voDich": _do("voDich", so_vo_dich.tom_tat),
            "hocOffline": self.hocGanNhat,
            "tienHoaMoHinh": self.tienHoaMoHinh,
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
            # Làn nào ngã trong vòng vừa rồi. Buồng lái phải thấy được:
            # đếm `vòng` tăng đều mà mọi làn đều ngã là một cỗ máy chết
            # trông y hệt một cỗ máy đang chạy.
            "lanNga": dict(self.lanNga),
            # Cộng dồn từ lúc khởi động — `lanNga` chỉ nói VÒNG NÀY.
            "lanNgaTong": dict(self.lanNgaTong),
            "quyetChan": dict(self.quyetChan),
            "hieuChinh": {
                "bang": self.hieuChinh.bang(),
                "tongMau": self.hieuChinh.tong_mau,
                "duDeDungKelly": self.hieuChinh.du_de_dung_kelly(),
                "saiSoTB": self.hieuChinh.sai_so_tuyet_doi_tb(),
            },
            "thongKe": _do("thongKe", lambda: thong_ke(ket)),
            "vi": _do("vi", dai_quan_vi.tom_tat),
            "dongCo": _do("dongCo", dong_co.tom_tat),
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
            # Thống kê GHI và báo cáo ĐỌC là hai chuyện. Bản trước chỉ hiện
            # cái đầu, nên hai file băng hỏng nằm trên đĩa suốt mà buồng lái
            # vẫn xanh — `BaoCaoDoc` được tính rất kỹ rồi vứt đi.
            "bang": dict(may_ghi.tom_tat(), doc=bao_cao_doc_cuoi()),
            # Nút nào đang nằm ở MÉP dải vặn. Mép quyết định thì mọi
            # lượt tiến hoá kết luận "giữ nguyên" nghe như dữ liệu đã
            # nói — thật ra là cái lồng đã nói.
            "nutOMep": nut_o_mep(),
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
