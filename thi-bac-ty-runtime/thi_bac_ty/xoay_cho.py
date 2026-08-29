"""XOAY CHỖ — chỗ ngồi có hạn, và ai ngồi mới là câu hỏi.

## Chuyện đo được, không phải suy đoán

Đo trên máy sống 29/08/2026, danh mục 12 vị thế / 6.000 USD:

    4 vị thế AMM       2.000 USD   21–39 %/năm   giữ 168h
    8 vị thế cho vay   4.000 USD   1,89–3,01 %   giữ 720h  ← 30 NGÀY
    bình quân gia quyền:          +13,21 %/năm

Cùng lúc ấy, trong hàng đợi tờ trình của CÙNG vòng: mười hai cơ hội
Pendle ở 9,2 · 10,5 · 11,2 · 12,1 · 16,0 %/năm. **Không cái nào được
cấp.** Lý do từ chối, nguyên văn: «đã đủ 12 vị thế».

Tám chỗ bị khoá ba mươi ngày ở mức 2,4 %/năm, trong khi 10–16 % đi qua
mỗi vòng rồi bị đuổi. Ty giữ tám chỗ ấy tên là `lending.rate_rotation` —
*xoay theo lãi suất* — và nó không xoay: mở rồi giữ tới hết hạn.

## Vì sao KHÔNG xoay ngay khi thấy cái tốt hơn

Vì đổi chỗ TỐN TIỀN. Ra khỏi vị thế cũ và vào vị thế mới đều mất phí, và
phí ấy trả ngay trong khi phần lãi hơn thì nhỏ giọt theo giờ. Xoay vì
thấy một con số đẹp hơn là cách chắc chắn để **thua vì phí** trong khi
mọi lần đổi đều trông như một quyết định thông minh.

Nên phép tính phải trả lời đúng một câu:

    (lãi MỚI − lãi CŨ) × số giờ CHUNG  >  phí RA + phí VÀO

Vế trái là thứ được thêm; vế phải là thứ trả ngay. Nhỏ hơn thì ngồi yên.

BỐN chỗ dễ tự lừa, và cả bốn đều bị chặn ở đây:

**Giờ CÒN LẠI, không phải giờ giữ.** Một vị thế còn 2 giờ nữa hết hạn thì
đổi nó chẳng được gì — phần lãi hơn chỉ chạy trong 2 giờ ấy. Lấy `giuGio`
là tính ra một khoản lợi không có thật.

**Và giờ chung là NGẮN HƠN trong hai bên.** Bản đầu của chính file này lấy
giờ còn lại của vị thế CŨ (713h) cho một cơ hội mới chỉ giữ 168h, và ra
một khoản lợi lớn gấp bốn lần sự thật. Sau 168h thì cơ hội mới đóng, phần
lãi hơn hết chạy, và 545 giờ còn lại kia là một lời hứa không ai đưa ra.

**Vốn KHOÁ thì không xoay được, dù phép tính có đẹp tới đâu.** Một PT
Pendle khoá 90 ngày là 90 ngày không rút ra. Đổi một vị thế đang khoá là
một việc KHÔNG LÀM ĐƯỢC, không phải một việc lỗ — nên đếm riêng, đừng
gộp vào "không đáng đổi".

**Chưa đo được thanh khoản thoát thì chưa biết có ra nổi không.** `None`
ở đây phải chặn, không được coi như "ra được" — vào được không có nghĩa
là ra được, và một phép xoay giả định ra được là một phép xoay có thể
mắc kẹt giữa chừng.

## Bản này chỉ ĐO, không xoay

Trả về một bản kê: đổi được bao nhiêu chỗ, mỗi chỗ thêm bao nhiêu, và
danh mục sẽ ra bao nhiêu phần trăm. Đường THỰC HIỆN chưa nối, và nối nó
là quyết định của người — cùng lý do với `tuVanTienHoa`.

Đo trước, làm sau. Một cỗ máy tự đổi danh mục vì một phép tính chưa ai
nhìn qua là một cỗ máy không ai dám để chạy qua đêm.
"""
from __future__ import annotations

from dataclasses import dataclass, field

NAM_GIO = 365.0 * 24.0


