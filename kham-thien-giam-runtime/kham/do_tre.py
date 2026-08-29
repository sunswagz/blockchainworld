"""Thước đo ĐỘ TRỄ: Binance động trước bao lâu thì Polymarket mới đổi giá?

Đây là con số mà cả một dòng bot được dựng lên quanh nó, và cũng là con số
được kể lại rất khác nhau tuỳ người kể:

    một bài lan truyền (4/2026)      ≈ 2.700 ms
    nghiên cứu OpenMarket (7/2026)   ≈   347 ms

Tám lần. Chọn tin bên nào là chọn một chiến lược khác hẳn — 2,7 giây thì
một cỗ máy nhịp 2 giây vẫn kịp, còn 347 ms thì nó đã muộn trước khi bắt
đầu nghĩ. Nên đừng tin bên nào cả. Đo.

## Cách đo

1. Tìm **cú động** phía Binance: trong cửa sổ W, log-return vượt k lần độ
   lệch chuẩn của chính nó. Không lấy ngưỡng cố định theo phần trăm —
   ngưỡng cố định biến một phiên yên ả thành "không có gì xảy ra" và một
   phiên sôi động thành "cái gì cũng là cú động".
2. Sau mốc đó, xem giá giữa bên Polymarket. Bấm giờ tới lúc nó dịch ít
   nhất `nguongPoly` theo **đúng hướng** cú động hàm ý.
3. Ghi lại độ trễ. Gộp lại lấy trung vị, tứ phân vị, và tỉ lệ trúng hướng.

## Và bước 4, bước quan trọng nhất: ĐỐI CHỨNG

Với bất kỳ chuỗi giá nào, nếu ta chọn một mốc thời gian rồi chờ "giá dịch
0,5 xu theo một hướng", ta LUÔN LUÔN đợi được. Nghĩa là quy trình ba bước
ở trên sẽ ra một con số độ trễ đẹp đẽ **ngay cả khi giữa hai sàn không có
quan hệ nào cả**.

Nên mỗi lần đo thật, đo kèm một lần đối chứng: cùng số sự kiện, nhưng mốc
thời gian **rút ngẫu nhiên** trong cùng quãng quan sát. Nếu trung vị thật
không khác trung vị đối chứng, thì thứ vừa đo được là tiếng ồn, không phải
độ trễ — và phải nói ra đúng như vậy.

Đây là chỗ khác nhau giữa một con số và một biểu đồ đẹp. Bài viết nêu 2,7
giây không kèm đối chứng nào; nghiên cứu OpenMarket có, và cũng chính vì
có mà họ kết luận được rằng lợi thế biến mất sau phí — một kết luận không
vui nhưng đứng được.

## Giới hạn phải nói trước

Ta lấy mẫu phía Polymarket bằng một luồng chạy nhịp `NHIP_LAY_MAU_MS`, nên
KHÔNG đo được độ trễ nhỏ hơn nhịp đó. Với nhịp 50 ms thì phân biệt được
347 ms với 2.700 ms rất thoải mái, nhưng đừng đọc chữ số hàng đơn vị.
"""
from __future__ import annotations

import math
import random
import statistics
import threading
import time
from collections import deque
from dataclasses import dataclass, field

from .bus import bus

NHIP_LAY_MAU_MS = 50.0        # sàn phân giải của phép đo này
CUA_SO_MS = 1000.0            # cửa sổ tìm cú động phía nền
K_NGUONG = 3.0                # cú động = vượt k lần độ lệch chuẩn
NGUONG_POLY = 0.004           # Polymarket phải dịch ≥ 0,4 xu mới tính
TRE_TOI_DA_MS = 8000.0        # quá mốc này thì coi như không phản ứng
NGHI_SAU_SU_KIEN_MS = 3000.0  # tránh đếm một cú động thành nhiều
SAU_LICH = 8192

# Ô lưới để ước sigma. KHÔNG ước từ tick liền tick — xem `_sigma_luoi`.
O_LUOI_MS = 250.0
CUA_SO_SIGMA_MS = 60_000.0    # một phút, đủ 240 ô lưới


@dataclass
class SuKien:
    tMs: float
    ma: str
    huong: int                 # +1 nền tăng, −1 nền giảm
    doLon: float               # log-return đã chuẩn hoá theo sigma
    treMs: float | None = None  # None = Polymarket không phản ứng kịp


