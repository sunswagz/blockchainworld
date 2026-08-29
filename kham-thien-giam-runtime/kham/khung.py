"""Vòng đời một khung Up/Down — đo trên chợ thật, không suy từ tên trường.

Đây là module đắt nhất của cả runtime, vì mọi thứ tôi TƯỞNG về vòng đời khi
viết bản đầu đều sai, và mỗi cái sai đều hỏng im lặng.

## Ba trường thời gian, và cái nào mới đúng

Một market `btc-updown-5m-1787217300` khai:

    startDate        2026-08-19T09:23:44Z   <- lúc TẠO market, hôm trước
    eventStartTime   2026-08-20T09:15:00Z   <- trùng mốc Unix trong slug
    endDate          2026-08-20T09:20:00Z   <- eventStartTime + 5 phút

`startDate` là bẫy: nó cách endDate gần một NGÀY, và bản đầu của tôi suýt
dùng nó. Mốc thật nằm ở `eventStartTime`, và nó bằng đúng con số trong slug.

## Cửa đặt cược nằm TRƯỚC cửa quan sát

Bản đầu tôi giả định `bắt đầu = endDate − 300s`, tức cửa đặt cược trùng cửa
quan sát. Đo thật thì ngược: bám bốn khung qua ranh giới bằng WebSocket, ghi
mỗi 11 giây, thấy rõ hai trạng thái tách bạch:

    09:12:12  khung eventStart 09:10  ->  sổ 101/0, thang chờ, KHÔNG yết giá
    09:12:12  khung eventStart 09:15  ->  sổ 92/7,  UP 0.930, giá CHẠY thật

Khung đã qua `eventStartTime` thì sổ đóng băng thành thang chờ. Khung chưa
tới `eventStartTime` mới là khung giao dịch được. Nói cách khác:

    [eventStart − 300, eventStart]   ĐẶT CƯỢC   <- bot làm việc ở đây
    [eventStart, endDate]            QUAN SÁT   <- sổ đóng băng, chờ kết quả

Bản đầu nhắm đúng vào cửa quan sát và bỏ qua cửa đặt cược. Hệ quả: runtime
chỉ nhìn thấy thang chờ, tưởng chợ điên (UP 99,9¢), và mọi lệch giá nó thấy
đều là ảo.

## Strike đặt ở đâu — CHƯA CHỐT, và cố ý đo chứ không đoán

Trong cửa đặt cược, giá chợ CHẠY THEO BTC rất mạnh: cùng một khung, P(UP)
đi 0,24 → 0,49 → 0,59 → 0,71 → 0,93 trong hai phút. Nếu strike đặt ở
`eventStartTime` (còn ở tương lai) thì đó là tung đồng xu chưa bắt đầu, và
giá phải quanh quẩn 0,5. Nó không quanh quẩn. Nên strike gần như chắc chắn
đã CỐ ĐỊNH từ đầu cửa đặt cược.

Nhưng "gần như chắc chắn" không đủ để đem tính tiền. Nên cả hai ứng viên
đều được tính, và `ket_toan.py` đối chiếu kết quả tự tính với kết quả SÀN
sau mỗi khung. Ứng viên sai sẽ lộ ra thành `soBatDong` tăng — dữ liệu quyết,
không phải tôi quyết. Xem `config.json` → `khung.mocStrike`.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

# ── giai đoạn ─────────────────────────────────────────────────────────────
CHUA_MO = "chua-mo"       # chưa tới cửa đặt cược
DAT_CUOC = "dat-cuoc"     # ĐANG giao dịch được
QUAN_SAT = "quan-sat"     # sổ đóng băng, giá đang được đo
DA_XONG = "da-xong"       # qua endDate, chờ kết quả

NHAN = {CHUA_MO: "chưa mở", DAT_CUOC: "đặt cược",
        QUAN_SAT: "quan sát", DA_XONG: "đã xong"}


def doc_moc(iso) -> float | None:
    try:
        return dt.datetime.fromisoformat(
            str(iso).replace("Z", "+00:00")).timestamp() * 1000.0
    except (ValueError, TypeError, AttributeError):
        return None


@dataclass(frozen=True)
class Khung:
    """Một khung Up/Down đã phân giải xong mọi mốc thời gian."""
    slug: str
    ma: str
    capNen: str
    tokenUp: str
    tokenDown: str
    batDauDatCuocMs: float
    eventStartMs: float
    endMs: float
    daiSongGiay: float = 300.0

    # ── vị trí trong vòng đời ─────────────────────────────────────────────
    def giai_doan(self, bayGioMs: float) -> str:
        if bayGioMs < self.batDauDatCuocMs:
            return CHUA_MO
        if bayGioMs < self.eventStartMs:
            return DAT_CUOC
        if bayGioMs < self.endMs:
            return QUAN_SAT
        return DA_XONG

    def dat_cuoc_duoc(self, bayGioMs: float) -> bool:
        return self.giai_doan(bayGioMs) == DAT_CUOC

    def con_lai_giay(self, bayGioMs: float) -> float:
        """Số giây còn lại của CỬA ĐẶT CƯỢC.

        KHÔNG phải τ của mô hình. Chú thích cũ ở đây viết nó là "τ đúng
        cho mô hình… nếu strike cố định từ đầu cửa" — và cái "nếu" ấy đã
        được đo là SAI (`scripts/do-strike.py`). Strike là giá lúc
        `eventStartMs`, nên trong cửa đặt cược nó chưa tồn tại.

        Giữ hàm này cho phần hiển thị và cho việc ghi băng cửa đặt cược.
        τ của mô hình là `con_lai_an_thua_giay`.
        """
        return max(0.0, (self.eventStartMs - bayGioMs) / 1000.0)

    def con_lai_an_thua_giay(self, bayGioMs: float) -> float:
        """Số giây còn lại của KHUNG ĂN THUA [T, T+300]. τ đúng của mô hình.

        Ở đây strike đã cố định (giá lúc `eventStartMs`) và thời gian còn
        lại là quãng khuếch tán thật sự chưa biết. Đo được: cùng mô hình,
        cùng τ=60s, cùng tỉ lệ nền, đứng ở đây điểm kỹ năng +43,5%; đứng
        ở cửa đặt cược −74,3%.
        """
        return max(0.0, (self.endMs - bayGioMs) / 1000.0)

    def troi_qua_pct(self, bayGioMs: float) -> float:
        tong = max(1.0, self.eventStartMs - self.batDauDatCuocMs)
        return min(100.0, max(0.0, (bayGioMs - self.batDauDatCuocMs) / tong * 100.0))

    def tom_tat(self, bayGioMs: float) -> dict:
        gd = self.giai_doan(bayGioMs)
        return {
            "slug": self.slug, "ma": self.ma,
            "giaiDoan": gd, "nhan": NHAN.get(gd, gd),
            "datCuocDuoc": gd == DAT_CUOC,
            "conLaiGiay": self.con_lai_giay(bayGioMs),
            "troiQuaPct": self.troi_qua_pct(bayGioMs),
            "eventStartMs": self.eventStartMs, "endMs": self.endMs,
        }


def phan_giai(m: dict, ma: str, capNen: str, songGiay: float = 300.0) -> Khung | None:
    """Đổi một bản ghi Gamma thành `Khung`. None nếu thiếu mốc.

    KHÔNG đọc `startDate` — xem chú thích đầu file. Mốc duy nhất tin được là
    `eventStartTime`; `endDate` chỉ dùng để biết khi nào hỏi kết quả.
    """
    import json as _json

    evs = doc_moc(m.get("eventStartTime"))
    end = doc_moc(m.get("endDate"))
    if evs is None:
        # Dự phòng: mốc Unix nằm ngay trong slug và bằng eventStartTime.
        # Giữ đường này vì nó đã được đối chiếu khớp trên chợ thật.
        try:
            evs = float(str(m.get("slug", "")).rsplit("-", 1)[1]) * 1000.0
        except (IndexError, ValueError):
            return None
    if end is None:
        end = evs + songGiay * 1000.0

    toks = doc_token(m)
    if toks is None:
        return None

    return Khung(
        slug=m.get("slug") or "", ma=ma, capNen=capNen,
        tokenUp=toks[0], tokenDown=toks[1],
        batDauDatCuocMs=evs - songGiay * 1000.0,
        eventStartMs=evs, endMs=end, daiSongGiay=songGiay,
    )


def doc_token(m: dict) -> tuple[str, str] | None:
    """Hai token của một market. Gamma có lúc trả mảng, có lúc trả CHUỖI
    JSON của mảng — nên phải thử cả hai chứ không tin một dạng."""
    import json as _json
    toks = m.get("clobTokenIds") or []
    if isinstance(toks, str):
        try:
            toks = _json.loads(toks)
        except _json.JSONDecodeError:
            return None
    if not isinstance(toks, (list, tuple)) or len(toks) < 2:
        return None
    return str(toks[0]), str(toks[1])


def phan_giai_dai(m: dict, ma: str, capNen: str) -> Khung | None:
    """Một market sống hàng tháng — họ chạm mốc.

    Dùng lại nguyên `Khung` chứ không dựng lớp thứ hai, bằng cách đặt mốc
    khác đi: cửa đặt cược mở SUỐT từ lúc market mở tới lúc hết hạn.

        batDauDatCuocMs = lúc market mở
        eventStartMs    = endMs          ← cửa đặt cược đóng đúng lúc hết hạn
        endMs           = hạn

    Nhờ vậy `giai_doan()` trả DAT_CUOC suốt vòng đời, và `con_lai_giay()`
    trả đúng τ tới hạn — chính là τ mà công thức chạm mốc cần. Không phải
    mẹo: ở họ này, "cửa còn đặt được" và "còn bao lâu tới kết quả" ĐÚNG là
    một khoảng, khác hẳn họ Lên/Xuống nơi chúng là hai cửa tách rời.
    """
    het = doc_moc(m.get("endDate"))
    mo = doc_moc(m.get("startDate")) or doc_moc(m.get("createdAt"))
    if not het or not mo or het <= mo:
        return None
    toks = doc_token(m)
    if toks is None:
        return None
    up, down = toks
    return Khung(slug=m.get("slug") or "", ma=ma, capNen=capNen,
                 tokenUp=up, tokenDown=down,
                 batDauDatCuocMs=mo, eventStartMs=het, endMs=het,
                 daiSongGiay=(het - mo) / 1000.0)


def chon_quan_sat(ds: list[Khung], bayGioMs: float) -> Khung | None:
    """Khung ĐANG trong cửa ăn thua [T, T+300]. None nếu không có.

    Đây là cửa mà runtime chưa bao giờ chạm tới, và cũng là cửa DUY NHẤT
    mô hình làm việc được. Đo trên Binance, cùng mô hình, cùng τ=60s,
    cùng tỉ lệ nền, chỉ khác chỗ đứng (`scripts/do-cua-nao.py`):

        đứng ở cửa đặt cược, K = giá(T−300)   điểm kỹ năng  −74,3%
        đứng trong cửa ăn thua, K = giá(T)    điểm kỹ năng  +43,5%

    Lý do đơn giản tới mức khó tin là mình đã bỏ qua: trong cửa đặt cược
    strike CHƯA TỒN TẠI — nó là giá lúc T, mà T còn ở phía trước. Số gia
    từ T tới T+300 độc lập với mọi thứ quan sát được, nên giá trị thật là
    đúng 0,5 bất kể giá đang ở đâu.

    Hàm này để GHI BĂNG, chưa để đặt lệnh. Chưa ai đo được có tiền trong
    cửa ấy không, vì chưa có một dòng sổ lệnh nào của nó — và không có dữ
    liệu thì mọi quyết định về nó chỉ là đoán.
    """
    qs = [k for k in ds if k.giai_doan(bayGioMs) == QUAN_SAT]
    if not qs:
        return None
    return min(qs, key=lambda k: k.endMs)


def chon_dat_cuoc(ds: list[Khung], bayGioMs: float) -> Khung | None:
    """Khung ĐANG đặt cược được, gần hết cửa nhất. None nếu không có.

    Gần hết cửa nhất chứ không phải xa nhất: cửa càng gần đóng thì strike
    càng đã cố định lâu, giá càng phản ánh nhiều thông tin, và mô hình càng
    có cái để so.
    """
    dc = [k for k in ds if k.dat_cuoc_duoc(bayGioMs)]
    if not dc:
        return None
    return min(dc, key=lambda k: k.eventStartMs)