@dataclass
class CoHoiDoiCho:
    """Một lần đổi chỗ ĐÁNG giá, đã trừ phí."""
    maCu: str
    chienLuocCu: str
    taiSanCu: str
    aprCu: float
    maMoi: str
    chienLuocMoi: str
    taiSanMoi: str
    aprMoi: float
    vonUsd: float
    gioConLai: float           # vị thế CŨ còn bao lâu
    gioChung: float            # ngắn hơn trong hai bên — quãng lãi hơn CHẠY
    laiThemUsd: float          # phần lãi hơn trong số giờ CHUNG
    phiDoiUsd: float           # phí ra + phí vào
    loiRongUsd: float          # lãi thêm − phí đổi; đã dương mới vào danh sách

    def tom_tat(self) -> dict:
        return {
            "maCu": self.maCu, "chienLuocCu": self.chienLuocCu,
            "taiSanCu": self.taiSanCu, "aprCu": self.aprCu,
            "maMoi": self.maMoi, "chienLuocMoi": self.chienLuocMoi,
            "taiSanMoi": self.taiSanMoi, "aprMoi": self.aprMoi,
            "vonUsd": self.vonUsd, "gioConLai": self.gioConLai,
            "gioChung": self.gioChung,
            "laiThemUsd": self.laiThemUsd, "phiDoiUsd": self.phiDoiUsd,
            "loiRongUsd": self.loiRongUsd,
        }


@dataclass
class LatCatXoayCho:
    soViThe: int = 0
    soXoayDuoc: int = 0
    soBiKhoa: int = 0              # vốn còn khoá — KHÔNG xoay được
    soKhongDoDuocThoat: int = 0    # chưa đo thanh khoản thoát
    aprHienTai: float | None = None
    aprSauKhiXoay: float | None = None
    loiRongUsd: float = 0.0
    #: Bao nhiêu chỗ ĐÃ đóng thật. Khác `soXoayDuoc` — cái kia là "đáng
    #: đổi", cái này là "đã đổi". Bằng 0 khi `tuXoayCho` tắt, và lúc ấy
    #: buồng lái phải đọc được rằng đây mới chỉ là phép đo.
    soDaDong: int = 0
    #: Còn ghế trống thì KHÔNG đuổi ai — tiền đề của cả cơ chế này là chỗ
    #: ngồi có hạn, và còn chỗ thì câu hỏi «ai nên ngồi» không đặt ra.
    viConGhe: bool = False
    xoay: list = field(default_factory=list)
    vi: str = ""

    def tom_tat(self) -> dict:
        return {
            "soViThe": self.soViThe, "soXoayDuoc": self.soXoayDuoc,
            "soBiKhoa": self.soBiKhoa,
            "soKhongDoDuocThoat": self.soKhongDoDuocThoat,
            "aprHienTai": self.aprHienTai,
            "aprSauKhiXoay": self.aprSauKhiXoay,
            "loiRongUsd": self.loiRongUsd, "soDaDong": self.soDaDong,
            "viConGhe": self.viConGhe,
            "xoay": [x.tom_tat() for x in self.xoay],
            "vi": self.vi,
        }


def apr_tu_to_trinh(toTrinh: dict) -> float | None:
    """APR khai trên tờ trình, %/năm. `None` khi tờ trình không khai.

    `None` chứ không phải 0: một cơ hội không khai lãi thì ta chưa biết nó
    lãi bao nhiêu, khác hẳn một cơ hội khai huề vốn — và trộn hai thứ ấy
    làm bảng xếp hạng đẩy những tờ trình IM LẶNG xuống đáy như thể chúng
    tệ, trong khi ta chỉ đơn giản là chưa hỏi.
    """
    if not isinstance(toTrinh, dict):
        return None
    v = toTrinh.get("netMoiGioBps")
    if v is None:
        net, gio = toTrinh.get("netUocBps"), toTrinh.get("giuGio")
        if net is None or not gio:
            return None
        v = float(net) / float(gio)
    return float(v) * NAM_GIO / 100.0


def phi_mot_chieu_usd(toTrinh: dict, vonUsd: float) -> float | None:
    """Phí MỘT chiều theo `phiUocBps`. `None` khi tờ trình không khai.

    `None` chứ không phải 0: không khai phí thì ta KHÔNG BIẾT đổi sang nó
    tốn bao nhiêu, và coi là 0 là dựng ra một phép đổi miễn phí — đúng
    cách để xoay liên tục rồi thua sạch vì phí, mà mỗi lần đổi vẫn trông
    như một quyết định thông minh.
    """
    if not isinstance(toTrinh, dict):
        return None
    try:
        return abs(vonUsd) * float(toTrinh["phiUocBps"]) / 10_000.0
    except (KeyError, TypeError, ValueError):
        return None


