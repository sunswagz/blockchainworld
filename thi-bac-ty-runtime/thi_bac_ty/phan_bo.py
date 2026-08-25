"""PHÂN BỔ VỐN — chia tiền, và chịu trách nhiệm về cái đã chia.

Rủi Ro Tổng nói *"tờ này cho tối đa $X"*. Phân Bổ nói *"trong tất cả những
tờ được phép, tôi rót thật vào đâu, bao nhiêu, và giữ lại bao nhiêu tiền
mặt"*.

    $1.000 có sẵn

    Perp     xin $300  ·  Rủi Ro Tổng cho tối đa $300
    Tín dụng xin $400  ·  cho tối đa $400
    Chênh lệch xin $500 ·  cho tối đa $200   ← đã bị cắt
    Cơ bản   xin $300  ·  cho tối đa $300

    tổng được phép = $1.200 > $1.000 có

              ↓  Phân Bổ quyết

    Perp        $200
    Tín dụng    $400
    Chênh lệch  $0
    Cơ bản      $300
    dự trữ      $100

## Cấp TUẦN TỰ, không cấp song song — và đây là chỗ dễ sai nhất

Rủi Ro Tổng xét từng tờ trên **danh mục hiện tại**. Hai tờ cùng chạm Binance,
xét riêng thì cả hai đều lọt; cấp cả hai cùng lúc thì vượt trần cảng.

Nên Phân Bổ cấp từng tờ một, và **xét lại** trên danh mục đã cập nhật sau
mỗi lần cấp. Chậm hơn, nhưng đó là cách duy nhất trần phơi nhiễm còn nghĩa.

Xét trước-cấp-sau hàng loạt là một lỗi kinh điển và nó im lặng: mọi tờ đều
"đã qua rủi ro", tổng lại thì vượt, và không dòng log nào báo.

## Xếp hạng theo cái gì

    điểm = netMoiGioBps × tinCay × (1 − diemRuiRo)

Ba thừa số, và mỗi thừa số chặn một cách tự lừa:

  * `netMoiGioBps` — không phải `netBps` trần. 20 bps giữ 24 giờ thua 6 bps
    giữ 2 giờ, vì vốn quay được mười hai lượt.
  * `tinCay` — một cơ hội đẹp dựng trên dữ liệu mù không đáng bằng một cơ
    hội vừa phải dựng trên dữ liệu chắc.
  * `1 − diemRuiRo` — lợi nhuận kỳ vọng phải chiết khấu theo rủi ro, nếu
    không thì cỗ máy luôn chọn thứ nguy hiểm nhất.

**NET âm thì không xếp hạng, loại thẳng.** Nhân một số âm với hai thừa số
trong [0,1] vẫn ra số âm, nhưng "âm ít" sẽ đứng trên "âm nhiều" và cỗ máy
vẫn rót tiền vào chỗ lỗ ít nhất. Lỗ ít vẫn là lỗ.

## Dự trữ tiền mặt là một quyết định, không phải phần thừa

`tiLeDuTru` giữ lại một phần NAV bằng tiền mặt kể cả khi còn cơ hội tốt. Lý
do: cơ hội tốt hơn có thể đến sau, và một danh mục dùng hết vốn thì không
vào được cơ hội ấy — chi phí cơ hội của việc **không còn tiền**.
"""
from __future__ import annotations

from dataclasses import dataclass, field

MAC_DINH = {
    "tiLeDuTru": 0.20,        # giữ lại phần NAV này bằng tiền mặt
    "toiThieuMotLanUsd": 25.0,  # rót ít hơn thì phí cố định ăn hết
    "toiDaSoViThe": 12,       # quá nhiều vị thế thì không theo dõi nổi
}


@dataclass
class LatCatPhanBo:
    luc: str
    vonKhaDungUsd: float
    duTruUsd: float
    daCap: list = field(default_factory=list)
    tuChoi: list = field(default_factory=list)
    tongCapUsd: float = 0.0

    def tom_tat(self) -> dict:
        return {"luc": self.luc, "vonKhaDungUsd": self.vonKhaDungUsd,
                "duTruUsd": self.duTruUsd, "tongCapUsd": self.tongCapUsd,
                "soCap": len(self.daCap), "soTuChoi": len(self.tuChoi),
                "daCap": list(self.daCap), "tuChoi": list(self.tuChoi)}


