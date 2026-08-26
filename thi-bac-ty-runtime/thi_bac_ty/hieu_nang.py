"""HIỆU NĂNG — đo bằng đường NAV, không bằng một APR nhân thẳng.

## Vì sao không lấy một con số phần trăm nhân lên

Vốn thật đi thế này:

    100 × 1,12 × 1,31 × 0,92 × 1,22 × 1,05

chứ không phải `100 × 1,5^5`. Một năm âm ở giữa không chỉ làm chậm — nó ăn
vào cái nền mà mọi năm sau nhân lên từ đó. Lấy một APR đẹp nhân thẳng là
giấu đúng phần ấy.

Nên bộ máy đo:

    CAGR              lợi suất gộp thật sự, không phải trung bình cộng
    SỤT VỐN TỐI ĐA    đáy sâu nhất tính từ đỉnh trước đó
    THỜI GIAN DƯỚI ĐÁY  bao lâu chưa về lại đỉnh cũ

Con số thứ hai và thứ ba là thứ quyết định người ta có giữ nổi hệ thống qua
một đợt xấu hay không, và không APR nào nói được chúng.

## Chưa đủ mẫu thì NÓI CHƯA ĐỦ MẪU

Với vài giờ dữ liệu, CAGR ngoại suy ra một con số vô nghĩa và trông rất
thuyết phục — quy 0,3% của nửa ngày thành hàng nghìn phần trăm một năm.
Nên dưới `TOI_THIEU_GIO`, mọi trường tỉ suất trả `None`, và `duDeKetLuan`
là `False`. `None` chứ không phải 0: "chưa đo được" khác hẳn "bằng không".
"""
from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field

#: Dưới ngần này giờ thì không quy đổi ra năm. Bảy ngày.
TOI_THIEU_GIO = 168.0

NAM_GIO = 365.0 * 24.0


@dataclass
class DuongNav:
    """Đường NAV theo thời gian. Chỉ thêm, và có trần độ dài."""
    tran: int = 20_000
    diem: list = field(default_factory=list)     # [(lucMs, nav)]

    def ghi(self, navUsd: float, lucMs: float | None = None) -> None:
        import time
        t = lucMs if lucMs is not None else time.time() * 1000.0
        self.diem.append((float(t), float(navUsd)))
        if len(self.diem) > self.tran:
            # Bỏ điểm CŨ NHẤT, không bỏ ngẫu nhiên: đỉnh và đáy gần đây là
            # thứ quyết định sụt vốn, và chúng nằm ở cuối.
            self.diem = self.diem[-self.tran:]

    def do(self, vonBanDauUsd: float) -> dict:
        return do_hieu_nang(self.diem, vonBanDauUsd)


def do_hieu_nang(diem: list, vonBanDauUsd: float) -> dict:
    """`[(lucMs, nav)]` → CAGR, sụt vốn tối đa, thời gian dưới đáy."""
    if not diem:
        return {"duDeKetLuan": False, "vi": "chưa có điểm NAV nào",
                "soDiem": 0}

    ds = sorted(diem, key=lambda x: x[0])
    t0, n0 = ds[0]
    t1, n1 = ds[-1]
    gio = (t1 - t0) / 3_600_000.0

    # ── sụt vốn: đáy sâu nhất tính từ ĐỈNH TRƯỚC ĐÓ ─────────────────────
    dinh = ds[0][1]
    sut_max = 0.0
    sut_luc = None
    dinh_luc = ds[0][0]
    duoi_day_lau = 0.0
    dang_duoi_tu = None
    for t, n in ds:
        if n >= dinh:
            dinh, dinh_luc = n, t
            if dang_duoi_tu is not None:
                duoi_day_lau = max(duoi_day_lau, (t - dang_duoi_tu) / 3_600_000.0)
                dang_duoi_tu = None
        else:
            if dang_duoi_tu is None:
                dang_duoi_tu = t
            s = (dinh - n) / dinh if dinh > 0 else 0.0
            if s > sut_max:
                sut_max, sut_luc = s, t
    if dang_duoi_tu is not None:
        duoi_day_lau = max(duoi_day_lau, (ds[-1][0] - dang_duoi_tu) / 3_600_000.0)

    ra = {
        "soDiem": len(ds), "soGio": gio,
        "navDau": n0, "navCuoi": n1, "vonBanDauUsd": float(vonBanDauUsd),
        "laiLoPhanTram": ((n1 / float(vonBanDauUsd) - 1.0) * 100.0
                          if vonBanDauUsd else None),
        "sutVonToiDaPhanTram": sut_max * 100.0,
        "sutVonLuc": _iso(sut_luc) if sut_luc else None,
        "gioDuoiDayLauNhat": duoi_day_lau,
        "dangDuoiDay": ds[-1][1] < dinh - 1e-9,
    }

    # ── CAGR: chỉ khi đủ mẫu ────────────────────────────────────────────
    if gio < TOI_THIEU_GIO:
        ra.update({
            "duDeKetLuan": False, "cagrPhanTram": None,
            "vi": f"mới {gio:.1f} giờ dữ liệu, cần ≥ {TOI_THIEU_GIO:.0f} — "
                  f"quy một con số nửa ngày ra năm cho một tỉ suất vô nghĩa "
                  f"mà trông rất thuyết phục"})
        return ra

    if n0 <= 0 or n1 <= 0:
        ra.update({"duDeKetLuan": False, "cagrPhanTram": None,
                   "vi": "NAV không dương, không tính gộp được"})
        return ra

    nam = gio / NAM_GIO
    ra.update({"duDeKetLuan": True,
               "cagrPhanTram": ((n1 / n0) ** (1.0 / nam) - 1.0) * 100.0,
               "vi": ""})
    return ra


def _iso(ms: float) -> str:
    return _dt.datetime.fromtimestamp(
        ms / 1000.0, _dt.timezone.utc).isoformat(timespec="seconds")


def doi_chieu_giay_that(so_cai) -> dict:
    """Giấy nói một đằng, thật nói một nẻo? — thước nghiệm thu của $100.

    Bản đồ đặt đúng câu hỏi: nếu sổ giấy ra +18% mà tiền thật ra +2% thì mô
    phỏng đang nói dối, và biết được điều ấy đáng giá hơn cả hai con số.

    Ở bản này **chưa có lệnh thật nào** — `thuc_thi.moPhong` là True cứng.
    Nên hàm này trả về "chưa đối chiếu được", và đó là câu trả lời ĐÚNG, chứ
    không phải một con số 0 giả vờ là kết quả.

    Nó tồn tại để chỗ ấy có sẵn khi lớp ký lệnh tới, và để không ai dựng một
    bảng đối chiếu bịa trong lúc chờ.
    """
    try:
        theo = so_cai.tom_tat().get("theoLoai") or {}
    except Exception:                                     # noqa: BLE001
        theo = {}
    so_but = sum(int((v or {}).get("so") or 0) for v in theo.values())
    return {
        "doiChieuDuoc": False,
        "soButToanGiay": so_but,
        "soButToanThat": 0,
        "vi": "chưa có lệnh thật nào — `thuc_thi.moPhong` là True CỨNG và "
              "không cấu hình nào tắt được. Đối chiếu giấy ↔ thật chỉ có "
              "nghĩa khi cả hai vế cùng tồn tại.",
        "khiNaoDoDuoc": "khi lớp ký lệnh tồn tại và đã có đủ lệnh thật để "
                        "so — trước đó, mọi con số 'sai lệch' đều là bịa.",
    }