def do_xoay_cho(soViThe: dict, toTrinhMoi: list, gioHienTai: float,
                bienAnToan: float = 1.0) -> LatCatXoayCho:
    """Đo xem đổi chỗ nào ĐÁNG, sau khi trừ phí. **KHÔNG đổi gì.**

    `bienAnToan` nhân lên phí: 1,0 là hoà vốn đúng bằng phí. Để 1,0 ở đây
    vì phép đo này để NGƯỜI đọc; đường tự động — nếu có ngày được nối —
    phải đặt biên rộng hơn, vì lúc ấy không ai nhìn từng lần đổi nữa.
    """
    lat = LatCatXoayCho(soViThe=len(soViThe))
    if not soViThe:
        lat.vi = "chưa giữ vị thế nào — không có chỗ nào để xoay"
        return lat

    # ── vị thế ĐANG GIỮ, và vì sao một số cái không xoay được ───────────
    dang: list[tuple[float, str, tuple]] = []
    tongVon = 0.0
    tongApr = 0.0
    for ma, so in soViThe.items():
        t = getattr(so, "toTrinh", None) or {}
        apr = apr_tu_to_trinh(t)
        von = abs(float(getattr(so, "vonUsd", 0.0)))
        tongVon += von
        if apr is not None:
            tongApr += von * apr
        daGiu = max(0.0, (gioHienTai - float(
            getattr(so, "moLucGiay", gioHienTai))) / 3600.0)
        khoa = t.get("khoaVonDenGiay")
        if khoa is not None and daGiu < float(khoa):
            lat.soBiKhoa += 1
            continue
        if t.get("thanhKhoanThoatUsd") is None:
            lat.soKhongDoDuocThoat += 1
            continue
        if apr is None:
            continue
        conLai = max(0.0, float(t.get("giuGio") or 0.0) - daGiu)
        dang.append((apr, ma, (so, t, von, conLai)))
    lat.aprHienTai = (tongApr / tongVon) if tongVon > 0 else None

    # ── cơ hội MỚI, tốt nhất trước ──────────────────────────────────────
    moi: list[tuple[float, dict]] = []
    for tt in (toTrinhMoi or []):
        t = tt if isinstance(tt, dict) else (
            tt.tom_tat() if hasattr(tt, "tom_tat") else {})
        apr = apr_tu_to_trinh(t)
        if apr is not None:
            moi.append((apr, t))
    moi.sort(key=lambda x: -x[0])
    dang.sort(key=lambda x: x[0])          # tệ nhất đổi trước

    daDung: set[int] = set()
    them = 0.0
    for aprCu, ma, (so, tCu, von, conLai) in dang:
        for i, (aprMoi, tMoi) in enumerate(moi):
            if i in daDung or aprMoi <= aprCu:
                continue
            phiRa = phi_mot_chieu_usd(tCu, von)
            phiVao = phi_mot_chieu_usd(tMoi, von)
            if phiRa is None or phiVao is None:
                continue                   # không biết phí thì không đổi
            # NGẮN HƠN trong hai bên: phần lãi hơn chỉ chạy chừng nào
            # CẢ HAI còn hiệu lực. Lấy giờ của bên cũ là hứa thay cho một
            # cơ hội chưa hứa.
            giuMoi = float(tMoi.get("giuGio") or 0.0)
            chung = min(conLai, giuMoi) if giuMoi > 0 else conLai
            lai = von * (aprMoi - aprCu) / 100.0 * (chung / NAM_GIO)
            phi = (phiRa + phiVao) * bienAnToan
            if lai <= phi:
                continue
            daDung.add(i)
            lat.soXoayDuoc += 1
            lat.loiRongUsd += lai - phi
            them += von * (aprMoi - aprCu)
            lat.xoay.append(CoHoiDoiCho(
                maCu=ma, chienLuocCu=str(getattr(so, "chienLuoc", "?")),
                taiSanCu=str(tCu.get("taiSan")), aprCu=aprCu,
                maMoi=str(tMoi.get("ma")),
                chienLuocMoi=str(tMoi.get("chienLuoc")),
                taiSanMoi=str(tMoi.get("taiSan")), aprMoi=aprMoi,
                vonUsd=von, gioConLai=conLai, gioChung=chung,
                laiThemUsd=lai, phiDoiUsd=phi, loiRongUsd=lai - phi))
            break

    if lat.aprHienTai is not None and tongVon > 0:
        lat.aprSauKhiXoay = lat.aprHienTai + them / tongVon
    lat.vi = _vi(lat)
    return lat


def _vi(lat: LatCatXoayCho) -> str:
    if lat.soXoayDuoc == 0:
        return (f"KHÔNG chỗ nào đáng đổi sau khi trừ phí — {lat.soBiKhoa} vị "
                f"thế còn khoá vốn, {lat.soKhongDoDuocThoat} chưa đo được "
                f"thanh khoản thoát. Ngồi yên là một kết quả hợp lệ.")
    return (f"{lat.soXoayDuoc} chỗ ĐÁNG đổi: danh mục {lat.aprHienTai:+.2f}% "
            f"→ {lat.aprSauKhiXoay:+.2f}%/năm, lợi ròng "
            f"{lat.loiRongUsd:+.4f} USD ĐÃ TRỪ phí đổi. Đây là phép ĐO — "
            f"chưa đổi gì, và đường thực hiện chưa nối.")