class PhanBo:
    def __init__(self, cau_hinh: dict | None = None) -> None:
        self.c = {**MAC_DINH, **(cau_hinh or {})}

    @staticmethod
    def diem(tt, diemRuiRo: float | None) -> float:
        """Điểm xếp hạng. Xem docstring đầu file cho ba thừa số."""
        net = tt.net_moi_gio_bps
        if net <= 0:
            return float("-inf")            # lỗ ít vẫn là lỗ, loại thẳng
        tin = 1.0 if tt.tinCay is None else max(0.0, min(1.0, tt.tinCay))
        rr = 0.5 if diemRuiRo is None else max(0.0, min(1.0, diemRuiRo))
        return net * tin * (1.0 - rr)

    def chia(self, toTrinh: list, rui_ro_tong, danh_muc, so_cai=None,
             luc: str = "") -> LatCatPhanBo:
        """Chia vốn cho một lô tờ trình. **Thay đổi `danh_muc` tại chỗ.**

        Trả về lát cắt ghi lại đã cấp gì và từ chối gì — kèm lý do, luôn kèm
        lý do. Một quyết định phân bổ không giải thích được thì không kiểm
        toán được, và cái không kiểm toán được thì không sửa được.
        """
        from .so_cai import ButToan
        from .danh_muc import ViThe

        nav = danh_muc.navUsd
        du_tru = nav * float(self.c["tiLeDuTru"])
        lat = LatCatPhanBo(luc=luc or _bay_gio(),
                           vonKhaDungUsd=max(0.0, danh_muc.tienMatUsd - du_tru),
                           duTruUsd=du_tru)

        # Xếp hạng TRƯỚC, cấp SAU. Xếp hạng dùng điểm rủi ro sơ bộ (chưa xét
        # danh mục) chỉ để định thứ tự; trần thật vẫn do `xet()` quyết ở
        # từng bước cấp.
        xep = []
        for tt in toTrinh:
            d, _ = rui_ro_tong.diem(tt)
            xep.append((self.diem(tt, d), tt))
        xep.sort(key=lambda x: x[0], reverse=True)

        for diem, tt in xep:
            if diem == float("-inf"):
                lat.tuChoi.append({"maToTrinh": tt.ma, "chienLuoc": tt.chienLuoc,
                                   "lyDo": "NET mỗi giờ ≤ 0 — lỗ ít vẫn là lỗ"})
                continue
            if len(danh_muc.viThe) >= int(self.c["toiDaSoViThe"]):
                lat.tuChoi.append({"maToTrinh": tt.ma, "chienLuoc": tt.chienLuoc,
                                   "lyDo": f"đã đủ {self.c['toiDaSoViThe']} vị "
                                           f"thế — quá nhiều thì không theo dõi nổi"})
                continue

            # XÉT LẠI trên danh mục ĐÃ CẬP NHẬT — xem docstring đầu file.
            pq = rui_ro_tong.xet(tt, danh_muc)
            if not pq.duyet:
                lat.tuChoi.append({**pq.tom_tat(), "diemXep": diem})
                if so_cai:
                    so_cai.ghi(ButToan(
                        "TU_CHOI", "; ".join(pq.lyDo) or "Rủi Ro Tổng từ chối",
                        0.0, tt.chienLuoc, tt.ma,
                        {"xinUsd": tt.vonCanUsd, "diemXep": diem}))
                continue

            con = danh_muc.tienMatUsd - du_tru
            cap = min(pq.choToiDaUsd, con)
            if cap < float(self.c["toiThieuMotLanUsd"]):
                lat.tuChoi.append({
                    "maToTrinh": tt.ma, "chienLuoc": tt.chienLuoc,
                    "lyDo": f"chỉ còn cấp được {cap:.2f} USD, dưới sàn "
                            f"{self.c['toiThieuMotLanUsd']} — phí cố định ăn hết",
                    "choToiDaUsd": pq.choToiDaUsd})
                continue

            # Chia đều cho các chân: mỗi chân cần đúng phần vốn của nó.
            moi_chan = cap / len(tt.chan)
            chan = [ViThe(tt.ma, tt.chienLuoc, c.ben, c.cang, c.taiSan,
                          moi_chan, c.chuoi, c.loai, lat.luc)
                    for c in tt.chan]
            if not danh_muc.cam_ket(tt.ma, chan):
                lat.tuChoi.append({"maToTrinh": tt.ma, "chienLuoc": tt.chienLuoc,
                                   "lyDo": "Danh Mục từ chối — không đủ tiền mặt"})
                continue

            lat.daCap.append({
                "maToTrinh": tt.ma, "chienLuoc": tt.chienLuoc,
                "taiSan": tt.taiSan, "xinUsd": tt.vonCanUsd,
                "choToiDaUsd": pq.choToiDaUsd, "capUsd": cap,
                "diemXep": diem, "diemRuiRo": pq.diemRuiRo,
                "biCat": pq.biCat, "lyDoCat": list(pq.lyDoCat),
                "netMoiGioBps": tt.net_moi_gio_bps})
            lat.tongCapUsd += cap
            if so_cai:
                so_cai.ghi(ButToan(
                    "CAP_VON",
                    (f"xếp hạng {diem:.4f} · xin {tt.vonCanUsd:.0f} · "
                     f"trần {pq.choToiDaUsd:.0f} · cấp {cap:.0f}"
                     + (" (BỊ CẮT: " + "; ".join(pq.lyDoCat) + ")"
                        if pq.biCat else "")),
                    cap, tt.chienLuoc, tt.ma,
                    {"netMoiGioBps": tt.net_moi_gio_bps,
                     "diemRuiRo": pq.diemRuiRo, "tinCay": tt.tinCay,
                     "chan": [c.tom_tat() for c in tt.chan],
                     "bangChung": list(tt.bangChung)}))
        return lat

    def tom_tat(self) -> dict:
        return dict(self.c)


def _bay_gio() -> str:
    import datetime as dt
    return dt.datetime.now(dt.timezone.utc).isoformat(
        timespec="milliseconds").replace("+00:00", "Z")