@dataclass
class KetQua:
    n: int = 0
    soPhanUng: int = 0
    trungVi: float | None = None
    p25: float | None = None
    p75: float | None = None
    tyLePhanUng: float = 0.0
    # đối chứng
    nDoiChung: int = 0
    trungViDoiChung: float | None = None
    tyLeDoiChung: float = 0.0
    ketLuan: str = "chưa đủ mẫu"
    lichSu: list = field(default_factory=list)


class DoTre:
    """Đo một chiều: nền động → Polymarket đổi giá."""

    def __init__(self, dongSongNen, dongSong) -> None:
        self.nen = dongSongNen
        self.song = dongSong
        self._lien: dict[str, tuple[str, str]] = {}   # ma → (capNen, assetIdUp)
        self._poly: dict[str, deque] = {}             # ma → [(tMs, giua)]
        self._suKien: deque = deque(maxlen=SAU_LICH)
        self._khoa = threading.Lock()
        self._chay = False
        self._luong: threading.Thread | None = None
        self._nghiToi: dict[str, float] = {}

    def lien_ket(self, ma: str, capNen: str, assetIdUp: str) -> None:
        with self._khoa:
            self._lien[ma] = (capNen.lower(), assetIdUp)
            self._poly.setdefault(ma, deque(maxlen=SAU_LICH))

    def bo_lien_ket(self, ma: str) -> None:
        with self._khoa:
            self._lien.pop(ma, None)

    def bat(self) -> None:
        if self._chay:
            return
        self._chay = True
        self._luong = threading.Thread(target=self._vong, daemon=True)
        self._luong.start()

    def dung(self) -> None:
        self._chay = False

    # ── vòng lấy mẫu ──────────────────────────────────────────────────
    def _vong(self) -> None:
        while self._chay:
            try:
                self._mot_nhip()
            except Exception as e:                     # noqa: BLE001
                bus.ghi(f"đo trễ vấp: {type(e).__name__}: {e}", loai="canh")
            time.sleep(NHIP_LAY_MAU_MS / 1000.0)

    def _mot_nhip(self) -> None:
        now = time.time() * 1000.0
        with self._khoa:
            lien = dict(self._lien)
        for ma, (cap, aid) in lien.items():
            so = self.song.lay(aid)
            if so is not None:
                g = _giua(so)
                if g is not None:
                    with self._khoa:
                        b = self._poly.get(ma)
                        if b is not None and (not b or abs(b[-1][1] - g) > 1e-12):
                            b.append((now, g))
            self._soat_cu_dong(ma, cap, now)
        self._cham_diem(now)

    def _soat_cu_dong(self, ma: str, cap: str, now: float) -> None:
        if now < self._nghiToi.get(ma, 0.0):
            return
        mau = self.nen.lat(cap, now - CUA_SO_SIGMA_MS, now)
        if len(mau) < 40:
            return
        sd = _sigma_luoi(mau)
        if sd is None or sd <= 0:
            return

        dau = self.nen.gan_nhat_truoc(cap, now - CUA_SO_MS)
        if dau is None or dau[1] <= 0:
            return
        cuoi = mau[-1]
        buoc = math.log(cuoi[1] / dau[1])
        chuan = abs(buoc) / (sd * math.sqrt(CUA_SO_MS))
        if chuan < K_NGUONG:
            return

        self._nghiToi[ma] = now + NGHI_SAU_SU_KIEN_MS
        with self._khoa:
            self._suKien.append(SuKien(tMs=cuoi[0], ma=ma,
                                       huong=1 if buoc > 0 else -1,
                                       doLon=chuan))

    def _cham_diem(self, now: float) -> None:
        """Với mỗi sự kiện chưa chấm, xem Polymarket đã phản ứng chưa."""
        with self._khoa:
            for sk in self._suKien:
                if sk.treMs is not None:
                    continue
                b = self._poly.get(sk.ma)
                if not b:
                    continue
                goc = None
                for t, g in b:
                    if t <= sk.tMs:
                        goc = g
                    else:
                        break
                if goc is None:
                    continue
                for t, g in b:
                    if t <= sk.tMs:
                        continue
                    if t - sk.tMs > TRE_TOI_DA_MS:
                        sk.treMs = -1.0          # −1 = không phản ứng kịp
                        break
                    # Nền tăng ⇒ P(UP) phải TĂNG. Sai hướng thì không tính:
                    # một cú dịch ngược hướng không phải là "phản ứng chậm",
                    # nó là bằng chứng chống lại giả thuyết.
                    if (g - goc) * sk.huong >= NGUONG_POLY:
                        sk.treMs = t - sk.tMs
                        break
                else:
                    if now - sk.tMs > TRE_TOI_DA_MS:
                        sk.treMs = -1.0

    # ── kết quả ───────────────────────────────────────────────────────
    def ket_qua(self, toiThieu: int = 20) -> KetQua:
        with self._khoa:
            xong = [s for s in self._suKien if s.treMs is not None]
            poly = {ma: list(b) for ma, b in self._poly.items()}
        k = KetQua(n=len(xong))
        if not xong:
            return k
        tre = [s.treMs for s in xong if s.treMs is not None and s.treMs >= 0]
        k.soPhanUng = len(tre)
        k.tyLePhanUng = len(tre) / len(xong)
        if tre:
            k.trungVi = statistics.median(tre)
            s = sorted(tre)
            k.p25 = s[len(s) // 4]
            k.p75 = s[(3 * len(s)) // 4]

        dc = self._doi_chung(xong, poly)
        k.nDoiChung, k.trungViDoiChung, k.tyLeDoiChung = dc

        k.lichSu = [{"tMs": s.tMs, "ma": s.ma, "huong": s.huong,
                     "doLon": round(s.doLon, 2), "treMs": s.treMs}
                    for s in list(xong)[-60:]]
        k.ketLuan = self._ket_luan(k, toiThieu)
        return k

    def _doi_chung(self, xong, poly) -> tuple[int, float | None, float]:
        """Cùng số sự kiện, mốc thời gian RÚT NGẪU NHIÊN trong cùng quãng.

        Không có bước này thì mọi con số phía trên đều vô nghĩa: chọn bất kỳ
        mốc nào rồi chờ giá dịch 0,4 xu thì bao giờ cũng chờ được.
        """
        rng = random.Random(20260821)
        tre: list[float] = []
        # ĐẾM MỌI cú động, kể cả cú không đánh giá được — đúng quy ước
        # nhánh thật.
        #
        # Bản trước `n += 1` nằm SAU hai lệnh `continue`, nên đối chứng
        # bỏ những cú có đệm sổ mỏng ra khỏi mẫu số, trong khi nhánh thật
        # tính chúng vào (`tyLePhanUng = len(tre) / len(xong)`) — ở đó
        # chúng thành "không phản ứng kịp" và KÉO TỈ LỆ THẬT XUỐNG.
        #
        # Hai mẫu số khác nhau thì hai tỉ lệ không so được với nhau, và
        # cái so ấy là toàn bộ lý do nhóm đối chứng tồn tại. Lệch theo
        # chiều LÀM TÍN HIỆU THẬT TRÔNG KÉM HƠN — chiều an toàn, nhưng
        # một nhóm đối chứng không công bằng thì không phải nhóm đối
        # chứng.
        n = 0
        for sk in xong:
            n += 1
            b = poly.get(sk.ma) or []
            if len(b) < 10:
                continue
            t0, t1 = b[0][0], b[-1][0] - TRE_TOI_DA_MS
            if t1 <= t0:
                continue
            gia = rng.uniform(t0, t1)
            goc = None
            for t, g in b:
                if t <= gia:
                    goc = g
                else:
                    break
            if goc is None:
                continue
            for t, g in b:
                if t <= gia:
                    continue
                if t - gia > TRE_TOI_DA_MS:
                    break
                if (g - goc) * sk.huong >= NGUONG_POLY:
                    tre.append(t - gia)
                    break
        if not n:
            return 0, None, 0.0
        return n, (statistics.median(tre) if tre else None), len(tre) / n

    @staticmethod
    def _ket_luan(k: KetQua, toiThieu: int) -> str:
        if k.n < toiThieu:
            return f"chưa đủ mẫu ({k.n}/{toiThieu} cú động)"
        if k.trungVi is None:
            return "Polymarket không phản ứng theo hướng nền trong khung thời gian đo"
        if k.trungViDoiChung is None:
            return (f"trung vị {k.trungVi:.0f} ms · đối chứng không tìm được "
                    "phản ứng nào — dấu hiệu TỐT cho giả thuyết có độ trễ thật")
        # Thật phải NHANH hơn đối chứng rõ rệt thì mới là độ trễ thật.
        if k.trungVi >= k.trungViDoiChung * 0.7:
            return (f"trung vị {k.trungVi:.0f} ms nhưng đối chứng ngẫu nhiên ra "
                    f"{k.trungViDoiChung:.0f} ms — KHÔNG khác biệt. Thứ đo được "
                    "ở đây là tiếng ồn, không phải độ trễ.")
        return (f"trung vị {k.trungVi:.0f} ms so với đối chứng "
                f"{k.trungViDoiChung:.0f} ms — có độ trễ thật đo được")

    def tom_tat(self) -> dict:
        k = self.ket_qua()
        with self._khoa:
            # Số THÔ để phân biệt ba kiểu "không có gì": chưa liên kết
            # market nào, chưa lấy được giá giữa bên Polymarket, hay có
            # sự kiện mà chưa chấm xong. Không có ba số này thì cả ba
            # hiện ra giống hệt nhau — `n = 0` — và không lần được.
            chuanDoan = {
                "soLienKet": len(self._lien),
                "soSuKienTho": len(self._suKien),
                "sauPoly": {m: len(b) for m, b in self._poly.items()},
            }
        return {
            "chuanDoan": chuanDoan,
            "n": k.n, "soPhanUng": k.soPhanUng,
            "trungViMs": k.trungVi, "p25Ms": k.p25, "p75Ms": k.p75,
            "tyLePhanUng": k.tyLePhanUng,
            "doiChung": {"n": k.nDoiChung, "trungViMs": k.trungViDoiChung,
                         "tyLe": k.tyLeDoiChung},
            "ketLuan": k.ketLuan,
            "thamSo": {"cuaSoMs": CUA_SO_MS, "kNguong": K_NGUONG,
                       "nguongPoly": NGUONG_POLY,
                       "nhipLayMauMs": NHIP_LAY_MAU_MS,
                       "treToiDaMs": TRE_TOI_DA_MS},
            "sanPhanGiaiMs": NHIP_LAY_MAU_MS,
            "gan": k.lichSu[-12:],
        }


def _sigma_luoi(mau: list[tuple[float, float]]) -> float | None:
    """Độ lệch chuẩn log-return mỗi √ms, ước từ LƯỚI THÔ chứ không từ tick.

    Bản đầu ước từ tick liền tick và phát hiện được ĐÚNG 0 cú động trong
    46.000 tin. Không phải chợ yên — là phép ước sai.

    Ở nhịp mili-giây, giá không phải khuếch tán thuần: nó có nhiễu vi cấu
    trúc (giá tốt nhất nhấp nháy qua lại quanh giá trị thật). Nhiễu đó có
    tự tương quan ÂM mạnh, nên khi ta nhân với √(1/dt) để quy về mỗi ms,
    nó thổi sigma lên nhiều lần. Sigma phồng thì ngưỡng k·sigma dâng theo,
    và không cú động thật nào vượt nổi — thước im lặng trong lúc trông
    như đang chạy tốt.

    Cách chữa chuẩn: lấy mẫu lại theo lưới đủ thô để nhiễu tan bớt, rồi
    tính trên lưới đó. 250 ms là chỗ thoả hiệp: đủ thô để tránh nhiễu, đủ
    mịn để một cửa sổ một giây vẫn còn bốn ô.
    """
    o: dict[int, float] = {}
    for t, g in mau:
        if g > 0:
            o[int(t // O_LUOI_MS)] = g          # giá cuối trong mỗi ô
    if len(o) < 12:
        return None
    khoa = sorted(o)
    r = []
    for i in range(1, len(khoa)):
        b = khoa[i] - khoa[i - 1]
        if b <= 0:
            continue
        # Ô trống thì khoảng cách dài hơn; chia cho √(số ô) để quy chuẩn.
        r.append(math.log(o[khoa[i]] / o[khoa[i - 1]]) /
                 math.sqrt(b * O_LUOI_MS))
    if len(r) < 8:
        return None
    try:
        return statistics.pstdev(r)
    except statistics.StatisticsError:
        return None


def _giua(so) -> float | None:
    """Giá giữa của một sổ.

    Bản đầu viết `getattr(so, "bestBid", None)` — nhưng `bestBid` là tên
    trong JSON trả ra, còn thuộc tính thật là `best_bid`. `getattr` có
    tham số mặc định nên nó không báo lỗi: nó trả None, đều đặn, mãi mãi.

    Hậu quả: thước đo trễ bắt được 21 cú động thật rồi chấm cả 21 vào một
    cuốn sổ RỖNG, và báo ra "chưa đủ mẫu". Cả chuỗi WebSocket → phát hiện
    → chấm điểm đều chạy đúng; chỉ một cái tên gõ sai làm con số cuối
    cùng bằng 0. Không có ba số chẩn đoán trong `tom_tat` thì không cách
    nào phân biệt được nó với "chợ đang yên".

    `SoLenh` vốn đã có sẵn `giua`. Dùng thẳng, và để nó ném nếu sai tên.
    """
    return so.giua if so is not None else None
